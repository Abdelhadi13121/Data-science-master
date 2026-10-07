"""Exporter-weather supply-shock instrument for world cereal prices.

For each commodity c, major exporting region j and month t:
  adverse_jt = z(HDD30_jt) - z(SoilMoisture_jt) - z(Precip_jt)    (standardized, region-level)
built only in the region's crop-critical months (growing season), 0 otherwise.
The instrument is the export-share-weighted sum:
  Z_ct = sum_j s_jc * adverse_jt * 1[t in season_j]

Region boxes are the core production zones of each exporter; export shares are
approximate 2000-2005 averages (pre-sample, FAOSTAT/USDA order of magnitude) so that
they are predetermined with respect to 2006-2026 price movements.

Output: data/processed/exporter_weather.csv (date x commodity x region components) and
        data/processed/instrument.csv (date x commodity: Z, Z_hdd, Z_sm, Z_pr).
"""
import glob
import os

import numpy as np
import pandas as pd
import xarray as xr

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW, PROC = f"{ROOT}/data/raw", f"{ROOT}/data/processed"
os.makedirs(PROC, exist_ok=True)

# (lat_min, lat_max, lon_min, lon_max) in degrees East (-180..180), crop-critical months
REGIONS = {
    "wheat": {
        "US_winter": ((33, 42, -103, -95), [4, 5, 6], 0.20),
        "US_CA_spring": ((45, 54, -114, -96), [6, 7, 8], 0.22),
        "EU_core": ((43, 54, -2, 15), [4, 5, 6], 0.16),
        "Russia_south": ((44, 54, 36, 50), [5, 6, 7], 0.10),
        "Ukraine": ((46, 52, 28, 40), [5, 6, 7], 0.05),
        "Kazakhstan": ((50, 55, 62, 77), [6, 7, 8], 0.05),
        "Australia": ((-36, -28, 115, 152), [8, 9, 10], 0.14),
        "Argentina": ((-39, -30, -65, -58), [9, 10, 11], 0.08),
    },
    "maize": {
        "US_cornbelt": ((37, 45, -100, -82), [6, 7, 8], 0.62),
        "Argentina": ((-36, -30, -64, -58), [12, 1, 2], 0.14),
        "Brazil": ((-25, -10, -58, -46), [3, 4, 5], 0.12),
        "Ukraine": ((46, 51, 28, 38), [6, 7, 8], 0.04),
        "South_Africa": ((-29, -25, 25, 31), [12, 1, 2], 0.03),
    },
    "rice": {
        "Thailand": ((13, 17, 99, 105), [7, 8, 9, 10], 0.32),
        "Vietnam": ((9, 11.5, 104.5, 106.8), [7, 8, 9, 10], 0.17),
        "India": ((20, 32, 73, 89), [7, 8, 9], 0.17),
        "Pakistan": ((29, 33, 71, 75), [7, 8, 9], 0.10),
        "US_south": ((33, 36, -92, -90), [6, 7, 8], 0.12),
    },
}

LAT = np.linspace(90, -90, 721)
LON = np.arange(1440) * 0.25  # 0..359.75


def box_mask(lat0, lat1, lon0, lon1, lat, lon):
    lon = np.where(lon > 180, lon - 360, lon)
    la = (lat >= lat0) & (lat <= lat1)
    lo = (lon >= lon0) & (lon <= lon1)
    return la[:, None] & lo[None, :]


