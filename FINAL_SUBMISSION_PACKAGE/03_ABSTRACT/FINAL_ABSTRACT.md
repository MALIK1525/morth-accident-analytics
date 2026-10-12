# Abstract (final; verified numbers only) — for: A Multi-Level Data-Driven Analysis of Road Traffic
Accidents in India

Background: India recorded 487,707 accidents and 177,175 deaths in 2024 (+3.7%/+12.4% since 2018)
with severity rising 33.50 -> 36.33 deaths/100 accidents, yet exposure denominators are missing.
Objective (RQ1-RQ11): relate geography, time, weather, road-user, violation, and collision factors to
occurrence and severity using verified sources. Methods: MoRTH 2018-2024 panel (254 state-years,
38 entities); conditional AR2017 2014-2017 candidate; NCRB ADSI 2024 monthly (separate vintage);
IMD rain/temp to states (236 matched of 254 state-years across 38 reporting entities); AR-2024 supporting tables; OLS/corr/chi2/Friedman + BH-FDR;
lag-only ML (train 2019-22 N=141; test 2023-2024 N=72) vs naive baseline (acc RMSE 1038.6); K-means (K=2-6).
Results: pooled rain r=-0.234/-0.376, Tmax r=+0.452/+0.498, Tmin r=+0.366/+0.340 (associational);
severity-weather null; Friedman p=3.0e-4 (descriptive zone differences); NCRB May 8.84%/Jul 7.46%;
no trained model beat persistence (acc RMSE 1038.6 vs 2148.6 best trained); K=2 (silhouette 0.356).
Conclusion: severity rises while counts fluctuate; risk ranking, causal, and forecasting claims are
unsupported; state vehicle stock and microdata are binding gaps. Keywords as above.
