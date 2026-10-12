# A Multi-Level Data-Driven Analysis of Road Traffic Accidents in India: Geographical, Temporal, Seasonal, Environmental and Severity Assessment
## FINAL B.TECH RESEARCH REPORT (submission draft)

TITLE PAGE — [Candidate Name], [Roll No.], Department of [___], [Institute], 2026.
DECLARATION — The candidate declares this work is original and sources are acknowledged. [Signature/placeholders]
CERTIFICATE PLACEHOLDER — [Guide name, designation, signature, department seal.]
ACKNOWLEDGEMENT — [Candidate to complete: guide, department, MoRTH/NCRB/IMD data publishers, OpenCity mirror.]

## ABSTRACT
See FINAL_ABSTRACT.md (Background/Objective/Methods/Results/Conclusion/Keywords; verified numbers only).

## KEYWORDS
road safety India; MoRTH; accident severity; weather association; persistence baseline; K-means typology.

## TABLE OF CONTENTS / LIST OF FIGURES / LIST OF TABLES / ABBREVIATIONS
- Figures: FINAL_FIGURE_LIST.csv (16 planned). Tables: FINAL_TABLES.md (15). Abbreviations: MoRTH,
  NCRB, ADSI, IMD, CMPG, ABDB, RGI, BRSI, TRW, OLS, FDR, BH, RMSE, MAE, KNN.

## CHAPTER 1 — INTRODUCTION
1.1 Background: India records ~0.48M accidents and ~0.18M deaths yearly (2024: 487,707 / 177,175).
1.2 Problem: counts without exposure denominators; fragmented vintages; no microdata.
1.3 Research gap: prior work rarely reconciles vintages, geographies, and missing exposure jointly.
1.4 Motivation: evidence-linked analytics + reusable upload platform.
1.5 Research question: "How do geographical, temporal, seasonal, environmental, roadway, vehicle and
    other available factors influence the occurrence and severity of road traffic accidents across
    India?" — read observationally ("associated with"), never causally.
1.6 Objectives 1-13 (per brief Part 4).
1.7 Scope: 2018-2024 benchmark; conditional history; NCRB/IMD/supporting layers kept separate.
1.8 Contributions: 10 supported items (PHASE10_CONTRIBUTIONS.md).
1.9 Limitations: vehicle stock, microdata, monthly MoRTH, N=213 panel (PHASE10_LIMITATIONS_MATRIX.csv).
1.10 Organization: Ch2 data/design; Ch3 methods; Ch4 results; Ch5 discussion; Ch6 limitations;
    Ch7 contributions; Ch8 recommendations; Ch9 future work; Ch10 conclusion.

## CHAPTER 2 — DATA SOURCES AND STUDY DESIGN
2.1 Framework: benchmark -> harmonization -> normalization -> weather -> statistics -> ML -> synthesis.
2.2 MoRTH benchmark: 254 state-years, 38 entities, 0 mismatches (MoRTH_Primary_Dataset_3.xlsx CLEAN).
2.3 NCRB: ADSI 2024 Table 1A.5 monthly, separate vintage (467,967 vs 487,707 gap documented).
2.4 IMD: CMPG daily grids -> state means (236 matched / 18 excluded; <=0.6% weighting sensitivity).
2.5 Supporting: 7 AR-2024 modules via OpenCity mirror (VERIFIED-MIRROR, reconciled).
2.6 TN districts 2021-23 (sums == benchmark). 2.7 AR2017 2014-17 candidate (144 rows, 12/12 MATCH,
    CONDITIONAL). 2.8-2.13: provenance files, validation summaries, cleaning log (no silent edits),
    year-aware geography, calendar-year temporality, full missingness maps (research_audit/).

## CHAPTER 3 — METHODOLOGY
Per PHASE10_METHODOLOGY.md (3.1-3.21): descriptives/YoY; OLS slopes N=7 + CI; Pearson+Spearman;
chi-square; Friedman (years as blocks); BH-FDR; lag-only ML (train 2019-22 N=141, test 2023-24 N=72)
with naive baseline + rolling-origin validation; K-means standardized profiles K=2-6 (K=2 selected);
leakage audit (4 exclusions); seed 42; scripts preserved.

## CHAPTER 4 — RESULTS
Per PHASE10_RESULTS_SECTION.md 4.1-4.11 (exact values; association language). Key test figures:
2023-2024 holdout, accident baseline RMSE 1038.6, K=2 silhouette 0.356.

## CHAPTER 5 — DISCUSSION
Per PHASE10_DISCUSSION_SECTION.md (5.1-5.11 mapped to file sections).

## CHAPTER 6 — LIMITATIONS
Per PHASE10_LIMITATIONS_MATRIX.csv (exposure, microdata, granularity, weather, injuries, history, ML N, vintages).

## CHAPTER 7 — CONTRIBUTIONS
Per PHASE10_CONTRIBUTIONS.md.

## CHAPTER 8 — RECOMMENDATIONS
Per PHASE10_RECOMMENDATIONS.md (A data-system, B research, C analytical, D technology).

## CHAPTER 9 — FUTURE WORK
Per PHASE10_FUTURE_WORK.md (10 prioritized acquisitions).

## CHAPTER 10 — CONCLUSION
Per PHASE10_CONCLUSION.md (RQ1-RQ11 answered from evidence).

## REFERENCES
See FINAL_REFERENCES.md (no invented citations; mirrors labeled as mirrors).

## APPENDICES
A: data dictionary (DATA_DICTIONARY in benchmark + supporting schemas). B: availability matrix
(MASTER_PARAMETER_AVAILABILITY.csv). C: statistical results (Phase 7/8 CSVs). D: ML results
(PHASE9_MODEL_RESULTS/PREDICTIONS/BASELINE_COMPARISON). E: clustering (K_SELECTION/RESULTS/PROFILES).
F: OriginPro graph plans. G: reproducibility (seeds, scripts, PHASE10_REPRODUCIBILITY_AUDIT.csv).
