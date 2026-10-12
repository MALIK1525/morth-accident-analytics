# Phase 4 — Acquisition Log (2026-09-28, local only, no commit/push/deploy)

1. OpenCity CKAN package_search "road accidents india" → located TN district reports,
   ADSI 2024 chapter PDFs (month-wise Table 1A.5, time-wise 1A.6), AR 2014-2017 PDFs.
2. Downloaded TN district CSV (1,729 bytes) → 01_RAW_DATA/phase4/tamilnadu_district/.
   Inspected: 38 districts + Total, 2021-23 acc/deaths. District sums == benchmark TN exactly.
3. Downloaded NCRB ADSI Table 1A.5 PDF (1,249,490 bytes, 8 pp) → 01_RAW_DATA/phase4/ncrb_adsi2024/.
   Inspected with pypdf: 4 blocks (Road/RailwayCrossing/Railway/GrandTotal) x (States/UTs/Cities).
4. Extracted 364-row verified CSV → 02_VERIFIED_DATA/phase4/. Recovered serial-less
   DAMAN & DIU UT row (144). All 4 sections reconcile exactly (Road ALL-INDIA 467,967).
5. data.gov.in OGD: RTYB 2010-2020 state-vehicles resource page confirmed (Tier 1) but
   direct CSV sits behind JS/API-key wall; api.data.gov.in SSL-timeout here. DISCOVERED, not acquired.
6. eDAR (edar.parivahan.gov.in): DNS-unresolvable from this environment; known authority-only
   portal. ACCESS-RESTRICTED, no bypass attempted.
7. IMD DSP gridded climatology: temp + rainfall only. Humidity/visibility/fog/wind: NOT AVAILABLE.
8. No application code touched. Benchmark untouched. Nothing merged.
