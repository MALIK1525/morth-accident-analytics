# PHASE 4 — INFERENTIAL STATISTICS REPORT (script: `phase4_analysis.py`; Phase 3 reproduction TRUE)

## State normalized slopes (N=7; legacy DNH/Diu N=2 → INSUFFICIENT, not estimated)
- Accidents/lakh: 7 significant before adjustment → **0 significant after BH-FDR**. Full table `phase4_state_slopes.csv`.
- Fatalities/lakh: 9 significant before adjustment → **3 significant after BH-FDR** (see sheet 11 for identities).
- Injury/lakh: valid-only N (2018–22); 2023–24 never filled. Classification POSITIVE/NEGATIVE/NEAR-ZERO + significance kept separate; no improvement/deterioration language, metric stated each time.

## India (N=7, limited power)
- Normalized accident slope +0.15/yr, p 0.81 — insufficient evidence of trend. Raw/fatality/per-100-accidents slopes in sheet 14 with N=7 caveat.

## Zones
Per-zone normalized slopes/R²/p/CI in sheet 13; reported independently, never ranked.

## Raw vs normalized
Per-state direction agreement table (sheet 05): raw counts can rise while normalized burden falls — cases documented numerically, no better/worse labels.

## Within-state associations (N≥4; N<4 marked NOT PERFORMED)
Pearson/Spearman pop↔acc and pop↔fat per state (`phase4_within_state.csv`), kept distinct from pooled Phase 3 values (0.677/0.910, 0.903/0.956, N=254 — still labeled pooled/scale-confounded).

## Road 2021–2022 (N=34 same-entity pairs; UNRESOLVED excluded)
Shapiro rejected normality → **Wilcoxon signed-rank**: Acc/1000km p≈4.7e-05; Fat/1000km p≈1.2e-04. Labeled TWO-YEAR COMPARISON, not a trend.

## Fixed effects
Spec: Acc/lakh ~ Year + state FE (within estimator, DIRECT joins, N≥3 states): N=245, 35 entities, year coef +0.028 (SE, 95% CI [−0.74, +0.79], p 0.94, within-R² in sheet 09). Interpretation: after removing state means, no within-state year association remains on average — descriptive decomposition, NOT causal identification; SEs unclustered.

## 2020 sensitivity
India normalized full-period vs 2021–24 in sheet 10; pre-2020 (N=2) declared insufficient — no pre-trend estimated. No causal attribution for 2020.

## Multiple testing / assumptions / CIs
BH-FDR per metric family; Shapiro-gated road test; t-CIs everywhere; non-significance worded as "insufficient evidence". DNH: "Insufficient evidence for a stable sensitivity conclusion" (n=5).
