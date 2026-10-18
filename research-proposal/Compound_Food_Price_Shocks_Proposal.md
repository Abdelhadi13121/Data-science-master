# Research Proposal (Q1 paper → Master thesis)

## When Local Droughts Meet Global Price Spikes: Causal Machine Learning Evidence on Compound Shocks in ~3,000 Local Food Markets

**Programme:** Master in Data Science for Economics and Business
**Supervisor:** Dr. Abdelhadi Benghalem
**Status:** Theme proposal. The literature gap and data availability were checked on 2026‑10‑06; see §9 for what was checked.
**Primary target journal:** *Food Policy* (Elsevier, Q1). **Alternatives:** *World Development*, *American Journal of Agricultural Economics*, *Global Environmental Change*, *Environmental and Resource Economics*.

---

## 1. Research question

> **How does a local weather shock (drought or heat) change the size and speed with which world cereal‑price and exchange‑rate shocks pass through to local food prices? In which markets is this amplification largest?**

The question has three parts:

| # | Question | Estimand |
|---|---|---|
| RQ1 | What is the dynamic causal effect of world price shocks on local prices, using **exogenous variation in world prices**? | $\beta^{G}_h$, $h=0,\dots,12$ |
| RQ2 | Does a local weather shock **amplify** that pass‑through (compound shock)? | $\gamma_h$ (interaction) |
| RQ3 | Which market characteristics (import dependence, remoteness, conflict, subsidies, irrigation) drive the heterogeneity, and where would buffer policies help most? | $\tau_h(x)=\mathbb{E}[\beta^{G}_{h,i}\mid X_i=x]$ and policy‑tree assignment |

---

## 2. Why this theme is plausible, new and publishable

### 2.1 What the literature has done, and what it has not

| Strand | Representative work | What remains open |
|---|---|---|
| Local weather → local prices | Kakpo et al. 2022 (*Food Policy*, Niger); Letta et al. 2021 (*AJAE*, India); Bohorquez‑Penuela et al. 2026 (Colombia, ML heterogeneity); Nino 2026 (*Food Policy*, Colombia, causal forest) | Each covers **one country**. None models interaction with global shocks. |
| World → local price transmission | Emediegwu et al. 2024 (*Food Policy*, PVAR, 23 countries); Hoffmann et al. 2026 (*Agric. Econ.*, STECM); Ceballos et al. 2015; Baltzer 2013 | World prices are treated as **exogenous or correlational**. Baltzer (2013) names "coinciding domestic shocks" as a driver of overshooting but does not estimate it. |
| Climate → aggregate inflation | Kotz et al. 2024 (*Commun. Earth Environ.*, 27k CPI obs.); Compaore et al. 2026 (*Climatic Change*, LP, WAMU/CAMU); Kunawotor et al. 2021 | Uses **national CPI**, so market‑level heterogeneity and the global–local interaction are averaged out. |
| Closest prior study | **Brown & Kshirsagar 2015** (*Global Environmental Change*): 554 markets, 51 countries, **2008–2012**. Weather and international price effects are estimated market by market; 4% of markets show both. | Short window that ends before 2022. No causal identification of world prices, no pooled interaction parameter, no ML heterogeneity, no policy targeting. |
| Extreme events × food groups | Venkat et al. 2022 (conference abstract, 2,321 markets, OLS with fixed effects) | Not a full paper. Linear fixed effects only, with no global‑shock channel. |

### 2.2 Contributions (each tied to the gap above)

1. **Compound‑shock parameter at global scale.** This would be the first pooled estimate of $\gamma_h$, the amplification of world‑price pass‑through by local drought or heat. It covers about 98 countries and about 3,000 markets over 2000–2026, including the 2022 Black Sea shock and the 2023–24 El Niño.
2. **Causal identification of world price shocks.** World prices are instrumented with a share‑weighted **exporter‑weather yield‑shock index** in the spirit of Roberts & Schlenker (2013): weather in the main exporting regions (Black Sea, US, EU, Argentina, Australia, Thailand/Vietnam/India). Searches of Consensus and the Firecrawl research index on 2026‑10‑06 found no local pass‑through study using this instrument.
3. **Methods.** Local projections are estimated with double/debiased ML using dependence‑aware cross‑fitting. Heterogeneity comes from orthogonalized causal forests, and targeting from policy trees. This goes beyond the PVAR, STECM and fixed‑effects OLS used so far.
4. **Policy output.** A map of the markets where pre‑positioned stocks, import diversification or temporary tariff cuts would reduce compound‑shock exposure most. This speaks directly to WFP, FAO and MENA/Sahel governments.

