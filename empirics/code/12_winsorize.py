"""Exploratory robustness: main effect with the outcome winsorized at the 1st/99th and
0.5th/99.5th percentiles (h = 4, 6). Output: output/tables/winsorized.csv"""
import importlib.util, os
import numpy as np, pandas as pd
from linearmodels.iv import IV2SLS
spec = importlib.util.spec_from_file_location("lw", os.path.join(os.path.dirname(__file__), "06_local_weather.py"))
lw = importlib.util.module_from_spec(spec); spec.loader.exec_module(lw)
rows = []
p = lw.load([4, 6])
for h in (4, 6):
    d = p.dropna(subset=[f"y{h}", "W"] + lw.CTRL).copy()
    for lo, hi in ((0.01, 0.99), (0.005, 0.995)):
        q = d[f"y{h}"].quantile([lo, hi]).values
        d["yw"] = d[f"y{h}"].clip(*q)
        r = lw.fe_demean(d, ["yw", "W"] + lw.CTRL)
        cl = np.column_stack([pd.factorize(d.countryiso3)[0], pd.factorize(d.date)[0]])
        m = IV2SLS(r.yw, r[["W"] + lw.CTRL], None, None).fit(cov_type="clustered", clusters=cl)
        rows.append(dict(h=h, winsor=f"{lo}/{hi}", coef=m.params["W"], se=m.std_errors["W"], t=m.params["W"] / m.std_errors["W"], n=int(m.nobs)))
        print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv(f"{lw.OUT}/winsorized.csv", index=False)
