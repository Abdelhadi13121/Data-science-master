# Results: local weather shocks and local food prices

All analyses in Sections 1–5 were pre‑specified in `PAP_local_weather.md`, committed (af071f3) before estimation. Section 6 is labelled exploratory.

**Sample.**
- WFP retail prices, 2000–2026: 25,428 series (market × product), 86 countries.
- Staples: wheat, maize, rice, sorghum/millet, and cassava/yam/plantain.
- Up to 884,313 market‑months at h = 0.

**Shock.** W is an adverse local weather index at each market's coordinates, built from ERA5 at 0.25° and GPCP: 3‑month heat, soil dryness and rainfall deficit, scaled to unit s.d. It was validated against known droughts and floods.

**Specification.** Local projections with series × calendar‑month and country × year fixed effects. Controls: 3 lags of Δlnp, W and ΔG, the contemporaneous world price change, and the exchange‑rate change. Standard errors are **two‑way clustered by country and month**.

## 1. Main effect (RQ1)

| h (months) | 0 | 2 | 4 | 6 | 8 | 10 | 12 |
|---|---|---|---|---|---|---|---|
| δ_h (% per 1 s.d.) | −0.00 | 0.42 | 0.87 | **0.99** | 0.76 | 0.78 | 0.84 |
| t | −0.04 | 2.13 | 3.41 | 3.63 | 3.23 | 3.14 | 2.98 |

A one‑s.d. adverse local weather shock raises local staple prices by about **1% after six months**. The effect does not reverse within a year. A two‑s.d. drought, which is common in the sample (Zambia 2024: +3.05), implies a 2–3% price rise from local weather alone.

## 2. Placebos

| Test | Coefficient | t |
|---|---|---|
| Future shock W(t+6) on the h = 0 outcome | −0.0005 | −0.72 |
| Future shock W(t+6) on the h = 2 outcome | −0.0012 | −0.64 |
| Pre‑trend: shock at t on the price change t−4 → t−1 | −0.0015 | −1.00 |

All placebos pass, so the causal interpretation stands under the pre‑committed decision rule.

## 3. Channels and nonlinearity

**Components** (entered jointly):
- **Rainfall deficit** drives the response at 2–6 months: +0.50 to +0.79% (t = 2.4–3.2).
- **Heat** dominates later: +0.56% at 10 months (t = 1.9) and +0.80% at 12 months (t = 2.5). This fits harvest timing.
- **Soil dryness** adds little once rainfall is controlled for.

**Bins** (reference: |W| ≤ 1):
- moderate drought (1 < W ≤ 2): +1.06% at h = 4 (t = 4.2);
- severe drought (W > 2): +1.11% (t = 2.1);
- wet shocks (W ≤ −1): **−1.47% at h = 6 (t = −2.4)**.

The response is roughly symmetric. Good seasons lower local prices about as much as bad ones raise them.

## 4. Who pays? Tradability (RQ2)

Differential response relative to rice (pp):

| h | Maize | Sorghum/millet | Cassava/yam/plantain | Wheat |
|---|---|---|---|---|
| 2 | **+1.41** (t 4.8) | **+1.01** (2.4) | +0.71 (1.6) | −0.25 (−1.2) |
| 4 | **+1.67** (4.0) | **+1.40** (2.1) | +1.10 (1.8) | −0.18 (−0.7) |
| 6 | **+1.19** (2.3) | +1.33 (1.7) | **+1.46** (2.6) | −0.00 (0.0) |

- **Rice and wheat** are internationally traded and largely imported, and their prices do not respond to local weather. The rice baseline is +0.27% at h = 4, not significant; wheat is not different from rice.
- **Locally produced staples carry the whole burden.** Maize leads, followed by coarse grains and roots/tubers.
- **Imported‑label products** respond less (−0.61 pp at h = 4, t = −1.6), though not significantly.

This is what spatial arbitrage predicts. Import parity caps traded‑good prices, while non‑traded staples clear locally. The poorest households, whose diets rely on coarse grains and roots, face the largest weather‑driven price risk.

## 5. Heterogeneity (RQ3: causal forest, cross‑fitted by country halves, h = 6)

**Out‑of‑sample calibration.** Market‑months are sorted into terciles by the forest's predicted effect, and the effect is re‑estimated within each tercile in held‑out countries:

| Tercile of predicted effect | Realized δ (%) | t |
|---|---|---|
| Low | 0.47 | 2.1 |
| Middle | 0.50 | 2.3 |
| **High** | **2.16** | **4.3** |
| High − middle | **+1.66 pp** | **3.8** |

