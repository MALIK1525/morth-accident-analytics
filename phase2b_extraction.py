"""Phase 2B: extract RGI Table 11 (1 July, 2018-2024) + BRSI Annex 1.1.2/2.1.2.
No joins, no normalized metrics, no website changes. Originals untouched.
Run: python phase2b_extraction.py"""
import re, hashlib, os
from datetime import date
import pandas as pd
from pypdf import PdfReader
from openpyxl import Workbook

POP_PDF = "phase2_raw/population/RGI_Population_Projection_2011-2036.pdf"
ROAD_PDF = "phase2_raw/road_length/BRSI_2020-22.pdf"

def sha(f):
    return hashlib.sha256(open(f, "rb").read()).hexdigest()

print("hash pop:", sha(POP_PDF)[:16], "road:", sha(ROAD_PDF)[:16])

# ---------- RGI Table 11 ----------
# 0-index PDF pages 88..100; entities verified by manual header inspection
PAGES = {
 88: ["INDIA", "JAMMU & KASHMIR (UT)", "HIMACHAL PRADESH"],
 89: ["PUNJAB", "HARYANA", "NCT OF DELHI"],
 90: ["RAJASTHAN", "UTTAR PRADESH", "BIHAR"],
 91: ["ASSAM", "WEST BENGAL", "JHARKHAND"],
 92: ["ODISHA", "CHHATTISGARH", "MADHYA PRADESH"],
 93: ["GUJARAT", "MAHARASHTRA", "ANDHRA PRADESH"],
 94: ["KARNATAKA", "KERALA", "TAMIL NADU"],
 95: ["CHANDIGARH", "UTTARAKHAND", "SIKKIM"],
 96: ["ARUNACHAL PRADESH", "NAGALAND", "MANIPUR"],
 97: ["MIZORAM", "TRIPURA", "MEGHALAYA"],
 98: ["DAMAN & DIU", "DADRA & NAGAR HAVELI", "GOA"],
 99: ["LAKSHADWEEP", "PUDUCHERRY", "ANDAMAN & NICOBAR ISLANDS"],
 100: ["TELANGANA", "LADAKH"],
}
r = PdfReader(POP_PDF)
pop_rows, survey_note = [], []
for pg, ents in PAGES.items():
    t = r.pages[pg].extract_text() or ""
    # sanity: each entity token present (first word)
    for e in ents:
        assert e.split()[0] in t.replace("&", "&"), (pg, e)
    for m in re.finditer(r"(?m)^(201[89]|202[0-4])[^\S\n]+([\d,][\d,\s]*?)[^\S\n]*$", t):
        yr = int(m.group(1))
        nums = [int(x.replace(",", "")) for x in re.findall(r"[\d,]+", m.group(2))]
        assert len(nums) == 3 * len(ents), (pg, yr, len(nums))
        for k, e in enumerate(ents):
            p, ml, f = nums[3*k:3*k+3]
            pop_rows.append({"State_UT_Source": e, "Year": yr, "Population_000": p,
                             "Male_000": ml, "Female_000": f,
                             "Source_Table": "Table 11", "Reference_Date": "1 July",
                             "Source_Page": "PDF p.%d" % (pg+1),
                             "Source_Note": "RGI projection ('000); M+F=%d" % (ml+f)})
pop = pd.DataFrame(pop_rows)
exp_pop = (37+1) * 7  # 37 entities + INDIA, 7 years (p100 has 2 entities, no INDIA)
print("pop rows:", len(pop), "expected:", 3*7 + 3*7*11 + 2*7, "dupes:", pop.duplicated(["State_UT_Source","Year"]).sum())
print("pop missing:", exp_pop - len(pop))
india_pub = pop[pop.State_UT_Source=="INDIA"].set_index("Year")["Population_000"]
state_sum = pop[pop.State_UT_Source!="INDIA"].groupby("Year")["Population_000"].sum()
recon = pd.DataFrame({"computed": state_sum, "published": india_pub})
recon["diff"] = recon["computed"] - recon["published"]

