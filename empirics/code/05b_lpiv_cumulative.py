"""LP-IV with cumulative normalization (Stock & Watson 2018; Jorda, Schularick & Taylor 2015).

For each horizon h the endogenous regressor is the cumulative world price change over the
same window as the outcome:
    y_h  = ln p_{i,t+h} - ln p_{i,t-1}
    G_h  = ln G_{c,t+h} - ln G_{c,t-1}
    y_h = beta_h G_h + gamma_h (W_it x G_h) + delta_h W_it + theta dE + controls + FE
instrumented by [Z_ct, W_it x Z_ct].  beta_h is the cumulative pass-through elasticity.
This corrects 05_estimate.py, which instrumented only the one-month change dG_t although
the exporter-weather shock moves world prices gradually (see RESULTS_first_stage.md).

Inference: two-way clustered (country, month); first-stage F; Anderson-Rubin sets.
Output: output/tables/lpiv_cumulative.csv
"""
import importlib.util
import os
import sys

import numpy as np
import pandas as pd
from linearmodels.iv import IV2SLS

HERE = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location("e", os.path.join(HERE, "05_estimate.py"))
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)

HS = [int(x) for x in os.environ.get("HORIZONS", "0,2,4,6,8,12").split(",")]


def run(p, groups, tag):
    p = p.sort_values(["series", "date"]).copy()
    g = p.groupby("series")
    rows = []
    for h in HS:
        p["Gh"] = g.lG.shift(-h) - g.lG.shift(1)
        p["WGh"] = p.W * p.Gh
        d = p[p.group.isin(groups)].dropna(subset=[f"y{h}", "Gh", "W", "Z", "dE"] + e.CTRL)
        cols = [f"y{h}", "Gh", "WGh", "W", "Z", "WZ", "dE"] + e.CTRL
        r = e.fe_demean(d, cols)
        cl = np.column_stack([pd.factorize(d.countryiso3)[0], pd.factorize(d.ym)[0]])
        ex = r[["W", "dE"] + e.CTRL]
        # single endogenous (pass-through only) and two endogenous (with drought interaction)
        m1 = IV2SLS(r[f"y{h}"], ex, r[["Gh"]], r[["Z"]]).fit(cov_type="clustered", clusters=cl)
        m2 = IV2SLS(r[f"y{h}"], ex, r[["Gh", "WGh"]], r[["Z", "WZ"]]).fit(cov_type="clustered", clusters=cl)
        ols = IV2SLS(r[f"y{h}"], pd.concat([ex, r[["Gh", "WGh"]]], axis=1), None, None).fit(cov_type="clustered", clusters=cl)
        fs1 = m1.first_stage.diagnostics
        fs2 = m2.first_stage.diagnostics
        for mod, m, terms in (("LPIV-1", m1, ["Gh", "W"]), ("LPIV-2", m2, ["Gh", "WGh", "W"]), ("OLS-cum", ols, ["Gh", "WGh", "W"])):
            for v in terms:
                rows.append(dict(model=mod, h=h, term=v, coef=m.params[v], se=m.std_errors[v], n=int(m.nobs),
                                 F_Gh=float(fs1.loc["Gh", "f.stat"]) if mod == "LPIV-1" else float(fs2.loc["Gh", "f.stat"]),
                                 F_WGh=float(fs2.loc["WGh", "f.stat"]) if mod == "LPIV-2" else np.nan))
        # Anderson-Rubin on the cumulative design
        r2 = r.rename(columns={"Gh": "dG", "WGh": "WdG"})
        rows.extend(e.ar_rows(d, r2, h))
        print(f"h={h} n={len(d)} F1={fs1.loc['Gh','f.stat']:.1f} beta={m1.params['Gh']:.3f} ({m1.std_errors['Gh']:.3f})", flush=True)
    out = pd.DataFrame(rows)
    out.to_csv(f"{e.OUT}/lpiv_cumulative_{tag}.csv", index=False)
    return out


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else f"{e.ROOT}/data/processed/panel.parquet"
    tag = os.path.splitext(os.path.basename(path))[0]
    p = e.prepare(pd.read_parquet(path), max(HS))
    out = run(p, ["wheat", "maize", "rice"], tag)
    pd.set_option("display.width", 220)
    x = out[out.model != "AR"].assign(t=lambda d: d.coef / d.se)
    print(x.pivot_table(index="h", columns=["model", "term"], values=["coef", "t"]).round(3).to_string())
    print(out[out.model == "AR"].pivot(index="h", columns="term", values="coef").to_string())
