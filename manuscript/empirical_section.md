---
title: "Who pays for local droughts? Weather shocks and staple prices in 3,200 local markets"
subtitle: "Empirical sections (draft for *Food Policy*)"
---

# 3. Data

## 3.1 Local food prices

Retail prices come from the World Food Programme price database, distributed through the Humanitarian Data Exchange as yearly global files (accessed 7 October 2026). We keep retail quotations for five staple groups: wheat products (grain, flour, bread and pasta), maize grain and flour, rice, sorghum and millet, and roots and tubers (cassava, yams and plantains). Oils, seed, food aid and milling-cost entries are dropped.

A series is one product in one market, measured in one unit. We take the monthly median of all quotations in a series and work in logs. When a price moves by more than 1.5 log points in a single month, we set that observation to missing; in the raw files such jumps almost always come from a change of unit or currency. The sample starts in January 2000.

At the six-month horizon the estimation sample has 757,136 market-months from 15,561 series in 3,221 markets and 85 countries, running from May 2000 to April 2026 (Table 1). Coverage is uneven over time. There are about 1,300 market-months in 2000 and roughly 80,000 a year after 2020, and Section 6 shows that this expansion does not drive the results. Rice is the largest group (226,440 market-months), followed by wheat (173,296), maize (139,634), sorghum and millet (135,340) and roots and tubers (82,426). We also build a monthly exchange rate for each country as the median ratio of local-currency to US-dollar prices in the same files.

## 3.2 Local weather

Weather is measured at each market's coordinates. Temperature and soil moisture come from the ERA5 reanalysis (Hersbach et al., 2020) at 0.25°, read from the public analysis-ready archive. For every month we compute mean 2 m temperature from four daily samples (00, 06, 12 and 18 UTC), extreme-heat degree days $\mathrm{HDD30}=\sum_d \max(T^{\max}_d-30^{\circ}\mathrm{C},0)$, and mean volumetric soil water in the top layer. Precipitation comes from GPCP v2.3 (Adler et al., 2018) at 2.5°.

Each variable is aggregated over three months, the usual convention for standardized drought indices, and expressed as a z-score against the market's own 1991 to 2020 climatology for that calendar month. In deserts and dry seasons the climatological variance can be close to zero, which makes z-scores explode. To prevent this, we floor the standard deviation at the 10th percentile of positive standard deviations across markets and cap z-scores at ±4. Where extreme heat never occurs in a given season, the heat component uses the temperature anomaly instead. The index averages the three components in their adverse direction and rescales the result to unit standard deviation:

$$
W_{mt}=\frac{\tilde W_{mt}-\overline{\tilde W}}{\operatorname{sd}(\tilde W)},\qquad
\tilde W_{mt}=\tfrac13\left(z^{\text{heat}}_{mt}-z^{\text{soil}}_{mt}-z^{\text{rain}}_{mt}\right). \qquad\qquad (1)
$$

Positive values mean hotter and drier than normal for that market and season. In the estimation sample W has mean 0.30 and standard deviation 1.10 (Table 1). The positive mean reflects warming since the 1991 to 2020 base period; detrending makes no difference (Section 6). A quarter of market-months lie above W = 1, 6.1 percent above W = 2, and 11.1 percent below W = −1.

Before estimating anything, we checked the index against documented events. Averaged over each country's monitored markets in the main growing season, it reads +3.05 in Zambia (January to March 2024, the El Niño drought), +2.01 in Malawi (January to March 2016) and +2.02 in Zimbabwe (January to March 2024). It reads −2.48 in Pakistan during the 2022 floods (July to September) and −1.65 in Kenya during the wet March to May season of 2020.

## 3.3 Other data

World prices for wheat, maize and rice are IMF benchmark series taken from FRED and enter only as controls; coarse grains and roots are matched to the maize price. National crop production for the mechanism comes from FAOSTAT, by country, crop and year, for 2000 to 2024. Three policy moderators complete the data. Cereal import dependence is imports over domestic supply, averaged over 2010 to 2013, from the FAOSTAT Food Balance Sheets. Conflict exposure counts UCDP-GED (v26.1) fatalities within 50 km of the market over the previous 12 months. Remoteness is the distance to the nearest city of at least 500,000 people in Natural Earth. Staple calorie shares by group, also from the Food Balance Sheets for 2010 to 2013, are used for the welfare mapping.

