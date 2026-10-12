# Viva questions (55; Q/A/caution each — condensed)

A. Basics: title/RQ/objectives/scope/why 2018-2024 (verified benchmark span; 2014-17 conditional vintage).
B. Data: MoRTH vs NCRB (different collection/definitions; 2024 gap -19,740; never merged); IMD grids;
OpenCity mirror status (VERIFIED-MIRROR, reconciled); TN districts; provenance hashes.
C. Methods: State-Year unit (254 obs, policy-relevant granularity); OLS N=7 limits; Pearson+Spearman
(linear + monotonic); Friedman (repeated years as blocks); FDR/BH (multiple testing); p-value/R2 meanings.
D. Stats: severity definition (deaths/100 acc, not population rate); chi2 monthly (large-N sensitivity);
near-zero rule (0.5% of mean, documented); CIs wide.
E. Weather: N=236/18 excluded; pooled scale confounding; within-state N<=7 descriptive only;
severity null; never causal; humidity etc. unavailable (IMD grids temp/rain only).
F. ML: lag-only + cutoff T-1; leakage audit (4 exclusions); train 2019-22/test 2023-24; naive wins
(persistence + small N + scale variance); GBR train R2~1.0 = overfitting; KNN supervised (labeled pairs).
G. K-means: unsupervised (no labels); standardized; K=2 by max silhouette 0.356; ARI stability; PCA display;
descriptive labels (no exposure => no "risk").
H. OriginPro: workbook per phase; README graph specs; tables trace to CSVs.
I. Limits: vehicle stock (blocks per-vehicle rates); microdata/coords (eDAR restricted); monthly MoRTH;
2023-24 state injuries; history conditional (J&K break, DNH merge); N=213.
J. Integrity: no fabrication (reconciliation gates); vintages labeled; nulls preserved; counts≠risk.
K. Future: eDAR, vehicle stock, monthly series, longer panel, station weather.
Mandatory 19: covered above (2018-24 span; history conditional; State-Year unit; vehicle gap; counts≠risk;
naive wins; KNN supervised; K-means unsupervised; Friedman; Pearson+Spearman; FDR; p/R2; train-R2 trap;
leakage; NCRB/MoRTH split; weather non-causal; 2023-24 injuries; history conditional).
CAUTION on all: answer with numbers + file pointers; never upgrade association to cause.