def era5_region_series():
    files = sorted(glob.glob(f"{RAW}/era5_monthly/*.npz"))
    # land mask from a soil-moisture climatology (sea points are ~0 in ERA5 swvl1)
    sm0 = np.load(files[len(files) // 2])["swvl1"].astype(np.float32)
    land = sm0 > 0.02
    w = np.cos(np.deg2rad(LAT))[:, None] * np.ones((1, 1440))
    masks = {(c, j): box_mask(*b, LAT, LON) & land for c, R in REGIONS.items() for j, (b, _, _) in R.items()}
    rows = []
    for f in files:
        d = np.load(f)
        date = pd.Timestamp(os.path.basename(f)[:7] + "-01")
        arr = {k: d[k].astype(np.float32) for k in ("tmean", "tmax", "hdd30", "swvl1")}
        for (c, j), m in masks.items():
            ww = w[m]
            rows.append({"date": date, "commodity": c, "region": j,
                         **{k: float(np.sum(v[m] * ww) / ww.sum()) for k, v in arr.items()}})
    return pd.DataFrame(rows)


def gpcp_region_series():
    files = sorted(glob.glob(f"{RAW}/gpcp/*/*.nc"))
    # prefer final over preliminary for duplicated months
    by_month = {}
    for f in files:
        ym = os.path.basename(f).split("_d")[1][:6]
        if ym not in by_month or "preliminary" in by_month[ym]:
            by_month[ym] = f
    ds = xr.open_mfdataset([by_month[k] for k in sorted(by_month)], combine="by_coords")["precip"].load()
    lat, lon = ds.latitude.values, ds.longitude.values
    w = np.cos(np.deg2rad(lat))[:, None] * np.ones((1, len(lon)))
    rows = []
    for c, R in REGIONS.items():
        for j, (b, _, _) in R.items():
            m = box_mask(*b, lat, lon)
            if m.sum() == 0:  # small box: nearest cell
                m = np.zeros_like(m)
                m[np.abs(lat - (b[0] + b[1]) / 2).argmin(), np.abs(np.where(lon > 180, lon - 360, lon) - (b[2] + b[3]) / 2).argmin()] = True
            s = (ds.values[:, m] * w[m]).sum(1) / w[m].sum()
            rows += [{"date": pd.Timestamp(t).normalize().replace(day=1), "commodity": c, "region": j, "precip": float(v)}
                     for t, v in zip(ds.time.values, s)]
    return pd.DataFrame(rows)


def standardize(df, cols, base=(1991, 2020)):
    df = df.copy()
    df["month"] = df.date.dt.month
    clim = df[(df.date.dt.year >= base[0]) & (df.date.dt.year <= base[1])].groupby(["commodity", "region", "month"])[cols]
    mu, sd = clim.mean(), clim.std()
    df = df.join(mu, on=["commodity", "region", "month"], rsuffix="_mu").join(sd, on=["commodity", "region", "month"], rsuffix="_sd")
    for c in cols:
        df[f"z_{c}"] = (df[c] - df[f"{c}_mu"]) / df[f"{c}_sd"].replace(0, np.nan)
    return df.drop(columns=[f"{c}_mu" for c in cols] + [f"{c}_sd" for c in cols])


if __name__ == "__main__":
    era = era5_region_series()
    pr = gpcp_region_series()
    df = era.merge(pr, on=["date", "commodity", "region"], how="left")
    df = standardize(df, ["tmean", "tmax", "hdd30", "swvl1", "precip"])
    # hdd30 is zero in many cool-season cells: fall back to tmax anomaly where sd==0
    df["z_heat"] = df["z_hdd30"].fillna(df["z_tmax"])
    df["adverse"] = df["z_heat"].fillna(0) - df["z_swvl1"].fillna(0) - df["z_precip"].fillna(0)
    season = {(c, j): s for c, R in REGIONS.items() for j, (_, s, _) in R.items()}
    share = {(c, j): sh for c, R in REGIONS.items() for j, (_, _, sh) in R.items()}
    key = list(zip(df.commodity, df.region))
    df["in_season"] = [m in season[k] for k, m in zip(key, df.month)]
    df["share"] = [share[k] for k in key]
    df["share"] = df["share"] / df.groupby(["date", "commodity"])["share"].transform("sum")
    df.to_csv(f"{PROC}/exporter_weather.csv", index=False)

    comps = {"Z": "adverse", "Z_heat": "z_heat", "Z_sm": "z_swvl1", "Z_pr": "z_precip"}
    out = []
    for name, col in comps.items():
        tmp = df.assign(v=df[col].fillna(0) * df.share * df.in_season)
        out.append(tmp.groupby(["date", "commodity"])["v"].sum().rename(name))
    inst = pd.concat(out, axis=1).reset_index()
    inst.to_csv(f"{PROC}/instrument.csv", index=False)
    print(inst.groupby("commodity")[list(comps)].describe().T.round(2))
