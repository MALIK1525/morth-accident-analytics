# PHASE 21 — Browser Functional Fix Report

## Root causes
1. **Stuck "Loading state boundaries…" (CONFIRMED BY CODE PATH):** any exception
   after the GeoJSON fetch (layer construction, styling, fitBounds) escaped the
   narrow try-block, leaving the loading text forever. The whole init body is
   now inside one guarded block with step statuses + a Retry button.
2. **Stale-bundle risk:** scripts loaded without cache-busting, so browsers
   could run weeks-old JS after deploys. Added `?v=ph21` to both scripts and
   the GeoJSON fetch. (If the user retests, hard-refresh Ctrl+Shift+R once.)
3. **Near-Me silent hangs:** no timeout and one generic error. Added 25 s abort,
   step messages (permission → received → fetching → done), and a specific
   timeout/rate-limit message with city-search fallback.
4. **Tooltip/panel mechanics:** bind-once sticky tooltips + interactive polygons
   retained and covered by static tests; no logic defect found in review.

## Files changed
- app/static/js/india_map.js (guarded init, retry, near-me timeout)
- app/templates/live.html (cache-busted script URLs)
- tests/test_phase19.py (guard/retry/timeout assertions)

## Endpoint diagnostics (live this phase)
- state-intel 200/38; geojson 200/530KB; status 200; audit zero_mismatch True.
- Point weather success via MET Norway fallback (Near-Me path).

## Tests: 181/181.
## Browser verification: NOT VERIFIED (no headed browser).
Manual acceptance (must pass on screen): hover Punjab/Tamil Nadu/Andaman shows
accident tooltip; click opens persistent panel; search + reset work; Near-Me
allow returns weather; deny shows fallback; boundary-status reads "36 polygons
loaded"; console shows no relevant errors.
## Benchmark checksum: d8064caa… MATCH. Research untouched. No secrets added.
## Deployment: (verify) commit + push + served-asset checks.
