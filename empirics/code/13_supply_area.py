"""Supply-area weather (EXPLORATORY; not in PAP_local_weather.md; referee point 1).

The baseline measures weather at the market's own 0.25 deg ERA5 cell. Food sold in a market is grown
in its hinterland, so point weather is a noisy proxy for the relevant supply shock and attenuates
delta_h. Here heat (HDD30 / Tmean) and soil moisture are averaged over all ERA5 land cells within
R km of the market (R = 50, 100, 200), and W is rebuilt exactly as in the baseline (3-month aggregates,
1991-2020 market x calendar-month climatology, sd floor, clip +/-4). GPCP rainfall (2.5 deg, about
275 km) is already an area measure and is unchanged.

Re-estimated with the main specification (Eq. 2), two-way clustered by country and month:
  main          delta_h, h = 0, 2, ..., 12
  tradability   W and W x group (reference rice), h = 2, 4, 6
  horse race    W_point and W_R jointly, h = 6
Output: output/tables/supply_area.csv
"""
import importlib.util
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(__file__)


def _mod(name, f):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


lw = _mod("lw", "06_local_weather.py")
bp = _mod("bp", "04_build_wfp_panel.py")
PROC, OUT = f"{lw.ROOT}/data/processed", lw.OUT
RADII = (50, 100, 200)
H_MAIN = (0, 2, 4, 6, 8, 10, 12)
H_TRADE = (2, 4, 6)
TRADE = ["W", "W_x_wheat", "W_x_maize", "W_x_coarse", "W_x_nontraded"]
ZCOLS = ["z_tmean", "z_hdd30", "z_swvl1", "z_precip", "z_heat", "W"]


def fit(p, h, X):
    d = p.dropna(subset=[f"y{h}"] + X + lw.CTRL)
    r = lw.fe_demean(d, list(dict.fromkeys([f"y{h}"] + X + lw.CTRL)))
    cl = np.column_stack([pd.factorize(d.countryiso3)[0], pd.factorize(d.date)[0]])
    return lw.ols(r, f"y{h}", list(dict.fromkeys(X + lw.CTRL)), cl)


def estimate(p, label, rows):
    for h in H_MAIN:
        m = fit(p, h, ["W"])
        rows.append(dict(weather=label, spec="main", h=h, term="W", coef=m.params["W"], se=m.std_errors["W"], n=int(m.nobs)))
        print(f"{label} h={h} delta={100 * m.params['W']:.2f} se={100 * m.std_errors['W']:.2f}", flush=True)
    for h in H_TRADE:
        m = fit(p, h, TRADE)
        rows += [dict(weather=label, spec="tradability", h=h, term=v, coef=m.params[v], se=m.std_errors[v], n=int(m.nobs)) for v in TRADE]


if __name__ == "__main__":
    base = pd.read_parquet(f"{PROC}/panel.parquet")
    mk = base.groupby("mkey", as_index=False)[["latitude", "longitude"]].first()
    rows = []
    estimate(lw.load(list(H_MAIN)), "point (baseline)", rows)
    pt = base[["mkey", "date", "W"]].drop_duplicates(["mkey", "date"]).rename(columns={"W": "W_point"})
    for R in RADII:
        Wr = bp.local_weather(mk, base.date.unique(), radius_km=R)
        path = f"{PROC}/panel_supply{R}.parquet"
        base.drop(columns=ZCOLS).merge(Wr[["mkey", "date"] + ZCOLS], on=["mkey", "date"], how="left").to_parquet(path, index=False)
        p = lw.load(list(H_MAIN), path)
        cor = pt.merge(Wr[["mkey", "date", "W"]], on=["mkey", "date"]).dropna()[["W_point", "W"]].corr().iloc[0, 1]
        print(f"R={R} km: corr(W_point, W_R) = {cor:.3f}", flush=True)
        rows.append(dict(weather=f"{R} km", spec="corr_with_point", h=np.nan, term="W", coef=cor, se=np.nan, n=np.nan))
        estimate(p, f"{R} km", rows)
        q = p.merge(pt, on=["mkey", "date"], how="left")
        m = fit(q, 6, ["W", "W_point"])
        rows += [dict(weather=f"{R} km", spec="horse_race", h=6, term=v, coef=m.params[v], se=m.std_errors[v], n=int(m.nobs)) for v in ("W", "W_point")]
        os.remove(path)
        pd.DataFrame(rows).to_csv(f"{OUT}/supply_area.csv", index=False)
    print(pd.DataFrame(rows).query("spec=='main' and h==6"))
