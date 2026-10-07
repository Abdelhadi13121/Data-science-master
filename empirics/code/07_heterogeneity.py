"""RQ3: heterogeneity of the local-weather price effect (pre-specified, PAP_local_weather.md).

Horizon h = 6. Outcome and treatment are FE-demeaned (series x calendar month, country x year)
and partialled on the main-specification controls (FWL). Then:
  1. Causal forest (econml CausalForestDML, honest), continuous treatment W, moderators X.
     Cross-fitted by country halves: trained on countries in A, CATE predicted for B, and vice versa,
     so every CATE is out-of-sample for its country.
  2. Calibration: terciles of out-of-sample CATE; the LP coefficient of W is re-estimated
     within each tercile (two-way clustered). Real heterogeneity => monotone increase.
  3. Linear heterogeneity (BLP-type): y ~ W + W x standardized moderators, two-way clustered.
Moderators: distance to coast (km), aridity (log mean annual precipitation, GPCP 1991-2020),
climatological heat exposure (mean annual HDD30, ERA5 1991-2020), |latitude|, product group, imported label.
Outputs: output/tables/het_terciles.csv, het_blp.csv, het_forest_importance.csv
"""
import glob
import importlib.util
import os

import numpy as np
import pandas as pd
import xarray as xr
from linearmodels.iv import IV2SLS
from scipy.spatial import cKDTree

HERE = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location("lw", os.path.join(HERE, "06_local_weather.py"))
lw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lw)
ROOT, OUT = lw.ROOT, lw.OUT
H = 6
SEED = 20261007


def xyz(lat, lon):
    la, lo = np.deg2rad(lat), np.deg2rad(lon)
    return np.column_stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def market_moderators(mk):
    files = sorted(glob.glob(f"{ROOT}/data/raw/era5_monthly/*.npz"))
    lat = np.linspace(90, -90, 721)
    lon = np.arange(1440) * 0.25
    clim = [f for f in files if "1991" <= os.path.basename(f)[:4] <= "2020"]
    sm = np.load(clim[0])["swvl1"].astype(np.float32)
    LA, LO = np.meshgrid(lat, lon, indexing="ij")
    sea = sm <= 0.02
    tree = cKDTree(xyz(LA[sea], LO[sea]))
    dist, _ = tree.query(xyz(mk.latitude.values, mk.longitude.values % 360))
    mk["dist_coast_km"] = 2 * 6371 * np.arcsin(np.clip(dist / 2, 0, 1))
    li = np.clip(np.round((90 - mk.latitude.values) / 0.25).astype(int), 0, 720)
    lj = np.round((mk.longitude.values % 360) / 0.25).astype(int) % 1440
    hdd = np.zeros(len(mk))
    for f in clim:
        hdd += np.load(f)["hdd30"][li, lj].astype(np.float32)
    mk["heat_clim"] = hdd / 30.0  # mean annual HDD30
    gp = sorted(glob.glob(f"{ROOT}/data/raw/gpcp/*/*.nc"))
    gp = [f for f in gp if "preliminary" not in f and "1991" <= os.path.basename(f).split("_d")[1][:4] <= "2020"]
    pr = xr.open_mfdataset(gp, combine="by_coords")["precip"].mean("time")
    pts = pr.sel(latitude=xr.DataArray(mk.latitude.values, dims="m"),
                 longitude=xr.DataArray(mk.longitude.values % 360, dims="m"), method="nearest").load()
    mk["aridity_logprecip"] = np.log(pts.values * 365 + 1)  # mm/day -> mm/yr
    mk["abs_lat"] = mk.latitude.abs()
    return mk


def prepare():
    p = lw.load([H])
    d = p.dropna(subset=[f"y{H}", "W"] + lw.CTRL).copy()
    mk = d.groupby("mkey", as_index=False)[["latitude", "longitude"]].first()
    d = d.merge(market_moderators(mk)[["mkey", "dist_coast_km", "heat_clim", "aridity_logprecip", "abs_lat"]], on="mkey", how="left")
    r = lw.fe_demean(d, [f"y{H}", "W"] + lw.CTRL)
    C = r[lw.CTRL].to_numpy()
    fwl = lambda v: v - C @ np.linalg.lstsq(C, v, rcond=None)[0]
    d["y_t"] = fwl(r[f"y{H}"].to_numpy())
    d["W_t"] = fwl(r.W.to_numpy())
    for gname in ("wheat", "maize", "coarse", "nontraded"):
        d[f"g_{gname}"] = (d.group == gname).astype(float)
    return d