**Table 1. Descriptive statistics, estimation sample at h = 6**

{{TABLE1}}

*Notes:* Price and exchange-rate changes in log points × 100. W and its components are standardized as described in Section 3.2. The extreme exchange-rate values come from hyperinflation and redenomination episodes; Section 6 drops those economies.

# 4. Empirical strategy

## 4.1 Baseline local projections

We estimate the cumulative response of local prices to an adverse local weather shock with panel local projections (Jordà, 2005). For series *i* in market *m* and country *k*, and for horizons $h\in\{0,2,4,\ldots,12\}$ months,

$$
\ln p_{i,t+h}-\ln p_{i,t-1}=\delta_h W_{m t}+\sum_{l=1}^{3}\left(\rho_{hl}\,\Delta\ln p_{i,t-l}+\phi_{hl}W_{m,t-l}+\kappa_{hl}\,\Delta G_{c,t-l}\right)+\kappa_{h0}\,\Delta G_{ct}+\theta_h\,\Delta E_{kt}+\alpha^{h}_{i,s(t)}+\lambda^{h}_{k,y(t)}+\varepsilon_{i,t+h}. \qquad\qquad (2)
$$

Here $W_{mt}$ is the index in Eq. (1), $\Delta G_{ct}$ the monthly log change in the matched world price, and $\Delta E_{kt}$ the monthly log change in the exchange rate. The fixed effects $\alpha_{i,s(t)}$ are defined for each series and calendar month, and $\lambda_{k,y(t)}$ for each country and year.

*Estimand.* $\delta_h$ is the percent change in the local retail price h months after a one-standard-deviation adverse weather anomaly, measured against the month before the shock.

*Identification.* The coefficient comes from deviations of weather from its seasonal norm within a series, after removing anything common to a country in a given year. The series × calendar-month effects absorb each product's seasonal price cycle in each market. The country × year effects absorb inflation, exchange-rate regimes, policy changes and the national harvest. Lagged weather separates a new shock from the persistence of earlier anomalies, and lagged price changes absorb momentum.

The identifying assumption is that, conditional on these terms, local weather anomalies are unrelated to other local shocks to food demand or supply. It would fail if weather set off conflict, migration or market closures that moved prices through some channel other than local supply, or if traders anticipated anomalies before month *t*. We test anticipation with leads (Section 6) and conflict as a moderator (Section 5.4).

The remaining choices were fixed in a pre-analysis plan committed to the project repository before estimation. Horizons run to 12 months, one agricultural cycle. Three lags match the aggregation window of W. The contemporaneous world price change is included because a single market cannot move it.

## 4.2 Inference

Standard errors are clustered two ways, by country (85 clusters) and by month (312 clusters), following Cameron et al. (2011). Weather is spatially correlated within countries, and common shocks such as world prices and El Niño reach every market in the same month. Because effects are estimated separately at seven horizons, we also report Holm (1979) adjusted p-values. Fixed effects are removed by iterative demeaning, with a convergence check before every regression.

## 4.3 Hypotheses

We stated five hypotheses before estimation.

H1. Adverse weather raises local prices once the harvest effect materializes, so $\delta_h>0$ for $h\geq 2$.

H2. The effect is larger for staples that rarely cross borders (maize, sorghum and millet, roots and tubers) than for rice and wheat, whose local prices are held near import parity. We test this by interacting W with product-group indicators, using rice as the reference.

H3. The size of the effect varies predictably with a market's climate, remoteness and diet.

H4. The local effect does not depend on world-market conditions. We interact W with $\Delta G_{ct}$ and with an indicator for the world price lying above its 24-month moving average.

H5. Adverse weather lowers production of traded and local staples alike. If it left rice and wheat output unchanged, the contrast in H2 could reflect the absence of a supply shock rather than trade.

## 4.4 Heterogeneity and mechanism

For H3, we residualize the six-month outcome and W on the fixed effects and controls of Eq. (2) and fit a causal forest with W as a continuous treatment (Athey et al., 2019). The forest uses honest splitting, 400 trees and leaves of at least 200 observations. Its inputs are distance to the coast, climatological aridity (log mean annual rainfall), climatological heat exposure, absolute latitude, product group and a label for imported products.

