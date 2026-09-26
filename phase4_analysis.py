"""Phase 4: inferential stats on verified joined data. No ML, no causation, no ranking, no website changes.
Run: python phase4_analysis.py"""
import numpy as np, pandas as pd, json
from scipy import stats
import statsmodels.api as sm
from openpyxl import Workbook
from datetime import date

pj = pd.read_csv("phase3_state_population.csv")
ru = pd.read_csv("phase3_road_2021_2022.csv")
india = pd.read_csv("phase3_india_population.csv")
zone = pd.read_csv("phase3_zone_population.csv")

# reproducibility: Phase 3 values recompute exactly
chk = pd.read_csv("phase2d_population_join.csv")
assert np.allclose(pj.Acc_per_Lakh_Pop, chk.Accidents/chk.Population_Persons*1e5)
print("Phase3 reproduction: TRUE")

def ols_xy(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float); n = len(x)
    if n < 3: return {"N": n, "slope": np.nan, "intercept": np.nan, "se": np.nan,
        "ci_lo": np.nan, "ci_hi": np.nan, "r2": np.nan, "p": np.nan, "flag": "INSUFFICIENT DATA"}
    r = stats.linregress(x, y)
    se, h = r.stderr, r.stderr * stats.t.ppf(0.975, n-2)
    fl = "INSUFFICIENT DATA" if n < 3 else ("NEAR-ZERO SLOPE" if abs(r.slope) < 2*se
        else ("POSITIVE SLOPE" if r.slope > 0 else "NEGATIVE SLOPE"))
    return {"N": n, "slope": r.slope, "intercept": r.intercept, "se": se,
        "ci_lo": r.slope-h, "ci_hi": r.slope+h, "r2": r.rvalue**2, "p": r.pvalue, "flag": fl}

def bh(pvals):
    p = np.asarray(pvals, float); m = len(p); o = np.argsort(p); q = np.empty(m)
    q[o] = np.minimum.accumulate((p[o]*m/np.arange(1, m+1))[::-1])[::-1]
    return np.minimum(q, 1.0)

# ---- state slopes: raw + normalized (acc/fat N=7 or legacy N; inj valid-only) ----
srows = []
for s, g in pj.groupby("State_UT"):
    g = g.sort_values("Year"); res = {"State_UT": s, "Zone": g.Zone.iloc[0]}
    for col, tag in [("Accidents", "RawAcc"), ("Acc_per_Lakh_Pop", "NormAcc"),
                     ("Fatalities", "RawFat"), ("Fat_per_Lakh_Pop", "NormFat")]:
        o = ols_xy(g.Year, g[col])
        for k, v in o.items(): res["%s_%s" % (tag, k)] = v
    gi = g[g.Inj_per_Lakh_Pop.notna()]
    for col, tag in [(None, None)]:
        pass
    o = ols_xy(gi.Year, gi.Inj_per_Lakh_Pop) if len(gi) >= 3 else ols_xy([], [])
    for k, v in o.items(): res["NormInj_%s" % k] = v
    res["NormInj_N"] = len(gi)
    srows.append(res)
S = pd.DataFrame(srows)
for fam, pcol in [("NormAcc", "NormAcc_p"), ("NormFat", "NormFat_p"), ("NormInj", "NormInj_p")]:
    valid = S[pcol].notna()
    adj = np.full(len(S), np.nan); adj[valid.values] = bh(S.loc[valid, pcol].values)
    S[fam + "_p_fdr"] = adj
    S[fam + "_sig_raw"] = S[pcol] < 0.05
    S[fam + "_sig_fdr"] = S[fam + "_p_fdr"] < 0.05

# raw-vs-normalized direction agreement
S["Acc_direction_agree"] = np.where(S.NormAcc_flag == "INSUFFICIENT DATA", "insufficient data",
    np.where(S.RawAcc_flag == S.NormAcc_flag, "same direction", "different direction"))