# ---------- BRSI totals ----------
rr = PdfReader(ROAD_PDF)
road_rows = []
for pg, yr, tab in [(127, 2021, "Annexure 1.1.2"), (159, 2022, "Annexure 2.1.2")]:
    t = rr.pages[pg].extract_text() or ""
    seg = t[t.find("Name of State"):]
    for m in re.finditer(r"(\d+)\s+([A-Za-z&\. ]+?)\s+([\d,]+)\s+([\d,]+)", seg):
        name = m.group(2).strip()
        if len(name) < 2: continue
        road_rows.append({"State_UT_Source": re.sub(r"\s+", " ", name), "Year": yr,
                          "Road_Length_km": int(m.group(3).replace(",", "")),
                          "Surfaced_km": int(m.group(4).replace(",", "")),
                          "Source_Table": tab, "Reference_Date": "31.03.%d" % yr,
                          "Source_Page": "PDF p.%d" % (pg+1),
                          "Source_Note": "Total incl. surfaced+unsurfaced; *Excluding JRY roads"})
road = pd.DataFrame(road_rows)
print("road rows:", len(road), "dupes:", road.duplicated(["State_UT_Source","Year"]).sum())
print("road entities 2021:", (road.Year==2021).sum(), "2022:", (road.Year==2022).sum())

# ---------- workbook ----------
wb = Workbook(); wb.remove(wb.active)
def sheet(title, df):
    ws = wb.create_sheet(title[:31])
    ws.append(list(df.columns))
    for row in df.itertuples(index=False): ws.append(list(row))
    return ws
import pandas as pd
ws = wb.create_sheet("01_README")
for l in ["PHASE2_EXTRACTED_EXPOSURE.xlsx — " + str(date.today()),
 "02: RGI Table-11 1-July projections 2018-2024 (unit '000, PROJECTIONS not counts).",
 "03: BRSI state totals+surfaced 2021 (1.1.2) + 2022 (2.1.2), km, excl. JRY.",
 "NO JOIN. NO NORMALIZED METRICS. Vehicles: NOT AVAILABLE."]: ws.append([l])
sheet("02_RAW_POPULATION", pop)
sheet("03_RAW_ROAD_LENGTH", road)
sheet("04_SOURCE_TABLE_INDEX", pd.DataFrame([
 ["RGI Table 11","Projected Total Population by Sex as on 1st July 2011-2036","PDF pp.83-95","Persons/Male/Female ('000)","2018-2024 slice","37 entities + INDIA"],
 ["BRSI 1.1.2","State/UT-wise Total & Surfaced Length of Roads as on 31.03.2021 (km, excl JRY)","PDF p.~1122","Total, Surfaced","2021","37 entities"],
 ["BRSI 2.1.2","State/UT-wise Total & Surfaced Length of Roads as on 31.03.2022 (km, excl JRY)","PDF p.~1133","Total, Surfaced","2022","37 entities"]],
 columns=["Table","Title","Location","Columns","Slice","Entities"]))
sheet("05_COVERAGE", pd.DataFrame([
 ["Population projection",37,7,37*7,len(pop)-7,"0 (excl INDIA row)","'000","2018-2024","Table 11 only"],
 ["Road length total",37,2,74,len(road),"0","km","2021-2022","1.1.2 + 2.1.2"],
 ["Registered vehicles",0,0,0,0,"ALL","—","—","NOT ACQUIRED"]],
 columns=["Variable","Entities","Years","Expected","Extracted","Missing","Unit","Coverage","Tables"]))
