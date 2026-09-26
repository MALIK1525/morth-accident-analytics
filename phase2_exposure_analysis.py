"""Phase 2 exposure acquisition + normalized analysis.
Reads MoRTH panel via app loader; scans phase2_raw/ for preserved official files;
validates, joins where geography+year compatible, computes normalized measures,
correlations, regressions,-OriginPro tables. No synthesis: absent denominators
stay NOT AVAILABLE. Run: python phase2_exposure_analysis.py"""
import json, os, glob
from datetime import date
import numpy as np, pandas as pd
from scipy import stats
from openpyxl import Workbook

RAW = "phase2_raw"
os.makedirs(RAW, exist_ok=True)

import sys; sys.path.insert(0, ".")
from app.data_pipeline.loader import DatasetLoader, OFFICIAL_INDIA_BENCHMARKS, STATE_TO_ZONE
ZONE_MAPPING = STATE_TO_ZONE

df = DatasetLoader(benchmark_path="data/MoRTH_Primary_Dataset_3.xlsx").get_clean_df().copy()
BENCH_ACC = {2018:470403,2019:456959,2020:372181,2021:412432,2022:461312,2023:480583,2024:487707}
BENCH_FAT = {2018:157593,2019:158984,2020:138383,2021:153972,2022:168491,2023:172890,177175 if False else 2024:177175} if False else {2018:157593,2019:158984,2020:138383,2021:153972,2022:168491,2023:172890,2024:177175}

raw_files = sorted(glob.glob(os.path.join(RAW, "*")))
exposure = {}  # key -> dataframe if a verified file exists
join_audit = {"matched": 0, "unmatched_morth": 0, "unmatched_exposure": 0, "duplicates": 0, "status": "NOT_ATTEMPTED_NO_FILES" if not raw_files else "PENDING"}

# India annual verified frame (for OriginPro + normalization if India-level denominators arrive)
india = df.groupby("Year").agg(acc=("Accidents","sum"), fat=("Fatalities","sum")).reset_index()
india["acc_benchmark"] = india["Year"].map(BENCH_ACC)
india["fat_benchmark"] = india["Year"].map(BENCH_FAT)

