# PHASE 24 (second) — India-Wide Live Traffic Map Report

## Root cause of Delhi-centric display
Flow used 10 point queries (city markers + circles); incidents used 10 city
bboxes. Nothing outside those points ever rendered. Not a data bug — an
architecture gap: no viewport-driven flow layer existed.

## Chosen endpoint
TomTom Raster Flow Tiles v4, `relative0` style (documented ratio bands +
explicit road-closed color; absolute would mislead). Verified: endpoint exists
(no-key probe returns 401, not 404); docs confirm format/params/styles.

## Files changed
- app/live/traffic.py (fetch_tile with style/zoom/coord validation, 150-entry
  TTL cache, sanitized errors) + routes (same-origin tile proxy + segment
  point-details endpoint).
- app/static/js/live.js (flow tile overlay, click-for-segment popup, toggle
  retarget, dead-filter cleanup) + live.html (traffic container, notice,
  relative0 legend, responsive heights).
- tests (tile validation/cache/errors/segment/HTML tokens).

## Coverage honesty
Tiles render only where TomTom returns segments; grey/blank = no data (never
green). Legend states this. City flow endpoint retained as data source for
badges/zoom; coverage labels kept ("monitored-city areas" for incidents).

## Tests: 195/195.
## Benchmark: d8064caa… (verify at commit). Research untouched.
## Deployment: (verify) commit + push + regional tile/pan checks + screenshot.