**Honest assessment.** The topic area is established, which helps acceptance, but the space is crowded. The paper's novelty rests on contributions 1 and 2. If the instrument is weak (see §6), the paper falls back to a reduced‑form "exporter‑weather → local price" design. That is still publishable, but less strong.

---

## 3. Data (availability verified)

| Block | Source | Coverage | Access | Verified |
|---|---|---|---|---|
| **Local food prices (core)** | WFP VAM via HDX, "Global – Food Prices" | 98 countries, about 3,000 markets, mostly monthly, 1992–Sep 2026, updated monthly | Free CSV per year | ✅ HDX page, 2026‑10‑06 |
| Gap‑filled prices (robustness) | World Bank RTFP, "Monthly food price estimates by product and market" (Andrée 2021 method) | 37 countries, 3,128 markets, 2007‑01 to 2026‑08 | Free, World Bank Microdata Library | ✅ catalog page |
| Exchange rates (incl. parallel‑market estimates) | World Bank **RTFX** (same catalog); WFP exchange‑rate series | Country × month | Free | ✅ listed in catalog (series detail to check) |
| World prices | World Bank Pink Sheet; FAO Food Price Index (released 2 Oct 2026); IGC | Monthly, 1960/1990– | Free | ✅ FAO page |
| Weather | ERA5‑Land monthly (Copernicus CDS); CHIRPS v2 rainfall; SPEIbase | Gridded 0.05–0.25°, 1950/1981– | Free; CDS needs registration | Standard sources (not re‑downloaded) |
| Exporter yields (instrument) | FAOSTAT production; USDA PSD; GDHY gridded yields | Annual/seasonal | Free | Standard |
| Moderators | FAOSTAT Food Balance Sheets (import dependence); Weiss et al. 2018 travel‑time raster; UCDP‑GED (conflict, open) or ACLED (free with registration); FAO FPMA policy database; FAO GMIA irrigation | Static or annual | Free | ACLED registration model confirmed |

**Algeria limitation.** WFP's Algeria dataset covers only the **Tindouf refugee‑camp monitoring unit**, from 15 Apr 2015 to 15 Jun 2026 (HDX). Algeria therefore cannot be the core sample. Algerian relevance comes through the **MENA wheat‑import‑dependence** subsample (Egypt, Syria, Yemen, Iraq, Lebanon, Libya, Sudan, Mauritania) and an optional national‑level case study. That case study would use ONS monthly food CPI, whose sub‑national availability still needs confirming.

**Expected panel.** Roughly 10⁶ market × commodity × month observations after cleaning, in line with Venkat et al. 2022, who used 1.35M observations from the same sources.

---

## 4. Empirical strategy

### 4.1 Variables

Indices: market $m$, commodity $c$, country $k$, month $t$.

- $y_{mct}$: log real retail price (nominal local currency deflated by national CPI).
- $W_{mt}$: local weather shock. Standardized SPEI‑3 in a 50 km catchment, and growing‑season extreme‑heat degree days above crop thresholds, both as anomalies from the 1981–2010 calendar‑month climatology.
- $G_{ct}$: log world price of commodity $c$ in USD. For non‑traded staples, use the nearest traded substitute.
- $E_{kt}$: log local‑currency/USD exchange rate.
- $Z_{ct}$: exporter‑weather instrument,
$$Z_{ct}=\sum_{j\in\mathcal{J}_c} s_{jc,\,t_0}\;\widehat{\Delta \text{yield}}_{jct}(\text{weather}_{jt}),$$
where $s_{jc,t_0}$ is exporter $j$'s pre‑sample export share and $\widehat{\Delta \text{yield}}$ is the weather‑predicted yield anomaly.

### 4.2 Baseline: panel local projections with a compound‑shock term

For $h=0,\dots,12$:
$$
y_{mc,t+h}-y_{mc,t-1}= \beta^{W}_h W_{mt} + \beta^{G}_h \Delta G_{ct} + \gamma_h\,(W_{mt}\times \Delta G_{ct}) + \theta_h \Delta E_{kt} + \sum_{\ell=1}^{L}\rho_{h\ell}\Delta y_{mc,t-\ell} + \alpha^{h}_{mc,\,\text{month}(t)} + \delta^{h}_{k,\,\text{year}(t)} + \varepsilon^{h}_{mct}
$$

