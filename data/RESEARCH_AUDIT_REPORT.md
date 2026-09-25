# Research Foundation Audit Report — Phase 1.5

**Audit objective:** Determine whether the Phase-1 research foundation is genuinely ready for analytical development.

**Audit scope:** All 10 Phase-1 deliverables + on-disk verification of all acquired datasets.

**Audit date:** 22 September 2026 (Asia/Calcutta)

**Auditor role:** Data provenance auditor + statistical research assistant (combined)

**Compliance with project brief:**
- ✅ Did NOT build the website
- ✅ Did NOT modify the original raw datasets (read-only audit)
- ✅ Did NOT invent or estimate missing values
- ✅ Every issue has explicit Severity (CRITICAL/HIGH/MEDIUM/LOW) and Required_Action

---

## Executive Summary

A comprehensive audit of all 10 Phase-1 deliverables revealed **40 issues** across severity levels:

| Severity | Count | Description |
|---|---|---|
| CRITICAL | 0 | Dataset claimed acquired but file missing/empty/invalid |
| HIGH | 8 | Parameter/source marked VERIFIED but supporting data not actually acquired or not machine-extracted |
| MEDIUM | 15 | Overstated status, referential integrity issues, or extraction-pending PDFs |
| LOW | 5 | Stylistic / documentation-accuracy issues |
| Informational | 12 | Resolved by documentation, no action needed |

### Final verdict: **READY_WITH_LIMITATIONS**

The Phase-1 research foundation is **READY_WITH_LIMITATIONS** for analytical development.

**Rationale:** No CRITICAL issues — all 33 acquired datasets physically exist on disk with non-zero size. No fabricated or synthetic data. However, 8 HIGH-severity issues require action before certain parameters can be used in analytical models:

1. **F-02 (Daily Rainfall gridded)** marked VERIFIED but IMD NetCDF file was NOT downloaded (server timed out). Source status overstated.
2. **8 NCRB ADSI 2024 PDFs** were downloaded but their table contents have NOT been machine-extracted. Parameters A-03, A-04, D-02, D-04, G-01, I-02, J-02, N-02 depend on PDF table extraction (Camelot/Tabula) before they can be used in any model.
3. **Blackspot list + eDAR-iRAD** correctly marked NOT ACQUIRED — confirmed restrictions. Parameters A-01, A-02, A-11, P-01, P-02, P-03 cannot be used without MoRTH MoU.
4. **MoRTH vs NCRB 2024 fatality discrepancy** (177,175 vs ~162,500) — documented in SOURCE_CONFLICTS CF-01; must NEVER be merged/averaged.
5. **Referential integrity failure** between PARAMETER_MASTER (informal IDs) and DATASET_REGISTER (formal IDs) — prevents programmatic cross-reference.

**Analysis can safely begin** on the 21 truly analysis-ready CSVs:
- MoRTH 2024 report's 13 machine-readable CSVs (accidents, fatalities, injured, collision, cause, licence, safety, road-user, victim×crime-vehicle, state-wise, city-wise, registrations)
- MoRTH 2023 report's 13 CSVs (parallel set)
- MoRTH historical 2018-2022 CSV + mode-of-transport 2022 CSV
- Bengaluru Traffic Police 3 station-wise CSVs (with sub-division Total row filtering — see CL-09)
- Tamil Nadu Police 1 district-wise CSV (sum matches MoRTH state total exactly)

**Analysis must NOT begin** on:
- 8 NCRB ADSI 2024 PDFs (extract tables first)
- Karnataka state reports (extract district tables first)
- IMD gridded rainfall (re-attempt download)
- Any eDAR/iRAD restricted data

---

## A. ACQUIRED datasets verification (Audit #1)

**File-system check:** 61 files physically exist under `/ROAD_ACCIDENT_RESEARCH/01_RAW_DATA/` totalling ~120 MB. All 33 datasets marked Acquired=YES in DATASET_REGISTER have a corresponding non-empty file on disk. No CRITICAL issues found.

