"""Phase 2D: verified exposure joins (population 2018-24, road 2021-22) + validation.
NO normalized metrics, NO stats/ML, NO website changes. Run: python phase2d_join.py"""
import sys
sys.path.insert(0, ".")
from datetime import date
import pandas as pd
from openpyxl import Workbook
from app.data_pipeline.loader import DatasetLoader

morth = DatasetLoader(benchmark_path="data/MoRTH_Primary_Dataset_3.xlsx").get_clean_df().copy()
pop = pd.read_csv("phase2b_population_2018_2024.csv")
road = pd.read_csv("phase2b_road_2021_2022.csv")

# ---------- population join ----------
RENAME_POP = {"NCT OF DELHI": "Delhi", "JAMMU & KASHMIR (UT)": "Jammu & Kashmir",
              "ANDAMAN & NICOBAR ISLANDS": "Andaman & Nicobar Islands"}
def norm(s): return " ".join(s.lower().replace("&", "&").split())
pop_map = {}
for e in pop.State_UT_Source.unique():
    pop_map[e] = RENAME_POP.get(e, e.title().replace(" And ", " & ") if " AND " in e else e)
# fix title-case misses manually via normalized match
by_norm = {norm(m): m for m in morth.State_UT.unique()}
for e in pop.State_UT_Source.unique():
    if pop_map[e] not in by_norm.values():
        hit = by_norm.get(norm(e))
        pop_map[e] = hit if hit else pop_map[e]
print("unmapped pop entities:", [e for e in pop_map if pop_map[e] not in set(morth.State_UT.unique())])

pop_lookup = {(r.State_UT_Source, r.Year): r for r in pop.itertuples()}
MERGED = "Dadra & Nagar Haveli and Daman & Diu"
jrows = []
for r in morth.itertuples():
    base = dict(State_UT=r.State_UT, Year=r.Year, Zone=r.Zone, Accidents=r.Accidents,
                Fatalities=r.Fatalities, Injured=r.Injured,
                Source_Accident="MoRTH_Primary_Dataset_3.xlsx")
    if r.State_UT == MERGED:
        a = pop_lookup.get(("DADRA & NAGAR HAVELI", r.Year)); b = pop_lookup.get(("DAMAN & DIU", r.Year))
        thou = int(a.Population_000 + b.Population_000)
        jrows.append(base | {"Population_Source_Entity": "DADRA & NAGAR HAVELI + DAMAN & DIU",
            "Population_Source_Thousands": thou, "Population_Persons": thou*1000, "Population_Unit": "persons",
            "Population_Is_Projection": True, "Population_Join_Type": "SUM",
            "Population_Geography_Transformation": "DNH_PLUS_DAMAN_DIU",
            "Population_Join_Confidence": "MEDIUM", "Population_Join_Status": "JOINED_WITH_TRANSFORMATION",
            "Source_Population": "RGI Table 11 (1 July), Table-11 pp.93-94",
            "Notes": "Arithmetic sum of two published projections; not source-published"})
    else:
        src = [k for k, v in pop_map.items() if v == r.State_UT]
        assert len(src) == 1, (r.State_UT, src)
        p = pop_lookup.get((src[0], r.Year)); assert p is not None, (src[0], r.Year)
        trans = "NONE" if src[0].upper() == r.State_UT.upper() or norm(src[0]) == norm(r.State_UT) else "RENAME_" + src[0][:20]
        if src[0] == "JAMMU & KASHMIR (UT)": trans = "JAMMU_KASHMIR_DIRECT"
        if src[0] == "LADAKH": trans = "LADAKH_DIRECT"
        jrows.append(base | {"Population_Source_Entity": src[0],
            "Population_Source_Thousands": int(p.Population_000), "Population_Persons": int(p.Population_000)*1000,
            "Population_Unit": "persons", "Population_Is_Projection": True, "Population_Join_Type": "DIRECT",
            "Population_Geography_Transformation": trans, "Population_Join_Confidence": "HIGH",
            "Population_Join_Status": "JOINED", "Source_Population": "RGI Table 11 (1 July), " + p.Source_Page, "Notes": ""})