# geography mapping skeleton (documented, unresolved马克思 where noted)
sheet("06_GEOGRAPHY_MAPPING", pd.DataFrame([
 ["DAMAN & DIU","Daman & Diu",2018,2019,"DIRECT","No","HIGH","RGI Table 11 p.93; MoRTH legacy row","MoRTH legacy entity 2018-19"],
 ["DADRA & NAGAR HAVELI","Dadra & Nagar Haveli",2018,2019,"DIRECT","No","HIGH","RGI Table 11 p.93; MoRTH legacy row","MoRTH legacy entity 2018-19"],
 ["DAMAN & DIU + DADRA & NAGAR HAVELI","Dadra & Nagar Haveli and Daman & Diu",2020,2024,"AGGREGATE_SUM","Yes: sum both RGI entities","MEDIUM","UT merger Jan 2020","Sum is arithmetic, not source-published"],
 ["JAMMU & KASHMIR (UT)","Jammu & Kashmir",2018,2024,"RENAMED","Check pre-2019 undivided base","MEDIUM","RGI Table 11 p.83","RGI base year composition unclear pre-2019"],
 ["LADAKH","Ladakh",2019,2024,"DIRECT","No (2018 excluded)","HIGH","RGI Table 11 p.95","No 2018 Ladakh join"],
 ["TELANGANA","Telangana",2018,2024,"DIRECT","No","HIGH","RGI Table 11 p.95","Present both systems"],
 ["NCT OF DELHI","Delhi",2018,2024,"RENAMED","No","HIGH","Naming only",""],
 ["A & N Islands","Andaman & Nicobar",2018,2024,"RENAMED","No","HIGH","Naming only","BRSI writes 'A & N Islands'"],
 ["Tamilnadu (BRSI)","Tamil Nadu",2021,2022,"RENAMED","No","HIGH","BRSI spelling",""],
 ["Jammu And Kashmir (BRSI)","Jammu & Kashmir",2021,2022,"RENAMED","Check undivided base","MEDIUM","BRSI spelling; includes Ladakh? UNRESOLVED","BRSI lists Ladakh separately too — verify no double count at validation"],
 ["Dadra & Nagar Haveli (BRSI)","Dadra & Nagar Haveli and Daman & Diu",2021,2022,"UNRESOLVED","BRSI keeps separate; MoRTH merged","LOW","BRSI 1.1.2 rows 31-32","Do not force join"],
 ["Daman & Diu (BRSI)","Dadra & Nagar Haveli and Daman & Diu",2021,2022,"UNRESOLVED","Same as above","LOW","BRSI 1.1.2 rows 31-32","Do not force join"]],
 columns=["Source_Entity","MoRTH_Entity","Year_Start","Year_End","Mapping_Type","Transformation_Required","Confidence","Evidence","Notes"]))
sheet("07_POPULATION_VALIDATION", recon.reset_index().rename(columns={"index":"Year"}))
sheet("08_ROAD_VALIDATION", pd.DataFrame([
 [2021, road[road.Year==2021].Road_Length_km.sum(), 5598284, road[road.Year==2021].Road_Length_km.sum()-5598284, "Annex 1.1.2 Total* row"],
 [2022, road[road.Year==2022].Road_Length_km.sum(), 5692801, road[road.Year==2022].Road_Length_km.sum()-5692801, "Annex 2.1.2 Total* row"]],
 columns=["Year","Computed_Sum_km","Published_Total_km","Difference","Source"]))
sheet("09_UNRESOLVED_ISSUES", pd.DataFrame([
 ["RGI M+F vs Persons rounding (e.g. Lakshadweep 33+31=64 vs 65)","Persons used; sexes kept for audit","OPEN"],
 ["BRSI J&K/Ladakh double-count check","Verify J&K row excludes Ladakh 2021/22","OPEN"],
 ["BRSI DNH/Diu separate vs MoRTH merged join rule","UNRESOLVED mapping — no join","OPEN"],
 ["BRSI stale footnotes (*2018/#2019/@2020)","Not observed in 1.1.2/2.1.2 state rows; flagged for category tables","MONITOR"],
 ["Road coverage only 2021-2022","Cannot support 2018-2024 trends","LIMITATION"],
 ["Vehicles entirely missing","Phase 2C","BLOCKED"]], columns=["Issue","Handling","Status"]))
sheet("10_PROVENANCE", pd.DataFrame([
 ["phase2_raw/population/RGI_Population_Projection_2011-2036.pdf", sha(POP_PDF), "RGI/TG cere NCP, MoHFW Jul 2020", "Tables 8/11/14; used Table 11"],
 ["phase2_raw/road_length/BRSI_2020-22.pdf", sha(ROAD_PDF), "MoRTH TRW BRSI 2020-22", "Annex 1.1.2 (2021), 2.1.2 (2022)"]],
 columns=["File","SHA-256","Source","Tables_Used"]))
wb.save("PHASE2_EXTRACTED_EXPOSURE.xlsx")
pop.to_csv("phase2b_population_2018_2024.csv", index=False)
road.to_csv("phase2b_road_2021_2022.csv", index=False)
print("saved. pop M+F check fails:", (pop.Male_000+pop.Female_000 != pop.Population_000).sum())
print(recon.to_string())
