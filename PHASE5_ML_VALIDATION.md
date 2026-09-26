# PHASE 5 — VALIDATION

- [x] No duplicate state-target-year rows (175 unique)
- [x] Target = annual state accident count
- [x] Every feature source-year documented (sheets 02/03)
- [x] Leakage audit passed: no target-year/future values, no full-period slopes, Pop_t assumption explicit
- [x] No random split; test (2023–24) strictly after train (2020–22)
- [x] Naive baseline on identical test rows
- [x] Scaler fit on train per fold; defaults documented, no test-touched tuning
- [x] Importance after leakage-safe training only; labeled predictive
- [x] Missing/excluded rows documented (9 non-full-panel rows; road/vehicle/weather excluded)
- [x] No synthetic data; vehicles/weather/GIS absent; website unchanged
- [x] KNN labeled supervised; no k-means
