# PHASE 18 — Production Fix Report (blank map, weather, Data Watch filter)

## Root cause: blank India map (P0) — CONFIRMED IN CODE
`loadLive()` created the Leaflet map only AFTER a successful weather fetch
(`if (!map)` nested inside the try-block after the throw-on-empty check).
With production weather returning 429/error, the map object was never created:
blank white container. NOT a tile, CSS, GeoJSON, or fitBounds problem.
Fix: new `ensureMap()` runs unconditionally at page boot; weather failure path
also calls it. Tile-provider failures now surface a visible basemap notice
(`tile-notice`) instead of silent blankness; GeoJSON failure writes an explicit
boundary-data message into the state panel. Boundaries/tiles verified served.

## Root cause: weather outage (P0) — EXTERNAL, MITIGATED
Evidence: provider healthy from here; Render egress persistently HTTP 429
(shared-IP quota). Fix in this phase is resilience only: batched 1-call scans
(Phase 18 earlier commit), retry, stale last-good + STALE badge. Map, state
polygons, and accident statistics now provably render with weather red —
map boot no longer depends on any provider.

## Root cause: Data Watch filter defect (P1) — CONFIRMED, FIXED
`classify_relevance` matched the generic "accident" keyword in the ADSI 2024
mixed crime/suicide record → RELEVANT. Fix: suicide/crime-dominant signals
force NOT_RELEVANT, or REVIEW when paired with explicit road-accident signals;
original records/audit history preserved (only the verdict refined). Default
view (RELEVANT) no longer shows ADSI-type cards. REVIEW added to the filter
dropdown. Regression tests use the exact production ADSI 2024 title/description.

## Files changed
- app/static/js/live.js (ensureMap, tile notice hook, unconditional boot)
- app/templates/live.html (tile-notice element)
- app/live/watch.py (relevance refinement)
- tests/test_data_watch.py (3 new classification tests)
- tests/test_live_hardening.py (map-independence tests)

## Tests: FULL SUITE (see verification)
## Benchmark checksum: d8064caa… (re-verify at commit)
## Deployment: push both branches + verify /live + state-intel + watch scan.
## Remaining external blockers
Shared-IP 429 (weather), missing TomTom/data.gov.in keys, NCRB bot-block,
no headed browser here (visual map behavior structurally verified only).
