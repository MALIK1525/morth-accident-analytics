"""Phase 12 figure generation (all from verified CSVs; Agg backend)."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

O = 'research_analysis'
F = 'FINAL_SUBMISSION_PACKAGE/FIGURES'
os.makedirs(F, exist_ok=True)
plt.rcParams.update({'figure.dpi': 150, 'font.size': 9})

iy = pd.read_csv(f'{O}/INDIA_YEAR_ANALYSIS.csv')
zy = pd.read_csv(f'{O}/ZONE_YEAR_ANALYSIS.csv')
st = pd.read_csv(f'{O}/STATE_YEAR_2018_2024.csv')
wa = pd.read_csv(f'{O}/WEATHER_ASSOCIATIONS.csv')
wj = pd.read_csv(f'{O}/WEATHER_STATE_YEAR_MATCHED.csv')
ncm = pd.read_csv(f'{O}/NCRB_MONTHLY_2024.csv')
mr = pd.read_csv(f'{O}/PHASE9_MODEL_RESULTS.csv')
pr = pd.read_csv(f'{O}/PHASE9_PREDICTIONS.csv')
ks = pd.read_csv(f'{O}/PHASE9_CLUSTER_K_SELECTION.csv')
km = pd.read_csv(f'{O}/PHASE9_KMEANS_RESULTS.csv')

def save(fig, name):
    fig.tight_layout()
    fig.savefig(f'{F}/{name}.png')
    plt.close(fig)
    print(name, 'ok')

fig, ax = plt.subplots()
ax.plot(iy.Year, iy.Accidents, marker='o')
ax.set_title('F01 India road accidents 2018-2024 (MoRTH benchmark)')
ax.set_xlabel('Year'); ax.set_ylabel('Accidents')
save(fig, 'F01')

fig, ax = plt.subplots()
ax.plot(iy.Year, iy.Fatalities, marker='o', color='crimson')
ax.set_title('F02 India road fatalities 2018-2024 (MoRTH benchmark)')
ax.set_xlabel('Year'); ax.set_ylabel('Fatalities')
save(fig, 'F02')

fig, ax = plt.subplots()
ax.plot(iy.Year, iy.Fatalities_per_100_Accidents, marker='o', color='darkorange')
ax.set_title('F03 Fatality ratio 33.50 to 36.33 per 100 accidents')
ax.set_xlabel('Year'); ax.set_ylabel('Deaths / 100 accidents')
save(fig, 'F03')

fig, ax = plt.subplots(figsize=(8, 4))
for z, g in zy.groupby('Zone'):
    ax.plot(g.Year, g.Accidents, marker='o', label=z)
ax.set_title('F04 Zone accident trends (descriptive; no ranking)')
ax.set_xlabel('Year'); ax.set_ylabel('Accidents'); ax.legend(fontsize=7)
save(fig, 'F04')

fig, ax = plt.subplots(figsize=(9, 6))
piv = st.pivot_table(index='State_UT', columns='Year', values='Accidents')
im = ax.imshow(piv.values, aspect='auto', cmap='YlOrRd')
ax.set_title('F05 State-year accident heatmap (missing = blank)')
ax.set_xticks(range(len(piv.columns)), piv.columns)
ax.set_yticks(range(len(piv.index)), piv.index, fontsize=6)
fig.colorbar(im, ax=ax, label='Accidents')
save(fig, 'F05')

sl = pd.read_csv(f'{O}/STATE_TREND_STATISTICS.csv')
sa = sl[sl.Metric == 'Accidents'].sort_values('Slope')
fig, ax = plt.subplots(figsize=(8, 7))
ax.barh(sa.State_UT, sa.Slope, xerr=[sa.Slope - sa.CI_lo, sa.CI_hi - sa.Slope],
        capsize=2)
ax.set_title('F06 State accident slopes with 95% CI (OLS N=7; mostly non-detectable)')
ax.set_xlabel('Slope (accidents/year)')
save(fig, 'F06')

for i, (x, t) in enumerate([('Annual_Rainfall_mm', 'F07 Rainfall vs accidents (r=-0.234 pooled)'),
                            ('Annual_Mean_Tmax_C', 'F08 Tmax vs fatalities (r=+0.498 pooled)')]):
    y = 'Accidents' if 'accidents' in t else 'Fatalities'
    d = wj[[x, y]].dropna()
    fig, ax = plt.subplots()
    ax.scatter(d[x], d[y], s=8, alpha=0.6)
    ax.set_title(t + ' (N=236; associational only)')
    ax.set_xlabel(x); ax.set_ylabel(y)
    save(fig, t.split()[0])

cs = pd.read_csv(f'{O}/CAUSE_SEVERITY_ANALYSIS.csv')
c24 = cs[cs.Year == 2024].sort_values('Killed')
fig, ax = plt.subplots()
ax.barh(c24.Category, c24.Killed)
ax.set_title('F09 2024 fatalities by reported violation category (reported share, not cause)')
ax.set_xlabel('Killed')
save(fig, 'F09')

cl = pd.read_csv(f'{O}/COLLISION_SEVERITY_ANALYSIS.csv')
cl24 = cl[cl.Year == 2024].sort_values('Accidents')
fig, ax = plt.subplots()
ax.barh(cl24.Category, cl24.Accidents)
ax.set_title('F10 2024 accidents by collision type (India-level)')
ax.set_xlabel('Accidents')
save(fig, 'F10')

ru = pd.read_csv(f'{O}/ROAD_USER_FATALITY_ANALYSIS.csv')
ru24 = ru[ru.Year == 2024].sort_values('Killed')
fig, ax = plt.subplots()
ax.barh(ru24.Category, ru24.Killed)
ax.set_title('F11 2024 fatalities by road-user mode (counts, not risk)')
ax.set_xlabel('Killed')
save(fig, 'F11')

li = pd.read_csv(f'{O}/LICENCE_ANALYSIS.csv')
li24 = li[li.Year == 2024]
fig, ax = plt.subplots()
ax.bar(li24.Category, li24.Accidents)
ax.set_title('F12 2024 accidents by licence status (share of reported accidents)')
ax.set_ylabel('Accidents')
plt.setp(ax.get_xticklabels(), rotation=15, ha='right', fontsize=7)
save(fig, 'F12')

fig, ax = plt.subplots()
ax.bar(ncm.Month, ncm.Cases, color='steelblue')
ax.set_title('F13 NCRB 2024 monthly road accidents (NCRB vintage, NOT MoRTH)')
ax.set_ylabel('Cases')
save(fig, 'F13')

tn = pd.read_csv(f'{O}/TN_DISTRICT_ANALYSIS.csv')
tn = tn[tn.District != 'Total'].copy() if 'District' in tn.columns else tn
fig, ax = plt.subplots(figsize=(8, 5))
top = tn.nlargest(10, 'Total Accidents 2023') if 'Total Accidents 2023' in tn.columns else tn.head(10)
ax.barh(top.iloc[:, 1] if top.shape[1] > 1 else top.index, top.iloc[:, 2] if top.shape[1] > 2 else 0)
ax.set_title('F14 TN top districts 2023 accidents (TN-only evidence)')
save(fig, 'F14')

pa = pr[(pr.Target == 'Accidents') & (pr.Model == 'GradientBoosting')]
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].scatter(pa.Actual, pa.Predicted, s=10, alpha=0.6)
axes[0].plot([pa.Actual.min(), pa.Actual.max()], [pa.Actual.min(), pa.Actual.max()], 'r--')
axes[0].set_title('F15a Actual vs predicted (GBR, test)')
axes[0].set_xlabel('Actual'); axes[0].set_ylabel('Predicted')
m = mr[mr.Target == 'Accidents'].sort_values('Test_RMSE')
axes[1].bar(m.Model, m.Test_RMSE)
axes[1].set_title('F15b Test RMSE by model (naive wins)')
plt.setp(axes[1].get_xticklabels(), rotation=20, ha='right', fontsize=7)
save(fig, 'F15')

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].plot(ks.K, ks.Silhouette, marker='o')
axes[0].set_title('F16a Silhouette vs K (K=2 selected)')
axes[0].set_xlabel('K'); axes[0].set_ylabel('Silhouette')
axes[1].scatter(km.MAcc, km.MFat, c=km.Cluster, cmap='tab10', s=20)
axes[1].set_xscale('log'); axes[1].set_yscale('log')
axes[1].set_title('F16b State clusters (K=2, descriptive)')
axes[1].set_xlabel('Mean accidents'); axes[1].set_ylabel('Mean fatalities')
save(fig, 'F16')
print('all figures done')