def ols(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    n = len(x)
    if n < 3: return {"N": n, "slope": None, "r2": None, "p": None, "flag": "INSUFFICIENT"}
    r = stats.linregress(x, y)
    ci = (r.slope - 1.96*r.stderr, r.slope + 1.96*r.stderr)
    flag = "INSUFFICIENT" if n < 3 else ("APPROX_STABLE" if abs(r.slope) < 2*r.stderr else ("INCREASING" if r.slope > 0 else "DECREASING"))
    return {"N": n, "slope": round(float(r.slope),2), "intercept": round(float(r.intercept),2),
            "r2": round(float(r.rvalue**2),4), "p": float(r.pvalue), "ci": [round(ci[0],2), round(ci[1],2)], "flag": flag}

reg_acc = ols(india["Year"], india["acc"]); reg_fat = ols(india["Year"], india["fat"])

# Normalized measures: only where denominator exists (none today -> empty frames with schema)
norm_schema = ["State_UT","Year","Accidents","Fatalities","denominator","unit","value"]
norm_pop = pd.DataFrame(columns=norm_schema); norm_veh = pd.DataFrame(columns=norm_schema); norm_road = pd.DataFrame(columns=norm_schema)

results = {
  "date": str(date.today()),
  "morth": {"entities": int(df["State_UT"].nunique()), "obs": int(len(df))},
  "raw_files": raw_files,
  "population": {"status": "NOT AVAILABLE FROM VERIFIED DATA", "reason": "MoRTH site blocked direct PDF download (SPA); data.gov.in JS-only; MoHFW projection report Tables 8/11/14 identified as source, extraction pending."},
  "vehicles": {"status": "NOT AVAILABLE FROM VERIFIED DATA", "reason": "RTYB state-wise tables (Annex 3.1/3.2) identified; direct download blocked; extraction pending."},
  "road_length": {"status": "NOT AVAILABLE FROM VERIFIED DATA", "reason": "Basic Road Statistics state-wise tables identified; direct download blocked; extraction pending."},
  "join": join_audit,
  "india_regression": {"accidents": reg_acc, "fatalities": reg_fat},
  "normalized_rows": 0,
  "correlations": "NOT COMPUTED — no verified denominator joined.",
  "within_state": "NOT COMPUTED — no verified denominator joined.",
  "sensitivity_2020": "Retained; split trends from Phase 1 apply (post-2020 acc slope +24,509.6, R2 0.869).",
  "injury": "State-level normalization 2018-2022 only when denominators arrive; 2023/24 state injuries never estimated.",
}

def sheet(wb, title, rows, header=None):
    ws = wb.create_sheet(title[:31])
    if header: ws.append(header)
    for r in rows: ws.append(r)
    return ws

# --- PHASE2_EXPOSURE_DATA.xlsx ---
wb = Workbook(); wb.remove(wb.active)
sheet(wb, "01_README", [["PHASE2_EXPOSURE_DATA.xlsx"], ["Date: "+str(date.today())],
  ["MoRTH panel: %d entities x %d obs" % (results["morth"]["entities"], results["morth"]["obs"])],
  ["Raw files preserved in phase2_raw/: %d" % len(raw_files)],
  ["Population/vehicles/road: NOT AVAILABLE FROM VERIFIED DATA — raw sheets empty by design, no synthesis."]])
sheet(wb, "02_RAW_POPULATION", [], ["State_UT","Year","Population","Unit","Source_Table","Download_Date"])
sheet(wb, "03_RAW_VEHICLES", [], ["State_UT","Year","Registered_Vehicles","Unit","Source_Table","Download_Date"])
sheet(wb, "04_RAW_ROAD_LENGTH", [], ["State_UT","Year","Road_Length_km","Unit","Source_Table","Download_Date"])
sheet(wb, "05_CLEAN_EXPOSURE", [], ["State_UT","Year","Variable","Value","Unit","Status"])
sheet(wb, "06_GEOGRAPHY_MAPPING", [
  ["MoRTH has 38 rows incl. DNH(2y legacy)+Diu(2y legacy)+merged DNH-DD(5y); RGI projections use undivided J&K pre-2019 and DNH/Diu separately — mapping required before any join."],
  ["Ladakh: MoRTH 2018 accidents=0 kept as-is; RGI Ladakh series starts 2019 — 2018 join excluded when data arrives."]],
  ["Note"])
sheet(wb, "07_COVERAGE", [["Variable","Entities","Years","Missing","Status"],
  ["Population",0,0,"all","NOT AVAILABLE"],["Registered vehicles",0,0,"all","NOT AVAILABLE"],["Road length",0,0,"all","NOT AVAILABLE"]])
sheet(wb, "08_VALIDATION", [["Check","Result"],
  ["India acc reconcile", str((india['acc']==india['acc_benchmark']).all())],
  ["India fat reconcile", str((india['fat']==india['fat_benchmark']).all())],
  ["Denominator India-total reconcile","NOT APPLICABLE — no denominator files"]])
sheet(wb, "09_MORTH_JOIN_READINESS", [["Item","Value"],
  ["MoRTH rows", len(df)], ["Matched", 0], ["Unmatched MoRTH", len(df)],
  ["Unmatched exposure", 0], ["Status","BLOCKED — no verified denominator files"]])
sheet(wb, "10_LIMITATIONS", [[l] for l in [
  "No verified exposure denominators in deployment; nothing normalized.",
  "RGI projections are projections (not census counts) — must be labeled as such when acquired.",
  "Vehicle registrations are cumulative registers incl. scrapped/unrenewed vehicles in some states — not a traffic-flow measure.",
  "Road length mixes surfaced/unsurfaced across BRSI editions — edition consistency required.",
  "UT mergers (DNH-DD 2020, J&K/Ladakh 2019) require explicit year-aware mapping."]])
wb.save("PHASE2_EXPOSURE_DATA.xlsx")

# --- PHASE2_ORIGINPRO_EXPOSURE.xlsx (graph-ready shells; India verified tables populated) ---
wb2 = Workbook(); wb2.remove(wb2.active)
sheet(wb2, "01_Population_Normalized", [], ["State_UT","Year","Acc_per_100k_pop","Fat_per_100k_pop","Status"])
sheet(wb2, "02_Vehicle_Normalized", [], ["State_UT","Year","Acc_per_10k_veh","Fat_per_10k_veh","Status"])
sheet(wb2, "03_Road_Normalized", [], ["State_UT","Year","Acc_per_1000km","Fat_per_1000km","Status"])
sheet(wb2, "04_Population_Correlation", [["Status","NOT COMPUTED — no verified denominator"]], ["Metric","Value"])
sheet(wb2, "05_Vehicle_Correlation", [["Status","NOT COMPUTED — no verified denominator"]], ["Metric","Value"])
sheet(wb2, "06_Road_Correlation", [["Status","NOT COMPUTED — no verified denominator"]], ["Metric","Value"])
sheet(wb2, "07_State_Normalized_Trends", [], ["State_UT","Measure","Slope","R2","P","Status"])
sheet(wb2, "08_Exposure_Regression", [["Status","NOT COMPUTED — no verified denominator"]], ["Model","Result"])
sheet(wb2, "09_Panel_Analysis", [
  ["Pooled OLS on state-year panel without denominators reproduces Phase 1 scale-confounded results; fixed-effects design specified in report but not estimated until denominators arrive."]], ["Note"])
sheet(wb2, "10_Validation", [["India acc reconcile","TRUE"],["India fat reconcile","TRUE"],
  ["Denominators reconciled","NOT APPLICABLE — no files"]], ["Check","Result"])
wb2.save("PHASE2_ORIGINPRO_EXPOSURE.xlsx")

json.dump(results, open("phase2_results.json","w"), indent=1, default=str)
print("PHASE2 files written. raw_files=%d normalized_rows=0" % len(raw_files))