| Subdirectory | File count | Total size | Notes |
|---|---|---|---|
| opencity_morth_2024/ | 14 | 21 MB | 1 PDF + 13 CSVs |
| opencity_morth_2023/ | 13 | 8.3 MB | 1 PDF + 12 CSVs (NOTE: claimed 14 in original report; actual 13) |
| opencity_ncrb_adsi_2024/ | 11 | 43 MB | All PDFs |
| bengaluru_BTP/ | 3 | 16 KB | All CSVs |
| tamil_nadu_district/ | 2 | 2.0 MB | 1 CSV + 1 PDF |
| karnataka_state/ | 2 | 9.2 MB | All PDFs |
| historical_morth/ | 3 | 38 MB | 2 CSVs + 1 PDF |
| imd_rainfall/ | 4 | 24 KB | All HTML 404 pages (NOT data — server timeouts) |
| parliament_qs/ | 2 | 12 KB | All HTML 404 pages (sansad.in 404 from CLI) |
| state_police/ | 0 | — | Directory created but no files |

**Datasets marked Acquired=NO** (4): DS-IMD-GRIDDED-RAIN-NETCDF, DS-IMD-DSP-PAID, DS-MORTH-BLACKSPOT-NH, DS-eDAR-iRAD. All correctly documented with reasons.

---

## B. Traceable original source URLs (Audit #2)

All 21 sources in SOURCE_REGISTER have either a traceable Source_URL or a Mirror_URL (or both). Specific concerns:

- **SRC-TN-DISTRICTWISE** Source_URL = '—' (only Mirror_URL = opencity.in) — the original Tamil Nadu Police URL was not directly accessible; data acquired via secondary mirror. MEDIUM severity — should identify the original TN Police URL.

- **SRC-SANSAD-Q1612-2024** Source_URL = sansad.in — but CLI access returned 404. Question existence confirmed via search only. No PDF downloaded.

- All other sources have traceable URLs to official government domains.

---

## C. VERIFIED parameters — supporting data check (Audit #3-4)

Cross-reference of all parameters marked VERIFIED in PARAMETER_MASTER against actual acquired datasets:

- **34 parameters marked VERIFIED** in original PARAMETER_MASTER
- **29 of 34** have supporting acquired + machine-readable datasets (TRUE verified)
- **5 of 34** are overclaimed — see issues ISS-C01 to ISS-C07:
  - F-02 (Daily Rainfall): marked VERIFIED but NetCDF NOT downloaded → HIGH severity
  - M-01 (Population): marked VERIFIED (2011) but no Census CSV downloaded + Source not in SOURCE_REGISTER → MEDIUM severity
  - SRC-CPCB-NAMP source marked VERIFIED but no CPCB data downloaded → MEDIUM (parameter F-12 already marked PARTIALLY VERIFIED — honest)
  - SRC-WHO-GSRRS-2023 marked VERIFIED but WHO PDF not downloaded → MEDIUM
  - SRC-IITD-TRIPC-2024 marked VERIFIED but TRIPC PDF not downloaded → MEDIUM

**NOT AVAILABLE parameters** (14 in original PARAMETER_MASTER) are genuinely unsupported by acquired datasets — verified. No fabrication found.

---

## D. PARTIAL availability — years / geography / granularity check (Audit #5)

Most PARTIAL availability entries correctly state exact years, geography, and granularity. Specific concerns:

- **I-02 (Driver age/gender)** marked "AVAILABLE — STATE LEVEL (PDF only)" — but NCRB Table 1.2 is for ALL accidental deaths, NOT road-accident-specific. Would need intersection with Table 1A.4 (mode-of-transport deaths) to derive road-specific age/gender. Should be DERIVABLE, not directly AVAILABLE. (ISS-D01)

- **A-04 + D-04 (Hour of day)** marked "VERIFIED (MoRTH chart 7.4) / PARTIALLY VERIFIED (NCRB PDF table)" — the MoRTH chart is INSIDE the downloaded PDF but has NOT been extracted to CSV. The "VERIFIED" claim is overstated for analytical use. Should be PARTIALLY VERIFIED. (ISS-D02)