A flexible learner can mistake noise for heterogeneity, so we cross-fit by country. The forest is trained on a random half of countries and predicts effects for the other half, then the halves swap. We sort market-months into terciles of predicted effect and re-estimate Eq. (2) inside each tercile, using only countries the forest did not see. If the forest has found heterogeneity that exists, realized effects should rise across terciles. A linear projection of the effect on standardized moderators, with two-way clustered errors, complements the forest.

For H5 we estimate

$$
\ln Q_{ckt}=\beta\,\overline{W}_{ct}+\mu_{ck}+\tau_{kt}+u_{ckt}, \qquad\qquad (3)
$$

where $Q_{ckt}$ is production of crop *k* in country *c* and year *t*, and $\overline{W}_{ct}$ is the annual mean of W across the country's monitored markets. Standard errors are clustered by country.

The three policy moderators (import dependence, conflict exposure and remoteness) were added in a dated addendum to the pre-analysis plan after the main estimates and before their own estimation. Each is interacted with W at h = 6, and we label the results exploratory.

## 4.5 Choices not taken

The project began with a different design: it instrumented world price changes with weather shocks in the main exporting regions, to measure how much of a world price shock reaches local markets. At the aggregate level the instrument works, moving world cereal prices by 6 to 8 percent within four to eight months (F between 8 and 12). In the market panel it is too weak, because country × year effects strip out the annual variation in world prices: first-stage F lies between 0.5 and 9.6 across horizons. Anderson-Rubin confidence sets for pass-through are uninformative at every horizon except two months, where they bound the pass-through of supply-driven world price shocks at 0.11. We report that design in the Online Appendix and use it for no result in the main text. The local weather effect studied here does not depend on it.

We also considered an index built from rainfall alone, as in much of the price literature. The joint index is preferred because heat and soil moisture capture crop stress that rainfall misses in irrigated and high-evaporation areas. Panel B of Table 2 reports the components separately, so the rainfall-only response can be read directly.

# 5. Results

## 5.1 Local weather raises local staple prices

Adverse local weather raises local staple prices after a delay of two to four months, and the effect lasts a year (Table 2, Panel A; Figure 1). Nothing happens in the month of the shock (−0.00 percent, SE 0.10). Prices are 0.42 percent higher per standard deviation of W after two months (SE 0.20), 0.87 percent after four (SE 0.26) and 0.99 percent at the six-month peak (95% CI 0.46 to 1.53; 757,136 market-months). At twelve months the effect is still 0.84 percent, with no sign of reversal. The effects from four to twelve months survive the Holm correction across seven horizons, with adjusted p-values between 0.002 and 0.009. The two-month effect does not (adjusted p = 0.066).

The magnitudes matter in practice. A drought of two standard deviations, which occurs in 6.1 percent of market-months, implies prices about 2 percent higher within six months from local weather alone; the Zambian 2024 anomaly of +3.05 implies about 3 percent. These are partial effects. Because the country × year effects remove national inflation and the country's harvest in that year, they measure the local part of a price shock, not the national one.

**Table 2. Response of local prices to adverse local weather (percent per 1 s.d.)**

{{TABLE2}}

*Notes:* Local projections, Eq. (2). Dependent variable: $100\times(\ln p_{t+h}-\ln p_{t-1})$. Series × calendar-month and country × year fixed effects. Controls: three lags of Δln p, W and ΔG; contemporaneous ΔG; ΔE. Standard errors, two-way clustered by country (85) and month (312), in parentheses. Panel B enters the three weather components jointly; Panel C replaces W with bins. \*\*\* p < 0.01, \*\* p < 0.05, \* p < 0.1.

Rainfall drives the early response (Table 2, Panel B; Figure 3). A one-standard-deviation rainfall deficit raises prices by 0.49 percent at two months and 0.79 percent at four and six months (SE 0.25), the stretch between a failed growing season and the lean season. Heat works later. Its effect is small and imprecise up to eight months, then reaches 0.56 percent at ten months and 0.80 percent at twelve (SE 0.32). Once rainfall is controlled for, soil dryness adds little. The timing fits the crop cycle: a rainfall shortfall shows in the fields and in traders' expectations during the season, the channel Letta et al. (2022) document in India, while heat damage becomes visible only when a short harvest comes in.

