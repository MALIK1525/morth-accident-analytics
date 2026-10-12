# Presentation Script (~7-8 minutes, 25 slides)

| Slide | Target Time |
|------|-------------|
| 1 Title | 15s |
| 2 Problem | 20s |
| 3 Motivation | 15s |
| 4 Research Question | 15s |
| 5 Objectives | 20s |
| 6 Framework | 15s |
| 7 Data Sources | 25s |
| 8 Validation | 20s |
| 9 India Trends | 25s |
| 10 Geographical | 15s |
| 11 Zone | 20s |
| 12 State | 20s |
| 13 Temporal | 15s |
| 14 Seasonal/NCRB | 20s |
| 15 Weather | 30s |
| 16 Severity | 15s |
| 17 Violations | 20s |
| 18 Collision/Road-User | 20s |
| 19 Licence/Safety | 15s |
| 20 Statistics | 20s |
| 21 ML Methodology | 25s |
| 22 ML Results | 30s |
| 23 K-Means | 20s |
| 24 Limitations+Contributions | 25s |
| 25 Conclusion | 15s |
| TOTAL | ~465s (~7.75 min) |

---

## SLIDE 1 — Title

TIME: ~15 seconds

WHAT TO SAY: Good morning everyone. My project is a multi-level data-driven analysis of road traffic accidents in India. It examines how accident occurrence and severity vary across geography, time, season, environment and other reported factors, using verified official data from 2018 to 2024.

KEY POINT: Establish problem, multi-level scope, official-data basis.

TRANSITION: Let me start with why this problem matters.

## SLIDE 2 — Problem

TIME: ~20 seconds

WHAT TO SAY: Road accidents remain a major public-safety problem in India. In 2024 alone there were 487,707 accidents and 177,175 deaths. But national totals alone do not explain where, when, or under what reported conditions these accidents occur. Different official datasets also use different definitions and vintages, so a validated multi-level framework is needed before any honest analysis.

KEY POINT: Totals are not enough; validated framework required.

TRANSITION: That is what motivated this project.

## SLIDE 3 — Motivation

TIME: ~15 seconds

WHAT TO SAY: What this shows is the need for an India-wide understanding that separates state and zone differences, temporal patterns, weather associations, severity, and supporting factors, and then honestly tests whether prediction is even feasible with the available aggregate data.

KEY POINT: Scope of the contribution.

TRANSITION: This leads directly to my research question.

## SLIDE 4 — Research Question

TIME: ~15 seconds

WHAT TO SAY: My research question is: how do geographical, temporal, seasonal, environmental, roadway, vehicle and other available factors associate with the occurrence and severity of road traffic accidents across India? The important point here is that this is an observational study, so I report associations, not causation.

KEY POINT: Observational framing.

TRANSITION: From this question I derived thirteen objectives.

## SLIDE 5 — Objectives

TIME: ~20 seconds

WHAT TO SAY: The objectives cover India-wide trends, state and zone patterns, temporal and monthly structure, weather associations, violation and collision analysis, road-user distributions, statistical validation, predictive benchmarking against a naive baseline, clustering exploration, and limitation mapping. I will walk through each in turn.

KEY POINT: Roadmap of the talk.

TRANSITION: First, how the analysis is organized.

## SLIDE 6 — Research Framework

TIME: ~15 seconds

WHAT TO SAY: The framework flows from India to six zones to states and UTs, then temporal, weather, road and cause factors, severity, statistics, machine learning and clustering, and finally the reusable application. Each layer uses only the dataset vintage that actually supports it.

KEY POINT: Hierarchy with vintage separation.

TRANSITION: The data behind each layer.

## SLIDE 7 — Data Sources

TIME: ~25 seconds

WHAT TO SAY: The primary benchmark is MoRTH data for 2018 to 2024: 254 state-year observations across 38 reporting entities. Supporting layers are kept separate: NCRB 2024 monthly data as its own vintage, IMD-derived weather matched at state-year level, seven verified MoRTH 2024 supporting modules, Tamil Nadu district data, and a conditional 2014 to 2017 historical candidate that I never merged into the benchmark.

KEY POINT: Benchmark plus separated supporting sources.