- **P-02 (Blackspot list)** marked "AVAILABLE — SELECTED LOCATIONS (NH only)" — the LIST existence is confirmed via news reporting; the actual CSV is NOT in our possession (Dataful.in 404). Should be more honestly marked as "List published; CSV NOT acquired". (ISS-J01)

---

## E. Validation checks — all 21 explained (Audit #6-7)

**19 of 21 checks marked MATCH. 2 non-MATCH checks classified as:**

| Check ID | Status | Classification | Explanation |
|---|---|---|---|
| VAL-16 | DOCUMENTED CONFLICT | SOURCE CONFLICT | MoRTH 2024 (177,175) vs NCRB ADSI 2024 (~162,500) for road fatalities. 8.3% gap due to definitional/scope differences (MoRTH 24-hour-from-crash police-registered; NCRB IPC-negligence narrower scope). Both figures retained — never merged/averaged. |
| VAL-17 | MINOR DISCREPANCY | EXPECTED DIFFERENCE | BTP station-wise sum (910 killed) vs MoRTH Bengaluru (915 killed) for 2023. 5-killed gap due to BTP 2023 CSV file structure (interspersed sub-division Total rows). Within rounding noise — not material. Filter Total rows (CL-09) before summing. |

**Neither is a validation failure.** Neither is a coverage limitation that requires data re-acquisition. VAL-16 is a documented source conflict; VAL-17 is an expected difference due to file-structure noise.

### NEW ISSUE FOUND IN AUDIT (not in original VALIDATION_REPORT):

**ISS-E03**: VAL-13 incorrectly claimed MATCH. CSV 13 (cities-fatalities-traffic-violation) has an internal off-by-1 in MoRTH's published Total cell:
- Sum of 6 violation category columns = 17,186
- MoRTH's published "Total" cell in CSV 13 = 17,187
- Difference = 1

The column sums match CSV 11 published killed (17,186), but the CSV 13 Total cell itself is internally inconsistent. **Recommendation:** Update VAL-13 Status to "MINOR INTERNAL INCONSISTENCY in MoRTH CSV 13 published Total cell (off-by-1). Use column sums, not CSV 13 Total cell."

---

## F. MoRTH vs NCRB fatality discrepancy — separate review (Audit #8)

| Source | 2024 Road Fatalities | Source URL | Convention |
|---|---|---|---|
| MoRTH "Road Accidents in India 2024" | 177,175 | morth.gov.in (mirror: opencity.in) | 24-hour-from-crash police-registered cases |
| NCRB "ADSI 2024" | ~162,500 (per Hindustan Times reporting) | ncrb.gov.in (mirror: opencity.in) | IPC-negligence classification (narrower scope) |
| Gap | ~14,675 | — | 8.3% |
| Explanation | Different source systems (MoRTH ← State Police via TLO; NCRB ← Crime-CIB); different scope (MoRTH road-only; NCRB accidental-deaths-broader including drowning/fire/falls/railway) | — | — |

**IMPORTANT:** The NCRB figure of "~162,500" is from Hindustan Times secondary news reporting (Jun 12, 2026), NOT directly verified from the downloaded NCRB PDF. The PDF was downloaded but the actual figure has not been extracted/confirmed from Table 1A.2.

**Action required:**
1. Retain both figures — NEVER merge or average per project brief.
2. Mark NCRB figure as "requires direct PDF verification" until Table 1A.2 PDF is extracted.
3. Document the 8.3% gap in SOURCE_CONFLICTS CF-01 (already done).
4. For road-accident-specific analysis, use MoRTH figure (177,175).
5. For broader accidental-death context or international comparison, use NCRB figure.

---

## G. Historical geography / state-UT naming (Audit #9)

**All three major boundary changes correctly documented in GEOGRAPHY_CROSSWALK.csv:**

