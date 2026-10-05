# PHASE 13.1 — Data Source Audit (verified Oct 2026)

## A. Traffic / congestion / incidents

| Source | URL | Type | API | Public | Key | Free | India | Lat/Lon | Live | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| TomTom Traffic API (Flow + Incidents) | developer.tomtom.com / docs.tomtom.com | Commercial | YES (REST + vector/raster tiles) | YES | YES (freemium key) | Freemium tier | YES (global incl India) | YES | YES (flow speeds + incident details: location, road, delay, significance) | **RECOMMENDED Tier 3** — needs user-supplied API key; browser must NOT hold key (proxy via backend) |
| HERE Traffic API | developer.here.com | Commercial | YES | YES | YES | Freemium | YES | YES | YES | Alternative Tier 3 |
| OpenStreetMap tiles | tile.openstreetmap.org | Public infra | Tiles only (no traffic) | YES | NO | YES | YES | YES | Base map only | Tier 2 base map (follow tile usage policy; or CARTO/OSM-compatible tiles) |
| Leaflet.js | leafletjs.com | OSS (BSD) | JS lib | YES | NO | YES | n/a | n/a | n/a | Tier 2 map renderer |

LIVE TRAFFIC (flow speeds) vs TRAFFIC INCIDENTS are separate TomTom endpoints — keep as separate map layers.

## B. Weather (current)

| Source | URL | Type | API | Key | Free | India | Variables | Verdict |
|---|---|---|---|---|---|---|---|---|
| **Open-Meteo** | api.open-meteo.com | Public infra (CC-BY 4.0) | YES, no signup | NO | YES (10k calls/day non-commercial) | YES (global grids, coord-based) | temp, rain, precipitation, humidity, visibility, wind, alerts | **RECOMMENDED Tier 2** — no key, attribution required |
| OpenWeatherMap | api.openweathermap.org | Commercial | YES | YES | Free: current+5d/3h; OneCall 3.0 1000 calls/day (card required) | YES | temp, humidity, wind, visibility, alerts | Tier 3 fallback (needs user key) |
| IMD (mausam.imd.gov.in) | mausam.imd.gov.in | Gov Tier 1 | NO open API (website only) | n/a | n/a | YES | Official alerts | Tier 1 reference/link only — no programmatic access; link out to IMD warnings |

## C. Live / recent accidents — **NOT PUBLICLY AVAILABLE**

- **iRAD / eDAR** (irad.parivahan.gov.in): national accident database, 36 States/UTs, but **restricted to police/official logins**. No public API. Verdict: ACCESS-RESTRICTED, cannot integrate.
- NCRB ADSI / MoRTH reports: annual, 1–2 yr lag — research data, not live.
- TomTom Incident Details: includes accident-type traffic incidents with location+timestamp (commercial probe/crowd data, NOT official accident records). May be shown ONLY labeled as "reported traffic incidents (TomTom)", never as official accident counts.
- **No KPI accident/fatality/injured counters are possible in Live Monitor.** KPIs must be: traffic conditions, weather, incident counts (labeled), source status — never fabricated accident numbers.

## D. Road hazards

| Feed | Via | Verdict |
|---|---|---|
| Closures, construction, road works, congestion | TomTom Incidents API (categories) | PARTIAL — available where TomTom coverage exists |
| Floods/landslides/potholes/fallen trees | No verified public API for India | UNAVAILABLE — do not claim |
| Severe weather alerts | Open-Meteo alerts / IMD website link | PARTIAL |

## E. Government data watch (monitorable)

| Source | Mechanism | API | Verdict |
|---|---|---|---|
| data.gov.in (OGD, NIC) | Catalog + resource APIs; per-API key via data.gov.in | YES (keyed) | AVAILABLE — poll MoRTH/NCRB catalogs (weekly cron); needs key |
| OpenCity CKAN (data.opencity.in) | CKAN DataStore API (`/api/3/action/…`), open, includes MoRTH mirrors | YES (open) | AVAILABLE — easiest watch feed |
| MoRTH (morth.nic.in) | Annual PDF reports, no API | NO | Manual/semi-auto check (page HEAD polling) |
| NCRB (ncrb.gov.in) | Annual ADSI PDFs | NO | Same as MoRTH |
| PIB (pib.gov.in) | Press releases + RSS | PARTIAL | Keyword watch (MoRTH/accident) |

Detection ≠ integration: new item → Data Watch list → human validation → Phase 7-style provenance → optional integration. Benchmark NEVER auto-overwrites.
