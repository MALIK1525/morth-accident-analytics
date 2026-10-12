"""Phase 8 cross-factor analysis (research only, not application code).
All statistics computed from verified files. Association language only.
"""
import csv
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
from scipy import stats as sstats

OUT = 'research_analysis'
SUP = 'data/supporting_csv'

def bh(pvals):
    """Benjamini-Hochberg adjusted p-values."""
    p = np.array(pvals, float)
    n = len(p)
    order = np.argsort(p)
    adj = np.empty(n)
    adj[order] = np.minimum.accumulate((p[order] * n / np.arange(1, n + 1))[::-1])[::-1]
    return np.clip(adj, 0, 1).tolist()

def pear_spear(x, y):
    d = pd.DataFrame({'x': x, 'y': y}).dropna()
    n = len(d)
    if n < 10:
        return [n, None, None, None, None, 'INSUFFICIENT_N']
    pr = sstats.pearsonr(d.x, d.y)
    sp = sstats.spearmanr(d.x, d.y)
    return [n, round(pr[0], 4), round(pr[1], 6), round(sp[0], 4), round(sp[1], 6), 'OK']

# ---------- validation gate (Part 32) ----------
bench = pd.read_csv(f'{OUT}/STATE_YEAR_2018_2024.csv')
for c in ['Accidents', 'Fatalities']:
    bench[c] = pd.to_numeric(bench[c], errors='coerce')
PUB_A = {2018: 470403, 2019: 456959, 2020: 372181, 2021: 412432, 2022: 461312, 2023: 480583, 2024: 487707}
PUB_F = {2018: 157593, 2019: 158984, 2020: 138383, 2021: 153972, 2022: 168491, 2023: 172890, 2024: 177175}
for y in range(2018, 2025):
    g = bench[bench.Year == y]
    assert int(g.Accidents.sum()) == PUB_A[y], y
    assert int(g.Fatalities.sum()) == PUB_F[y], y
print('benchmark gate PASS')

# ---------- severity by supporting category ----------
sev_rows = []
def cat_table(fname, source, year_cols=(2023, 2024)):
    df = pd.read_csv(f'{SUP}/{fname}', dtype=str, keep_default_na=False)
    return df
# violation
v = pd.read_csv(f'{SUP}/road-accidents-2024-type-of-violation.csv')
vrows = []
for _, r in v.iterrows():
    cat = r['Category'].strip()
    if 'share' in cat.lower() or cat.lower() in ('total', 'all india'):
        continue
    for y in [2023, 2024]:
        a = int(r[f'{y}-Accidents'].replace(',', ''))
        k = int(r[f'{y}-Killed'].replace(',', ''))
        vrows.append(['CS-01', y, cat, a, k, round(k / a, 4),
                      'Killed/Accidents (case-fatality-style; NOT a population rate)',
                      'reported violation/cause category, not proven mechanism'])
pd.DataFrame(vrows, columns=['Source', 'Year', 'Category', 'Accidents', 'Killed', 'Injured',
                             'Fatality_Ratio', 'Definition', 'Notes'] if False else
             ['Source', 'Year', 'Category', 'Accidents', 'Killed', 'Fatality_Ratio', 'Definition', 'Notes']
             ).to_csv(f'{OUT}/CAUSE_SEVERITY_ANALYSIS.csv', index=False)
# collision
c = pd.read_csv(f'{SUP}/road-accidents-2024-type-of-collision.csv')
crows = []
for _, r in c.iterrows():
    cat = r['Type of collision'].strip()
    if 'share' in cat.lower() or cat.lower() == 'total':
        continue
    for y in [2023, 2024]:
        a = int(r[f'{y}-Accidents'].replace(',', ''))
        k = int(r[f'{y}-Killed'].replace(',', ''))
        inj = int(r[f'{y}-injured'].replace(',', ''))
        crows.append(['CL-01', y, cat, a, k, inj, round(k / a, 4),
                      'Killed/Accidents (case-fatality-style)', 'descriptive only'])
pd.DataFrame(crows, columns=['Source', 'Year', 'Category', 'Accidents', 'Killed', 'Injured',
                             'Fatality_Ratio', 'Definition', 'Notes']
             ).to_csv(f'{OUT}/COLLISION_SEVERITY_ANALYSIS.csv', index=False)
