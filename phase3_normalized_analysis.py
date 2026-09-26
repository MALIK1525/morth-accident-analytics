"""Phase 3: normalized DESCRIPTIVE analysis only. No regression/ML/causal claims/website changes.
Run: python phase3_normalized_analysis.py"""
import numpy as np, pandas as pd
from scipy import stats
from openpyxl import Workbook
from datetime import date

pj = pd.read_csv("phase2d_population_join.csv")
rj = pd.read_csv("phase2d_road_join.csv")
au = pd.read_csv("phase2d_exposure_audit.csv")

# ---------- PART A/E: population normalization ----------
pj["Acc_per_Lakh_Pop"] = pj.Accidents / pj.Population_Persons * 100000
pj["Fat_per_Lakh_Pop"] = pj.Fatalities / pj.Population_Persons * 100000
pj["Injured_num"] = pd.to_numeric(pj.Injured, errors="coerce")
inj_valid = pj.Injured_num.notna() & (pj.Injured_num >= 0)
pj["Inj_per_Lakh_Pop"] = np.where(inj_valid, pj.Injured_num / pj.Population_Persons * 100000, np.nan)
pj["Normalization_Status"] = np.where(pj.Population_Join_Type == "SUM", "VALID_WITH_TRANSFORMATION", "VALID")
assert (pj.Population_Persons > 0).all() and (pj.Population_Is_Projection == True).all()
assert pj.duplicated(["State_UT", "Year"]).sum() == 0
print("pop usable:", len(pj), "| injury-metric rows:", int(inj_valid.sum()))

# ---------- PART D: India level (published India projection, not state sum) ----------
PUB_POP = {2018:1324609, 2019:1338995, 2020:1353378, 2021:1367173, 2022:1379750, 2023:1392329, 2024:1404910}
BENCH_A = {2018:470403, 2019:456959, 2020:372181, 2021:412432, 2022:461312, 2023:480583, 2024:487707}
BENCH_F = {2018:157593, 2019:158984, 2020:138383, 2021:153972, 2022:168491, 2023:172890, 2024:177175}
BENCH_I = {2018:464715, 2019:449360, 2020:346747, 2021:384448, 2022:443366, 2023:462825, 2024:471441}
india = pd.DataFrame([{"Year": y, "Accidents": BENCH_A[y], "Fatalities": BENCH_F[y], "Injuries_India": BENCH_I[y],
    "Projected_Population_000": PUB_POP[y], "Projected_Population": PUB_POP[y]*1000,
    "Acc_per_Lakh_ProjPop": BENCH_A[y]/(PUB_POP[y]*1000)*1e5, "Fat_per_Lakh_ProjPop": BENCH_F[y]/(PUB_POP[y]*1000)*1e5,
    "Population_Is_Projection": True} for y in sorted(BENCH_A)])
# verify state sums match benchmarks
chk = pj.groupby("Year")[["Accidents", "Fatalities"]].sum()
assert (chk.Accidents == pd.Series(BENCH_A)).all() and (chk.Fatalities == pd.Series(BENCH_F)).all()
print("India state-sum == benchmarks: TRUE")

# ---------- PART G: YoY ----------
for c in ["Accidents", "Fatalities", "Acc_per_Lakh_ProjPop", "Fat_per_Lakh_ProjPop"]:
    india[c + "_YoYpct"] = india[c].pct_change() * 100
syoy = pj.sort_values(["State_UT", "Year"]).copy()
for c in ["Accidents", "Fatalities", "Acc_per_Lakh_Pop", "Fat_per_Lakh_Pop"]:
    syoy[c + "_YoYpct"] = syoy.groupby("State_UT")[c].pct_change() * 100

# ---------- PART F/N: zones (aggregate numerator+denominator first) ----------
z = pj.groupby(["Zone", "Year"]).agg(Accidents=("Accidents", "sum"), Fatalities=("Fatalities", "sum"),
    Population_Persons=("Population_Persons", "sum")).reset_index()
z["Acc_per_Lakh_ProjPop"] = z.Accidents / z.Population_Persons * 1e5
z["Fat_per_Lakh_ProjPop"] = z.Fatalities / z.Population_Persons * 1e5

# ---------- PART H: raw vs normalized (shares use raw counts) ----------
itot = pj.groupby("Year")[["Accidents", "Fatalities"]].sum().rename(columns={"Accidents": "ITot_A", "Fatalities": "ITot_F"})
rvn = pj.merge(itot, on="Year")
rvn["Raw_Accident_Share_pct"] = rvn.Accidents / rvn.ITot_A * 100
rvn["Raw_Fatality_Share_pct"] = rvn.Fatalities / rvn.ITot_F * 100

