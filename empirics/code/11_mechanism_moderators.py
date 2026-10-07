"""Addendum A of PAP_local_weather.md (exploratory; specifications fixed before estimation).

M1  Mechanism: FAOSTAT production on annual mean local weather (country x crop x year).
M2  Policy moderators of the price effect at h = 6: cereal import dependence (FBS 2010-13),
    conflict exposure (UCDP-GED fatalities within 50 km, previous 12 months), remoteness
    (log distance to nearest city >= 500k, Natural Earth). One at a time, then jointly.
M3  Welfare exposure: calorie-share-weighted staple price response per 1 s.d. drought.
Outputs: output/tables/mech_production.csv, moderators.csv, welfare_exposure.csv
"""
import glob
import importlib.util
import json
import os

import numpy as np
import pandas as pd
import pycountry
import pyfixest as pf
from linearmodels.iv import IV2SLS
from scipy.spatial import cKDTree

HERE = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location("lw", os.path.join(HERE, "06_local_weather.py"))
lw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lw)
RAW, OUT = f"{lw.ROOT}/data/raw", lw.OUT
FAO = f"{RAW}/faostat"
R_EARTH = 6371.0
H = 6


def iso3(m49):
    try:
        return pycountry.countries.get(numeric=str(m49).strip("'").zfill(3)).alpha_3
    except Exception:
        return None


def xyz(lat, lon):
    la, lo = np.deg2rad(np.asarray(lat, float)), np.deg2rad(np.asarray(lon, float))
    return np.column_stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def chord(km):
    return 2 * np.sin(km / (2 * R_EARTH))


# ---------------------------------------------------------------- M1 mechanism
CROPS = {56: "maize", 27: "rice", 15: "wheat", 83: "sorghum", 79: "millet", 125: "cassava", 137: "yams", 489: "plantains"}


def mechanism(p):
    q = pd.read_csv(f"{FAO}/Production_Crops_Livestock_E_All_Data_(Normalized).csv", encoding="latin-1",
                    usecols=["Area Code (M49)", "Item Code", "Element Code", "Year", "Value"])
    q = q[(q["Element Code"] == 5510) & q["Item Code"].isin(CROPS) & q.Year.between(2000, 2024) & (q.Value > 0)]
    q["iso3"] = q["Area Code (M49)"].map(iso3)
    q["crop"] = q["Item Code"].map(CROPS)
    q["lprod"] = np.log(q.Value)
    wy = (p.drop_duplicates(["mkey", "date"]).assign(year=lambda d: d.date.dt.year)
           .groupby(["countryiso3", "year"]).W.mean().rename("Wy").reset_index())
    d = q.merge(wy, left_on=["iso3", "Year"], right_on=["countryiso3", "year"])
    d["traded"] = d.crop.isin(["rice", "wheat"]).astype(float)
    d["Wy_traded"] = d.Wy * d.traded
    d["cc"] = d.iso3 + "_" + d.crop
    d["cy"] = d.crop + "_" + d.Year.astype(str)
    rows = []
    for name, fml, terms in [("pooled", "lprod ~ Wy | cc + cy", ["Wy"]),
                             ("traded interaction", "lprod ~ Wy + Wy_traded | cc + cy", ["Wy", "Wy_traded"])]:
        m = pf.feols(fml, d, vcov={"CRV1": "iso3"})
        t = m.tidy()
        for v in terms:
            rows.append(dict(model=name, term=v, coef=t.loc[v, "Estimate"], se=t.loc[v, "Std. Error"], t=t.loc[v, "t value"],
                             n=m._N, countries=d.iso3.nunique()))
    for c in CROPS.values():
        dc = d[d.crop == c]
        if dc.iso3.nunique() < 8:
            continue
        m = pf.feols("lprod ~ Wy | cc + cy", dc, vcov={"CRV1": "iso3"})
        t = m.tidy()
        rows.append(dict(model=f"crop={c}", term="Wy", coef=t.loc["Wy", "Estimate"], se=t.loc["Wy", "Std. Error"],
                         t=t.loc["Wy", "t value"], n=m._N, countries=dc.iso3.nunique()))
    out = pd.DataFrame(rows)
    out.to_csv(f"{OUT}/mech_production.csv", index=False)
    print(out.round(4).to_string(), flush=True)


# ---------------------------------------------------------------- M2 moderators
def fbs():
    f = pd.read_csv(f"{FAO}/FoodBalanceSheets_E_All_Data_(Normalized).csv", encoding="latin-1",
                    usecols=["Area Code (M49)", "Item Code", "Element Code", "Year", "Value"])
    f = f[f.Year.between(2010, 2013)]
    f["iso3"] = f["Area Code (M49)"].map(iso3)
    return f.dropna(subset=["iso3"])


def import_dependence(f):
    c = f[f["Item Code"] == 2905].pivot_table(index="iso3", columns="Element Code", values="Value", aggfunc="mean")
    return (c[5611] / c[5301]).clip(0, 2).rename("import_dep")


