# Project handover for Claude Cowork

**Paper:** "Who pays for local droughts? Weather shocks and staple food prices in 3,200 local markets"
**Target journal:** *Food Policy* (Elsevier, Q1). **Status:** full draft ready for submission, pending the author items in Section 6.
**Authors:** a master's student in data science for economics and business (first author) and Dr. Abdelhadi Benghalem (supervisor, corresponding author). The paper is also the basis of the student's master's thesis.
**Local folder:** `E:\master paper\replication_package\` (extracted from the five replication zips). The Scopus exports used for the literature review are in `E:\master paper\`.

---

## 1. Research question and contribution

*Who pays when local weather goes bad?* We estimate how an adverse local weather anomaly (hotter and drier than normal) moves retail staple food prices in the local markets of low- and middle-income countries, which foods absorb the shock, and which markets are most exposed.

The three contributions, checked against a Scopus screen of 1,556 records:
1. **Scale and design.** Pooled causal estimates at the market level for 85 countries, with weather measured at each market. Earlier work covers one country or a few hundred markets, or uses national price indices.
2. **Tradability gradient ("who pays").** Local weather lowers the production of every staple, but only the prices of staples that do not cross borders respond. Imports cap the price of rice and wheat. This is the spatial-arbitrage (law of one price) logic, shown at scale.
3. **Validated heterogeneity.** A causal forest trained on half of the countries ranks markets in the other half. The top third shows four times the average response, concentrated in arid markets.

Closest papers: Brown & Kshirsagar (2015, *GEC*), Chen & Villoria (2019, *ERL*), Okou et al. (2022, IMF WP), Kakpo et al. (2022, *Food Policy*), Letta et al. (2022, *AJAE*), Baffes et al. (2019, *WBER*).

## 2. Data

| Source | Use |
|---|---|
| WFP retail food prices (HDX, 1990–2026) | Monthly prices at market × product level. Staples are wheat, maize, rice, sorghum/millet and cassava/yam/plantain. |
| ERA5 reanalysis (ARCO, 0.25°) | Heat (HDD30), maximum temperature, soil moisture |
| GPCP v2.3 | Monthly rainfall |
| IMF world prices via FRED | World price of wheat, maize and rice |
| FAOSTAT QCL and FBS | Crop production (mechanism); calorie shares and import dependence |
| UCDP GED v26.1 | Conflict exposure within 50 km of each market |
| Natural Earth | Remoteness (distance to the nearest city of 500,000 or more) |

**Estimation sample (h = 6):** 757,136 market-months, 15,561 series, 3,221 markets, 85 countries, May 2000 to April 2026.

**Weather index W.** At each market, 3-month heat, soil dryness and rainfall deficit are each standardized against the 1991–2020 climatology for that market and calendar month, then averaged and rescaled to unit s.d. Positive values mean hotter and drier than normal.

## 3. Method

- **Panel local projections (Jordà, 2005):** the outcome is $\ln p_{t+h}-\ln p_{t-1}$, regressed on $W_t$.
  - Fixed effects: series × calendar month and country × year.
  - Controls: 3 lags of the price change, of W and of the world-price change, plus the contemporaneous world-price and exchange-rate changes.
  - Standard errors two-way clustered by country (85) and month (312).
- **Tests of the identifying assumptions:** a lead placebo ($W_{t+6}$), a pre-trend test, an entry/selection test and the Holm correction across 7 horizons.
- **Heterogeneity:** econml `CausalForestDML`, cross-fitted by country halves, with a tercile calibration test and a best linear projection on moderators.
- **Mechanism:** FAOSTAT production regressed on annual W.
- **Moderators:** import dependence, conflict exposure and remoteness.
- **Welfare exposure:** the price effect weighted by calorie shares.
- **Pre-registration:** the pre-analysis plan (`PAP_local_weather.md`, commit af071f3) and its Addendum A (commit e5e0ed8) are git-timestamped before the estimates. Everything outside them is labelled exploratory.
- **Appendix A:** a world-price IV using weather in the main exporting regions. Its aggregate first stage works (F 8–12), but it is weak in the market panel (F 0.5–9.6). It is reported honestly as a negative result.

## 4. Main results (all reproduced from `output/tables/*.csv`)

| Result | Estimate |
|---|---|
| Effect of +1 s.d. W on local staple prices | 0.42% (h = 2), 0.87% (h = 4), **0.99% (h = 6, 95% CI 0.46 to 1.53)**, 0.84% (h = 12). Holm-adjusted p ≤ 0.009 for h = 4 to 12 |
| Placebos (lead, pre-trend) | All pass (t between −0.6 and −1.0) |
| Difference from rice (pp) | Maize +1.41 (h = 2), +1.67 (h = 4); sorghum/millet +1.40 (h = 4); roots +1.46 (h = 6); wheat −0.00 |
| Production (FAOSTAT) | −7.4% per s.d. pooled; rice −6.3%, so rice supply falls but its price does not move |
| Causal-forest terciles (out of sample, h = 6) | 0.47 / 0.50 / **2.16%**; high minus middle 1.66 pp (t 3.8) |
| Aridity moderator | −0.44 pp per s.d. of log rainfall (t −2.95), i.e. drier markets respond more |
| Moderators (import dependence, conflict, remoteness) and world-price state | Not significant; reported with minimum detectable effects (MDEs) |
| Welfare exposure | Median 0.79% of the staple basket; DR Congo 1.73% |
| Robustness (21 variants, Table 7) | 0.56 (1-month window) to 1.66 (pre-2010 series); only the monthly-innovation version of W is null |

## 5. Folder map (`replication_package/`)

| Path | Contents |
|---|---|
| `README.md` | Replication instructions and the map from scripts to tables (required by *Food Policy*) |
| `run_all.py` | `python run_all.py` reproduces every table and figure (about 1 to 2 h); `--full` rebuilds from raw data |
| `code/00`–`12`, `99` | Pipeline: download, build the panel, estimate, heterogeneity, figures, robustness, mechanism, Monte Carlo |
| `data/raw/`, `data/processed/` | Raw files (ERA5 excluded, re-downloadable with `code/01`); `panel.parquet` is the analysis panel |
| `output/` | Tables (CSV), figures, results notes `RESULTS_*.md` |
| `PAP_local_weather.md` | Pre-analysis plan and its addendum |
| `literature/` | Scopus exports, `screen_ranked.csv`, `literature_table.csv` |
| `manuscript/paper_front.md` | Title, abstract, keywords, Sections 1–2 (introduction, framework) |
| `manuscript/empirical_section.md` | Sections 3–7 (data, strategy, results, robustness, discussion, policy implications) |
| `manuscript/paper_back.md` | Section 8 (conclusion), AI declaration, data availability, references, Appendix A |
| `manuscript/build_paper.py` | Assembles `paper_full.md`, fills the tables from the CSVs, checks citations, counts words and builds `Manuscript_anonymized.docx` (needs pandoc) |
| `manuscript/submission/` | Files ready to upload: anonymized manuscript, title page, highlights, Figure_1–3 (300 dpi) |
| `manuscript/FoodPolicy_author_guidelines.md` | Journal requirements and compliance checklist |
| `manuscript/Notes_for_authors.md` | Audit, literature screen, references to verify, referee memo (the five weakest points and fixes) |

**Length:** 9,985 words including tables, references and appendix. The journal limit is 10,000, so any addition must be offset by a cut.

**Writing rules used:**
- American English; author–year citations.
- No em or en dashes in prose; ranges are written as "0.46 to 1.53".
- Prose humanized: no AI-typical phrasing.
- Every number in the text must match a CSV in `output/tables/`.

## 6. Open items before submission

1. **Title page** (`manuscript/title_page.md` → `Title_page.docx`): the student's full name, the affiliation (Oran Graduate School of Economics or Abou Bekr Belkaid University Tlemcen; confirm which) with postal address, and the actual CRediT roles.
2. **References:** add the Kotz et al. (2024) *Communications Earth & Environment* 5 article number (DOI 10.1038/s43247-023-01173-x), and replace "et al." with the full author list for Adler et al. (2018).
3. **Equations:** open `Manuscript_anonymized.docx` in Word and check that Eqs. (1)–(5) display.
4. **Read-through:** both authors read the paper end to end and own every claim. *Food Policy* holds authors responsible for AI-assisted content.
5. **Graphical abstract** (optional, encouraged): base it on Figure 2.
6. **On acceptance:** deposit `replication_package/` on Zenodo, put the DOI in the data-availability statement, and remove nothing.

## 7. Optional strengthening (from the referee memo)

1. **Supply-area weather: DONE** in the cloud session (`code/13_supply_area.py`, `output/tables/supply_area.csv`, Table 7, Section 6). δ₆ rises to 1.02 / 1.08 / 1.18% for 50 / 100 / 200 km, and the 200 km measure absorbs the point measure in a joint regression (1.24 vs. −0.06). Re-running it needs the ERA5 grids; possible next step: cropland weighting.
2. **Travel time instead of straight-line remoteness.** Use the Weiss et al. (2018) friction surface from the Malaria Atlas Project.
3. **Root-and-tuber substitution test.** Interact W × roots with the cereal share of the diet; the calorie shares are already computed in `code/11`.
4. **Online Appendix.** Collect the first-stage results, Anderson–Rubin sets and robustness tables from `output/RESULTS_*.md`.

Every new analysis must be labelled exploratory, because it is not in the pre-analysis plan.

## 8. Thesis route

The thesis can extend the paper chapter by chapter:
1. Literature and framework: Sections 1–2.
2. Data and the weather index: Section 3, plus validation of the index against known droughts.
3. Main estimates and robustness: Sections 4–6.
4. Machine-learning heterogeneity: forest, calibration, policy targeting.
5. The world-price IV in full (Appendix A) as a methods chapter on weak instruments.
6. Extensions from Section 7.
