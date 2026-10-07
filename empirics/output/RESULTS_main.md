# Main results: WFP market panel (real data, 2026‑10‑07)

**Sample.** WFP retail prices (HDX), 1990–2026‑10, wheat, maize and rice products:
- 13,002 market × commodity series with complete controls at h = 0;
- 631,230 market‑months at h = 0 and 488,959 at h = 12;
- up to 79 countries.

Local weather comes from ERA5 (0.25°) and GPCP at each market's coordinates. The local drought index W uses 3‑month aggregates, floored standard deviations and z‑scores clipped at ±4, rescaled to unit s.d. It was validated against known events (Zambia 2024 +3.05, Malawi 2016 +2.01, Pakistan floods 2022 −2.48).

**Specification.** Local projections with series × calendar‑month and country × year fixed effects. Controls: exchange‑rate change, and three lags of Δlnp, ΔG, W and Z. Standard errors are **two‑way clustered by country and month**. The instrument is exporter extreme heat (`RESULTS_first_stage.md`).

## 1. Robust findings (OLS / reduced form)

| h | World pass‑through (1‑month ΔG) | t | Local drought W (per s.d.) | t | Drought × ΔG | t |
|---|---|---|---|---|---|---|
| 0 | 0.029 | 2.7 | 0.0001 | 0.1 | −0.0005 | −0.1 |
| 2 | 0.103 | 5.0 | 0.0032 | 2.0 | −0.0108 | −1.0 |
| 4 | 0.157 | 5.1 | 0.0066 | 3.3 | −0.0100 | −0.8 |
| 6 | 0.200 | 4.8 | 0.0075 | 3.8 | −0.0093 | −0.5 |
| 8 | 0.222 | 4.9 | 0.0057 | 3.0 | −0.0099 | −0.5 |
| 12 | 0.197 | 4.4 | 0.0064 | 3.0 | −0.0059 | −0.3 |

- **World‑price pass‑through** builds to about 20% within 6–8 months and stays there.
- **Local drought** raises local cereal prices by 0.6–0.75% per s.d. after 4–6 months. Weather is plausibly exogenous, so this effect is causal under standard assumptions.
- **Compound amplification (the proposal's core hypothesis) is not supported.** The interaction is negative or zero at every horizon and never significant. The reduced‑form W × Z term is −0.0020 (t = −2.7) on impact and insignificant afterwards.

## 2. IV estimates: the exporter‑heat instrument is too weak in the market panel

| Design | Panel first‑stage F (h = 0, 2, 4, 6, 8, 12) |
|---|---|
| 1‑month ΔG instrumented (`05_estimate.py`) | 1.5, 1.4, 1.6, 1.4, 1.5, 1.9 |
| Cumulative LP‑IV (`05b_lpiv_cumulative.py`) | 1.2, **9.6**, 2.7, 1.5, 1.0, 0.5 |

- **Anderson–Rubin confidence sets** are unbounded at every horizon except **h = 2**. There, causal pass‑through of weather‑driven world price shocks lies in **[−0.39, 0.11]** at 95%. This rules out pass‑through above 11% within two months for supply‑driven shocks and is consistent with the OLS estimate of 0.07–0.10.
- **Why the panel is weaker than the aggregate first stage (F ≈ 8–12):**
  1. Country × year fixed effects absorb most cumulative world‑price variation, which happens at annual frequency, leaving only within‑year variation.
  2. The panel is dominated by 2020–2026, when the observation count rises from about 1,300 market‑months in 2000 to 80,000 a year.
  3. Two‑way clustering leaves only about 300 effective month clusters.
- **These fixed effects were pre‑specified.** Relaxing them after seeing the result would be a specification search, so this note does not do it.
- The double‑ML PLIV run was stopped because it relies on the same weak instrument; its output would not be interpretable.

## 3. Assessment for publication

- **The original design does not deliver a Q1 paper.** The causal IV channel cannot be identified with this instrument at monthly frequency, and the compound‑shock hypothesis is not supported.
- **What the data credibly support:**
  - a causal, exogenous local‑weather effect on local food prices across about 13,000 series in 79 countries;
  - a well‑estimated null on drought × world‑price amplification;
  - an AR bound on supply‑driven pass‑through at two months.
- These support a revised paper centred on the local weather shock. The local‑weather design does not depend on the instrument. See the options in the PR discussion.
