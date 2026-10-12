# Research Data Coverage Report — Phase 3 (2026-09-28, commit 670cd86)

Audit-only phase. No application code changed. All claims grounded in files
inspected in the repository (see Evidence column of MASTER_PARAMETER_AVAILABILITY.csv).

## Counts (52 parameters)
- DIRECT: 6 | DERIVED: 9 | SUPPORTING_DATA: 7 | INTEGRABLE: 5
- PARTIAL: 3 | YEAR_LIMITED: 3 | UNAVAILABLE: 16 | UNSAFE_TO_INFER: 3

## Primary benchmark (MoRTH_Primary_Dataset_3.xlsx, CLEAN, 254 rows)
- 2018: VERIFIED (38 entities; DNH + Diu separate) | 2019: VERIFIED (revised vintage — see below)
- 2020–2022: VERIFIED | 2023–2024: VERIFIED except state injuries N/A (India injuries verified)

## 2019 source-vintage issue (preserved, benchmark unchanged)
- Original 2019 report vintage: 449,002 acc / 151,113 fat / 451,361 inj
- Later revised vintage (benchmark): 456,959 acc / 158,984 fat / 449,360 inj
- Implication: longitudinal 2018→2019 step mixes vintages; YoY across that boundary is flagged in Phase 4 outputs.

## Historical extension 2014–2017
- 2014–2017 state panel: UNAVAILABLE (no verified state file; geography/vintage unvalidated)
- 2014–2017 India totals: PARTIAL via EX-01 exposure CSV (accidents/deaths/injuries India-level only)
- Verdict: NO combined 2014–2024 state panel. Unsafe to backfill.

## Weather
- 236 usable / 18 excluded (Lakshadweep 7, Andaman 7, legacy DNH/Diu 4). Rain + Tmax + Tmin.
- Humidity / visibility / fog / wind: UNAVAILABLE. Lighting: UNAVAILABLE.

## Supporting modules (all VERIFIED-MIRROR, MoRTH AR 2024 via OpenCity extraction)
- VH-01/CS-01/CL-01/EX-01/DL-01/SD-01/CT-01 + VH-02 matrix: India-level (cities: 50-city).
- RD-01/SV-01: no verified files, remain unavailable.

## Professor requirements (22 items)
- READY: 17 | PARTIALLY READY: 3 (time-to-threshold, KNN, exposure) | DATA REQUIRED: 2 (unsupervised, seasonality)

## Real research core
- India-wide immediate: accidents/fatalities/injuries-India/severity/pop-normalized/weather-assoc/ML-lag.
- State-level: accidents/fatalities/severity/pop-normalized/weather (matched)/slopes.
- India-only: violations/collisions/road-user/licence/safety/vehicles-registered/cities.
- 2023–24-only: violation/collision/road-user/cities/safety.
- Unavailable: IDs/dates/coords/district/driver-detail/vehicle-detail/month/hour/AADT/humidity.
- Do not pursue without new data: hotspot/blackspot, causal weather claims, state 2023–24 injuries, monthly seasonality.
