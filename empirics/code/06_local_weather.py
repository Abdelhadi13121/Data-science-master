"""Local weather shocks and local food prices: estimates pre-specified in PAP_local_weather.md.

Per horizon h, the estimation sample is FE-demeaned once (series x calendar-month and
country x year; Frisch-Waugh-Lovell), then every specification is OLS on the demeaned data with
standard errors two-way clustered by country and month.

Outputs (output/tables/):
  lw_main.csv        main delta_h, components, bins, tradability, state dependence
  lw_placebo.csv     lead (W_{t+6}) and pre-trend tests
Usage: python 06_local_weather.py [H list, default 0,2,4,6,8,10,12]
"""
import os
import sys

import numpy as np
import pandas as pd
from linearmodels.iv import IV2SLS
from pyfixest.estimation import demean

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = f"{ROOT}/output/tables"
os.makedirs(OUT, exist_ok=True)
GROUPS = ["wheat", "maize", "rice", "coarse", "nontraded"]
CTRL = [f"dlp_l{l}" for l in (1, 2, 3)] + [f"W_l{l}" for l in (1, 2, 3)] + ["dG"] + [f"dG_l{l}" for l in (1, 2, 3)] + ["dE"]


def load(H):
    p = pd.read_parquet(f"{ROOT}/data/processed/panel.parquet")
    p = p[p.group.isin(GROUPS) & (p.date >= "2000-01-01")].sort_values(["series", "date"]).copy()
    g = p.groupby("series")
    p["dG"] = g.lG.diff()
    p["dE"] = g.lfx.diff()
    for l in (1, 2, 3):
        p[f"dlp_l{l}"] = g.dlp.shift(l)
        p[f"W_l{l}"] = g.W.shift(l)
        p[f"dG_l{l}"] = g.dG.shift(l)
    for h in H:
        p[f"y{h}"] = g.lp.shift(-h) - g.lp.shift(1)
    p["y_pre"] = g.lp.shift(1) - g.lp.shift(4)
    p["W_lead6"] = g.W.shift(-6)
    # components (adverse direction), bins, interactions
    p["c_heat"] = p.z_heat.fillna(0)
    p["c_dry"] = -p.z_swvl1.fillna(0)
    p["c_rain"] = -p.z_precip.fillna(0)
    p["b_wet"] = (p.W <= -1).astype(float)
    p["b_dry1"] = ((p.W > 1) & (p.W <= 2)).astype(float)
    p["b_dry2"] = (p.W > 2).astype(float)
    for gr in ("wheat", "maize", "coarse", "nontraded"):
        p[f"W_x_{gr}"] = p.W * (p.group == gr)
    p["imported"] = p.commodity.str.contains("import", case=False).astype(float)
    p["W_x_imported"] = p.W * p.imported
    ma = g.lG.transform(lambda s: s.rolling(24, min_periods=12).mean())
    p["hiG"] = (p.lG > ma).astype(float)
    p["W_x_hiG"] = p.W * p.hiG
    p["W_x_dG"] = p.W * p.dG
    p["fe_sm"] = p.series + "_" + p.date.dt.month.astype(str)
    p["fe_ky"] = p.countryiso3 + "_" + p.date.dt.year.astype(str)
    return p


EXTRA = ["c_heat", "c_dry", "c_rain", "b_wet", "b_dry1", "b_dry2", "W_x_wheat", "W_x_maize", "W_x_coarse",
         "W_x_nontraded", "W_x_imported", "hiG", "W_x_hiG", "W_x_dG"]


def fe_demean(d, cols):
    codes = np.column_stack([pd.factorize(d.fe_sm)[0], pd.factorize(d.fe_ky)[0]]).astype(np.uint64)
    res, ok = demean(d[cols].to_numpy(np.float64), codes, np.ones(len(d)), tol=1e-7, maxiter=200000)
    if not ok:
        raise RuntimeError("demeaning did not converge")
    return pd.DataFrame(res, columns=cols, index=d.index)


def ols(r, y, X, cl):
    m = IV2SLS(r[y], r[X], None, None).fit(cov_type="clustered", clusters=cl)
    return m


SPECS = {
    "main": ["W"],
    "components": ["c_heat", "c_dry", "c_rain"],
    "bins": ["b_wet", "b_dry1", "b_dry2"],
    "tradability": ["W", "W_x_wheat", "W_x_maize", "W_x_coarse", "W_x_nontraded"],
    "imported": ["W", "W_x_imported"],
    "state_hiG": ["W", "hiG", "W_x_hiG"],
    "state_dG": ["W", "W_x_dG"],
}


def run_main(p, H):
    rows = []
    for h in H:
        d = p.dropna(subset=[f"y{h}", "W"] + CTRL)
        cols = [f"y{h}", "W"] + EXTRA + CTRL
        r = fe_demean(d, list(dict.fromkeys(cols)))
        cl = np.column_stack([pd.factorize(d.countryiso3)[0], pd.factorize(d.date)[0]])
        for name, X in SPECS.items():
            Xc = list(dict.fromkeys(X + [c for c in CTRL if c not in X]))
            m = ols(r, f"y{h}", Xc, cl)
            for v in X:
                rows.append(dict(spec=name, h=h, term=v, coef=m.params[v], se=m.std_errors[v], n=int(m.nobs)))
        print(f"h={h} n={len(d)} delta={rows[-len(sum(SPECS.values(), [])) ]['coef']:.4f}", flush=True)
        pd.DataFrame(rows).to_csv(f"{OUT}/lw_main.csv", index=False)
    return pd.DataFrame(rows)


def run_placebo(p):
    rows = []
    for h in (0, 2):
        d = p.dropna(subset=[f"y{h}", "W", "W_lead6"] + CTRL)
        r = fe_demean(d, [f"y{h}", "W", "W_lead6"] + CTRL)
        cl = np.column_stack([pd.factorize(d.countryiso3)[0], pd.factorize(d.date)[0]])
        m = ols(r, f"y{h}", ["W", "W_lead6"] + CTRL, cl)
        for v in ("W", "W_lead6"):
            rows.append(dict(test=f"lead6_h{h}", term=v, coef=m.params[v], se=m.std_errors[v], n=int(m.nobs)))
    d = p.dropna(subset=["y_pre", "W"] + CTRL)
    r = fe_demean(d, ["y_pre", "W"] + CTRL)
    cl = np.column_stack([pd.factorize(d.countryiso3)[0], pd.factorize(d.date)[0]])
    m = ols(r, "y_pre", ["W"] + [c for c in CTRL if not c.startswith("dlp")], cl)  # dlp lags overlap the outcome window
    rows.append(dict(test="pretrend_t-4..t-1", term="W", coef=m.params["W"], se=m.std_errors["W"], n=int(m.nobs)))
    out = pd.DataFrame(rows)
    out["t"] = out.coef / out.se
    out.to_csv(f"{OUT}/lw_placebo.csv", index=False)
    print(out.round(4).to_string(), flush=True)
    return out


if __name__ == "__main__":
    H = [int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else "0,2,4,6,8,10,12").split(",")]
    p = load(H)
    print("sample:", p.series.nunique(), "series,", p.countryiso3.nunique(), "countries", flush=True)
    run_placebo(p)
    res = run_main(p, H)
    res["t"] = res.coef / res.se
    res.to_csv(f"{OUT}/lw_main.csv", index=False)
    pd.set_option("display.width", 220)
    print(res.pivot_table(index="h", columns=["spec", "term"], values="coef").round(4).to_string())
    print(res.pivot_table(index="h", columns=["spec", "term"], values="t").round(2).to_string())
