# Phase 7 Analysis Report (research only; no website/app changes)

## India baseline 2018-2024 (verified benchmark)
- Accidents: 470,403 → 487,707 (+3.7%); pattern FLUCTUATING (2020 dip −18.6%, recovery after).
- Fatalities: 157,593 → 177,175 (+12.4%); rises faster than accidents.
- Injuries (India vintage): 464,715 → 471,441 (+1.5%).
- Fatality ratio: 33.50 → 36.33 per 100 accidents (severity rises while counts fluctuate).
- OLS slopes (N=7, descriptive only): accidents +6,725/yr (p=0.44, R2=0.12, NOT significant);
  fatalities +4,167/yr (p=0.09, R2=0.47, NOT significant at 0.05). No causal reading.

## State analysis (38 entities, OLS N=7 each)
- Full per-state slopes/R2/p/CI in STATE_TREND_STATISTICS.csv. Low power throughout; no rankings.

## Time-to-threshold
- Thresholds 10k/25k/50k accidents and 1k/5k/10k fatalities; first-reaching year per state
  in TIME_TO_THRESHOLD.csv; unreached states marked NOT_REACHED. No extrapolation.

## Zone analysis (6 zones)
- Zone totals/shares/YoY in ZONE_YEAR_ANALYSIS.csv. Descriptive differences only.

## Weather (236 matched state-years; 18 excluded preserved)
- Rain-Acc r=−0.234 (p=2.9e-4); Rain-Fat r=−0.376; Tmax-Acc +0.452; Tmax-Fat +0.498;
  Tmin-Acc +0.367; Tmin-Fat +0.340 — reproduces Phase 8. Pooled associations; not causal.
- Weather x severity: all |r|<0.15, none significant — no detectable severity association.

## Seasonal (NCRB vintage, separate)
- 2024 Road-States: peak May (41,364, 8.84%), trough Jul (34,895, 7.46%); Oct rebound +9.9% MoM.
  NCRB vintage; never merged into MoRTH benchmark.

## Supporting modules (2024, India-level, separate definitions)
- Inventory in SUPPORTING_INVENTORY.csv; analysis uses module tables as-is.

## Exposure
- State vehicle stock UNAVAILABLE — no per-vehicle metrics computed. India EX-01 described separately.

## Historical candidate
- 2014-2017 AR2017-vintage panel + harmonized 2014-2024 candidate kept CONDITIONAL and separate.

## Methods / ML plan
- STATISTICAL_METHODS_MATRIX.csv (7 entries: 5 READY, 1 CONDITIONAL, 1 DEFERRED).
- ML_METHOD_PLAN.csv (KNN correctly labeled supervised; K-means unsupervised clustering).

## Validation
- India sums recomputed from STATE_YEAR layer == published totals all 7 years (acc/fat exact;
  injuries exact where state data exist; India-vintage injuries labeled separately).
