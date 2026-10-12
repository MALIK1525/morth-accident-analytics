# Viva Questions and Answers

## SECTION A — PROJECT BASICS

### 1. What is your project?
QUESTION: What is your project?
ANSWER: A multi-level data-driven analysis of road traffic accidents in India, examining how accident occurrence and severity vary across geography, time, season, environment and reported factors, using verified official data from 2018 to 2024.
KEY POINT: Multi-level observational analysis of official data.
IF PROFESSOR PUSHES FURTHER: The short title is "Data-Driven Road Traffic Accident Analysis in India".

### 2. Why did you choose this topic?
QUESTION: Why did you choose this topic?
ANSWER: Road accidents are a major public-safety problem, and aggregate national numbers alone do not explain geographical, temporal, environmental and severity patterns. A validated framework was needed.
KEY POINT: Totals are not enough.
IF PROFESSOR PUSHES FURTHER: 2024 alone had 487,707 accidents and 177,175 deaths.

### 3. What problem are you solving?
QUESTION: What problem are you solving?
ANSWER: The lack of a validated, reproducible multi-level analytical framework that separates incompatible data vintages and documents exposure and microdata limits honestly.
KEY POINT: Framework plus honest limits.
IF PROFESSOR PUSHES FURTHER: Different official datasets use different definitions, so naive merging is unsafe.

### 4. What is your research question?
QUESTION: What is your research question?
ANSWER: How do geographical, temporal, seasonal, environmental, roadway, vehicle and other available factors associate with the occurrence and severity of road traffic accidents across India?
KEY POINT: Observational, association language.
IF PROFESSOR PUSHES FURTHER: Association, not causation, by design.

### 5. What are your objectives?
QUESTION: What are your objectives?
ANSWER: Thirteen objectives covering India trends, state/zone patterns, temporal and monthly structure, weather associations, violation/collision/road-user analysis, statistical validation, predictive benchmarking, clustering, limitations, and a reusable framework.
KEY POINT: Full pipeline from description to prediction testing.
IF PROFESSOR PUSHES FURTHER: Listed in full in the report Chapter 1.

### 6. What is novel about your project?
QUESTION: What is novel about your project?
ANSWER: I do not claim breakthrough novelty. The contribution is a validated multi-year benchmark combined with vintage separation, weather integration, honest predictive benchmarking, and a reusable platform with full provenance.
KEY POINT: Bounded, honest contribution.
IF PROFESSOR PUSHES FURTHER: No unsupported novelty claims are made anywhere.

### 7. What is your main contribution?
QUESTION: What is your main contribution?
ANSWER: A reproducible analytical framework over 254 verified state-years, with cross-factor associations, an honest ML null result, and a live analytics platform for future data.
KEY POINT: Framework plus platform.
IF PROFESSOR PUSHES FURTHER: Ten contributions are listed in the report.

## SECTION B — DATA

### 8. What is MoRTH?
QUESTION: What is MoRTH?
ANSWER: The Ministry of Road Transport and Highways, Government of India, which publishes the annual "Road Accidents in India" report. It is my primary data source.
KEY POINT: Primary official source.
IF PROFESSOR PUSHES FURTHER: Reports are published annually with state-wise accident, fatality and injury tables.

### 9. Why did you use MoRTH?
QUESTION: Why did you use MoRTH?
ANSWER: It is the authoritative national source for state-wise road accident statistics with consistent annual reporting, suitable for a 2018-2024 panel.
KEY POINT: Authoritative and panel-compatible.
IF PROFESSOR PUSHES FURTHER: Supporting modules also come from MoRTH 2024 tables.

### 10. What years did you analyze?
QUESTION: What years did you analyze?
ANSWER: Primary benchmark 2018 to 2024. Historical 2014-2017 kept as a separate conditional candidate. NCRB monthly is 2024 only.
KEY POINT: Three vintages, never merged.
IF PROFESSOR PUSHES FURTHER: Each vintage is labeled everywhere it appears.

### 11. What is the unit of analysis?
QUESTION: What is the unit of analysis?
ANSWER: State-Year for the primary benchmark and ML modeling; India-Year for national trends; Zone-Year for zonal analysis.
KEY POINT: State-Year is primary.
IF PROFESSOR PUSHES FURTHER: 254 state-year observations.

### 12. How many state-years?
QUESTION: How many state-years?
ANSWER: 254 state-year observations.
KEY POINT: Locked count.
IF PROFESSOR PUSHES FURTHER: Across 38 reporting entities over 7 years.

### 13. How many reporting entities?
QUESTION: How many reporting entities?
ANSWER: 38 reporting entities (states and UTs as reported, including legacy splits).
KEY POINT: Locked count.
IF PROFESSOR PUSHES FURTHER: Legacy DNH/Diu splits retained and excluded from totals where appropriate.

### 14. Why 2018-2024?
QUESTION: Why 2018-2024?
ANSWER: These are the years with a verified, reconciled MoRTH state panel at zero benchmark mismatches, with consistent geography handlable through documented harmonization.
KEY POINT: Verifiability drove the window.
IF PROFESSOR PUSHES FURTHER: 2014-2017 exists but under a different vintage with boundary issues.

### 15. What are the major limitations of the dataset?
QUESTION: What are the major limitations of the dataset?
ANSWER: No accident-level microdata or coordinates, no vehicle stock or AADT exposure, missing 2023-24 state injuries, limited weather variables, annual-only MoRTH granularity.
KEY POINT: Limits stated upfront.
IF PROFESSOR PUSHES FURTHER: Full limitations matrix is in the report.

