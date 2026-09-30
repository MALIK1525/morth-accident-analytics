# BLACK_WHITE_GRAPH_ACCESSIBILITY_AUDIT

Centralized style in `app/static/js/app.js`: `BW_SYMBOLS` (10 Plotly symbols),
`BW_DASHES` (6 dash styles), `BW_PATTERNS` (8 bar fill patterns),
helpers `bwStyle` / `bwLine` (marker symbol + dash + 9px marker + dark outline)
and `bwBar` (hatch pattern + dark outline). Color retained as supplementary only.

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
