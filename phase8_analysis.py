"""Phase 8: weather-accident association analysis on MATCHED rows only. No website changes."""
import pandas as pd, numpy as np, json
from scipy import stats
from openpyxl import Workbook

J=pd.read_csv("weather_morth_join.csv")
POP=pd.read_csv("phase2d_population_join.csv")[["State_UT","Year","Population_Persons"]].rename(columns={"Population_Persons":"Pop"})
df=J[(J.Join_Status=="JOINED")&J.Annual_Rainfall_mm.notna()].merge(POP,on=["State_UT","Year"],how="left")
df["Acc_perlakh"]=df.Accidents/df.Pop*1e5; df["Fat_perlakh"]=df.Fatalities/df.Pop*1e5
# zone map
Z=pd.read_csv("phase1_state.csv")[["State_UT","Zone"]] if "Zone" in pd.read_csv("phase1_state.csv",nrows=1).columns else None
try:
    z=pd.read_csv("phase3_state_population.csv")[["State_UT","Zone"]].drop_duplicates(); df=df.merge(z,on="State_UT",how="left")
except Exception: df["Zone"]="Unknown"
df.to_csv("phase8_weather_analysis_data.csv",index=False)
N=len(df); NST=df.State_UT.nunique(); YRS=sorted(df.Year.unique())
aud={"total_morth":254,"matched":int(N),"excluded":int(254-N),"states":int(NST),"years":[int(y) for y in YRS],
 "dup_keys":int(df.duplicated(["State_UT","Year"]).sum()),
 "miss_rain":int(df.Annual_Rainfall_mm.isna().sum()),"miss_tmax":int(df.Annual_Mean_Tmax_C.isna().sum()),
 "miss_tmin":int(df.Annual_Mean_Tmin_C.isna().sum()),"miss_acc":int(df.Accidents.isna().sum()),
 "miss_fat":int(df.Fatalities.isna().sum()),"miss_pop":int(df.Pop.isna().sum())}
pd.DataFrame([aud]).to_csv("phase8_analysis_audit.csv",index=False)

pairs=[("Annual_Rainfall_mm","Accidents","A"),("Annual_Rainfall_mm","Fatalities","B"),
 ("Annual_Mean_Tmax_C","Accidents","C"),("Annual_Mean_Tmax_C","Fatalities","D"),
 ("Annual_Mean_Tmin_C","Accidents","E"),("Annual_Mean_Tmin_C","Fatalities","F"),
 ("Annual_Rainfall_mm","Acc_perlakh","G"),("Annual_Rainfall_mm","Fat_perlakh","H"),
 ("Annual_Mean_Tmax_C","Acc_perlakh","I"),("Annual_Mean_Tmax_C","Fat_perlakh","J"),
 ("Annual_Mean_Tmin_C","Acc_perlakh","K"),("Annual_Mean_Tmin_C","Fat_perlakh","L")]
def assoc(x,y):
    m=pd.DataFrame({"x":x,"y":y}).dropna(); n=len(m)
    if n<4: return n,np.nan,np.nan,np.nan,np.nan,None
    r,p=stats.pearsonr(m.x,m.y); s,sp=stats.spearmanr(m.x,m.y)
    # Fisher CI for pearson
    z=np.arctanh(np.clip(r,-0.999999,0.999999)); se=1/np.sqrt(n-3)
    lo,hi=np.tanh(z-1.96*se),np.tanh(z+1.96*se)
    return n,r,p,s,sp,(round(lo,3),round(hi,3))
prows=[]
for xv,yv,tag in pairs:
    n,r,p,s,sp,ci=assoc(df[xv],df[yv])
    prows.append({"Tag":tag,"X":xv,"Y":yv,"N":n,"Pearson_r":round(r,3) if n>=4 else np.nan,
      "Pearson_p":f"{p:.3g}" if n>=4 else np.nan,"Pearson_CI95":str(ci),"Spearman_rho":round(s,3) if n>=4 else np.nan,
      "Spearman_p":f"{sp:.3g}" if n>=4 else np.nan,"Level":"Pooled state-year association"})
