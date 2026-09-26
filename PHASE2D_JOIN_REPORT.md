# PHASE 2D — JOIN REPORT (script: `phase2d_join.py`; 9/9 automated checks PASS)

## Population join (2018–2024): 254/254 matched, 0 unmatched, 0 unresolved
- DIRECT 249 (HIGH, JOINED) — incl. J&K DIRECT (residual proof) and Ladakh DIRECT all years.
- SUM 5 (MEDIUM, JOINED_WITH_TRANSFORMATION) — merged DNH-DD 2020–24 = RGI DNH + Diu arithmetic sums.
- Units: Population_Source_Thousands preserved + Population_Persons = ×1000; Population_Is_Projection = True everywhere.

## Road join (2021–2022 ONLY): 72/72 eligible rows present
- JOINED 66 DIRECT (HIGH, incl. renames Tamilnadu, A & N Islands) + JOINED_WITH_TRANSFORMATION 2 SUM (merged UT, MEDIUM).
- UNRESOLVED 4: J&K + Ladakh × 2021/22 — values preserved, excluded from usable set per Phase 2D rule.
- No rows outside 2021–22. 2018–20/2023–24 documented as NOT_AVAILABLE (no fake rows).

## Audit
254-row audit table; Overall_Exposure_Status ∈ {POPULATION_READY, POPULATION_READY_ROAD_READY}; no FULLY_EXPOSURE_READY row (vehicles absent).

## India sanity
- Population joined sums vs published: −1/−3/+7/+2/−1/0/+1 ('000, rounding only).
- Road: usable-joined + UNRESOLVED cells reconstruct published totals exactly (2021: 5,474,512 + 118,299 + 5,473 = 5,598,284 ✓).
- Vehicles: 0. Normalized metrics: none. Stats/ML: none. Website: untouched.
