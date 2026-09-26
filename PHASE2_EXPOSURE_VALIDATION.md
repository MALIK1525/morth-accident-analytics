# PHASE 2 — EXPOSURE VALIDATION

- MoRTH India totals reconcile: acc TRUE, fat TRUE (all 7 years, 0 mismatch).
- Denominator India-total reconciliation: NOT APPLICABLE — no denominator files.
- Missingness/duplicates on exposure: NOT APPLICABLE — no files.
- Provenance gate (source/doc/raw-file/definition/unit/geography/year/missingness/duplicates): all three variables FAIL at "raw file preserved" → STATUS = NOT VERIFIED → unused in calculations.
- Join audit: matched 0 / unmatched MoRTH 254 / unmatched exposure 0 / duplicates 0 → BLOCKED.
- Formulas reserved (not executed): Acc_per_100k_pop = Accidents/Population×100000; Acc_per_10k_veh = Accidents/Registered_Vehicles×10000; Acc_per_1000km = Accidents/Road_Length_km×1000 (and fatality/injury analogues).
- No synthesis, interpolation, or silent reconciliation performed.
