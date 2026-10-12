# Methodology (paper-ready draft; methods actually performed)

## Data sources
MoRTH Road Accidents in India reports 2014-2024 (state tables; benchmark 2018-2024, 254 state-years,
38 entities); NCRB ADSI 2024 Table 1A.5 (monthly, separate vintage); IMD Pune CMPG daily grids
(rain 0.25°, Tmax/Tmin 1°, 2018-2024) aggregated to state level via Survey of India ABDB polygons
(equal-cell weighting; area-weighting sensitivity <=0.6%); RGI population projections Table 11
(1 July); BRSI 2020-22 road length (2021-2022 only); MoRTH AR 2024 supporting tables via OpenCity
extraction mirror (collision, violation, road-user, licence, safety-device, cities, exposure).

## Verification
State sums reconciled against published India totals for every year/variable (exact matches;
full audit tables in research_acquisition/). NCRB kept vintage-separate (2024 road total 467,967
vs MoRTH 487,707). Historical 2014-2017 extracted single-vintage (AR2017) with 12/12 reconciliations.

## Geography
Year-aware harmonization: Telangana direct; J&K undivided pre-2020 (break flagged at 2019-2020);
DNH/Diu summed pre-2020 (MEDIUM, arithmetic); Ladakh values from 2021, NV before.

## Statistics
Descriptives, YoY, OLS slopes with 95% CI (N=7/state; low power disclosed), Pearson+Spearman,
chi-square goodness-of-fit, Friedman test (years as blocks), BH-FDR multiple-testing correction,
effect sizes (r, R2, Kendall W). Association language throughout; no causal claims.

## Predictive modeling
State-year panel, lag-only features (cutoff T-1), chronological train (targets 2019-2022, N=141)
vs test (2023-2024, N=72), naive persistence baseline, rolling-origin validation, no test-set tuning,
5 supervised regressors incl. KNN Regression (supervised). K-means on standardized state profiles
(K=2-6 diagnostics; K=2 by max silhouette 0.356; ARI stability; PCA for display).

## Software
Python (pandas, scipy, scikit-learn, pypdf); all scripts in research_analysis/; seeds fixed (42).
