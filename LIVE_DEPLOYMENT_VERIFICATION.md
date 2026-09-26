# Live Deployment Verification

- URL: https://morth-accident-analytics.onrender.com
- Commit: f256aef (master, pushed 2026-09-26; HTML markers tbody-yoy + honest KPIs confirmed served)
- Service: srv-dare9mm0tbcc73b8b5ig (Render, Docker python:3.12-slim, free)
- Repo: MALIK1525/morth-accident-analytics
- Dataset: MoRTH_Primary_Dataset_3.xlsx — 254 rows, 38 entities, 2018–2024, 0 reconciliation mismatches
- Supporting CSVs in repo/deploy: NONE (only .gitkeep + README). Searched attachments + workspace:
  the 13 analysis CSVs exist nowhere here; only their audit register does.

## Module table (all tested against the LIVE URL)

| MODULE | DATA | API | LIVE STATUS | VISUAL STATUS | RESULT |
|---|---|---|---|---|---|
| Home/dashboard shell | static HTML | GET / → 200, 70KB | PASS | renders | PASS |
| Filters (state/year/zone) | 38/7/6 options | /api/metadata 200 | PASS | wired | PASS |
| KPIs | panel sums | POST /api/kpis 200 | PASS | honest defaults | PASS |
| G1–G10 charts | 254-row panel | POST /api/visualization/G1 200 | PASS | renderers present | PASS |
| Stats (slopes/corr/threshold/YoY/fat-slopes) | live OLS | GET /api/statistical_analysis 200 | PASS | tables+heatmap | PASS |
| ML train | 141 train / 72 test | POST /api/train_ml 200 live | PASS | comparison+AvP | PASS |
| ML honesty | naive RMSE 1038.6 < GBR 2066.3, computed live | same | PASS | banner shows both | PASS |
| Risk tiers | trained RF 78.87% | same payload | PASS | labelled trained | PASS |
| Weather | no files | GET /api/weather/analytics → UNAVAILABLE | PASS | readiness panel | BLOCKED_BY_DATA |
| Supporting VH/CS/CL/EX/DL/SD/CT | no files | POST .../CL-01 → honest error | PASS | exact filename shown | BLOCKED_BY_DATA |
| Audit reconciliation | panel sums | GET /api/audit_details 200, zero_mismatch | PASS | table renders | PASS |
| Research audit | uploaded CSVs | /api/register 200 (37), /api/audit-files 200 (40) | PASS | cards+charts+tables | PASS |
| Registry/catalog | workbooks | /api/catalog 200 (21 analyses) | PASS | tables render | PASS |
| PDF report | live compute | GET /api/download_pdf_report 200, ~10KB | PASS | downloads | PASS |
| CSV/XLSX/slopes export | live compute | 200s | PASS | download links | PASS |
| Upload | validation+mapping | POST /api/upload_dataset (code path tested) | PASS | mapping UI | PASS |

## Honesty checks
- No hardcoded ML numbers anywhere (pdf_generator fixed; ML tab placeholders "—").
- No fabricated weather/causes/vehicles; unavailable modules name the missing file.
- Static HTML contains no pre-JS false claims (fixed 36.4%/44.7%/IMD-active defaults).
- KNN labelled supervised; K-Means unsupervised; classifier labelled trained.

## Tests
23/23 pytest pass (incl. test_ml_chrono, test_repaired_modules).

## Known limitations
- Supporting charts need the 13 MoRTH CSVs (exist only on user's /home/z machine).
- Free-tier sleeps after idle (~30s cold start).
- Browser console not directly inspectable from here; JS verified by code audit + API contract
  check (14 fetches all match backend routes).
