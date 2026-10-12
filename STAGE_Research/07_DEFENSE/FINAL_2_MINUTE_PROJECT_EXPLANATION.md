# 2-Minute Project Explanation

## 1. Problem (~20s)

India records nearly five lakh road accidents a year, but national totals alone cannot tell us where, when, or under what reported conditions they happen. Different official datasets also use different definitions, so analysis without validation and vintage separation is unreliable.

## 2. Objective (~15s)

My question: how do geographical, temporal, seasonal, environmental and severity factors associate with accident occurrence and severity across India? Observational throughout: association, never causation.

## 3. Data (~20s)

Primary benchmark is MoRTH 2018-2024: 254 state-years across 38 entities. Kept separate: NCRB 2024 monthly data, IMD weather with 236 matched state-years, seven verified 2024 supporting modules, Tamil Nadu districts, and a conditional 2014-17 historical candidate.

## 4. Methodology (~30s)

India, zone and state trends with OLS; Friedman test for zones; Pearson and Spearman correlations with FDR correction for weather; shares and fatality ratios for supporting factors; then supervised prediction on state-years (train 2019-22, test 2023-24) versus a naive baseline, plus descriptive K-means with K selected by silhouette.

## 5. Major findings (~25s)

Fatalities rose 12.4% while accidents rose 3.7%; severity 33.50 to 36.33. Zones differ detectably. Rainfall correlates negatively, temperatures positively, with no severity link. Overspeeding is 70% of reported cases; two-wheelers 46% of deaths. All shares, never risk.

## 6. ML result (~20s)

The naive baseline, RMSE 1038.6 accidents and 286.3 fatalities, beat every trained model on held-out data. That honest null is the finding: aggregate features cannot reliably predict here. K-means gave two descriptive profiles, silhouette 0.356.

## 7. Application (~15s)

The platform is live with validated data, weather, statistics, audit trails and an upload workspace, ready for future microdata, exposure and GIS integration.

## 8. Limitation and close (~15s)

No exposure denominator, no microdata, no causal claims. The contribution is a reproducible, honestly validated analytical foundation. Thank you.

---

## 30-SECOND EMERGENCY VERSION

I analyzed MoRTH road-accident data for 2018-2024, 254 state-years, across geography, time, weather and severity factors. Fatalities rose faster than accidents; weather shows real but non-causal associations; tested ML models could not beat a naive baseline, which is itself the finding. The contribution is a validated, reusable analytics platform with all limits documented.

## 5 NUMBERS TO REMEMBER

1. 487,707 accidents and 177,175 fatalities in 2024.
2. Fatality ratio 33.50 to 36.33 per 100 accidents.
3. Weather N = 236 matched state-years.
4. Naive baseline RMSE 1038.6 accidents, 286.3 fatalities, unbeaten.
5. K = 2, silhouette 0.356.

## 5 SENTENCES TO REMEMBER

1. This is an observational study, so I report associations, never causes.
2. Weather correlations are real associations that may partly reflect state scale, not proof of effect.
3. The ML null result is a finding: aggregate features were insufficient for held-out prediction.
4. Counts are not risk without an exposure denominator, so I never rank states by danger.
5. MoRTH, NCRB, historical and weather sources were never silently merged.