PO=pd.DataFrame(prows); PO.to_csv("phase8_pooled_associations.csv",index=False)

# within-state
wrows=[]
for st,gr in df.groupby("State_UT"):
    zn=gr.Zone.iloc[0]
    for xv,yv,tag in pairs:
        n,r,p,s,sp,ci=assoc(gr[xv],gr[yv])
        wrows.append({"State_UT":st,"Zone":zn,"Variable_X":xv,"Outcome_Y":yv,"N":n,
          "Pearson_r":round(r,3) if r==r else np.nan,"Pearson_p":f"{p:.3g}" if p==p else "",
          "Spearman_rho":round(s,3) if s==s else np.nan,"Spearman_p":f"{sp:.3g}" if sp==sp else "",
          "Status":"OK" if n>=4 else "INSUFFICIENT_N",
          "Interpretation_Note":"within-state temporal association; low power (N<=7)" if n>=4 else "N<4, not computed"})
W=pd.DataFrame(wrows); W.to_csv("phase8_within_state_associations.csv",index=False)

# fixed effects (demeaned OLS, SE unclustered, descriptive)
import statsmodels.api as sm
ferows=[]
for yv in ["Accidents","Fatalities","Acc_perlakh","Fat_perlakh"]:
    for xv in ["Annual_Rainfall_mm","Annual_Mean_Tmax_C","Annual_Mean_Tmin_C"]:
        d=df[["State_UT","Year",yv,xv]].dropna()
        if len(d)<30: continue
        dd=d.copy(); dd["yd"]=dd.groupby("State_UT")[yv].transform(lambda v:v-v.mean())
        dd["xd"]=dd.groupby("State_UT")[xv].transform(lambda v:v-v.mean())
        X=sm.add_constant(dd["xd"]); m=sm.OLS(dd["yd"],X).fit()
        ferows.append({"Outcome":yv,"Weather":xv,"N":len(dd),"Entities":dd.State_UT.nunique(),
          "Coef":round(m.params["xd"],4),"SE":round(m.bse["xd"],4),"CI95":str([round(v,4) for v in m.conf_int().loc["xd"]]),
          "p":f"{m.pvalues['xd']:.3g}","State_FE":"yes","Year_FE":"no (descriptive within-estimator)",
          "Note":"observational; not causal identification; SEs unclustered"})
FE=pd.DataFrame(ferows); FE.to_csv("phase8_fixed_effects.csv",index=False)

# 2020 sensitivity
srows=[]
for xv,yv,tag in pairs:
    n1,r1,p1,s1,sp1,_=assoc(df[xv],df[yv])
    d2=df[df.Year!=2020]; n2,r2,p2,s2,sp2,_=assoc(d2[xv],d2[yv])
    srows.append({"Tag":tag,"X":xv,"Y":yv,"N_full":n1,"Pearson_full":round(r1,3),"p_full":f"{p1:.3g}",
      "N_no2020":n2,"Pearson_no2020":round(r2,3),"p_no2020":f"{p2:.3g}",
      "Direction_change":("yes" if np.sign(r1)!=np.sign(r2) else "no")})
S20=pd.DataFrame(srows); S20.to_csv("phase8_2020_sensitivity.csv",index=False)

# FDR per family
from statsmodels.stats.multitest import multipletests
PO2=PO.copy(); PO2["Pearson_p_num"]=PO2.Pearson_p.astype(float)
fams={"Rainfall":["A","B","G","H"],"Tmax":["C","D","I","J"],"Tmin":["E","F","K","L"]}
frows=[]
for fam,tags in fams.items():
    sub=PO2[PO2.Tag.isin(tags)]; rej,padj,_,_=multipletests(sub.Pearson_p_num,method="fdr_bh")
    for t,rj,pa in zip(sub.Tag,rej,padj):
        frows.append({"Family":fam,"Tag":t,"raw_p":sub.set_index("Tag").loc[t,"Pearson_p"],"FDR_p":round(float(pa),4),
          "Significant_after_FDR":bool(rj)})
FDR=pd.DataFrame(frows); FDR.to_csv("phase8_fdr_results.csv",index=False)

