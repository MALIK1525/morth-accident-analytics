# Phase 4 — Data Gap Report (supplement to Phase 3 audit; Phase 3 files NOT overwritten)

## New verified data
- TN district 2021-23 (38 districts, sums == benchmark): enables TN-only district drill-down.
- NCRB month-wise 2024 (Road/RailX/Rail/Grand x States/UTs/Cities): enables 2024 seasonality
  analysis under NCRB vintage ONLY. NCRB road total 467,967 vs MoRTH 487,707 — separate sources.

## Coverage update
See research_audit/PHASE4_COVERAGE_UPDATE.csv. Two parameters move UNAVAILABLE → PARTIAL
(month, district); time-bucket and state-vehicles move to DISCOVERED.

## Still blocked
Accident-level IDs/coords (eDAR restricted); multi-state districts; driver/vehicle detail;
humidity/visibility/fog/wind; state vehicle panel (needs manual OGD download); 2014-17 state
panel (PDFs exist, extraction + geography reconciliation pending).

## Integration verdicts
- TN districts → CONDITIONAL (TN-only; sums reconcile).
- NCRB monthly → NO merge; parallel-vintage use only.
- Nothing was merged into MoRTH_Primary_Dataset_3.xlsx.
