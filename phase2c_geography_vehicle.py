"""Phase 2C: geography resolution (J&K/Ladakh, DNH/Diu) + vehicle acquisition attempt.
No joins, no normalized metrics, no website changes. Run: python phase2c_geography_vehicle.py"""
import hashlib, os
from datetime import date
import pandas as pd
from openpyxl import Workbook

RAW_POP = "phase2_raw/population/RGI_Population_Projection_2011-2036.pdf"
RAW_ROAD = "phase2_raw/road_length/BRSI_2020-22.pdf"
os.makedirs("phase2_raw/vehicles", exist_ok=True)
veh_files = [f for f in os.listdir("phase2_raw/vehicles") if not f.startswith(".")] if os.path.isdir("phase2_raw/vehicles") else []

jk = pd.DataFrame([
 ["RGI projections","JAMMU & KASHMIR (UT)",2018,"Projected via cohort-component on J&K(State) SRS fertility/mortality; Ladakh computed as residual of J&K(State) minus J&K(UT)","NO — Ladakh is the residual remainder","Jammu & Kashmir","DIRECT","HIGH","RGI report pp.8,22: 'Based on the residual of the projected population of J&K (State) and J&K (UT) ... projection of Ladakh (UT) have been made'","J&K(UT) excludes Ladakh by construction"],
 ["RGI projections","JAMMU & KASHMIR (UT)",2019,"as above","NO","Jammu & Kashmir","DIRECT","HIGH","as above",""],
 ["RGI projections","JAMMU & KASHMIR (UT)",2020,"as above","NO","Jammu & Kashmir","DIRECT","HIGH","as above",""],
 ["RGI projections","JAMMU & KASHMIR (UT)",2021,"as above","NO","Jammu & Kashmir","DIRECT","HIGH","as above",""],
 ["RGI projections","JAMMU & KASHMIR (UT)",2022,"as above","NO","Jammu & Kashmir","DIRECT","HIGH","as above",""],
 ["RGI projections","JAMMU & KASHMIR (UT)",2023,"as above","NO","Jammu & Kashmir","DIRECT","HIGH","as above",""],
 ["RGI projections","JAMMU & KASHMIR (UT)",2024,"as above","NO","Jammu & Kashmir","DIRECT","HIGH","as above",""],
 ["RGI projections","LADAKH",2018,"Residual of J&K(State) minus J&K(UT) projections; present all years incl. 2011 base (275k)","N/A (is Ladakh)","Ladakh","DIRECT","HIGH","RGI Table 11 p.95; method pp.8,22","2018 join allowed; MoRTH Ladakh 2018 accidents=0 kept as-is"],
 ["RGI projections","LADAKH",2019,"as above","N/A","Ladakh","DIRECT","HIGH","as above",""],
 ["RGI projections","LADAKH",2020,"as above","N/A","Ladakh","DIRECT","HIGH","as above",""],
 ["RGI projections","LADAKH",2021,"as above","N/A","Ladakh","DIRECT","HIGH","as above",""],
 ["RGI projections","LADAKH",2022,"as above","N/A","Ladakh","DIRECT","HIGH","as above",""],
 ["RGI projections","LADAKH",2023,"as above","N/A","Ladakh","DIRECT","HIGH","as above",""],
 ["RGI projections","LADAKH",2024,"as above","N/A","Ladakh","DIRECT","HIGH","as above",""],
 ["BRSI 2020-22","Jammu And Kashmir",2021,"State-wise total road length row (Annex 1.1.2); Ladakh listed as separate row","NOT VERIFIED FROM SOURCE (no composition note found)","Jammu & Kashmir","DIRECT","MEDIUM","Separate rows 34/35 imply separate territories; no explicit definition located","Double-count check still OPEN: verify against BRSI J&K historical series"],
 ["BRSI 2020-22","Ladakh",2021,"as above","N/A","Ladakh","DIRECT","MEDIUM","as above",""],
 ["BRSI 2020-22","Jammu And Kashmir",2022,"Annex 2.1.2 separate rows","NOT VERIFIED FROM SOURCE","Jammu & Kashmir","DIRECT","MEDIUM","as above",""],
 ["BRSI 2020-22","Ladakh",2022,"as above","N/A","Ladakh","DIRECT","MEDIUM","as above",""],
], columns=["Source","Source_Entity","Year","Source_Definition","Includes_Ladakh","MoRTH_Compatible_Entity","Join_Action","Confidence","Evidence","Notes"])