# ---------- PART I: distributions ----------
def distr(s):
    s = s.dropna(); q = s.quantile([0.25, 0.75])
    return {"N": len(s), "Mean": s.mean(), "Median": s.median(), "SD": s.std(ddof=1),
            "Min": s.min(), "Max": s.max(), "Q1": q[0.25], "Q3": q[0.75], "IQR": q[0.75]-q[0.25]}
dist_rows = []
for y, g in pj.groupby("Year"):
    for m in ["Acc_per_Lakh_Pop", "Fat_per_Lakh_Pop"]:
        dist_rows.append({"Year": y, "Metric": m} | {k: round(v, 3) for k, v in distr(g[m]).items()})
dist = pd.DataFrame(dist_rows)

# ---------- PART J/K: road (usable only) ----------
ru = rj[rj.Road_Join_Status.isin(["JOINED", "JOINED_WITH_TRANSFORMATION"])].copy()
rex = rj[~rj.index.isin(ru.index)].copy()
ru["Acc_per_1000km"] = ru.Accidents / ru.Total_Road_Length_km * 1000
ru["Fat_per_1000km"] = ru.Fatalities / ru.Total_Road_Length_km * 1000
ru["Acc_per_1000km_Surfaced"] = ru.Accidents / ru.Surfaced_Road_Length_km * 1000
ru["Fat_per_1000km_Surfaced"] = ru.Fatalities / ru.Surfaced_Road_Length_km * 1000
print("road eligible=%d usable=%d excluded=%d (%s)" % (len(rj), len(ru), len(rex), rex.Road_Join_Status.unique().tolist()))
assert set(ru.Year.unique()) <= {2021, 2022} and (ru.Total_Road_Length_km > 0).all()
rdist = []
for y, g in ru.groupby("Year"):
    for m in ["Acc_per_1000km", "Fat_per_1000km"]:
        rdist.append({"Year": y, "Metric": m} | {k: round(v, 4) for k, v in distr(g[m]).items()})
rdist = pd.DataFrame(rdist)
rcmp = ru.groupby("Year")[["Accidents", "Fatalities", "Acc_per_1000km", "Fat_per_1000km"]].mean().T
rcmp["abs_change_21_22"] = rcmp[2022] - rcmp[2021]
rcmp["pct_change_21_22"] = rcmp[2022] / rcmp[2021] * 100 - 100

# ---------- PART L: pooled associations (descriptive only) ----------
assoc = []
for x, y in [("Population_Persons", "Accidents"), ("Population_Persons", "Fatalities")]:
    a, b = pj[x], pj[y]
    assoc.append({"Pair": "%s vs %s" % (x, y), "N": len(pj), "Pearson_r": stats.pearsonr(a, b)[0],
        "Pearson_p": stats.pearsonr(a, b)[1], "Spearman_rho": stats.spearmanr(a, b)[0],
        "Spearman_p": stats.spearmanr(a, b)[1],
        "Caveat": "pooled state-year association; between-state scale effects dominate; NOT causal"})
assoc = pd.DataFrame(assoc)

# ---------- PART M: within-state 2018->2024 change (endpoints only, no slopes) ----------
mchg = []
for s, g in pj.groupby("State_UT"):
    g = g.sort_values("Year")
    if not set([2018, 2024]) <= set(g.Year): continue
    a, b = g[g.Year == 2018].iloc[0], g[g.Year == 2024].iloc[0]
    mchg.append({"State_UT": s, "Zone": a.Zone,
        "Acc_2018": a.Accidents, "Acc_2024": b.Accidents, "Acc_abs": b.Accidents-a.Accidents,
        "Acc_pct": (b.Accidents-a.Accidents)/a.Accidents*100 if a.Accidents else np.nan,
        "Fat_2018": a.Fatalities, "Fat_2024": b.Fatalities, "Fat_abs": b.Fatalities-a.Fatalities,
        "Fat_pct": (b.Fatalities-a.Fatalities)/a.Fatalities*100 if a.Fatalities else np.nan,
        "AccLakh_2018": a.Acc_per_Lakh_Pop, "AccLakh_2024": b.Acc_per_Lakh_Pop,
        "FatLakh_2018": a.Fat_per_Lakh_Pop, "FatLakh_2024": b.Fat_per_Lakh_Pop})
mchg = pd.DataFrame(mchg)

# ---------- PART O: DNH sensitivity ----------
sens = pj.groupby("Population_Join_Type")[["Acc_per_Lakh_Pop", "Fat_per_Lakh_Pop"]].agg(["count", "mean", "median"])
sens_txt = "DIRECT n=%d vs SUM n=%d; SUM rows are 5 merged-UT years (pop ~0.6-0.7M) — too small for stable sensitivity conclusion." % (
    (pj.Population_Join_Type == "DIRECT").sum(), (pj.Population_Join_Type == "SUM").sum())

