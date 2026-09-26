# Implementation Changelog

## Session A — honest rebuild (verified 25/25)
- Removed 7 fabricated `supporting_*.csv` files; Tiers 4–10 report NOT AVAILABLE with reasons.
- Removed hardcoded KPI claims (36.4% etc.) → "Awaiting data".
- Added missing G6/G9/G10 Plotly renderers; fixed G5 fixed-index crash.
- Fixed `/api/metadata` zone crash and PDF `is_trained` crash; added ML method aliases.
- Plotly switched to CDN; added `render.yaml`, `Dockerfile`; deployed to Render (Docker, python:3.12-slim).
- Files: `app/server.py`, `app/agents/visualization_agent.py`, `app/analytics/ml_models.py`,
  `app/static/js/app.js`, `app/templates/index.html`, `Dockerfile`, `render.yaml`.

## Session B — supporting-CSV engine + audit dashboard
- New `app/data_pipeline/supporting_loader.py`: drop-in `data/supporting_csv/` ingestion,
  Indian-number parsing, `% share` row filtering, schema matching, India-total checks.
- Catalog entries DL-01/SD-01/CT-01 added; statuses flip AVAILABLE on real files only.
- New endpoints: `/api/supporting`, `/api/availability`, `/api/register`, `/api/audit-files`.
- New dashboard cards VH/CS/CL/EX/DL/SD/CT + Research Audit section (register, issues, readiness charts).
- User audit CSVs committed (register, availability, parameter status, issues, cleaning log).

## Session C — master upgrade
- ML rewritten: chronological split (train 2018–2022, test 2023–2024), lag-only features,
  naive baseline + 5 trained regressors, RMSE primary, actual-vs-predicted + comparison table.
  Result: naive baseline wins (RMSE 1038.6), best trained GBR (RMSE 2066.3). Reported honestly.
- Stats: fatality slopes + India YoY table added to `/api/statistical_analysis`.
- ML tab: removed pre-training fake numbers; fixed result key mapping.
- Weather: no IMD files present in workspace (audit confirms NOT ACQUIRED) → module stays
  honestly unavailable; pipeline specified in WEATHER_METHODOLOGY.md.
- Docs: IMPLEMENTATION_CHANGELOG.md, DATA_PROVENANCE.md, ML_METHODOLOGY.md,
  STATISTICAL_METHODOLOGY.md, WEATHER_METHODOLOGY.md, DATA_AVAILABILITY_MATRIX.md.
