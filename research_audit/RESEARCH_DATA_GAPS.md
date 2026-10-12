# Research Data Gaps — Phase 3

## Blocking gaps (need new verified acquisition)
1. Per-accident records (ID/date/coords) — restricted eDAR; no public path.
2. Month/day/hour accident data — NCRB ADSI PDF-only (Table 1A.5); needs extraction for seasonality.
3. District panel — only TN publishes CSV (not in repo).
4. Driver/vehicle detail — no verified file; licence table is the only driver variable.
5. Humidity/visibility/fog/wind — no verified source.
6. State split of registered vehicles — India-only stock; state exposure rate unsafe.
7. AADT / vehicle-km — no source.
8. 2014–2017 state panel — no verified file; backfill unsafe.

## Safe integrations (join keys documented in INTEGRATION_COMPATIBILITY.csv)
- Population × accidents (State+Year, done in Phase 2D; 5 SUM rows flagged).
- Road length × accidents (State+Year, 2021–22 only).
- Weather × accidents (State+Year, 236 matched only).

## Prohibited inferences (UNSAFE_TO_INFER — must never be done)
- State 2023–24 injuries from India totals.
- Monthly accidents from annual totals.
- Coordinates for aggregates (state/city centroids as points).
- Hotspot/blackspot from state aggregates.
- Causal weather/severity claims from observational associations.
- Pan-India season labels without month data.
