# B.Tech presentation (25 slides; bullets only)

1. Title: A Multi-Level Data-Driven Analysis of Road Traffic Accidents in India (short: Data-Driven
Road Traffic Accident Analysis in India) + candidate/guide/institute/2026.
2. Background: 487,707 accidents, 177,175 deaths (2024); severity 36.33 and rising.
3. Problem: counts without exposure; fragmented vintages; no microdata.
4. Gap: reconciliation + geography + missing-denominator work rarely combined.
5. RQ: RQ1-RQ11 (observational framing stated upfront).
6. Objectives 1-13 (one line each).
7. Framework: discover -> verify -> preserve -> audit -> harmonize -> analyze -> validate -> model -> synthesize.
8. Data: benchmark 254 obs 2018-2024 (38 entities); history conditional; NCRB separate; IMD 236 matched; 7 modules; TN districts.
9. Validation: 0 benchmark mismatches; 12/12 history; NCRB sections exact; TN sums exact.
10. India trends: +3.7% acc / +12.4% fat; 2020 dip; slopes ns.
11. Zone/state: Friedman p=3e-4 (descriptive); state slopes mostly non-detectable; no rankings.
12. Weather: rain -0.234/-0.376; Tmax +0.452/+0.498; Tmin +0.366/+0.340; severity null; never causal.
13. Violations: over-speeding 70.3% of deaths (reported category).
14. Collisions: Hit from Back leads counts; Hit and Run highest ratio.
15. Road-user/safety: two-wheelers 46.2% (counts); licence/safety are reported shares.
16. Statistics: OLS/CI, Pearson+Spearman, chi2, Friedman, BH-FDR, effect sizes.
17. ML method: lag-only, train 2019-22 (N=141), test 2023-24 (N=72), naive baseline, no test tuning.
18. ML results: naive RMSE 1038.6/286.3 beats ALL trained; GBR overfits (train R2~1.0). Honest null.
19. K-means: standardized profiles, K=2 (silhouette 0.356), descriptive labels, ARI stability.
20. Major findings: severity rise; pooled weather links; May peak; null prediction result.
21. Limitations: vehicle stock, microdata, monthly MoRTH, N=213, vintages.
22. Contributions: 10 items (benchmark, harmonization, weather, nulls, provenance, platform).
23. Future: eDAR, vehicle stock, monthly series, longer panel.
24. Conclusion: RQ answers in one line each; counts are not risk; associations are not causes.
25. Questions. Thank you.
