# PHASE 2B — EXTRACTION REPORT (script: `phase2b_extraction.py`; originals untouched, hashes unchanged)

## Population (RGI Table 11, 1 July, 2018–2024)
- Extracted: 266/266 rows (37 entities + INDIA × 7 years), 0 duplicates, 0 missing. Unit '000 preserved.
- India projections ('000): 2018 1,324,609; 2019 1,338,995; 2020 1,353,378; 2021 1,367,173; 2022 1,379,750; 2023 1,392,329; 2024 1,404,910.
- Geography as printed: JAMMU & KASHMIR (UT) + LADAKH separate; TELANGANA separate; DAMAN & DIU + DADRA & NAGAR HAVELI separate; NCT OF DELHI; 37 entities + INDIA.
- M+F≠Persons in 73/266 rows: pure '000-rounding (e.g. Lakshadweep 33+31=64 vs 65). Persons used as denominator; sexes retained for audit.
- PROJECTIONS, not census counts — "The population denominator is based on RGI projections rather than a 2021 population census."

## Road length (BRSI Annex 1.1.2 = 2021, 2.1.2 = 2022)
- Extracted: 74/74 rows (37 entities × 2 years), 0 duplicates. Total + Surfaced km preserved; definition: all reported roads, *excluding JRY roads*.
- Geography as printed: Andhra Pradesh INCLUDES Telangana? NO — Telangana listed separately (rows 1+24). J&K + Ladakh separate rows. DNH + Diu separate. BRSI spellings preserved ("Tamilnadu", "A & N Islands").
- CAUTION carried: the "* AP includes Telangana / # J&K" footnote seen on project-road annexes (1.7.9/2.7.9) — checked NOT applicable to 1.1.2/2.1.2 totals tables, which list Telangana separately. Stale *#@ footnotes observed only on category tables (e.g. 1.3.1), not the extracted totals.
- Coverage: 2021–2022 ONLY. No 2018–2020 or 2023–2024 state road totals in this edition.

## Geography mapping
12 mapping rows in sheet 06: 6 HIGH (direct/rename), 3 MEDIUM (J&K base composition, DNH+Diu sum), 3 UNRESOLVED (BRSI-DNH/Diu→MoRTH-merged join rule, J&K double-count check). Nothing forced.

## Vehicles / join / normalized metrics
REGISTERED VEHICLE DENOMINATOR: NOT AVAILABLE FROM VERIFIED DATA. JOIN: NOT PERFORMED. NORMALIZED ANALYSIS: NOT PERFORMED. Production website untouched.