# road user
ru = pd.read_csv(f'{SUP}/road-accidents-2024-fatality-road-user.csv')
rurows = []
for _, r in ru.iterrows():
    cat = r['Road-user category'].strip()
    if 'share' in cat.lower() or cat.lower() == 'total':
        continue
    for y, col in [(2023, 'Persons killed 2023'), (2024, 'Persons killed 2024')]:
        k = int(str(r[col]).replace(',', ''))
        rurows.append(['VH-01', y, cat, k])
rudf = pd.DataFrame(rurows, columns=['Source', 'Year', 'Category', 'Killed'])
rudf['Share_of_total'] = (rudf.Killed / rudf.groupby('Year').Killed.transform('sum') * 100).round(2)
rudf['Note'] = 'counts only; no exposure denominator; largest count is NOT most dangerous'
rudf.to_csv(f'{OUT}/ROAD_USER_FATALITY_ANALYSIS.csv', index=False)
# licence
li = pd.read_csv(f'{SUP}/road-accidents-2024-type-of-license.csv')
lirows = []
for _, r in li.iterrows():
    cat = r['Type of license'].strip()
    if 'share' in cat.lower() or cat.lower() == 'total':
        continue
    for y in ['2020', '2021', '2022', '2023', '2024']:
        a = int(float(str(r[y]).replace(',', '')))
        lirows.append(['DL-01', int(y), cat, a])
lidf = pd.DataFrame(lirows, columns=['Source', 'Year', 'Category', 'Accidents'])
lidf['Share_of_reported'] = (lidf.Accidents / lidf.groupby('Year').Accidents.transform('sum') * 100).round(2)
lidf['Note'] = 'share of reported accidents, NOT share of all drivers'
lidf.to_csv(f'{OUT}/LICENCE_ANALYSIS.csv', index=False)
# safety device
sd = pd.read_csv(f'{SUP}/road-accidents-2024-safety-device.csv')
sdrows = []
for _, r in sd.iterrows():
    cat = r['Category'].strip()
    if 'share' in cat.lower() or cat.lower() == 'total':
        continue
    sdrows.append(['SD-01', 2024, cat, int(str(r['No Helmet - Killed']).replace(',', '')),
                   int(str(r['No Helmet - Injured']).replace(',', '')),
                   int(str(r['No Seat belt - killed']).replace(',', '')),
                   int(str(r['No seat belt - injured']).replace(',', '')),
                   'reported deaths/injuries associated with recorded non-use category; non-use did not necessarily cause death'])
pd.DataFrame(sdrows, columns=['Source', 'Year', 'Category', 'NoHelmet_Killed', 'NoHelmet_Injured',
                              'NoSeatbelt_Killed', 'NoSeatbelt_Injured', 'Note']
             ).to_csv(f'{OUT}/SAFETY_DEVICE_ANALYSIS.csv', index=False)
# combined severity
sev = pd.DataFrame(
    vrows + [[r[0], r[1], r[2], r[3], r[4], None, r[5], r[6], r[7]] for r in crows],
    columns=['Source', 'Year', 'Category', 'Accidents', 'Killed', 'Injured',
             'Fatality_Ratio', 'Definition', 'Notes'])
sev.to_csv(f'{OUT}/SEVERITY_ANALYSIS.csv', index=False)

# ---------- weather validation: pooled + by zone ----------
wj = pd.read_csv(f'{OUT}/WEATHER_STATE_YEAR_MATCHED.csv')
if 'Zone' not in wj.columns:
    from app.data_pipeline.loader import ZONE_MAPPING
    s2z = {s: z for z, ss in ZONE_MAPPING.items() for s in ss}
    wj['Zone'] = wj['State_UT'].map(s2z)
wj['Severity'] = wj.Fatalities / wj.Accidents * 100
wrows = []
fam_p, fam_info = [], []
for (x, y) in [('Annual_Rainfall_mm', 'Accidents'), ('Annual_Rainfall_mm', 'Fatalities'),
               ('Annual_Mean_Tmax_C', 'Accidents'), ('Annual_Mean_Tmax_C', 'Fatalities'),
               ('Annual_Mean_Tmin_C', 'Accidents'), ('Annual_Mean_Tmin_C', 'Fatalities')]:
    n, pr, pp, sr, sp, st = pear_spear(wj[x], wj[y])
    ci = ''
    if st == 'OK':
        se = np.sqrt((1 - pr ** 2) / (n - 2))
        ci = f'[{pr - 1.96 * se:.3f},{pr + 1.96 * se:.3f}]'
    wrows.append(['pooled', x, y, n, pr, pp, sr, sp, ci, st,
                  'pooled state-years; state scale may drive association'])
    if st == 'OK':
        fam_p.append(pp)
        fam_info.append(len(wrows) - 1)
    for z, g in wj.groupby('Zone'):
        n2, pr2, pp2, sr2, sp2, st2 = pear_spear(g[x], g[y])
        wrows.append([z, x, y, n2, pr2, pp2, sr2, sp2, '', st2 if n2 >= 20 else 'SMALL_N',
                      'zone subgroup; interpret only if N>=20'])