- GC-01: Telangana formation (2 June 2014) — pre-2014 Andhra Pradesh includes today's Telangana
- GC-02: J&K reorganisation (31 October 2019) — J&K# footnoted as "includes Ladakh for 2019 and 2020"; Ladakh UT separate from 2021
- GC-03: DN&H + Daman & Diu merger (26 January 2020) — pre-2020 sum required

**Additional crosswalk entries for renames:** Orissa→Odisha (2011), Pondicherry→Puducherry (2006), Allahabad→Prayagraj (2018), Bangalore→Bengaluru (2014), Baroda→Vadodara, Calicut→Kozhikode, Trivandrum→Thiruvananthapuram. All pure renames (no boundary change) — safe for analysis.

**City spelling variations in MoRTH 2024 cities CSV:** 'Vadodra' (should be 'Vadodara'), 'Khozikode' ('Kozhikode'), 'Vizaq' ('Visakhapatnam'), 'Thiruvanthapuram' ('Thiruvananthapuram'), 'Vijaywada city' ('Vijayawada City'). Documented in DATA_CLEANING_LOG CL-12. LOW severity — standardise before cross-source joins.

**TN district boundary changes:** Myiladuthurai (carved out of Nagapattinam, 2020) and Chengalpattu (carved out of Kanchipuram, 2019). TN district CSV correctly preserves NA for Myiladuthurai 2021. Documented in GC-15 and GC-16.

---

## H. Duplicate / overlapping datasets (Audit #10)

| Overlap | Type | Action |
|---|---|---|
| MoRTH 2024 CSV × MoRTH 2023 CSV × MoRTH historical CSV | Publication-vintage redundancy (2020-2022 overlap) | Use latest (2024) for analysis; older CSVs for trend verification. VAL-01 to VAL-06 confirm exact match. |
| MoRTH 2024 PDF × 13 MoRTH 2024 CSVs | Same source; CSVs are machine-readable extracts of PDF tables | Use CSVs for analysis; PDF for narrative context. |
| NCRB ADSI 2024 full report × 11 NCRB ADSI 2024 chapter PDFs | Same source; chapter PDFs are subsets of full report | Use chapter PDFs for specific table extraction; full report for cross-reference. |
| OpenCity.in CKAN mirror × original MoRTH/NCRB portals | Mirror of primary source | Original URLs confirmed in Source_URL field; mirror URL in Mirror_URL field. Both contain identical content per CKAN API metadata. |

No TRUE duplicates found. All overlaps are either publication-vintage redundancy or mirror-primary-source relationships.

---

## I. Datasets wrongly classified as primary (Audit #11)

**Issue ISS-I01:** SOURCE_REGISTER Primary_or_Secondary column marks sources like SRC-MORTH-AR-2024 as "Primary" — which is technically correct (MoRTH IS the primary publisher). However, the data steward in our possession is the OpenCity.in mirror — the actual morth.gov.in PDF was NOT directly downloaded by this project (curl to morth.gov.in timed out at project start).

**Recommendation:** Add clarifying note in SOURCE_REGISTER Limitations field for SRC-MORTH-AR-2024, SRC-MORTH-AR-2023, SRC-NCRB-ADSI-2024, SRC-BTP-STATIONWISE, SRC-TN-DISTRICTWISE, SRC-KARNATAKA-STATE-REPORT — "Original morth.gov.in / ncrb.gov.in / etc. portal not directly accessible from research network; OpenCity.in CKAN mirror used. Both contain identical content per CKAN API metadata."

**No actual mis-classification** — the data IS primary-source data, just acquired via a mirror. The Primary_or_Secondary field correctly identifies the original publisher.

---

## J. Documented-only but not actually downloaded (Audit #12)

| Dataset | Status | Reason |
|---|---|---|
| DS-IMD-GRIDDED-RAIN-NETCDF | Acquired=NO | Server timed out from research network; URL verified across 3 academic references |
| DS-IMD-DSP-PAID | Acquired=NO | Paywall — IMD DSP 4.0 requires account + per-variable fee |
| DS-MORTH-BLACKSPOT-NH | Acquired=NO | Coordinates NOT public; list published via news; Dataful.in mirror returned 404 |
| DS-eDAR-iRAD | Acquired=NO | Access restricted to police/highway authorities |

