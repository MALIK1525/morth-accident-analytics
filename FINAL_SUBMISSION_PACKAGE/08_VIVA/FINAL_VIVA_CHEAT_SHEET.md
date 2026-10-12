# Viva Cheat Sheet

Title: A Multi-Level Data-Driven Analysis of Road Traffic Accidents in India
Short: Data-Driven Road Traffic Accident Analysis in India
RQ: How do geographical, temporal, seasonal, environmental and severity factors associate with accident occurrence and severity? (association, not causation)
Objectives: 13 (trends, geography, temporal, weather, violations, collisions, road users, validation, prediction-vs-baseline, clustering, limits, platform)
Data: MoRTH 2018-2024 primary; NCRB 2024 monthly separate; IMD weather 236/18; 7 supporting modules; TN districts; history 2014-17 conditional
Period: 2018-2024. Unit: State-Year. State-years: 254. Entities: 38. Zones: 6.

## TOP 10 NUMBERS
1. 487,707 accidents, 177,175 deaths, 471,441 injured (2024 India)
2. +3.7% accidents, +12.4% fatalities; ratio 33.50 to 36.33
3. OLS slopes ns (p=.44 / p=.09)
4. Friedman 25.29, p=3.0e-4, W=.72
5. Rain r=-.234/-.376; Tmax +.452/+.498; Tmin +.366/+.340
6. NCRB May 8.84%, Jul 7.46%, chi2=1276
7. Overspeeding 70.7%/70.3% (reported)
8. Two-wheelers 46.2%, pedestrians 20.6% (shares)
9. Naive RMSE 1038.6 / 286.3 beats all trained; train N=141, test N=72
10. K=2, silhouette .356, clusters 17+6

## TOP 10 METHODS
OLS slopes, Pearson+Spearman, chi-square, Friedman, FDR correction, effect sizes, rolling-origin validation, naive baseline, K-means, reconciliation audits.

## TOP 10 FINDINGS
Severity rising; zones differ; most state slopes descriptive; weather linked but non-causal; May peak; overspeeding dominant category; Hit-and-Run severest ratio; 2W largest share; naive wins; two descriptive profiles.

## TOP 10 LIMITATIONS
No microdata/coords, no vehicle stock/AADT, no MoRTH monthly, 2023-24 state injuries N/A, 3 weather vars, N=213, history conditional, NCRB separate, scale confounding, annual grain.

## TOP 10 DEFENSE SENTENCES
1. Association, not causation, throughout.
2. Counts are not risk without exposure.
3. Reported categories are records, not proven causes.
4. The ML null is a finding, not a failure.
5. Vintages were never silently merged.
6. Missing stays missing, never zero.
7. Training metrics never decide; test metrics do.
8. Clusters are descriptive profiles, never risk labels.
9. The baseline proves whether learning adds value.
10. Every number traces to a verified source.

## IF I DON'T KNOW THE ANSWER
1. "Based on the available dataset, I cannot make that conclusion."
2. "That variable was not available in the benchmark data."
3. "I treated that as an association rather than a causal relationship."
4. "That would require accident-level or exposure-normalized data, outside the available dataset."
5. "That is documented as a limitation; I did not estimate beyond the evidence."
