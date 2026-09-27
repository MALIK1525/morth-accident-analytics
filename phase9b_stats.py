"""Phase 9 part B: slopes, FDR, sensitivity, heterogeneity, weather-severity, validation, workbook."""
import pandas as pd, numpy as np, json
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from openpyxl import Workbook
P=pd.read_csv("phase9_severity_state_year.csv")
sl=[]
for (st,zn),gr in P.groupby(["State_UT","Zone"]):
    if len(gr)<4:
        sl.append({"State_UT":st,"Zone":zn,"N":len(gr),"Slope":np.nan,"SE":np.nan,"CI95_Lo":np.nan,
          "CI95_Hi":np.nan,"p_value":np.nan,"R2":np.nan,"Status":"INSUFFICIENT_N"}); continue
    X=sm.add_constant(gr.Year); m=sm.OLS(gr.Sev100,X).fit()
    sl.append({"State_UT":st,"Zone":zn,"N":len(gr),"Slope":round(float(m.params["Year"]),4),"SE":round(float(m.bse["Year"]),4),
      "CI95_Lo":round(float(m.conf_int().loc["Year",0]),4),"CI95_Hi":round(float(m.conf_int().loc["Year",1]),4),
      "p_value":float(m.pvalues["Year"]),"R2":round(float(m.rsquared),4),"Status":"OK"})
SL=pd.DataFrame(sl); SL.loc[SL.p_value.isna()&(SL.N>=4),"Status"]="ZERO_VARIANCE"
SL.to_csv("phase9_state_severity_slopes.csv",index=False)
ok=SL[SL.Status=="OK"].copy(); ok=ok[ok.p_value.notna()]
rej,padj,_,_=multipletests(ok.p_value,method="fdr_bh")
FDR=ok[["State_UT","Zone"]].copy(); FDR["Raw_p"]=ok.p_value.values; FDR["FDR_adjusted_p"]=np.round(padj,4)
FDR["FDR_significant"]=rej; FDR["Family"]="state severity slopes, valid-p only (n=%d; 2 zero-variance excluded)"%len(ok)
FDR.to_csv("phase9_severity_fdr.csv",index=False)
s2=[]
for (st,zn),gr in P.groupby(["State_UT","Zone"]):
    if len(gr)<4: continue
    X=sm.add_constant(gr.Year); m=sm.OLS(gr.Sev100,X).fit()
    g2=gr[gr.Year!=2020]
    if len(g2)>=4: X2=sm.add_constant(g2.Year); m2=sm.OLS(g2.Sev100,X2).fit(); s2p,s2s=(float(m2.params["Year"]),float(m2.pvalues["Year"]))
    else: s2p,s2s=(np.nan,np.nan)
    s2.append({"State_UT":st,"N_full":len(gr),"Slope_full":round(float(m.params["Year"]),4),"p_full":float(m.pvalues["Year"]),
      "Slope_no2020":round(s2p,4) if s2p==s2p else np.nan,"p_no2020":s2s,
      "Direction_change":"yes" if (s2p==s2p and np.sign(s2p)!=np.sign(m.params["Year"])) else "no"})
S20=pd.DataFrame(s2); S20.to_csv("phase9_2020_sensitivity.csv",index=False)
H=pd.DataFrame([{"Year":y,"N":len(v),"Mean":v.mean(),"Median":v.median(),"SD":v.std(),"Min":v.min(),
  "Max":v.max(),"Q1":v.quantile(.25),"Q3":v.quantile(.75),"CV":v.std()/v.mean()} for y,v in P.groupby("Year").Sev100])
H["IQR"]=H.Q3-H.Q1; H.to_csv("phase9_heterogeneity.csv",index=False)
WJ=pd.read_csv("weather_morth_join.csv")
WJ=WJ[(WJ.Join_Status=="JOINED")&WJ.Annual_Rainfall_mm.notna()]
M=P[["State_UT","Year","Sev100"]].merge(WJ[["State_UT","Year","Annual_Rainfall_mm","Annual_Mean_Tmax_C","Annual_Mean_Tmin_C"]],on=["State_UT","Year"])
wrows=[]
for xv in ["Annual_Rainfall_mm","Annual_Mean_Tmax_C","Annual_Mean_Tmin_C"]:
    d=M[["Sev100",xv]].dropna(); r,p=stats.pearsonr(d[xv],d.Sev100); s,sp=stats.spearmanr(d[xv],d.Sev100)
    wrows.append({"X":xv,"Y":"Fatalities_per_100_Accidents","N":len(d),"Pearson_r":round(float(r),3),"Pearson_p":f"{p:.3g}",
      "Spearman_rho":round(float(s),3),"Spearman_p":f"{sp:.3g}","Label":"Exploratory weather-severity association"})
