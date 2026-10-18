"""Paper figures from output/tables/lw_main.csv (and het_terciles.csv if present).

Fig 1  main impulse response of local prices to a 1-s.d. adverse local weather shock
Fig 2  tradability: differential response vs rice (reference), by product group
Fig 3  channels: rainfall deficit, soil dryness, heat (entered jointly)
95% CIs from two-way (country, month) clustered SEs. Categorical palette validated with
dataviz/scripts/validate_palette.js; series also carry markers, line styles and direct labels.
"""
import os

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(__file__), "..")
T, F = f"{ROOT}/output/tables", f"{ROOT}/output/figures"
os.makedirs(F, exist_ok=True)
PAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
INK, MUTED, GRID = "#1a1a19", "#6b6a63", "#e4e3dc"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})

r = pd.read_csv(f"{T}/lw_main.csv")
r[["coef", "se"]] *= 100  # percent


def base(ax, ylabel):
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_xlabel("Months after shock")
    ax.set_ylabel(ylabel)
    ax.set_xticks(sorted(r.h.unique()))


def series(ax, s, color, label, marker="o", ls="-", offset=0.0):
    s = s.sort_values("h")
    x = s.h + offset
    ax.fill_between(x, s.coef - 1.96 * s.se, s.coef + 1.96 * s.se, color=color, alpha=0.12, lw=0)
    ax.plot(x, s.coef, color=color, lw=2, ls=ls, marker=marker, ms=4.5, label=label)
    last = s.iloc[-1]
    ax.annotate(label, (x.iloc[-1], last.coef), xytext=(6, 0), textcoords="offset points", va="center", color=INK, fontsize=8)


# Fig 1
fig, ax = plt.subplots(figsize=(6.2, 3.6))
series(ax, r[(r.spec == "main") & (r.term == "W")], PAL[0], "All staples")
base(ax, "Local price response (%)")
ax.set_title("Local food prices after a 1-s.d. adverse local weather shock", fontsize=10, color=INK, loc="left")
fig.tight_layout()
fig.savefig(f"{F}/fig1_main_irf.png", dpi=300)



def panels(items, spec, ylabel, title, fname, ncols):
    n = len(items)
    nrows = -(-n // ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(3.2 * ncols, 2.6 * nrows), sharey=True, squeeze=False)
    for ax, (term, lab), c, mk in zip(axes.flat, items, PAL, ["o", "s", "^", "D"]):
        s = r[(r.spec == spec) & (r.term == term)].sort_values("h")
        ax.fill_between(s.h, s.coef - 1.96 * s.se, s.coef + 1.96 * s.se, color=c, alpha=0.15, lw=0)
        ax.plot(s.h, s.coef, color=c, lw=2, marker=mk, ms=4.5)
        ax.set_title(lab, fontsize=9, color=INK, loc="left")
        base(ax, ylabel if ax in axes[:, 0] else "")
        if ax not in axes[-1]:
            ax.set_xlabel("")
    for ax in list(axes.flat)[n:]:
        ax.set_visible(False)
    fig.suptitle(title, fontsize=10, color=INK, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(f"{F}/{fname}", dpi=300)


panels([("W_x_maize", "Maize"), ("W_x_coarse", "Sorghum / millet"), ("W_x_nontraded", "Cassava / yam / plantain"), ("W_x_wheat", "Wheat")],
       "tradability", "Extra response vs rice (pp)",
       "Who pays for local droughts? Differential response by staple (reference: rice)", "fig2_tradability.png", 2)
panels([("c_rain", "Rainfall deficit"), ("c_dry", "Soil dryness"), ("c_heat", "Heat")],
       "components", "Price response (%)", "Channels: weather components entered jointly (per 1 s.d.)", "fig3_components.png", 3)
print("figures written")
