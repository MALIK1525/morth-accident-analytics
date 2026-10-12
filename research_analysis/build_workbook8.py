"""Phase 8 OriginPro workbook (research documentation)."""
import pandas as pd
from openpyxl import Workbook

wb = Workbook()
ws = wb.active
ws.title = 'README'
for r in [
    ['Sheet', 'Source', 'Vintage', 'Years', 'Variables', 'Question', 'Graph', 'X', 'Y', 'Method', 'Limitations'],
    ['All data sheets', 'see per-sheet Source col in CSVs', 'MoRTH benchmark / NCRB / IMD / AR2017', 'as listed', 'as listed', 'cross-factor associations', 'bar/scatter/line', 'factor', 'outcome', 'corr/OLS/chi2/Friedman', 'association only; NCRB separate; candidate conditional'],
]:
    ws.append(r)
import glob
for f in sorted(glob.glob('research_analysis/*.csv')):
    name = f.split('\\')[-1].replace('.csv', '')[:31]
    df = pd.read_csv(f)
    w = wb.create_sheet(name)
    w.append(list(df.columns))
    for row in df.itertuples(index=False):
        w.append([('' if pd.isna(v) else v) for v in row])
wb.save('OriginPro_Phase8_CrossFactor_Analysis.xlsx')
print('workbook saved')