### 16. Why did you not use accident-level data?
QUESTION: Why did you not use accident-level data?
ANSWER: It was not publicly available in verified form; eDAR microdata is access-restricted. I analyzed what was verifiable instead of fabricating it.
KEY POINT: Availability, not choice.
IF PROFESSOR PUSHES FURTHER: The platform is designed to accept such data when available.

### 17. Why are some variables unavailable?
QUESTION: Why are some variables unavailable?
ANSWER: The MoRTH state panel publishes counts by state and year only; variables like humidity, driver age, or coordinates are simply not in these tables.
KEY POINT: Source-bound.
IF PROFESSOR PUSHES FURTHER: Each unavailable parameter is listed with reason in the availability matrix.

### 18. How did you handle missing data?
QUESTION: How did you handle missing data?
ANSWER: Preserved as missing, never filled with zeros. Weather exclusions kept as 18 excluded records; 2023-24 state injuries left unavailable.
KEY POINT: Never impute silently.
IF PROFESSOR PUSHES FURTHER: Absence of evidence is never treated as zero.

### 19. Why are injuries unavailable for some years?
QUESTION: Why are injuries unavailable for some years?
ANSWER: The benchmark source does not publish state-level injury values for 2023-2024; only India-level injured totals exist there. I did not derive them.
KEY POINT: Source gap, honestly kept.
IF PROFESSOR PUSHES FURTHER: India-level 2024 injured is 471,441.

### 20. Why should historical 2014-2017 data remain separate?
QUESTION: Why should historical 2014-2017 data remain separate?
ANSWER: Different report vintage with boundary differences (J&K, DNH/Diu, Telangana) and its own provenance. Merging would silently mix vintages.
KEY POINT: Vintage separation.
IF PROFESSOR PUSHES FURTHER: It is analyzed as a conditional sensitivity candidate only.

## SECTION C — METHODOLOGY

### 21. Explain your overall methodology.
QUESTION: Explain your overall methodology.
ANSWER: Discover official data, verify provenance, preserve raw files, audit quality, harmonize geography and time, analyze India/zone/state levels, integrate weather, analyze supporting factors, validate statistically, benchmark ML, cluster descriptively, then synthesize with limits.
KEY POINT: Staged, reproducible pipeline.
IF PROFESSOR PUSHES FURTHER: Flowchart is in the report.

### 22. Why did you use India, zones, states?
QUESTION: Why did you use India, zones, states?
ANSWER: National totals hide regional heterogeneity; the three levels let me describe country trends, regional differences, and entity-level slopes without conflating them.
KEY POINT: Each level answers a different question.
IF PROFESSOR PUSHES FURTHER: Six zones per the approved mapping.

### 23. Why six zones?
QUESTION: Why six zones?
ANSWER: The project's approved mapping groups states into North, South, East, West, Central and Northeast for regional comparison.
KEY POINT: Pre-approved grouping.
IF PROFESSOR PUSHES FURTHER: Mapping is documented in the data pipeline.

### 24. What geographical analysis did you perform?
QUESTION: What geographical analysis did you perform?
ANSWER: State trend slopes with confidence intervals, zone-year totals and shares, Friedman test for repeated-year zone differences, and state-year heatmaps. No rankings.
KEY POINT: Descriptive geography.
IF PROFESSOR PUSHES FURTHER: Counts are never called risk.

### 25. What temporal analysis did you perform?
QUESTION: What temporal analysis did you perform?
ANSWER: Year-over-year change, OLS descriptive slopes, 2020 dip-and-recovery description, time-to-threshold tables, plus separate NCRB 2024 monthly shares and month-over-month change.
KEY POINT: Annual plus separate monthly.
IF PROFESSOR PUSHES FURTHER: Hour/day unavailable in the benchmark.

### 26. What seasonal analysis did you perform?
QUESTION: What seasonal analysis did you perform?
ANSWER: Calendar-quarter grouping of NCRB 2024 monthly data, explicitly not climate seasons, since one season definition cannot fit all of India.
KEY POINT: Calendar grouping, honestly labeled.
IF PROFESSOR PUSHES FURTHER: May 8.84%, July 7.46%.

### 27. What environmental analysis did you perform?
QUESTION: What environmental analysis did you perform?
ANSWER: State-year correlations of rainfall, mean Tmax and mean Tmin with accidents and fatalities, plus weather-versus-severity checks which showed no detectable association.
KEY POINT: Three variables only.
IF PROFESSOR PUSHES FURTHER: Humidity, fog, wind were unavailable.

### 28. What supporting analyses did you perform?
QUESTION: What supporting analyses did you perform?
ANSWER: 2024 modules for violations, collisions, road users, licence, safety devices, cities, plus the victim matrix, each with shares and fatality ratios where denominators allow.
KEY POINT: Separate source layers.
IF PROFESSOR PUSHES FURTHER: RD-01/SV-01 stayed unavailable.

### 29. What statistical tests did you use?
QUESTION: What statistical tests did you use?
ANSWER: OLS trends, Pearson and Spearman correlations, chi-square goodness-of-fit, Friedman test, confidence intervals, effect sizes, and Benjamini-Hochberg FDR correction.
KEY POINT: Named, justified tests.
IF PROFESSOR PUSHES FURTHER: Assumption audits are documented per method.

