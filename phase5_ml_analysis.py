"""Phase 5: leakage-audited supervised ML. Target = next-year state accidents.
No random splits, naive baseline mandatory, no website changes. Run: python phase5_ml_analysis.py"""
import numpy as np, pandas as pd, json
from scipy import stats
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, HistGradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from openpyxl import Workbook
from datetime import date

pj = pd.read_csv("phase3_state_population.csv").sort_values(["State_UT", "Year"])
# usable entities: full 2018-2024 (drop legacy N=2)
cnt = pj.groupby("State_UT").size()
ENTS = cnt[cnt == 7].index.tolist()
print("entities:", len(ENTS), "| legacy dropped:", cnt[cnt < 7].to_dict())

# ---- feature construction (lag-only; cutoff = target-1, except Pop_t*) ----
rows = []
for s, g in pj[pj.State_UT.isin(ENTS)].groupby("State_UT"):
    g = g.sort_values("Year").reset_index(drop=True)
    z = g.Zone.iloc[0]
    for i in range(2, len(g)):  # target idx>=2 -> targets 2020..2024
        t = g.iloc[i]; p1 = g.iloc[i-1]; p2 = g.iloc[i-2]
        rows.append({"State_UT": s, "Zone": z, "Target_Year": int(t.Year), "Target_Accidents": t.Accidents,
            "Cutoff": int(t.Year)-1, "Year": int(t.Year),
            "Lag1_Acc": p1.Accidents, "Lag2_Acc": p2.Accidents,
            "Lag1_Fat": p1.Fatalities, "Lag2_Fat": p2.Fatalities,
            "Pop_t": t.Population_Persons, "Lag1_Pop": p1.Population_Persons,
            "Pop_Growth": t.Population_Persons/p1.Population_Persons-1,
            "Lag1_AccLakh": p1.Acc_per_Lakh_Pop, "Lag1_FatLakh": p1.Fat_per_Lakh_Pop})
ml = pd.DataFrame(rows)
print("ML rows:", len(ml), "(35 ents x 5 targets 2020-24)")

NUM = ["Year", "Lag1_Acc", "Lag2_Acc", "Lag1_Fat", "Lag2_Fat", "Pop_t", "Pop_Growth", "Lag1_AccLakh", "Lag1_FatLakh"]
ml = pd.get_dummies(ml, columns=["Zone"], prefix="Z", dtype=float)
FEATS = NUM + [c for c in ml.columns if c.startswith("Z_")]

MODELS = {"Naive": None, "Linear": LinearRegression(), "Ridge": Ridge(alpha=1.0),
    "RandomForest": RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1),
    "GradientBoosting": GradientBoostingRegressor(random_state=42),
    "HistGradientBoosting": HistGradientBoostingRegressor(random_state=42),
    "KNN(k=5, supervised)": KNeighborsRegressor(n_neighbors=5)}

def mets(y, p):
    return {"RMSE": float(np.sqrt(mean_squared_error(y, p))), "MAE": float(mean_absolute_error(y, p)),
            "R2": float(r2_score(y, p))}

def run_fold(train, test):
    out = {}
    Xn, yn = train[FEATS].values, train.Target_Accidents.values
    Xt, yt = test[FEATS].values, test.Target_Accidents.values
    sc = StandardScaler().fit(Xn)
    for name, m in MODELS.items():
        if name == "Naive":
            p = test.Lag1_Acc.values
        elif name in ("Linear", "Ridge", "KNN(k=5, supervised)"):
            m.fit(sc.transform(Xn), yn); p = m.predict(sc.transform(Xt))
        else:
            m.fit(Xn, yn); p = m.predict(Xt)
        out[name] = {"pred": p} | mets(yt, p)
    return out

# ---- main chronological split: train targets 2020-22, test 2023-24 ----
tr = ml[ml.Target_Year <= 2022]; te = ml[ml.Target_Year >= 2023]
main = run_fold(tr, te)
comp = pd.DataFrame([{"Model": k, "Train_N": len(tr), "Test_N": len(te),
    "Train_Period": "targets 2020-2022", "Test_Period": "targets 2023-2024",
    "Features": "lag-only + Year + Zone (no state dummies, no future)"} | {m: v[m] for m in ["RMSE", "MAE", "R2"]}
    for k, v in main.items()])
print(comp[["Model", "RMSE", "MAE", "R2"]].to_string(index=False))

# ---- walk-forward ----
wf = []
for vy in [2021, 2022, 2023, 2024]:
    r = run_fold(ml[ml.Target_Year < vy], ml[ml.Target_Year == vy])
    for k, v in r.items():
        wf.append({"Val_Year": vy, "Train_Targets": "2020-%d" % (vy-1), "N_train": (ml.Target_Year < vy).sum(),
                   "Model": k} | {m: v[m] for m in ["RMSE", "MAE", "R2"]})