The response is close to linear and roughly symmetric (Panel C, reference −1 < W ≤ 1). Dry months with 1 < W ≤ 2 raise prices by 1.06 percent at four months (SE 0.25), and very dry months with W > 2 by 1.11 percent (SE 0.54). Wet months with W ≤ −1 lower them by 1.47 percent at six months (SE 0.61). Good seasons push local prices down by about as much as bad seasons push them up, so local markets pass on both kinds of supply shock.

## 5.2 Who pays: tradability (H2)

The response falls almost entirely on staples that rarely cross borders (Table 3; Figure 2). Rice, the reference product, shows a small and insignificant effect at every horizon (0.40 percent at six months, SE 0.27), and wheat cannot be told apart from rice (interaction −0.00 at six months, SE 0.33). Maize behaves very differently. It rises 1.41 pp more than rice at two months (SE 0.30) and 1.67 pp more at four (SE 0.42). Sorghum and millet add 1.40 pp at four months (SE 0.66), and roots and tubers 1.46 pp at six (SE 0.56). Products labelled as imported respond less than other products in the same market (−0.61 pp at four months, SE 0.38), but the difference is not significant, and with a minimum detectable effect of 1.1 pp a moderate gap cannot be ruled out.

**Table 3. Heterogeneity by product and world-market state (percent per 1 s.d.)**

{{TABLE3}}

*Notes:* As Table 2. Interaction rows report differences from the reference group. "World price above 24-m mean" equals one when the matched world price exceeds its 24-month moving average.

The obvious reading of Table 3 is that import parity caps the price of traded staples, so a local shortfall is met by imports rather than by a higher price. A competing explanation is that rice and wheat in these markets are largely imported and local weather never touches their supply. Table 5 rules this out. An adverse year lowers national production by 7.4 percent per standard deviation across the eight crops (SE 2.3; 7,233 country-crop-years, 86 countries). Rice output falls by 6.3 percent (SE 2.8), and the gap between rice and wheat on one side and local staples on the other is small and insignificant (+3.2 pp, SE 3.4). Maize (−11.3 percent) and sorghum (−16.9 percent) fall most.

Local weather therefore cuts the supply of traded and non-traded staples alike, yet only the prices of non-traded staples move, which is what spatial arbitrage predicts. Roots and tubers are the exception on the production side: their output does not respond (between −0.6 and −2.7 percent, none significant), while their prices do. Households switching from scarce cereals to roots would produce this pattern, but FAOSTAT imputes root-crop output for many countries, so we do not lean on it.

**Table 5. Production response to adverse weather (FAOSTAT, 2000 to 2024)**

{{TABLE5}}

*Notes:* Eq. (3). Dependent variable: ln production. Country × crop and crop × year fixed effects; standard errors clustered by country.

## 5.3 Which markets respond most (H3)

The forest finds large differences across markets, and they hold up out of sample (Table 4, Panel A). In countries it was not trained on, the tercile it ranks highest shows a six-month response of 2.16 percent (SE 0.51). The lowest and middle terciles show 0.47 percent (SE 0.23) and 0.50 percent (SE 0.22). The gap between the top and middle terciles is 1.66 pp (SE 0.44). A third of market-months thus carry roughly four times the average burden.

**Table 4. Heterogeneity in the six-month response**

{{TABLE4}}

*Notes:* Panel A: terciles of out-of-sample predicted effects from a causal forest cross-fitted by country halves; δ re-estimated within each tercile with two-way clustered errors. Panel B: linear projection with standardized continuous moderators; product groups relative to rice.

Aridity is the clearest continuous driver (Panel B). One standard deviation less mean rainfall raises the response by 0.44 pp (SE 0.15). Markets in dry climates have thin local supply, carry little storage from year to year and have fewer surplus neighbors to draw on, so a bad season moves their prices more. The product contrasts of Table 3 appear again (maize +1.32 pp and sorghum and millet +1.26 pp relative to rice). Distance to the coast, heat climatology and the imported label do not predict the response, and absolute latitude is borderline (−0.41 pp, SE 0.24). The forest's variable importances differ between the two country halves (latitude scores 0.95 in one and 0.23 in the other), so we treat them as descriptive and base inference on the calibration test and the linear projection.