The forest finds real heterogeneity. A third of market‑months face a response about **four times** larger than the rest.

**Linear heterogeneity** (standardized moderators, two‑way clustered):
- **Aridity** is the robust continuous driver: −0.44 pp per 1 s.d. of log mean rainfall (t = −2.95), so drier climates respond more.
- Distance to the coast, heat climatology and the imported label are not significant.
- Latitude is borderline (t = −1.7).
- Maize (+1.32 pp, t = 2.5) and coarse grains (+1.26 pp, t = 2.0) remain larger than rice.

The forest's feature importance is unstable across the two country halves: latitude ranks first in both, at 0.95 and 0.23. It is therefore not used for inference.

## 6. State dependence (RQ4) and robustness

- **State dependence on world prices:** W × 1[world price above its 24‑month average] and W × ΔG are insignificant at all horizons (|t| ≤ 1.3). Local drought effects do not depend on world market conditions. This confirms the null on compound amplification from the original design.
- **Robustness (exploratory):** see Section 7 and `output/tables/robustness.csv`.

## 7. Robustness (exploratory)

Not pre‑specified. δ is in % per 1 s.d. of W, with t in parentheses.

| Check | h = 4 | h = 6 | n (h = 6) |
|---|---|---|---|
| Baseline | 0.87 (3.41) | 0.99 (3.63) | 757,136 |
| R1 Drop crisis/hyperinflation economies | 0.97 (3.65) | 1.03 (3.47) | 680,367 |
| R2 Prices in USD | 0.66 (2.43) | 0.76 (2.64) | 783,868 |
| R3 Cluster by country only | 0.87 (3.67) | 0.99 (3.95) | 757,136 |
| R4 Sample ending 2019 | 1.01 (2.49) | 1.08 (2.37) | 338,165 |
| R6 Cereals only | 0.85 (3.27) | 0.96 (3.52) | 674,710 |
| R5 Monthly innovation of W (not the level) | 0.10 (0.90) | 0.13 (1.05) | 757,136 |

- **R1–R4 and R6:** the effect survives dropping crisis economies, using USD prices, alternative clustering, the pre‑2020 sample, and excluding roots and tubers.
- **R5:** month‑to‑month changes in the 3‑month index have no detectable effect. Prices respond to **accumulated seasonal conditions**, not to monthly fluctuations, which is consistent with harvest‑based supply effects. The paper should state that the estimand is the effect of a persistent seasonal anomaly.

## Link to the original proposal
The exporter‑heat instrument raised world cereal prices by 6–8% (aggregate F ≈ 8–12) but was too weak in the market panel. The paper therefore reports the global pass‑through only as conditional correlations (about 20% within 6–8 months) and an Anderson–Rubin bound at two months, [−0.39, 0.11]. See `RESULTS_main.md`.

## 8. Selection, measurement and inference (exploratory, `10_selection_sensitivity.py`)

All results below are δ at h = 6, in % per 1 s.d. of W, with t in parentheses.

**Multiple testing across the 7 horizons:**
- Holm‑adjusted p ≤ 0.009 at every horizon from h = 4 to h = 12, and Bonferroni‑adjusted p ≤ 0.02.
- Only h = 2 loses significance (Holm p = 0.066).

**Spatial correlation:**
| Clustering | δ | t |
|---|---|---|
| Baseline: country × month | 0.99 | 3.63 |
| 2° grid cell × month | 0.99 | 4.48 |
| 5° grid cell × month | 0.99 | 3.76 |

**Sample selection (WFP coverage is not random):**
- **Series monitored before 2010:** δ = **1.66 (3.83)**, n = 240,582. The effect is larger in long‑monitored markets, so later coverage expansion dilutes it rather than creating it.
- **Market‑entry test:** whether WFP starts monitoring a market is unrelated to adverse weather in the previous three months. The coefficient is −0.05 pp against a mean entry rate of 0.46 pp per month (t = −1.78), and if anything negative.

**Construction of the weather index:**
| Variant | δ | t |
|---|---|---|
| 1‑month window | 0.56 | 3.40 |
| 2‑month window | 0.81 | 3.53 |
| **3‑month window (baseline)** | **0.99** | **3.63** |
| 6‑month window | 1.40 | 4.24 |
| Clip at ±3 | 1.02 | 3.71 |
| Clip at ±5 | 0.98 | 3.59 |
| No clipping | 0.94 | 3.52 |
| Market‑specific detrending | 0.96 | 3.63 |

The effect rises steadily with the aggregation window, so prices respond to accumulated seasonal anomalies. The baseline is conservative. Clipping and detrending do not matter.

