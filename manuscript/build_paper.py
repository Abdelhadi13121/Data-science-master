"""Assemble the full Food Policy manuscript from paper_front.md, empirical_section.md and
paper_back.md; fill every table from empirics/output/tables; check citations; count words;
write anonymized manuscript, title page and highlights as .docx.  Usage: python build_paper.py"""
import re, subprocess, importlib.util, pandas as pd
from scipy.stats import norm

spec = importlib.util.spec_from_file_location("b", "build.py")
T = "../empirics/output/tables/"
F = "../empirics/output/figures/"

def star(t):
    p = 2 * norm.sf(abs(t)); return "***" if p < .01 else "**" if p < .05 else "*" if p < .1 else ""

def widen(tab, first=24, rest=13):
    out = []
    for line in tab.split("\n"):
        if line.startswith("|---"):
            n = line.count("|") - 1
            line = "|" + "-" * first + "|" + "|".join(["-" * rest] * (n - 1)) + "|"
        out.append(line)
    return "\n".join(out)

def tableA1():
    a = pd.read_csv(T + "first_stage_variants.csv")
    H = [0, 2, 4, 6, 8, 12]
    rows = ["| Index | " + " | ".join(f"h = {h}" for h in H) + " |", "|---|" + "---|" * len(H)]
    for v, lab in [("V2 heat", "Extreme heat (preferred)"), ("V3 heat, 2000+", "Extreme heat, 2000–2026"), ("V1 composite", "Composite (heat, soil, rain)")]:
        x = a[a.variant == v].set_index("h")
        rows.append(f"| {lab} | " + " | ".join(f"{100*x.loc[h,'beta']:.2f} [F {x.loc[h,'F']:.1f}]" for h in H) + " |")
    return "\n".join(rows)

def tableA2():
    b = pd.read_csv(T + "lpiv_cumulative_panel.csv")
    H = sorted(b.h.unique())
    rows = ["| | " + " | ".join(f"h = {h}" for h in H) + " |", "|---|" + "---|" * len(H)]
    iv = b[(b.model == "LPIV-1") & (b.term == "Gh")].set_index("h").astype({"coef": float, "se": float})
    ols = b[(b.model == "OLS-cum") & (b.term == "Gh")].set_index("h").astype({"coef": float, "se": float})
    ar = b[b.model == "AR"].pivot(index="h", columns="term", values="coef")
    rows.append("| IV pass-through | " + " | ".join(f"{iv.loc[h,'coef']:.2f} ({iv.loc[h,'se']:.2f})" for h in H) + " |")
    rows.append("| First-stage F | " + " | ".join(f"{iv.loc[h,'F_Gh']:.1f}" for h in H) + " |")
    def arcell(h):
        if str(ar.loc[h, "AR_b_bounded"]) in ("True", "1", "1.0"):
            return f"[{float(ar.loc[h,'AR_b_lo']):.2f}, {float(ar.loc[h,'AR_b_hi']):.2f}]"
        return "unbounded"
    rows.append("| AR 95% set | " + " | ".join(arcell(h) for h in H) + " |")
    rows.append("| OLS pass-through | " + " | ".join(f"{ols.loc[h,'coef']:.2f}{star(ols.loc[h,'coef']/ols.loc[h,'se'])} ({ols.loc[h,'se']:.2f})" for h in H) + " |")
    rows.append("| Observations | " + " | ".join(f"{int(iv.loc[h,'n']):,}" for h in H) + " |")
    return "\n".join(rows)

# --- body tables (same logic as build.py) ---
src = open("build.py").read()
ns = {}
exec(src.split("s = open(\"empirical_section.md\").read()")[0], ns)   # defines star, table7, table6
body = open("empirical_section.md").read()
body = re.sub(r"^---.*?---\n", "", body, flags=re.S)                    # drop yaml header
body = body.split("# References")[0]
body = body.replace("We report that design in the Online Appendix", "We report that design in Appendix A")
body = body.replace("Conflict exposure counts UCDP-GED (v26.1) fatalities", "Conflict exposure counts UCDP-GED (v26.1; Sundberg and Melander, 2013) fatalities")
t7, ww = ns["table7"]()
body = body.replace("{{WINS6}}", f"{100*ww.coef:.2f} percent (SE {100*ww.se:.2f})")
tabs = {1: open("table1.md").read(), 2: open("table2.md").read(), 3: open("table3.md").read(), 4: open("table4.md").read(),
        5: open("table5.md").read(), 6: ns["table6"](), 7: t7}
for i, tab in tabs.items():
    body = body.replace("{{TABLE%d}}" % i, widen(tab))
front = open("paper_front.md").read()
back = open("paper_back.md").read()
back = back.replace("**Aggregate first stage.** Table A.1", "**Aggregate first stage.** Table A.1")
back = back.replace("with F statistics between 8 and 12", "with F statistics between 8 and 12 (Montiel Olea and Pflueger, 2013)")
back = back.replace("{{TABLEA1}}", widen(tableA1(), 26, 14)).replace("{{TABLEA2}}", widen(tableA2(), 18, 14))
figs = ("\n# Figures {.unnumbered}\n\n"
        f"![Figure 1. Cumulative response of local staple prices to a one-standard-deviation adverse local weather shock. Shaded area: 95 percent confidence interval, two-way clustered by country and month.]({F}fig1_main_irf.png){{width=95%}}\n\n"
        f"![Figure 2. Differential response by staple group relative to rice (percentage points). Shaded areas: 95 percent confidence intervals.]({F}fig2_tradability.png){{width=100%}}\n\n"
        f"![Figure 3. Response to each weather component, entered jointly (percent per one standard deviation). Shaded areas: 95 percent confidence intervals.]({F}fig3_components.png){{width=100%}}\n")
paper = front + "\n" + body + "\n" + back.replace("# Declaration of generative AI", figs + "\n# Declaration of generative AI", 1)
assert "{{" not in paper
open("paper_full.md", "w").write(paper)

# --- citation check ---
refs_block = paper.split("# References {.unnumbered}")[1].split("## Data references")[0]
ref_keys = set()
for line in refs_block.strip().split("\n"):
    if not line.strip(): continue
    m = re.match(r"([A-Z][^,]+),.*?(\d{4})\.", line)
    if m: ref_keys.add((m.group(1).split()[-1] if " " in m.group(1) and m.group(1).startswith("Montiel") is False else m.group(1), m.group(2)))
text = paper.split("# References {.unnumbered}")[0] + paper.split("# Appendix A")[1]
cites = set(re.findall(r"([A-Z][A-Za-z'À-ſ]+(?: [A-Z][a-z]+)?)(?: et al\.| and [A-Z][A-Za-z']+)?,? \(?(\d{4})", text))
first_authors = {k[0].split(",")[0] for k in ref_keys}
missing = sorted({c for c in cites if c[0] not in first_authors and c[0] not in {"Table", "Figure", "Section", "Eq"} and int(c[1]) < 2027 and int(c[1]) > 1900})
print("cited but maybe not in refs:", missing)
uncited = sorted(a for a, y in ref_keys if a not in text)
print("refs not cited in text:", uncited)

# --- word count (Food Policy counts everything) ---
words = len(re.sub(r"\$\$.*?\$\$", " ", paper, flags=re.S).split())
print("TOTAL words incl. tables, references, appendix:", words)
main = paper.split("# Figures")[0]
print("main text up to figures:", len(main.split()))

# --- docx outputs ---
subprocess.run(["pandoc", "paper_full.md", "-o", "Manuscript_anonymized.docx", "--resource-path=."], check=True)
print("built Manuscript_anonymized.docx")
