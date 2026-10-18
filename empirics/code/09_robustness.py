"""Robustness of the main local-weather effect (EXPLORATORY: not in PAP_local_weather.md).

Horizons h = 4, 6. Each row changes one element of the main specification:
  R1 drop crisis/hyperinflation economies (VEN, ZWE, LBN, SYR, SDN, SSD, YEM, AFG, MMR, HTI)
  R2 outcome in USD prices instead of local currency (dE dropped)
  R3 one-way clustering by country
  R4 sample ends 2019-12 (before WFP coverage expansion and COVID)
  R5 monthly innovation of W (W_t - W_{t-1}, standardized) instead of the level
  R6 cereals only (wheat, maize, rice, coarse)
Output: output/tables/robustness.csv
"""
import importlib.util
import os

import numpy as np
import pandas as pd
from linearmodels.iv import IV2SLS

HERE = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location("lw", os.path.join(HERE, "06_local_weather.py"))
lw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lw)
CRISIS = {"VEN", "ZWE", "LBN", "SYR", "SDN", "SSD", "YEM", "AFG", "MMR", "HTI"}
HS = (4, 6)


def est(d, h, ycol, X, ctrl, cluster="twoway"):
    d = d.dropna(subset=[ycol] + X + ctrl)
    r = lw.fe_demean(d, [ycol] + X + ctrl)
    cl = (np.column_stack([pd.factorize(d.countryiso3)[0], pd.factorize(d.date)[0]]) if cluster == "twoway"
          else pd.factorize(d.countryiso3)[0])
    m = IV2SLS(r[ycol], r[X + ctrl], None, None).fit(cov_type="clustered", clusters=cl)
    return m.params[X[0]], m.std_errors[X[0]], int(m.nobs)


if __name__ == "__main__":
    p = lw.load(list(HS))
    g = p.groupby("series")
    p["lusd"] = np.log(p.usdprice.where(p.usdprice > 0))
    for h in HS:
        p[f"yusd{h}"] = g.lusd.shift(-h) - g.lusd.shift(1)
    # one-month index from the monthly components already in the panel is not available
    # (panel stores 3-month aggregates); use the 1-month change of the 3-month index as a proxy shock
    p["W1"] = (p.W - g.W.shift(1)) / (p.W - g.W.shift(1)).std()
    rows = []
    ctrl = lw.CTRL
    ctrl_nofx = [c for c in ctrl if c != "dE"]
    for h in HS:
        y = f"y{h}"
        cases = [
            ("baseline", p, y, ctrl, "twoway"),
            ("R1 drop crisis economies", p[~p.countryiso3.isin(CRISIS)], y, ctrl, "twoway"),
            ("R2 USD prices", p, f"yusd{h}", ctrl_nofx, "twoway"),
            ("R3 cluster by country only", p, y, ctrl, "country"),
            ("R4 sample to 2019", p[p.date <= "2019-12-01"], y, ctrl, "twoway"),
            ("R6 cereals only", p[p.group != "nontraded"], y, ctrl, "twoway"),
        ]
        for name, d, ycol, c, clu in cases:
            b, se, n = est(d, h, ycol, ["W"], c, clu)
            rows.append(dict(check=name, h=h, coef=b, se=se, t=b / se, n=n))
            print(name, h, round(100 * b, 3), round(b / se, 2), n, flush=True)
        b, se, n = est(p, h, y, ["W1"], [x for x in ctrl if not x.startswith("W_l")], "twoway")
        rows.append(dict(check="R5 monthly innovation of W", h=h, coef=b, se=se, t=b / se, n=n))
        print("R5", h, round(100 * b, 3), round(b / se, 2), n, flush=True)
        pd.DataFrame(rows).to_csv(f"{lw.OUT}/robustness.csv", index=False)
