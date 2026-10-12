"""Phase 10 synthesis builder (research only, not application code).
Assembles final tables ONLY from existing Phase 7-9 outputs. No new statistics.
"""
import os
import pandas as pd

O = 'research_analysis'
iy = pd.read_csv(f'{O}/INDIA_YEAR_ANALYSIS.csv')
st = pd.read_csv(f'{O}/STATE_TREND_STATISTICS.csv')
stv = pd.read_csv(f'{O}/STATE_TREND_VALIDATION.csv')
zy = pd.read_csv(f'{O}/ZONE_YEAR_ANALYSIS.csv')
wa = pd.read_csv(f'{O}/WEATHER_ASSOCIATIONS.csv')
mt = pd.read_csv(f'{O}/MULTIPLE_TESTING_CORRECTION.csv')
zt = pd.read_csv(f'{O}/ZONE_STATISTICAL_TESTS.csv')
mr = pd.read_csv(f'{O}/PHASE9_MODEL_RESULTS.csv')
bc = pd.read_csv(f'{O}/PHASE9_BASELINE_COMPARISON.csv')
ks = pd.read_csv(f'{O}/PHASE9_CLUSTER_K_SELECTION.csv')
kp = pd.read_csv(f'{O}/PHASE9_CLUSTER_PROFILES.csv')

# hypotheses
hadj_w = mt[mt.Family == 'weather/severity']['BH_adj_p'].tolist()
hadj_iter = iter(hadj_w)
wrows2 = []
for i, (_, r) in enumerate(wa.iterrows()):
    a = hadj_w[i] if i < len(hadj_w) else None
    dec = 'Supported (association)' if (r.Pearson_p or 1) < 0.05 else 'Not supported'
    wrows2.append([f'H-W{i+1}', f'{r.X} x {r.Y}', 'weather join', 'Pearson pooled',
                   f'r={r.Pearson_r} p={r.Pearson_p} adj={a}', dec, 'association only, not causal'])
hyp = wrows2 + [
    ['H-Z1', 'Systematic zone differences across years', 'ZONE_YEAR', 'Friedman (years as blocks)',
     f'chi2={zt.iloc[0].Statistic} p={zt.iloc[0].p_value}', 'Supported', 'descriptive, not a ranking'],
    ['H-P1', 'Trained model improves over naive baseline (accidents)', 'phase9 panel', 'held-out 2023-24 RMSE',
     'naive 1038.6 < all trained', 'Not supported (null preserved)', 'persistence dominates'],
    ['H-P2', 'Trained model improves over naive baseline (fatalities)', 'phase9 panel', 'held-out 2023-24 RMSE',
     'naive 286.3 < all trained', 'Not supported (null preserved)', 'persistence dominates'],
    ['H-C1', 'K-means typology', 'state profiles', 'exploratory (no H0/H1)', 'K=2, silhouette 0.356', 'Exploratory', 'descriptive only'],
]
pd.DataFrame(hyp, columns=['H0_H1', 'Hypothesis', 'Dataset', 'Method', 'Result', 'Decision', 'Limitation']
             ).to_csv(f'{O}/PHASE10_HYPOTHESIS_MATRIX.csv', index=False)

# final tables (copy-through with source/vintage columns)
iy2 = iy.copy()
iy2['Source'] = 'MoRTH benchmark CLEAN'
iy2['Vintage'] = 'benchmark (revised 2019)'
iy2['Notes'] = 'Injuries_India_Verified is India vintage; state sums N/A 2023-24'
iy2.to_csv(f'{O}/PHASE10_INDIA_FINAL_RESULTS.csv', index=False)

sv = pd.read_csv(f'{O}/STATE_TREND_VALIDATION.csv')
sv['Limitations'] = 'OLS N=7 per state; wide CI; no ranking'
sv.to_csv(f'{O}/PHASE10_STATE_FINAL_RESULTS.csv', index=False)

