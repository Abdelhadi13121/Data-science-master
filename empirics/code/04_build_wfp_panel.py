"""Build the market x commodity x month analysis panel from WFP (HDX) price files.

Input : data/raw/wfp/*.csv  -- HDX "Global - Food Prices" yearly files
        (columns: countryiso3,date,admin1,admin2,market,market_id,latitude,longitude,
         category,commodity,commodity_id,unit,priceflag,pricetype,currency,price,usdprice)
        data/raw/era5_monthly/*.npz, data/raw/gpcp/*/*.nc, data/processed/instrument.csv,
        data/raw/world_cereal_prices_imf_fred.csv
Output: data/processed/panel.parquet

Steps
 1. Keep retail prices; map commodities to traded cereal groups (wheat, maize, rice) and
    to a non-traded placebo group (cassava, plantain, local beans, ...).
 2. One series per market x commodity_id x unit; monthly median; log price.
 3. Implied exchange rate e_kt = median(price / usdprice) by country-month.
 4. Local weather at market coordinates (nearest ERA5 0.25 cell, GPCP 2.5 cell):
    standardized anomalies vs the 1991-2020 market-calendar-month climatology;
    local adverse index W = 3-month mean of z(HDD30) - z(soil moisture) - z(precip).
 5. Merge world prices and exporter-weather instrument by cereal group.
"""
import glob
import os
import re
import sys

import numpy as np
import pandas as pd
import xarray as xr

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW, PROC = f"{ROOT}/data/raw", f"{ROOT}/data/processed"

EXCLUDE = r"oil|milling cost|seed|food aid|soy blend|leaves|starch|buckwheat|tortilla|paddy|unmilled"
GROUP_PATTERNS = [  # evaluated in order, after EXCLUDE
    ("rice", r"\brice\b"),
    ("maize", r"maize|\bcorn\b"),
    ("coarse", r"sorghum|millet|teff"),
    ("nontraded", r"cassava|gari|plantain|\byam\b|cocoyam|sweet potato"),
    ("wheat", r"wheat|bread|pasta|macaroni|spaghetti|semolina|\bflour\b"),
]


def cereal_group(name):
    n = name.lower()
    if re.search(EXCLUDE, n):
        return None
    for g, pat in GROUP_PATTERNS:
        if re.search(pat, n):
            return g
    return None


