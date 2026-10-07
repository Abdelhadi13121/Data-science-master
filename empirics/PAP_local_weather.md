# Pre-analysis plan: local weather shocks and local food prices

Committed before running any of the estimates below. The original compound‑shock design ended with a weak instrument and a null on amplification (`output/RESULTS_main.md`). Those results stay reported as they are. This plan fixes the revised paper's specifications in advance.

**Working title.** *Weather Shocks and Food Prices in 13,000 Local Markets: Who Pays for Local Droughts?*

## Research questions
1. **RQ1 (average dynamic effect).** How much, and for how long, does an adverse local weather shock (drought/heat) raise local retail food prices?
2. **RQ2 (tradability).** Is the effect larger for less‑traded staples (coarse grains, cassava/yams/plantain) than for internationally traded cereals (rice, wheat, maize), and smaller for products labelled "imported"? Spatial‑arbitrage theory predicts that it is.
3. **RQ3 (heterogeneity).** Which market characteristics predict larger price responses? Pre‑specified moderators: distance to the coast, climatological aridity, climatological heat exposure, latitude, product group, and the imported label.
4. **RQ4 (state dependence; secondary).** Does the local effect depend on world price conditions? This re‑tests amplification from the other side; it was null in the first design.

## Data
WFP retail prices (HDX) for 2000–2026, all staple groups (wheat, maize, rice, coarse, non‑traded). Local weather from ERA5 0.25° and GPCP at market coordinates. The index W is built as in `04_build_wfp_panel.py`: 3‑month aggregates, floored s.d., z‑scores clipped at ±4, unit s.d. Components are z_heat, z_swvl1 (soil moisture) and z_precip.

## Main specification (fixed)
For h ∈ {0, 2, 4, 6, 8, 10, 12}:

$$y_{i,t+h}-y_{i,t-1}=\delta_h W_{it}+\sum_{l=1}^{3}\left(\rho_{hl}\Delta y_{i,t-l}+\phi_{hl}W_{i,t-l}+\kappa_{hl}\Delta G_{c,t-l}\right)+\kappa_{h0}\Delta G_{ct}+\theta_h\Delta E_{kt}+\alpha_{i,m(t)}+\lambda_{k,y(t)}+\varepsilon$$

- **Fixed effects:** series × calendar month and country × year.
- **Inference:** standard errors two‑way clustered by country and month.
- **Estimand:** δ_h, the price response to a 1‑s.d. adverse local weather shock.

## Pre‑specified secondary analyses
1. **Components:** replace W with (z_heat, −z_swvl1, −z_precip) entered jointly.
2. **Nonlinearity:** W bins (≤ −1, (−1, 1] as reference, (1, 2], > 2).
3. **Tradability:** W × group dummies (rice is the reference); W × imported label.
4. **State dependence:** W × ΔG_t and W × 1[world price above its 24‑month moving average].
5. **Placebo:**
   - **Lead test:** W_{t+6}, the shock six months in the future, added to the main specification at h = 0 and h = 2. It should be ≈ 0.
   - **Timing test:** a shock at t should not predict the price change from t−4 to t−1, controlling for W lags.
6. **Heterogeneity (ML):** a causal forest (econml CausalForestDML, honest splitting) on FE‑residualized data at h = 6, with W as a continuous treatment and the RQ3 moderators. Folds are grouped by country. Reported outputs: best‑linear‑projection coefficients and the ranking of conditional effects by quintile.

## Decision rules
- All of the above are reported regardless of significance. No new moderators, samples or fixed‑effect structures are added without labelling them exploratory.
- If the lead placebo is significant at 5%, the causal reading of δ_h is withdrawn.