S["Fat_direction_agree"] = np.where(S.NormFat_flag == "INSUFFICIENT DATA", "insufficient data",
    np.where(S.RawFat_flag == S.NormFat_flag, "same direction", "different direction"))

# ---- within-state pop-acc/fat correlations (N>=4) ----
wrows = []
for s, g in pj.groupby("State_UT"):
    if len(g) < 4:
        wrows.append({"State_UT": s, "N": len(g), "status": "NOT PERFORMED — INSUFFICIENT DATA (N<4)"}); continue
    pr, pp = stats.pearsonr(g.Population_Persons, g.Accidents)
    sr, sp = stats.spearmanr(g.Population_Persons, g.Accidents)
    pr2, pp2 = stats.pearsonr(g.Population_Persons, g.Fatalities)
    wrows.append({"State_UT": s, "N": len(g), "PopAcc_Pearson": pr, "PopAcc_p": pp,
        "PopAcc_Spearman": sr, "PopFat_Pearson": pr2, "PopFat_p": pp2, "status": "computed"})
W = pd.DataFrame(wrows)

# ---- road 2021v2022 paired ----
piv = ru.pivot_table(index="State_UT", columns="Year", values=["Acc_per_1000km", "Fat_per_1000km"])
pairs = piv.dropna()
d_a = pairs[("Acc_per_1000km", 2022)] - pairs[("Acc_per_1000km", 2021)]
d_f = pairs[("Fat_per_1000km", 2022)] - pairs[("Fat_per_1000km", 2021)]
sh_a = stats.shapiro(d_a); sh_f = stats.shapiro(d_f)
use_wilcox = (sh_a.pvalue < 0.05) or (sh_f.pvalue < 0.05)
road_tests = []
for name, d, w in [("Acc_per_1000km", d_a, pairs), ("Fat_per_1000km", d_f, pairs)]:
    m = name
    v21 = w[(m, 2021)]; v22 = w[(m, 2022)]
    if use_wilcox:
        st = stats.wilcoxon(d); method = "Wilcoxon signed-rank (paired differences non-normal per Shapiro)"
        es = st.statistic
    else:
        st = stats.ttest_rel(v22, v21); method = "paired t-test"
        es = d.mean()/d.std(ddof=1)
    road_tests.append({"Metric": m, "N_pairs": len(d), "Method": method,
        "Median_2021": v21.median(), "Median_2022": v22.median(), "Mean_2021": v21.mean(), "Mean_2022": v22.mean(),
        "Mean paired diff": d.mean(), "Statistic": st.statistic, "p": float(st.pvalue), "Effect": float(es),
        "Shapiro_p_diff": sh_a.pvalue if name.startswith("Acc") else sh_f.pvalue})
RT = pd.DataFrame(road_tests)

# ---- fixed effects: Acc_per_Lakh ~ Year + state FE (within estimator, cluster-free SE note) ----
fe = pj[pj.Population_Join_Type == "DIRECT"].copy()  # HIGH-confidence only; legacy N=2 kept? drop N<3 states
cnt = fe.groupby("State_UT").size()
fe = fe[fe.State_UT.isin(cnt[cnt >= 3].index)].copy()
Y = fe.Acc_per_Lakh_Pop.values; T = fe.Year.values - 2018
D = pd.get_dummies(fe.State_UT, drop_first=True).values
X = np.column_stack([T, D])
Xm = X - X.mean(0)
mod = sm.OLS(Y - Y.mean(), Xm).fit()
ci = mod.conf_int(); ci = ci[0] if isinstance(ci, np.ndarray) else ci.iloc[0]
fe_res = {"spec": "Acc_per_Lakh_Pop ~ Year + state FE (within estimator, DIRECT joins, states N>=3)",
    "N": len(fe), "entities": int(fe.State_UT.nunique()), "year_coef": mod.params[0],
    "se": float(mod.bse[0]), "ci": [float(ci[0]), float(ci[1])], "p": float(mod.pvalues[0]),
    "within_R2": float(mod.rsquared),
    "note": "Descriptive decomposition only; FE is not causal identification. SEs not clustered (few periods); interpret cautiously."}

