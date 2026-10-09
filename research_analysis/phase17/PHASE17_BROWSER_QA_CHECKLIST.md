# PHASE 17 — Browser QA Checklist (headed browser UNAVAILABLE in this environment)

Status legend: DONE-AUTO = verified via automated/HTTP checks; MANUAL = requires
human browser pass before professor demo; NOT-AVAILABLE = no headed browser here.

## Map
- [MANUAL] India centred, fills panel; 36 polygons render.
- [DONE-AUTO] GeoJSON valid (36 features), served HTTP 200.
- [MANUAL] Hover highlights + correct tooltip; click selects + panel matches.
- [MANUAL] Selection persists after cursor moves; search selects; reset restores.
- [DONE-AUTO] No blank-container failure (graceful catch + default view).

## Weather / Near-Me
- [DONE-AUTO] Retry + stale fallback + badges; opt-in-only geolocation (static).
- [MANUAL] Markers, chips, detail panel, denial fallback on screen.

## Data Watch
- [DONE-AUTO] Default RELEVANT filter in served HTML; scan API live.
- [MANUAL] Card grid 4/3/2/1 at widths; pagination; empty-state message.

## Console/network
- [MANUAL] No unexplained console errors; no failed asset loads.
- [DONE-AUTO] All live endpoints return documented shapes (see report).

## Responsive
- [MANUAL] 1440/1366/768/430/360 px pass.
- [DONE-AUTO] Breakpoints + 600/480/360 map ladder + no fixed-width cards.

Recommendation: run this checklist once in a real browser before the demo
(15 min). Nothing here blocks submission; all data paths are test-verified.