- $\alpha$ absorbs market × commodity seasonality. $\delta$ absorbs country‑year macro conditions.
- $\Delta G_{ct}$ and its interaction are instrumented with $Z_{ct}$ and $W_{mt}\times Z_{ct}$ (2SLS‑LP).
- **Key parameter:** $\gamma_h>0$ means a local drought amplifies global pass‑through.

### 4.3 Main estimator: DML‑LP (partially linear IV)

Let $D$ be the treatment block and $X$ the high‑dimensional controls (lags, seasonality, moderators, climatology). The model is
$$
Y^{(h)} = D'\psi_h + g_h(X) + U,\qquad \mathbb{E}[U\mid Z, X]=0 .
$$
Here $g_h$, $\mathbb{E}[D\mid X]$ and $\mathbb{E}[Z\mid X]$ are learned with gradient boosting, random forests or the lasso. Estimation uses **blocked cross‑fitting**: folds are formed by country × time blocks, with a buffer gap that leaves out neighbouring periods. This follows the dependence‑robust DML theory of Semenova et al. (*Quantitative Economics*), "DML for time series" (*Econometrics Journal* 2026, arXiv 2603.10999) and semiparametric IRFs (arXiv 2411.10009). Software: `DoubleML` (R/Python).

### 4.4 Heterogeneity and targeting (RQ3)

- An R‑learner / **causal forest** (`grf`) on orthogonalized LP residuals gives $\hat\tau_h(x)$, the pass‑through as a function of import dependence, travel time to port or city, conflict intensity, subsidy regime, irrigation share and market integration.
- Report the best linear projection of $\tau$, RATE/TOC curves (Yadlowsky et al.) and calibration tests.
- A **policy tree** (`policytree`) allocates a limited buffer budget across markets to minimize expected compound‑shock price spikes.

### 4.5 Inference and diagnostics

- Standard errors clustered by country, with two‑way market/month clustering and Conley spatial HAC (500 km) as robustness.
- IV strength: Montiel Olea–Pflueger effective F, with Anderson–Rubin confidence sets if weak.
- Exclusion restriction: placebo tests on non‑traded goods, the timing of exporter weather relative to the local harvest, and leave‑one‑exporter‑out instruments.
- Shift‑share validity: Borusyak–Hull–Jaravel exposure‑robust inference.
- Selection into reporting: re‑estimate on gap‑filled RTFP and use inverse‑probability‑of‑reporting weights.

---

## 5. Thesis architecture

| Chapter | Content | Output |
|---|---|---|
| 1 | Literature and data engineering: WFP, ERA5/CHIRPS and FAOSTAT merge; reproducible pipeline (`targets` in R or Snakemake/Python) | Open replication package |
| 2 | **Paper 1 core:** DML‑LP compound‑shock estimates (RQ1–RQ2) | Submission to *Food Policy* |
| 3 | Heterogeneity and policy targeting (RQ3) | Section of Paper 1, or Paper 2 (*World Development*) |
| 4 (extension) | **Early warning:** probabilistic one‑ to three‑month price‑spike forecasting with global LightGBM, a Temporal Fusion Transformer and time‑series foundation models (Chronos/TimesFM), using **conformal** prediction intervals and benchmarked against FEWS NET alerts | Paper 2 or 3 (*Int. J. Forecasting*, *Food Policy*) |

## 6. Risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Weak exporter‑weather instrument at monthly frequency | Medium | Aggregate to the crop season; use futures‑price surprises around USDA WASDE releases as an alternative instrument; fall back to a reduced form |
| Unbalanced, non‑random WFP coverage (conflict areas) | High | RTFP gap‑filled data, reporting‑probability weights, balanced sub‑panel |
| Parallel exchange rates (Syria, Lebanon, Sudan, Yemen) | High | RTFX/WFP parallel rates; exclude years with hyperinflation as robustness |
| Compute (about 10⁶ obs × 13 horizons × cross‑fitting) | Medium | Sub‑sample tuning, LightGBM, cloud or university HPC; feasible on a 32 GB workstation |
| Reviewer asks "how is this different from Brown & Kshirsagar 2015?" | Certain | §2.1 table: identification, interaction parameter, 2022 period, ML heterogeneity |

