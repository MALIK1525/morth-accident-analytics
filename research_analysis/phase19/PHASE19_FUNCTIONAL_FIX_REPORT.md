# PHASE 19 — Functional Fix Report

## Reproduced bugs and root causes
1. **Andaman gap (verified by mapping audit):** 37/38 benchmark entities resolved
   GeoJSON→API; only Andaman & Nicobar Islands missed (name-variant). Fixed with
   explicit alias; coverage test now enforces 38/38 resolution paths.
2. **Accident data not visually primary:** state fills were flat tints. Added
   log-scaled choropleth of latest recorded accidents + explicit NOT-risk legend.
3. **Tooltip lacked temperature/availability:** added city-proxy temperature
   (CITY_STATE map) with honest fallback line + historical-not-live footer.
4. **Weather outage (external):** Render egress persistently HTTP 429 from
   Open-Meteo (shared-IP quota; provider healthy elsewhere). Added MET Norway
   keyless fallback chain (verified format live) with per-point source labels;
   dynamic badge source; no keys, no fakery, fair-use UA.
5. **Hover/click mechanics:** code-reviewed event flow (bindTooltip sticky,
   select/persist/reset, search incl. polygon-less entities); no defect found in
   logic — only the Andaman data gap above. Headed-browser confirmation still
   required (no headed browser here).

## Files changed
- app/static/js/india_map.js (alias, choropleth, tooltip temp)
- app/templates/live.html (choropleth legend)
- app/live/weather.py (MET Norway fallback chain, dynamic source)
- app/static/js/live.js (dynamic badge source)
- tests/test_phase19.py (mapping, tooltip, choropleth, geolocation, URL audit)

## Test results
177/177 (175 baseline incl. Phase 18 additions + new/updated Phase 19 tests).
New: 38-entity resolution, tooltip/panel fields, choropleth-not-risk,
geolocation gating, MET Norway parse, fallback source labeling.

## Provider comparison (verified Oct 2026)
- Open-Meteo: free, keyless, CC-BY, 10k/day; EXCLUDED in practice by shared-IP
  429 from Render. Retained as primary (self-heals if quota frees).
- MET Norway Locationforecast: free, keyless, global, fair-use UA; no
  visibility field (shown Not available). ADOPTED as fallback.
- WeatherAPI.com: free $0/100K calls/mo, key signup required, attribution.
  BACKUP OPTION — needs user signup; not integrated (no approval).
- OpenWeather free 1M/mo: needs key (+card for OneCall). BACKUP OPTION.

## Browser QA: NOT AVAILABLE here — manual checklist in phase17 stands.
## Benchmark checksum: d8064caa… MATCH. Research untouched.
## Deployment: (verify) commit + push + /live + weather source check.
