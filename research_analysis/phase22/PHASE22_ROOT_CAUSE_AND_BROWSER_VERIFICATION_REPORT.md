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

### RESULTS (all against the DEPLOYED site, screenshots saved)
- Boundary status: "State boundaries loaded: 36 polygons…" ✓
- Dropdown: 39 options (38 entities + placeholder) ✓
- Search Punjab → panel with 6,063 / 4,759 / Not-available ✓, persists ✓, reset ✓
- Hover Punjab: tooltip "Punjab (2024, MoRTH benchmark), Accidents 6,063,
  Fatalities 4,759, Injured: Not available for this year" ✓
  (screenshot: BROWSER_PUNJAB_HOVER_EVIDENCE.png — choropleth, tooltip,
  markers, badges all visible)
- Click Punjab → persistent detail panel (severity 78.49) ✓
- Near-Me (granted mock): 23.5°C Clear sky via MET Norway fallback ✓
- Near-Me (denied): fallback message ✓
- Console: zero page errors ✓
- Near-Me denial on mobile viewport ✓
- Note: tooltip temperature line showed the honest unavailable-fallback for
  Punjab (no monitored city in that state) — correct behavior, not a defect.

## Tests: 182/182.
## Benchmark checksum: d8064caa… (verify at commit).
## Research untouched. No secrets. No paid APIs.
