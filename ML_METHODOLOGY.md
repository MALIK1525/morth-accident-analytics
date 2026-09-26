# ML Methodology

## Task
Predict a state's annual accident count for year *t* from pre-*t* history only.
NOT predicted: individual crashes, locations, timing, driver behaviour.

## Features (all strictly historical)
Year, lag1_accidents, lag1_fatalities, lag1_yoy_change, Zone (one-hot).
First year per state dropped. Same-year variables never used → no target/future leakage.

## Evaluation
Chronological split: train 2018–2022 (n=141), test 2023–2024 (n=72). No shuffling.
Primary metric RMSE; MAE/R²/MAPE reported. Module: `app/analytics/ml_models.py`.

## Models
Naive previous-year baseline (not trained) vs Linear, Ridge, KNN(k=5, supervised),
Random Forest, Gradient Boosting. Best overall AND best trained reported separately.

## Observed results (test 2023–2024)
- Naive baseline: RMSE 1038.6 (best overall — expected for a persistent series).
- Best trained: Gradient Boosting, RMSE 2066.3, R² 0.9867.
- Classifier (severity-ratio tiers, trained RF, chrono split): 78.87% accuracy.
- Clustering: K-Means (unsupervised), k=3, on 2024 state accidents/fatalities.

## Limits
Aggregate panel (n=213 with lags) is small for ML; high R² reflects cross-state scale
variance, not precision. Predictions are model estimates, not causal statements.
