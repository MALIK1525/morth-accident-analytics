# PHASE 3 — NORMALIZED ANALYSIS REPORT (script: `phase3_normalized_analysis.py`; DESCRIPTIVE ONLY)

## India (published RGI projections as denominator; state sums == MoRTH benchmarks TRUE)
| Year | Acc/lakh proj.pop | Fat/lakh proj.pop |
|---|---|---|
| 2018 | 35.51 | 11.90 | 2019 | 34.12 | 11.87 | 2020 | 27.50 | 10.22 |
| 2021 | 30.17 | 11.26 | 2022 | 33.43 | 12.21 | 2023 | 34.52 | 12.42 | 2024 | 34.71 | 12.61 |
YoY on normalized measures in sheet 05. Wording: "exposure-adjusted", never causal.

## Population normalization (254 usable, 0 excluded; 249 VALID + 5 VALID_WITH_TRANSFORMATION)
- State table (2018–24) + zone table (numerator+denominator aggregated first, never averaged rates) + raw-vs-normalized shares + distributions (N/mean/median/SD/min/max/Q1/Q3/IQR per year) + state YoY.
- Injury metric: 179 rows only (verified coverage); 2023–24 state cells NaN, never filled.
- No state/zone ranking or scores. Maximum reported as "maximum observed value in the analyzed distribution".

## Road normalization (2021–22 ONLY: eligible 72, usable 68, excluded 4 UNRESOLVED J&K/Ladakh)
- Metrics: Acc/Fat per 1,000 km total road (+ surfaced variants preserved separately; surfaced NOT treated as total exposure).
- State table + distributions + 2021–2022 change table (labeled "2021–2022 change", never "long-term trend").

## Associations (pooled state-year, descriptive)
- Population vs Accidents: Pearson 0.677, Spearman 0.910 (N=254).
- Population vs Fatalities: Pearson 0.903, Spearman 0.956 (N=254).
- Labeled pooled association with scale-effect caveat; NOT causal. No regression performed.

## Sensitivity
DNH: DIRECT n=249 vs SUM n=5 — insufficient evidence for a stable sensitivity conclusion. J&K/Ladakh road cells excluded as required.

## Graph specs
Tier 1 G-P1…G-P10 prioritized (India raw-vs-normalized, state/zone normalized, road 21-vs-22, pop-vs-acc scatter); data tables ready in workbook sheets 02–12.
