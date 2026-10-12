# PHASE 25 — Production Traffic Reliability, Coverage & Performance Audit

Starting commit: `3ea11dd` (Phase 24). Baseline pre-change: `ff1e0f9`.
Final commit: see git log (`Phase 25`).
Benchmark checksum: full `d8064caab5302bb13314210fe13166ad80c9d3d7a27e7db35e3e5fde08474fb1`
(`tests/test_phase16.py::test_benchmark_checksum_unchanged` passes before and after).

## 1. Findings (evidence-based)

- **Coverage is genuinely India-wide, not Delhi-only.** `probe_coverage.py` hit real tile
  + segment endpoints for 10 cities across N/S/E/W/Central at z7 and z11: all tiles
  HTTP 200 `image/png` with thousands of opaque flow pixels each, all segments HTTP 200
  with usable speeds (e.g. Delhi 28/36, Chennai 20/27, Kolkata 11/23, Mumbai 13/17,
  Ahmedabad 48/48, Bhopal 14/21). Full matrix in `coverage_matrix.json`.
- **Legend/no-data semantics hold.** `relative0` documented bands; blank = no data, never
  green. Invalid style/zoom/coords rejected pre-upstream (400/ValueError, no provider call).
  Upstream failures raise without caching failures as success (test_tile_upstream_failure_no_stale).
- **Cache audit:** keys include (style,z,x,y) ✓; invalid rejected pre-call ✓; TTL 120 s
  refresh ✓; 150-entry FIFO cap ✓; failures never cached ✓. Two micro-defects fixed:
  re-fetch appended duplicate keys to `_tile_order` (order-list growth), and
  `clear_caches()` left the tile cache uncleared. No concurrent-request dedup (single-flight);
  noted as limitation — acceptable under Flask/gunicorn per-worker load, no evidence of harm.
- **Proxy security:** key server-side only (`TOMTOM_API_KEY`); tile URLs are same-origin
  `/api/live/traffic/tile/...` with no `key=` param; `test_tile_route_no_key_leak` passes.
  No arbitrary upstream URLs accepted; inputs validated before any provider call.
- **Freshness:** segment panel shows fetch time + "provider observation time not supplied"
  (TomTom flow endpoint supplies no observation timestamp) — honest, no invented timestamps.
- **Performance (Playwright, deployed):** initial Traffic viewport 16 tiles; pan to Mumbai +
  2× zoom-in + 2× zoom-out → 58 total, zero failed tiles; segment click → popup rendered;
  tab switch weather→traffic leaves exactly 2 Leaflet containers (no duplicate maps);
  zero console errors. Screenshot `live_mumbai.png` inspected: green flow segments on
  Mumbai roads, segment popup (22/22 km/h, confidence 1, closure no, fetch time labeled),
  TomTom attribution, LIVE badges.
- **Layer isolation:** incidents remain TomTom-reported (NOT official records); flow/incident/
  weather/research layers independent; weather tab unaffected.

## 2. Files changed
- `app/live/traffic.py` — tile order-list dedup (`if cache_key not in _tile_order`),
  `clear_caches()` now resets tile cache + order.
- `tests/test_live_traffic.py` — new `test_tile_order_no_duplicates_and_clear_resets`.
- `probe_nav.py` — fixed syntax error (missing paren), used for perf/nav evidence.
- This report.

## 3. Test results
- Full suite: **198/198 passed** (was 197; +1 new).
- Live coverage: 10/10 cities × (z7 tile + z11 tile + segment) all success — real provider data.
- Playwright perf/nav: bounded requests, no dup maps, segment popup, zero console errors.

## 4. Limitations
- No single-flight dedup for concurrent identical tile requests (per-worker caches; low risk).
- Coverage verified at 10 city areas × 2 zooms; rural/intercity-highway tiles render via the
  same viewport-driven mechanism but were not exhaustively crawled (quota-respecting).
- Tile cache is in-memory per worker; no persistent cache (none needed per evidence).
- Segment endpoint returns one sampled provider segment; panel states this explicitly.

## 5. Deployment
- Pushed to origin; Render auto-deploys. Verified: `/live` loads, Traffic tab, Mumbai view,
  segment popup, 2 Leaflet containers, zero console errors (see probe output + screenshot).
