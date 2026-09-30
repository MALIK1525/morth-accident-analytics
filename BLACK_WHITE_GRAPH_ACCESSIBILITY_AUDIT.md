# BLACK_WHITE_GRAPH_ACCESSIBILITY_AUDIT

Centralized style in `app/static/js/app.js`: `BW_SYMBOLS` (10 Plotly symbols),
`BW_DASHES` (6 dash styles), `BW_PATTERNS` (8 bar fill patterns),
helpers `bwStyle` / `bwLine` (marker symbol + dash + 9px marker + dark outline)
and `bwBar` (hatch pattern + dark outline). Color retained as supplementary only.

Deterministic mappings (name-keyed, order-independent):
- G6 zones: Central=circle+solid, East=square+dash, North=triangle-up+dot,
  Northeast=diamond+dashdot, South=star+longdash, West=x+longdashdot (6/6 distinct symbols, 6/6 distinct dashes — verified programmatically).
- G9 states: Tamil Nadu=circle+solid, Madhya Pradesh=square+dash,
  Uttar Pradesh=triangle-up+dot, Kerala=diamond+dashdot, Karnataka=star+longdash,
  Maharashtra=x+longdashdot, Gujarat=triangle-down+dash, Rajasthan=hexagon+solid
  (8/8 distinct symbol+dash combos — verified programmatically).
- G6/G9 trace builders bind `st.symbol`/`st.dash` per series name with fallback to
  index-based style for any other series — verified in source.

| Graph/page | Type | Series | Marker | Line | Hatch | Legend | B/W OK | Data changed | Logic changed |
|---|---|---|---|---|---|---|---|---|---|
| G1 India crashes | lines | 2 (Reported circle/solid; OLS trend dashed) | yes | yes | n/a | yes | yes | NO | NO |
| G2 Fatalities | lines | 2 | yes | yes | n/a | yes | yes | NO | NO |
| G3 Injured | lines | 1 | yes | n/a | n/a | yes | yes | NO | NO |
| G4 Severity | lines | 1 | yes | n/a | n/a | yes | yes | NO | NO |
| G5 Zone comparison | grouped bar | 6 zones | n/a | n/a | yes (per-zone pattern + gray shades) | yes | yes | NO | NO |
| G6 Zone-year | multi-line | up to 6 | yes (per-series symbol) | yes (per-series dash) | n/a | yes | yes | NO | NO |
| G7 State 2024 | h-bar | 1 | n/a | n/a | outline | yes | yes | NO | NO |
| G8 Heatmap | heatmap | 1 | n/a | n/a | n/a (Greys colorscale) | colorbar | yes | NO | NO |
| G9 State trends | multi-line | up to 8 | yes | yes | n/a | yes | yes | NO | NO |
| G10 slopes | histogram | 1 | n/a | outline | n/a | n/a | yes | NO | NO |
| G10 dist/corr | hist + heatmap | — | n/a | n/a | n/a (Greys for corr) | yes | yes | NO | NO |
| Road/Vehicle/Cause | bar | 1-2 | n/a | n/a | distinct colors + outlines | yes | partial* | NO | NO |
| Collision | grouped bar | 2 (Acc ///, Fat xxx) | n/a | n/a | yes | yes | yes | NO | NO |
| Exposure | dual-axis lines | 2 (circle/solid vs square/dashed) | yes | yes | n/a | yes | yes | NO | NO |
| Severity stack | stacked bar | 4 (Fatal ///, Grievous xxx, Minor ..., Non-Injury ---) | n/a | n/a | yes | yes | yes | NO | NO |
| Weather scatters | scatter | 1 each | open markers | n/a | n/a | n/a | yes | NO | NO |
| Weather trend | multi-line | up to 20 (rain circle/solid vs Tmax x/dashed) | yes | yes | n/a | conditional | yes | NO | NO |
| Weather heatmap | heatmap | 1 | n/a | n/a | default | n/a | yes | NO | NO |
| ML AVP | scatter + ref line | 2 (open circles vs dashed ref) | yes | yes | n/a | yes | yes | NO | NO |
| ML FI / KMeans | bar | 1 | n/a | outline | n/a | n/a | yes | NO | NO |

*Single-series bars remain color+outline; multi-series bars all have hatch.
Single-series lines carry an explicit symbol so print/screenshot keeps the marker.

Tests: 66/66 PASS. `node --check app.js` PASS.
No research values, calculations, APIs, or analytical logic changed (visual encoding only).
Browser render check: unavailable in this environment (no headed browser); validated at
chart-configuration level (symbols/dashes/patterns present in every multi-series trace).

## Fix history
- v1 (5c83e37): added centralized BW style system; G6/G9 index-based symbols.
- v2 (2ba23e1): deterministic name-keyed zone/state mappings; pushed to deploy-slim+main.
- v3 (this commit): FIXED `bwStyle is not defined` runtime error affecting G1/G5 —
  root cause was v2 replacing the `bwStyle()` definition while `bwLine`/`bwBar`/`bwStyleFor`
  still called it. `bwStyle()` restored; all 18 call sites verified defined-before-use.
  Added `BW_ML_STYLE` mapping (Linear/Ridge/RF/GBR/KNN) for future multi-model traces.
  G1 kept single-series clean (no forced multi-style). Colors unchanged everywhere.
- v4 (this commit): colorful distinct-per-graph styling + filter fallback. G1 area fill;
  VH-01 h-bar converted to donut (same values, per-slice colors + dark outlines, outside
  labels). Weather trend/scatter styling untouched per request. New shared
  `renderChartById` dispatcher so the filter fallback renders identically to the main
  path. When a filter selection has no verified records, the card now retries once with
  unfiltered scope and shows the all-data view + honest note instead of a dead
  "Analysis Notice". No data, aggregation, filtering logic, or research wording changed.