dnh = pd.DataFrame([
 ["RGI projections","DADRA & NAGAR HAVELI",2018,"Projected by mathematical (exponential-LS) method; UT listed separately","Dadra & Nagar Haveli","NONE","DIRECT","HIGH","RGI p.26 UT list; Table 11 p.93","MoRTH legacy row 2018-19"],
 ["RGI projections","DAMAN & DIU",2018,"as above","Daman & Diu","NONE","DIRECT","HIGH","as above","MoRTH legacy row 2018-19"],
 ["RGI projections","DADRA & NAGAR HAVELI",2019,"as above","Dadra & Nagar Haveli","NONE","DIRECT","HIGH","as above",""],
 ["RGI projections","DAMAN & DIU",2019,"as above","Daman & Diu","NONE","DIRECT","HIGH","as above",""],
 ["RGI projections","DADRA & NAGAR HAVELI + DAMAN & DIU",2020,"Both UTs projected separately all years; merged UT formed Jan 2020","Dadra & Nagar Haveli and Daman & Diu","SUM_DNH_PLUS_DAMAN_DIU","AGGREGATE_REQUIRED","MEDIUM","Merger is administrative fact; sum is arithmetic, NOT source-published","Valid for population (additive persons)"],
 ["RGI projections","DADRA & NAGAR HAVELI + DAMAN & DIU",2021,"as above","Dadra & Nagar Haveli and Daman & Diu","SUM_DNH_PLUS_DAMAN_DIU","AGGREGATE_REQUIRED","MEDIUM","as above",""],
 ["RGI projections","DADRA & NAGAR HAVELI + DAMAN & DIU",2022,"as above","Dadra & Nagar Haveli and Daman & Diu","SUM_DNH_PLUS_DAMAN_DIU","AGGREGATE_REQUIRED","MEDIUM","as above",""],
 ["RGI projections","DADRA & NAGAR HAVELI + DAMAN & DIU",2023,"as above","Dadra & Nagar Haveli and Daman & Diu","SUM_DNH_PLUS_DAMAN_DIU","AGGREGATE_REQUIRED","MEDIUM","as above",""],
 ["RGI projections","DADRA & NAGAR HAVELI + DAMAN & DIU",2024,"as above","Dadra & Nagar Haveli and Daman & Diu","SUM_DNH_PLUS_DAMAN_DIU","AGGREGATE_REQUIRED","MEDIUM","as above",""],
 ["BRSI 2020-22","Dadra & Nagar Haveli",2021,"Separate rows 31-32 in Annex 1.1.2 (1,139 km / 320 km)","Dadra & Nagar Haveli and Daman & Diu","SUM_DNH_PLUS_DAMAN_DIU","AGGREGATE_REQUIRED","MEDIUM","Lengths are additive physical quantities","Sum=1,459 km; not source-published as merged"],
 ["BRSI 2020-22","Daman & Diu",2021,"as above","Dadra & Nagar Haveli and Daman & Diu","SUM_DNH_PLUS_DAMAN_DIU","AGGREGATE_REQUIRED","MEDIUM","as above",""],
 ["BRSI 2020-22","Dadra & Nagar Haveli",2022,"Annex 2.1.2 separate rows","Dadra & Nagar Haveli and Daman & Diu","SUM_DNH_PLUS_DAMAN_DIU","AGGREGATE_REQUIRED","MEDIUM","as above",""],
 ["BRSI 2020-22","Daman & Diu",2022,"as above","Dadra & Nagar Haveli and Daman & Diu","SUM_DNH_PLUS_DAMAN_DIU","AGGREGATE_REQUIRED","MEDIUM","as above",""],
], columns=["Source","Source_Entity","Year","MoRTH_Entity","Transformation","Join_Action","Confidence","Evidence","Notes"] if False else
 ["Source","Source_Entity","Year","Definition","MoRTH_Entity","Transformation","Join_Action","Confidence","Evidence","Notes"])
