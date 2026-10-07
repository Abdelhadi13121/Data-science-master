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
