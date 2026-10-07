"""Main estimates: compound climate x world-price shocks in local food markets.

For h = 0..H, with y_h = ln p_{i,t+h} - ln p_{i,t-1} (i = market x commodity series):

 (RF)   y_h = a W_it + b Z_ct + c (W_it x Z_ct) + d dE_kt + controls + FE
 (OLS)  y_h = beta^W W + beta^G dG + gamma (W x dG) + theta dE + controls + FE
 (2SLS) same as OLS, with [dG, W x dG] instrumented by [Z, W x Z]
 (DML)  partially linear IV (DoubleML PLIV): Y = theta*dG + g(X) + U, instrument Z,
        LightGBM nuisances on FE-residualized data, folds blocked by country,
        estimated separately for drought (W > 1) and normal (|W| < 0.5) market-months.

Controls: 3 lags of dlnp, dG, W, Z.  FE: series x calendar-month, country x year.
SE: clustered by country (pyfixest/linearmodels), so inference is robust to arbitrary
within-country spatial and serial correlation.

Usage: python 05_estimate.py [panel.parquet] [H]
"""
import os
import sys

import numpy as np
import pandas as pd
import pyfixest as pf
from linearmodels.iv import IV2SLS
from pyfixest.estimation import demean

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = f"{ROOT}/output/tables"
os.makedirs(OUT, exist_ok=True)


ZCOL = os.environ.get("INSTRUMENT", "Z_heat")  # primary: extreme-heat index (see RESULTS_first_stage.md)


def prepare(p, H):
    p = p.sort_values(["series", "date"]).copy()
    p["Z"] = p[ZCOL]
    g = p.groupby("series")
    p["dG"] = p.groupby("series").lG.diff()
    p["dE"] = g.lfx.diff()
    for l in (1, 2, 3):
        p[f"dlp_l{l}"] = g.dlp.shift(l)
        p[f"dG_l{l}"] = g.dG.shift(l)
        p[f"W_l{l}"] = g.W.shift(l)
        p[f"Z_l{l}"] = g.Z.shift(l)
    for h in range(H + 1):
        p[f"y{h}"] = g.lp.shift(-h) - g.lp.shift(1)
    p["WZ"] = p.W * p.Z
    p["WdG"] = p.W * p.dG
    p["fe_sm"] = p.series + "_" + p.date.dt.month.astype(str)
    p["fe_ky"] = p.countryiso3 + "_" + p.date.dt.year.astype(str)
    return p


CTRL = [f"{v}_l{l}" for v in ("dlp", "dG", "W", "Z") for l in (1, 2, 3)]


def fe_demean(d, cols):
    codes = np.column_stack([pd.factorize(d.fe_sm)[0], pd.factorize(d.fe_ky)[0]]).astype(np.uint64)
    x = d[cols].to_numpy(np.float64)
    res, ok = demean(x, codes, np.ones(len(d)))
    return pd.DataFrame(res, columns=cols, index=d.index)


def run_rf_ols(p, H, groups):
    rows = []
    for h in range(H + 1):
        d = p[p.group.isin(groups)].dropna(subset=[f"y{h}", "W", "Z", "dG", "dE"] + CTRL)
        ctrl = " + ".join(CTRL)
        for name, fml in [("RF", f"y{h} ~ W + Z + WZ + dE + {ctrl} | fe_sm + fe_ky"),
                          ("OLS", f"y{h} ~ W + dG + WdG + dE + {ctrl} | fe_sm + fe_ky")]:
            m = pf.feols(fml, d, vcov={"CRV1": "countryiso3"})
            t = m.tidy()
            for v in (["W", "Z", "WZ"] if name == "RF" else ["W", "dG", "WdG"]):
                rows.append(dict(model=name, h=h, term=v, coef=t.loc[v, "Estimate"], se=t.loc[v, "Std. Error"], n=m._N))
    return pd.DataFrame(rows)


