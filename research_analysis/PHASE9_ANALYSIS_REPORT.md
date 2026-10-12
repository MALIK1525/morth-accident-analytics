# Phase 9 Analysis Report (research only; no website/app changes)

## Modeling dataset
- STATE x YEAR, 2018-2024 benchmark; effective rows after lag-1 requirement: train 141 (targets 2019-2022), test 72 (2023-2024). 2018 dropped honestly (no benchmark-compatible 2017 lag); Ladakh NV rows excluded.
- Targets: Accidents, Fatalities. Injuries deferred (state N/A in test years); fatality ratio deferred (bounded + leakage-prone).

## Headline result (honest null)
- Under the 2023-2024 held-out design, the naive persistence baseline produced lower test RMSE
  than every trained model on both targets (Accidents: naive 1038.6 vs best trained GBR 2148.6;
  Fatalities: naive 286.3 vs best trained LinReg 766.7).
- "Model did not outperform the naive baseline under this test design" — recorded per model.
- Interpretation: year-to-year persistence dominates; trained models overfit train (GBR train R2=0.9999).
  This is a finding about the data/panel, not a model failure to hide.

## Supervised models (all supervised incl. KNN Regression; time-aware rolling-origin validation)
- Linear, Ridge(a=1), RF(200/j5... min_samples_leaf=5), GBR defaults, KNN k=5 standardized.
- No test-set tuning. Full metrics in PHASE9_MODEL_RESULTS.csv; predictions in PHASE9_PREDICTIONS.csv.

## Errors
- Errors grow with state volume (Corr_Volume_Error in PHASE9_ERROR_ANALYSIS.csv): scale confounding confirmed.
- 2023 vs 2024 MAE split reported per model.

## Features
- Best-model importance recorded (predictive contribution only, never causal).
- Log1p sensitivity: compared on raw scale only; population-normalized modeling NOT substituted.

## K-means (unsupervised; standardized state profiles, 7 features)
- K=2..6 diagnostics; K=2 selected by max silhouette (0.356). Profiles use descriptive labels only
  ("higher recorded-accident-count profile", etc.), never "high-risk".
- Stability: ARI across 4 seeds in PHASE9_CLUSTER_STABILITY.csv. PCA (2 comps) for visualization.

## Limits
- N=213 modeling rows; persistence-dominated series; no vehicle/microdata/monthly features;
  historical candidate excluded from training (sensitivity only); NCRB/MoRTH separate.
