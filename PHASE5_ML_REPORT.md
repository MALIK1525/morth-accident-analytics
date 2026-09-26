# PHASE 5 — ML REPORT (script: `phase5_ml_analysis.py`)

## Task / data
Target = next-year state accident count (features cutoff ≤ target−1; Pop_t assumption documented).
N=175 (35 full-panel entities × targets 2020–24; legacy 2×N=2 + merged N=5 excluded).
Features: Year, Lag1/2 Acc, Lag1/2 Fat, Pop_t, Pop_Growth, Lag1 Acc/Fat-per-lakh, Zone one-hot. No state dummies, no future, no road/vehicle/weather.

## Main split (train targets 2020–22, N=105; test 2023–24, N=70)
| Model | RMSE | MAE | R² |
|---|---|---|---|
| Naive Lag-1 | 1053.3 | 555.5 | 0.9966 |
| GradientBoosting | 1700.1 | 911.1 | 0.9911 |
| RandomForest | 2450.8 | 1196.7 | 0.9815 |
| Linear | 4820.2 | 4530.6 | 0.9285 |
| Ridge | 4846.4 | 4561.8 | 0.9277 |
| HistGradientBoosting | 4829.1 | 2521.9 | 0.9282 |
| KNN (k=5, supervised) | 7011.5 | 4498.4 | 0.8486 |

Finding: lowest test RMSE = Naive baseline (1053.3); best trained ML = GradientBoosting (1700.1).
Year-to-year persistence dominates; no trained model beat naive — an important honest result, not a failure to hide.

## Walk-forward (train→predict 2021/22/23/24, N=35 each): sheet 09 + `phase5_walk_forward.csv`.
## Errors: per-state residuals (`phase5_predictions.csv`); 2023 mean-AE > 2024 for both naive and GBR; large-state errors dominate absolute metrics.
## Importance (test-set permutation, leakage-safe fit): Lag1_Acc dominant; predictive importance only, never causal.
## 2020 sensitivity: full-train vs post-2020-train (N=70) on same test — sheet 13; post-2020 training too small for stable conclusions.
## Scale: high R² values reflect cross-state scale; absolute metrics (RMSE/MAE) are the decision metrics.
