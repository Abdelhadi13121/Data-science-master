# First-stage results: exporter weather → world cereal prices

**Data.** IMF world prices from FRED: wheat and maize 1992–2026‑07, rice 2010–2026‑07. ERA5 0.25° monthly grids for 1990–2026‑09, built from 4 daily samples (`01_era5_monthly.py`). GPCP v2.3 monthly precipitation. 18 exporter crop regions with pre‑sample export weights (`02_exporter_instrument.py`).

**Design.** Local projections pooled over wheat, maize and rice, with commodity × calendar‑month fixed effects. Controls are 3 lags of Δln P and of the instrument. Driscoll–Kraay standard errors (Newey–West applied to the cross‑commodity sum) with h+1 lags. With one instrument, F = t².

## 1. The composite index (proposal baseline) is weak

| h | 0 | 1 | 2 | 4 | 6 | 8 | 12 |
|---|---|---|---|---|---|---|---|
| β (%) | 0.68 | 1.20 | 0.95 | 1.20 | 1.24 | 1.53 | 1.20 |
| F | 4.5 | 5.0 | 2.2 | 2.3 | 1.9 | 2.6 | 1.0 |

## 2. The extreme‑heat component carries the signal, and it holds across pre‑declared variants

Response of world cereal prices (%) to a 1‑s.d. adverse heat shock in exporter crop regions:

| h | V2 heat | V3 heat, 2000+ | V4 season‑cumulative | V5 Black Sea weights ×2 |
|---|---|---|---|---|
| 0 | 1.51 (F 4.0) | 1.69 (4.1) | 1.20 (1.4) | 1.63 (4.1) |
| 2 | 4.05 (9.8) | 4.27 (10.1) | 5.05 (8.9) | 4.49 (10.2) |
| 4 | 6.15 (11.1) | 6.63 (12.0) | 7.44 (11.1) | 6.67 (12.5) |
| 6 | 6.31 (8.7) | 6.54 (8.3) | 7.21 (7.5) | 6.92 (9.4) |
| 8 | 6.96 (8.2) | 6.66 (6.4) | 7.91 (6.7) | 7.65 (9.0) |
| 12 | 5.40 (2.7) | 3.93 (1.4) | 5.56 (1.8) | 6.05 (3.3) |

**Interpretation.** Heat shocks in exporter regions raise world cereal prices by **6–8% within 4–8 months**. This is consistent with Schlenker & Roberts (2009), where degree days above 29–30°C drive yields. The instrument also captures the 2012 US Corn Belt drought, the 2010 Russian heatwave and the 2021 Northern Plains drought as its largest values.

## 3. Validity check: no pre‑trend once persistence is controlled

| Window before t | Controls | β (%) | t |
|---|---|---|---|
| t−2..t−1 | none | 0.91 | 1.75 |
| t−4..t−1 | none | 2.45 | 2.26 |
| t−2..t−1 | Z lags 1–2 | 0.41 | 0.72 |
| t−4..t−1 | Z lags 1–4 | 1.48 | 1.39 |
| t−7..t−1 | Z lags 1–7 | 1.61 | 0.96 |

Without controls, the shock appears to predict earlier price rises. This reflects within‑season persistence of heat (AR(1) of 0.20–0.34). With the lag controls used in the main specification, the placebo is insignificant.

## 4. Implications for the paper

- **Strength.** F ≈ 8–12.5 at h = 2–5 is below the Montiel Olea–Pflueger threshold (≈ 23 for 10% bias). The local‑market stage must therefore report **reduced‑form** estimates (local price on exporter heat) and **Anderson–Rubin weak‑IV‑robust** confidence sets. Point‑estimate 2SLS should not be the headline.
- **Proposal revision.** The heat‑only index replaces the composite as the primary instrument, a choice justified by agronomy before seeing local‑market outcomes. The composite and the other variants stay as robustness checks, all reported.
- **Local‑market estimates.** These require the WFP market panel (`04_build_wfp_panel.py`, `05_estimate.py`). The estimators were validated by Monte Carlo (`output/tables/*_panel_sim.csv`): 2SLS recovers β_h and γ_h within sampling error, while OLS is biased upward.