def conflict(p):
    ev = pd.read_csv(glob.glob(f"{RAW}/ucdp/*.csv")[0], usecols=["latitude", "longitude", "date_start", "best"], low_memory=False)
    ev["month"] = pd.to_datetime(ev.date_start).dt.to_period("M").dt.to_timestamp()
    ev = ev[ev.month >= "1999-01-01"]
    last = ev.month.max()
    mk = p.groupby("mkey", as_index=False)[["latitude", "longitude"]].first()
    tree = cKDTree(xyz(mk.latitude, mk.longitude))
    hits = tree.query_ball_point(xyz(ev.latitude, ev.longitude), r=chord(50.0))
    rec = [(mk.mkey.iat[j], m, b) for js, m, b in zip(hits, ev.month.values, ev.best.values) for j in js]
    c = pd.DataFrame(rec, columns=["mkey", "month", "fat"]).groupby(["mkey", "month"]).fat.sum()
    months = pd.date_range("1999-01-01", last, freq="MS")
    grid = c.unstack("mkey").reindex(months).fillna(0)
    grid = grid.reindex(columns=mk.mkey, fill_value=0)
    lag12 = grid.rolling(12, min_periods=12).sum().shift(1)  # months t-12..t-1
    lag12 = lag12[lag12.index <= last + pd.offsets.MonthBegin(1)]
    out = lag12.stack().rename("fat12").reset_index().rename(columns={"level_0": "date"})
    out.columns = ["date", "mkey", "fat12"]
    out["conflict"] = np.log1p(out.fat12)
    return out[["mkey", "date", "conflict"]]


def remoteness(p):
    g = json.load(open(f"{RAW}/access/ne_10m_populated_places_simple.geojson"))
    cities = pd.DataFrame([f["properties"] for f in g["features"]])
    cities = cities[cities.pop_max >= 500_000]
    tree = cKDTree(xyz(cities.latitude, cities.longitude))
    mk = p.groupby("mkey", as_index=False)[["latitude", "longitude"]].first()
    dist, _ = tree.query(xyz(mk.latitude, mk.longitude))
    mk["remote"] = np.log1p(2 * R_EARTH * np.arcsin(np.clip(dist / 2, 0, 1)))
    return mk[["mkey", "remote"]]


def moderators(p, f):
    p = p.merge(import_dependence(f).reset_index().rename(columns={"iso3": "countryiso3"}), on="countryiso3", how="left")
    p = p.merge(conflict(p), on=["mkey", "date"], how="left")
    p = p.merge(remoteness(p), on="mkey", how="left")
    d = p.dropna(subset=[f"y{H}", "W", "import_dep", "conflict", "remote"] + lw.CTRL).copy()
    for c in ("import_dep", "conflict", "remote"):
        d[f"{c}_z"] = (d[c] - d[c].mean()) / d[c].std()
        d[f"W_x_{c}"] = d.W * d[f"{c}_z"]
    cols = [f"y{H}", "W", "conflict_z", "W_x_import_dep", "W_x_conflict", "W_x_remote"] + lw.CTRL
    r = lw.fe_demean(d, cols)
    cl = np.column_stack([pd.factorize(d.countryiso3)[0], pd.factorize(d.date)[0]])
    rows = []
    specs = {"import dependence": ["W", "W_x_import_dep"], "conflict": ["W", "conflict_z", "W_x_conflict"],
             "remoteness": ["W", "W_x_remote"], "joint": ["W", "conflict_z", "W_x_import_dep", "W_x_conflict", "W_x_remote"]}
    for name, X in specs.items():
        m = IV2SLS(r[f"y{H}"], r[X + lw.CTRL], None, None).fit(cov_type="clustered", clusters=cl)
        for v in X:
            rows.append(dict(spec=name, term=v, coef=m.params[v], se=m.std_errors[v], t=m.params[v] / m.std_errors[v],
                             n=int(m.nobs), countries=d.countryiso3.nunique()))
    out = pd.DataFrame(rows)
    sd = {c: d[c].std() for c in ("import_dep", "conflict", "remote")}
    out.attrs["moderator_sd"] = sd
    out.to_csv(f"{OUT}/moderators.csv", index=False)
    print(out.round(4).to_string(), "\nmoderator sd:", {k: round(v, 3) for k, v in sd.items()}, flush=True)


# ---------------------------------------------------------------- M3 welfare
def welfare(f, countries):
    groups = {2511: "wheat", 2807: "rice", 2514: "maize", 2517: "coarse", 2518: "coarse",
              2532: "nontraded", 2535: "nontraded", 2616: "nontraded"}
    k = f[(f["Element Code"] == 664) & f["Item Code"].isin(groups)].copy()
    k["group"] = k["Item Code"].map(groups)
    s = k.groupby(["iso3", "group", "Year"]).Value.sum().groupby(["iso3", "group"]).mean().unstack(fill_value=0)
    s = s.div(s.sum(1), axis=0)
    r = pd.read_csv(f"{OUT}/lw_main.csv")
    t = r[(r.spec == "tradability") & (r.h == H)].set_index("term").coef
    delta = {"rice": t["W"], "wheat": t["W"] + t["W_x_wheat"], "maize": t["W"] + t["W_x_maize"],
             "coarse": t["W"] + t["W_x_coarse"], "nontraded": t["W"] + t["W_x_nontraded"]}
    s = s[s.index.isin(countries)]
    s["exposure_pct"] = 100 * sum(s[g] * delta[g] for g in delta)
    s["local_staple_share"] = s[["maize", "coarse", "nontraded"]].sum(1)
    s = s.sort_values("exposure_pct", ascending=False)
    s.to_csv(f"{OUT}/welfare_exposure.csv")
    print(s.round(3).head(15).to_string())
    print("corr(exposure, local staple share) =", round(s.exposure_pct.corr(s.local_staple_share), 3),
          "| median exposure", round(s.exposure_pct.median(), 3), "| IQR", s.exposure_pct.quantile([.25, .75]).round(3).tolist(), flush=True)


if __name__ == "__main__":
    p = lw.load([H])
    mechanism(p)
    f = fbs()
    welfare(f, set(p.countryiso3))
    moderators(p, f)
