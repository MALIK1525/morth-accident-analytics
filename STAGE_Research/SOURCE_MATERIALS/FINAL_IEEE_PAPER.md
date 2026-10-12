# Data-Driven Road Traffic Accident Analysis in India (IEEE-style draft)

Title as above. Abstract: per abstract draft. Index Terms: road safety; accident severity;
weather association; time-series baseline; K-means clustering; data provenance.

## I. INTRODUCTION — counts, severity rise, exposure gap, RQ1-RQ11 (observational framing).
## II. RELATED WORK — LITERATURE REVIEW SOURCES REQUIRED (no invented citations).
## III. DATA AND METHODOLOGY — benchmark 254 obs 2018-2024 (38 entities); conditional history; NCRB/IMD/supporting layers
(236 weather-matched); reconciliation; OLS/corr/chi2/Friedman + BH-FDR; lag-only ML (train 2019-22/test 2023-2024,
acc RMSE 1038.6) vs naive; K-means K=2 (silhouette 0.356); seed 42.
## IV. RESULTS — +3.7% acc vs +12.4% fat; severity 36.33; weather r values; Friedman p=3.0e-4;
May 8.84%/Jul 7.46%; naive RMSE 1038.6/286.3 beats all trained; K=2 silhouette 0.356.
## V. DISCUSSION — counts vs risk; persistence; exploratory clusters; vintage discipline.
## VI. LIMITATIONS — full matrix referenced. VII. FUTURE WORK — 10 items. VIII. CONCLUSION — RQ answers.
## REFERENCES — see FINAL_REFERENCES.md (mirrors labeled; no invented DOIs/papers).