## 7. Twelve‑month timeline

| Months | Milestone |
|---|---|
| 1–2 | Literature review; register for Copernicus CDS and ACLED; download WFP and RTFP |
| 3–4 | Weather extraction to market catchments; build the instrument; descriptive atlas |
| 5–6 | Baseline LP and 2SLS‑LP; first‑stage diagnostics |
| 7–8 | DML‑LP and causal forests; robustness |
| 9 | Draft Paper 1 and submit to *Food Policy*; post the preprint (SSRN/arXiv econ.GN) |
| 10–12 | Forecasting extension; thesis writing; defence |

## 8. Why this theme was chosen over the alternatives

| Alternative | Reason not chosen |
|---|---|
| Nowcasting Algerian GDP/inflation with ML | Data too thin (quarterly, short series); novelty mostly in the method; weak Q1 prospects |
| LLM‑based text indices (central‑bank or news sentiment, Arabic/French) | Data collection and annotation costs; LLM‑index papers are quickly saturating |
| Climate → national CPI | Already covered by Kotz et al. 2024 and Compaore et al. 2026 |

## 9. What was verified (2026‑10‑06)

- **Literature:** Consensus (four searches), Firecrawl research index (DML/LP methods; compound shocks; exporter‑weather instrument) and web search. Found no study combining the global × local interaction with causal identification of world prices at market scale. This is limited to what these indexes returned; Google Scholar and RePEc/IDEAS must be checked before submission.
- **Data:** HDX global WFP page (98 countries, about 3,000 markets, files 1990–2026, monthly updates); HDX Algeria page (Tindouf only); World Bank RTFP catalog (37 countries, 3,128 markets, to 2026‑08); FAO FFPI (release of 2 Oct 2026); ACLED registration model.
- **Not verified here:** direct file download. This environment's network policy blocked `data.humdata.org`, so coverage figures come from the official metadata pages and not from row counts.

## 10. Key references

- Brown, M.E., Kshirsagar, V. (2015). Weather and international price shocks on food prices in the developing world. *Global Environmental Change* 35, 31–40. doi:10.1016/j.gloenvcha.2015.08.003
- Emediegwu, L. et al. (2024). Agricultural commodities' price transmission from international to local markets in developing countries. *Food Policy*.
- Hoffmann, C. et al. (2026). Food price crises and the insulation of domestic grain markets. *Agricultural Economics*.
- Kotz, M., Kuik, F., Lis, E., Nickel, C. (2024). Global warming and heat extremes to enhance inflationary pressures. *Communications Earth & Environment*. doi:10.1038/s43247-023-01173-x
- Compaore, X.E.W.K. et al. (2026). Climate anomalies and price dynamics: insights from SSA currency unions. *Climatic Change*.
- Kakpo, A.T. et al. (2022). Weather shocks and food price seasonality in SSA: Niger. *Food Policy*.
- Letta, M. et al. (2021). Weather shocks, traders' expectations, and food prices. *AJAE*.
- Nino, G. (2026). Disruption in ground transportation: natural disasters and disintegration of local food markets. *Food Policy*.
- Bohorquez‑Penuela, C. et al. (2026). Heterogeneous effects of weather shocks on food prices in a country with diverse agriculture. Working paper.
- Baltzer, K. (2013). International to domestic price transmission in fourteen developing countries during the 2007–08 food crisis. WIDER.
- Roberts, M.J., Schlenker, W. (2013). Identifying supply and demand elasticities of agricultural commodities. *AER* 103(6).
- Chernozhukov, V. et al. (2018). Double/debiased machine learning. *Econometrics Journal* 21(1).
- Semenova, V. et al. Inference on heterogeneous treatment effects in high‑dimensional dynamic panels under weak dependence. *Quantitative Economics* (arXiv 1712.09988).
- Double machine learning for time series (2026). *Econometrics Journal* (arXiv 2603.10999).
- Semiparametric inference for impulse response functions using DML (arXiv 2411.10009).
- Athey, S., Tibshirani, J., Wager, S. (2019). Generalized random forests. *Annals of Statistics* 47(2).
- Jordà, Ò. (2005). Estimation and inference of impulse responses by local projections. *AER* 95(1).
- Andrée, B.P.J. (2021). Estimating food price inflation from partial surveys. World Bank Policy Research WP 9886.