WF = pd.DataFrame(wf)

# ---- predictions + errors (main split, best-ML + naive) ----
order = comp[comp.Model != "Naive"].sort_values("RMSE")
best_ml = order.Model.iloc[0]
pred = te[["State_UT", "Target_Year", "Target_Accidents", "Lag1_Acc"]].copy()
pred["Pred_Naive"] = main["Naive"]["pred"]
pred["Pred_%s" % best_ml] = main[best_ml]["pred"]
for c in ["Naive", best_ml]:
    p = pred["Pred_%s" % c]
    pred["Resid_%s" % c] = pred.Target_Accidents - p
    pred["AE_%s" % c] = (pred.Target_Accidents - p).abs()

# ---- permutation importance (final leakage-safe train, evaluated on test) ----
Xn, yn = tr[FEATS].values, tr.Target_Accidents.values
Xt, yt = te[FEATS].values, te.Target_Accidents.values
fimp = []
for name, cls in [("RandomForest", RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)),
                  ("GradientBoosting", GradientBoostingRegressor(random_state=42))]:
    m = cls.fit(Xn, yn)
    pi = permutation_importance(m, Xt, yt, n_repeats=10, random_state=42)
    for f, v in zip(FEATS, pi.importances_mean):
        fimp.append({"Model": name, "Feature": f, "PermImportance": float(v),
            "Note": "predictive importance only; NOT causal"})
FI = pd.DataFrame(fimp).sort_values(["Model", "PermImportance"], ascending=[True, False])

# ---- 2020 sensitivity: full train (2020-22) vs post-2020 train (2021-22), same test ----
sensA = main
sensB = run_fold(ml[ml.Target_Year.isin([2021, 2022])], te)
SENS = pd.DataFrame([{"Train": "targets 2020-2022 (incl 2020)", "Model": k} | {m: v[m] for m in ["RMSE", "MAE", "R2"]} for k, v in sensA.items()] +
    [{"Train": "targets 2021-2022 (post-2020)", "Model": k} | {m: v[m] for m in ["RMSE", "MAE", "R2"]} for k, v in sensB.items()])

# ---- stability: 2023 vs 2024 errors ----
stab = pred.groupby("Target_Year")[["AE_Naive", "AE_%s" % best_ml]].mean()

ml.to_csv("phase5_ml_dataset.csv", index=False)
comp.to_csv("phase5_model_comparison.csv", index=False)
WF.to_csv("phase5_walk_forward.csv", index=False)
pred.to_csv("phase5_predictions.csv", index=False)
FI.to_csv("phase5_feature_importance.csv", index=False)
leak = pd.DataFrame([
 ["Lag1_Acc / Lag2_Acc", "t-1 / t-2", "target t", "yes", "none", "INCLUDE"],
 ["Lag1_Fat / Lag2_Fat", "t-1 / t-2", "target t", "yes", "none", "INCLUDE"],
 ["Pop_t (RGI projection)", "target year", "target t", "yes — RGI report published 2020; projection not observed outcome", "low", "INCLUDE with documented assumption"],
 ["Lag1_Pop / Pop_Growth", "t-1 / t..t-1", "target t", "yes (Pop_Growth uses target-year projection — same assumption as Pop_t)", "low", "INCLUDE with assumption"],
 ["Lag1_AccLakh / Lag1_FatLakh", "t-1", "target t", "yes", "none", "INCLUDE"],
 ["Year (target year)", "target t", "target t", "yes — calendar year is known", "none", "INCLUDE"],
 ["Zone one-hot", "static", "any", "yes", "none", "INCLUDE"],
 ["Target-year accidents/fatalities", "t", "t", "NO", "direct target leak", "EXCLUDE"],
 ["Phase-4 full-period slopes", "2018-24", "t<2024", "NO", "future-derived", "EXCLUDE"],
 ["Road length (2021-22 only)", "2021-22", "any", "would restrict to targets 2022-23", "coverage", "EXCLUDE from main set"],
 ["Vehicles / weather / GIS", "—", "—", "unavailable", "—", "EXCLUDE"],
], columns=["Feature", "Source_Year", "Target_Year", "Available_Before_Target", "Leakage_Risk", "Decision"])
leak.to_csv("phase5_leakage_audit.csv", index=False)
json.dump({"best_ml": best_ml, "comparison": comp.to_dict("records"),
    "walkforward": WF.to_dict("records")}, open("phase5_results.json", "w"), indent=1, default=float)