MODS = ["dist_coast_km", "aridity_logprecip", "heat_clim", "abs_lat", "imported", "g_wheat", "g_maize", "g_coarse", "g_nontraded"]


def clustered_ols(df, X, y="y_t"):
    cl = np.column_stack([pd.factorize(df.countryiso3)[0], pd.factorize(df.date)[0]])
    return IV2SLS(df[y], df[X], None, None).fit(cov_type="clustered", clusters=cl)


if __name__ == "__main__":
    from econml.dml import CausalForestDML
    from lightgbm import LGBMRegressor

    d = prepare()
    print("n", len(d), "markets", d.mkey.nunique(), flush=True)
    rng = np.random.default_rng(SEED)
    countries = d.countryiso3.unique()
    half = set(rng.choice(countries, size=len(countries) // 2, replace=False))
    d["fold"] = d.countryiso3.isin(half).astype(int)
    d["cate"] = np.nan
    imp = []
    for f in (0, 1):
        tr = d[d.fold == f]
        tr = tr.sample(min(len(tr), 250_000), random_state=SEED)
        cf = CausalForestDML(model_y=LGBMRegressor(n_estimators=200, verbose=-1, random_state=SEED),
                             model_t=LGBMRegressor(n_estimators=200, verbose=-1, random_state=SEED),
                             n_estimators=400, min_samples_leaf=200, max_depth=None, honest=True,
                             cv=3, random_state=SEED)
        cf.fit(tr.y_t.values, tr.W_t.values, X=tr[MODS].values)
        te = d.fold == 1 - f
        d.loc[te, "cate"] = cf.effect(d.loc[te, MODS].values)
        imp.append(pd.Series(cf.feature_importances_, index=MODS, name=f"fold{f}"))
        print(f"fold {f} trained", flush=True)
    pd.concat(imp, axis=1).assign(mean=lambda x: x.mean(1)).sort_values("mean", ascending=False).to_csv(f"{OUT}/het_forest_importance.csv")

    # calibration on out-of-sample CATE terciles
    d["tercile"] = pd.qcut(d.cate.rank(method="first"), 3, labels=["low", "mid", "high"])
    rows = []
    for t, g in d.groupby("tercile", observed=True):
        m = clustered_ols(g, ["W_t"])
        rows.append(dict(tercile=t, delta=m.params["W_t"], se=m.std_errors["W_t"], mean_cate=g.cate.mean(), n=len(g)))
    d["W_hi"] = d.W_t * (d.tercile == "high")
    d["W_lo"] = d.W_t * (d.tercile == "low")
    m = clustered_ols(d, ["W_t", "W_hi", "W_lo"])
    rows.append(dict(tercile="high-minus-mid", delta=m.params["W_hi"], se=m.std_errors["W_hi"], n=len(d)))
    rows.append(dict(tercile="low-minus-mid", delta=m.params["W_lo"], se=m.std_errors["W_lo"], n=len(d)))
    ter = pd.DataFrame(rows)
    ter["t"] = ter.delta / ter.se
    ter.to_csv(f"{OUT}/het_terciles.csv", index=False)
    print(ter.round(4).to_string(), flush=True)

    # linear heterogeneity with standardized continuous moderators
    X = ["W_t"]
    for c in MODS:
        z = d[c] if c in ("imported",) or c.startswith("g_") else (d[c] - d[c].mean()) / d[c].std()
        d[f"Wx_{c}"] = d.W_t * z
        X.append(f"Wx_{c}")
    m = clustered_ols(d, X)
    blp = pd.DataFrame(dict(coef=m.params, se=m.std_errors))
    blp["t"] = blp.coef / blp.se
    blp.to_csv(f"{OUT}/het_blp.csv")
    print(blp.round(4).to_string())