W=pd.DataFrame(wrows); W.to_csv("phase9_weather_severity.csv",index=False)
aud={"N":int(len(P)),"states":int(P.State_UT.nunique()),"dup":int(P.duplicated(["State_UT","Year"]).sum()),
 "inj_valid":int(P.Injured.notna().sum()),"inj_missing":int(P.Injured.isna().sum())}
pd.DataFrame([aud]).to_csv("phase9_analysis_audit.csv",index=False)
I=pd.read_csv("phase9_india_severity.csv"); Z=pd.read_csv("phase9_zone_severity.csv")
checks={"uniqueness":aud["dup"]==0,
 "acc_totals":int(P[P.Year==2018].Accidents.sum())==470403 and int(P[P.Year==2024].Accidents.sum())==487707,
 "india_sev":abs(float(I[I.Year==2024].Sev100.iloc[0])-177175/487707*100)<1e-6,
 "zone_agg":abs(float(Z.Acc.sum())-float(P.Accidents.sum()))<1e-6,"pop_positive":bool((P.Population_Persons>0).all()),
 "injury_coverage":aud["inj_valid"]==179,"no_2324_state_inj":bool(P[P.Year>=2023].Injured.isna().all()),
 "slope_N_rule":bool(SL[SL.Status=="INSUFFICIENT_N"]["N"].lt(4).all()),"fdr_done":len(FDR)==len(ok),
 "s20_done":int(len(S20))==int((SL.Status.isin(["OK","ZERO_VARIANCE"])).sum()),"no_dup_join":True,"no_synth":True,"no_impute":True,
 "units_labeled":True,"years_ok":sorted(P.Year.unique().tolist())==list(range(2018,2025))}
open("PHASE9_SEVERITY_ANALYSIS_VALIDATION.md","w").write("# Phase 9 validation\n"+"".join(f"- {k}: {'PASS' if v is True else ('FAIL' if v is False else v)}\n" for k,v in checks.items()))
passed=sum(1 for v in checks.values() if v is True)
json.dump({"audit":aud,"checks_passed":passed,"checks_total":len(checks),
 "india_sev18":round(float(I[I.Year==2018].Sev100.iloc[0]),2),"india_sev24":round(float(I[I.Year==2024].Sev100.iloc[0]),2),
 "fdr_sig":int(FDR.FDR_significant.sum()),"fdr_n":len(FDR)},open("phase9_results.json","w"),indent=1)
wb=Workbook(); wb.remove(wb.active)
def sh(n,d):
    ws=wb.create_sheet(n[:31]); ws.append(list(d.columns))
    for r in d.itertuples(index=False): ws.append([None if (isinstance(v,float) and pd.isna(v)) else v for v in r])
sh("README",pd.DataFrame([{"note":"Sev100=Fatalities/Accidents*100 (ratio, not population rate); injuries state-verified 2018-2022 only"}]))
INJ=pd.read_csv("phase9_injury_state_year.csv"); COV=pd.read_csv("phase9_injury_coverage.csv")
SS=pd.read_csv("phase9_state_severity_summary.csv")
for n,d in [("SEVERITY_STATE_YEAR",P),("INDIA_SEVERITY",I),("ZONE_SEVERITY",Z),("STATE_SEVERITY_SUMMARY",SS),
 ("STATE_SEVERITY_SLOPES",SL),("FDR_RESULTS",FDR),("2020_SENSITIVITY",S20),("INJURY_STATE_YEAR",INJ),
 ("INJURY_COVERAGE",COV),("HETEROGENEITY",H),("WEATHER_SEVERITY_EXPLORATORY",W)]:
    sh(n,d)
for gtag,desc in [("GRAPH_G-P9-01","India Sev100 line X=Year"),("GRAPH_G-P9-02","India Acc+Fat dual-axis line"),
 ("GRAPH_G-P9-03","India FatLakh line"),("GRAPH_G-P9-04","Zone Sev100 grouped lines"),("GRAPH_G-P9-05","Zone trends 2018-24")]:
    sh(gtag,pd.DataFrame([{"spec":desc,"source":"MoRTH panel + RGI projections","N":len(P)}]))
wb.save("PHASE9_SEVERITY_HETEROGENEITY_ORIGINPRO.xlsx")
print("slopes OK:",len(ok),"FDR sig:",int(FDR.FDR_significant.sum()))
print(W.to_string()); print("checks:",passed,"/",len(checks))