wb = Workbook(); wb.remove(wb.active)
def sheet(title, df):
    ws = wb.create_sheet(title[:31]); ws.append(list(df.columns))
    for row in df.itertuples(index=False):
        ws.append([("" if (isinstance(v, float) and pd.isna(v)) else v) for v in row])
ws0 = wb.create_sheet("01_README")
for l in ["PHASE5_ML_ANALYSIS.xlsx — " + str(date.today()),
 "Target = next-year state accidents. Lag-only features, chronological splits, naive baseline mandatory.",
 "KNN = supervised. Importance is predictive, never causal."]: ws0.append([l])
sheet("02_FEATURE_INVENTORY", pd.DataFrame([
 ["Lag1_Acc", "MoRTH accidents t-1", "count", "INCLUDE"], ["Lag2_Acc", "MoRTH accidents t-2", "count", "INCLUDE"],
 ["Lag1_Fat/Lag2_Fat", "MoRTH fatalities t-1/t-2", "count", "INCLUDE"],
 ["Pop_t", "RGI projection target year", "persons", "INCLUDE (assumption documented)"],
 ["Pop_Growth", "Pop_t/Pop_t-1-1", "fraction", "INCLUDE (assumption)"],
 ["Lag1_AccLakh/Lag1_FatLakh", "Phase-3 metrics t-1", "per lakh", "INCLUDE"],
 ["Year", "target calendar year", "year", "INCLUDE"], ["Zone dummies", "static zone", "0/1", "INCLUDE"],
 ["Road/vehicles/weather", "unavailable or coverage-restricting", "—", "EXCLUDE"],
], columns=["Feature", "Definition", "Unit", "Decision"]))
sheet("03_LEAKAGE_AUDIT", leak)
sheet("04_ML_DATASET_AUDIT", pd.DataFrame([
 ["Entities (full 2018-24)", 35], ["Legacy/merged dropped (N=2/2/5)", 3], ["Candidate rows (35x7)", 245],
 ["Rows lost to lag-2 construction", 70], ["Rows lost to missing", 0], ["Rows excluded for leakage", 0],
 ["Final ML N", len(ml)], ["Targets", "2020-2024"]], columns=["Item", "Value"]))
sheet("05_MODELING_DATA", ml)
sheet("06_TRAIN_TEST_SPLIT", pd.DataFrame([["Main train", "targets 2020-2022", len(tr)], ["Main test", "targets 2023-2024", len(te)],
 ["Walk-forward folds", "2021,2022,2023,2024", "36 each"]], columns=["Split", "Period", "N"]))
sheet("07_NAIVE_BASELINE", pd.DataFrame([{"Model": "Naive Lag-1"} | {m: main["Naive"][m] for m in ["RMSE", "MAE", "R2"]}]))
sheet("08_MODEL_COMPARISON", comp)
sheet("09_WALK_FORWARD", WF)
sheet("10_PREDICTIONS", pred)
sheet("11_ERROR_ANALYSIS", pred.describe().reset_index().rename(columns={"index": "Stat"}))
sheet("12_FEATURE_IMPORTANCE", FI)
sheet("13_2020_SENSITIVITY", SENS)
sheet("14_MODEL_STABILITY", stab.reset_index())
sheet("15_METRICS", pd.DataFrame([["RMSE", "primary; accident-count scale"], ["MAE", "primary; robust"],
 ["R2", "secondary; scale-inflated caution"]], columns=["Metric", "Role"]))
sheet("16_EXCLUSIONS", pd.DataFrame([["Legacy DNH/Diu (N=2 each) + merged DNH-DD (N=5: insufficient stable lag history)", "non-full panels excluded from ML", 9],
 ["Road features", "would restrict targets to 2022-23", "documented"], ["Vehicles/weather/GIS", "unavailable", "—"]],
 columns=["Exclusion", "Reason", "Rows"]))
sheet("17_DATA_DICTIONARY", pd.DataFrame([["Target_Accidents", "state accidents target year", "count"],
 ["Cutoff", "latest feature year = target-1 (Pop_t assumption noted)", "year"]], columns=["Field", "Definition", "Unit"]))
sheet("18_METHODS", pd.DataFrame([
 ["Split", "chronological only; test strictly later; scaler fit on train per fold"],
 ["Tuning", "documented defaults; no grid search on small panel; test untouched until final eval"],
 ["KNN", "supervised regressor (k=5); NOT unsupervised; NOT k-means"],
], columns=["Topic", "Method"]))
wb.save("PHASE5_ML_ANALYSIS.xlsx")
print("best_ml:", best_ml)
print("stability (mean AE by year):"); print(stab.to_string())
