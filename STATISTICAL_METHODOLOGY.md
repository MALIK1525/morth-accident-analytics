# Statistical Methodology (`app/analytics/statistics.py`)

- **OLS trend per state** (Accidents ~ Year; Fatalities ~ Year): slope, intercept, R², N,
  p-value (t-test on slope), std. error. Computed live via scipy.
- **Trend labels** (neutral, threshold-documented): slope magnitude vs standard error —
  Increasing / Decreasing / Relatively flat fitted trend; never "good/bad".
- **YoY change**: absolute + percentage, India level (verified totals) and derivable per state.
- **CAGR**: (end/start)^(1/years)−1, descriptive only, not a forecast.
- **Correlation**: Pearson + Spearman on numeric panel columns with N and p-values;
  reported as association, never causation.
- **Time-to-threshold**: first observed year a state reaches a user threshold; observed only,
  no extrapolation unless a forecasting mode is explicitly selected.
- Categorical data is never Pearson-correlated without encoding disclosure.
