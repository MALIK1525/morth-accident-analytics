# PHASE 2C — GEOGRAPHY REPORT (script: `phase2c_geography_vehicle.py`; no join, no metrics, website untouched)

## J&K / Ladakh — RESOLVED (RGI, HIGH; BRSI, MEDIUM)
- RGI report pp.8,22: J&K(UT) projected by cohort-component on J&K(State) SRS rates; **Ladakh = residual of J&K(State) minus J&K(UT)**. Hence RGI J&K EXCLUDES Ladakh; summing them reconstructs the old state — no double-count.
- Join actions: RGI J&K→MoRTH J&K DIRECT all 2018–2024 (HIGH); RGI Ladakh→MoRTH Ladakh DIRECT all years incl. 2018 (HIGH; Ladakh series present from 2011 base).
- BRSI lists J&K and Ladakh as separate rows (1.1.2 rows 34/35) but carries no composition note → DIRECT with MEDIUM confidence; J&K double-count check remains OPEN.
- 18-row resolution table in sheet 04 with per-year evidence.

## DNH / Daman & Diu — RESOLVED with documented aggregation (MEDIUM)
- RGI projects DNH and Diu separately (mathematical/exponential method, p.26) for all years; MoRTH has legacy separate rows 2018–19 and merged "Dadra & Nagar Haveli and Daman & Diu" 2020–24 (merger Jan 2020).
- Join actions: 2018–19 DIRECT (HIGH); 2020–24 SUM_DNH_PLUS_DAMAN_DIU (MEDIUM) — arithmetic sum, NOT source-published, must be flagged in outputs. Same rule for BRSI 2021/22 rows.
- 13-row resolution table in sheet 05.

## Master crosswalk — 16 rows, year-aware (sheet 06)
Covers RGI + BRSI + future-vehicle slot (UNRESOLVED). Timeless mappings avoided where structure changed.

## Vehicles — NOT ACQUIRED
Attempts: MoRTH RTYB direct (blocked SPA), morth.gov.in year-book page (SPA, no links), data.gov.in JS-only + catalog API 404, CEIC/secondary rejected per rules. `phase2_raw/vehicles/` empty. Sheets 02/03 present but empty by design.
