# PHASE 13 — Live Monitor Architecture (plan only, no code)

## Navigation
`Research Analytics | 🔴 Live Monitor | 📡 Data Watch` — Live/Watch are separate
Flask blueprints (`/live/*`, `/watch/*`); zero imports from frozen research modules
except shared state-name/ZONE mapping (read-only copy).

## Data flow (browser never touches external APIs)
```
TomTom / Open-Meteo / CKAN APIs
  → backend fetcher (app/live/fetchers/) + server-side API keys (env only)
  → validation (schema, timestamp freshness, geo bounds for India)
  → normalization (state, timestamp IST, source label)
  → cache (in-memory TTL; NO persistence into research data dirs)
  → /api/live/* JSON → Leaflet map + layer toggles
```

## Map spec
- Renderer: Leaflet.js + OSM base tiles.
- Layers (each independently toggleable + source badge): Traffic flow (TomTom raster
  overlay), Incidents (TomTom markers, labeled "reported traffic incidents — NOT official
  accident records"), Weather (Open-Meteo per-city markers), Alerts (Open-Meteo/IMD link).
- State hover: tooltip adapts to available data; unavailable fields say
  "Data unavailable", never 0.
- State click: detail panel (current conditions from available layers + source + timestamp).
- NO accident/fatality/injured KPIs (no source). Live KPIs: reporting sources online,
  open incidents count (labeled), cities with severe weather, last refresh.

## Refresh strategy
- Server cron/fetcher: TomTom incidents 5–10 min; flow tiles client-cached 5 min;
  Open-Meteo 30–60 min (8–10 cities, one batched call each cycle); CKAN/data.gov.in
  watch weekly; MoRTH/NCRB/PIB pages weekly (conditional GET).
- Browser polls OUR `/api/live/*` only (60s), never external APIs. Keys stay server-side.

## Source indicator (every layer)
`Source: XYZ | Status: 🟢/🟡/🔴 | Last updated: HH:MM IST`. Stale (>2× interval) → 🟡;
fetch failure → 🔴 + last-good timestamp.

## Data Watch
Poll list (source, catalog URL, last-checked, new-items). New item stores:
name, source, pub date, detection date, URL, type, coverage, relevance flag,
validation status (UNVALIDATED default). No auto-integration.

## Reliability tiers
T1 gov official (IMD link, data.gov.in, MoRTH/NCRB pages) · T2 public infra
(Open-Meteo, OSM, OpenCity CKAN, Leaflet) · T3 commercial verified (TomTom/HERE,
key required) · T4 secondary · T5 unverified. Live site uses T1–T3 only.

## Limitations (honest)
Live accidents UNAVAILABLE (iRAD restricted) · hazards PARTIAL (TomTom categories only) ·
traffic needs user API key (no keyless verified option) · IMD has no open API ·
state-level weather is city-proxy, not state measurement · free-tier quotas bound refresh.

## Implementation order
- 13.2: backend live blueprint + cache + Open-Meteo weather layer + map shell + source badges.
- 13.3: TomTom incident+flow layers (key via env), state hover/click, refresh loop.
- 13.4: Data Watch (CKAN open first, data.gov.in keyed, page checks), strict research separation tests.