TRANSITION: How I verified all of this.

## SLIDE 8 — Data Validation

TIME: ~20 seconds

WHAT TO SAY: From this analysis, the benchmark reconciles with zero mismatches against published totals. The historical candidate matched 12 out of 12 checks, NCRB sections reconciled exactly, and Tamil Nadu district sums matched the benchmark. Weather gave 236 usable matched records with 18 excluded, never filled with zeros.

KEY POINT: Provenance and reconciliation.

TRANSITION: Now the findings, starting at India level.

## SLIDE 9 — India-Level Trends

TIME: ~25 seconds

WHAT TO SAY: Accidents rose from 470,403 to 487,707, about 3.7 percent, while fatalities rose faster, from 157,593 to 177,175, about 12.4 percent. The fatality ratio rose from 33.50 to 36.33 per 100 accidents. 2020 showed a major dip followed by recovery. However, I have to interpret this carefully: the fitted OLS slopes are not statistically significant, so I describe the pattern as fluctuating rather than a proven trend.

KEY POINT: Severity rising faster than counts; trends not significant.

TRANSITION: How this varies geographically.

## SLIDE 10 — Geographical Analysis

TIME: ~15 seconds

WHAT TO SAY: The six-zone framework reveals real geographical heterogeneity across states and UTs. But since I have no exposure denominator like vehicle-kilometres, I report recorded counts and never label any state as most dangerous or safest.

KEY POINT: Heterogeneity without risk ranking.

TRANSITION: The formal zone test.

## SLIDE 11 — Zone Analysis

TIME: ~20 seconds

WHAT TO SAY: Using the Friedman test, which is appropriate because zones are observed repeatedly across years, I got chi-square 25.29 with p equal to 3.0e-4 and Kendall's W of 0.72. This indicates statistically detectable repeated-year zone differences. This is a statistical association, not a causal conclusion, and I do not rank zones.

KEY POINT: Zone differences detectable, descriptive only.

TRANSITION: State-level trends next.

## SLIDE 12 — State Analysis

TIME: ~20 seconds

WHAT TO SAY: For accidents, 17 states had positive slopes, 15 negative, 6 near-zero. For fatalities, 26 positive, 10 negative, 2 near-zero. But only a minority of these state trends were statistically detectable, so most state slopes should be read as descriptive, not proven increases or decreases.

KEY POINT: Mostly descriptive state trends.

TRANSITION: Temporal structure beyond years.

## SLIDE 13 — Temporal Analysis

TIME: ~15 seconds

WHAT TO SAY: The primary benchmark is annual, so hour and day patterns are simply not available there. The limitation here is temporal granularity, which is why monthly analysis uses a separate dataset.

KEY POINT: Annual benchmark limits.

TRANSITION: That separate monthly source.

## SLIDE 14 — Seasonal/NCRB

TIME: ~20 seconds

WHAT TO SAY: Using NCRB 2024 monthly data, clearly a separate statistical vintage from MoRTH, May had the largest share at 8.84 percent and July the smallest at 7.46 percent, with chi-square 1276. This is a monthly distribution result. I use calendar quarters descriptively and never claim a single India-wide climate season or call any month universally dangerous.

KEY POINT: Monthly pattern, vintage-labeled.

TRANSITION: Environmental associations.

## SLIDE 15 — Weather Analysis

TIME: ~30 seconds

WHAT TO SAY: With 236 matched state-years, rainfall correlated at minus 0.234 with accidents and minus 0.376 with fatalities; mean maximum temperature at plus 0.452 and plus 0.498; mean minimum temperature at approximately plus 0.366 and plus 0.340. This is an association, not a causal conclusion, and it may partly reflect geographic and scale differences between states. Weather versus severity showed no statistically detectable association, which I report honestly.

KEY POINT: Associations with confounding caveat.

TRANSITION: Severity patterns from supporting data.

## SLIDE 16 — Severity Analysis

TIME: ~15 seconds

WHAT TO SAY: The India fatality ratio rose from 33.50 to 36.33 per 100 accidents. I treat this as a case-fatality-style measure, never a population death rate, since no population denominator is integrated here.

KEY POINT: Severity rising; correct denominator language.

TRANSITION: Reported causes next.