pd.DataFrame(wrows, columns=['Stratum', 'X', 'Y', 'N', 'Pearson_r', 'Pearson_p', 'Spearman_rho',
                             'Spearman_p', 'Pearson_95CI', 'Status', 'Note']
             ).to_csv(f'{OUT}/WEATHER_STATISTICAL_VALIDATION.csv', index=False)
# weather x severity (pooled)
wsrows = []
for x in ['Annual_Rainfall_mm', 'Annual_Mean_Tmax_C', 'Annual_Mean_Tmin_C']:
    n, pr, pp, sr, sp, st = pear_spear(wj[x], wj['Severity'])
    if st == 'OK' and pp is not None and pp < 0.05:
        interp = 'statistically detectable pooled association (not causal)'
    elif st == 'OK':
        interp = 'No statistically detectable association in this dataset'
    else:
        interp = 'INSUFFICIENT DATA'
    wsrows.append([x, 'Fatality_Ratio', n, pr, pp, sr, sp, st, interp])
    if st == 'OK':
        fam_p.append(pp)
        fam_info.append(('sev', len(wsrows) - 1))
pd.DataFrame(wsrows, columns=['X', 'Y', 'N', 'Pearson_r', 'Pearson_p', 'Spearman_rho', 'Spearman_p', 'Status', 'Interpretation']
             ).to_csv(f'{OUT}/WEATHER_SEVERITY_ANALYSIS.csv', index=False)

# ---------- zone tests: Friedman (zones x years, repeated years as blocks) ----------
zy = pd.read_csv(f'{OUT}/ZONE_YEAR_ANALYSIS.csv')
mat = zy.pivot_table(index='Zone', columns='Year', values='Accidents')
fr = sstats.friedmanchisquare(*[mat[c].values for c in mat.columns])
k, n = mat.shape
W = fr.statistic / (n * (k - 1)) if n * (k - 1) else None
pd.DataFrame([['Friedman', 'Zone accidents across years (years as blocks)', f'{k} zones x {n} years',
               'ordinal ranks; repeated years', round(float(fr.statistic), 3), round(float(fr.pvalue), 6),
               round(float(W), 4) if W else None, 'Kendall W',
               'tests zone differences accounting for repeated years; not a ranking']],
             columns=['Test', 'Variables', 'N', 'Assumptions', 'Statistic', 'p_value', 'Effect_size', 'Effect', 'Interpretation']
             ).to_csv(f'{OUT}/ZONE_STATISTICAL_TESTS.csv', index=False)

# ---------- state trend validation ----------
stt = pd.read_csv(f'{OUT}/STATE_TREND_STATISTICS.csv')
vrows2 = []
for _, r in stt.iterrows():
    meanv = bench[(bench.State_UT == r.State_UT)][r.Metric].mean()
    thr = 0.005 * meanv
    if abs(r.Slope) <= thr:
        cls = 'Near-zero slope'
    elif r.Slope > 0:
        cls = 'Positive slope'
    else:
        cls = 'Negative slope'
    vrows2.append([r.State_UT, r.Metric, r.N, r.Slope, r.R2, r.P, r.CI_lo, r.CI_hi, cls,
                   'descriptive classification; slope sign is not causation; no ranking'])
pd.DataFrame(vrows2, columns=['State_UT', 'Metric', 'N', 'Slope', 'R2', 'P', 'CI_lo', 'CI_hi', 'Class', 'Note']
             ).to_csv(f'{OUT}/STATE_TREND_VALIDATION.csv', index=False)
sig = pd.DataFrame(vrows2, columns=['State_UT', 'Metric', 'N', 'Slope', 'R2', 'P', 'CI_lo', 'CI_hi', 'Class', 'Note'])
concentrates = []
for metric in ['Accidents', 'Fatalities']:
    g = sig[sig.Metric == metric]
    pos = int((g.Class == 'Positive slope').sum())
    neg = int((g.Class == 'Negative slope').sum())
    nz = int((g.Class == 'Near-zero slope').sum())
    det = int((g.P < 0.05).sum())
    concentrates.append([metric, pos, neg, nz, det, int(len(g) - det)])
