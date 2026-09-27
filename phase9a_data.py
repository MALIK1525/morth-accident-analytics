"""Phase 9 part A: severity datasets."""
import pandas as pd, numpy as np
P=pd.read_csv("phase2d_population_join.csv")
for c in ["Accidents","Fatalities","Population_Persons"]:
    P[c]=pd.to_numeric(P[c],errors="coerce")
P["Injured"]=pd.to_numeric(P["Injured"],errors="coerce")
P["Sev100"]=P.Fatalities/P.Accidents*100; P["Sev1"]=P.Fatalities/P.Accidents
P["AccLakh"]=P.Accidents/P.Population_Persons*1e5; P["FatLakh"]=P.Fatalities/P.Population_Persons*1e5
P["Injury_Data_Status"]=np.where(P.Injured.notna(),"VERIFIED","NOT_AVAILABLE")
P["Data_Quality_Flag"]=P.Population_Join_Confidence.map({"HIGH":"OK","MEDIUM":"TRANSFORMED"})
P.to_csv("phase9_severity_state_year.csv",index=False)
I=P.groupby("Year").agg(Acc=("Accidents","sum"),Fat=("Fatalities","sum"),Pop=("Population_Persons","sum"),
  Inj=("Injured","sum"),InjN=("Injured",lambda s:int(s.notna().sum()))).reset_index()
I["Sev100"]=I.Fat/I.Acc*100; I["AccLakh"]=I.Acc/I.Pop*1e5; I["FatLakh"]=I.Fat/I.Pop*1e5
I.to_csv("phase9_india_severity.csv",index=False)
Z=P.groupby(["Zone","Year"]).agg(Acc=("Accidents","sum"),Fat=("Fatalities","sum"),Pop=("Population_Persons","sum"),N=("State_UT","count")).reset_index()
Z["Sev100"]=Z.Fat/Z.Acc*100; Z["AccLakh"]=Z.Acc/Z.Pop*1e5; Z["FatLakh"]=Z.Fat/Z.Pop*1e5
Z.to_csv("phase9_zone_severity.csv",index=False)
g=P.groupby(["State_UT","Zone"])
SS=pd.DataFrame({"N":g.Year.count(),"Mean_Severity":g.Sev100.mean(),"Median_Severity":g.Sev100.median(),
 "SD_Severity":g.Sev100.std(),"Min_Severity":g.Sev100.min(),"Max_Severity":g.Sev100.max()}).reset_index()
ends=P.sort_values("Year").groupby("State_UT").agg(First_Year=("Year","first"),First_Severity=("Sev100","first"),
 Last_Year=("Year","last"),Last_Severity=("Sev100","last"))
SS=SS.merge(ends,on="State_UT")
SS["Absolute_Change"]=SS.Last_Severity-SS.First_Severity
SS["Percent_Change"]=SS.Absolute_Change/SS.First_Severity*100
SS["Status"]=np.where(SS.N>=4,"OK","INSUFFICIENT_N")
SS.to_csv("phase9_state_severity_summary.csv",index=False)
INJ=P[P.Injured.notna()].copy()
INJ["Inj_per100acc"]=INJ.Injured/INJ.Accidents*100; INJ["Inj_perlakh"]=INJ.Injured/INJ.Population_Persons*1e5
INJ.to_csv("phase9_injury_state_year.csv",index=False)
COV=P.groupby("Year").agg(N_states=("State_UT","count"),Inj_valid=("Injured",lambda s:int(s.notna().sum()))).reset_index()
COV["Coverage"]=np.where(COV.Inj_valid>=30,"STATE_VERIFIED","INDIA_ONLY")
COV.to_csv("phase9_injury_coverage.csv",index=False)
print("part A done", P.shape, I.shape, Z.shape, SS.shape, INJ.shape)
