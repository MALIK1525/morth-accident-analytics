"""Phase 11 numerical audit: verify every key number from its source file."""
import pandas as pd

checks = []
def chk(name, got, exp):
    ok = abs(float(got) - float(exp)) < 0.01 * max(1, abs(float(exp))) * 0.001 + 1e-9 if isinstance(exp, float) else str(got) == str(exp)
    checks.append([name, got, exp, 'PASS' if ok else 'FAIL'])

iy = pd.read_csv('research_analysis/INDIA_YEAR_ANALYSIS.csv').set_index('Year')
expA = {2018: 470403, 2019: 456959, 2020: 372181, 2021: 412432, 2022: 461312, 2023: 480583, 2024: 487707}
expF = {2018: 157593, 2019: 158984, 2020: 138383, 2021: 153972, 2022: 168491, 2023: 172890, 2024: 177175}
for y in expA:
    chk(f'{y} accidents', int(iy.loc[y, 'Accidents']), expA[y])
    chk(f'{y} fatalities', int(iy.loc[y, 'Fatalities']), expF[y])
chk('fatality ratio 2018', round(float(iy.loc[2018, 'Fatalities_per_100_Accidents']), 2), 33.50)
chk('fatality ratio 2024', round(float(iy.loc[2024, 'Fatalities_per_100_Accidents']), 2), 36.33)

wa = pd.read_csv('research_analysis/WEATHER_ASSOCIATIONS.csv').set_index(['X', 'Y'])
chk('rain-acc r', round(float(wa.loc[('Annual_Rainfall_mm', 'Accidents'), 'Pearson_r']), 3), -0.234)
chk('rain-fat r', round(float(wa.loc[('Annual_Rainfall_mm', 'Fatalities'), 'Pearson_r']), 3), -0.376)
chk('tmax-acc r', round(float(wa.loc[('Annual_Mean_Tmax_C', 'Accidents'), 'Pearson_r']), 3), 0.452)
chk('tmax-fat r', round(float(wa.loc[('Annual_Mean_Tmax_C', 'Fatalities'), 'Pearson_r']), 3), 0.498)
chk('tmin-acc r', round(float(wa.loc[('Annual_Mean_Tmin_C', 'Accidents'), 'Pearson_r']), 3), 0.366)
chk('tmin-fat r', round(float(wa.loc[('Annual_Mean_Tmin_C', 'Fatalities'), 'Pearson_r']), 3), 0.340)

zt = pd.read_csv('research_analysis/ZONE_STATISTICAL_TESTS.csv').iloc[0]
chk('friedman chi2', round(float(zt.Statistic), 2), 25.29)
chk('kendall W', round(float(zt.Effect_size), 2), 0.72)

nc = pd.read_csv('research_analysis/NCRB_MONTHLY_2024.csv').set_index('Month')
chk('NCRB May share', float(nc.loc['May', 'Share_pct']), 8.84)
chk('NCRB Jul share', float(nc.loc['Jul', 'Share_pct']), 7.46)

mr = pd.read_csv('research_analysis/PHASE9_MODEL_RESULTS.csv')
chk('acc baseline RMSE', float(mr[(mr.Target == 'Accidents') & (mr.Model == 'Naive_lag1')].iloc[0].Test_RMSE), 1038.6)
chk('fat baseline RMSE', float(mr[(mr.Target == 'Fatalities') & (mr.Model == 'Naive_lag1')].iloc[0].Test_RMSE), 286.31)
chk('test period', sorted(mr.Test_N.unique().tolist()), [72])

ks = pd.read_csv('research_analysis/PHASE9_CLUSTER_K_SELECTION.csv')
chk('K=2 silhouette', round(float(ks[ks.K == 2].iloc[0].Silhouette), 3), 0.356)

nfail = sum(1 for c in checks if c[3] == 'FAIL')
pd.DataFrame(checks, columns=['Check', 'Got', 'Expected', 'Status']).to_csv(
    'research_analysis/PHASE11_NUMCHECK.csv', index=False)
print(f'{len(checks) - nfail}/{len(checks)} PASS')
assert nfail == 0, 'NUMERICAL DISCREPANCY FOUND'