### 30. Why did you use Friedman test?
QUESTION: Why did you use Friedman test?
ANSWER: Because zones are observed repeatedly across the same years, so an independent-samples test would ignore the repeated structure. Friedman handles ranked blocks.
KEY POINT: Repeated-years design.
IF PROFESSOR PUSHES FURTHER: Result chi-square 25.29, p=3.0e-4, Kendall W 0.72.

### 31. What does Kendall's W mean?
QUESTION: What does Kendall's W mean?
ANSWER: An effect-size measure for the Friedman test between 0 and 1; 0.72 indicates strong agreement among yearly blocks about zone ordering, descriptively.
KEY POINT: Effect size, not ranking.
IF PROFESSOR PUSHES FURTHER: It does not say which zone is best or worst.

### 32. What does a correlation coefficient mean?
QUESTION: What does a correlation coefficient mean?
ANSWER: The strength and direction of linear association between two variables, from -1 to +1. My rainfall-accident r of -0.234 is a weak negative association.
KEY POINT: Association strength.
IF PROFESSOR PUSHES FURTHER: Spearman rho captures monotonic rather than strictly linear association.

### 33. Why does correlation not prove causation?
QUESTION: Why does correlation not prove causation?
ANSWER: Because a third factor, like state size or exposure, can drive both variables, and observational data cannot rule that out. My weather correlations may partly reflect scale differences.
KEY POINT: Confounding.
IF PROFESSOR PUSHES FURTHER: That is why every weather statement says association only.

### 34. Why did you use OLS?
QUESTION: Why did you use OLS?
ANSWER: To summarize the descriptive linear direction of each series over the observed years, with R-squared, p-values and confidence intervals reported.
KEY POINT: Descriptive summary.
IF PROFESSOR PUSHES FURTHER: A slope is not a claim that year causes accidents.

### 35. What does p=.44 mean?
QUESTION: What does p=.44 mean?
ANSWER: The accident slope of +6,725 per year is not statistically significant; the data are consistent with no linear trend over just seven years.
KEY POINT: Not significant.
IF PROFESSOR PUSHES FURTHER: I describe the series as fluctuating.

### 36. What does p=.09 mean?
QUESTION: What does p=.09 mean?
ANSWER: The fatality slope of +4,167 per year is also not significant at alpha 0.05, though closer; I still do not call it a proven trend.
KEY POINT: Not significant.
IF PROFESSOR PUSHES FURTHER: Exact p-values are reported, significant or not.

## SECTION D — WEATHER

### 37. What weather variables were used?
QUESTION: What weather variables were used?
ANSWER: Annual rainfall, annual mean maximum temperature, and annual mean minimum temperature, from IMD-derived state-year integration.
KEY POINT: Three variables.
IF PROFESSOR PUSHES FURTHER: 236 usable records, 18 excluded.

### 38. Why rainfall?
QUESTION: Why rainfall?
ANSWER: It was one of the three verified IMD variables available at state-year resolution with documented provenance.
KEY POINT: Availability plus provenance.
IF PROFESSOR PUSHES FURTHER: r = -0.234 accidents, -0.376 fatalities.

### 39. Why Tmax and Tmin?
QUESTION: Why Tmax and Tmin?
ANSWER: Same reason: verified, documented, joinable at state-year level. Tmax r = +0.452/+0.498, Tmin approximately +0.366/+0.340.
KEY POINT: Verified and joinable.
IF PROFESSOR PUSHES FURTHER: Severity correlations were null.

### 40. What does r = -.376 mean?
QUESTION: What does r = -.376 mean?
ANSWER: A moderate negative linear association between rainfall and fatalities across matched state-years: higher-rainfall observations tend to have fewer recorded fatalities, descriptively.
KEY POINT: Moderate negative association.
IF PROFESSOR PUSHES FURTHER: Not proof that rain prevents deaths.

### 41. What does r = +.498 mean?
QUESTION: What does r = +.498 mean?
ANSWER: A moderate positive linear association between mean maximum temperature and fatalities. Higher-Tmax observations tend to have more recorded fatalities.
KEY POINT: Moderate positive association.
IF PROFESSOR PUSHES FURTHER: Scale confounding may contribute.

### 42. Can you conclude that temperature causes accidents?
QUESTION: Can you conclude that temperature causes accidents?
ANSWER: No. These are observational associations that may reflect geography, exposure, and scale differences. I state association only throughout.
KEY POINT: Firm no.
IF PROFESSOR PUSHES FURTHER: No causal design was available.

### 43. Why were 18 records excluded?
QUESTION: Why were 18 records excluded?
ANSWER: Unresolved or unavailable spatial coverage for Lakshadweep, Andaman and Nicobar Islands, and legacy DNH/Diu rows. Kept as null, never zero.
KEY POINT: Coverage gaps, honestly kept.
IF PROFESSOR PUSHES FURTHER: Replacing them with zero would fabricate data.

### 44. What weather variables were unavailable?
QUESTION: What weather variables were unavailable?
ANSWER: Humidity, visibility, fog, and wind, plus lighting conditions. IMD gridded climatology covers temperature and rainfall only.
KEY POINT: Named gaps.
IF PROFESSOR PUSHES FURTHER: Station-data access was restricted.

### 45. What would improve this analysis?
QUESTION: What would improve this analysis?
ANSWER: State-month weather matched to monthly accident data, plus station-level humidity and visibility, with exposure denominators.
KEY POINT: Concrete next data.
IF PROFESSOR PUSHES FURTHER: Listed in future work.

## SECTION E — CONTRIBUTING FACTORS

