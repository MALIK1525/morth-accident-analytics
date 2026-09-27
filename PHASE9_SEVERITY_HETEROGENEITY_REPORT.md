# PHASE 9 — Severity & Heterogeneity Report (descriptive/inferential; no causal claims)

## India severity
Fatalities per 100 accidents: 33.50 (2018) → 37.18 (2020) → 37.33 (2021) → 36.52 (2022) → 35.98 (2023) → 36.33 (2024).
Absolute 2018→2024: +2.83 points (+8.4%). Pattern: rise through 2021, partial retreat, net higher — not a monotone trend.
Fatalities/lakh population rose 11.90 → 12.61; accidents/lakh fell-then-recovered 35.51 → 34.71. Raw deaths (+12.4%) outpaced accidents (+3.7%): severity and scale moved differently.

## Zone heterogeneity
Six zones computed (phase9_zone_severity.csv, G-P9-04/05 specs in workbook). No rankings. Between-zone severity gaps persist all years; see workbook.

## State severity (no rankings)
Full 38-entity table (phase9_state_severity_summary.csv). Cross-state CV ≈ 0.48–0.55 every year — stable, wide heterogeneity.

## State slopes + FDR
36 entities eligible (N≥4); Ladakh/Lakshadweep ZERO_VARIANCE (constant severity, p undefined, excluded from FDR family); 2 legacy rows INSUFFICIENT_N.
34 tested; **9 survive BH-FDR**: 8 with positive slopes (Andaman & Nicobar +2.20, Andhra Pradesh +1.69, Assam +1.25, Bihar +1.90, Chhattisgarh +2.32, Gujarat +1.16, Jharkhand +2.07, Madhya Pradesh +0.76 per year) and Kerala negative (−0.49/yr). All N=7: low power, CIs wide — reported, not ranked.

## 2020 sensitivity
3 entities flip slope sign excluding 2020 (merged DNH-DD N=5, Delhi, UP — all near-zero slopes, p>0.6 either way). No material severity-trend distortion from 2020.

## Injury analysis (coverage-bounded)
179 verified state-years (2018–2022 only); 2023–24 state injuries NOT AVAILABLE (75 missing cells, never filled). Injuries/100 accidents + injuries/lakh in phase9_injury_state_year.csv; coverage table phase9_injury_coverage.csv.

## Raw vs normalized
Raw fatalities = total deaths; Sev100 = severity conditional on recorded accidents; FatLakh = population burden. India 2018→24: deaths +12.4%, Sev100 +2.83 pts, FatLakh +0.71 — three different answers to three different questions; none universally superior.

## Weather–severity (exploratory, N=233 matched)
Rainfall–Sev100 r=-0.058 (p 0.38); Tmax r=+0.002 (p 0.98); Tmin r=-0.069 (p 0.29): **insufficient evidence** of any weather–severity association. (Tmin Spearman p 0.025 uncorrected — not significant under any family correction; reported as non-finding.)

## Conclusion
Severity rose-then-eased but ended higher (36.33 vs 33.50); heterogeneity across states is wide and stable; 9 states show FDR-robust severity slopes (8 rising, 1 falling); injuries analyzable only to 2022; weather shows no detectable severity association. All associations observational.
