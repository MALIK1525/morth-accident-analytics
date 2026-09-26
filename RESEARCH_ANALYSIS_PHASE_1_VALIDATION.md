# PHASE 1 VALIDATION
Script: `phase1_analysis.py` (re-runnable). All values recomputed from `data/MoRTH_Primary_Dataset_3.xlsx`, 2026-09-26.

- Benchmarks: panel sums == official India totals all 7 years for Acc/Fat (0 mismatch); Inj India values match stated benchmarks.
- Formulas: YoY% = (cur−prev)/prev×100; Fat/100 = Fat/Acc×100; OLS via scipy.stats.linregress on numeric Year; 95% CI = slope ± t(0.975,N−2)·SE; flag = APPROX_STABLE if |slope|<2·SE else sign.
- Counts: 38 entities, 254 rows, 0 dupes, 0 unmapped zones; Inj missing 75 cells (2023/24 state + UT gaps); correlation N=179 complete rows.
- Zone reconciliation: zone-year sums == India totals each year (shares sum to 100%).
- Regression verification: India Acc R² 0.1217/p 0.4432; Fat R² 0.4694/p 0.0894; post-2020 Acc R² 0.869/p 0.068 — CIs include 0, so no significance claimed.
- Injury coverage: per-year reporting counts 36/36/35/36/36/0/0 verified; no state 2023/24 injury values created.
- Threshold pairs: 20 pairs across 10k/25k/50k thresholds, mechanically derived.
- Exposure/weather/supporting: verified absent (empty supporting_csv/, no IMD files) → correctly NOT computed.
- 2019 vintage: panel uses later vintage; older values documented, not mixed.
