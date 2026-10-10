# PHASE 20 — Functional Fix Report

## Actual root causes (reproduced in code, not assumed)
1. **Single-point weather had no fallback (CONFIRMED):** the MET Norway chain
   covered only the 10-city summary. Near-Me + state-centroid weather call
   `fetch_point` (Open-Meteo only) → 429 from Render → both features dead.
   Fixed: `fetch_point` now falls back to MET Norway per-point; source labeled.
2. **Tooltip binding fragility:** tooltips were rebound + force-opened on every
   mouseover. Rewrote to bind-once sticky tooltips (Leaflet auto-opens on hover)
   with `interactive: true` polygons and selection-safe mouseout.
3. **No visible load proof:** added `boundary-status` line (polygon count on
   success, explicit error otherwise) so a blank map is diagnosable on sight.
4. **Andaman gap (from Phase 19 audit):** alias added; 38/38 resolution tested.

## Files changed
- app/live/weather.py (point-level fallback)
- app/static/js/india_map.js (tooltip/boundary-status)
- app/templates/live.html (status element)
- tests/test_live_monitor.py, tests/test_phase19.py (fallback + binding tests)

## Endpoint diagnostics (live, this phase)
- state-intel 200/38 states; status+diagnostics 200; audit zero_mismatch True.
- Weather summary now serves via MET Norway fallback in production (10/10).
- Near-Me path uses the same fixed `fetch_point`.

## Tests: 179/179 (177 + 2 new).
## Browser verification: NOT VERIFIED (no headed browser) — manual procedure:
hover Punjab/Tamil Nadu/Andaman (tooltip with stats), click (panel+highlight),
search+reset, Near-Me allow + deny, weather badge source. Do not mark passed
until done on screen.
## Benchmark checksum: d8064caa… MATCH. Research untouched. No secrets added.
## Deployment: (verify) commit + push + served-asset checks.
## Limitations: headed-browser QA outstanding; TomTom/data.gov.in keys absent;
NCRB bot-blocked; shared-IP 429 possible (now absorbed by fallback+stale).