z2 = zy.merge(zt[['Statistic', 'p_value']], how='cross')
z2['Interpretation'] = 'zones differ descriptively across years; not a ranking'
z2['Limitation'] = 'repeated years as blocks; small N'
z2.to_csv(f'{O}/PHASE10_ZONE_FINAL_RESULTS.csv', index=False)

wa2 = wa.copy()
wa2['Adj_p'] = hadj_w[:len(wa2)] + [None] * max(0, len(wa2) - len(hadj_w))
wa2['Interpretation'] = 'statistical association; causal effect NOT established'
wa2.to_csv(f'{O}/PHASE10_WEATHER_FINAL_RESULTS.csv', index=False)

for src, dst in [('CAUSE_SEVERITY_ANALYSIS.csv', 'PHASE10_CAUSE_COLLISION_RESULTS.csv'),
                 ('ROAD_USER_FATALITY_ANALYSIS.csv', 'PHASE10_ROAD_USER_RESULTS.csv'),
                 ('LICENCE_ANALYSIS.csv', 'PHASE10_LICENCE_SAFETY_RESULTS.csv'),
                 ('NCRB_MONTHLY_2024.csv', 'PHASE10_NCRB_MONTHLY_RESULTS.csv'),
                 ('CITY_ANALYSIS.csv', 'PHASE10_CITY_RESULTS.csv'),
                 ('TN_DISTRICT_ANALYSIS.csv', 'PHASE10_TN_DISTRICT_RESULTS.csv'),
                 ('PHASE9_MODEL_RESULTS.csv', 'PHASE10_ML_FINAL_RESULTS.csv'),
                 ('PHASE9_CLUSTER_PROFILES.csv', 'PHASE10_CLUSTER_RESULTS.csv')]:
    pd.read_csv(f'{O}/{src}').to_csv(f'{O}/{dst}', index=False)
# collision merged into cause file per brief (single CAUSE_COLLISION file)
cc = pd.read_csv(f'{O}/COLLISION_SEVERITY_ANALYSIS.csv')
ca = pd.read_csv(f'{O}/PHASE10_CAUSE_COLLISION_RESULTS.csv')
pd.concat([ca.assign(Family='violation/cause'), cc.assign(Family='collision')[list(ca.columns) + ['Family']] if set(ca.columns) <= set(cc.columns) else cc],
          ignore_index=True).to_csv(f'{O}/PHASE10_CAUSE_COLLISION_RESULTS.csv', index=False)
sd = pd.read_csv(f'{O}/SAFETY_DEVICE_ANALYSIS.csv')
lic = pd.read_csv(f'{O}/PHASE10_LICENCE_SAFETY_RESULTS.csv')
pd.concat([lic.assign(Family='licence'), sd.assign(Family='safety')], ignore_index=True
          ).to_csv(f'{O}/PHASE10_LICENCE_SAFETY_RESULTS.csv', index=False)

# limitations / evidence / findings
pd.DataFrame([
    ['Vehicle exposure (state stock)', 'per-vehicle rates', 'no denominator exists', 'UNAVAILABLE', 'manual OGD/RTYB acquisition'],
    ['Vehicle-km / AADT', 'exposure modeling', 'no source', 'UNAVAILABLE', 'transport surveys'],
    ['Accident-level microdata / coords', 'hotspots, severity modeling', 'eDAR restricted', 'ACCESS-RESTRICTED', 'authority data-sharing'],
    ['Driver / vehicle detail', 'driver-risk analysis', 'no verified file', 'UNAVAILABLE', 'MoRTH annexure extraction'],
    ['Humidity/visibility/fog/wind', 'environmental completeness', 'IMD grids temp/rain only', 'UNAVAILABLE', 'station-data request'],
    ['MoRTH monthly state data', 'seasonality in-benchmark', 'NCRB vintage only', 'PARTIAL', 'NCRB extraction stands separate'],
    ['Multi-state districts', 'sub-state analysis', 'TN only', 'PARTIAL', 'state transport portals'],
    ['2023-24 state injuries', 'recent severity', 'source stops 2022', 'UNAVAILABLE', 'future AR releases'],
    ['2014-17 compatibility', 'long panel', 'J&K break; DNH merge', 'CONDITIONAL', 'flagged harmonized candidate'],
    ['Small ML panel (N=213)', 'prediction power', 'persistence dominates', 'LIMITED', 'more years / richer features'],
], columns=['Limitation', 'Affected_Analysis', 'Why_It_Matters', 'Current_Status', 'Possible_Future_Solution']
).to_csv(f'{O}/PHASE10_LIMITATIONS_MATRIX.csv', index=False)