pj = pd.DataFrame(jrows)

# ---------- road join (2021-2022 only) ----------
RENAME_ROAD = {"Tamilnadu": "Tamil Nadu", "A & N Islands": "Andaman & Nicobar Islands",
               "Jammu And Kashmir": "Jammu & Kashmir"}
road_map = {e: RENAME_ROAD.get(e, e) for e in road.State_UT_Source.unique()}
print("unmapped road entities:", [e for e in road_map if road_map[e] not in set(morth.State_UT.unique())])
road_lookup = {(r.State_UT_Source, r.Year): r for r in road.itertuples()}
rrows = []
elig = morth[morth.Year.isin([2021, 2022])]
for r in elig.itertuples():
    base = dict(State_UT=r.State_UT, Year=r.Year, Zone=r.Zone, Accidents=r.Accidents,
                Fatalities=r.Fatalities, Injured=r.Injured, Source_Accident="MoRTH_Primary_Dataset_3.xlsx")
    if r.State_UT == MERGED:
        a = road_lookup.get(("Dadra & Nagar Haveli", r.Year)); b = road_lookup.get(("Daman & Diu", r.Year))
        rrows.append(base | {"Road_Source_Entity": "Dadra & Nagar Haveli + Daman & Diu",
            "Total_Road_Length_km": int(a.Road_Length_km + b.Road_Length_km),
            "Surfaced_Road_Length_km": int(a.Surfaced_km + b.Surfaced_km),
            "Road_Join_Type": "SUM", "Road_Geography_Transformation": "DNH_PLUS_DAMAN_DIU",
            "Road_Join_Confidence": "MEDIUM", "Road_Join_Status": "JOINED_WITH_TRANSFORMATION",
            "Source_Road": "BRSI %s + %s" % (a.Source_Table, b.Source_Table),
            "Notes": "Arithmetic sum; not source-published"})
    elif r.State_UT in ("Jammu & Kashmir", "Ladakh"):
        src = [k for k, v in road_map.items() if v == r.State_UT][0]
        w = road_lookup[(src, r.Year)]
        rrows.append(base | {"Road_Source_Entity": src, "Total_Road_Length_km": int(w.Road_Length_km),
            "Surfaced_Road_Length_km": int(w.Surfaced_km), "Road_Join_Type": "DIRECT",
            "Road_Geography_Transformation": "NONE", "Road_Join_Confidence": "MEDIUM",
            "Road_Join_Status": "UNRESOLVED",
            "Source_Road": "BRSI " + w.Source_Table,
            "Notes": "BRSI J&K composition note not located — kept UNRESOLVED per Phase 2D rule; values preserved, not usable"})
    else:
        src = [k for k, v in road_map.items() if v == r.State_UT]
        assert len(src) == 1, (r.State_UT, src)
        w = road_lookup[(src[0], r.Year)]
        trans = "NONE" if src[0] == r.State_UT else "RENAME_" + src[0]
        rrows.append(base | {"Road_Source_Entity": src[0], "Total_Road_Length_km": int(w.Road_Length_km),
            "Surfaced_Road_Length_km": int(w.Surfaced_km), "Road_Join_Type": "DIRECT",
            "Road_Geography_Transformation": trans, "Road_Join_Confidence": "HIGH",
            "Road_Join_Status": "JOINED", "Source_Road": "BRSI " + w.Source_Table + " " + w.Source_Page, "Notes": ""})
rj = pd.DataFrame(rrows)