## 5.4 Policy moderators and world-market state

The three policy moderators lean the way the arbitrage mechanism predicts, but none reaches significance (Table 6; h = 6, 547,980 market-months in 73 countries). In the joint model, a one-standard-deviation increase in cereal import dependence lowers the response by 0.28 pp (SE 0.16, MDE 0.46 pp), and one standard deviation more remoteness raises it by 0.19 pp (SE 0.11, MDE 0.30 pp). Both sit close to their detection thresholds. Conflict exposure changes nothing (+0.15 pp, SE 0.23), and its MDE of 0.66 pp lets us rule out amplification larger than about 70 percent of the average effect.

**Table 6. Policy moderators of the six-month response (exploratory)**

{{TABLE6}}

*Notes:* Main specification at h = 6 with W interacted with standardized moderators. MDE = 2.8 × SE (80% power, 5% two-sided test).

The local weather effect does not depend on world-market conditions either (H4). When the world price sits above its 24-month average, the interaction at six months is 0.32 pp (SE 0.33, MDE 0.94 pp). The interaction with the concurrent world price change is −0.04 pp per standard deviation of ΔG (MDE 0.31 pp). A world price spike therefore does not double the local weather effect. This matches, from the other direction, the null we found when testing whether local drought amplifies world price pass-through.

## 5.5 Exposure of national diets

Weighting the product-specific effects at six months by each country's staple calorie shares gives the price rise of a typical staple basket after a one-standard-deviation local drought. It is 0.79 percent in the median country (interquartile range 0.52 to 1.19) and highest in DR Congo (1.73), Uganda (1.58), Niger (1.57), Malawi (1.56), Zambia (1.55) and Ghana (1.55). These countries draw 80 to 93 percent of staple calories from maize, sorghum and millet, and roots and tubers. Because the measure is built from those shares, its correlation with them (0.996) holds by construction; it shows where the estimated effects land and is not separate evidence.

# 6. Robustness

Table 7 reports the six-month effect under alternative choices, grouped by the threat each one addresses. All were added after the main estimates and are labelled exploratory.

**Table 7. Robustness of the six-month effect**

{{TABLE7}}

*Notes:* Each row changes one element of the baseline in the first row. Standard errors two-way clustered by country and month unless stated.

Two falsification tests support the causal reading. Weather six months in the future, added to Eq. (2), has no effect on current price changes (−0.05 pp at h = 0, SE 0.07; −0.12 pp at h = 2, SE 0.19). Weather at month *t* does not predict price changes from t−4 to t−1 (−0.15 pp, SE 0.16). Under the decision rule in the pre-analysis plan, the causal interpretation stands.

WFP decides which markets to monitor, often in response to crises, so we tested for selection in two ways. First, the month a market enters the panel is unrelated to mean W in the three preceding months (−0.05 pp against a mean monthly entry rate of 0.46 percent, SE 0.03; country × year and market fixed effects). Second, among series already monitored before 2010 the effect is larger, at 1.66 percent (SE 0.43), so the expansion of coverage after 2020 dilutes the estimate rather than producing it. Dropping ten crisis and hyperinflation economies gives 1.03 percent, and ending the sample in 2019 gives 1.08 percent.

How W is built matters in one predictable way. The estimate rises with the aggregation window, from 0.56 percent for one month to 0.81, 0.99 and 1.40 percent for two, three and six months. Prices respond to accumulated seasonal anomalies, not to monthly weather, which makes our three-month baseline conservative. For the same reason the monthly innovation of the three-month index has no detectable effect (0.13 percent, SE 0.12). Capping z-scores at ±3 or ±5, removing the cap, or detrending W by market leaves the estimate between 0.94 and 1.02 percent. In US dollars the effect is 0.76 percent (SE 0.29); it is slightly smaller because dollar prices also carry exchange-rate noise. Winsorizing the outcome at the 1st and 99th percentiles gives {{WINS6}}.

