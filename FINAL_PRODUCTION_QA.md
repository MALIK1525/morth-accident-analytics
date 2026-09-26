# Final Production QA

Date: 2026-09-26. Scope: genuine fixes only, no rebuild, no new data.

## Bugs found and fixed
1. G3 hardcoded injury array contradicted verified benchmarks (2020: 348279 vs 346747;
   2021: 386452 vs 384448; 2023: 462100 vs 462825; 2024: 468500 vs 471441).
   Fixed: G3 now sums the CLEAN panel per year (2018–2022) and uses India-level
   benchmarks for 2023–2024 with per-year coverage labels. Verified live values:
   [464715, 449360, 346747, 384448, 443366, 462825, 471441].
2. Misleading status text claimed supporting modules "integrated" — replaced with the
   exact honest sentence.
3. Static KPI default showed fabricated 468,500 before JS loads — replaced with "—";
   injuries card now carries a coverage note (state-wise verified through 2022).
4. KPI injuries for scopes with zero published values returned misleading sums/0 —
   now returns "N/A" with explanation (e.g. Punjab 2024, All-years 2023/2024 views
   exclude unpublished state-wise injuries instead of zero-filling).
5. Full-repo sweep: no remaining hardcoded 0.684 / 1,124 / 36.4% / 44.7% / 71.6% claims.

## KPI definitions (all respect the active State/Year/Zone filter)
| KPI | Value (All Years) | Formula / scope |
|---|---|---|
| Total Crashes | 3,141,577 | sum(Accidents) over filtered rows |
| Fatalities | 1,127,488 | sum(Fatalities) over filtered rows |
| Injuries | 2,088,636 cumulative (2018–2022 state panel) | sum of non-null Injured in scope; "N/A" when scope has none; 2023–24 state-wise unpublished (India 462,825 / 471,441, India views only) |
| Deaths / 100 Crashes | 35.89 | fatalities/accidents×100 over scope (ratio, not mortality rate) |
| Avg Annual Crashes | total / distinct years in scope | clearly a scope mean |
| Peak Crash Year | 2024 | argmax of yearly sums in scope |

## QA results
- Filters: All Years + 2018–2024 + 7 spot states + 6 zones — KPIs change consistently;
  per-year accidents/fatalities match verified benchmarks exactly (470403/157593 … 487707/177175).
- Statistics: slopes/R²/p-values/trajectory/YoY/fatality-slopes/correlation/thresholds all
  served live; methodology + causation disclaimer in UI.
- ML: live retrain verified (naive RMSE 1038.6 best overall; GBR 2066.31 best trained);
  KNN labelled supervised, K-Means unsupervised, tiers labelled trained.
- Weather: UNAVAILABLE with readiness panel (IMD GRID→STATE→MoRTH pipeline specified).
- Audit/registry/catalog/reports: all render from real rows; PDF/CSV/XLSX download live.
- Tests: 23/23 pass. Contract audit: 14/14 frontend fetches match backend routes.

## Remaining limitations (data, not bugs)
Supporting charts (VH/CS/CL/EX/DL/SD/CT) await the 13 MoRTH CSVs, which exist only on the
user's /home/z machine; cards name the exact expected file and auto-activate on drop-in.