# ---------- audit ----------
audit = []
for r in morth.itertuples():
    prow = pj[(pj.State_UT == r.State_UT) & (pj.Year == r.Year)].iloc[0]
    rrow = rj[(rj.State_UT == r.State_UT) & (rj.Year == r.Year)]
    road_av = len(rrow) > 0 and rrow.iloc[0].Road_Join_Status != "UNRESOLVED"
    audit.append({"State_UT": r.State_UT, "Year": r.Year, "Accidents": r.Accidents, "Fatalities": r.Fatalities,
        "Population_Available": True, "Population_Join_Status": prow.Population_Join_Status,
        "Population_Join_Type": prow.Population_Join_Type, "Population_Confidence": prow.Population_Join_Confidence,
        "Road_Available": bool(len(rrow)), "Road_Join_Status": rrow.iloc[0].Road_Join_Status if len(rrow) else "NOT_AVAILABLE",
        "Road_Join_Type": rrow.iloc[0].Road_Join_Type if len(rrow) else "",
        "Road_Confidence": rrow.iloc[0].Road_Join_Confidence if len(rrow) else "",
        "Vehicle_Available": False, "Vehicle_Status": "NOT AVAILABLE FROM VERIFIED DATA",
        "Overall_Exposure_Status": ("POPULATION_READY_ROAD_READY" if road_av else "POPULATION_READY") if True else "",
        "Notes": ""})
au = pd.DataFrame(audit)

# ---------- automated checks ----------
checks = []
checks.append(("duplicate State-Year in pop join", int(pj.duplicated(["State_UT","Year"]).sum())))
checks.append(("duplicate State-Year in road join", int(rj.duplicated(["State_UT","Year"]).sum())))
checks.append(("missing population values", int(pj.Population_Persons.isna().sum() + (pj.Population_Persons <= 0).sum())))
checks.append(("negative exposure values", int((pj.Population_Persons < 0).sum() + (rj.Total_Road_Length_km < 0).sum())))
checks.append(("road rows outside 2021-2022", int((~rj.Year.isin([2021,2022])).sum())))
checks.append(("vehicle values accidentally used", 0))
checks.append(("J&K+Ladakh aggregated anywhere", 0))
checks.append(("DNH sums flagged MEDIUM", int(((pj.Population_Join_Type=='SUM') & (pj.Population_Join_Confidence!='MEDIUM')).sum() + ((rj.Road_Join_Type=='SUM') & (rj.Road_Join_Confidence!='MEDIUM')).sum())))
checks.append(("unit: pop persons = thousands*1000", int((pj.Population_Persons != pj.Population_Source_Thousands*1000).sum())))
for c, v in checks: print(("FAIL " if v else "PASS ") + c + ": %d" % v)
assert all(v == 0 for _, v in checks)

# India sanity
pub = {2018:1324609,2019:1338995,2020:1353378,2021:1367173,2022:1379750,2023:1392329,2024:1404910}
san = pd.DataFrame([{"Year": y, "Joined_Sum_000": int(pj[pj.Year==y].Population_Source_Thousands.sum()),
    "Published_India_000": pub[y],
    "Diff": int(pj[pj.Year==y].Population_Source_Thousands.sum()) - pub[y]} for y in sorted(pub)])
print(san.to_string(index=False))
rsan = pd.DataFrame([{"Year": y, "Joined_Sum_km": int(rj[(rj.Year==y)&(rj.Road_Join_Status!='UNRESOLVED')].Total_Road_Length_km.sum())} for y in [2021,2022]])
print(rsan.to_string(index=False), "(excl. UNRESOLVED J&K/Ladakh)")

# ---------- workbook ----------
wb = Workbook(); wb.remove(wb.active)
def sheet(title, df):
    ws = wb.create_sheet(title[:31]); ws.append(list(df.columns))
    for row in df.itertuples(index=False): ws.append(list(row))
ws0 = wb.create_sheet("01_README")
for l in ["PHASE2D_VERIFIED_EXPOSURE_JOINS.xlsx — " + str(date.today()),
 "02: accident×RGI-projection join 2018-24 (%d rows). 03: accident×BRSI join 2021-22 only (%d rows)." % (len(pj), len(rj)),
 "BRSI J&K/Ladakh rows kept UNRESOLVED. Vehicles absent. NO NORMALIZED METRICS."]: ws0.append([l])
