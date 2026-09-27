# Website Phase 1 Changelog — final audit and production repair

## BUG-1: G10/audit NaN leak (blank tables/charts)
- Repro: `GET /api/g10_slopes` raw body contained `NaN` (2 legacy rows: Dadra & Nagar Haveli, Daman & Diu, N=2).
- Root cause: pandas NaN serialized by Flask into invalid JSON; frontend JSON parse / Plotly choked.
- Fix: `_json_safe()` in `app/server.py` converts non-finite → null; applied to g10, statistical_analysis, audit_details. Null is never coerced to 0.
- Test: `test_no_nan_leak_in_json`, `test_g10_insufficient_rows_are_null_not_nan`.

## BUG-2: Variable Registry blank (API contract mismatch)
- Repro: frontend read `dataMeta.discovery.variable_registry`, backend `get_summary()` never sent that key (only `get_summary` omitted it; `discover_all` had it) → `tbody-variable-registry` stayed "Loading…".
- Root cause: `DataDiscoveryAgent.get_summary()` dropped the `variable_registry` field.
- Fix: added `"variable_registry": self.variable_registry` to `get_summary()` (168 rows now served).
- Test: `test_registry_contract`.

## BUG-3: G9 ignored State filter
- Repro: `POST /api/visualization/G9 {state:Punjab}` returned all 8 illustrative states.
- Root cause: `_generate_g9` hardcoded the illustrative list, never read `filters`.
- Fix: honor `state` (single-state series) and `zone` filters; default list otherwise.
- Test: `test_g9_honors_state_filter`.

## Verified, no change needed
- Hardcoded-value sweep (468500/348279/386452/462100/0.684/36.4%/44.7%/71.6%): zero hits in app code.
- ML train live: Naive 1038.6 < GBR 2066.31 — matches Phase 5; baseline shown first, KNN labelled supervised.
- KPI injury: Punjab-2024 → "N/A" with coverage note (test added).
- Benchmarks: 2018 (470403/157593), 2024 (487707/177175) MATCH via audit_details.
- SVG export: `Plotly.downloadImage(..., {format:'svg'})` wired per-card; no dead code found (browser-run not possible here).
- Weather/supporting modules: honestly unavailable (no verified CSVs in `data/supporting_csv/`); no fake data added.

## Research impact
NONE — research values, methodology, and Phase 1–10 outputs untouched.