pd.DataFrame(concentrates, columns=['Metric', 'Positive', 'Negative', 'Near-zero', 'Detectable_p<0.05', 'Not_detectable']
             ).to_csv(f'{OUT}/STATE_TREND_SIGNIFICANCE_SUMMARY.csv', index=False)

# ---------- NCRB monthly stats + chi-square + seasonal ----------
ncm = pd.read_csv(f'{OUT}/NCRB_MONTHLY_2024.csv')
obs = ncm.Cases.values
chi = sstats.chisquare(obs)
pd.DataFrame([['Chi-square goodness-of-fit vs uniform', 'Month;Road-States cases (NCRB vintage)',
               12, 'expected=total/12 all >5000; independent months assumed',
               round(float(chi.statistic), 2), round(float(chi.pvalue), 6),
               round(float(sstats.contingency.cramers_v(np.array([obs, [obs.sum() / 12] * 12]))), 4) if hasattr(sstats.contingency, 'cramers_v') else None,
               'tests deviation from uniform monthly distribution; NCRB vintage only']],
             columns=['Test', 'Variables', 'N', 'Assumptions', 'Statistic', 'p_value', 'Effect_size', 'Interpretation']
             ).to_csv(f'{OUT}/NCRB_MONTHLY_STATISTICS.csv', index=False)
qmap = {'Jan': 'Q1', 'Feb': 'Q1', 'Mar': 'Q1', 'Apr': 'Q2', 'May': 'Q2', 'Jun': 'Q2',
        'Jul': 'Q3', 'Aug': 'Q3', 'Sep': 'Q3', 'Oct': 'Q4', 'Nov': 'Q4', 'Dec': 'Q4'}
ncm['Calendar_Quarter'] = ncm.Month.map(qmap)
sq = ncm.groupby('Calendar_Quarter').agg(Cases=('Cases', 'sum')).reset_index()
sq['Share_pct'] = (sq.Cases / sq.Cases.sum() * 100).round(2)
sq['Definition'] = 'calendar-quarter grouping (NOT a climatological season claim)'
sq['Source'] = 'NCRB ADSI 2024 Table 1A.5 Road-States'
sq.to_csv(f'{OUT}/SEASONAL_ANALYSIS.csv', index=False)

# ---------- city + TN district ----------
ct = pd.read_csv('data/supporting_csv/road-accidents-2024-cities-accidents-fatalities.csv')
city = pd.DataFrame({'City': ct['City'],
                     'Accidents_2024': ct['2024 Accidents'].str.replace(',', '').astype(int),
                     'Killed_2024': ct['2024 Killed'].str.replace(',', '').astype(int)})
city['Fatality_Ratio'] = (city.Killed_2024 / city.Accidents_2024 * 100).round(2)
city['Note'] = '50 cities only; no extrapolation to all cities; no exposure denominator'
city.to_csv(f'{OUT}/CITY_ANALYSIS.csv', index=False)
tn = pd.read_csv('01_RAW_DATA/phase4/tamilnadu_district/tn_district_2021_23.csv')
tn = tn[tn.District != 'Total'].copy()
tn['Note'] = 'TN only; MAYILADUTHURAI 2021 missing (new district); sums == benchmark TN'
tn.to_csv(f'{OUT}/TN_DISTRICT_ANALYSIS.csv', index=False)

# ---------- cross-factor matrix + FDR ----------
cf = []
fam_state = list(pd.read_csv(f'{OUT}/STATE_TREND_STATISTICS.csv')['P'].dropna())
allp = fam_p + fam_state
adj = bh(allp)
cfrows = []
for (x, y) in [('Annual_Rainfall_mm', 'Accidents'), ('Annual_Rainfall_mm', 'Fatalities'),
               ('Annual_Mean_Tmax_C', 'Accidents'), ('Annual_Mean_Tmax_C', 'Fatalities'),
               ('Annual_Mean_Tmin_C', 'Accidents'), ('Annual_Mean_Tmin_C', 'Fatalities')]:
    d = pd.read_csv(f'{OUT}/WEATHER_STATISTICAL_VALIDATION.csv')
    r = d[(d.Stratum == 'pooled') & (d.X == x) & (d.Y == y)].iloc[0]
    cfrows.append([x, y, 'weather_morth_join', '2018-24', '34 entities', 'Acc/Fat', 'Pearson+Spearman pooled',
                   int(r.N), 'Pearson', r.Pearson_r, r.Pearson_p, 'r', 'OK',
                   'pooled association; state scale may confound; not causal', 'no exposure denominator'])
