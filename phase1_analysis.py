"""Phase-1 research analysis: verified MoRTH 2018-2024 panel only. No synthesis."""
import sys, os, glob
sys.path.insert(0, '.')
import numpy as np
import pandas as pd
from scipy import stats
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from app.data_pipeline.loader import DatasetLoader, OFFICIAL_INDIA_BENCHMARKS, STATE_TO_ZONE

OUT = 'RESEARCH_ANALYSIS_PHASE_1_WORKBOOK.xlsx'
loader = DatasetLoader(benchmark_path='data/MoRTH_Primary_Dataset_3.xlsx')
df = loader.get_clean_df().copy()
df['Acc_n'] = pd.to_numeric(df['Accidents'], errors='coerce')
df['Fat_n'] = pd.to_numeric(df['Fatalities'], errors='coerce')
df['Inj_n'] = pd.to_numeric(df['Injured'], errors='coerce')

R = {}  # results stash for report writing
import json
def reg(years, vals):
    x = np.array(years, dtype=float); y = np.array(vals, dtype=float)
    m = np.isfinite(y)
    x, y = x[m], y[m]
    n = len(x)
    if n < 3:
        return dict(N=n, slope=None, intercept=None, r2=None, p=None, ci=None, flag='INSUFFICIENT_N')
    s = stats.linregress(x, y)
    # 95% CI for slope
    ci = None
    if n > 3:
        t = stats.t.ppf(0.975, n - 2)
        ci = (round(s.slope - t * s.stderr, 2), round(s.slope + t * s.stderr, 2))
    flat = 'INSUFFICIENT_N' if n < 3 else ('APPROX_STABLE' if abs(s.slope) < 2 * (s.stderr or 0) else ('INCREASING' if s.slope > 0 else 'DECREASING'))
    return dict(N=n, slope=round(float(s.slope), 2), intercept=round(float(s.intercept), 2),
                r2=round(float(s.rvalue ** 2), 4), p=round(float(s.pvalue), 5),
                stderr=round(float(s.stderr), 2) if s.stderr else None, ci=ci, flag=flat)

# ---------- 1. audit ----------
states = sorted(df['State_UT'].unique().tolist())
years = sorted(df['Year'].unique().tolist())
audit = {
    'entities': int(df['State_UT'].nunique()), 'obs': int(len(df)), 'years': years,
    'null_acc': int(df['Acc_n'].isna().sum()), 'null_fat': int(df['Fat_n'].isna().sum()),
    'null_inj': int(df['Inj_n'].isna().sum()),
    'dupes': int(df.duplicated(subset=['State_UT', 'Year']).sum()),
    'unmapped': [s for s in states if s.strip().lower() not in STATE_TO_ZONE],
}
R['audit'] = audit
R['states'] = states
india = df.groupby('Year').agg(acc=('Acc_n', 'sum'), fat=('Fat_n', 'sum'), inj=('Inj_n', 'sum')).sort_index()
R['india'] = india
# reconciliation
rec = {}
for y in years:
    b = OFFICIAL_INDIA_BENCHMARKS[y]
    rec[y] = dict(acc_c=int(india.loc[y, 'acc']), acc_p=b['Accidents'],
                  fat_c=int(india.loc[y, 'fat']), fat_p=b['Fatalities'],
                  inj_p=b.get('Injured'))
R['rec'] = rec
inj_cov = df.groupby('Year')['Inj_n'].apply(lambda s: int(s.notna().sum())).to_dict()
R['inj_cov'] = inj_cov

# ---------- 2-7. India annual ----------
ind = pd.DataFrame({'Year': years})
ind['Accidents'] = [rec[y]['acc_c'] for y in years]
ind['Fatalities'] = [rec[y]['fat_c'] for y in years]
ind['Injured'] = [rec[y]['inj_p'] for y in years]
ind['Fat_per_100'] = (ind['Fatalities'] / ind['Accidents'] * 100).round(2)
for c, yn in [('Accidents', 'YoY_Acc_pct'), ('Fatalities', 'YoY_Fat_pct'), ('Injured', 'YoY_Inj_pct')]:
    ind[yn] = (ind[c].pct_change() * 100).round(2)
R['india_table'] = ind
R['reg_acc'] = reg(ind['Year'], ind['Accidents'])
R['reg_fat'] = reg(ind['Year'], ind['Fatalities'])
R['reg_inj'] = reg(ind['Year'], ind['Injured'])
R['reg_acc_post'] = reg([2021, 2022, 2023, 2024], ind[ind['Year'] >= 2021]['Accidents'])
R['reg_fat_post'] = reg([2021, 2022, 2023, 2024], ind[ind['Year'] >= 2021]['Fatalities'])

# ---------- 8. zones ----------
from app.data_pipeline.loader import get_zone_for_state
df['Zone'] = df['State_UT'].apply(get_zone_for_state)
zone_ann = df.groupby(['Zone', 'Year']).agg(acc=('Acc_n', 'sum'), fat=('Fat_n', 'sum')).reset_index()
zone_ann['share_acc'] = zone_ann.apply(lambda r: round(r['acc'] / rec[r['Year']]['acc_c'] * 100, 2), axis=1)
zone_ann['share_fat'] = zone_ann.apply(lambda r: round(r['fat'] / rec[r['Year']]['fat_c'] * 100, 2), axis=1)
zone_ann['fat_per_100'] = (zone_ann['fat'] / zone_ann['acc'] * 100).round(2)
R['zone_ann'] = zone_ann
zreg = []
for z, g in zone_ann.groupby('Zone'):
    ra, rf = reg(g['Year'], g['acc']), reg(g['Year'], g['fat'])
    zreg.append(dict(Zone=z, acc_slope=ra['slope'], acc_r2=ra['r2'], acc_p=ra['p'],
                     fat_slope=rf['slope'], fat_r2=rf['r2'], fat_p=rf['p'], N=ra['N'], flag=ra['flag']))
