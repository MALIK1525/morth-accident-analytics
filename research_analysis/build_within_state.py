"""Within-state weather addendum (N=7 per state: descriptive only, not for inference)."""
import os
import pandas as pd
from scipy import stats as sstats

wj = pd.read_csv('research_analysis/WEATHER_STATE_YEAR_MATCHED.csv')
rows = []
for st, g in wj.groupby('State_UT'):
    for x, y in [('Annual_Rainfall_mm', 'Accidents'), ('Annual_Rainfall_mm', 'Fatalities'),
                 ('Annual_Mean_Tmax_C', 'Accidents'), ('Annual_Mean_Tmax_C', 'Fatalities'),
                 ('Annual_Mean_Tmin_C', 'Accidents'), ('Annual_Mean_Tmin_C', 'Fatalities')]:
        d = g[[x, y]].dropna()
        n = len(d)
        if n < 7:
            rows.append([st, x, y, n, None, None, 'INSUFFICIENT_TEMPORAL_OBSERVATIONS'])
            continue
        r = sstats.pearsonr(d[x], d[y])
        rows.append([st, x, y, n, round(r[0], 4), round(r[1], 6), 'LOW_POWER_DESCRIPTIVE'])
pd.DataFrame(rows, columns=['State_UT', 'X', 'Y', 'N', 'Pearson_r', 'Pearson_p', 'Status']).to_csv(
    'research_analysis/WITHIN_STATE_WEATHER.csv', index=False)
d = pd.read_csv('research_analysis/WITHIN_STATE_WEATHER.csv')
print('rows:', len(d), '| insufficient:', int((d.Status == 'INSUFFICIENT_TEMPORAL_OBSERVATIONS').sum()))
print('NOTE: N<=7 per state; values are descriptive only and excluded from all inference.')
