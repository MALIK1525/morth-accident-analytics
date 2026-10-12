# Discussion (paper-ready draft)

## What the results show
Deaths outpace accidents (+12.4% vs +3.7%), so severity rises (33.5 -> 36.3/100 acc) while counts
fluctuate. State patterns are heterogeneous but low-powered (N=7). Weather shows robust pooled
associations whose direction survives FDR, yet between-state scale differences plausibly drive much
of the pooled signal; within-state evidence is low-power. Severity shows no weather association.

## What they do not show
No causal effects (observational, no identification); no risk ranking (no exposure denominators);
no reliable forecasting (persistence beats trained models); no climate-season claims (quarters only).

## Counts vs risk
Raw counts reflect exposure (population, vehicles, road use). All state/zone/city comparisons use
"recorded counts", never "risk". Vehicle-stock exposure remains the binding missing denominator.

## Why persistence won
Strong year-to-year autocorrelation + small panel + scale-dominated variance: last year's count is
the best predictor. GBR's train R2~1.0 vs test loss is textbook overfitting under small N.

## K-means is exploratory
K=2 typology describes, never explains; no exposure-based risk labels.

## Vintage discipline
NCRB monthly, AR2017 history, IMD weather, RGI projections each carry vintage labels; mixing them
would create false precision. The 2019 benchmark revision and J&K break are flagged, not smoothed.

## Missing pieces that matter most
State vehicle stock, accident-level microdata with coordinates, MoRTH monthly series.