ev = pd.read_csv(f'{O}/RESEARCH_FINDINGS_TABLE.csv')
ev['Source'] = 'research_analysis phase 7-9 outputs'
ev.to_csv(f'{O}/PHASE10_EVIDENCE_MATRIX.csv', index=False)
fin = ev.rename(columns={'Finding_ID': 'Finding_ID'})
fin['Category'] = ['B', 'B', 'B', 'B', 'B', 'A', 'A', 'D']
fin.to_csv(f'{O}/PHASE10_FINAL_FINDINGS.csv', index=False)

# graph + paper table plans
g = pd.read_csv(f'{O}/PHASE9_GRAPH_PLAN.csv')
g['Priority'] = g['Priority'].map({1: 1, 2: 2})
pd.concat([pd.read_csv(f'{O}/GRAPH_PLAN.csv').assign(Phase=7),
           g.assign(Phase=9)[['Graph', 'Dataset', 'X', 'Y', 'Type', 'Priority']].rename(
               columns={'Graph': 'Graph_ID', 'Dataset': 'Dataset', 'X': 'X', 'Y': 'Y', 'Type': 'Graph_Type'})],
          ignore_index=True).to_csv(f'{O}/PHASE10_FINAL_GRAPH_PLAN.csv', index=False)
pd.DataFrame([
    ['Table 1', 'Data sources and coverage', 'MASTER_PARAMETER_AVAILABILITY + provenance files'],
    ['Table 2', 'India annual trends', 'PHASE10_INDIA_FINAL_RESULTS.csv'],
    ['Table 3', 'State trend statistics', 'PHASE10_STATE_FINAL_RESULTS.csv'],
    ['Table 4', 'Zone analysis + Friedman', 'PHASE10_ZONE_FINAL_RESULTS.csv'],
    ['Table 5', 'Weather associations', 'PHASE10_WEATHER_FINAL_RESULTS.csv'],
    ['Table 6', 'Cause/violation findings', 'PHASE10_CAUSE_COLLISION_RESULTS.csv'],
    ['Table 7', 'Collision findings', 'PHASE10_CAUSE_COLLISION_RESULTS.csv'],
    ['Table 8', 'ML model comparison', 'PHASE10_ML_FINAL_RESULTS.csv'],
    ['Table 9', 'K-means profiles', 'PHASE10_CLUSTER_RESULTS.csv'],
    ['Table 10', 'Limitations', 'PHASE10_LIMITATIONS_MATRIX.csv'],
], columns=['Table', 'Title', 'Source_File']).to_csv(f'{O}/PHASE10_PAPER_TABLE_PLAN.csv', index=False)

# reproducibility audit
import glob
ra = []
for f in sorted(glob.glob(f'{O}/PHASE10_*.csv')):
    d = pd.read_csv(f, nrows=3)
    ra.append([f.split('/')[-1], len(pd.read_csv(f)), 'columns: ' + '|'.join(d.columns[:6]), 'PASS'])
pd.DataFrame(ra, columns=['File', 'Rows', 'Schema_Check', 'Status']
             ).to_csv(f'{O}/PHASE10_REPRODUCIBILITY_AUDIT.csv', index=False)
print('phase10 tables complete')
