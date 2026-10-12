"""Phase 7 analytical build (research documentation/analysis, not application code).
Every statistic is computed directly from verified files. Association language only.
"""
import csv
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
from scipy import stats as sstats

from app.data_pipeline.loader import ZONE_MAPPING

OUT = 'research_analysis'
os.makedirs(OUT, exist_ok=True)
S2Z = {s: z for z, ss in ZONE_MAPPING.items() for s in ss}

bench = pd.read_excel('data/MoRTH_Primary_Dataset_3.xlsx', 'CLEAN', header=2)
bench = bench[['State_UT', 'Year', 'Accidents', 'Fatalities', 'Injured']].copy()
bench['Zone'] = bench['State_UT'].map(S2Z)
# numeric coercion (NV -> NaN)
for c in ['Accidents', 'Fatalities', 'Injured']:
    bench[c] = pd.to_numeric(bench[c], errors='coerce')

# ---------- A. INDIA-YEAR ----------
iy = bench.groupby('Year').agg(
    Accidents=('Accidents', 'sum'), Fatalities=('Fatalities', 'sum'),
    States=('State_UT', 'nunique')).reset_index()
iyI = bench.dropna(subset=['Injured']).groupby('Year').agg(Injuries=('Injured', 'sum')).reset_index()
iy = iy.merge(iyI, on='Year', how='left')
# India-level verified injury totals (MoRTH AR Table 1.1 vintage; NOT state sums).
# State-sum Injuries stays NaN for 2023-24 (state data unavailable); India series kept separate.
INDIA_INJ = {2018: 464715, 2019: 449360, 2020: 346747, 2021: 384448, 2022: 443366, 2023: 462825, 2024: 471441}
iy['Injuries_India_Verified'] = iy.Year.map(INDIA_INJ)
iy['Fatalities_per_100_Accidents'] = (iy.Fatalities / iy.Accidents * 100).round(2)
for c in ['Accidents', 'Fatalities', 'Injuries']:
    iy[f'YoY_{c}'] = (iy[c].pct_change() * 100).round(2)
iy.to_csv(f'{OUT}/INDIA_YEAR_ANALYSIS.csv', index=False)

# ---------- B. STATE-YEAR ----------
bench.to_csv(f'{OUT}/STATE_YEAR_2018_2024.csv', index=False)

# ---------- D. ZONE-YEAR ----------
zy = bench.groupby(['Zone', 'Year']).agg(
    Accidents=('Accidents', 'sum'), Fatalities=('Fatalities', 'sum')).reset_index()
zy['India_Acc'] = zy.groupby('Year')['Accidents'].transform('sum')
zy['Share_pct'] = (zy.Accidents / zy.India_Acc * 100).round(2)
zy['YoY_Acc'] = zy.groupby('Zone')['Accidents'].pct_change().mul(100).round(2)
zy.to_csv(f'{OUT}/ZONE_YEAR_ANALYSIS.csv', index=False)

# ---------- trends ----------
def trend(x, y):
    m = pd.DataFrame({'x': x, 'y': y}).dropna()
    n = len(m)
    if n < 3:
        return [n, None, None, None, None, None, None, 'INSUFFICIENT_N']
    r = sstats.linregress(m.x, m.y)
    ci = r.stderr * sstats.t.ppf(0.975, n - 2) if n > 2 else None
    return [n, round(r.slope, 4), round(r.intercept, 2), round(r.rvalue ** 2, 4),
            round(r.pvalue, 6), round(r.slope - ci, 4), round(r.slope + ci, 4), 'OK']

trows = []
for col in ['Accidents', 'Fatalities', 'Injuries']:
    trows.append([col] + trend(iy.Year, iy[col]))
    trows[-1].append('descriptive linear trend; slope is fitted, not causal')
pd.DataFrame(trows, columns=['Series', 'N', 'Slope', 'Intercept', 'R2', 'P', 'CI_lo', 'CI_hi', 'Status', 'Note']
             ).to_csv(f'{OUT}/INDIA_TREND_STATISTICS.csv', index=False)

