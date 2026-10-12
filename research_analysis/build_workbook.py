"""OriginPro workbook builder for Phase 7 (research documentation)."""
import csv
from openpyxl import Workbook

wb = Workbook()
readme = [
    ['Sheet', 'Research question', 'Source', 'Years', 'Variables', 'Recommended OriginPro graph', 'X', 'Y', 'Notes/Limitations'],
    ['INDIA_YEAR', 'India trend 2018-24', 'MoRTH benchmark CLEAN', '2018-24', 'Acc/Fat/Inj + YoY', 'Line (3 series)', 'Year', 'Count', 'Injuries_India_Verified is India vintage; state sums N/A 2023-24'],
    ['ZONE_YEAR', 'Zone comparison', 'Benchmark + zone map', '2018-24', 'Acc/Fat/Share/YoY', 'Grouped bar + line', 'Year', 'Count', 'Descriptive; no ranking'],
    ['MATRICES', 'State-year heatmap', 'Benchmark', '2018-24', 'Acc/Fat', 'Heatmap', 'Year', 'State', 'NV preserved as missing'],
    ['STATE_TRENDS', 'State slopes', 'OLS per state N=7', '2018-24', 'Slope/R2/p/CI', 'Bar with CI', 'State', 'Slope', 'Low power; association only'],
    ['WEATHER', 'Weather association', 'IMD join (236 matched)', '2018-24', 'Rain/Tmax/Tmin vs Acc/Fat/Sev', 'Scatter', 'Weather', 'Outcome', 'Pooled; scale confounding; not causal'],
    ['NCRB_MONTHLY', '2024 seasonality', 'NCRB ADSI T1A.5 (separate vintage)', '2024', 'Month cases/share/MoM', 'Bar', 'Month', 'Cases', 'NCRB vintage; never merged to MoRTH'],
]
ws = wb.active
ws.title = 'README'
for r in readme:
    ws.append(r)

import pandas as pd
sheets = {
    'INDIA_YEAR': 'research_analysis/INDIA_YEAR_ANALYSIS.csv',
    'ZONE_YEAR': 'research_analysis/ZONE_YEAR_ANALYSIS.csv',
    'STATE_TRENDS': 'research_analysis/STATE_TREND_STATISTICS.csv',
    'WEATHER_ASSOC': 'research_analysis/WEATHER_ASSOCIATIONS.csv',
    'NCRB_MONTHLY': 'research_analysis/NCRB_MONTHLY_2024.csv',
    'GRAPH_PLAN': 'research_analysis/GRAPH_PLAN.csv',
}
for name, path in sheets.items():
    df = pd.read_csv(path)
    w = wb.create_sheet(name)
    w.append(list(df.columns))
    for row in df.itertuples(index=False):
        w.append([('' if pd.isna(v) else v) for v in row])
piv = pd.read_csv('research_analysis/STATE_YEAR_ACCIDENT_MATRIX.csv')
w = wb.create_sheet('MATRICES_ACC')
w.append(list(piv.columns))
for row in piv.itertuples(index=False):
    w.append([('' if pd.isna(v) else v) for v in row])
wb.save('OriginPro_Phase7_Research_Analysis.xlsx')
print('workbook saved')
