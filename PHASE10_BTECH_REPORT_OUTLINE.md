# B.Tech Report Outline — chapter→evidence map

TITLE / CERTIFICATE / DECLARATION / ACKNOWLEDGEMENT / ABSTRACT (see vintage notes) / TOC / FIGURES (FIG-01..12) / TABLES (Table_1..15) / ABBREVIATIONS.

## Ch.1 Introduction
1.1 Background (F01–F03) · 1.2 Problem · 1.3 Motivation · 1.4 Gap (vehicles/monthly/cause absent) · 1.5 Questions (core Q, §25 objectives) · 1.6 Objectives · 1.7 Scope (2018–24, state-year) · 1.8 Contributions (§16 list).

## Ch.2 Literature review
Sections 2.1–2.9 as specified — NO invented citations; student fills from library with the gap: exposure-normalized, boundary-aware weather + severity on verified MoRTH panel.

## Ch.3 Data & methodology
3.1 Framework (pipeline §6) · 3.2 Sources (Table_1) · 3.3 Verification (P1 audit, 0 mismatches) · 3.4 Cleaning (types, dupes, NV handling) · 3.5 Geography (vintage notes) · 3.6 Pop normalization (RGI projections!) · 3.7 Road normalization (2021–22 only) · 3.8 Weather (IMD+SOI, equal-cell, Status B) · 3.9 Stats (OLS/FDR/FE/2020 sens) · 3.10 Severity (Sev100 definition) · 3.11 ML (lag-only, chronological, naive mandatory) · 3.12 Validation (all phase validation MDs) · 3.13 Reproducibility (guide below).

## Ch.4 Results
4.1 India (Table_3, FIG-01..04) · 4.2 Zones (Table_4, FIG-05) · 4.3 States (Table_5, FIG-06) · 4.4 Temporal (2020 break) · 4.5 Pop-normalized (Table_6) · 4.6 Road (Table_7) · 4.7 Weather (Table_8–10, FIG-07..09; pooled vs within vs FE) · 4.8 Severity (Table_11–12, FIG-10..11) · 4.9 Injury (Table_13, coverage!) · 4.10 ML (Table_14, FIG-12, naive wins).

## Ch.5 Discussion
Findings → interpretation (association language only) → literature comparison (student) → implications (no causal prescriptions beyond data).

## Ch.6 Limitations & future work (§19 lists; §28 datasets).

## Ch.7 Conclusion (FINAL_RESEARCH_FINDINGS.csv F01–F13 + §27 five-way split).

## Appendices
A data dictionary (phase dictionaries) · B source verification (manifests) · C validation reports (all PHASE*_VALIDATION.md) · D OriginPro tables (all PHASE* workbooks) · E additional results (CSVs) · F reproducibility (below).

# Reproducibility guide (condensed)
Structure: phase*_raw/ (immutable) + phase CSVs + phase*.py scripts + PHASE*.xlsx/MD. Hashes: RGI/BRSI/IMD/SOI manifests. Order P1→P10; each script reads prior outputs only. OriginPro: open listed workbook/sheet, X/Y per figure map. ML: phase5_ml_analysis.py (chronological, seed noted). Weather: phase6→phase7→final-validation scripts. Exclusions: Join_Status / Quality_Status flags. Gaps: §5 matrix; never fill NV.