### 46. What does the overspeeding percentage represent?
QUESTION: What does the overspeeding percentage represent?
ANSWER: The share of reported accidents and fatalities recorded under the overspeeding violation category in 2024: 70.7% and 70.3%.
KEY POINT: Recorded share.
IF PROFESSOR PUSHES FURTHER: Category label, not verified mechanism.

### 47. Can you say overspeeding caused accidents?
QUESTION: Can you say overspeeding caused accidents?
ANSWER: No. I say "reported overspeeding category" because the table records classifications, not proven causal mechanisms.
KEY POINT: Firm no.
IF PROFESSOR PUSHES FURTHER: Causal inference needs a different design.

### 48. What did the collision analysis show?
QUESTION: What did the collision analysis show?
ANSWER: Nine collision types over two years; Hit from Back most frequent with 113,907 accidents in 2024; totals reconcile with published figures.
KEY POINT: Frequency description.
IF PROFESSOR PUSHES FURTHER: Counts and shares only.

### 49. Why is Hit-and-Run important?
QUESTION: Why is Hit-and-Run important?
ANSWER: It had the highest observed fatality ratio at approximately 0.50, a case-fatality-style measure worth noting descriptively.
KEY POINT: Severity signal, not risk claim.
IF PROFESSOR PUSHES FURTHER: Not called most dangerous without exposure data.

### 50. What did the road-user analysis show?
QUESTION: What did the road-user analysis show?
ANSWER: In 2024, two-wheelers were 46.2% of recorded deaths and pedestrians 20.6%, across nine road-user modes.
KEY POINT: Death shares.
IF PROFESSOR PUSHES FURTHER: Largest count is explicitly not called highest risk.

### 51. Why can't you call two-wheelers the highest-risk users?
QUESTION: Why can't you call two-wheelers the highest-risk users?
ANSWER: Because risk needs an exposure denominator like vehicle-kilometres per mode, which is unavailable. Shares of deaths are not risk.
KEY POINT: No denominator, no risk claim.
IF PROFESSOR PUSHES FURTHER: This distinction is stated in every road-user table.

### 52. What does the licence result mean?
QUESTION: What does the licence result mean?
ANSWER: Valid-licence holders accounted for 68.2% of reported 2024 accidents, a share of reported accidents, not of all drivers.
KEY POINT: Share of reports.
IF PROFESSOR PUSHES FURTHER: Sums reconcile with published totals.

### 53. What do the helmet/seatbelt numbers mean?
QUESTION: What do the helmet/seatbelt numbers mean?
ANSWER: Observed toll counts in the non-use categories: 54,122 no-helmet deaths and 14,466 no-seatbelt deaths in 2024.
KEY POINT: Toll, not effectiveness.
IF PROFESSOR PUSHES FURTHER: 2024 only.

### 54. Can you estimate safety-device effectiveness from these counts?
QUESTION: Can you estimate safety-device effectiveness from these counts?
ANSWER: No. Effectiveness needs usage rates among all road users, which these tables do not provide.
KEY POINT: Firm no.
IF PROFESSOR PUSHES FURTHER: I state this limit in the report.

## SECTION F — MACHINE LEARNING

### 55. Why did you use machine learning?
QUESTION: Why did you use machine learning?
ANSWER: To test whether state-year counts can be predicted better than a naive baseline using available aggregate features, as the professor required.
KEY POINT: Benchmark test, not product.
IF PROFESSOR PUSHES FURTHER: The honest null is the result.

### 56. What exactly were you predicting?
QUESTION: What exactly were you predicting?
ANSWER: Next-year state accident counts and fatality counts. Injuries and fatality ratio were deferred for missingness and leakage reasons.
KEY POINT: Two count targets.
IF PROFESSOR PUSHES FURTHER: Documented in the target audit.

### 57. Why State-Year as the modeling unit?
QUESTION: Why State-Year as the modeling unit?
ANSWER: It is the finest verified granularity with 213 usable rows after lags, keeping vintages separate and leakage auditable.
KEY POINT: Finest verifiable grain.
IF PROFESSOR PUSHES FURTHER: Mixing granularities would break the design.

### 58. Why train on 2019-2022?
QUESTION: Why train on 2019-2022?
ANSWER: Chronological training block with 141 rows after lag construction; 2018 drops out because no benchmark-compatible 2017 lag exists.
KEY POINT: Chronology plus lag logic.
IF PROFESSOR PUSHES FURTHER: No 2017 values were fabricated.

### 59. Why test on 2023-2024?
QUESTION: Why test on 2023-2024?
ANSWER: The most recent held-out years, 72 rows, never used for tuning, giving a true forward-looking test.
KEY POINT: Unseen years.
IF PROFESSOR PUSHES FURTHER: Hyperparameters were fixed on rolling folds inside training years.

### 60. Why did you use a time-based split?
QUESTION: Why did you use a time-based split?
ANSWER: Random splits would leak future information into training and overstate performance on time-ordered data.
KEY POINT: No future leakage.
IF PROFESSOR PUSHES FURTHER: Rolling-origin folds were used for tuning.

### 61. What models did you test?
QUESTION: What models did you test?
ANSWER: Linear Regression, Ridge, Random Forest, Gradient Boosting, and KNN Regression, all against naive persistence.
KEY POINT: Five supervised models.
IF PROFESSOR PUSHES FURTHER: Each had a methodological reason, not padding.

### 62-66. Why each model?
QUESTION: Why each model?
ANSWER: Linear/Ridge for interpretable baselines; Random Forest and Gradient Boosting for nonlinear interactions; KNN Regression as a supervised similarity-based comparator.
KEY POINT: Coverage of model families.
IF PROFESSOR PUSHES FURTHER: KNN is supervised; K-means is the unsupervised one.