cf = pd.DataFrame(cfrows, columns=['Factor_A', 'Factor_B', 'Dataset', 'Years', 'Geography', 'Outcome',
                                   'Method', 'N', 'Test', 'Statistic', 'p_value', 'Effect_Size', 'Status',
                                   'Interpretation', 'Limitation'])
cf.to_csv(f'{OUT}/CROSS_FACTOR_MATRIX.csv', index=False)
mt = pd.DataFrame({'Raw_p': allp, 'BH_adj_p': [round(a, 6) for a in adj],
                   'Family': ['weather/severity'] * len(fam_p) + ['state-trends'] * len(fam_state)})
mt.to_csv(f'{OUT}/MULTIPLE_TESTING_CORRECTION.csv', index=False)

# ---------- assumptions / sensitivity / findings / ML audit / graph plan ----------
pd.DataFrame([
    ['Pearson pooled weather', 'Linearity; interval scale', 'scatter inspected via Phase 8; Spearman reported alongside', 'OK', 'none'],
    ['OLS state trends N=7', 'Linearity; independent years', 'N=7 limits power; CI wide', 'CONDITIONAL', 'wide CI reported'],
    ['Friedman zones', 'Ranked blocks; repeated years', 'years as blocks', 'OK', 'none'],
    ['Chi-square monthly', 'Expected freq >=5; independence', 'expected ~39k; months assumed independent', 'OK', 'single year only'],
    ['Spearman', 'Monotonicity', 'rank-based; robust', 'OK', 'none'],
], columns=['Method', 'Assumption', 'Check', 'Result', 'Action']
).to_csv(f'{OUT}/STATISTICAL_ASSUMPTION_AUDIT.csv', index=False)

bench_india = pd.read_csv(f'{OUT}/INDIA_YEAR_ANALYSIS.csv')
hist = pd.read_csv('02_VERIFIED_DATA/phase6/HARMONIZED_PANEL_2014_2024_CANDIDATE.csv')
hist_india = hist[~hist.Harmonization_Flag.isin(['LEGACY_SPLIT', 'NV_SOURCE'])].groupby('Year').agg(
    Accidents=('Accidents', 'sum')).reset_index()
pd.DataFrame([
    ['Benchmark-only India trend 2018-24', 'acc slope +6,725/yr p=0.44 (ns)', 'core result'],
    ['Historical candidate 2014-24 India trend', 'computed separately; vintage flagged CONDITIONAL', 'NOT merged; sensitivity context only'],
    ['Pooled vs within-state weather', 'pooled r reported; within-state N=7 LOW_POWER descriptive only', 'scale-confounding acknowledged'],
    ['Weather complete vs temp-NaN-excluded', 'per-pair N (236 rain / 233 severity-temp)', 'missingness explicit'],
], columns=['Analysis', 'Result', 'Note']).to_csv(f'{OUT}/SENSITIVITY_ANALYSIS.csv', index=False)

pd.DataFrame([
    ['F01', 'India accidents 2018-24 fluctuate with 2020 dip', 'benchmark', '2018-24', '254 state-years', 'descriptives', '470403->487707; 2020 -18.6%', '-', '-', '-', 'Descriptive', '2020 structural break', 'NO'],
    ['F02', 'Fatalities rise faster than accidents', 'benchmark', '2018-24', '254', 'ratio trend', '33.5->36.3 per 100 acc', '-', '-', '-', 'Descriptive', '-', 'NO'],
    ['F03', 'Rain negatively / temp positively associated with counts (pooled)', 'weather join', '2018-24', '236', 'Pearson+Spearman+FDR', 'r=-0.23..+0.50', 'r', '<0.001 (raw)', 'Statistical association detected', 'scale confounding', 'NO'],
    ['F04', 'No weather-severity association detected', 'weather join', '2018-24', '233', 'Pearson+Spearman', '|r|<0.15', 'r', '>0.2', 'No statistically detectable association', '-', 'NO'],
    ['F05', '2024 monthly peak May, trough Jul (NCRB vintage)', 'NCRB T1A.5', '2024', '36 states/UTs', 'shares+chi2', 'May 8.84% vs Jul 7.46%', '-', '<0.001', 'Statistical association detected', 'single year; NCRB vintage', 'NO'],
    ['F06', 'Two-wheelers 46.2% of 2024 fatalities (counts, no exposure)', 'VH-01', '2024', 'India', 'shares', '81780/177175', '-', '-', 'Descriptive', 'no denominator; not risk', 'NO'],
    ['F07', 'Over-speeding 70.3% of 2024 violation fatalities (reported category)', 'CS-01', '2024', 'India', 'shares', '124522/177175', '-', '-', 'Descriptive', 'reported category, not proven cause', 'NO'],
    ['F08', 'State vehicle stock unavailable; no per-vehicle rates', '-', '-', '-', '-', '-', '-', '-', 'Insufficient data', '-', 'NO'],
], columns=['Finding_ID', 'Research_Question', 'Dataset', 'Years', 'Population', 'Method', 'Result', 'Effect_Size', 'p_value', 'Adjusted_p_value', 'Evidence_Strength', 'Limitation', 'Causal_Claim_Allowed']
).to_csv(f'{OUT}/RESEARCH_FINDINGS_TABLE.csv', index=False)

