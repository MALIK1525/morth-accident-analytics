"""Phase 9 OriginPro workbook (research documentation)."""
import pandas as pd
from openpyxl import Workbook
import glob

wb = Workbook()
ws = wb.active
ws.title = 'README'
for r in [['Sheet = CSV name in research_analysis/', 'Source/vintage in file headers',
           'Methods: OLS/corr/chi2/Friedman/ML/K-means', 'Association only; NCRB separate; candidate conditional']]:
    ws.append(r)
for f in sorted(glob.glob('research_analysis/PHASE9_*.csv')) + sorted(glob.glob('research_analysis/PHASE9_*.md')):
    if f.endswith('.csv'):
        name = f.split('\\')[-1].replace('.csv', '')[:31]
        df = pd.read_csv(f)
        w = wb.create_sheet(name)
        w.append(list(df.columns))
        for row in df.itertuples(index=False):
            w.append([('' if pd.isna(v) else v) for v in row])
wb.save('OriginPro_Phase9_Predictive_Analysis.xlsx')
print('workbook saved')