### 67. What is the baseline?
QUESTION: What is the baseline?
ANSWER: Naive persistence: predict this year with last year's actual value. Accidents RMSE 1038.6, fatalities RMSE 286.3.
KEY POINT: Simple, strong comparator.
IF PROFESSOR PUSHES FURTHER: Every trained model lost to it.

### 68. Why is the naive baseline important?
QUESTION: Why is the naive baseline important?
ANSWER: Without it, any model metric looks impressive in isolation. The baseline proves whether learning adds value; here it did not.
KEY POINT: Honesty device.
IF PROFESSOR PUSHES FURTHER: Omitting it would be misleading.

### 69. What does RMSE mean?
QUESTION: What does RMSE mean?
ANSWER: Root mean squared error: average prediction error penalizing large errors more, in the same units as the target.
KEY POINT: Error magnitude.
IF PROFESSOR PUSHES FURTHER: Accidents baseline 1038.6.

### 70. What does MAE mean?
QUESTION: What does MAE mean?
ANSWER: Mean absolute error: average absolute miss size. Baseline 540.7 accidents, 166.0 fatalities.
KEY POINT: Average miss.
IF PROFESSOR PUSHES FURTHER: Reported alongside RMSE and R-squared.

### 71. Why were your models worse than the baseline?
QUESTION: Why were your models worse than the baseline?
ANSWER: Year-to-year persistence dominates this panel, and 141 training rows with lag-only aggregate features cannot capture the remaining variation. The evaluation exposed this honestly.
KEY POINT: Persistence plus small panel.
IF PROFESSOR PUSHES FURTHER: Scale confounding also concentrates error in large states.

### 72. Does this mean machine learning is useless?
QUESTION: Does this mean machine learning is useless?
ANSWER: No. It means these features at this aggregation cannot beat persistence. The null guides future data collection toward exposure, monthly, and microdata features.
KEY POINT: Useful negative result.
IF PROFESSOR PUSHES FURTHER: Reported transparently instead of hidden.

### 73. What does train R²≈1.0 for Gradient Boosting indicate?
QUESTION: What does train R²≈1.0 for Gradient Boosting indicate?
ANSWER: Overfitting: memorized training rows but generalized worse than baseline on unseen years.
KEY POINT: Overfitting evidence.
IF PROFESSOR PUSHES FURTHER: That is why test metrics decide, never training metrics.

### 74. What is overfitting?
QUESTION: What is overfitting?
ANSWER: When a model memorizes training noise instead of general patterns, so training performance looks perfect while test performance collapses.
KEY POINT: Memorize versus generalize.
IF PROFESSOR PUSHES FURTHER: GBR is my project example.

### 75. What would you need to improve prediction?
QUESTION: What would you need to improve prediction?
ANSWER: Vehicle stock, traffic volume, monthly series, weather at finer resolution, and accident-level features, all currently unavailable.
KEY POINT: Named data, not new algorithms.
IF PROFESSOR PUSHES FURTHER: More models on the same features would not fix it.

### 76. Would you deploy this model?
QUESTION: Would you deploy this model?
ANSWER: No. It loses to last year's value on unseen years, so deployment as a prediction system would be irresponsible. The platform is an analytics system.
KEY POINT: Firm no.
IF PROFESSOR PUSHES FURTHER: Application vision states this explicitly.

## SECTION G — CLUSTERING

### 77. What is K-means?
QUESTION: What is K-means?
ANSWER: An unsupervised algorithm grouping states into K clusters by similarity across standardized profile features, with no labels used.
KEY POINT: Unsupervised grouping.
IF PROFESSOR PUSHES FURTHER: Distinct from KNN Regression, which is supervised.

### 78. Is K-means supervised or unsupervised?
QUESTION: Is K-means supervised or unsupervised?
ANSWER: Unsupervised. It finds structure without target labels.
KEY POINT: Unsupervised.
IF PROFESSOR PUSHES FURTHER: KNN in my project is supervised regression.

### 79. Why did you use K=2?
QUESTION: Why did you use K=2?
ANSWER: It had the maximum silhouette score, 0.356, across K=2 to 6, with inertia, Calinski-Harabasz and Davies-Bouldin reported for all candidates.
KEY POINT: Diagnostic-selected.
IF PROFESSOR PUSHES FURTHER: Not claimed as the objectively true K.

### 80. What does silhouette=.356 mean?
QUESTION: What does silhouette=.356 mean?
ANSWER: Modest cluster separation: positive but not strong, so clusters are descriptive tendencies, not sharp natural kinds.
KEY POINT: Modest separation.
IF PROFESSOR PUSHES FURTHER: Stability checked across seeds with ARI.

### 81. What do the clusters represent?
QUESTION: What do the clusters represent?
ANSWER: A higher recorded-accident-count profile with 6 states and a lower-count profile with 17 states, over standardized means, ratios, slopes and weather.
KEY POINT: Count profiles.
IF PROFESSOR PUSHES FURTHER: Features listed in the cluster audit.

### 82. Can you call them high-risk and low-risk?
QUESTION: Can you call them high-risk and low-risk?
ANSWER: No. Risk requires exposure normalization, which is unavailable. They are descriptive profile labels only.
KEY POINT: Firm no.
IF PROFESSOR PUSHES FURTHER: This wording is enforced in every cluster file.