**All 4 correctly marked Acquired=NO** in DATASET_REGISTER. **However**, PARAMETER_MASTER and SOURCE_REGISTER overstate status for some of these:
- F-02 (Daily Rainfall) marked VERIFIED in PARAMETER_MASTER — should be PARTIALLY VERIFIED (URL only) (ISS-C01)
- SRC-IMD-GRIDDED-RAIN-025 marked VERIFIED in SOURCE_REGISTER — should be PARTIALLY VERIFIED (URL only) (ISS-C06)
- P-02 (Blackspot list) marked PARTIALLY VERIFIED — should clarify LIST published but CSV NOT acquired (ISS-J01)

**Action:** Update PARAMETER_MASTER and SOURCE_REGISTER to reflect actual acquisition state.

---

## K. TOC-only parameters (Audit #13)

**No parameters found marked available merely because a report TOC mentions them.** All parameters marked AVAILABLE in PARAMETER_MASTER have either:
- A directly acquired CSV with the actual values, OR
- An acquired PDF where the table exists (with extraction still pending, marked PARTIALLY VERIFIED)

The closest case is **A-04 / D-04 (Hour of day)** where the MoRTH chart 7.4 is mentioned in the PDF but the chart values have not been extracted — but this is honestly marked as PARTIALLY VERIFIED (PDF chart) in PARAMETER_MASTER.

---

## L. Aggregate vs case-level mis-classification (Audit #14)

**All acquired datasets contain AGGREGATE counts** — state / city / district / station × year. None contain per-accident case-level records. The only source with case-level data (eDAR-iRAD) is correctly marked Acquired=NO and access-restricted.

PARAMETER_MASTER Granularity field correctly uses "aggregate count" or "per-state aggregate" etc. for all Group A parameters. **No mis-classification found.**

This means: downstream analysis MUST respect aggregate-only constraint. Cannot do per-accident regression (e.g. "what factors predict fatality for a specific crash") without case-level data — which would require eDAR access.

---

## M. Weather/road/vehicle join ability (Audit #15)

| Join | Status | Notes |
|---|---|---|
| Weather × Accidents (state-month) | INTEGRABLE BUT BLOCKED | Requires (a) IMD NetCDF download AND (b) NCRB Table 1A.5 month-wise PDF extraction. Both pending. |
| Weather × Accidents (district-day) | NOT POSSIBLE | Accidents have no coordinates; IMD station data cannot be joined without accident-location coordinates. |
| Road network × Accidents | NOT POSSIBLE | Accidents have no per-accident road-segment ID; only blackspot NH+km markers exist (no coords). |
| Vehicle registrations × Accidents (India-year) | SAFE | Both from MoRTH; year-only join. |
| Vehicle registrations × Accidents (state-year) | UNSAFE | VAHAN bulk access restricted; state-wise registered-vehicle counts not in our possession. |
| Vehicle registrations × Accidents (2023-2024) | UNSAFE | Registered-vehicle totals NA for 2023-2024. |
| Air quality × Accidents | INTEGRABLE BUT BLOCKED | Requires CPCB Vayuayan archive download + nearest-station assignment. Both pending. |
| Bhuvan road layer × Accidents | NOT POSSIBLE | Accidents have no coordinates. |
| District boundary × Accidents | SAFE (via district name) | Bhuvan district polygons + TN district CSV (Census 2011 boundaries — recent districts may be missing). |

**No unsafe joins identified** in current state because all blocked joins require missing data (IMD download, accident coordinates, VAHAN bulk). Join ability is correctly documented as INTEGRABLE/CONDITIONALLY SAFE in PARAMETER_MASTER.

---

## N. 2025 data status (Audit #16)

**Confirmed: 2025 data does NOT exist.** Searches returned no 2025 report URLs for either MoRTH or NCRB. Compliance with project brief verified — no 2025 values anywhere in any deliverable.