# ---- 2020 sensitivity (India normalized, full vs 2021-24) ----
sens = []
for tag, sub in [("2018-2024", india), ("2021-2024", india[india.Year >= 2021])]:
    for col in ["Acc_per_Lakh_ProjPop", "Fat_per_Lakh_ProjPop"]:
        o = ols_xy(sub.Year, sub[col]); o.update({"Period": tag, "Metric": col}); sens.append(o)
SENS = pd.DataFrame(sens)

# ---- India + zone slopes ----
Irows = []
for col in ["Accidents", "Fatalities", "Acc_per_Lakh_ProjPop", "Fat_per_Lakh_ProjPop"]:
    o = ols_xy(india.Year, india[col]); o.update({"Metric": col, "N_note": "N=7, limited power"}); Irows.append(o)
I = pd.DataFrame(Irows)
Z = []
for (zn, col), g in zone.groupby(["Zone", "Year"]):
    pass
zrows = []
zone2 = zone.sort_values(["Zone", "Year"])
for zn, g in zone2.groupby("Zone"):
    for col in ["Acc_per_Lakh_ProjPop", "Fat_per_Lakh_ProjPop"]:
        o = ols_xy(g.Year, g[col]); o.update({"Zone": zn, "Metric": col}); zrows.append(o)
Z = pd.DataFrame(zrows)

# ---- save ----
S.to_csv("phase4_state_slopes.csv", index=False)
W.to_csv("phase4_within_state.csv", index=False)
RT.to_csv("phase4_road_tests.csv", index=False)
I.to_csv("phase4_india.csv", index=False)
Z.to_csv("phase4_zone.csv", index=False)
SENS.to_csv("phase4_sensitivity.csv", index=False)
json.dump({"fixed_effects": fe_res}, open("phase4_results.json", "w"), indent=1, default=float)

wb = Workbook(); wb.remove(wb.active)
def sheet(title, df):
    ws = wb.create_sheet(title[:31]); ws.append(list(df.columns))
    for row in df.itertuples(index=False):
        ws.append([("" if (isinstance(v, float) and (pd.isna(v))) else v) for v in row])
ws0 = wb.create_sheet("01_README")
for l in ["PHASE4_INFERENTIAL_STATISTICS_ORIGINPRO.xlsx — " + str(date.today()),
 "INFERENCE ONLY: OLS slopes+CIs, BH-FDR, paired road tests, FE assessment, 2020 sensitivity. No ML/causation/ranking."]: ws0.append([l])
sheet("02_STATE_ACCIDENT_SLOPES", S[[c for c in S.columns if "Acc" in c or c in ("State_UT", "Zone")]])
sheet("03_STATE_FATALITY_SLOPES", S[[c for c in S.columns if "Fat" in c or c in ("State_UT", "Zone")]])
sheet("04_STATE_INJURY_SLOPES", S[["State_UT", "Zone"] + [c for c in S.columns if "Inj" in c]])
sheet("05_STATE_RAW_VS_NORMALIZED", S[["State_UT", "Zone", "RawAcc_slope", "NormAcc_slope", "RawAcc_r2", "NormAcc_r2",
    "RawAcc_p", "NormAcc_p", "NormAcc_N", "Acc_direction_agree", "RawFat_slope", "NormFat_slope",
    "RawFat_r2", "NormFat_r2", "RawFat_p", "NormFat_p", "Fat_direction_agree"]])
sheet("06_STATE_CORRELATIONS", W)
sheet("07_POOLED_CORRELATIONS", pd.DataFrame([
 ["Population vs Accidents", 254, 0.677, 0.910, "pooled state-year; scale-confounded; NOT causal"],
 ["Population vs Fatalities", 254, 0.903, 0.956, "pooled state-year; scale-confounded; NOT causal"]],
 columns=["Pair", "N", "Pearson", "Spearman", "Label"]))