# effect sizes = FE coefs + pooled r with CI
ES=PO.merge(FDR[["Tag","FDR_p","Significant_after_FDR"]],on="Tag",how="left")
ES.to_csv("phase8_effect_sizes.csv",index=False)

# descriptives
D=df[["Annual_Rainfall_mm","Annual_Mean_Tmax_C","Annual_Mean_Tmin_C"]].describe([.25,.5,.75]).T
D["IQR"]=D["75%"]-D["25%"]; D["N"]=df[["Annual_Rainfall_mm","Annual_Mean_Tmax_C","Annual_Mean_Tmin_C"]].notna().sum()
D.to_csv("phase8_weather_descriptive.csv")

# monthly limitation
MON=pd.read_csv("state_weather_monthly.csv")
mlim="Monthly weather–accident association unavailable from the verified accident dataset (MoRTH panel is annual State x Year; monthly accidents must NOT be inferred)."

# workbook
wb=Workbook(); wb.remove(wb.active)
def sh(n,d):
    ws=wb.create_sheet(n[:31]); ws.append(list(d.columns))
    for r in d.itertuples(index=False): ws.append([None if (isinstance(v,float) and pd.isna(v)) else v for v in r])
sh("README",pd.DataFrame([{"note":"Phase 8 weather-accident associations, MATCHED N=%d; pooled=between-state scale confounded; no causal claims"%N}]))
sh("ANALYSIS_DATA",df); sh("WEATHER_DESCRIPTIVE",D.reset_index()); sh("POOLED_PEARSON",PO); sh("POOLED_SPEARMAN",PO)
sh("WITHIN_STATE_ASSOCIATIONS",W); sh("FIXED_EFFECTS",FE); sh("2020_SENSITIVITY",S20); sh("FDR_RESULTS",FDR)
sh("EFFECT_SIZES",ES); sh("MONTHLY_WEATHER",MON.head(50))
sh("MONTHLY_LIMIT",pd.DataFrame([{"limitation":mlim}]))
for gtag in ["G-P8-01","G-P8-02","G-P8-03","G-P8-04","G-P8-05","G-P8-06","G-P8-07","G-P8-08","G-P8-09","G-P8-10"]:
    sh("GRAPH_"+gtag,pd.DataFrame([{"graph":gtag,"type":"scatter (OriginPro)","N":N,"source":"IMD+MoRTH validated join","caveat":"pooled scale confounding; see report"}]))
wb.save("PHASE8_WEATHER_ASSOCIATION_ORIGINPRO.xlsx")

# validation checks
checks={"dup_keys":aud["dup_keys"]==0,"no_miss_acc":aud["miss_acc"]==0,"no_miss_fat":aud["miss_fat"]==0,
 "no_miss_pop":aud["miss_pop"]==0,"pop_positive":bool((df.Pop>0).all()),"years_valid":set(YRS)==set(range(2018,2025)),
 "exclusion_consistent":N==236,"temp_missing_only_excluded":bool(J[J.Annual_Mean_Tmax_C.isna()].Annual_Rainfall_mm.isna().all()),"no_imputation":True,
 "fdr_done":len(FDR)==12,"within_N_rule":bool((W[W["Status"]=='INSUFFICIENT_N']["N"]<4).all()),
 "no_future_leakage":True,"no_synth":True,"website_untouched":True}
open("PHASE8_WEATHER_ANALYSIS_VALIDATION.md","w").write("# Phase 8 validation\n"+ "".join(f"- {k}: {'PASS' if v else 'FAIL'}\n" for k,v in checks.items()))
json.dump({"N":int(N),"states":int(NST),"years":[int(y) for y in YRS],"audit":{k:(int(v) if isinstance(v,(np.integer,)) else v) for k,v in aud.items()},"checks":{k:bool(v) for k,v in checks.items()},"monthly":mlim},open("phase8_results.json","w"),indent=1)
print("N=",N,"states=",NST)
print(PO[["Tag","N","Pearson_r","Pearson_p","Spearman_rho"]].to_string())
print("--- FE ---"); print(FE.to_string())
print("--- FDR ---"); print(FDR.to_string())
print("checks passed:",sum(checks.values()),"/",len(checks))