def run_2sls(p, H, groups):
    rows = []
    for h in range(H + 1):
        d = p[p.group.isin(groups)].dropna(subset=[f"y{h}", "W", "Z", "dG", "dE"] + CTRL)
        cols = [f"y{h}", "W", "dG", "WdG", "Z", "WZ", "dE"] + CTRL
        r = fe_demean(d, cols)
        m = IV2SLS(r[f"y{h}"], r[["W", "dE"] + CTRL], r[["dG", "WdG"]], r[["Z", "WZ"]]).fit(
            cov_type="clustered", clusters=pd.factorize(d.countryiso3)[0])
        fs = m.first_stage.diagnostics
        for v in ("W", "dG", "WdG"):
            rows.append(dict(model="2SLS", h=h, term=v, coef=m.params[v], se=m.std_errors[v], n=int(m.nobs),
                             fs_F_dG=float(fs.loc["dG", "f.stat"]), fs_F_WdG=float(fs.loc["WdG", "f.stat"])))
    return pd.DataFrame(rows)


def run_dml(p, h, groups, seed=0):
    import doubleml as dml
    from lightgbm import LGBMRegressor
    from sklearn.model_selection import GroupKFold

    d = p[p.group.isin(groups)].dropna(subset=[f"y{h}", "W", "Z", "dG", "dE"] + CTRL)
    cols = [f"y{h}", "dG", "Z", "W", "dE"] + CTRL
    r = fe_demean(d, cols)
    out = []
    for regime, mask in [("drought W>1", d.W > 1), ("normal |W|<0.5", d.W.abs() < 0.5), ("all", d.W.notna())]:
        rr = r[mask.values]
        obj = dml.DoubleMLData(rr, y_col=f"y{h}", d_cols="dG", z_cols="Z", x_cols=["W", "dE"] + CTRL)
        lgb = dict(n_estimators=300, learning_rate=0.05, num_leaves=31, min_child_samples=50, verbose=-1, random_state=seed)
        est = dml.DoubleMLPLIV(obj, ml_l=LGBMRegressor(**lgb), ml_m=LGBMRegressor(**lgb), ml_r=LGBMRegressor(**lgb), n_folds=5)
        # folds blocked by country to respect spatial/serial dependence
        grp = pd.factorize(d.countryiso3[mask.values])[0]
        folds = list(GroupKFold(5).split(rr, groups=grp))
        est.set_sample_splitting([(tr, te) for tr, te in folds])
        est.fit()
        out.append(dict(model="DML-PLIV", h=h, regime=regime, coef=float(est.coef[0]), se=float(est.se[0]), n=len(rr)))
    return pd.DataFrame(out)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else f"{ROOT}/data/processed/panel.parquet"
    H = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    tag = os.path.splitext(os.path.basename(path))[0]
    p = prepare(pd.read_parquet(path), H)
    traded = ["wheat", "maize", "rice"]
    rf = run_rf_ols(p, H, traded)
    rf.to_csv(f"{OUT}/rf_ols_{tag}.csv", index=False)
    iv = run_2sls(p, H, traded)
    iv.to_csv(f"{OUT}/iv_{tag}.csv", index=False)
    dm = pd.concat([run_dml(p, h, traded) for h in (0, 3, 6, 12) if h <= H])
    parts = [rf, iv, dm.rename(columns={"regime": "term"})]
    if (p.group == "nontraded").any():
        pl = run_rf_ols(p, min(H, 6), ["nontraded"])
        parts.append(pl.assign(model="placebo_" + pl.model))
    res = pd.concat(parts)
    res["t"] = res.coef / res.se
    res.to_csv(f"{OUT}/main_{tag}.csv", index=False)
    pd.set_option("display.width", 200)
    print(res[res.model.isin(["2SLS", "RF"])].pivot_table(index="h", columns=["model", "term"], values=["coef", "t"]).round(3))
    print(dm.round(3))