def load_wfp(files):
    usecols = ["countryiso3", "date", "market_id", "market", "latitude", "longitude", "commodity",
               "commodity_id", "unit", "pricetype", "priceflag", "currency", "price", "usdprice"]
    df = pd.concat([pd.read_csv(f, usecols=lambda c: c in usecols, low_memory=False) for f in files], ignore_index=True)
    df = df[~df.date.astype(str).str.startswith("#")]  # HXL tag row
    df["date"] = pd.to_datetime(df.date).dt.to_period("M").dt.to_timestamp()
    for c in ("price", "usdprice", "latitude", "longitude"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df[(df.pricetype.str.lower() == "retail") & (df.price > 0)]
    if "priceflag" in df:
        df = df[~df.priceflag.astype(str).str.contains("forecast", case=False)]
    df["group"] = df.commodity.map(cereal_group)
    return df.dropna(subset=["group", "latitude", "longitude"])


def build_prices(df):
    keys = ["countryiso3", "market_id", "commodity_id", "unit"]
    p = df.groupby(keys + ["date"], as_index=False).agg(
        price=("price", "median"), usdprice=("usdprice", "median"), latitude=("latitude", "first"),
        longitude=("longitude", "first"), group=("group", "first"), commodity=("commodity", "first"),
        market=("market", "first"))
    p["series"] = p[keys].astype(str).agg("|".join, axis=1)
    # implied exchange rate (LCU per USD), country-month median
    fx = (df.assign(e=df.price / df.usdprice).replace([np.inf, -np.inf], np.nan)
            .groupby(["countryiso3", "date"]).e.median().rename("fx").reset_index())
    p = p.merge(fx, on=["countryiso3", "date"], how="left")
    # balanced monthly index within series span (gaps stay NaN; LPs use available pairs)
    out = []
    for s, g in p.groupby("series"):
        idx = pd.date_range(g.date.min(), g.date.max(), freq="MS")
        g = g.set_index("date").reindex(idx)
        g.index.name = "date"
        g[["series", "countryiso3", "market_id", "commodity_id", "unit", "group", "commodity", "market"]] = \
            g[["series", "countryiso3", "market_id", "commodity_id", "unit", "group", "commodity", "market"]].ffill().bfill()
        g[["latitude", "longitude"]] = g[["latitude", "longitude"]].ffill().bfill()
        out.append(g.reset_index())
    p = pd.concat(out, ignore_index=True)
    p["lp"] = np.log(p.price)
    p["lfx"] = np.log(p.fx)
    # drop absurd month-on-month jumps (data-entry errors): |dlog| > 1.5
    p["dlp"] = p.groupby("series").lp.diff()
    p.loc[p.dlp.abs() > 1.5, ["lp", "dlp"]] = np.nan
    return p


def local_weather(markets, dates, window=3, clip=4.0, detrend=False):
    """Market-level monthly weather anomalies from ERA5 grids + GPCP.
    window: months aggregated (baseline 3); clip: |z| cap (None = no clipping);
    detrend: remove a market-specific linear trend from W (sensitivity only)."""
    lat_idx = np.clip(np.round((90 - markets.latitude.values) / 0.25).astype(int), 0, 720)
    lon_idx = np.round((markets.longitude.values % 360) / 0.25).astype(int) % 1440
    rows = {}
    for f in sorted(glob.glob(f"{RAW}/era5_monthly/*.npz")):
        d = np.load(f)
        t = pd.Timestamp(os.path.basename(f)[:7] + "-01")
        rows[t] = {k: d[k][lat_idx, lon_idx].astype(np.float32) for k in ("tmean", "hdd30", "swvl1")}
    ts = sorted(rows)
    w = {k: pd.DataFrame(np.stack([rows[t][k] for t in ts]), index=ts, columns=markets.mkey.values) for k in ("tmean", "hdd30", "swvl1")}
    # GPCP
    files = sorted(glob.glob(f"{RAW}/gpcp/*/*.nc"))
    by_month = {}
    for f in files:
        ym = os.path.basename(f).split("_d")[1][:6]
        if ym not in by_month or "preliminary" in by_month[ym]:
            by_month[ym] = f
    pr = xr.open_mfdataset([by_month[k] for k in sorted(by_month)], combine="by_coords")["precip"]
    pts = pr.sel(latitude=xr.DataArray(markets.latitude.values, dims="m"),
                 longitude=xr.DataArray(markets.longitude.values % 360, dims="m"), method="nearest").load()
    w["precip"] = pd.DataFrame(pts.values, index=pd.to_datetime(pts.time.values).to_period("M").to_timestamp(), columns=markets.mkey.values)
    # 3-month aggregates (SPI/SPEI convention), then robust standardization against the
    # 1991-2020 market x calendar-month climatology: sd floored at the 10th percentile of
    # positive sds across markets for that variable, z clipped to +/-4.
    agg = {"tmean": "mean", "hdd30": "sum", "swvl1": "mean", "precip": "sum"}
    out = []
    for k, m in w.items():
        m = m.sort_index()
        mp = max(1, window - 1)
        m = m.rolling(window, min_periods=mp).sum() if agg[k] == "sum" else m.rolling(window, min_periods=mp).mean()
        base = m[(m.index.year >= 1991) & (m.index.year <= 2020)]
        mu = base.groupby(base.index.month).mean()
        sd = base.groupby(base.index.month).std()
        pos = sd.to_numpy()[sd.to_numpy() > 0]
        floor = np.nanquantile(pos, 0.10) if pos.size else 1.0
        sd = sd.where(sd > floor, floor)
        z = (m - mu.loc[m.index.month].values) / sd.loc[m.index.month].values
        if clip is not None:
            z = z.clip(-clip, clip)
        # markets with (near-)zero heat exposure in a season carry no heat signal
        if k == "hdd30":
            z = z.where(mu.loc[m.index.month].values > 1.0)
        out.append(z.stack(future_stack=True).rename(f"z_{k}"))
    W = pd.concat(out, axis=1)
    W.index.names = ["date", "mkey"]
    W = W.reset_index()
    # where extreme heat is climatologically absent, use the mean-temperature anomaly
    W["z_heat"] = W.z_hdd30.fillna(W.z_tmean)
    raw = (W.z_heat.fillna(0) - W.z_swvl1.fillna(0) - W.z_precip.fillna(0)) / 3
    if detrend:
        tt = (W.date - W.date.min()).dt.days.to_numpy(float)
        W["_t"] = tt
        W["_r"] = raw
        def _dt(g):
            b = np.polyfit(g._t, g._r, 1) if g._r.notna().sum() > 24 else (0.0, g._r.mean())
            return g._r - (b[0] * g._t + b[1])
        raw = W.groupby("mkey", group_keys=False).apply(_dt)
        W = W.drop(columns=["_t", "_r"])
    W["W"] = (raw - raw.mean()) / raw.std()
    return W[W.date.isin(dates)]


def rebuild_weather():
    """Recompute local weather on an existing panel without re-reading the price files."""
    p = pd.read_parquet(f"{PROC}/panel.parquet")
    p = p.drop(columns=[c for c in p.columns if c.startswith("z_") or c in ("adverse", "W")])
    mk = p.groupby("mkey", as_index=False)[["latitude", "longitude"]].first()
    p = p.merge(local_weather(mk, p.date.unique()), on=["mkey", "date"], how="left")
    p.to_parquet(f"{PROC}/panel.parquet", index=False)
    print(p.W.describe().round(3))


def main(wfp_glob=f"{RAW}/wfp/wfp_food_prices_global_*.csv"):
    files = sorted(glob.glob(wfp_glob))
    if not files:
        sys.exit(f"No WFP files found at {wfp_glob}. See README: download HDX 'Global - Food Prices' yearly CSVs.")
    p = build_prices(load_wfp(files))
    p["mkey"] = p.countryiso3 + "|" + p.market_id.astype(str)
    mk = p.groupby("mkey", as_index=False)[["latitude", "longitude"]].first()
    W = local_weather(mk, p.date.unique())
    p = p.merge(W, on=["mkey", "date"], how="left")
    wp = pd.read_csv(f"{RAW}/world_cereal_prices_imf_fred.csv", parse_dates=["date"]).melt("date", var_name="wgroup", value_name="wprice")
    wp["lG"] = np.log(wp.wprice)
    p["wgroup"] = p.group.replace({"coarse": "maize", "nontraded": "maize"})  # nearest traded substitute
    p = p.merge(wp[["date", "wgroup", "lG"]], on=["date", "wgroup"], how="left")
    z = pd.read_csv(f"{PROC}/instrument.csv", parse_dates=["date"]).rename(columns={"commodity": "wgroup"})
    p = p.merge(z, on=["date", "wgroup"], how="left")
    os.makedirs(PROC, exist_ok=True)
    p.to_parquet(f"{PROC}/panel.parquet", index=False)
    print(p.groupby("group").agg(series=("series", "nunique"), markets=("mkey", "nunique"),
                                 countries=("countryiso3", "nunique"), obs=("lp", "count")))


if __name__ == "__main__":
    if sys.argv[1:] == ["--weather-only"]:
        rebuild_weather()
    else:
        main(*sys.argv[1:])
