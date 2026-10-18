"""Pre-declared first-stage variants (all reported; no selection on significance).

V1  composite adverse index (baseline in proposal)
V2  extreme-heat component only (Schlenker-Roberts mechanism)
V3  V2, sample 2000-2026 (WFP sample period)
V4  season-to-date cumulative heat (markets price accumulated crop news)
V5  V2 with the wheat weights on Russia/Ukraine/Kazakhstan doubled, reflecting the Black Sea rise
    (robustness to the pre-sample share choice)
Output: output/tables/first_stage_variants.csv  (h, beta, se, t, F) and figure.
"""
import os

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import importlib.util

ROOT = os.path.join(os.path.dirname(__file__), "..")
spec = importlib.util.spec_from_file_location("fs", os.path.join(os.path.dirname(__file__), "03_first_stage.py"))
fs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fs)

ew = pd.read_csv(f"{ROOT}/data/processed/exporter_weather.csv", parse_dates=["date"])
ew["year"] = ew.date.dt.year


def season_cum(e, col):
    e = e.sort_values("date").copy()
    # season id: consecutive in-season months within region
    e["sid"] = (~e.in_season).groupby([e.commodity, e.region]).cumsum()
    e["cum"] = e[col].fillna(0).where(e.in_season, 0).groupby([e.commodity, e.region, e.sid]).cumsum()
    return e


def build(e, col, cum=False, share_adj=None):
    e = e.copy()
    if share_adj:
        e["share"] = e.share * e.region.map(share_adj).fillna(1.0)
        e["share"] = e.share / e.groupby(["date", "commodity"]).share.transform("sum")
    if cum:
        e = season_cum(e, col)
        v = e.cum / np.sqrt(e.groupby(["commodity", "region", "sid"]).cumcount() + 1)
    else:
        v = e[col].fillna(0)
    e["v"] = v * e.share * e.in_season
    return e.groupby(["date", "commodity"]).v.sum().rename("Zv").reset_index()


def run(z, sample_start="1992-01-01"):
    d = fs.df.drop(columns=[c for c in fs.df.columns if c.startswith("Zv")]).merge(z, on=["date", "commodity"])
    g = d.groupby("commodity")
    for l in (1, 2, 3):
        d[f"Zv_l{l}"] = g.Zv.shift(l)
    return fs.lp("Zv", d[d.date >= sample_start])


variants = {
    "V1 composite": (build(ew, "adverse"), "1992-01-01"),
    "V2 heat": (build(ew, "z_heat"), "1992-01-01"),
    "V3 heat, 2000+": (build(ew, "z_heat"), "2000-01-01"),
    "V4 heat, season-cumulative": (build(ew, "z_heat", cum=True), "1992-01-01"),
    "V5 heat, Black Sea x2": (build(ew, "z_heat", share_adj={"Russia_south": 2, "Ukraine": 2, "Kazakhstan": 2}), "1992-01-01"),
}

if __name__ == "__main__":
    out = pd.concat([run(z, s).assign(variant=k) for k, (z, s) in variants.items()])
    out.to_csv(f"{ROOT}/output/tables/first_stage_variants.csv", index=False)
    pd.set_option("display.width", 200)
    print(out.pivot(index="h", columns="variant", values="F").round(1))
    print(out.pivot(index="h", columns="variant", values="beta").mul(100).round(2))

    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    for k, col in zip(["V2 heat", "V3 heat, 2000+", "V4 heat, season-cumulative"], ["#2a6f97", "#c44536", "#6a994e"]):
        s = out[out.variant == k]
        ax.plot(s.h, 100 * s.beta, color=col, lw=2, marker="o", ms=3, label=k)
        ax.fill_between(s.h, 100 * (s.beta - 1.96 * s.se), 100 * (s.beta + 1.96 * s.se), color=col, alpha=0.12, lw=0)
    ax.axhline(0, color="#888", lw=0.8)
    ax.set_xlabel("Months after shock (h)")
    ax.set_ylabel("World cereal price response (%)")
    ax.legend(frameon=False, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{ROOT}/output/figures/first_stage_variants.png", dpi=200)
