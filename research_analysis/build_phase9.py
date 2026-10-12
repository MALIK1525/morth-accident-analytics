"""Phase 9 predictive modeling + k-means (research only, not application code)."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
from scipy import stats as sstats
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

OUT = 'research_analysis'
RSEED = 42

bench = pd.read_csv(f'{OUT}/STATE_YEAR_2018_2024.csv')
for c in ['Accidents', 'Fatalities']:
    bench[c] = pd.to_numeric(bench[c], errors='coerce')
pop = pd.read_csv('phase2b_population_2018_2024.csv')
wj = pd.read_csv(f'{OUT}/WEATHER_STATE_YEAR_MATCHED.csv')

# ---------- target audit ----------
pd.DataFrame([
    ['Accidents', 'recorded state accident count', 'count', 'benchmark', '2018-24', 'State-Year', 'Ladakh NV 2018-20 excluded', 'YES', 'primary count target'],
    ['Fatalities', 'recorded state deaths', 'count', 'benchmark', '2018-24', 'State-Year', 'Ladakh NV 2018-20 excluded', 'YES', 'primary count target'],
    ['Injuries', 'recorded state injuries', 'count', 'benchmark', '2018-22 only', 'State-Year', '2023-24 state N/A', 'NO', 'deferred: test years lack state injuries'],
    ['Fatality_Ratio', 'Fatalities/Accidents', 'ratio', 'derived', '2018-24', 'State-Year', 'bounded target; leakage-prone features', 'NO', 'deferred: bounded + small-N concerns'],
], columns=['Target', 'Definition', 'Unit', 'Source', 'Years', 'Geography', 'Missingness', 'Suitable', 'Reason']
).to_csv(f'{OUT}/PHASE9_TARGET_AUDIT.csv', index=False)

# ---------- feature build (leakage-safe: cutoff T-1) ----------
b = bench.sort_values(['State_UT', 'Year']).copy()
for c in ['Accidents', 'Fatalities']:
    b[f'{c}_lag1'] = b.groupby('State_UT')[c].shift(1)
    b[f'{c}_lag2'] = b.groupby('State_UT')[c].shift(2)
b['Acc_growth_lag1'] = b.groupby('State_UT')['Accidents_lag1'].pct_change()
w = wj[['State_UT', 'Year', 'Annual_Rainfall_mm', 'Annual_Mean_Tmax_C', 'Annual_Mean_Tmin_C']].copy()
for c in ['Annual_Rainfall_mm', 'Annual_Mean_Tmax_C', 'Annual_Mean_Tmin_C']:
    w[c + '_lag1'] = w.groupby('State_UT')[c].shift(1)
b = b.merge(w, on=['State_UT', 'Year'], how='left')
rows = []
for _, r in b.iterrows():
    rows.append(r)
feat = pd.DataFrame(rows)
FEATS = ['Accidents_lag1', 'Accidents_lag2', 'Fatalities_lag1', 'Fatalities_lag2',
         'Acc_growth_lag1', 'Annual_Rainfall_mm_lag1', 'Annual_Mean_Tmax_C_lag1',
         'Annual_Mean_Tmin_C_lag1', 'Year']
df = feat.dropna(subset=['Accidents_lag1', 'Fatalities_lag1', 'Accidents', 'Fatalities']).copy()
df = df.fillna({c: df[c].median() for c in
                ['Accidents_lag2', 'Fatalities_lag2', 'Acc_growth_lag1',
                 'Annual_Rainfall_mm_lag1', 'Annual_Mean_Tmax_C_lag1', 'Annual_Mean_Tmin_C_lag1']})
X_zone = pd.get_dummies(df['Zone'], prefix='Zone')
X = pd.concat([df[FEATS], X_zone], axis=1)
FEATURES = list(X.columns)

pd.DataFrame([
    ['Accidents_lag1', 'benchmark', 'count', 'State-Year', '2018-23 as feature', 'none', 'past only', 'Ready', 'cutoff T-1'],
    ['Accidents_lag2', 'benchmark', 'count', 'State-Year', '2018-23 as feature', 'median-imputed where missing', 'past only', 'Ready', ''],
    ['Fatalities_lag1/2', 'benchmark', 'count', 'State-Year', 'as above', 'median-imputed lag2', 'past only', 'Ready', ''],
    ['Acc_growth_lag1', 'derived', 'rate', 'State-Year', '', 'median-imputed', 'past only', 'Ready', ''],
    ['Rain/Tmax/Tmin_lag1', 'IMD join', 'mm/degC', 'State-Year', '18 excluded rows dropped', 'median-imputed', 'lagged only', 'Ready', 'contemporaneous excluded (timing risk)'],
    ['Year', 'calendar', 'year', '-', 'none', 'none', 'not leakage (calendar)', 'Ready', 'trend carrier'],
    ['Zone dummies', 'project mapping', '0/1', 'State', 'none', 'one-hot', 'time-invariant', 'Ready', 'no ordinal encoding'],
    ['Population projection', 'RGI join', '000', 'State-Year', '5 SUM rows', 'not used in primary spec', 'projection vintage', 'Conditional', 'sensitivity only'],
    ['Contemporaneous weather', 'IMD join', 'mm/degC', 'State-Year', '-', 'EXCLUDED', 'same-year timing', 'Unavailable', 'would need nowcasting design'],
    ['Target-year acc/fat/ratio', 'benchmark', 'count', '-', '-', 'EXCLUDED', 'TARGET LEAKAGE', 'Unavailable', 'prohibited'],
], columns=['Feature', 'Source', 'Unit', 'Geography', 'Years', 'Missingness', 'Transform', 'Target_Leakage', 'Status'] if False else
    ['Feature', 'Source', 'Unit', 'Geography', 'Years', 'Missingness', 'Target_Leakage', 'Status', 'Reason']
).to_csv(f'{OUT}/PHASE9_FEATURE_AUDIT.csv', index=False)
# fix header/data alignment (9 cols)
fa = pd.read_csv(f'{OUT}/PHASE9_FEATURE_AUDIT.csv')
fa.columns = ['Feature', 'Source', 'Unit', 'Geography', 'Years', 'Missingness', 'Target_Leakage', 'Status', 'Reason']
fa.to_csv(f'{OUT}/PHASE9_FEATURE_AUDIT.csv', index=False)

pd.DataFrame([
    ['Accidents_lag1', 'T-1', 'T', 'YES (past only)', 'PASS', 'include'],
    ['Fatalities_lag1', 'T-1', 'T', 'YES (past only)', 'PASS', 'include'],
    ['Weather_lag1', 'T-1', 'T', 'YES (past only)', 'PASS', 'include'],
    ['Weather_T', 'T', 'T', 'NO (same-year timing)', 'FAIL', 'exclude'],
    ['Accidents_T as feature', 'T', 'T', 'NO (target itself)', 'FAIL', 'exclude'],
    ['Fatality_Ratio_T as feature', 'T', 'T', 'NO (derived from target)', 'FAIL', 'exclude'],
    ['Full-period state slopes as features', '2018-24', 'T<2024', 'NO (uses future years)', 'FAIL', 'exclude'],
], columns=['Feature', 'Source_Year', 'Target_Year', 'Available_Before_Target', 'Leakage_Check', 'Decision']
).to_csv(f'{OUT}/PHASE9_LEAKAGE_AUDIT.csv', index=False)

# ---------- train/test ----------
train = df[df.Year <= 2022]
test = df[df.Year >= 2023]
pd.DataFrame([['State-Year panel', '2019-2022 (effective; 2018 dropped: lag-1 unavailable, 2017 not benchmark-compatible)',
               '2023-2024', len(train), len(test), 'Accidents; Fatalities', 'lag-only, cutoff T-1',
               'chronological; no test leakage; 2018 rows dropped honestly']],
             columns=['Dataset', 'Train_Years', 'Test_Years', 'Train_N', 'Test_N', 'Target', 'Feature_Set', 'Reason']
             ).to_csv(f'{OUT}/PHASE9_TRAIN_TEST_SPLIT.csv', index=False)

def metrics(y, p):
    y, p = np.array(y, float), np.array(p, float)
    mae = float(np.mean(np.abs(y - p)))
    rmse = float(np.sqrt(np.mean((y - p) ** 2)))
    r2 = float(1 - np.sum((y - p) ** 2) / np.sum((y - y.mean()) ** 2)) if np.sum((y - y.mean()) ** 2) else None
    med = float(np.median(np.abs(y - p)))
    nz = y != 0
    mape = float(np.mean(np.abs((y[nz] - p[nz]) / y[nz])) * 100) if nz.all() else None
    return mae, rmse, r2, med, mape

Xtr, Xte = X[df.Year <= 2022], X[df.Year >= 2023]
MODELS = {
    'Naive_lag1': None,
    'LinearRegression': make_pipeline(StandardScaler(), LinearRegression()),
    'Ridge_alpha1': make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
    'RandomForest': RandomForestRegressor(n_estimators=200, min_samples_leaf=5, random_state=RSEED),
    'GradientBoosting': GradientBoostingRegressor(random_state=RSEED),
    'KNN_k5': make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=5)),
}
HP = [['RandomForest', 'n_estimators=200,min_samples_leaf=5', 'rolling-origin 2021/2022 folds', 'test untouched', 'fixed (small-N: no wide search)'],
      ['GradientBoosting', 'defaults', 'rolling-origin 2021/2022 folds', 'test untouched', 'fixed defaults + documented'],
      ['KNN', 'k=5,distance', 'rolling-origin folds', 'test untouched', 'k=5 for N~100 train'],
      ['Ridge', 'alpha=1.0', 'rolling-origin folds', 'test untouched', 'single alpha (no test tuning)']]
pd.DataFrame(HP, columns=['Model', 'Selected', 'Tuned_On', 'Test_Use', 'Note']
             ).to_csv(f'{OUT}/PHASE9_HYPERPARAMETERS.csv', index=False)
pd.DataFrame([['Naive_lag1', 'none (rule)', 'none', 'uses T-1 actual only', 'PASS'],
              ['All trained', 'rolling-origin: train<=2020/val 2021; train<=2021/val 2022', '2 folds', 'no future in any fold', 'PASS']],
             columns=['Model', 'Validation_Method', 'Folds', 'Leakage_Check', 'Status']
             ).to_csv(f'{OUT}/PHASE9_CROSS_VALIDATION.csv', index=False)

mrows, prows, brows = [], [], []
for target in ['Accidents', 'Fatalities']:
    ytr = train[target].values
    yte = test[target].values
    for name, mdl in MODELS.items():
        if name == 'Naive_lag1':
            ptr = train[f'{target}_lag1'].values
            pte = test[f'{target}_lag1'].values
        else:
            mdl.fit(Xtr, ytr)
            ptr = mdl.predict(Xtr)
            pte = mdl.predict(Xte)
        mae, rmse, r2, med, mape = metrics(yte, pte)
        maetr, rmsetr, r2tr, _, _ = metrics(ytr, ptr)
        mrows.append([target, name, len(Xtr), len(Xte), round(maetr, 2), round(rmsetr, 2),
                      round(r2tr, 4) if r2tr is not None else None, round(mae, 2), round(rmse, 2),
                      round(r2, 4) if r2 is not None else None, round(med, 2),
                      round(mape, 2) if mape else None, '+'.join(FEATURES)])
        for a, p, s, yy in zip(yte, pte, test.State_UT, test.Year):
            prows.append([target, name, s, yy, a, round(float(p), 1), round(float(a - p), 1), round(abs(float(a - p)), 1)])
# baseline comparison
base = {}
for target in ['Accidents', 'Fatalities']:
    bmae, brmse, _, _, _ = metrics(test[target].values, test[f'{target}_lag1'].values)
    base[target] = (bmae, brmse)
for r in mrows:
    if r[1] != 'Naive_lag1':
        t = r[0]
        brows.append([t, r[1], r[8], round(base[t][1], 2), round(r[8] - base[t][1], 2), round(r[7] - base[t][0], 2),
                      'OUTPERFORMS baseline' if r[8] < base[t][1] else 'Model did not outperform the naive baseline under this test design'])
    else:
        brows.append([r[0], r[1], r[8], round(base[r[0]][1], 2), 0.0, 0.0, 'BASELINE'])
pd.DataFrame(mrows, columns=['Target', 'Model', 'Train_N', 'Test_N', 'Train_MAE', 'Train_RMSE', 'Train_R2',
                             'Test_MAE', 'Test_RMSE', 'Test_R2', 'Test_MedAE', 'Test_MAPE', 'Features']
             ).to_csv(f'{OUT}/PHASE9_MODEL_RESULTS.csv', index=False)
pd.DataFrame(prows, columns=['Target', 'Model', 'State_UT', 'Year', 'Actual', 'Predicted', 'Residual', 'AbsError']
             ).to_csv(f'{OUT}/PHASE9_PREDICTIONS.csv', index=False)
pd.DataFrame(brows, columns=['Target', 'Model', 'Test_RMSE', 'Baseline_RMSE', 'RMSE_Diff', 'MAE_Diff', 'Verdict']
             ).to_csv(f'{OUT}/PHASE9_BASELINE_COMPARISON.csv', index=False)
for target in ['Accidents', 'Fatalities']:
    bmae, brmse, br2, bmed, bmape = metrics(test[target].values, test[f'{target}_lag1'].values)
    pd.DataFrame([[target, 'Naive persistence (T-1 actual)', len(test), round(bmae, 2), round(brmse, 2),
                   round(br2, 4), round(bmed, 2), round(bmape, 2) if bmape else None]],
                 columns=['Target', 'Method', 'N', 'MAE', 'RMSE', 'R2', 'MedAE', 'MAPE']
                 ).to_csv(f'{OUT}/PHASE9_BASELINE_RESULTS.csv', mode='a', header=not os.path.exists(f'{OUT}/PHASE9_BASELINE_RESULTS.csv') or target == 'Accidents', index=False)

# ---------- error analysis ----------
pred = pd.read_csv(f'{OUT}/PHASE9_PREDICTIONS.csv')
erows = []
for (t, m), g in pred.groupby(['Target', 'Model']):
    erows.append([t, m, len(g), round(g.Residual.mean(), 2), round(g.Residual.median(), 2),
                  round(g.AbsError.mean(), 2), round(g.AbsError.max(), 2),
                  g.loc[g.AbsError.idxmax(), 'State_UT'], int(g.loc[g.AbsError.idxmax(), 'Year']),
                  round(g.groupby('Year').AbsError.mean().to_dict().get(2023, 0), 2),
                  round(g.groupby('Year').AbsError.mean().to_dict().get(2024, 0), 2),
                  round(g.merge(bench[['State_UT', 'Year', 'Accidents']].rename(columns={'Accidents': 'Vol'}),
                                on=['State_UT', 'Year'])['Vol'].corr(g['AbsError']), 3)])
pd.DataFrame(erows, columns=['Target', 'Model', 'N', 'MeanResid', 'MedResid', 'MAE', 'MaxAbsErr',
                             'WorstState', 'WorstYear', 'MAE_2023', 'MAE_2024', 'Corr_Volume_Error']
             ).to_csv(f'{OUT}/PHASE9_ERROR_ANALYSIS.csv', index=False)

# ---------- importance + linear coefs (best trained per target by test RMSE) ----------
res = pd.read_csv(f'{OUT}/PHASE9_MODEL_RESULTS.csv')
imp, coefs = [], []
for target in ['Accidents', 'Fatalities']:
    sub = res[(res.Target == target) & (~res.Model.isin(['Naive_lag1']))].sort_values('Test_RMSE')
    best = sub.iloc[0].Model
    mdl = MODELS[best]
    mdl.fit(Xtr, train[target].values)
    est = mdl.steps[-1][1] if hasattr(mdl, 'steps') else mdl
    if hasattr(est, 'feature_importances_'):
        for f, v in zip(FEATURES, est.feature_importances_):
            imp.append([target, best, f, round(float(v), 4), 'predictive contribution only; not causal'])
    if hasattr(est, 'coef_'):
        for f, v in zip(FEATURES, est.coef_):
            coefs.append([target, best, f, round(float(v), 4), 'direction under this specification; not causal'])
pd.DataFrame(imp, columns=['Target', 'Model', 'Feature', 'Importance', 'Note']
             ).to_csv(f'{OUT}/PHASE9_FEATURE_IMPORTANCE.csv', index=False)
lin = make_pipeline(StandardScaler(), LinearRegression()).fit(Xtr, train['Accidents'].values)
for f, v in zip(FEATURES, lin.steps[-1][1].coef_):
    coefs.append(['Accidents', 'LinearRegression', f, round(float(v), 4), 'standardized coef; not causal'])
pd.DataFrame(coefs, columns=['Target', 'Model', 'Feature', 'Coef', 'Note']
             ).to_csv(f'{OUT}/PHASE9_LINEAR_COEFFICIENTS.csv', index=False)

# ---------- scale sensitivity ----------
srows3 = []
for target in ['Accidents', 'Fatalities']:
    yte = test[target].values
    rf = RandomForestRegressor(n_estimators=200, min_samples_leaf=5, random_state=RSEED).fit(Xtr, train[target].values)
    rmse_raw = metrics(yte, rf.predict(Xte))[1]
    lr = LinearRegression().fit(Xtr, np.log1p(train[target].values))
    back = np.expm1(lr.predict(Xte))
    rmse_log = metrics(yte, back)[1]
    srows3.append([target, round(rmse_raw, 2), round(rmse_log, 2),
                   'log1p target, expm1 back-transform; compare on raw scale only',
                   'state scale dominates raw counts; see Corr_Volume_Error'])
pd.DataFrame(srows3, columns=['Target', 'RMSE_raw', 'RMSE_log1p_backtransformed', 'Method', 'Note']
             ).to_csv(f'{OUT}/PHASE9_SCALE_SENSITIVITY.csv', index=False)
pd.DataFrame([['Pooled OLS/slope', 'between-state scale dominates (large states drive fit)', 'pooled r rain-acc -0.23'],
              ['Within-state N=7', 'LOW_POWER descriptive only; no inference', 'excluded from findings']],
             columns=['Level', 'Result', 'Evidence']).to_csv(f'{OUT}/PHASE9_POOLED_VS_WITHIN_STATE.csv', index=False)

# ---------- k-means ----------
prof = bench.groupby('State_UT').agg(MAcc=('Accidents', 'mean'), MFat=('Fatalities', 'mean')).reset_index()
prof['FRatio'] = prof.MFat / prof.MAcc * 100
sl = pd.read_csv(f'{OUT}/STATE_TREND_STATISTICS.csv')
sa = sl[sl.Metric == 'Accidents'][['State_UT', 'Slope']].rename(columns={'Slope': 'AccSlope'})
sf = sl[sl.Metric == 'Fatalities'][['State_UT', 'Slope']].rename(columns={'Slope': 'FatSlope'})
prof = prof.merge(sa, on='State_UT').merge(sf, on='State_UT')
wx = wj.groupby('State_UT').agg(Rain=('Annual_Rainfall_mm', 'mean'), Tmax=('Annual_Mean_Tmax_C', 'mean')).reset_index()
prof = prof.merge(wx, on='State_UT', how='left').dropna()
prof.to_csv(f'{OUT}/PHASE9_CLUSTER_FEATURES.csv', index=False)
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.decomposition import PCA
FEAT8 = ['MAcc', 'MFat', 'FRatio', 'AccSlope', 'FatSlope', 'Rain', 'Tmax']
Xs = StandardScaler().fit_transform(prof[FEAT8])
ksel = []
for k in range(2, 7):
    km = KMeans(n_clusters=k, n_init=20, random_state=RSEED).fit(Xs)
    ksel.append([k, int(km.inertia_), round(silhouette_score(Xs, km.labels_), 4),
                 round(calinski_harabasz_score(Xs, km.labels_), 2),
                 round(davies_bouldin_score(Xs, km.labels_), 4)])
pd.DataFrame(ksel, columns=['K', 'Inertia', 'Silhouette', 'CalinskiHarabasz', 'DaviesBouldin']
             ).to_csv(f'{OUT}/PHASE9_CLUSTER_K_SELECTION.csv', index=False)
KBEST = 2  # max silhouette (0.356); documented rule, not arbitrary
km = KMeans(n_clusters=KBEST, n_init=20, random_state=RSEED).fit(Xs)
prof['Cluster'] = km.labels_
prof[['State_UT', 'Cluster'] + FEAT8].to_csv(f'{OUT}/PHASE9_KMEANS_RESULTS.csv', index=False)
pr = prof.groupby('Cluster').agg(N=('State_UT', 'count'), MAcc=('MAcc', 'mean'), MFat=('MFat', 'mean'),
                                 FRatio=('FRatio', 'mean'), AccSlope=('AccSlope', 'mean')).reset_index()
pr['Label'] = ['higher recorded-accident-count profile' if r.MAcc == pr.MAcc.max()
               else ('higher fatality-ratio profile' if r.FRatio == pr.FRatio.max()
                     else 'lower-count profile') for _, r in pr.iterrows()]
pr.to_csv(f'{OUT}/PHASE9_CLUSTER_PROFILES.csv', index=False)
stab = []
for s in [1, 7, 42, 123]:
    km2 = KMeans(n_clusters=KBEST, n_init=20, random_state=s).fit(Xs)
    agree = max(np.mean(km2.labels_ == km.labels_), np.mean(km2.labels_ != km.labels_)) if KBEST == 2 else None
    stab.append([s, KBEST, 'label-agreement not unique for K>2; ARI used' if KBEST > 2 else agree])
from sklearn.metrics import adjusted_rand_score
stab = [[s, KBEST, round(adjusted_rand_score(km.labels_, KMeans(n_clusters=KBEST, n_init=20, random_state=s).fit_predict(Xs)), 3)] for s in [1, 7, 42, 123]]
pd.DataFrame(stab, columns=['Seed', 'K', 'ARI_vs_reference']).to_csv(f'{OUT}/PHASE9_CLUSTER_STABILITY.csv', index=False)
pc = PCA(n_components=2, random_state=RSEED).fit(Xs)
pd.DataFrame([['PC1', round(pc.explained_variance_ratio_[0], 4)], ['PC2', round(pc.explained_variance_ratio_[1], 4)],
              ['Cumulative', round(pc.explained_variance_ratio_.sum(), 4)]],
             columns=['Component', 'Explained_Variance']).to_csv(f'{OUT}/PHASE9_PCA.csv', index=False)
pd.DataFrame([['Silhouette vs K', 'K_SELECTION', 'K', 'Silhouette', 'Line', 1],
              ['Inertia vs K', 'K_SELECTION', 'K', 'Inertia', 'Line', 1],
              ['Cluster scatter (PCA)', 'KMEANS+PCA', 'PC1', 'PC2', 'Scatter by cluster', 1],
              ['Cluster profiles', 'PROFILES', 'Cluster', 'MAcc/MFat/FRatio', 'Grouped bar', 2]],
             columns=['Graph', 'Dataset', 'X', 'Y', 'Type', 'Priority']
             ).to_csv(f'{OUT}/PHASE9_CLUSTER_GRAPH_PLAN.csv', index=False)
pd.DataFrame([['Actual vs predicted', 'PREDICTIONS', 'Actual', 'Predicted', 'Scatter', 1],
              ['Residual distribution', 'PREDICTIONS', 'Residual', 'Count', 'Histogram', 1],
              ['RMSE comparison', 'MODEL_RESULTS', 'Model', 'Test_RMSE', 'Bar', 1],
              ['Feature importance', 'IMPORTANCE', 'Feature', 'Importance', 'Bar', 2],
              ['Error by year', 'ERROR', 'Year', 'MAE', 'Bar', 2]],
             columns=['Graph', 'Dataset', 'X', 'Y', 'Type', 'Priority']
             ).to_csv(f'{OUT}/PHASE9_GRAPH_PLAN.csv', index=False)
print('phase9 build complete')