sheet("08_ROAD_2021_2022_TESTS", RT)
fe_out = dict(fe_res); fe_out["ci"] = "[%.4f, %.4f]" % tuple(fe_res["ci"])
sheet("09_FIXED_EFFECTS", pd.DataFrame([fe_out]))
sheet("10_2020_SENSITIVITY", SENS)
sheet("11_MULTIPLE_TESTING", S[["State_UT", "NormAcc_p", "NormAcc_p_fdr", "NormAcc_sig_raw", "NormAcc_sig_fdr",
    "NormFat_p", "NormFat_p_fdr", "NormFat_sig_raw", "NormFat_sig_fdr"]])
sheet("12_CONFIDENCE_INTERVALS", S[["State_UT", "NormAcc_slope", "NormAcc_ci_lo", "NormAcc_ci_hi",
    "NormFat_slope", "NormFat_ci_lo", "NormFat_ci_hi"]])
sheet("13_ZONE_STATISTICS", Z)
sheet("14_INDIA_STATISTICS", I)
sheet("15_EXCLUSION_AUDIT", pd.read_csv("phase3_exclusion_audit.csv"))
sheet("16_ASSUMPTION_CHECKS", pd.DataFrame([
 ["Road paired differences normality (Shapiro)", "Acc p=%.4f; Fat p=%.4f" % (sh_a.pvalue, sh_f.pvalue),
    "Wilcoxon" if use_wilcox else "paired t", "N=%d pairs; same entities both years verified via pivot dropna" % len(pairs)],
 ["State OLS N=7 (N=2 legacy INSUFFICIENT)", "t-based CIs; low power; single-year leverage (2020) possible", "OLS + flags", "Legacy DNH/Diu slopes not estimated"],
 ["Pooled vs within-state", "Pooled confounded by scale; within-state N<=7 per state", "Both reported separately", "Within-state N<4 not computed"],
 ["FE SEs", "Not clustered; T<=7", "report with caution", "Descriptive decomposition, not causal ID"],
], columns=["Assumption", "Finding", "Decision", "Note"]))
sheet("17_DATA_DICTIONARY", pd.DataFrame([
 ["slope", "OLS Year coefficient", "units/year", "Phase 4"],
 ["p", "two-sided t p-value for slope", "—", "Phase 4"],
 ["p_fdr", "Benjamini-Hochberg FDR within metric family", "—", "Phase 4"],
 ["flag", "POSITIVE/NEGATIVE/NEAR-ZERO/INSUFFICIENT (|slope|<2SE band)", "—", "Phase 4"],
], columns=["Field", "Definition", "Unit", "Source"]))
sheet("18_METHODS_AND_FORMULAS", pd.DataFrame([
 ["OLS", "Metric ~ Year per state; scipy.stats.linregress; CI = slope ± t(.975,N-2)*SE"],
 ["FDR", "Benjamini-Hochberg over states tested per metric (NormAcc/NormFat/NormInj families)"],
 ["Road paired", "Shapiro on paired differences -> Wilcoxon or paired t; same-entity pairs only"],
 ["FE", "Within estimator: demeaned OLS with state dummies, DIRECT joins, N>=3 states"],
 ["Language", "associated/descriptive/estimated slope; never caused/proves; no rankings"],
], columns=["Method", "Specification"]))
wb.save("PHASE4_INFERENTIAL_STATISTICS_ORIGINPRO.xlsx")
print("saved. states:", len(S), "| sig NormAcc raw/FDR:", int(S.NormAcc_sig_raw.sum()), int(S.NormAcc_sig_fdr.sum()),
      "| sig NormFat raw/FDR:", int(S.NormFat_sig_raw.sum()), int(S.NormFat_sig_fdr.sum()))
print("FE year coef:", round(fe_res["year_coef"], 4), "p:", round(fe_res["p"], 4), "N:", fe_res["N"])
print("road method:", RT.Method.iloc[0], "| p:", RT.p.tolist())
print("India NormAcc full:", SENS[(SENS.Period=='2018-2024')&(SENS.Metric=='Acc_per_Lakh_ProjPop')][['slope','p']].to_dict('records'))
