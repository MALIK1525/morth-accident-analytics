# Results (paper-ready draft; numbers from analysis files)

## 4.1 India-wide temporal trends (2018-2024)
Accidents 470,403 -> 487,707 (+3.7%) with a 2020 dip (-18.6%) and recovery; fatalities 157,593 ->
177,175 (+12.4%); fatality ratio 33.50 -> 36.33 per 100 accidents. OLS slopes (N=7): accidents
+6,725/yr (p=0.44, ns); fatalities +4,167/yr (p=0.09, ns). Descriptive only.

## 4.2 State-level patterns
38 entities; per-state slopes/R2/p/CI in PHASE10_STATE_FINAL_RESULTS.csv. Accidents: 17 positive /
15 negative / 6 near-zero (5 detectable p<0.05). Fatalities: 26 / 10 / 2 (9 detectable). No rankings.

## 4.3 Zone-level analysis
Six zones, 2018-2024 totals/shares/YoY. Friedman: chi2=25.29, p=3.0e-4, Kendall W=0.72 —
zones differ descriptively across years; not a ranking.

## 4.4 Weather associations (N=236 pooled)
Rain-acc r=-0.234 (p=2.9e-4); rain-fat r=-0.376; Tmax-acc +0.452; Tmax-fat +0.498; Tmin-acc +0.367;
Tmin-fat +0.340. FDR-adjusted. Pooled scale confounding disclosed. Weather x severity: |r|<0.15,
none significant.

## 4.5 Reported violations and collision patterns (2024, India)
Over-speeding: 345,024 accidents (70.7%), 124,522 fatalities (70.3%) — reported category.
Hit from Back most frequent collision (113,907); Hit and Run highest fatality ratio (~0.50).

## 4.6 Road-user fatalities (2024)
Two-wheelers 81,780 (46.2%), pedestrians 36,526 (20.6%). Counts without exposure denominators.

## 4.7 Licence and safety-device findings
Valid licence 68.2% of 2024 accidents (share of reported accidents). No-helmet deaths 54,122;
no-seatbelt deaths 14,466 (non-use toll, not effectiveness).

## 4.8 NCRB monthly pattern (2024, NCRB vintage)
Peak May 41,364 (8.84%), trough July 34,895 (7.46%); chi2 vs uniform = 1276, p<1e-6 (large-N).
Calendar quarters Q1-Q4 only; never merged to MoRTH.

## 4.9 Tamil Nadu district analysis (2021-2023)
38 districts; sums == benchmark TN exactly. TN-only evidence.

## 4.10 Predictive modeling (test 2023-2024)
Naive baseline RMSE 1038.6 (acc) / 286.3 (fat) beat all trained models (best trained: GBR 2148.6 /
LinReg 766.7). GBR train R2~1.0 with worse test error = overfitting evidence. Honest null preserved.

## 4.11 Unsupervised clustering
K=2 (silhouette 0.356): higher-count profile (N=6) vs lower-count profile (N=17, plus mid group
per K=3 sensitivity). Descriptive labels; ARI stability reported.
