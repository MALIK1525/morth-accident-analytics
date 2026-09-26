# RESEARCH ANALYSIS PHASE 1 — REPORT
Source: `data/MoRTH_Primary_Dataset_3.xlsx` via `app/data_pipeline/loader.py`. No synthetic data. No website changes.

## 1. Dataset audit
- Entities: 38 (incl. merged DNH-DD row + 2 legacy rows with N<7). Observations: 254 state-years. Years: 2018–2024.
- Missing: Accidents 0, Fatalities 0, Injured 75 (all 2023/2024 state cells + scattered UT cells; 2020 has 35/38 reporting).
- Duplicates: 0. Unmapped zones: none (6-zone mapping complete, each state exactly one zone).
- Naming notes: "Dadra & Nagar Haveli" (N=2, pre-merger), "Daman & Diu" (N=2, pre-merger), "Dadra & Nagar Haveli and Daman & Diu" (N=5, post-merger). Ladakh 2018 accidents = 0 (flagged, kept as-is).

| Variable | Years | Level | Missingness | Source | Status |
|---|---|---|---|---|---|
| Accidents | 2018–2024 | State/UT | 0/254 | MoRTH panel | VERIFIED |
| Fatalities | 2018–2024 | State/UT | 0/254 | MoRTH panel | VERIFIED |
| Injured | 2018–2022 state; 2018–2024 India | mixed | 75/254 (state cells) | MoRTH panel | PARTIAL (state), VERIFIED (India) |
| Zone | all | derived mapping | 0 | project mapping | DOCUMENTED |
| Fatalities/100 acc | derived | any | 0 | Acc/Fat | DERIVED, formula stated |
| Exposure/weather/road/vehicle/driver/cause/collision/city | — | — | 100% | none in deployment | NOT AVAILABLE |

## 2. Verified coverage
Benchmarks (all match panel sums exactly, 0 mismatch): Acc 470403/456959/372181/412432/461312/480583/487707; Fat 157593/158984/138383/153972/168491/172890/177175; Inj (India) 464715/449360/346747/384448/443366/462825/471441.

## 3–7. India annual / YoY / severity / regression
| Year | Acc | YoY% | Fat | YoY% | Inj | YoY% | Fat/100 |
|---|---|---|---|---|---|---|---|
| 2018 | 470403 | — | 157593 | — | 464715 | — | 33.50 |
| 2019 | 456959 | −2.86 | 158984 | +0.88 | 449360 | −3.30 | 34.79 |
| 2020 | 372181 | −18.55 | 138383 | −12.96 | 346747 | −22.84 | 37.18 |
| 2021 | 412432 | +10.81 | 153972 | +11.27 | 384448 | +10.87 | 37.33 |
| 2022 | 461312 | +11.85 | 168491 | +9.43 | 443366 | +15.33 | 36.52 |
| 2023 | 480583 | +4.18 | 172890 | +2.61 | 462825 | +4.39 | 35.98 |
| 2024 | 487707 | +1.48 | 177175 | +2.48 | 471441 | +1.86 | 36.33 |
Overall 2018→2024: Acc +17,304 (+3.68%); Fat +19,582 (+12.42%); Fat/100 +2.83 points.
OLS (Year as numeric, N=7): Acc slope +6,724.68/yr, R² 0.1217, p 0.4432 → APPROX_STABLE (slope < 2·SE; CI −14,046…+27,496 includes 0). Fat slope +4,166.64/yr, R² 0.4694, p 0.0894 → INCREASING by threshold rule but NOT significant at α=0.05; CI includes 0. Inj slope +5,133.11, R² 0.0545, p 0.614 → APPROX_STABLE.
Interpretation: "Although the fitted fatality trend is positive, the annual series is non-monotonic with substantial year-to-year fluctuation, dominated by the 2020 dip." No causal claims.

## 8. Six-zone analysis
All zones N=7; full table in workbook sheets 05/06. Accident-slope flags: all APPROX_STABLE except Northeast DECREASING-flag (−189.32, R² 0.24, p 0.26 — not significant). Only significant slope: Central fatalities (+1,080.43, R² 0.93, p 0.00045) and East fatalities (p 0.018). No best/worst ranking. Shares: South largest accident share (~30%), North largest fatality share — see workbook.

## 9/11. State analysis + regression
Full tables: workbook 08/09, `phase1_state.csv`. Examples: Bihar INCREASING (slope +364.5, p 0.042); Manipur DECREASING (−49.21, p 0.031); Tamil Nadu APPROX_STABLE (+859, R² 0.07, p 0.55). DNH/Daman-Diu legacy rows INSUFFICIENT_N. Ladakh slope distorted by 2018 zero — flagged. 95% CIs included; states with R²≈0 or single-year dominance flagged in workbook notes.

## 10. Same-value/threshold analysis
First-year each state reached ≥10,000 / ≥25,000 / ≥50,000 accidents; 20 cross-state pairs with year gaps (workbook sheet 10). Neutral wording only, e.g. "Bihar reached 10,000+ in 2018; Odisha in 2018 (gap 0y)". No causal inference.

## 12. 2020 COVID period
2020 flagged structurally unusual. Split trends: post-2020 (2021–2024) Acc slope +24,509.6 (R² 0.869, p 0.068); Fat +7,400.8 (R² 0.898, p 0.0525). Pre-2020 N=2 — insufficient, reported as INSUFFICIENT, not fitted. No causal attribution to COVID.

## 13. Injury coverage
State-level verified 2018–2022 (179 states-cells with values); 2023/2024 state cells all missing → N/A, never estimated. India-level 2018–2024 complete.

## 14. Correlation (state-year panel)
Pooled N=179 complete rows: Pearson/Spearman matrices in workbook sheet 11. Acc–Fat Pearson p < 1e-6 (strong scale association). Caveat documented: pooled correlation is inflated by between-state scale differences; association only, not causation; within-state analysis recommended next phase.

## 15. Exposure
NOT AVAILABLE FROM VERIFIED DATA — no denominator files in deployment (`data/supporting_csv/` empty). No per-population/vehicle/road-length measures computed.

## 16–17. OriginPro inventory
Workbook `RESEARCH_ANALYSIS_PHASE_1_WORKBOOK.xlsx`: all 15 sheets (01–15) with units/sources/coverage/formulas. Graph-ready tables for G1–G10 (India annual, YoY, zone annual, state annual/regression/threshold, correlation).

## 18. ML readiness
Target candidate: annual state accidents (N=213 usable). Features available: Year, State, Zone, lags, YoY (documented). No leakage design yet. KNN = supervised; K-Means = unsupervised (terminology fixed). Full matrix in workbook sheet 14 + PARAMETER_FINAL_STATUS.csv. Training NOT started per instructions.

## 19. Weather/supporting
NOT AVAILABLE — no IMD files, no 13 supporting CSVs in deployment. No weather graphs computed.

## 20–21. Integrity + vintage
No synthesis/interpolation/causal claims. 2019 vintage documented: longitudinal panel uses later vintage (456,959/158,984/449,360); older report values (449,002/151,113/451,361) noted in sheet 15, never mixed.

## 22. Deliverables
This report + VALIDATION doc + workbook + `phase1_{india,zone,state}.csv` + `phase1_analysis.py` (re-runnable).