## SLIDE 17 — Violations/Causes

TIME: ~20 seconds

WHAT TO SAY: In 2024, the reported overspeeding category accounted for 70.7 percent of reported accidents and 70.3 percent of reported fatalities. The important point here is the wording: reported violation category, not proven cause. These records do not establish causation.

KEY POINT: Reported shares, not causes.

TRANSITION: Collision and road-user patterns.

## SLIDE 18 — Collision/Road-User

TIME: ~20 seconds

WHAT TO SAY: Hit from Back was the most frequent recorded collision category, while Hit-and-Run had the highest observed fatality ratio at approximately 0.50. For road users, two-wheelers made up 46.2 percent of 2024 deaths and pedestrians 20.6 percent. These are shares of recorded deaths, not exposure-normalized risk estimates.

KEY POINT: Shares, never risk claims.

TRANSITION: Licence and safety-device records.

## SLIDE 19 — Licence/Safety

TIME: ~15 seconds

WHAT TO SAY: Valid licence holders accounted for 68.2 percent of reported accidents. No-helmet deaths were 54,122 and no-seatbelt deaths 14,466. These are observed toll counts, not effectiveness estimates, so I make no claim that the analysis proves helmet or seatbelt effectiveness.

KEY POINT: Toll counts, correct interpretation.

TRANSITION: The statistical backbone.

## SLIDE 20 — Statistical Findings

TIME: ~20 seconds

WHAT TO SAY: I used OLS trends with confidence intervals, Pearson and Spearman correlations, chi-square, the Friedman test, effect sizes, and Benjamini-Hochberg FDR correction across test families. That is why I used the baseline and corrections throughout: every test is reported, significant or not.

KEY POINT: Validated, correction-aware statistics.

TRANSITION: How prediction was tested.

## SLIDE 21 — ML Methodology

TIME: ~25 seconds

WHAT TO SAY: The modeling unit is state-year. I trained on 2019 to 2022 with 141 observations and tested on 2023 to 2024 with 72 observations, using lag-only features so no target-year information leaks. I tested linear regression, ridge, random forest, gradient boosting, and KNN regression against a naive persistence baseline that simply predicts last year's value.

KEY POINT: Time-aware, leakage-audited design.

TRANSITION: The headline result.

## SLIDE 22 — ML Results

TIME: ~30 seconds

WHAT TO SAY: The naive baseline gave an RMSE of 1038.6 for accidents and 286.3 for fatalities, and it outperformed all trained models on the held-out test set. This result is important because it is a legitimate finding: the available aggregate features were insufficient for reliable held-out prediction. Gradient boosting reached a training R-squared near 1.0 but tested worse, which is textbook overfitting. I present this as an honest null, not a failure to hide.

KEY POINT: Honest null result.

TRANSITION: Unsupervised exploration next.

## SLIDE 23 — K-Means

TIME: ~20 seconds

WHAT TO SAY: K-means, which is unsupervised, on standardized state profiles selected K equal to 2 with silhouette 0.356, giving clusters of 17 and 6 states. These are descriptive profile groups only. I never label them high-risk or safe, because no exposure denominator exists.

KEY POINT: Descriptive typology.

TRANSITION: What remains unavailable.

## SLIDE 24 — Limitations + Contributions

TIME: ~25 seconds

WHAT TO SAY: The binding gaps are accident-level microdata, coordinates, national district coverage, vehicle stock, AADT and vehicle-kilometres, driver and vehicle detail, limited weather variables, and missing 2023-24 state injuries. Against that, the contributions are a validated benchmark, harmonization, weather integration, association analysis, a verified supporting base, separate-vintage monthly analysis, district validation, honest predictive benchmarking, provenance, and a reusable platform.

KEY POINT: Limits first, then earned contributions.

TRANSITION: To close.

## SLIDE 25 — Conclusion + Vision

TIME: ~15 seconds

WHAT TO SAY: In one line: the project establishes a reproducible multi-level framework, finds real geographical, temporal, environmental and severity patterns, benchmarks prediction honestly, and provides a platform ready for future accident-level, exposure and GIS data. Thank you, and I welcome your questions.

KEY POINT: Confident honest close.
