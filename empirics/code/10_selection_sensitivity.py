"""Referee-proofing for the local-weather paper (EXPLORATORY; not in the PAP).

S1  Index sensitivity at h = 6: aggregation window 1/2/6 months, clipping +/-3, +/-5, none,
    market-specific detrending of W.
S2  Sample selection:
    (a) markets already monitored before 2010 (coverage not triggered by recent shocks);
    (b) entry test: does local weather predict the month WFP starts monitoring a market?
        Linear probability of entry on W_{t-1..t-3} over market-months up to entry,
        country x year FE, clustered by country.
S3  Spatial inference at h = 6: two-way clusters (grid cell x month) for 2 deg and 5 deg cells.
S4  Multiple testing across the 7 horizons of the main effect: Holm and Bonferroni.
Output: output/tables/sensitivity.csv, selection_entry.csv, multiple_testing.csv
"""
import importlib.util
import os

import numpy as np
import pandas as pd
import pyfixest as pf
from linearmodels.iv import IV2SLS
from scipy.stats import norm

HERE = os.path.dirname(__file__)


def _mod(name, f):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


lw = _mod("lw", "06_local_weather.py")
bp = _mod("bp", "04_build_wfp_panel.py")
H = 6
OUT = lw.OUT


def est(d, X, ctrl, clusters):
    d = d.dropna(subset=[f"y{H}"] + X + ctrl)
    r = lw.fe_demean(d, [f"y{H}"] + X + ctrl)
    m = IV2SLS(r[f"y{H}"], r[X + ctrl], None, None).fit(cov_type="clustered", clusters=clusters(d))
    return m.params[X[0]], m.std_errors[X[0]], int(m.nobs)


twoway = lambda d: np.column_stack([pd.factorize(d.countryiso3)[0], pd.factorize(d.date)[0]])


def with_W(p, Wdf):
    q = p.drop(columns=["W"] + [f"W_l{l}" for l in (1, 2, 3)]).merge(Wdf[["mkey", "date", "W"]], on=["mkey", "date"], how="left")
    q = q.sort_values(["series", "date"])
    g = q.groupby("series")
    for l in (1, 2, 3):
        q[f"W_l{l}"] = g.W.shift(l)
    return q


def multiple_testing():
    r = pd.read_csv(f"{OUT}/lw_main.csv")
    m = r[(r.spec == "main") & (r.term == "W")].sort_values("h").copy()
    m["p"] = 2 * norm.sf(np.abs(m.coef / m.se))
    k = len(m)
    m["p_bonferroni"] = np.minimum(1, m.p * k)
    order = np.argsort(m.p.values)
    holm = np.empty(k)
    running = 0
    for rank, i in enumerate(order):
        running = max(running, min(1, (k - rank) * m.p.values[i]))
        holm[i] = running
    m["p_holm"] = holm
    m[["h", "coef", "se", "p", "p_bonferroni", "p_holm"]].to_csv(f"{OUT}/multiple_testing.csv", index=False)
    print(m[["h", "coef", "p", "p_bonferroni", "p_holm"]].round(4).to_string(), flush=True)


def entry_test(p):
    first = p.dropna(subset=["lp"]).groupby("mkey").date.min().rename("entry")
    mk = p.groupby("mkey", as_index=False)[["latitude", "longitude", "countryiso3"]].first().merge(first, on="mkey")
    mk = mk[mk.entry >= "2001-01-01"]  # entries observable after the panel start
    dates = pd.date_range("2000-01-01", "2026-09-01", freq="MS")
    W = bp.local_weather(mk[["mkey", "latitude", "longitude"]], dates)
    W = W.merge(mk[["mkey", "countryiso3", "entry"]], on="mkey")
    W = W[W.date <= W.entry].sort_values(["mkey", "date"])
    g = W.groupby("mkey")
    for l in (1, 2, 3):
        W[f"W_l{l}"] = g.W.shift(l)
    W["entry_now"] = (W.date == W.entry).astype(float) * 100  # percentage points
    W["fe_ky"] = W.countryiso3 + "_" + W.date.dt.year.astype(str)
    W["Wbar3"] = W[["W_l1", "W_l2", "W_l3"]].mean(1)
    m = pf.feols("entry_now ~ Wbar3 | fe_ky + mkey", W.dropna(subset=["Wbar3"]), vcov={"CRV1": "countryiso3"})
    t = m.tidy()
    out = pd.DataFrame([dict(test="entry on mean W(t-1..t-3)", coef_pp=t.loc["Wbar3", "Estimate"], se=t.loc["Wbar3", "Std. Error"],
                             t=t.loc["Wbar3", "t value"], n=m._N, mean_entry_pp=W.entry_now.mean())])
    out.to_csv(f"{OUT}/selection_entry.csv", index=False)
    print(out.round(4).to_string(), flush=True)


if __name__ == "__main__":
    multiple_testing()
    p = lw.load([H])
    rows = []

    def add(name, b, se, n):
        rows.append(dict(check=name, h=H, coef=b, se=se, t=b / se, n=n))
        print(name, round(100 * b, 3), round(b / se, 2), n, flush=True)
        pd.DataFrame(rows).to_csv(f"{OUT}/sensitivity.csv", index=False)

    add("baseline", *est(p, ["W"], lw.CTRL, twoway))
    # S3 spatial clusters
    for deg in (2, 5):
        cell = lambda d, deg=deg: (np.floor(d.latitude / deg).astype(int).astype(str) + "_" + np.floor(d.longitude / deg).astype(int).astype(str))
        add(f"S3 cluster {deg}deg cell x month", *est(p, ["W"], lw.CTRL,
            lambda d, cell=cell: np.column_stack([pd.factorize(cell(d))[0], pd.factorize(d.date)[0]])))
    # S2a markets monitored before 2010
    first = p.dropna(subset=["lp"]).groupby("series").date.min()
    old = first[first < "2010-01-01"].index
    add("S2a series monitored before 2010", *est(p[p.series.isin(old)], ["W"], lw.CTRL, twoway))
    # S1 index variants
    mk = p.groupby("mkey", as_index=False)[["latitude", "longitude"]].first()
    dates = p.date.unique()
    for name, kw in [("S1 window 1 month", dict(window=1)), ("S1 window 2 months", dict(window=2)),
                     ("S1 window 6 months", dict(window=6)), ("S1 clip 3", dict(clip=3.0)),
                     ("S1 clip 5", dict(clip=5.0)), ("S1 no clipping", dict(clip=None)),
                     ("S1 detrended W", dict(detrend=True))]:
        q = with_W(p, bp.local_weather(mk, dates, **kw))
        add(name, *est(q, ["W"], lw.CTRL, twoway))
    entry_test(p)
