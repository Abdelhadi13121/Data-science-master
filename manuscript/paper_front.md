---
title: "Who pays for local droughts? Weather shocks and staple food prices in 3,200 local markets"
---

# Abstract {.unnumbered}

Climate shocks are expected to raise food prices, but the evidence comes mostly from national price indices or single countries, and it says little about which foods and which markets absorb the shock. We combine 26 years of monthly retail prices from 3,221 markets in 85 low- and middle-income countries with reanalysis weather measured at each market. Panel local projections with series × calendar-month and country × year fixed effects show that a one-standard-deviation adverse weather anomaly (hotter and drier than normal) raises local staple prices by 0.99 percent after six months (95% CI 0.46 to 1.53). The effect persists for at least a year and survives correction for testing at seven horizons. The burden falls on staples that rarely cross borders. Maize, sorghum and millet, and roots and tubers respond by 1.2 to 1.7 percentage points more than rice. Rice and wheat prices do not respond, even though local weather lowers their national production by as much as it lowers other crops. A causal forest, validated on countries it was not trained on, finds that one third of market-months face a response four times the average, concentrated in arid areas. World price conditions do not amplify the local effect. Placebo tests, selection tests and eighteen alternative specifications support these results. Monitoring and assistance aimed at weather-driven food price spikes should target locally traded staples in dry markets, where trade cannot absorb a bad harvest.

**Keywords:** food prices; weather shocks; drought; market integration; tradability; local projections; causal forest

# 1. Introduction

A bad rainy season raises the price of food in the markets where poor households buy it, and higher food prices cut the real income of net food buyers and worsen child health (Ivanic and Martin, 2008; Grace et al., 2014). Climate change makes these seasons more frequent. National evidence now shows that heat raises food inflation for up to a year (Kotz et al., 2024). That evidence has two gaps that matter for policy. National price indices average across foods and markets, so they cannot say which foods carry the shock or where it lands. And most market-level studies cover a single country or a few hundred markets over short periods (Brown and Kshirsagar, 2015; Baffes et al., 2019; Kakpo et al., 2022), which makes it hard to know whether their findings apply elsewhere.

This paper asks who pays for local droughts. We assemble monthly retail prices for staple foods from the World Food Programme's market monitoring system for 3,221 markets in 85 countries between 2000 and 2026 and match each market to hot, dry and wet anomalies from the ERA5 reanalysis and satellite rainfall. With 757,136 market-months in the main sample, we can estimate the dynamic price response to local weather with fixed effects that remove each product's seasonal cycle in each market and every national shock in a given year. What remains is the variation in local weather relative to its seasonal norm, which is as close to random as observational data allow, and we test that claim with leads, pre-trends and an analysis of where the monitoring system chose to collect prices.

We find four things. First, a one-standard-deviation adverse anomaly raises local staple prices by about 1 percent after six months, with no reversal within a year. A two-standard-deviation drought, which occurs in about six percent of market-months, raises prices by about 2 percent from local weather alone, on top of any national harvest effect. Rainfall drives the response in the first six months and heat matters at longer horizons. Good seasons lower prices by about as much as bad seasons raise them.

Second, the burden falls on staples that do not cross borders. Maize, sorghum and millet, and cassava, yams and plantains respond by 1.2 to 1.7 percentage points more than rice. Rice and wheat prices do not respond at all. This is not because local weather spares rice and wheat: in FAOSTAT data, an adverse year lowers national rice production by 6.3 percent, about as much as the average across crops. Local supply falls for all staples, but only the prices of staples that cannot be replaced by imports adjust. This is the spatial arbitrage logic behind the law of one price (Fackler and Goodwin, 2001), and our results show it operating across a large share of the developing world.

Third, the response varies across markets far more than the average suggests. We train a causal forest (Athey et al., 2019) on half of the countries and evaluate it on the other half. Markets in the top third of predicted effects show a realized response of 2.2 percent at six months, against about 0.5 percent elsewhere. Aridity is the clearest predictor: dry places have thin local supply and fewer neighbors with surplus to draw on.

Fourth, the local effect does not depend on world market conditions. When world cereal prices are high, local weather shocks are not larger, and we can rule out that a world price spike doubles the local effect. A related exercise, reported in Appendix A, instruments world prices with weather in the main exporting regions to estimate how much of a world price shock reaches these markets. That instrument works for world prices but is too weak in the market panel, and we report it as a negative result.