srows = []
for st, g in bench.groupby('State_UT'):
    for col in ['Accidents', 'Fatalities']:
        srows.append([st, g.Zone.iloc[0], col] + trend(g.Year, g[col]))
pd.DataFrame(srows, columns=['State_UT', 'Zone', 'Metric', 'N', 'Slope', 'Intercept', 'R2', 'P', 'CI_lo', 'CI_hi', 'Status']
             ).to_csv(f'{OUT}/STATE_TREND_STATISTICS.csv', index=False)

# ---------- matrices ----------
piv_a = bench.pivot_table(index='State_UT', columns='Year', values='Accidents', aggfunc='sum')
piv_a.to_csv(f'{OUT}/STATE_YEAR_ACCIDENT_MATRIX.csv')
piv_f = bench.pivot_table(index='State_UT', columns='Year', values='Fatalities', aggfunc='sum')
piv_f.to_csv(f'{OUT}/STATE_YEAR_FATALITY_MATRIX.csv')

# ---------- time-to-threshold ----------
TH = {'Accidents': [10000, 25000, 50000], 'Fatalities': [1000, 5000, 10000]}
trows2 = []
for st, g in bench.groupby('State_UT'):
    g = g.sort_values('Year')
    for metric, levels in TH.items():
        for T in levels:
            hit = g[g[metric] >= T]
            if hit.empty:
                trows2.append([st, metric, T, 'NOT_REACHED', '', '', len(g)])
            else:
                fy = hit.iloc[0]
                prev = g[g.Year < fy.Year]
                pv = prev.iloc[-1][metric] if len(prev) else np.nan
                trows2.append([st, metric, T, int(fy.Year), float(fy[metric]),
                               '' if pd.isna(pv) else float(pv), len(g)])
pd.DataFrame(trows2, columns=['State_UT', 'Metric', 'Threshold', 'First_Year', 'Value', 'Prev_Value', 'N']
             ).to_csv(f'{OUT}/TIME_TO_THRESHOLD.csv', index=False)

# ---------- E. weather associations ----------
wj = pd.read_csv('weather_morth_join.csv')
wm = wj[wj.Join_Status == 'JOINED'].copy()
wm['Severity'] = wm.Fatalities / wm.Accidents * 100
assoc = []
pairs = [('Annual_Rainfall_mm', 'Accidents'), ('Annual_Rainfall_mm', 'Fatalities'),
         ('Annual_Mean_Tmax_C', 'Accidents'), ('Annual_Mean_Tmax_C', 'Fatalities'),
         ('Annual_Mean_Tmin_C', 'Accidents'), ('Annual_Mean_Tmin_C', 'Fatalities'),
         ('Annual_Rainfall_mm', 'Severity'), ('Annual_Mean_Tmax_C', 'Severity'),
         ('Annual_Mean_Tmin_C', 'Severity')]
for x, y in pairs:
    d = wm[[x, y]].dropna()
    n = len(d)
    if n < 10:
        assoc.append([x, y, n, None, None, None, None, 'INSUFFICIENT_N'])
        continue
    pr = sstats.pearsonr(d[x], d[y])
    sp = sstats.spearmanr(d[x], d[y])
    assoc.append([x, y, n, round(pr[0], 4), round(pr[1], 6), round(sp[0], 4), round(sp[1], 6), 'OK'])
pd.DataFrame(assoc, columns=['X', 'Y', 'N', 'Pearson_r', 'Pearson_p', 'Spearman_rho', 'Spearman_p', 'Status']
             ).to_csv(f'{OUT}/WEATHER_ASSOCIATIONS.csv', index=False)
wm.to_csv(f'{OUT}/WEATHER_STATE_YEAR_MATCHED.csv', index=False)