# fix columns (defined explicitly)
dnh.columns = ["Source","Source_Entity","Year","Definition","MoRTH_Entity","Transformation","Join_Action","Confidence","Evidence","Notes"]

xw = pd.DataFrame([
 ["RGI","JAMMU & KASHMIR (UT)","Jammu & Kashmir",2018,2024,"NONE","DIRECT","HIGH","RGI pp.8,22 residual method","Excludes Ladakh by construction"],
 ["RGI","LADAKH","Ladakh",2018,2024,"NONE","DIRECT","HIGH","RGI Table 11 p.95","All years incl. 2011 base"],
 ["RGI","DADRA & NAGAR HAVELI","Dadra & Nagar Haveli",2018,2019,"NONE","DIRECT","HIGH","RGI Table 11 p.93","Legacy"],
 ["RGI","DAMAN & DIU","Daman & Diu",2018,2019,"NONE","DIRECT","HIGH","RGI Table 11 p.93","Legacy"],
 ["RGI","DADRA & NAGAR HAVELI + DAMAN & DIU","Dadra & Nagar Haveli and Daman & Diu",2020,2024,"SUM","AGGREGATE","MEDIUM","UT merger Jan 2020","Arithmetic sum, not published"],
 ["RGI","TELANGANA","Telangana",2018,2024,"NONE","DIRECT","HIGH","RGI Table 11 p.95",""],
 ["RGI","NCT OF DELHI","Delhi",2018,2024,"RENAME","DIRECT","HIGH","Naming only",""],
 ["RGI","* (all other 30 entities)","same name",2018,2024,"RENAME_AS_NEEDED","DIRECT","HIGH","Table 11 pp.83-94","Case/spelling only"],
 ["BRSI","Jammu And Kashmir","Jammu & Kashmir",2021,2022,"RENAME","DIRECT","MEDIUM","Separate row from Ladakh","Composition note not found"],
 ["BRSI","Ladakh","Ladakh",2021,2022,"NONE","DIRECT","MEDIUM","Separate row",""],
 ["BRSI","Dadra & Nagar Haveli","Dadra & Nagar Haveli and Daman & Diu",2021,2022,"SUM_WITH_DIU","AGGREGATE","MEDIUM","Additive lengths",""],
 ["BRSI","Daman & Diu","Dadra & Nagar Haveli and Daman & Diu",2021,2022,"SUM_WITH_DNH","AGGREGATE","MEDIUM","Additive lengths",""],
 ["BRSI","Tamilnadu","Tamil Nadu",2021,2022,"RENAME","DIRECT","HIGH","Spelling",""],
 ["BRSI","A & N Islands","Andaman & Nicobar",2021,2022,"RENAME","DIRECT","HIGH","Naming only",""],
 ["BRSI","* (all other entities)","same name",2021,2022,"NONE","DIRECT","HIGH","Annex 1.1.2/2.1.2",""],
 ["RTYB/future vehicles","TBD","TBD",2018,2024,"TBD","UNRESOLVED","LOW","No verified file acquired","Phase 2C vehicle attempt failed"],
], columns=["Source_System","Source_Entity","MoRTH_Entity","Year_Start","Year_End","Transformation","Join_Type","Confidence","Evidence","Notes"])

