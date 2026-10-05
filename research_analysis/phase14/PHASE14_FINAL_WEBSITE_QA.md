# PHASE 14 — Final Website QA

## Architecture audit
Single Flask app: research blueprint (benchmark/stats/ML/audit/upload) + live
blueprint (`app/live/`: weather, traffic, watch) sharing only the Flask app object.
Browser→backend→provider for all live data; keys server-side (env).

## Research/live separation
Labels: VERIFIED RESEARCH DATA (dashboard) vs LIVE EXTERNAL DATA (/live).
Live modules import nothing from benchmark/ML agents (static tests); live API
calls leave audit_details byte-identical (functional test). No retrain/recalc/
overwrite/merge/promote surface exists.

## Chart audit
All Plotly builders in `app/static/js/app.js`; centralized BW helpers defined
exactly once; G6/G9 bind per-name symbol+dash; single-series graphs kept clean;
error fallback retries all-data view once, then honest notice. No
"bwStyle is not defined" possible (definition verified).

## Black-and-white audit
Multi-series lines: distinct symbol+dash; bars: hatch+outline; heatmaps: Greys;
incidents/weather: shape+symbol; legends textual. Colour supplementary everywhere.

## Live monitor audit
Map/22.5,79.5 z5, toggles, legends, filters, freshness ages, hazards derived
from feeds only, disclaimers, awaiting-key/unavailable states honest.

## Data Watch audit
OpenCity live, MoRTH hash, data.gov.in key-gated, NCRB unavailable-card,
PIB manual card; NEW/UPDATED/KNOWN + relevance/vintage/exposure; geo+exposure
filters; review_queue confinement; ephemeral-history disclosure.

## Responsive / accessibility / performance / security
Tailwind grids, 360 px mobile map query, text-based statuses, single 5-min loop,
TTLs 300/120/180, 300-marker cap, server-side keys, secret regex tests.
Headed-browser screenshots unavailable here — structural QA only (honest).

## Demo flow
`FINAL_SUBMISSION_PACKAGE/07_DEFENSE/FINAL_LIVE_WEBSITE_DEMO_FLOW.md`
(4-step professor script with failure fallbacks).

## Limitations
External: TomTom/data.gov.in keys not supplied; NCRB blocks bots; PIB no feed;
history ephemeral; city-proxy weather. Environment: no headed browser here.

## Tests
142/142 (130 baseline + 12 integration). Issues fixed in PHASE14_ISSUES_AND_FIXES.md.