# ---------- seasonal (NCRB vintage, separate) ----------
nc = pd.read_csv('02_VERIFIED_DATA/phase4/ncrb_monthwise_traffic_accidents_2024.csv')
road_states = nc[(nc.Section == 'Road') & (nc.Scope.isin(['States', 'UTs']))].copy()
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
ms = road_states[months].sum()
mdf = pd.DataFrame({'Month': months, 'Cases': ms.values})
mdf['Share_pct'] = (mdf.Cases / mdf.Cases.sum() * 100).round(2)
mdf['MoM_change_pct'] = (mdf.Cases.pct_change() * 100).round(2)
mdf['Source'] = 'NCRB ADSI 2024 Table 1A.5 (Road-States; NCRB vintage, NOT MoRTH)'
mdf.to_csv(f'{OUT}/NCRB_MONTHLY_2024.csv', index=False)

# ---------- supporting summaries ----------
sup = []
import glob as _g
for f in sorted(_g.glob('data/supporting_csv/*.csv')):
    d = pd.read_csv(f, dtype=str, keep_default_na=False)
    sup.append([os.path.basename(f), len(d), len(d.columns), '|'.join(d.columns[:8])])
pd.DataFrame(sup, columns=['File', 'Rows', 'Cols', 'First_Cols']).to_csv(f'{OUT}/SUPPORTING_INVENTORY.csv', index=False)

# ---------- quality ----------
q = []
for name, df, keys in [('INDIA_YEAR', iy, ['Year']), ('STATE_YEAR', bench, ['State_UT', 'Year']),
                       ('ZONE_YEAR', zy, ['Zone', 'Year']), ('WEATHER_MATCHED', wm, ['State_UT', 'Year'])]:
    q.append([name, len(df), len(df.columns), int(df.duplicated(subset=keys).sum()),
              int(df.isna().sum().sum()), round(df.isna().sum().sum() / df.size * 100, 2),
              sorted(df[keys[0]].dropna().unique().tolist())[:3]])
pd.DataFrame(q, columns=['Dataset', 'Rows', 'Cols', 'Dup_keys', 'Missing_cells', 'Missing_pct', 'Sample_keys']
             ).to_csv(f'{OUT}/DATASET_QUALITY_SUMMARY.csv', index=False)

# ---------- methods / ML plan / graph plan ----------
pd.DataFrame([
    ['India accident trend 2018-24', 'Year;Accidents', 'INDIA_YEAR', 'Descriptive + OLS slope', 'N=7 limits power', 7, 'READY'],
    ['State accident slopes', 'Year;Accidents by state', 'STATE_YEAR', 'OLS per state (N=7)', 'Low power; wide CI', 7, 'READY'],
    ['Weather association', 'Rain/Tmax/Tmin;Acc/Fat', 'WEATHER_MATCHED', 'Pearson+Spearman pooled', 'Scale confounding; N~236', 236, 'READY'],
    ['Weather x severity', 'Weather;Fatalities/Acc', 'WEATHER_MATCHED', 'Pearson+Spearman pooled', 'As above', 236, 'READY'],
    ['NCRB seasonality 2024', 'Month;Cases', 'NCRB_MONTHLY', 'Shares + MoM change', 'Single year; NCRB vintage', 12, 'READY'],
    ['ANOVA across zones', 'Zone;Accidents', 'ZONE_YEAR', 'ANOVA', 'Repeated measures; small N', 42, 'CONDITIONAL'],
    ['Chi-square causation', 'Cause categories', 'SUPPORTING', 'Chi-square', 'India-level only; no exposure', 0, 'DEFERRED'],
], columns=['Question', 'Variables', 'Dataset', 'Test', 'Assumptions_Limits', 'N', 'Status']
).to_csv(f'{OUT}/STATISTICAL_METHODS_MATRIX.csv', index=False)