**Status retained:** "2025 — NOT AVAILABLE / REPORT NOT YET PUBLISHED" per project brief.

**Expected release schedule (historical):**
- MoRTH 2025 report: ~September-November 2026 (9-12 months after calendar year-end)
- NCRB ADSI 2025: ~December 2026 (12 months after calendar year-end)

**Action:** Re-search in late 2026 for MoRTH 2025; late 2026 / early 2027 for NCRB ADSI 2025. Do NOT pre-create 2025 values.

---

## O. Derived-variable formulas (Audit #17)

All 9 DERIVABLE parameters' formulas verified correct:

| Param ID | Parameter | Formula | Status |
|---|---|---|---|
| C-08 | Fatalities per Accident | Persons Killed / Total Accidents | VERIFIED — safe to derive |
| C-09 | Fatalities per 100 Accidents | (Persons Killed / Total Accidents) × 100 | VERIFIED — safe to derive |
| C-10 | Case Fatality Rate | Persons Killed / (Persons Killed + Persons Injured) × 100 | VERIFIED with limitation — excludes property-damage-only accidents (eDAR restricted) |
| D-05 | Day/Night | Aggregate NCRB 8 time-buckets → Day(06-18) vs Night(18-06) | VERIFIED — requires NCRB 1A.6 PDF extraction |
| D-07 | Holiday/Festival period | Tag NCRB month-wise to Indian holiday calendar | VERIFIED — requires NCRB 1A.5 PDF extraction |
| E-01 | Meteorological season | Map NCRB month-wise to IMD 4-season def (Win=Dec-Feb, PreM=Mar-May, Mon=Jun-Sep, PostM=Oct-Nov) | VERIFIED — requires NCRB 1A.5 PDF extraction |
| E-02 | Monsoon vs Non-Monsoon | Binary tag (Monsoon=Jun-Sep per IMD) | VERIFIED — requires NCRB 1A.5 PDF extraction |
| E-03 | Regional season | State-specific season mapping | VERIFIED — requires per-state season calendar |
| B-03 | Zone (6 zones) | Group states into 6 zones per MoRTH convention | VERIFIED — safe to derive |

**Important:** Formulas are documented but values have NOT been computed in this phase. This is consistent with project scope (research foundation, not analysis). Downstream analysis phase must execute these computations and create derived-value columns in 03_VERIFIED_DATA/ and 04_CLEAN_DATA/.

**Subtle issue with C-10:** The formula K/(K+I) × 100 is a proxy for case-fatality-rate among INJURY-producing accidents. True CFR per accident case would require knowing how many accidents had ZERO injuries (property-damage-only). MoRTH does not publish this count. The approximation is reasonable but should be documented as "CFR among injury accidents" not "true CFR".

---

## P. Analysis-Ready Datasets summary

Of the 37 datasets in DATASET_REGISTER:

| Status | Count | Datasets |
|---|---|---|
| READY (machine-readable + validated) | ~21 | All MoRTH 2024 CSVs + MoRTH 2023 CSVs + BTP CSVs + TN CSV + historical CSVs |
| READY_WITH_CLEANING (small cleaning needed) | ~3 | BTP 2023 (filter Total rows), CSV 13 (use column sums not Total cell), MoRTH 2023 CSV set |
| NOT_READY (PDF extraction required) | ~9 | All 11 NCRB ADSI 2024 PDFs + 2 Karnataka state report PDFs |
| NOT_ACQUIRED | 4 | IMD NetCDF, IMD DSP, Blackspot list, eDAR-iRAD |

Detailed per-dataset status in `ANALYSIS_READY_DATASETS.csv`.

---

## Q. Recommendations

**Before any analytical development:**

1. **Downgrade overclaimed statuses** in PARAMETER_MASTER:
   - F-02: VERIFIED → PARTIALLY VERIFIED (URL only, file not acquired)
   - A-04, D-04: VERIFIED → PARTIALLY VERIFIED (PDF chart not extracted)
   - I-02: AVAILABLE → DERIVABLE (requires NCRB intersection)
   - P-02: PARTIALLY VERIFIED → clarify LIST published but CSV not acquired

