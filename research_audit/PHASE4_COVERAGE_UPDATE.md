# Phase 4 coverage update (2026-09-28; supplements, never overwrites, Phase 3 audit)

- D-02 Month: UNAVAILABLE → PARTIAL. NCRB ADSI Table 1A.5 2024 Road-states extracted
  (02_VERIFIED_DATA/phase4/ncrb_monthwise_traffic_accidents_2024.csv). NCRB vintage kept
  separate from MoRTH; no MoRTH monthly exists.
- B-04 District: UNAVAILABLE → PARTIAL. TN 38 districts 2021-23 verified against benchmark
  (01_RAW_DATA/phase4/tamilnadu_district/). Single-state evidence only.
- A-03 Time bucket: PARTIAL → PARTIAL (NCRB Table 1A.6 PDF discovered, not downloaded).
- F-04 State vehicle split: PARTIAL → DISCOVERED (OGD RTYB 2010-2020; download pending API key).
- 2014-2017 state panel: UNAVAILABLE → DISCOVERED PDF-only (AR PDFs located, extraction pending).
- A-01 Accident ID/coords: UNAVAILABLE → ACCESS-RESTRICTED (eDAR confirmed authority-only).
- J-04 Humidity/visibility/fog/wind: UNAVAILABLE → confirmed NOT AVAILABLE (IMD grids temp/rain only).

Nothing merged into the benchmark. Full detail: research_acquisition/PHASE4_DATA_GAP_REPORT.md.
