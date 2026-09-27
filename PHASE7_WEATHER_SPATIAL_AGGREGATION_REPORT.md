# PHASE 7 — SPATIAL AGGREGATION REPORT (script: `phase7_weather_spatial_aggregation.py`)

## Boundary: SOI ABDB (official, Survey of India)
- File: `phase7_raw/boundaries/SOI/SOI_ABDB_PANINDIA.rar` (202,524,438 bytes; RAR4, verified listable; extracted with modern 7-Zip).
- 36 non-disputed state polygons, all valid, CRS LCC_WGS84 (projected metres — areas used directly, no degree-areas).
- Vintage: post-2019 (J&K + Ladakh separate; merged DNH-DD). 4 DISPUTED slivers excluded (documented).
- J&K/Ladakh: separate polygons, DIRECT both. DNH-DD merged: DIRECT 2020–24; legacy 2018–19 separate polygons unavailable → 4 MoRTH rows UNRESOLVED (accidents preserved, weather missing).

## Aggregation (area-weighted, per-day renormalized)
- Rain: -999 → nan (CORRECTION to Phase 6 note which said ocean-as-0.0); daily valid-weight ≥50%.
- Temp: 99.9 excluded per-day, weights renormalized; daily coverage ≥50%.
- Monthly: full rain month + ≥25 temp days. Annual: all rain days + ≥330 temp days.
- BUG FOUND & FIXED: masked-array `np.where` kept -999 (TN −8981mm); fixed with `ma.filled(...,nan)`; re-validated 0 negatives.

## Outputs
- Annual: 252 rows, 238 VERIFIED, 14 PARTIAL (islands temp). Monthly: full 36×84 grid with flags.
- MoRTH join: 254 rows, 250 matched, 4 unmatched (legacy, expected), 0 duplicates, no many-to-many.
- No weather-accident statistics, no causal claims, 2020 unexplained, website untouched.
