# PHASE 26 — Mode-Aware Dashboard: Separate Weather & Traffic Information

## Root cause
The incident click handler in `app/static/js/live.js` (`drawIncidents`) rendered TomTom
incident details into `#weather-detail` / `#detail-sub` — the "Current Weather" card. The tab
switch (`showTab`) toggled only the maps, never the sidebar or KPI area. So in Traffic mode a
jam ("Backed up traffic", "Moderate delay", TomTom source) appeared under a "Current Weather"
heading. Weather KPIs also stayed visible in Traffic mode.

## Files changed
- `app/templates/live.html` — weather card gained `id="card-weather"`; new hidden
  `id="card-traffic"` ("Current Traffic", `#traffic-detail`, TomTom NOT-record attribution);
  Near-Me card gained `id="card-nearme"`; new hidden traffic KPI grid
  (`#live-kpis-traffic`: `kpi-tflow/kpi-tinc/kpi-tclose/kpi-tcov`) with honest coverage note.
- `app/static/js/live.js` — new `showTrafficDetail()` (writes only to `#traffic-detail`);
  incident clicks and road-segment clicks now render there (segment also keeps its map popup);
  new `applyModePanels()` toggles weather card / traffic card / Near-Me / both KPI grids +
  notes; `showTab()` calls it; `loadTraffic`/`loadIncidents` fill traffic KPIs
  (flow status, incident count, closure count via /clos/i, coverage label; "Unavailable" on error).
- `app/static/js/india_map.js` — boot applies weather mode panels.
- Bundle version `ph21` → `ph26` (cache-bust).
- `tests/test_phase26.py` — 7 regression tests (traffic card exists/hidden by default;
  incident handler targets traffic card, never `#weather-detail`; all 7 panels toggled;
  traffic KPIs present; no TomTom attribution inside weather card; served page contains both
  cards + ph26 bundle).
- `probe_mode26.py` — Playwright mode-switch verification script.

## Browser verification (Playwright, deployed, zero console errors)
- Weather mode: card-weather ✓ visible, card-traffic hidden, Near-Me ✓, weather KPIs ✓,
  traffic KPIs hidden.
- Traffic mode: card-traffic ✓, weather card hidden, Near-Me hidden, traffic KPIs
  (Live / 309 incidents / 136 closures / monitored-city coverage).
- Incident click (Jam, Basai Road, "Slow traffic", "Minor delay (provider-reported)"):
  renders in Current Traffic with NOT-official-record label; `#weather-detail`
  byte-identical before/after (WEATHER UNCHANGED: True).
- Traffic → Weather: weather card returns with weather content, no TomTom text.
- Screenshots: `ph26_traffic.png` (clusters, incident list, live legend counts
  Jam 156 / Road closed 136 / Road works 8), `ph26_weather.png`. No duplicate maps.

## Deployment note (important for future phases)
Render tracks the **`main`** branch, not `deploy-slim`. Pushing Phase 26 to `deploy-slim`
alone did NOT deploy (verified: served bundle stayed `v=ph21` for 15+ min). After
cherry-picking `ff27180` + `4d86680` onto `main` as `15cf2e2` + `1858cb7` and pushing,
`v=ph26` was live within ~1 min. `deploy-slim` was reset to `main` so both agree.

## Tests & integrity
- Full suite: **205/205 passed** (198 + 7 new).
- Benchmark: `test_benchmark_checksum_unchanged` (`d8064caa…`) passes; research untouched.
- Weather, state boundaries/search, Near-Me, tile proxy, clustering, Data Watch unaffected.
- Key server-side only; no new endpoints; no fabricated values.

## Commit & status
- `main`: `1858cb7` (Phase 26); `deploy-slim` synced. Deployed and browser-verified.
- Acceptance criterion met: "Current Weather" never heads TomTom incident content.
