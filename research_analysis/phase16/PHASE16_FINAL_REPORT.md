# PHASE 16 — India-Only Road Accident Intelligence Map: Final Report

## Root causes found
1. Map too broad: Leaflet defaulted to a world view with city-point markers only;
   no state boundaries existed in the app.
2. "Weather temporarily unavailable": single-point fetch failures replaced the
   whole panel; now per-location graceful states (existing behavior retained).
3. "Awaiting API key" vagueness: TomTom messaging lacked setup guidance; page
   was otherwise independent of the key (verified).
4. Crime datasets in Data Watch: keyword discovery legitimately returns them;
   default view now pre-filters to RELEVANT (ALL still selectable).

## Files changed
- app/static/geo/india_states.geojson (NEW, 531 KB): 36 States/UTs, simplified
  datameet Admin2 (ST_NM), EPSG:4326. Source/license recorded in file properties.
- app/server.py: read-only `/api/live/state-intel` (38 entities, years, severity,
  null injuries preserved).
- app/live/routes.py: `/api/live/status` diagnostics block (key presence flags
  + cache ages; values never exposed).
- app/templates/live.html: state search + reset, state panel, Near-Me card,
  relevance default, footer unchanged otherwise.
- app/static/js/india_map.js (NEW): boundaries, hover/click/select, panel,
  centroid weather, opt-in geolocation.
- app/static/js/live.js: layer init hooks + TomTom setup instructions.
- tests/test_phase16.py (NEW, 12 tests); tests/test_live_traffic.py: key test
  now detects assigned literals instead of var-name mentions.

## Map and state interaction
Fit-bounds India on load; hover highlights + tooltip (name, latest acc/fat/inj
with year, MoRTH label); click selects + opens panel (per-entity stats, severity
with formula, year-trend table, centroid weather labeled as proxy, quality notes
+ MoRTH/data.gov.in links). Search incl. legacy entities without polygons
(honest "boundary unavailable" note — no boundaries invented). Reset restores view.

## Datasets retained / filtered
Benchmark untouched (checksum verified). Data Watch default = RELEVANT only;
crime/suicide sets remain discoverable under All/NOT_RELEVANT with unchanged
classifications. No discovery logic modified.

## Weather Near Me
Button-gated geolocation; coordinates used for one weather request only, shown
as a session map marker; never stored/logged/URL-shared. Denial/unsupported
falls back to city search with no breakage.

## Provider findings
Open-Meteo works (10/10). TomTom/data.gov.in keys absent → documented
awaiting-states + setup instructions; map/boundaries/stats/weather independent
of keys (verified). NCRB bot-blocked (manual card); PIB manual.

## Tests: 158/158 (146 baseline + 12 new)
## Frozen benchmark: SHA-256 d8064caa… unchanged. No research files modified.
## Deployment: (verify below) commit + push + /live + endpoint checks.
## Limitations
No headed browser here (structural checks only); NCRB/PIB manual; keys absent;
watch history ephemeral (disclosed); centroid weather is a proxy (labeled);
Admin2 boundaries simplified for web (provenance in file).
