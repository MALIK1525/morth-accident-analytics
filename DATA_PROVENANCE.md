# Data Provenance

## Primary panel (DIRECTLY VERIFIED)
- Source: Ministry of Road Transport & Highways (MoRTH), "Road Accidents in India" annual series,
  via PIB annexures and Parliamentary Q&A documents.
- File: `data/MoRTH_Primary_Dataset_3.xlsx`, sheets RAW (untouched extract) / CLEAN (standardised).
- Coverage: 254 state-year rows, 38 reporting entities, 2018–2024.
- India totals reconcile with published benchmarks with 0 difference every year.
- Injured: state-wise 2018–2022; India-level only 2023 (462,825) / 2024 (471,441).
- Boundary change: 37 units (2018–19) → 36 units (2020+); DNH+Daman&Diu merged; Ladakh split from J&K.
  No back-casting performed.

## Supporting workbooks (reference, read-only)
- `MoRTH_Primary_Dataset_1/2.xlsx`, `OriginPro_Tier1_Tables.xlsx`,
  `OriginPro_Tier1_Analysis_Tables.xlsx` — Tier-1 G1–G10 table definitions.

## Audit CSVs (user-supplied, visualised as-is)
- DATASET_REGISTER, ANALYSIS_READY_DATASETS, PARAMETER_FINAL_STATUS, DATA_AVAILABILITY,
  RESEARCH_AUDIT_ISSUES, DATA_CLEANING_LOG — provenance: user's own research audit, 2026-09-22.
- Underlying data files they describe (paths `/home/z/...`) are NOT in this workspace.

## Source separation
- MoRTH, NCRB, IMD, police sources are never merged silently. NCRB 2024 road deaths (162,500)
  vs MoRTH (177,175) is surfaced as a documented conflict, not reconciled.

## Derived variables (formula-labelled in UI)
- Fatalities_per_100_Accidents = Fatalities/Accidents×100 (ratio, not a mortality rate).
- OLS slopes, R², p-values, CAGR, YoY changes — computed live, never hardcoded.