### 83. What is the purpose of clustering in your project?
QUESTION: What is the purpose of clustering in your project?
ANSWER: Exploratory typology: showing which states share similar accident-profile characteristics to guide future stratified analysis.
KEY POINT: Exploration, not decision.
IF PROFESSOR PUSHES FURTHER: PCA scatter supports visualization only.

## SECTION H — APPLICATION

### 84. What is your application?
QUESTION: What is your application?
ANSWER: A Flask analytics platform with the verified benchmark dashboard, weather, statistics, ML, audit, registry, reports, and an upload workspace for user datasets.
KEY POINT: Analytics platform.
IF PROFESSOR PUSHES FURTHER: Live at the documented Render URL.

### 85. What does the dashboard provide?
QUESTION: What does the dashboard provide?
ANSWER: G1-G10 visualizations, filters, KPIs, statistics, weather, supporting modules, audit trails, and exports, all from verified data.
KEY POINT: Full analytical surface.
IF PROFESSOR PUSHES FURTHER: Demo script covers the click path.

### 86. What are G1-G10?
QUESTION: What are G1-G10?
ANSWER: The ten core graph families: India accidents, fatalities, injuries, fatality ratio, zone comparison, zone-year, state 2024, state-year heatmap, state trends, and slope distribution.
KEY POINT: Core visuals.
IF PROFESSOR PUSHES FURTHER: All verified working.

### 87. How does the application help a researcher?
QUESTION: How does the application help a researcher?
ANSWER: By giving validated data, documented methods, reproducible tables, visualizations, and provenance in one place instead of scattered files.
KEY POINT: Reproducibility.
IF PROFESSOR PUSHES FURTHER: Plus honest unavailable-data handling.

### 88. What data can users upload?
QUESTION: What data can users upload?
ANSWER: CSV, XLSX, or JSON accident datasets, which are inspected, mapped, quality-checked, and analyzed separately from the benchmark.
KEY POINT: Three formats, separate mode.
IF PROFESSOR PUSHES FURTHER: Uploads never overwrite the benchmark.

### 89. What happens when data is unavailable?
QUESTION: What happens when data is unavailable?
ANSWER: The module shows an honest unavailable state with the expected source file, never a blank chart or fabricated values.
KEY POINT: Honest empty states.
IF PROFESSOR PUSHES FURTHER: Five states per chart: loading, success, no-data, error, unavailable-source.

### 90. How does the application prevent fabricated data?
QUESTION: How does the application prevent fabricated data?
ANSWER: Uploads are validated, benchmark and upload modes are separated, missing values stay null, and every supporting dataset carries provenance.
KEY POINT: Separation plus provenance.
IF PROFESSOR PUSHES FURTHER: 54/54 upload-era tests enforced this.

### 91. What is the purpose of the audit/registry system?
QUESTION: What is the purpose of the audit/registry system?
ANSWER: To show dataset status, variable definitions, availability, and reconciliation so any number can be traced to its source.
KEY POINT: Traceability.
IF PROFESSOR PUSHES FURTHER: 168 registry entries.

### 92. What is the difference between benchmark mode and upload workspace?
QUESTION: What is the difference between benchmark mode and upload workspace?
ANSWER: Benchmark mode shows verified MoRTH research data; the upload workspace analyzes a separate user file with its own inspection, mapping, and readiness panels.
KEY POINT: Mode A versus Mode B.
IF PROFESSOR PUSHES FURTHER: Switching never destroys either dataset.

## SECTION I — LIMITATIONS

### 93. What is the biggest limitation?
QUESTION: What is the biggest limitation?
ANSWER: The absence of a state-wise traffic exposure denominator, which blocks all risk normalization and limits ML features.
KEY POINT: Exposure gap.
IF PROFESSOR PUSHES FURTHER: Vehicle stock, AADT, vehicle-km all unavailable.

### 94. What is the biggest data gap?
QUESTION: What is the biggest data gap?
ANSWER: Accident-level microdata with coordinates, which would enable hotspot, severity, and time-of-day analysis.
KEY POINT: Microdata gap.
IF PROFESSOR PUSHES FURTHER: eDAR access is restricted.

### 95. Why can't you calculate exposure-normalized risk?
QUESTION: Why can't you calculate exposure-normalized risk?
ANSWER: Because state vehicle stock, traffic volume, and vehicle-kilometres at compatible geography and years were never acquired in verified form.
KEY POINT: No denominator.
IF PROFESSOR PUSHES FURTHER: OGD acquisition was blocked; documented as discovered-not-acquired.

### 96. Why is accident-level geospatial analysis unavailable?
QUESTION: Why is accident-level geospatial analysis unavailable?
ANSWER: No verified coordinates or district panel exist nationally; only Tamil Nadu districts for three years were verified.
KEY POINT: No coordinates.
IF PROFESSOR PUSHES FURTHER: State aggregates cannot support hotspot claims.

### 97. What are the limitations of weather analysis?
QUESTION: What are the limitations of weather analysis?
ANSWER: Annual aggregation only, three variables, 18 exclusions, possible scale confounding, and no severity association detected.
KEY POINT: Resolution plus confounding.
IF PROFESSOR PUSHES FURTHER: Monthly matching would be the fix.

### 98. What are the limitations of ML?
QUESTION: What are the limitations of ML?
ANSWER: Small panel of 213 rows, persistence-dominated series, no exposure or monthly features, and overfitting on tree models.
KEY POINT: Data-bound, not tuning-bound.
IF PROFESSOR PUSHES FURTHER: Hence the honest null.