# ---------- save CSVs ----------
pj.to_csv("phase3_state_population.csv", index=False)
india.to_csv("phase3_india_population.csv", index=False)
z.to_csv("phase3_zone_population.csv", index=False)
ru.to_csv("phase3_road_2021_2022.csv", index=False)
assoc.to_csv("phase3_associations.csv", index=False)
excl = pd.concat([rex.assign(Reason="UNRESOLVED J&K/Ladakh composition"),
                  au[au.Year.isin([2018, 2019, 2020, 2023, 2024])].assign(Reason="No BRSI road year (2021-2022 only)")])
excl.to_csv("phase3_exclusion_audit.csv", index=False)

# ---------- workbook ----------
wb = Workbook(); wb.remove(wb.active)
def sheet(title, df):
    ws = wb.create_sheet(title[:31]); ws.append(list(df.columns))
    for row in df.itertuples(index=False):
        ws.append([("" if (isinstance(v, float) and pd.isna(v)) else v) for v in row])
ws0 = wb.create_sheet("01_README")
for l in ["PHASE3_NORMALIZED_ANALYSIS_ORIGINPRO.xlsx — " + str(date.today()),
 "DESCRIPTIVE ONLY. Denominators: RGI projections (pop) + BRSI totals (road 2021-22). No regression/ML/causation/ranking.",
 "Formulas: Acc_per_Lakh = Acc/Pop_Persons*1e5; Acc_per_1000km = Acc/Total_km*1000."]: ws0.append([l])
sheet("02_INDIA_POPULATION_NORMALIZED", india)
sheet("03_STATE_POPULATION_NORMALIZED", pj)
sheet("04_ZONE_POPULATION_NORMALIZED", z)
sheet("05_INDIA_YOY", india[["Year", "Accidents", "Accidents_YoYpct", "Fatalities", "Fatalities_YoYpct",
    "Acc_per_Lakh_ProjPop", "Acc_per_Lakh_ProjPop_YoYpct", "Fat_per_Lakh_ProjPop", "Fat_per_Lakh_ProjPop_YoYpct"]])
sheet("06_STATE_YOY", syoy[["State_UT", "Year", "Accidents", "Accidents_YoYpct", "Fatalities", "Fatalities_YoYpct",
    "Acc_per_Lakh_Pop", "Acc_per_Lakh_Pop_YoYpct", "Fat_per_Lakh_Pop", "Fat_per_Lakh_Pop_YoYpct"]])
sheet("07_RAW_VS_NORMALIZED", rvn[["State_UT", "Year", "Accidents", "Fatalities", "Population_Persons",
    "Acc_per_Lakh_Pop", "Fat_per_Lakh_Pop", "Raw_Accident_Share_pct", "Raw_Fatality_Share_pct"]])
sheet("08_POPULATION_DISTRIBUTIONS", dist)
sheet("09_POPULATION_ASSOCIATIONS", assoc)
sheet("10_ROAD_NORMALIZED_2021_2022", ru)
sheet("11_ROAD_DISTRIBUTIONS", rdist)
sheet("12_ROAD_YEAR_COMPARISON", rcmp.reset_index().rename(columns={"index": "Metric"}))
sheet("13_DNH_SENSITIVITY", pd.DataFrame([{"Comparison": "DIRECT vs SUM", "Finding": sens_txt}],
    columns=["Comparison", "Finding"]))
sheet("14_EXCLUSION_AUDIT", excl)
sheet("15_DATA_DICTIONARY", pd.DataFrame([
 ["Acc_per_Lakh_Pop", "Accidents/Population_Persons*100000", "MoRTH acc / RGI projection", "per lakh persons", "2018-24", "Join_Type/Confidence"],
 ["Fat_per_Lakh_Pop", "Fatalities/Population_Persons*100000", "MoRTH fat / RGI projection", "per lakh persons", "2018-24", "Join_Type/Confidence"],
 ["Inj_per_Lakh_Pop", "Injured/Population_Persons*100000 (valid injuries only)", "MoRTH inj / RGI projection", "per lakh persons", "2018-22 states; 2023-24 NaN", "NaN where injury missing"],
 ["Acc_per_1000km", "Accidents/Total_Road_Length_km*1000", "MoRTH acc / BRSI total", "per 1000 km", "2021-22 usable", "UNRESOLVED excluded"],
 ["Fat_per_1000km", "Fatalities/Total_Road_Length_km*1000", "MoRTH fat / BRSI total", "per 1000 km", "2021-22 usable", "UNRESOLVED excluded"],
], columns=["Metric", "Formula", "Numerator/Denominator", "Unit", "Coverage", "Flag"]))
wb.save("PHASE3_NORMALIZED_ANALYSIS_ORIGINPRO.xlsx")
print("saved. india2024:", round(india[india.Year==2024].Acc_per_Lakh_ProjPop.iloc[0], 2),
      round(india[india.Year==2024].Fat_per_Lakh_ProjPop.iloc[0], 2))
print("assoc:", assoc[["Pair", "Pearson_r", "Spearman_rho"]].to_string(index=False))