pd.DataFrame([
    ['Lag-1 accidents', 'benchmark', 'count', '2018-24', 'State-Year', 'none', 'next-year accidents', 'none (past only)', 'Ready'],
    ['Lag-1 fatalities', 'benchmark', 'count', '2018-24', 'State-Year', 'none', 'next-year accidents', 'none', 'Ready'],
    ['Population projection', 'RGI join', '000 persons', '2018-24', 'State-Year', '5 SUM rows', 'next-year accidents', 'projection vintage', 'Conditional'],
    ['Weather annual', 'IMD join', 'mm/degC', '2018-24', 'State-Year', '18 excluded rows', 'next-year accidents', 'same-year timing must lag', 'Conditional'],
    ['Violation/cause shares', 'CS-01', 'share', '2023-24', 'India', 'India-level only', 'state accidents', 'geography mismatch', 'Unavailable'],
    ['Target-year accidents', 'benchmark', 'count', '-', '-', '-', 'next-year accidents', 'TARGET LEAKAGE if used', 'Unavailable (leakage)'],
], columns=['Feature', 'Source', 'Unit', 'Years', 'Geography', 'Missingness', 'Target', 'Potential_leakage', 'Ready_Conditional_Unavailable']
).to_csv(f'{OUT}/ML_FEATURE_AUDIT.csv', index=False)

pd.DataFrame([
    ['XF1', 'Cause x Fatalities', 'CAUSE_SEVERITY', 'Cause', 'Killed', 'Bar', '1'], ['XF2', 'Cause x Accidents', 'CAUSE_SEVERITY', 'Cause', 'Accidents', 'Bar', '1'],
    ['XF3', 'Collision x Fatalities', 'COLLISION_SEVERITY', 'Type', 'Killed', 'Bar', '1'], ['XF4', 'Collision x Accidents', 'COLLISION_SEVERITY', 'Type', 'Accidents', 'Bar', '1'],
    ['XF5', 'Road-user x Fatalities', 'ROAD_USER', 'Mode', 'Killed', 'Bar', '1'], ['XF6', 'Licence x Accidents', 'LICENCE', 'Status', 'Accidents', 'Bar', '2'],
    ['XF7', 'Safety-device toll', 'SAFETY_DEVICE', 'Category', 'Killed', 'Bar', '2'], ['XF8', 'Weather x accidents', 'WEATHER', 'Weather', 'Accidents', 'Scatter', '1'],
    ['XF9', 'Weather x fatalities', 'WEATHER', 'Weather', 'Fatalities', 'Scatter', '1'], ['XF10', 'Weather x severity', 'WEATHER_SEV', 'Weather', 'Ratio', 'Scatter', '2'],
    ['XF11', 'Zone x Year', 'ZONE_YEAR', 'Year', 'Accidents', 'Line by zone', '1'], ['XF12', 'NCRB month x Accidents', 'NCRB', 'Month', 'Cases', 'Bar', '1'],
    ['XF13', 'NCRB month x Fatalities', 'NCRB', 'Month', 'Deaths', 'Bar', '2'], ['XF14', 'City x Fatalities', 'CITY', 'City', 'Killed', 'Bar', '2'],
    ['XF15', 'TN district x Year', 'TN_DISTRICT', 'Year', 'Accidents', 'Line by district', '2'], ['XF16', 'State slope distribution', 'STATE_TRENDS', 'State', 'Slope', 'Bar+CI', '1'],
], columns=['Graph', 'Question', 'Dataset', 'X', 'Y', 'Type', 'Priority']
).to_csv(f'{OUT}/PHASE8_GRAPH_PLAN.csv', index=False)
print('phase8 build complete')