### 99. What would you do differently with better data?
QUESTION: What would you do differently with better data?
ANSWER: Add exposure-normalized targets, monthly and district granularity, richer weather, and accident-level severity modeling with proper validation.
KEY POINT: Named upgrades.
IF PROFESSOR PUSHES FURTHER: Future work lists ten priorities.

### 100. What is the biggest limitation you would tell a reviewer?
QUESTION: What is the biggest limitation you would tell a reviewer?
ANSWER: Recorded counts are not risk, associations are not causes, and the tested models cannot beat last year's value, so the work is a validated descriptive foundation, not a prediction product.
KEY POINT: Three-sentence honesty.
IF PROFESSOR PUSHES FURTHER: All three are stated in the abstract itself.

## SECTION J — FUTURE SCOPE

### 101. What would you do next?
QUESTION: What would you do next?
ANSWER: Pursue eDAR access, state vehicle stock, monthly MoRTH series, and GIS integration, in that priority order.
KEY POINT: Data first.
IF PROFESSOR PUSHES FURTHER: Then re-test prediction with real features.

### 102. What additional data would you collect?
QUESTION: What additional data would you collect?
ANSWER: Coordinates, multi-state districts, vehicle stock, AADT, vehicle-km, driver and vehicle traits, monthly series, denser weather.
KEY POINT: Ten-item list.
IF PROFESSOR PUSHES FURTHER: Documented in future work.

### 103-108. Short answers.
QUESTION: Coordinates, traffic volume, satellite data, deep learning, real-time system, government use?
ANSWER: Coordinates would enable hotspots if verified. Traffic volume would unlock risk rates. Satellite weather could enrich environment data. Deep learning on 213 rows would overfit worse, so no. Real-time operation needs live feeds not present. Government use is decision support, not automated decisions, given current limits.
KEY POINT: Each conditional on data.
IF PROFESSOR PUSHES FURTHER: Application vision states the staged path.

## SECTION K — DIFFICULT / TRAP QUESTIONS (25)

### K1. Your ML models lost to the baseline. Why is the project successful?
QUESTION: Your ML models performed worse than the baseline. Why should I consider the project successful?
ANSWER: Because the evaluation was rigorous and honest: it proved aggregate features cannot beat persistence here, which is itself publishable evidence guiding future data work. Hiding it would be misconduct.
KEY POINT: Null as finding.
IF PROFESSOR PUSHES FURTHER: The descriptive and statistical contributions stand independently.

### K2. Isn't your weather analysis just correlation?
QUESTION: Isn't your weather analysis just correlation?
ANSWER: Yes, and I say so everywhere: pooled Pearson and Spearman with FDR, interpreted as associations with scale-confounding caveats, never causes.
KEY POINT: Agreed, labeled.
IF PROFESSOR PUSHES FURTHER: Severity correlations were null and reported.

### K3. How do you know overspeeding is responsible?
QUESTION: How do you know overspeeding is actually responsible?
ANSWER: I don't claim responsibility. I report the recorded category share and use "reported violation category" wording throughout.
KEY POINT: Records, not mechanisms.
IF PROFESSOR PUSHES FURTHER: Causal design would need microdata.

### K4. Why didn't you use a better ML model?
QUESTION: Why didn't you use a better ML model?
ANSWER: Five families were tested; the binding constraint is features and N=213, not algorithm choice. More models on the same data would not fix that.
KEY POINT: Data-bound.
IF PROFESSOR PUSHES FURTHER: Tuning used proper rolling folds, not the test set.

### K5. Why didn't you use deep learning?
QUESTION: Why didn't you use deep learning?
ANSWER: Deep learning on 213 tabular rows would overfit severely; even gradient boosting already hit train R-squared near 1.0.
KEY POINT: Would worsen overfitting.
IF PROFESSOR PUSHES FURTHER: Documented in the ML plan.

### K6. Why trust government accident data?
QUESTION: Why should I trust government accident data?
ANSWER: I verified rather than trusted: reconciled every total, checked vintages, preserved provenance with hashes, and reported discrepancies like the 2019 vintage openly.
KEY POINT: Verified, not trusted.
IF PROFESSOR PUSHES FURTHER: Zero benchmark mismatches.

### K7. Why did you exclude records?
QUESTION: Why did you exclude some records?
ANSWER: 18 weather joins lacked spatial coverage and are kept null and excluded from correlations, documented per row, never zeroed.
KEY POINT: Documented exclusion.
IF PROFESSOR PUSHES FURTHER: Excluding with documentation beats fabricating.

### K8. Why call this multi-level?
QUESTION: Why are you calling this a multi-level analysis?
ANSWER: Because it analyzes India, zone, and state levels with distinct methods per level, plus temporal, weather, and supporting-factor layers.
KEY POINT: Levels plus layers.
IF PROFESSOR PUSHES FURTHER: Framework diagram shows the hierarchy.

### K9. What is actually new here?
QUESTION: What is actually new here?
ANSWER: The combined package is the contribution: reconciled benchmark, harmonized history, weather integration, FDR-validated associations, honest ML null, and a reusable platform, all with provenance. No single-result novelty is claimed.
KEY POINT: Package, not miracle.
IF PROFESSOR PUSHES FURTHER: Ten contributions listed.

### K10. What if another dataset gives different numbers?
QUESTION: What if another dataset gives different numbers?
ANSWER: That is expected across vintages like MoRTH versus NCRB; my design keeps vintages separate precisely so differences are visible, not hidden.
KEY POINT: Separation handles it.
IF PROFESSOR PUSHES FURTHER: The minus 19,740 NCRB gap is documented.