The paper contributes to three literatures. The first studies how weather affects food prices in developing countries. Single-country studies document that drought raises prices and amplifies price seasonality (Kakpo et al., 2022), that traders respond to weather news before the harvest (Letta et al., 2022), and that domestic factors explain most local price variation in Tanzania (Baffes et al., 2019). Cross-country work uses national price indices (Kotz et al., 2024) or global climate indices such as El Niño (Emediegwu, 2024; Villoria, 2026). We provide pooled causal estimates at the market level for 85 countries, with weather measured at each market, and show where the effect concentrates.

The second literature studies how world prices reach local markets. Imported staples follow world prices closely (Okou et al., 2022), and imports reduce intra-annual price volatility in maize markets (Chen and Villoria, 2019). Our results are the other side of the same coin. Local staples follow local weather, and traded staples are insulated from it. Together these findings describe a split market in which households that eat traded staples carry world price risk and households that eat local staples carry local weather risk.

The third literature uses machine learning to study heterogeneity in development and agricultural economics. Causal forests have been used to map the profitability of fertilizer across sub-Saharan Africa (McCullough et al., 2022) and the effect of road closures on market prices in Colombia (Nino, 2026). We apply the method across countries and validate it on countries the forest has not seen, which guards against reading noise as heterogeneity.

The results matter for food security policy. Early warning systems already combine weather and market information to anticipate crises (Krishnamurthy et al., 2020; Davenport et al., 2021). Our estimates tell these systems which prices to watch and where: local staples in arid markets, not imported rice and wheat. They also bear on trade policy, since openness protects only the staples that are traded. Section 2 sets out the framework and predictions. Sections 3 and 4 describe the data and empirical strategy. Section 5 presents the results, Section 6 the robustness checks, Section 7 the discussion and policy implications, and Section 8 concludes.

# 2. Background and conceptual framework

## 2.1 Local supply, trade and storage

Most staple food in low-income countries is grown by smallholders under rainfed conditions and sold in local markets. When a local harvest fails, three margins absorb the shortfall: lower consumption, released storage and imports from other markets. Storage spreads the shortfall over the season and makes prices persistent (Deaton and Laroque, 1992). Imports cap the local price at the cost of bringing food from elsewhere. Which margin dominates depends on whether the good is traded across the market's boundary. Rice and wheat are largely imported in the countries we study, so their local price is anchored to an import parity price. Maize is traded regionally but often blocked by export bans and high transport costs. Sorghum, millet, cassava and yams rarely cross borders and are traded only over short distances (Baffes et al., 2019; Yami et al., 2020).

## 2.2 A simple spatial arbitrage model

Consider a market *m* and a staple *k*. Local supply is $Q_{mk}(W_m)=\bar Q_{mk}(1-\omega_{k}W_m)$, where $W_m$ is the adverse weather anomaly and $\omega_k>0$ is the sensitivity of output to weather. Local demand has price elasticity $-\varepsilon_{mk}<0$. Without trade, the market clears at the autarky price $p^{A}_{mk}(W_m)$, which rises with $W_m$:

$$
\frac{\partial \ln p^{A}_{mk}}{\partial W_m}\approx\frac{\omega_k}{\varepsilon_{mk}}. \qquad\qquad (4)
$$

Traders bring food in whenever the local price exceeds the import parity price $p^{M}_{mk}=G_k\,E\,(1+\tau_{m})$, where $G_k$ is the world price, *E* the exchange rate and $\tau_m$ the proportional cost of moving food to market *m*. The local price is therefore

$$
p_{mk}=\min\{\,p^{A}_{mk}(W_m),\;p^{M}_{mk}\,\}. \qquad\qquad (5)
$$

When import parity binds, a local supply shock is absorbed by imports and $\partial \ln p_{mk}/\partial W_m=0$. When it does not bind, the response equals Eq. (4). Storage (Deaton and Laroque, 1992) smooths the response over the months after the harvest but does not change its sign.

## 2.3 Predictions

The model gives four predictions, which map to the hypotheses in Section 4.3.

**P1 (H1).** Adverse local weather raises local prices of staples for which import parity does not bind, with a lag that reflects the harvest and storage cycle.

**P2 (H2, H5).** Local weather lowers local production of every staple ($\omega_k>0$ for all *k*), but prices respond only for staples whose import parity rarely binds. Traded staples such as rice and wheat should show a production response without a price response.

**P3 (H3).** The price response is larger where local demand is less elastic and supply more weather-sensitive, as in arid and thinly traded markets, and where transport costs $\tau_m$ are high, because import parity binds less often there. It is smaller where a country already relies on imports.

**P4 (H4).** A higher world price raises $p^{M}_{mk}$ and makes import parity bind less often, which could amplify the local response for traded staples. For staples that are not traded, world prices should not change the response. Pooled across staples, the model allows but does not require state dependence, and we test it directly.
