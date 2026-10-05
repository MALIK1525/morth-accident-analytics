# PHASE 13.5 — Final Live Monitor Audit

## UX audit
Numbered hierarchy 1–7 (map primary; weather/traffic/incidents/hazards supporting;
watch; availability). Layer toggles + legends + filters + freshness ages. No dead ends:
empty filter selections fall back to all-data view (research tabs) or honest
unavailable notes (live layers).

## Map audit
India-centered (22.5,79.5 z5), OSM tiles + attribution, 3 toggleable layer groups,
shape+icon markers, click details, tooltips with values. No invented coordinates:
weather/traffic from fixed city proxies; incidents only provider coords (nulls filtered).

## Weather audit
Server proxy, 300 s TTL, Refresh Now, per-field missing→"Not available", timeout/
failure → badge + preserved last-good clock. Monitored-location summary labeling kept.

## Traffic audit
Key absent → awaiting-key badges, no crash. Congestion from real speed ratios;
segment click shows speeds/times/delay/closure/source. Never labeled as accidents.

## Incident audit
Provider categories only; cap 300; per-type shape+symbol; detail panel carries
NOT-official-record wording. No fatality/injury/rate/risk derivation (test-enforced).

## Data Watch audit
OpenCity live (55 datasets first scan), MoRTH hash baseline, data.gov.in
awaiting-key, NCRB unavailable-card, PIB manual card. NEW/UPDATED/KNOWN,
relevance/vintage/exposure flags, geo+exposure filters added this phase.
Ephemeral-history notice displayed. Downloads confined to review_queue (32 MB cap).

## Accessibility / B-W audit
Traffic: thickness+dash+letter; incidents: shape+symbol; weather: icon+shape;
legends textual. Colour supplementary everywhere. Marker classes verified in HTML.

## Responsive audit
Tailwind md: grids, 520 px map desktop / 360 px mobile via media query, no fixed
pixel widths on cards. Headed-browser screenshot check unavailable (no headed
browser in this environment) — structural audit only, stated honestly.

## Performance audit
Single 5-min interval driving all layers; server TTLs 300/120/180 s; incident cap
300; one CKAN query set per scan (6×20 rows) with 10-min UI cache + 6-h source
interval. No per-interaction provider calls.

## Security audit
Keys via os.environ only; no literals (regex test); frontend/HTML/log/Git clean;
proxy server-side; review downloads scheme+size+path-checked. Repo secret scan: PASS.

## Research-separation audit
Live modules import nothing from benchmark/ML/weather-agent (static tests);
watch writes confined to research_watch/ (static + functional tests); no
retrain/recalc/overwrite/merge/promote surface exists. Benchmark + Phases 7–12
+ frozen package untouched (git status clean except intended app files).

## Limitations (real)
- No headed-browser visual QA available here.
- NCRB page blocks bots; PIB has no feed; data.gov.in/TomTom need user keys.
- Watch history ephemeral on free-tier redeploys (disclosed in UI).
- Weather city-proxies are not state measurements (labeled).

## Tests
130/130 (118 baseline + 12 hardening). See PHASE13.5_LIVE_MONITOR_TEST_MATRIX.csv.
Issues found and fixed: see PHASE13.5_ISSUES_AND_FIXES.md.