R['zone_reg'] = pd.DataFrame(zreg)

# ---------- 9/11. states ----------
srows, srows_f = [], []
for st, g in df.groupby('State_UT'):
    g = g.sort_values('Year')
    ra = reg(g['Year'], g['Acc_n'])
    rf = reg(g['Year'], g['Fat_n'])
    a18 = g[g['Year'] == 2018]['Acc_n'].values
    a24 = g[g['Year'] == 2024]['Acc_n'].values
    if len(a18) and len(a24) and pd.notnull(a18[0]) and pd.notnull(a24[0]) and a18[0] != 0:
        abs_c, pct_c = int(a24[0] - a18[0]), round((a24[0] - a18[0]) / a18[0] * 100, 2)
    else:
        abs_c, pct_c = None, None
    z = get_zone_for_state(st)
    srows.append(dict(State_UT=st, Zone=z, N=ra['N'], slope_acc=ra['slope'], r2_acc=ra['r2'],
                      p_acc=ra['p'], ci_acc=str(ra['ci']), flag_acc=ra['flag'],
                      acc_2018=int(a18[0]) if len(a18) and pd.notnull(a18[0]) else None,
                      acc_2024=int(a24[0]) if len(a24) and pd.notnull(a24[0]) else None,
                      abs_change=abs_c, pct_change=pct_c))
    srows_f.append(dict(State_UT=st, Zone=z, N=rf['N'], slope_fat=rf['slope'], r2_fat=rf['r2'],
                        p_fat=rf['p'], ci_fat=str(rf['ci']), flag_fat=rf['flag']))
R['state_reg'] = pd.DataFrame(srows)
R['state_reg_f'] = pd.DataFrame(srows_f)

# ---------- 10. same-value/threshold pairs ----------
thresh_rows = []
for th in [10000, 25000, 50000]:
    first = {}
    for st, g in df.groupby('State_UT'):
        hit = g[g['Acc_n'] >= th].sort_values('Year')
        if len(hit):
            first[st] = (int(hit.iloc[0]['Year']), int(hit.iloc[0]['Acc_n']))
    sts = sorted(first)
    for i in range(len(sts)):
        for j in range(i + 1, len(sts)):
            a, b = sts[i], sts[j]
            (ya, va), (yb, vb) = first[a], first[b]
            if ya != yb:
                thresh_rows.append(dict(Threshold=th, State_A=a, Year_A=ya, Value_A=va,
                                        State_B=b, Year_B=yb, Value_B=vb, Year_gap=abs(ya - yb),
                                        Note=f"{a} reached {th:,}+ in {ya}; {b} in {yb} (gap {abs(ya-yb)}y)"))
R['threshold_pairs'] = pd.DataFrame(thresh_rows)
R['thresholds'] = [10000, 25000, 50000]

# ---------- 14. correlation ----------
num = df[['Acc_n', 'Fat_n', 'Inj_n']].dropna()
R['corr_n'] = len(num)
R['pearson'] = num.corr('pearson').round(3).to_dict()
R['spearman'] = num.corr('spearman').round(3).to_dict()
R['pearson_p'] = {'acc_fat': round(float(stats.pearsonr(num['Acc_n'], num['Fat_n'])[1]), 6),
                  'acc_inj': round(float(stats.pearsonr(num['Acc_n'], num['Inj_n'])[1]), 6)}

# ---------- 15. exposure ----------
exp_files = glob.glob('data/supporting_csv/*.csv') + glob.glob('data/*exposure*') + glob.glob('data/*registr*')
R['exposure_files'] = exp_files

# ---------- ML readiness ----------
mlr = []
if os.path.exists('data/PARAMETER_FINAL_STATUS.csv'):
    p = pd.read_csv('data/PARAMETER_FINAL_STATUS.csv', dtype=str, keep_default_na=False)
    for _, r in p.iterrows():
        fs = r.get('Final_Status_for_Analysis', '')
        mlr.append(dict(Parameter=r.get('Parameter', ''), Final_Status=fs,
                        ML_Suitable='YES' if fs == 'READY_FOR_ANALYSIS' else 'NO'))
R['ml_readiness'] = pd.DataFrame(mlr)

json.dump({k: (v.to_dict() if isinstance(v, pd.DataFrame) else v) for k, v in R.items()
           if k in ('audit', 'inj_cov')}, open('phase1_results.json', 'w'), default=str)
R['india_table'].to_csv('phase1_india.csv', index=False)
R['zone_ann'].to_csv('phase1_zone.csv', index=False)
R['state_reg'].to_csv('phase1_state.csv', index=False)
print('AUDIT:', audit)
print('unmapped zones:', audit['unmapped'])
print('inj coverage:', inj_cov)
print('exposure files:', exp_files)
print('corr n:', R['corr_n'])
print('threshold pairs:', len(thresh_rows))
print('INDIA REG acc:', R['reg_acc'])
print('INDIA REG fat:', R['reg_fat'])
print('INDIA REG inj:', R['reg_inj'])
print('POST20 acc:', R['reg_acc_post'], 'fat:', R['reg_fat_post'])
print('ZONE REG:'); print(R['zone_reg'].to_string())