Clustering on 2° or 5° grid cells crossed with month raises the t-statistic to 4.48 and 3.76, and clustering by country alone gives 3.95. The baseline two-way clustering by country and month is the most conservative of these.

# 7. Discussion

## 7.1 Relation to the literature

Table 8 compares our estimates with the closest studies.

**Table 8. Comparison with closest studies**

| Study | Sample | Shock and method | Estimate | This paper |
|---|---|---|---|---|
| Brown and Kshirsagar (2015) | 554 markets, 51 countries, 2008–12 | Vegetation-based weather and international prices; market-by-market regressions | Weather affects about 20% of markets | Extends: pooled causal estimate over 26 years and 85 countries; tradability gradient |
| Okou et al. (2022) | 15 SSA countries, 5 staples | Global prices; disaster and war dummies | Pass-through ≈ 1 for imported staples; disasters +1.8% | Mirror image: local staples follow local weather; continuous gridded shocks |
| Kotz et al. (2024) | National food CPIs, 121 countries | Monthly temperature, fixed effects | Heat raises food inflation for 12 months | Confirms persistence at market level; rainfall dominates early, heat late |
| Chen and Villoria (2019) | 76 maize markets, 27 net importers, 2000–15 | Imports, stocks, climate-induced production shocks | Imports lower intra-annual price variation | Confirms with price levels and all staples: tradability insulates |
| Baffes et al. (2019) | 18 Tanzanian maize markets | Domestic vs. regional and international drivers | Domestic factors explain two-thirds of explained variation | Extends to 85 countries; remoteness amplifies only weakly |
| Kakpo et al. (2022); Letta et al. (2022) | Niger; India | Rainfall shocks; drought news | Drought amplifies seasonality; pre-harvest price rises | Confirms timing: the rainfall effect peaks 4–6 months after the anomaly |
| Nino (2026) | Colombia, weekly | Landslide road closures (IV); causal forest | +0.5–0.9% in one week; peripheral markets most affected | First cross-country causal forest on weather shocks, validated out of sample |

Brown and Kshirsagar (2015) estimated weather effects market by market and found them in about a fifth of markets. Our pooled estimate is consistent with that share once heterogeneity is allowed for, since the top tercile carries most of the effect. Okou et al. (2022) show that imported staples follow world prices almost one for one. We find the reverse side of the same market: local staples follow local weather, and imported staples do not. Put together, the two results describe a split market in which households that eat traded staples carry world price risk and households that eat local staples carry local weather risk. Kotz et al. (2024) find that heat raises national food inflation for a year. Our market-level estimates confirm that persistence but trace it to rainfall at short horizons and heat at long ones; national indices average over products and hide the difference between traded and local staples.

## 7.2 Competing explanations

A drought lowers rural incomes and could reduce local demand, which would push prices down. If this happens, our estimates are net of it and understate the supply effect; it cannot explain a positive sign.

Weather could also raise prices by damaging roads rather than harvests, the channel Nino (2026) documents for landslides in Colombia. Two results argue against this as the main channel. Wet anomalies, which carry most of the flood and road risk, lower prices (−1.47 percent at six months), and distance to cities amplifies the effect only weakly (+0.19 pp per standard deviation).

Weather might instead set off conflict, which then raises prices, the feedback Raleigh et al. (2015) describe for African markets. Conflict exposure does not change the effect (+0.15 pp, MDE 0.66 pp), and the estimate is unchanged when the ten crisis economies are dropped. Finally, WFP could start monitoring markets after bad seasons, so that the sample over-represents shocks; the entry test rules this out.

What remains is a local supply shortfall passed through markets that are integrated for traded staples and segmented for local ones. The production results, with output falling for every major cereal, support that reading.

## 7.3 Implications

Weather-driven price risk concentrates in non-traded staples in arid markets, and that is where price monitoring and seasonal food assistance should go. The out-of-sample calibration shows that market characteristics known in advance can identify these places. In the most exposed tercile, a two-standard-deviation drought implies staple prices about 4 percent higher within six months. For a household spending half its budget on staples, that is a real income loss of about 2 percent from local weather alone.

