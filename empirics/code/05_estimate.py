"""Main estimates: compound climate x world-price shocks in local food markets.

For h = 0..H, with y_h = ln p_{i,t+h} - ln p_{i,t-1} (i = market x commodity series):

 (RF)   y_h = a W_it + b Z_ct + c (W_it x Z_ct) + d dE_kt + controls + FE
 (OLS)  y_h = beta^W W + beta^G dG + gamma (W x dG) + theta dE + controls + FE
 (2SLS) same as OLS, with [dG, W x dG] instrumented by [Z, W x Z]
 (DML)  partially linear IV (DoubleML PLIV): Y = theta*dG + g(X) + U, instrument Z,
        LightGBM nuisances on FE-residualized data, folds blocked by country,
        estimated separately for drought (W > 1) and normal (|W| < 0.5) market-months.

Controls: 3 lags of dlnp, dG, W, Z.  FE: series x calendar-month, country x year.
SE: two-way clustered by country and month (the instrument varies only by commodity-month,
so month clustering is essential); AR weak-IV-robust confidence sets, same clustering.

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
    p["ym"] = p.date.dt.strftime("%Y-%m")
    return p


CTRL = [f"{v}_l{l}" for v in ("dlp", "dG", "W", "Z") for l in (1, 2, 3)]


def fe_demean(d, cols):
    codes = np.column_stack([pd.factorize(d.fe_sm)[0], pd.factorize(d.fe_ky)[0]]).astype(np.uint64)
    x = d[cols].to_numpy(np.float64)
    res, ok = demean(x, codes, np.ones(len(d)), tol=1e-7, maxiter=200000)
    if not ok:
        raise RuntimeError("fixed-effect demeaning did not converge")
    return pd.DataFrame(res, columns=cols, index=d.index)


ALLV = ["W", "Z", "WZ", "dG", "WdG", "dE"] + CTRL
_CACHE = {}


def demeaned(p, h, groups):
    """Horizon-h estimation sample and its FE-demeaned variables, computed once and reused by
    RF, OLS, 2SLS and AR (Frisch-Waugh-Lovell: identical point estimates to FE regressions)."""
    key = (h, tuple(groups))
    if key not in _CACHE:
        d = p[p.group.isin(groups)].dropna(subset=[f"y{h}", "W", "Z", "dG", "dE"] + CTRL)
        r = fe_demean(d, [f"y{h}"] + ALLV)
        cl = np.column_stack([pd.factorize(d.countryiso3)[0], pd.factorize(d.ym)[0]])
        _CACHE.clear()
        _CACHE[key] = (d, r, cl)
    return _CACHE[key]


def run_rf_ols(p, H, groups):
    rows = []
    for h in range(H + 1):
        d, r, cl = demeaned(p, h, groups)
        for name, reg in [("RF", ["W", "Z", "WZ"]), ("OLS", ["W", "dG", "WdG"])]:
            m = IV2SLS(r[f"y{h}"], r[reg + ["dE"] + CTRL], None, None).fit(cov_type="clustered", clusters=cl)
            for v in reg:
                rows.append(dict(model=name, h=h, term=v, coef=m.params[v], se=m.std_errors[v], n=int(m.nobs)))
        m = IV2SLS(r[f"y{h}"], r[["W", "dE"] + CTRL], r[["dG", "WdG"]], r[["Z", "WZ"]]).fit(cov_type="clustered", clusters=cl)
        fs = m.first_stage.diagnostics
        for v in ("W", "dG", "WdG"):
            rows.append(dict(model="2SLS", h=h, term=v, coef=m.params[v], se=m.std_errors[v], n=int(m.nobs),
                             fs_F_dG=float(fs.loc["dG", "f.stat"]), fs_F_WdG=float(fs.loc["WdG", "f.stat"])))
        rows.extend(ar_rows(d, r, h))
        print(f"h={h} done", flush=True)
    return pd.DataFrame(rows)


def _cluster_meat(S_parts, ids):
    """Two-way (country, month) cluster 'meat' for score contributions.
    S_parts: (n, k) array of per-observation scores; ids: list of integer cluster arrays."""
    out = 0
    for sign, idv in ids:
        G = pd.DataFrame(S_parts).groupby(idv).sum().to_numpy()
        out = out + sign * G.T @ G
    return out


def ar_rows(d, r, h, grid_b=np.linspace(-2, 3, 501), grid_g=np.linspace(-2, 2, 401)):
    """Weak-IV-robust AR confidence sets, two-way clustered (country, month).
    Model: y = b*dG + g*(W x dG) + exog; instruments (Z, W x Z).  Scores z_i*u_i(b,g) are
    linear in (b, g), so cluster sums are computed once and the grid is evaluated in closed form.
    Reports (i) joint AR set projected on b and on g (chi2(2), conservative) and
    (ii) single-endogenous AR set for b using Z only (chi2(1))."""
    from scipy.stats import chi2
    rows = []
    if True:
        X = r[["W", "dE"] + CTRL].to_numpy()
        P = lambda v: v - X @ np.linalg.lstsq(X, v, rcond=None)[0]  # FWL partial-out exog
        y, d1, d2 = P(r[f"y{h}"].to_numpy()), P(r.dG.to_numpy()), P(r.WdG.to_numpy())
        Zm = np.column_stack([P(r.Z.to_numpy()), P(r.WZ.to_numpy())])
        cty = pd.factorize(d.countryiso3)[0]
        ym = pd.factorize(d.date)[0]
        both = pd.factorize(pd.Series(cty).astype(str) + "_" + pd.Series(ym).astype(str))[0]
        ids = [(1, cty), (1, ym), (-1, both)]
        # cluster sums of the score components, computed once per clustering dimension;
        # scores z_i*(y_i - b d1_i - g d2_i) are linear in (b, g)
        def gsum(v, k):
            return [(sg, pd.DataFrame(Zm[:, :k] * v[:, None]).groupby(idv).sum().to_numpy()) for sg, idv in ids]
        Gk = {k: {"y": gsum(y, k), "d1": gsum(d1, k), "d2": gsum(d2, k)} for k in (1, 2)}

        def stat(b, g, k=2):
            G = Gk[k]
            m, V = 0, 0
            for j, (sg, Gy) in enumerate(G["y"]):
                S = Gy - b * G["d1"][j][1] - g * G["d2"][j][1]
                V = V + sg * S.T @ S
                if j == 0:
                    m = S.sum(0)
            return float(m @ np.linalg.pinv(V) @ m)

        # (ii) single endogenous dG, instrument Z only: AR test of y - b*dG on Z
        acc_b = [bb for bb in grid_b if stat(bb, 0.0, k=1) < chi2.ppf(0.95, 1)]
        # (i) joint AR set for (b, g), projected on each coordinate
        crit2 = chi2.ppf(0.95, 2)
        acc = [(bb, gg) for bb in grid_b for gg in grid_g if stat(bb, gg) < crit2]
        gs = [x[1] for x in acc]
        bs = [x[0] for x in acc]
        rows.append(dict(h=h, n=len(d),
                         AR_b_lo=min(acc_b) if acc_b else np.nan, AR_b_hi=max(acc_b) if acc_b else np.nan,
                         AR_b_bounded=bool(acc_b) and min(acc_b) > grid_b[0] and max(acc_b) < grid_b[-1],
                         ARjoint_b_lo=min(bs) if bs else np.nan, ARjoint_b_hi=max(bs) if bs else np.nan,
                         AR_g_lo=min(gs) if gs else np.nan, AR_g_hi=max(gs) if gs else np.nan,
                         AR_g_bounded=bool(gs) and min(gs) > grid_g[0] and max(gs) < grid_g[-1],
                         AR_rejects_g0=(min(gs) > 0 or max(gs) < 0) if gs else None))
    return [dict(model="AR", h=h, term=k, coef=v) for k, v in rows[0].items() if k not in ("h", "n")]


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
    rf.to_csv(f"{OUT}/rf_ols_iv_ar_{tag}.csv", index=False)
    iv = pd.DataFrame()
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
