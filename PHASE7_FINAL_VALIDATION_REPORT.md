# PHASE 7 FINAL VALIDATION REPORT

**Status: B — VALIDATED WITH DOCUMENTED EQUAL-CELL METHOD**

No weather-accident statistics performed. No website changes. No raw-file modifications.

## 1. Area-weighting validation
- Formal cos(latitude) area weights implemented and compared against production equal-cell means for all 245 state-years (rainfall).
- Max relative difference **0.596%** (West Bengal 2022, 9.3 mm on 1571.8 mm); mean **0.09%**.
- Conclusion: deviation is **immaterial**. Dataset retains EQUAL_CELL_WEIGHTED label with this quantified justification; no relabeling as area-weighted.

## 2. Boundary-cell / centroid validation
- 17,415 IMD rainfall cells considered; **4,651** assigned by centroid-in-polygon; **3,356** fully inside, **1,295** partial-overlap boundary cells.
- Overlap-fraction-weighted comparison: max rel diff **2.68%** (Haryana 2019), mean **0.71%**; 238/245 rows OK, 7 INSUFFICIENT_COVERAGE (Andaman).
- Conclusion: centroid assignment effect is small and bounded; existing method retained with this sensitivity table (`boundary_cell_sensitivity.csv`).

## 3. Andaman & Nicobar explicit spatial validation
- SOI polygon intersects **53** rainfall grid cells; **0** valid on any checked day (all carry the IMD −999 ocean mask).
- Nearest valid land cell is **~1,287 km** away (mainland) — nearest-cell substitution would be indefensible.
- Conclusion: 7-year exclusion **verified as genuine ocean-masking**, not a processing error. Retained as unavailable with exact reason (`andaman_spatial_validation.csv` with all 53 cell coordinates).

## Files
- `PHASE7_FINAL_VALIDATION.xlsx` (summary, comparisons, Andaman cells, methods)
- `area_weighting_comparison.csv`, `boundary_cell_sensitivity.csv`, `andaman_spatial_validation.csv`
- `phase7_final_validation.py` (re-runnable), `phase7_final_numbers.json`

## Blocking issues for Phase 8
None. Phase 8 may proceed on MATCHED rows only, with island/legacy exclusions preserved.
