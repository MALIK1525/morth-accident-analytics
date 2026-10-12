# Presentation summary (B.Tech, presentation-ready)

Problem: how do geography, time, weather, road-user, violation, and collision factors relate to
Indian road accidents and severity? Gap: no exposure denominators, fragmented sources, vintage mixing.
Objectives RQ1-RQ11 (see report). Data: MoRTH 2018-24 (254 obs) + AR2017 history (conditional) +
NCRB monthly (separate) + IMD weather (236 matched) + 7 supporting modules. Methods: verification by
reconciliation; OLS/corr/chi2/Friedman + FDR; lag-only ML vs naive baseline; K-means K=2.
Major findings: +3.7% accidents vs +12.4% deaths; severity 36.3; pooled weather associations;
May peak / July trough (NCRB); two-wheelers 46.2% of deaths (counts). Statistical: most state slopes
non-detectable (N=7); Friedman p=3e-4 (descriptive). ML: naive wins both targets (honest null);
GBR overfits. Clustering: 2 descriptive profiles. Limitations: no vehicle stock, no microdata/coords,
no MoRTH monthly, N=213. Contribution: verified benchmark + integrations + honest nulls + provenance.
Future: eDAR access, vehicle stock, monthly series, longer panel.
