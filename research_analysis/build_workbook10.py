"""Phase 10 final workbook (research documentation)."""
import pandas as pd
from openpyxl import Workbook
import glob

wb = Workbook()
ws = wb.active
ws.title = 'README'
ws.append(['Phase 10 final workbook: every sheet = a PHASE10_ CSV in research_analysis/',
           'Sources/vintages/methods/limits documented per sheet header in source CSVs and PHASE10_METHODOLOGY.md'])
for f in sorted(glob.glob('research_analysis/PHASE10_*.csv')):
    name = f.split('\\')[-1].replace('.csv', '')[:31]
    df = pd.read_csv(f)
    w = wb.create_sheet(name)
    w.append(list(df.columns))
    for row in df.itertuples(index=False):
        w.append([('' if pd.isna(v) else v) for v in row])
wb.save('OriginPro_Phase10_Final_Research_Workbook.xlsx')
print('workbook saved')