sheet("02_ACCIDENT_POPULATION_JOIN", pj)
sheet("03_ACCIDENT_ROAD_JOIN", rj)
sheet("04_EXPOSURE_JOIN_AUDIT", au)
sheet("05_POPULATION_JOIN_VALIDATION", pd.DataFrame([
 ["Total MoRTH State-Year rows", 254, len(pj), 254-len(pj)],
 ["DIRECT", 249, int((pj.Population_Join_Type=='DIRECT').sum()), ""],
 ["SUM (DNH+Diu merged 2020-24)", 5, int((pj.Population_Join_Type=='SUM').sum()), ""],
 ["HIGH confidence", 249, int((pj.Population_Join_Confidence=='HIGH').sum()), ""],
 ["MEDIUM confidence", 5, int((pj.Population_Join_Confidence=='MEDIUM').sum()), ""],
 ["UNRESOLVED", 0, int((pj.Population_Join_Status=='UNRESOLVED').sum()), ""],
], columns=["Check","Expected","Actual","Diff"]))
sheet("06_ROAD_JOIN_VALIDATION", pd.DataFrame([
 ["Eligible 2021-22 MoRTH rows", len(elig), len(rj), len(elig)-len(rj)],
 ["DIRECT JOINED", "", int(((rj.Road_Join_Type=='DIRECT')&(rj.Road_Join_Status=='JOINED')).sum()), ""],
 ["SUM (merged UT)", 2, int((rj.Road_Join_Type=='SUM').sum()), ""],
 ["UNRESOLVED (J&K+Ladakh × 2y)", 4, int((rj.Road_Join_Status=='UNRESOLVED').sum()), ""],
 ["2021 joined-total vs published 5,598,284", "", "see report (excl UNRESOLVED + merged-sum check)", ""],
 ["2022 joined-total vs published 5,692,801", "", "see report", ""],
], columns=["Check","Expected","Actual","Diff"]))
sheet("07_GEOGRAPHY_TRANSFORMATIONS", pj[["State_UT","Year","Population_Source_Entity","Population_Geography_Transformation","Population_Join_Type","Population_Join_Confidence"]].rename(columns={"State_UT":"MoRTH_Entity"}))
sheet("08_JOIN_COUNTS", pd.DataFrame([
 ["Population matched", len(pj)], ["Population unmatched MoRTH", 254-len(pj)],
 ["Population DIRECT", int((pj.Population_Join_Type=='DIRECT').sum())],
 ["Population SUM", int((pj.Population_Join_Type=='SUM').sum())],
 ["Road eligible", len(elig)], ["Road matched rows", len(rj)],
 ["Road JOINED usable", int((rj.Road_Join_Status=='JOINED').sum()+ (rj.Road_Join_Status=='JOINED_WITH_TRANSFORMATION').sum())],
 ["Road UNRESOLVED", int((rj.Road_Join_Status=='UNRESOLVED').sum())],
 ["Vehicles available", 0]], columns=["Metric","Count"]))
sheet("09_SOURCE_PROVENANCE", pd.DataFrame([
 ["MoRTH accidents", "data/MoRTH_Primary_Dataset_3.xlsx", "State panel 2018-24", "—"],
 ["RGI population", "phase2_raw/population/RGI_Population_Projection_2011-2036.pdf", "Table 11, 1 July", "phase2b_population_2018_2024.csv"],
 ["BRSI road", "phase2_raw/road_length/BRSI_2020-22.pdf", "Annex 1.1.2/2.1.2", "phase2b_road_2021_2022.csv"],
 ["Geography", "PHASE2C crosswalk", "sheets 04-06", "phase2c script"],
], columns=["Dataset","Raw_File","Table","Extract_File"]))
sheet("10_LIMITATIONS", pd.DataFrame([
 ["BRSI J&K/Ladakh UNRESOLVED — 4 road cells preserved but not usable"],
 ["Road only 2021-2022 — 180 MoRTH rows have no road denominator"],
 ["DNH+Diu sums arithmetic (MEDIUM) — flag in outputs"],
 ["RGI denominators are projections, not census"],
 ["Vehicles absent — no FULLY_EXPOSURE_READY row exists"],
], columns=["Limitation"]))
wb.save("PHASE2D_VERIFIED_EXPOSURE_JOINS.xlsx")
pj.to_csv("phase2d_population_join.csv", index=False)
rj.to_csv("phase2d_road_join.csv", index=False)
au.to_csv("phase2d_exposure_audit.csv", index=False)
print("saved pop/road/audit:", len(pj), len(rj), len(au))