## 9. Mechanism, policy moderators and welfare (PAP Addendum A; exploratory, `11_mechanism_moderators.py`)

### M1 – Production mechanism
FAOSTAT, country × crop × year, 2000–2024, 86 countries, 7,233 observations. Fixed effects: country × crop and crop × year; standard errors clustered by country.

| Crop | Effect of annual mean W (per 1 s.d.) on ln(production) | t |
|---|---|---|
| **Pooled** | **−7.4%** | −3.17 |
| Maize | −11.3% | −3.45 |
| Sorghum | −16.9% | −3.02 |
| **Rice** | **−6.3%** | −2.28 |
| Millet | −6.6% | −1.24 |
| Wheat | −3.6% | −0.71 |
| Cassava / yams / plantains | −0.6 / −2.3 / −2.7% | ≤ 0.8 in absolute value |

- **Traded vs. local:** the traded × W interaction is +3.2 pp (t = 0.93). Local weather lowers rice and wheat production about as much as other crops.
- **Interpretation:** rice *prices* still do not respond (Section 4). The price contrast therefore reflects **trade arbitrage, not an absence of supply shocks.** Imports cap the price of traded staples.
- **Roots and tubers:** production does not respond, yet prices do. This points to substitution away from scarce cereals. FAOSTAT root‑crop data are also known to be noisy, so this is not over‑interpreted.

### M2 – Policy moderators of the price effect at h = 6
73 countries, 547,980 market‑months; two‑way clustering by country and month. Interactions are per 1 s.d. of the moderator, in percentage points.

| Moderator | One at a time | Joint |
|---|---|---|
| Cereal import dependence (FBS 2010–13; s.d. 0.25) | −0.25 (t −1.43) | −0.28 (t −1.68) |
| Conflict exposure (log UCDP fatalities, 50 km, t−12..t−1) | +0.11 (t 0.44) | +0.15 (t 0.66) |
| Remoteness (log km to the nearest city ≥ 500k) | +0.13 (t 1.23) | +0.19 (t 1.74) |
| Main effect W in the same sample | 0.92–0.94 (t ≈ 3.2) | 0.92 (t 3.26) |

- **Direction:** consistent with the arbitrage mechanism. Import‑dependent countries respond less and remote markets respond more.
- **Precision:** no moderator is significant at 5%. These results are reported as suggestive. Conflict exposure does not change the effect.

### M3 – Welfare exposure
Staple‑basket price increase per 1‑s.d. drought at 6 months = Σ_k (calorie share_k × δ_k), with FBS calorie shares for 2010–13.

| Statistic | Value |
|---|---|
| Median across WFP countries | 0.79% |
| Interquartile range | 0.52–1.19% |
| Most exposed | DR Congo 1.73%, Uganda 1.58%, Niger 1.57%, Malawi 1.56%, Zambia 1.55%, Ghana 1.55%, Rwanda 1.51% |

The most exposed countries get 80–93% of their staple calories from locally produced maize, coarse grains and roots. The exposure is, by construction, almost a linear function of that share (r = 0.996), so this is a descriptive mapping, not separate evidence.

## 10. Positioning relative to the closest literature (checked 2026‑10‑07)

| Paper | Scope | Shock | Key finding | How this paper differs |
|---|---|---|---|---|
| Okou, Spray & Unsal (2022, IMF WP 22/135) | 15 SSA countries, 5 staples | Global prices; natural‑disaster and war dummies | Pass‑through ≈ 1 for imported staples; disasters raise prices 1.8% | Mirror image: **local** staples respond to **local** weather. Continuous gridded shocks at each market, 86 countries, local projections with placebos, production mechanism, ML heterogeneity |
| Brown & Kshirsagar (2015, *GEC*) | 554 markets, 2008–12 | Local weather and international prices | 20% of markets weather‑sensitive | Pooled causal estimates over 26 years; tradability gradient; selection tests |
| Kotz et al. (2024, *Commun. Earth Environ.*) | National CPIs, 121 countries | Temperature | Heat raises food inflation for 12 months | Market‑level data; who pays (tradability, aridity); supply mechanism |
| Bohorquez‑Penuela et al. (2026); Nino (2026, *Food Policy*) | Colombia | Weather or landslides | Heterogeneity driven by farm and network characteristics | Global scope; causal forest validated out of sample |

**Proposed contribution statement.** *Across about 25,000 local markets in 86 countries, adverse local weather raises staple prices by about 1% per s.d. within six months. The burden falls entirely on locally produced staples. Traded rice and wheat are insulated even though their local production falls. Arid and low‑import markets bear up to four times the average effect. World‑market conditions do not amplify local shocks.*
