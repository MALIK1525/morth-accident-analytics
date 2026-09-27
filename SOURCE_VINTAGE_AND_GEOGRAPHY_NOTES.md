# SOURCE VINTAGE & GEOGRAPHY NOTES (locked reference)

## 2019 vintage
- Earlier MoRTH 2019 report: 449,002 acc / 151,113 fat / 451,361 inj.
- Later vintage (used in panel): 456,959 / 158,984 / 449,360.
- Decision: longitudinal 2018–2024 panel uses later vintage throughout; earlier vintage retained for reference only, never mixed.

## Geography (year-aware)
- J&K/Ladakh: separate throughout exposure/weather joins; RGI J&K excludes Ladakh by construction (RGI pp.8,22); BRSI composition note unresolved → 4 road cells UNRESOLVED.
- DNH/Daman & Diu: legacy separate (2018–19, DIRECT) → merged (2020–24, SUM/MEDIUM, arithmetic); weather split 2018–19 UNRESOLVED; 4 MoRTH rows unmatched.
- Telangana separate in all sources. NCT→Delhi, Tamilnadu, A&N renames recorded.
- SOI ABDB = modern vintage; 4 DISPUTED polygons excluded from weather.

## Abstract (draft)
Background: India carries a large road-traffic mortality burden with marked geographic variation. Objective: multi-level analysis of occurrence and severity, 2018–2024. Data: verified MoRTH state-year panel (254 obs), RGI projections, BRSI road length (2021–22), IMD rainfall/temperature aggregated via SOI boundaries (236 matched obs). Methods: normalization, OLS/FDR, FE, leakage-safe chronological ML, sensitivity analyses. Results: accidents +3.7%, fatalities +12.4%, severity 33.50→36.33; weather associations FDR-robust but observational; 9/34 severity slopes FDR-robust; naive baseline beat trained ML (RMSE 1053.3). Limitations: no vehicles/Census/monthly/driver data; N=7 trends; no causal identification. Contribution: verified multi-level framework with quantified uncertainties and transparent data gaps.

## Objectives (final)
PRIMARY (achieved): India/zone/state temporal analysis; exposure normalization; weather integration+association; severity heterogeneity; leakage-safe ML benchmark.
SECONDARY (achieved): sensitivity/FDR discipline; OriginPro reproducibility; unavailable-data framework.
OUT OF SCOPE (data absent): causal attribution, prediction deployment, vehicle/cause/driver analysis, monthly/GIS analysis.

## Reproducibility (summary)
Order: P1 audit → P2 exposure+joins → P3 normalized → P4 inference → P5 ML → P6 IMD → P7 boundaries/aggregation/join → P8 associations → P9 severity → P10 synthesis. Scripts phase*_*.py rerun in order; raw files hashed/preserved (phase2_raw, phase6_raw, phase7_raw); exclusions enforced by Join_Status flags; website untouched throughout.
