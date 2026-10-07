---
title: "Notes for authors: audit, literature screen and referee memo"
subtitle: "Companion to Empirical_section_Food_Policy_draft.docx"
---

# 1. Pre-writing audit

| Check | Assessment |
|---|---|
| Identification | Within-series deviations of market weather from its calendar-month norm, net of country × year shocks. Key assumption: local anomalies are unrelated to other local demand or supply shocks. Main threat: weather → conflict/migration → prices. Leads and pre-trend tests pass; conflict does not moderate the effect. |
| Estimand | δ_h is the percent change in local retail price h months after a 1 s.d. adverse anomaly. This matches the research question. |
| Inference | Two-way clustering by country (85) and month (312). Spatial alternatives (2° and 5° cells) and country-only clustering give larger t-statistics, so the baseline is the conservative choice. |
| Power | Every null reports an MDE (2.8 × SE). W × world-price state: estimate 0.32, MDE 0.94 pp. W × ΔG: −0.04, MDE 0.31 pp per s.d. Conflict: +0.15, MDE 0.66 pp. Imported label: −0.61, MDE 1.1 pp. Import dependence and remoteness sit near their MDEs, so they are underpowered rather than null. |
| Multiplicity | Seven horizons with Holm correction: h = 4 to 12 survive (p ≤ 0.009) and h = 2 does not. Heterogeneity tests were pre-specified; moderators and robustness checks are labelled exploratory. |
| Robustness | 18 alternatives across sample, measurement, specification and inference (Table 7). Only the monthly-innovation version of W is null, which the text explains. |
| Quality ceiling | Realistic targets: *Food Policy*, *World Development*, *Global Food Security*, *Environmental and Resource Economics*. Not top-5 or *JDE*: identification is selection-on-observables with weather anomalies, a standard design, and the novelty is scale, the tradability gradient and validated heterogeneity, not a new identification strategy. |

# 2. Word count and budget

Food Policy (guide saved in FoodPolicy_author_guidelines.md) expects 6,000–10,000 words for the whole submission, including abstract, tables, references and appendices.

| Section | Words | Budget (L = 8,000) |
|---|---|---|
| 3. Data | 749 | 700–850 |
| 4. Empirical strategy | ≈ 980 | 1,000–1,200 |
| 5. Results | ≈ 1,510 | 1,500–1,700 |
| 6. Robustness | ≈ 400 | 500–650 |
| 7. Discussion | ≈ 630 | 750–900 |
| **Total (prose, excluding tables and equations)** | **≈ 4,245** | 4,450–5,300 |

The draft sits slightly under budget. That leaves room for the introduction and conceptual framework, or for expanding the Discussion if the editor asks for more on policy.

# 3. Literature screen (Scopus, three queries, 1,556 records)

The screen covered the three exports you supplied:
- **Q1** (weather and food prices): 1,386 records;
- **Q2** (tradability and import parity): 13 records;
- **Q3** (causal ML on food prices or food security): 157 records.

Records were scored on relevance (food-price terms, weather terms, local or market-level data, tradability, heterogeneity), and energy and electricity papers were removed. The 138 high-scoring records were read at abstract level.

**Novelty verdict: no paper pre-empts the contribution.**

- **Closest in design:**
  - Brown and Kshirsagar (2015, *GEC*): 554 markets, 2008–12, market-by-market regressions.
  - Chen and Villoria (2019, *ERL*): 76 maize markets; the outcome is volatility, not the level response to weather.
- **Closest in framing:** Okou et al. (2022, IMF WP), with global prices and disaster dummies for 15 countries.
- **Causal ML:** of 157 Q3 records, only two combine prices and weather. One is fertilizer profitability (McCullough et al., 2022, *Nature Food*). The other is Nino (2026, *Food Policy*), which covers a single country (Colombia) and studies road closures.

`empirics/literature/literature_table.csv` holds the full 15-paper comparison. `empirics/literature/screen_ranked.csv` holds all scored records.

**Further papers worth citing in the introduction** (all verified from the Scopus export):
- Shively and Thapa (2017, *AJAE*): Nepal, infrastructure.
- Cedrez et al. (2020, *GFS*): 168 SSA markets.
- Raleigh et al. (2015, *GEC*): conflict–price–climate.
- Dietrich and Schmerzeck (2019, *Food Policy*): market isolation after weather shocks.
- Salazar et al. (2023, *Agricultural Economics*): Chile.
- Song et al. (2026, *Agricultural Economics*): Northern Nigeria.
- Bren d'Amour et al. (2016, *ERL*): teleconnected supply shocks.
- Animashaun et al. (2026, *Ecological Economics*): heat and consumption in Nigeria.

# 4. Citation verification

**Verified** against Scopus export metadata or publisher and RePEc pages:

- **From the Scopus export:** Brown & Kshirsagar 2015; Chen & Villoria 2019; Baffes et al. 2019; Kakpo et al. 2022; Raleigh et al. 2015; Nino 2026; Villoria 2026.
- **From publisher or RePEc pages:** Okou et al. 2022; Letta et al. 2022; Jordà 2005; Athey et al. 2019; Hersbach et al. 2020; Adler et al. 2018; Cameron et al. 2011; Holm 1979.

**[VERIFY] before submission:**
1. Kotz et al. (2024), *Communications Earth & Environment* 5: the article number. The DOI 10.1038/s43247-023-01173-x is verified.
2. Adler et al. (2018): the full author list (shortened to "et al." in the draft).
3. The *Food Policy* word limit and reference style (author–year assumed).

# 5. Referee memo: the five weakest points

1. **"Selection on observables with weather is standard; what is new?"** Lead the introduction with the tradability gradient and the out-of-sample heterogeneity, not with the average effect. The average effect of about 1% confirms prior work; the who-pays result and the forest calibration (2.16% vs. about 0.5%) are the contribution. Okou et al. (2022) is the natural foil: imported staples follow world prices, local staples follow local weather.

2. **"Weather is measured at the market, not over its supply area."** This attenuates δ_h toward zero, so the estimates are conservative. A strong revision would compute W over a 100–200 km buffer, or over cropland within the market's catchment. The ERA5 grids already downloaded make this a short extension in `04_build_wfp_panel.py`.

3. **"Policy moderators are insignificant."** They are near their MDEs (import dependence −0.28 vs. MDE 0.46; remoteness +0.19 vs. MDE 0.30). Better measures would sharpen them: time-varying import shares, and travel time rather than straight-line distance. The `malariaatlas.org` access you added covers the main domain but not `data.malariaatlas.org`; adding that subdomain allows the Weiss et al. (2018) travel-time raster.

4. **"The root-and-tuber price response has no production counterpart."** State the substitution channel as a hypothesis. A test is whether root prices respond more where cereals dominate the diet. That is a single interaction using the calorie shares already computed.

5. **"Why not causal pass-through of world prices?"** Section 4.5 discloses the weak exporter-weather instrument. Put the full first-stage and Anderson–Rubin results in the Online Appendix (`empirics/output/RESULTS_first_stage.md`, `RESULTS_main.md`). Referees reward disclosed failed designs more than they penalize them.

# 6. Reproducibility

Every number in the draft is generated from `empirics/output/tables/*.csv` by `manuscript/build.py`, so re-running the pipeline updates the tables automatically.

The pre-analysis plan (`empirics/PAP_local_weather.md`) and its Addendum A carry git timestamps that precede the corresponding estimates:
- PAP: commit af071f3;
- Addendum A: commit e5e0ed8.
