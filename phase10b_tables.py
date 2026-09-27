"""Phase 10 part B: publication workbooks + package docs."""
import pandas as pd, numpy as np
from openpyxl import Workbook
def save_wb(path, sheets):
    wb=Workbook(); wb.remove(wb.active)
    for n,d in sheets:
        ws=wb.create_sheet(n[:31])
        if isinstance(d,pd.DataFrame):
            ws.append(list(d.columns))
            for r in d.itertuples(index=False): ws.append([None if (isinstance(v,float) and pd.isna(v)) else v for v in r])
        else:
            for row in d: ws.append(row)
    wb.save(path); print("saved",path)
I=pd.read_csv("phase1_india.csv"); P9I=pd.read_csv("phase9_india_severity.csv")
Z9=pd.read_csv("phase9_zone_severity.csv"); S9=pd.read_csv("phase9_state_severity_summary.csv")
SL=pd.read_csv("phase9_state_severity_slopes.csv"); F9=pd.read_csv("phase9_severity_fdr.csv")
P8=pd.read_csv("phase8_pooled_associations.csv"); F8=pd.read_csv("phase8_fdr_results.csv")
FE8=pd.read_csv("phase8_fixed_effects.csv"); M5=pd.read_csv("phase5_model_comparison.csv")
COV=pd.read_csv("phase9_injury_coverage.csv"); W9=pd.read_csv("phase9_weather_severity.csv")
t1=pd.DataFrame([
 ["MoRTH Road Accidents in India","MoRTH/TRW","Road Accidents in India (annual reports)","2018-2024","State-Year panel + India totals","Accidents/Fatalities/Injured","VERIFIED","2019 vintage: panel uses later-vintage (456959/158984/449360)","P1"],
 ["RGI Population Projections","RGI/NCP-MoHFW","Population Projections 2011-2036, Tbl 11 (1 July)","2018-2024 slice","State-Year","Projected population ('000)","VERIFIED (projections, not census)","No Census 2021; J&K excl Ladakh by construction","P2"],
 ["MoRTH Basic Road Statistics 2020-22","MoRTH/TRW","BRSI 2020-22 Ann 1.1.2/2.1.2","2021-2022","State-Year","Total+surfaced road km","VERIFIED","2 of 7 years only; J&K note unresolved","P2"],
 ["IMD RF25 rainfall","IMD Pune CMPG","RF25 gridded NetCDF 0.25-deg daily","2018-2024","grid-state","mm/day","VERIFIED","ocean=-999 masked; islands excluded","P6-7"],
 ["IMD TMAX1/TMIN1","IMD Pune CMPG","GrADS flat-binary 1-deg daily, 99.9 flag","2018-2024","grid-state","degC","VERIFIED","coarse grid; temp coords assumed (documented)","P6-7"],
 ["SOI ABDB boundaries","Survey of India","ABDB State Boundary shp (LCC_WGS84)","modern vintage","polygon","STATE polygons","VERIFIED","merged DNH-DD; 4 disputed excluded","P7"],
],columns=["Dataset","Org","Document","Coverage","Geography","Variables","Status","Limits","Phase"])
avail=pd.DataFrame([
 ["Accidents","A-ANALYZED"],["Fatalities","A-ANALYZED"],["State","A-ANALYZED"],["Year","A-ANALYZED"],
 ["Zone","A-ANALYZED"],["Severity(F/100acc)","C-DERIVED"],["Acc/Fat per lakh pop","C-DERIVED + D-INTEGRATED"],
 ["Road per 1000km","C-DERIVED + D (2021-22 only)"],["Rainfall","D-INTEGRATED (236 obs)"],["Tmax/Tmin","D-INTEGRATED (236 obs)"],
 ["Injuries state","B-PARTIAL (2018-22)"],["Injuries India","A-ANALYZED (2018-24)"],
 ["Registered vehicles","E-NOT AVAILABLE"],["Humidity/visibility/fog/wind","E-NOT AVAILABLE"],
 ["Driver/vehicle/cause/collision/road-type","E-NOT AVAILABLE"],["Month/day/hour/GIS/coords","F-NOT SAFE TO INFER"],
 ["Traffic volume/AADT","E-NOT AVAILABLE"],["District/city/police-stn","E-NOT AVAILABLE"],
],columns=["Parameter","Status"])
t3=I.merge(P9I[["Year","AccLakh","FatLakh"]],on="Year"); t3["Data_status"]="VERIFIED"
figs=pd.DataFrame([
 ["FIG-01","India Accidents+Fatalities 2018-24","trend","phase1_india.csv","Year","Acc/Fat","counts","254 obs","2018-24","dual-line","P1","-","caption: verified MoRTH; 2020 break",""],
 ["FIG-02","India Fatalities/100 acc","severity","phase9_india_severity.csv","Year","Sev100","per 100","India","2018-24","line","P9","-","ratio not rate",""],
 ["FIG-03","India Acc/lakh pop","exposure","phase9_india_severity.csv","Year","AccLakh","per lakh proj pop","India","2018-24","line","P9","-","RGI projections",""],
 ["FIG-04","India Fat/lakh pop","exposure","phase9_india_severity.csv","Year","FatLakh","per lakh","India","2018-24","line","P9","-","RGI projections",""],
 ["FIG-05","Zone accident trends","heterogeneity","phase9_zone_severity.csv","Year","Acc","counts","6 zones","2018-24","multi-line","P9","-","no ranking",""],
 ["FIG-06","State x Year heatmap","heterogeneity","phase9_severity_state_year.csv","Year x State","Acc","counts","38 ent","2018-24","heatmap","P9","-","full table",""],
 ["FIG-07","Rainfall vs Accidents","weather","phase8_weather_analysis_data.csv","rain","Acc","mm/counts","N=236","2018-24","scatter","P8","r=-0.234 FDR-sig","pooled confounding","observational"],
 ["FIG-08","Tmax vs Accidents","weather","phase8_weather_analysis_data.csv","Tmax","Acc","C/counts","N=236","2018-24","scatter","P8","r=+0.452 FDR-sig","pooled confounding","observational"],
 ["FIG-09","Weather assoc summary","weather","phase8_pooled_associations.csv","variable","r","-","12 tests","2018-24","forest","P8","all FDR-sig","pooled vs within",""],
 ["FIG-10","State severity heterogeneity","severity","phase9_state_severity_summary.csv","State","Sev100","per 100","38 ent","2018-24","column","P9","-","no ranking","CV~0.5"],
 ["FIG-11","Severity trend","severity","phase9_india_severity.csv","Year","Sev100","per 100","India","2018-24","line","P9","9 FDR slopes","ratio",""],
 ["FIG-12","ML vs naive","ML","phase5_model_comparison.csv","model","RMSE","counts","N=70 test","2023-24","column","P5","naive 1053 wins","test-only","no deploy"],
],columns=["Figure_ID","Title","Purpose","Data_Source","X","Y","Units","Population","Years","Graph_Type","Phase","Stat_Annot","Caption","Limit"])
fmap=figs[["Figure_ID","Data_Source","X","Y","Graph_Type","Stat_Annot","Caption"]].copy()
fmap["Workbook"]=["PHASE1/3/4/8/9 workbooks (see index)"]*len(fmap); fmap["Export"]="OriginPro graph export PNG/EMF"
save_wb("PHASE10_PUBLICATION_TABLES.xlsx",[
 ("Table_1_Data_Sources",t1),("Table_2_Parameter_Availability",avail),("Table_3_India_Annual_Trends",t3),
 ("Table_4_Zone_Summary",Z9),("Table_5_State_Summary",S9),("Table_6_Population_Normalized",pd.read_csv("phase3_state_population.csv")),
 ("Table_7_Road_Normalized",pd.read_csv("phase3_road_2021_2022.csv")),("Table_8_Weather_Associations",P8),
 ("Table_9_Within_State_Associations",pd.read_csv("phase8_within_state_associations.csv").head(100)),
 ("Table_10_Fixed_Effects",FE8),("Table_11_Severity",P9I),("Table_12_Severity_Slopes",SL),
 ("Table_13_Injury_Coverage",COV),("Table_14_ML_Performance",M5),("Table_15_Data_Limitations",pd.DataFrame({"n":[1,2,3,4,5],"limitation":["no verified vehicle denominator","no Census 2021","humidity/visibility/fog/wind N/A","monthly accidents N/A","driver/vehicle/cause detail N/A"]}))])
save_wb("PHASE10_PUBLICATION_FIGURES.xlsx",[("FIGURE_CATALOG",figs)])
save_wb("PHASE10_ORIGINPRO_FINAL_MAP.xlsx",[("FIGURE_MAP",fmap)])
print("workbooks done")