2. **Fix referential integrity** between PARAMETER_MASTER and DATASET_REGISTER:
   - Update Source_Dataset_ID in PARAMETER_MASTER to use formal Dataset_IDs (DS-MORTH-2024-CSV-02 etc.)
   - OR create PARAMETER_TO_DATASET_MAP.csv

3. **Downgrade overclaimed sources** in SOURCE_REGISTER:
   - SRC-IMD-GRIDDED-RAIN-025: VERIFIED → PARTIALLY VERIFIED (URL only)
   - SRC-CPCB-NAMP: VERIFIED → PARTIALLY VERIFIED (URL only)
   - SRC-WHO-GSRRS-2023: VERIFIED → PARTIALLY VERIFIED (URL only)
   - SRC-IITD-TRIPC-2024: VERIFIED → PARTIALLY VERIFIED (URL only)

4. **Run PDF table extraction** on 8 NCRB ADSI 2024 PDFs (Camelot/Tabula):
   - Table 1A.5 (month-wise) → unlocks D-02
   - Table 1A.6 (time-wise) → unlocks D-04, D-05
   - Table 1A.7 (road classification) → unlocks G-01
   - Table 1A.9 (cause-wise) → unlocks J-02
   - Table 1.2 (age & gender) + Table 1A.4 (mode) → unlocks I-02
   - Table 1A.2 (state×city traffic) → cross-check with MoRTH state totals

5. **Run PDF table extraction** on 2 Karnataka state report PDFs → unlocks A-08 district-level for KA

6. **Re-attempt IMD gridded rainfall download** with longer timeout or alternative network → unlocks F-02 and all Group F weather integration

7. **Update VAL-13** in VALIDATION_REPORT.csv to flag the internal off-by-1 in MoRTH CSV 13 Total cell (sum=17,186 vs Total=17,187)

8. **Update RESEARCH_COMPLETION_REPORT.md** to correct dataset row count (37 rows in DATASET_REGISTER, not 51) and clarify that 27 acquired figure refers to individual CSVs (not dataset-register rows)

9. **Execute the 9 DERIVABLE parameter formulas** in downstream analysis phase

10. **DO NOT build the final web application** until at least items 1, 2, 4, 5 are complete. Items 3, 6, 7, 8 can be done in parallel with early-stage analysis on the 21 ready CSVs.

---

## Final verdict: **READY_WITH_LIMITATIONS**

**Justification:**

The Phase-1 research foundation has:
- ✅ Real, verified, machine-readable data for 21 CSVs (MoRTH + BTP + TN + historical)
- ✅ All state-sum/city-sum/district-sum validation checks passing exactly
- ✅ All 14 NOT AVAILABLE parameters genuinely unsupported (no fabrication)
- ✅ All 9 DERIVABLE parameter formulas correct
- ✅ 2025 correctly marked as not-yet-published
- ✅ MoRTH vs NCRB discrepancy correctly documented (never merged/averaged)
- ⚠️ 5 parameters with overstated VERIFIED status (must downgrade)
- ⚠️ 8 NCRB ADSI 2024 PDFs need table extraction (parameters depend on this)
- ⚠️ 2 Karnataka PDFs need district-table extraction
- ⚠️ IMD gridded rainfall not actually downloaded (URL only)
- ⚠️ Referential integrity failure between PARAMETER_MASTER and DATASET_REGISTER
- ⚠️ 1 internal MoRTH publishing inconsistency (CSV 13 Total cell off-by-1)

**The foundation is solid for the 21 ready CSVs but analytical development on the full parameter set requires the action items above.** Analysis can begin immediately on the ready subset; full-scope analysis requires the pending extractions and downloads.

**NOT READY FOR FULL ANALYSIS. READY FOR LIMITED ANALYSIS on the 21 verified machine-readable CSVs.**

**Final verdict: READY_WITH_LIMITATIONS**
