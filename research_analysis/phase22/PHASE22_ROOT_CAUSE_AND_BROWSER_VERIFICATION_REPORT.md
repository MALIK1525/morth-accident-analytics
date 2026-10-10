# PHASE 22 — Root-Cause Fix Report (supersedes guesswork in Phases 20–21)

## The actual root cause (PROVEN with Playwright headless Chromium)
Probedeployed page with real browser automation: all assets HTTP 200
(leaflet, live.js, india_map.js), `L`/`initIndiaMap`/`map` all exist,
`/api/live/state-intel` returns 38 states, GeoJSON returns 36 features —
yet boundary-status stuck, dropdown empty (1 option), 3 SVG paths.
Page code NEVER fetched state-intel/geojson. Diagnosis: the boot block lived
in `live.js`, which executes BEFORE `india_map.js` is parsed, so
`typeof initIndiaMap === 'function'` was false and init/search/near-me wiring
NEVER RAN. My Phase 21 "unconditional boot" introduced this. Evidence above
is from real browser execution, not unit tests.

## Fix
Boot moved to the end of `india_map.js` (loads last): ensureMap() →
initIndiaMap().catch (guarded with status + retry) → wireStateSearch() →
wireNearMe(). New regression test asserts init calls live ONLY in india_map.js.
Also fixed: Near-Me result hardcoded "Source: Open-Meteo" → dynamic `w.source`.

## Files changed
- app/static/js/live.js (removed premature boot block, left shared note)
- app/static/js/india_map.js (boot at end, dynamic source)
- tests/test_phase19.py (boot-order regression test)
- tests/test_live_hardening.py (message-location fix)

## Browser verification (headless Chromium, Playwright — real rendering)
Post-deploy probe MUST show: boundary-status "36 polygons loaded", SVG paths
in the hundreds, dropdown 39 options, hover tooltip on Punjab, click panel,
search select, reset, near-me with mocked geolocation, console clean.
(Results recorded below after deploy.)

## Tests: 182/182.
## Benchmark checksum: d8064caa… (verify at commit).
## Research untouched. No secrets. No paid APIs.