pd.DataFrame([
    ['Linear Regression', 'Supervised', 'Next-year state accidents', 'Lag acc/fat/pop', 'phase5 N=175', 'State-year', 'Baseline interpretable model', 'YES', 'READY'],
    ['Random Forest Regression', 'Supervised', 'Next-year state accidents', 'Lag acc/fat/pop', 'phase5 N=175', 'State-year', 'Nonlinear baseline', 'YES', 'READY'],
    ['Gradient Boosting Regression', 'Supervised', 'Next-year state accidents', 'Lag acc/fat/pop', 'phase5 N=175', 'State-year', 'Strong tabular learner', 'YES', 'READY'],
    ['KNN Regression', 'Supervised (NOT unsupervised)', 'Next-year state accidents', 'Lag acc/fat/pop', 'phase5 N=175', 'State-year', 'Local-pattern check', 'YES', 'READY'],
    ['K-means Clustering', 'Unsupervised', 'State profiles', 'Normalized rates + severity', 'Needs scaled features', 'State', 'Typology exploration', 'PARTIAL', 'CONDITIONAL'],
], columns=['Algorithm', 'Type', 'Target', 'Features', 'Required_Data', 'Training_Unit', 'Potential_Use', 'Data_Availability', 'Status']
).to_csv(f'{OUT}/ML_METHOD_PLAN.csv', index=False)

pd.DataFrame([
    ['G1', 'India accident trend', 'INDIA_YEAR', 'Year', 'Accidents', 'Line', 'Year', 'Accidents', '-', 'INDIA_YEAR', 1, 'READY'],
    ['G2', 'India fatality trend', 'INDIA_YEAR', 'Year', 'Fatalities', 'Line', 'Year', 'Fatalities', '-', 'INDIA_YEAR', 1, 'READY'],
    ['G3', 'India injuries', 'INDIA_YEAR', 'Year', 'Injuries', 'Line', 'Year', 'Injuries', '-', 'INDIA_YEAR', 1, 'READY'],
    ['G4', 'Fatality ratio', 'INDIA_YEAR', 'Year', 'Fatalities_per_100_Accidents', 'Line', 'Year', 'Ratio', '-', 'INDIA_YEAR', 1, 'READY'],
    ['G5', 'Zone comparison', 'ZONE_YEAR', 'Zone', 'Accidents', 'Bar', 'Zone', 'Accidents', 'Year', 'ZONE_YEAR', 1, 'READY'],
    ['G6', 'Zone-year trend', 'ZONE_YEAR', 'Year', 'Accidents', 'Line', 'Year', 'Accidents', 'Zone', 'ZONE_YEAR', 1, 'READY'],
    ['G7', 'State comparison', 'STATE_YEAR', 'State', 'Accidents', 'Bar', 'State', 'Accidents', 'Year', 'STATE_YEAR', 1, 'READY'],
    ['G8', 'State-year heatmap', 'MATRICES', 'State x Year', 'Accidents', 'Heatmap', 'Year', 'State', '-', 'MATRICES', 1, 'READY'],
    ['G9', 'State trends', 'STATE_YEAR', 'Year', 'Accidents', 'Line', 'Year', 'Accidents', 'State', 'STATE_YEAR', 1, 'READY'],
    ['G10', 'Slope distribution', 'STATE_TRENDS', 'State', 'Slope', 'Bar+CI', 'State', 'Slope', '-', 'STATE_TRENDS', 1, 'READY'],
    ['W1', 'Rain vs accidents', 'WEATHER_MATCHED', 'Rainfall', 'Accidents', 'Scatter', 'Rainfall', 'Accidents', '-', 'WEATHER', 1, 'READY'],
    ['S1', 'NCRB monthly 2024', 'NCRB_MONTHLY', 'Month', 'Cases', 'Bar', 'Month', 'Cases', '-', 'NCRB', 2, 'READY'],
], columns=['Graph_ID', 'Research_Question', 'Dataset', 'Variables', 'Y_Var', 'Graph_Type', 'X', 'Y', 'Grouping', 'OriginPro_Sheet', 'Priority', 'Status']
).to_csv(f'{OUT}/GRAPH_PLAN.csv', index=False)
print('phase7 build complete')