compat = pd.DataFrame([
 ["Population (RGI projection)",2018,2024,"37 entities + INDIA","'000 persons","Projected (cohort-component / exponential)","YES exc. merged-UT arithmetic","JOIN-READY (DIRECT: 2018-19 all + J&K/Ladakh/Telangana all years; AGGREGATE: DNH+Diu 2020-24)","HIGH/MEDIUM","Residual J&K proof (RGI pp.8,22); merger Jan 2020","DNH+Diu sums are arithmetic, flag in outputs"],
 ["Road length (BRSI)",2021,2022,"37 entities","km","Total reported roads excl. JRY","YES for confirmed rows","JOIN-READY for 2021-2022 compatible cells only","MEDIUM","Annex 1.1.2/2.1.2 reconcile exactly","2 of 7 years; J&K composition note missing"],
 ["Registered vehicles",None,None,"—","—","—","NO","NOT JOIN-READY","—","No verified file (RTYB blocked; data.gov.in JS-only; catalog API 404; CEIC rejected)","NOT AVAILABLE FROM VERIFIED DATA"],
], columns=["Exposure","Year_Start","Year_End","Geography","Unit","Definition","MoRTH_Compatible","Join_Ready","Confidence","Evidence","Blocking_Issue"])

wb = Workbook(); wb.remove(wb.active)
def sheet(title, df):
    ws = wb.create_sheet(title[:31]); ws.append(list(df.columns))
    for row in df.itertuples(index=False): ws.append([("" if (isinstance(v, float) and pd.isna(v)) else v) for v in row])
ws0 = wb.create_sheet("01_README")
for l in ["PHASE2C_GEOGRAPHY_VEHICLES.xlsx — " + str(date.today()),
 "04: J&K/Ladakh resolution (RGI residual proof). 05: DNH/Diu resolution. 06: master crosswalk.",
 "02/03: vehicle sheets EMPTY — no verified file acquired. NO JOIN. NO NORMALIZED METRICS."]: ws0.append([l])
sheet("02_RAW_REGISTERED_VEHICLES", pd.DataFrame(columns=["Source_Entity","Year","Registered_Vehicles","Unit","Source_Table","Source_Page","Source_Definition","Source_Footnote","Extraction_Status"]))
sheet("03_VEHICLE_DATA_VALIDATION", pd.DataFrame([["NOT ACQUIRED",None,None,None,None,0,0,"NOT AVAILABLE FROM VERIFIED DATA","RTYB blocked; see manifest"]], columns=["Year","Published_India_Total","State_Sum","Difference","Difference_pct","Duplicate_Count","Missing_Count","Validation_Status","Notes"]))
sheet("04_JK_LADAKH_RESOLUTION", jk)
sheet("05_DNH_DAMAN_DIU_RESOLUTION", dnh)
sheet("06_MASTER_GEOGRAPHY_CROSSWALK", xw)
sheet("07_SOURCE_MANIFEST", pd.DataFrame([
 [RAW_POP, hashlib.sha256(open(RAW_POP,'rb').read()).hexdigest(), "RGI/TG cere NCP, MoHFW Jul 2020", "mohfw-dohfw.gov.in mirror", "2026-09-26", "Tables 8/11/14; evidence pp.8,22,26"],
 [RAW_ROAD, hashlib.sha256(open(RAW_ROAD,'rb').read()).hexdigest(), "MoRTH TRW BRSI 2020-22", "morth.gov.in backend docs", "2026-09-26", "Annex 1.1.2/2.1.2; geography rows 31-35"],
 ["phase2_raw/vehicles/ (empty)", "N/A", "RTYB sought, not acquired", "morth.nic.in blocked; data.gov.in JS-only", "2026-09-27", "CEIC/secondary rejected"],
], columns=["File","SHA-256","Publisher","URL","Download_Date","Notes"]))
sheet("08_COMPATIBILITY_STATUS", compat)
sheet("09_LIMITATIONS", pd.DataFrame([
 ["BRSI J&K composition note not located — double-count check OPEN (MEDIUM)"],
 ["DNH+Diu sums are arithmetic, not source-published — must be flagged in any future join output"],
 ["RGI small-UT values are exponential-fit projections — higher uncertainty than cohort-component states"],
 ["Road covers 2/7 years; vehicles 0/7 years — full-period normalization impossible"],
 ["No Census 2021 — all population denominators are projections"],
], columns=["Limitation"]))
wb.save("PHASE2C_GEOGRAPHY_VEHICLES.xlsx")
print("saved. vehicle files:", veh_files)
