"""First stage: do exporter-region weather shocks move world cereal prices?

Local projections, h = 0..12, pooled over wheat/maize/rice (commodity x calendar-month FE):
  ln P_{c,t+h} - ln P_{c,t-1} = b_h Z_{c,t} + sum_{l=1..3}(rho_l dlnP_{c,t-l} + phi_l Z_{c,t-l}) + a_{c,m} + e
Inference: Driscoll-Kraay (time-clustered HAC) standard errors with h+1 lags.
With one instrument the HAC-robust F equals t^2 and coincides with the
Montiel Olea-Pflueger effective F.
Outputs: output/tables/first_stage_lp.csv, output/figures/first_stage_lp.png
"""
import os

import matplotlib
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(__file__), "..")
os.makedirs(f"{ROOT}/output/tables", exist_ok=True)
os.makedirs(f"{ROOT}/output/figures", exist_ok=True)

p = pd.read_csv(f"{ROOT}/data/raw/world_cereal_prices_imf_fred.csv", parse_dates=["date"])
p = p.melt("date", var_name="commodity", value_name="price").dropna()
z = pd.read_csv(f"{ROOT}/data/processed/instrument.csv", parse_dates=["date"])
df = p.merge(z, on=["date", "commodity"]).sort_values(["commodity", "date"])
df["lp"] = np.log(df.price)
g = df.groupby("commodity")
df["dlp"] = g.lp.diff()
for l in (1, 2, 3):
    df[f"dlp_l{l}"] = g.dlp.shift(l)
for zc in ("Z", "Z_heat", "Z_sm", "Z_pr"):
    for l in (1, 2, 3):
        df[f"{zc}_l{l}"] = g[zc].shift(l)
df["cm"] = df.commodity + "_" + df.date.dt.month.astype(str)
df["tid"] = df.date.rank(method="dense").astype(int)


def lp(zcol, sample, H=12):
    res = []
    for h in range(H + 1):
        d = sample.copy()
        d["y"] = d.groupby("commodity").lp.shift(-h) - d.groupby("commodity").lp.shift(1)
        ctrl = " + ".join([f"dlp_l{l}" for l in (1, 2, 3)] + [f"{zcol}_l{l}" for l in (1, 2, 3)])
        d = d.dropna(subset=["y", zcol, f"{zcol}_l3", "dlp_l3"])
        m = smf.ols(f"y ~ {zcol} + {ctrl} + C(cm)", d).fit(
            cov_type="nw-groupsum", cov_kwds={"time": d.tid.values, "groups": pd.factorize(d.commodity)[0], "maxlags": h + 1})
        b, se = m.params[zcol], m.bse[zcol]
        res.append(dict(instrument=zcol, h=h, beta=b, se=se, t=b / se, F=(b / se) ** 2, n=int(m.nobs)))
    return pd.DataFrame(res)


if __name__ == "__main__":
    full = df[df.date >= "1992-01-01"]
    out = pd.concat([lp(zc, full) for zc in ("Z", "Z_heat", "Z_sm", "Z_pr")]
                    + [lp("Z", df[(df.commodity == c) & (df.date >= "1992-01-01")]).assign(instrument=f"Z|{c}")
                       for c in ("wheat", "maize", "rice")])
    out.to_csv(f"{ROOT}/output/tables/first_stage_lp.csv", index=False)
    print(out[out.instrument.isin(["Z", "Z_heat", "Z_sm", "Z_pr"])].pivot(index="h", columns="instrument", values=["beta", "t"]).round(3))
    print(out[out.instrument.str.startswith("Z|")].pivot(index="h", columns="instrument", values="t").round(2))

    s = out[out.instrument == "Z"]
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.axhline(0, color="#888", lw=0.8)
    ax.fill_between(s.h, 100 * (s.beta - 1.96 * s.se), 100 * (s.beta + 1.96 * s.se), color="#2a6f97", alpha=0.18, lw=0)
    ax.plot(s.h, 100 * s.beta, color="#2a6f97", lw=2, marker="o", ms=3)
    ax.set_xlabel("Months after shock (h)")
    ax.set_ylabel("World price response (%)")
    ax.set_title("World cereal prices after a 1-s.d. adverse exporter-weather shock", fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{ROOT}/output/figures/first_stage_lp.png", dpi=200)
