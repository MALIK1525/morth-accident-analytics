# Phase 8 Analysis Report (research only; no website/app changes)

## Severity
- Cause (CS-01 2024): Over-speeding 345,024 acc / 124,522 killed (ratio 0.361); drunk driving ratio 0.387 (highest ratio, small base 8,270) — "reported category", never proven cause.
- Collision (CL-01 2024): Hit from Back most frequent (113,907); Hit and Run highest ratio (~0.496).
- Road-user (VH-01 2024): Two-wheelers 81,780 (46.2%); pedestrian 36,526 (20.6%) — counts, no exposure.
- Licence (DL-01): Valid licence 68.2% of 2024 accidents (share of reported accidents, not drivers).
- Safety (SD-01 2024): no-helmet killed 54,122; no-seatbelt killed 14,466 (non-use toll, not effectiveness).

## Weather (pooled N=236; zone subgroups N>=20 interpreted, smaller SMALL_N)
- Reproduces Phase 7/8 values. Zone-stratified results in WEATHER_STATISTICAL_VALIDATION.csv.
- Within-state (N<=7): LOW_POWER_DESCRIPTIVE only, excluded from inference (WITHIN_STATE_WEATHER.csv).
- Severity: no detectable association (|r|<0.15).

## Zone test
- Friedman (6 zones x 7 years, years as blocks): chi2=25.29, p=3.0e-4, Kendall W=0.72 — zones differ
  descriptively across years; NOT a ranking.

## State trends
- Accidents: 17 positive / 15 negative / 6 near-zero; 5 detectable at p<0.05.
- Fatalities: 26 positive / 10 negative / 2 near-zero; 9 detectable.
- Near-zero rule: |slope| <= 0.5% of state mean. Exact p-values reported; non-significant shown.

## NCRB monthly (separate vintage)
- Chi-square vs uniform: 1276.0, p<1e-6 (N=467,967 — significance expected at this N; shares matter:
  May 8.84% vs Jul 7.46%). Calendar-quarter grouping (Q1-Q4), never called climate seasons.

## City / TN district
- 50 cities with fatality ratios (no extrapolation). TN districts reconcile; TN-only.

## Multiple testing
- BH-FDR over weather/severity + state-trend families (MULTIPLE_TESTING_CORRECTION.csv).

## Sensitivity
- Benchmark-only core; historical candidate separate; pooled-vs-within-state documented;
  per-pair weather N explicit.

## ML features
- Ready: lag acc/fat; Conditional: population, weather (lagged only); Unavailable: India-level
  shares, target-year values (leakage). No training in this phase.

## Exposure
- State vehicle stock UNAVAILABLE — no per-vehicle metrics. Stated in every relevant table note.