Openness protects the staples that are traded. Lowering border frictions for maize, the one local staple that moves across regional borders, should narrow the gap, in line with Villoria (2026). World price spikes do not make local weather shocks worse, so policies aimed at the two risks can be designed separately.

## 7.4 Limitations

W is measured at the market rather than over the area that supplies it. Where that area lies far away, the estimate of $\delta_h$ is attenuated toward zero.

WFP coverage is selected. The entry test and the pre-2010 subsample suggest that any bias works against our findings, but neither rules out selection on unobserved fragility.

The policy moderators are measured with error (import shares are national and conflict is counted within a fixed radius), which biases their interactions toward zero. FAOSTAT root-crop production is partly imputed, which weakens the mechanism evidence for roots and tubers.

Finally, the estimates describe the markets WFP monitors, which are poorer and more exposed to crises than the average market in the same countries.

# References

Adler, R.F., et al., 2018. The Global Precipitation Climatology Project (GPCP) monthly analysis (new version 2.3) and a review of 2017 global precipitation. Atmosphere 9(4), 138.

Athey, S., Tibshirani, J., Wager, S., 2019. Generalized random forests. Annals of Statistics 47(2), 1148–1178. https://doi.org/10.1214/18-AOS1709

Baffes, J., Kshirsagar, V., Mitchell, D., 2019. What drives local food prices? Evidence from the Tanzanian maize market. World Bank Economic Review 33(1), 160–184. https://doi.org/10.1093/wber/lhx008

Brown, M.E., Kshirsagar, V., 2015. Weather and international price shocks on food prices in the developing world. Global Environmental Change 35, 31–40. https://doi.org/10.1016/j.gloenvcha.2015.08.003

Cameron, A.C., Gelbach, J.B., Miller, D.L., 2011. Robust inference with multiway clustering. Journal of Business & Economic Statistics 29(2), 238–249. https://doi.org/10.1198/jbes.2010.07136

Chen, B., Villoria, N.B., 2019. Climate shocks, food price stability and international trade: Evidence from 76 maize markets in 27 net-importing countries. Environmental Research Letters 14(1), 014007. https://doi.org/10.1088/1748-9326/aaf07f

Hersbach, H., Bell, B., Berrisford, P., et al., 2020. The ERA5 global reanalysis. Quarterly Journal of the Royal Meteorological Society 146(730), 1999–2049. https://doi.org/10.1002/qj.3803

Holm, S., 1979. A simple sequentially rejective multiple test procedure. Scandinavian Journal of Statistics 6(2), 65–70.

Jordà, Ò., 2005. Estimation and inference of impulse responses by local projections. American Economic Review 95(1), 161–182. https://doi.org/10.1257/0002828053828518

Kakpo, A., Mills, B.F., Brunelin, S., 2022. Weather shocks and food price seasonality in Sub-Saharan Africa: Evidence from Niger. Food Policy 112, 102347. https://doi.org/10.1016/j.foodpol.2022.102347

Kotz, M., Kuik, F., Lis, E., Nickel, C., 2024. Global warming and heat extremes to enhance inflationary pressures. Communications Earth & Environment 5, [VERIFY article number]. https://doi.org/10.1038/s43247-023-01173-x

Letta, M., Montalbano, P., Pierre, G., 2022. Weather shocks, traders' expectations, and food prices. American Journal of Agricultural Economics 104(3), 1100–1119. https://doi.org/10.1111/ajae.12258

Nino, G., 2026. Disruption in ground transportation: Natural disasters and disintegration of local food markets. Food Policy 140, 103051. https://doi.org/10.1016/j.foodpol.2026.103051

Okou, C., Spray, J., Unsal, D.F., 2022. Staple food prices in Sub-Saharan Africa: An empirical assessment. IMF Working Paper 22/135. International Monetary Fund, Washington, DC.

Raleigh, C., Choi, H.J., Kniveton, D., 2015. The devil is in the details: An investigation of the relationships between conflict, food price and climate across Africa. Global Environmental Change 32, 187–199. https://doi.org/10.1016/j.gloenvcha.2015.03.005

Villoria, N.B., 2026. Trade frictions and domestic food price stability in the presence of large-scale climate shocks. American Journal of Agricultural Economics 108(1), 285–308. https://doi.org/10.1111/ajae.12531