### K11. Why didn't you merge MoRTH and NCRB?
QUESTION: Why didn't you merge MoRTH and NCRB?
ANSWER: Different definitions, totals, and vintages; merging would corrupt both series. NCRB monthly is analyzed in parallel only.
KEY POINT: Incompatible by definition.
IF PROFESSOR PUSHES FURTHER: Every NCRB file is vintage-labeled.

### K12. Why not one 2014-2024 dataset?
QUESTION: Why didn't you use 2014-2024 as one continuous dataset?
ANSWER: Different vintage with boundary breaks at J&K and DNH/Diu; a forced merge would smooth over real discontinuities.
KEY POINT: Breaks must stay visible.
IF PROFESSOR PUSHES FURTHER: Conditional candidate exists for sensitivity only.

### K13. Can your model predict tomorrow's accidents?
QUESTION: Can your model predict tomorrow's accidents?
ANSWER: No. It predicts next-year state counts and loses to last year's value. No daily or real-time capability is claimed.
KEY POINT: Firm no.
IF PROFESSOR PUSHES FURTHER: Deployment would be irresponsible.

### K14. Can your dashboard identify the most dangerous road?
QUESTION: Can your dashboard identify the most dangerous road in India?
ANSWER: No. No road-level or coordinate data exists in the verified set, so no such claim is made anywhere.
KEY POINT: Firm no.
IF PROFESSOR PUSHES FURTHER: It identifies recorded patterns at state resolution.

### K15. Can clustering identify dangerous states?
QUESTION: Can clustering identify dangerous states?
ANSWER: No. Clusters are descriptive count profiles without exposure denominators, so risk labels are prohibited.
KEY POINT: Firm no.
IF PROFESSOR PUSHES FURTHER: Wording enforced in all cluster outputs.

### K16. What is the causal mechanism for weather?
QUESTION: What is the causal mechanism behind your weather finding?
ANSWER: I propose none. The analysis is associational; any mechanism would need exposure, behavioral, and road-condition data.
KEY POINT: No mechanism claimed.
IF PROFESSOR PUSHES FURTHER: Scale confounding is the leading alternative explanation.

### K17. Does negative rainfall correlation mean rain reduces accidents?
QUESTION: Does a negative rainfall correlation mean rain reduces accidents?
ANSWER: No. It means higher-rainfall state-years tend to have fewer recorded accidents, which could reflect geography, exposure, or reporting differences.
KEY POINT: No causal reading.
IF PROFESSOR PUSHES FURTHER: Within-state samples are too small for mechanism claims.

### K18. Why is the 2020 decline meaningful?
QUESTION: Why is the 2020 decline meaningful?
ANSWER: It is the largest single-year move in the panel, coinciding with restricted mobility, but I describe it as an observed dip with recovery, not a proven cause.
KEY POINT: Observed, contextualized.
IF PROFESSOR PUSHES FURTHER: Minus 18.6% accidents that year.

### K19. Why aren't counts enough for risk?
QUESTION: Why aren't accident counts enough to measure risk?
ANSWER: Because large states have more people, vehicles, and road length. Without dividing by exposure, big only means big, not dangerous.
KEY POINT: Denominator logic.
IF PROFESSOR PUSHES FURTHER: My go-to defense sentence.

### K20. Association versus causation?
QUESTION: What is the difference between association and causation?
ANSWER: Association means two variables move together; causation means changing one changes the other, which needs a design ruling out confounders. My study shows the first only.
KEY POINT: Textbook distinction applied.
IF PROFESSOR PUSHES FURTHER: Every finding is labeled accordingly.

### K21. Why exclude Ladakh early years?
QUESTION: Why do early Ladakh rows show no values?
ANSWER: Ladakh as a separate UT did not exist in those years; values appear from 2021 onward. History, not missing data handling.
KEY POINT: Boundary history.
IF PROFESSOR PUSHES FURTHER: Flagged in the harmonization map.

### K22. Why is severity rising while accidents fluctuate?
QUESTION: Why is severity rising while accidents fluctuate?
ANSWER: Fatalities grew 12.4% against 3.7% accident growth, so the ratio rose. I report the pattern and its components without asserting a single cause.
KEY POINT: Components reported.
IF PROFESSOR PUSHES FURTHER: 33.50 to 36.33 per 100 accidents.

### K23. Could the weather result be pure scale effect?
QUESTION: Could the weather result be pure scale effect?
ANSWER: Partly, plausibly. Large dry states differ from small wet ones on many dimensions. I disclose this and show within-state descriptives as context.
KEY POINT: Conceded and documented.
IF PROFESSOR PUSHES FURTHER: Sensitivity analysis covers pooled versus within-state.

### K24. What stops someone misusing your dashboard?
QUESTION: What stops someone misusing your dashboard as a risk ranking?
ANSWER: Every relevant surface states counts are not risk, associations are not causes, and unavailable data stays unavailable with reasons.
KEY POINT: Guardrails in UI text.
IF PROFESSOR PUSHES FURTHER: Demo script trains the presenter to repeat this.

### K25. One line: why pass this project?
QUESTION: In one line, why should this project pass?
ANSWER: Because it built a verified, reproducible, honestly limited analytical foundation that answers eleven research questions with evidence while refusing to fabricate what the data cannot support.
KEY POINT: Evidence plus integrity.
IF PROFESSOR PUSHES FURTHER: That is the closing line of my presentation.
