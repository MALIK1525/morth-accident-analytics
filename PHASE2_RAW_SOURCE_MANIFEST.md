# PHASE 2A — RAW SOURCE MANIFEST (acquisition only; no parsing/joining/normalization done)

## 1. Population — ACQUIRED
- File: `phase2_raw/population/RGI_Population_Projection_2011-2036.pdf`
- SHA-256: `bf867a344d5eead958235dd03c75a3fc2a39187072f6ddedcbab3cc3720e8417`
- Source: Report of the Technical Group on Population Projections (RGI chair), National Commission on Population
- Publisher: Ministry of Health and Family Welfare (mirror host: mohfw-dohfw.gov.in; original mohfw.gov.in URL now 404)
- Publication date: July 2020. URL: https://www.mohfw-dohfw.gov.in/static/uploads/2025/10/1c3c2048814bd3747f44e661f8547055.pdf
- Tables: Table 8 (projected total pop. by sex, 1 March), Table 11 (1 July), Table 14 (1 Oct), 2011–2036; 270 pages; tables located (pp. ~49–135).
- Coverage: 2011–2036 (2018–2024 slice usable). Geography: India + States/UTs; Telangana separate; Ladakh separate; J&K listed as "JAMMU & KASHMIR (UT)"; Daman & Diu and Dadra & Nagar Haveli SEPARATE (pre-merger structure).
- Unit: thousands (’000). Definition: PROJECTIONS (Census-2011-based cohort component), NOT census counts — must never be renamed "population counts".
- Download date: 2026-09-26. Verification status: FILE VERIFIED (real PDF, tables located); values NOT yet extracted/validated.
- Limitations: projections drift from reality post-2020 (no Census 2021 held); J&K pre-2019 combined in base; DNH/Diu pre-merger — year-aware mapping required; 1 Mar vs 1 Jul vs 1 Oct vintage must be chosen once and documented.

## 2. Registered vehicles — NOT ACQUIRED FROM VERIFIED SOURCE
- Attempts: MoRTH RTYB direct PDF (morth.nic.in → SPA shell, blocked); data.gov.in RTYB group (JS-only, no extractable resources); data.gov.in catalog API (404); web search (no official mirror; CEIC paywalled/secondary — REJECTED as non-authoritative).
- Tables sought: RTYB Annex 3.1/3.2 (state-wise registered vehicles). Status: still missing.
- Note: even when acquired, registration totals include dead/non-operational vehicles in some states — not active-vehicle counts.

## 3. Road length — ACQUIRED (single edition)
- File: `phase2_raw/road_length/BRSI_2020-22.pdf`
- SHA-256: `3288df12fb15571bfcdbcd388befe36e2cf7fdc07bf794024906e242fda73a9a`
- Source: Basic Road Statistics of India 2020–22. Publisher: MoRTH (Transport Research Wing), via morth.gov.in backend documents.
- Publication URL: https://morth.gov.in/backend/documents/uploaded/1781850176_EDsilQvsKL.pdf
- Tables: Annexures 1.x (as on 31.03.2021) + 2.x (as on 31.03.2022); state-wise tables located (e.g. 1.3.1 State Highways, 1.4.1 District Roads, 1.5.1 Rural Roads; India totals 63.36 lakh km 2021 → 64.98 lakh km 2022).
- Coverage: reference dates 31.03.2021 + 31.03.2022 ONLY — not 2018–2024. Geography: State/UT-wise per edition (UT-merger handling to be checked at extraction).
- Unit: km. Definition: total + surfaced length by category (NH/SH/district/rural/urban/project).
- Download date: 2026-09-26. Verification status: FILE VERIFIED; values NOT yet extracted/validated.
- Limitations: CRITICAL — some state cells carry footnotes "* as on 31.03.2018 / # 2019 / @ 2020" (stale carry-forward); editions must never be mixed; single edition cannot support 2018–2024 trends.

## Geography issues (documented, not resolved)
- RGI: separate DNH + Diu vs MoRTH merged DNH-DD (2020+); RGI J&K(UT)+Ladakh vs MoRTH J&K+Ladakh rows; Telangana present in both. Year-aware mapping required at parse phase.
- BRSI: edition-specific UT structures; stale-data footnotes per state.

## Provenance
Original filenames preserved under edition-descriptive names; hashes recorded BEFORE any parsing.
No values extracted, joined, or normalized in this phase. Production website untouched.
