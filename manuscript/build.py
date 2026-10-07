"""Fill result tables from empirics/output/tables into the manuscript template and build .docx.
Usage: python build.py   (requires pandoc)"""
import re, subprocess, pandas as pd
from scipy.stats import norm
T = "../empirics/output/tables/"
F = "../empirics/output/figures/"

def star(t):
    p = 2 * norm.sf(abs(t))
    return "***" if p < .01 else "**" if p < .05 else "*" if p < .1 else ""

def table7():
    rb = pd.read_csv(T + "robustness.csv"); rb = rb[rb.h == 6]
    sv = pd.read_csv(T + "sensitivity.csv"); w = pd.read_csv(T + "winsorized.csv"); w = w[w.h == 6]
    g = lambda df, k: df[df.check == k].iloc[0]
    rows = []
    def add(threat, name, x):
        t = x.coef / x.se
        rows.append(f"| {threat} | {name} | {100*x.coef:.2f}{star(t)} | {100*x.se:.2f} | {t:.2f} | {int(x.n):,} |")
    add("Baseline", "Table 2, h = 6", g(sv, "baseline"))
    for k, lab in [("R1 drop crisis economies", "Drop 10 crisis/hyperinflation economies"), ("R4 sample to 2019", "Sample ends December 2019"), ("R6 cereals only", "Cereals only")]:
        add("Sample", lab, g(rb, k))
    add("Sample", "Series monitored before 2010", g(sv, "S2a series monitored before 2010"))
    for k, lab in [("S1 window 1 month", "W aggregated over 1 month"), ("S1 window 2 months", "W aggregated over 2 months"), ("S1 window 6 months", "W aggregated over 6 months"), ("S1 clip 3", "z-scores capped at ±3"), ("S1 clip 5", "z-scores capped at ±5"), ("S1 no clipping", "No cap on z-scores"), ("S1 detrended W", "Market-specific detrending of W")]:
        add("Measurement", lab, g(sv, k))
    add("Measurement", "Prices in US dollars", g(rb, "R2 USD prices"))
    add("Measurement", "Monthly innovation of W instead of level", g(rb, "R5 monthly innovation of W"))
    for _, x in w.iterrows():
        add("Specification", "Outcome winsorized at " + x.winsor.replace("/", " and "), x)
    add("Inference", "Clustered by country only", g(rb, "R3 cluster by country only"))
    add("Inference", "Clustered by 2° cell × month", g(sv, "S3 cluster 2deg cell x month"))
    add("Inference", "Clustered by 5° cell × month", g(sv, "S3 cluster 5deg cell x month"))
    return "| Threat | Variant | δ₆ (%) | SE | t | N |\n|---|---|---|---|---|---|\n" + "\n".join(rows), w.iloc[0]

def table6():
    t6 = open("table6.md").read()
    for a, b in {"| import dependence |": "| Import dependence |", "| conflict |": "| Conflict exposure |", "| remoteness |": "| Remoteness |", "| joint |": "| Joint |",
                 "| W_x_import_dep |": "| W × import dependence |", "| W_x_conflict |": "| W × conflict |", "| W_x_remote |": "| W × remoteness |", "| conflict_z |": "| Conflict (level) |"}.items():
        t6 = t6.replace(a, b)
    return t6

s = open("empirical_section.md").read()
t7, ww = table7()
s = s.replace("{{WINS6}}", f"{100*ww.coef:.2f} percent (SE {100*ww.se:.2f})")
def widen(tab):
    out = []
    for line in tab.split("\n"):
        if line.startswith("|---"):
            n = line.count("|") - 1
            line = "|" + "-" * 24 + "|" + "|".join(["-" * 13] * (n - 1)) + "|"
        out.append(line)
    return "\n".join(out)
for i, tab in [(1, open("table1.md").read()), (2, open("table2.md").read()), (3, open("table3.md").read()), (4, open("table4.md").read()), (5, open("table5.md").read()), (6, table6()), (7, t7)]:
    s = s.replace("{{TABLE%d}}" % i, widen(tab))
assert "{{" not in s
figs = (
    "\n# Figures\n\n"
    f"![Figure 1. Cumulative response of local staple prices to a one-standard-deviation adverse local weather shock. Shaded area: 95 percent confidence interval, two-way clustered by country and month.]({F}fig1_main_irf.png){{width=95%}}\n\n"
    f"![Figure 2. Differential response by staple group relative to rice (percentage points). Shaded areas: 95 percent confidence intervals.]({F}fig2_tradability.png){{width=100%}}\n\n"
    f"![Figure 3. Response to each weather component, entered jointly (percent per one standard deviation). Shaded areas: 95 percent confidence intervals.]({F}fig3_components.png){{width=100%}}\n"
)
s = s.replace("# References", figs + "\n# References", 1)
open("empirical_section_filled.md", "w").write(s)
subprocess.run(["pandoc", "empirical_section_filled.md", "-o", "Empirical_section_Food_Policy_draft.docx", "--resource-path=."], check=True)
body = s.split("# Figures")[0]
tot = 0
for sec in re.split(r"\n# ", body)[1:]:
    title = sec.split("\n")[0]; txt = re.sub(r"\|.*\|", "", sec); txt = re.sub(r"\$\$.*?\$\$", "", txt, flags=re.S); n = len(txt.split()); tot += n
    print(f"{title}: {n} words")
print("Empirical part total:", tot)
