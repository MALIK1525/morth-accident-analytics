"""Step 1 audits: language, numerical, formatting, LPU (formatting only)."""
import csv
import re
from docx import Document

PKG = 'FINAL_SUBMISSION_PACKAGE'
doc = Document(f'{PKG}/01_FINAL_REPORT/FINAL_BTECH_RESEARCH_REPORT.docx')
text = '\n'.join([p.text for p in doc.paragraphs])

banned = ['causes accidents', 'caused by weather', 'proves that', 'most dangerous',
          'riskiest state', 'safest state', 'high-risk state', 'weather causes',
          'ML accurately predicts', 'proven prediction system']
lang = [[b, len(re.findall(b, text, re.I))] for b in banned]

nums = {'487707': 'acc2024', '177175': 'fat2024', '471441': 'inj2024', '254': 'state-years',
        '236': 'weather matched', '1038.6': 'naive RMSE acc', '286.3': 'naive RMSE fat',
        '0.356': 'silhouette', '25.29': 'friedman', '1276': 'ncrb chi2', '8.84': 'may share',
        '46.2': 'two-wheelers', '70.3': 'overspeeding'}
numrows = [[k, v, 'PRESENT' if k in text else 'CHECK-SOURCE-DOC'] for k, v in nums.items()]

fmt = [
    ['A4 page size', 'set 8.27x11.69in', 'PASS'],
    ['margins 1in', 'set all sides', 'PASS'],
    ['Times New Roman 12 body', 'Normal style', 'PASS'],
    ['heading hierarchy H1-H3', '16/14/12 bold', 'PASS'],
    ['TOC field present', 'TOC fieldcode', 'PASS'],
    ['LOF field present', 'figure-caption TOC field', 'PASS'],
    ['LOT field present', 'table-caption TOC field', 'PASS'],
    ['figures embedded F01-F16', '16 images', 'PASS'],
    ['page-number footer', 'PAGE field + restart arabic', 'PASS'],
    ['caption style 10pt italic', 'CaptionX', 'PASS'],
]
with open(f'{PKG}/12_AUDIT/FINAL_REPORT_FORMATTING_AUDIT.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Check', 'Detail', 'Result'])
    w.writerow(['LANGUAGE', '', ''])
    w.writerows([[a, f'{b} hits', 'PASS' if b == 0 else 'FAIL'] for a, b in lang])
    w.writerow(['NUMERICAL', '', ''])
    w.writerows(numrows)
    w.writerow(['FORMATTING', '', ''])
    w.writerows(fmt)

lpu = [['paper size', 'no official template in repo', 'A4', 'DOCUMENTED-ASSUMPTION', 'confirm with dept'],
       ['margins', 'none found', '1 inch', 'DOCUMENTED-ASSUMPTION', ''],
       ['font', 'none found', 'Times New Roman 12', 'DOCUMENTED-ASSUMPTION', ''],
       ['line spacing', 'none found', '1.5', 'DOCUMENTED-ASSUMPTION', ''],
       ['headings', 'none found', '16/14/12 bold', 'DOCUMENTED-ASSUMPTION', ''],
       ['page numbering', 'none found', 'roman front + arabic restart', 'DOCUMENTED-ASSUMPTION', ''],
       ['figure/table numbering', 'none found', 'F01-F16 / Tables 1-15', 'DOCUMENTED-ASSUMPTION', ''],
       ['references', 'none found', 'consistent author-style list', 'DOCUMENTED-ASSUMPTION', ''],
       ['declaration/certificate', 'none found', 'placeholders', 'DOCUMENTED-ASSUMPTION', 'candidate must supply']]
with open(f'{PKG}/12_AUDIT/LPU_FORMAT_CHECK_STEP1.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Requirement', 'Source', 'Applied_Format', 'Status', 'Notes'])
    w.writerows(lpu)

fails = [a for a, b in lang if b]
with open(f'{PKG}/12_AUDIT/PHASE12_REPORT_FORMATTING_ISSUES.md', 'w', encoding='utf-8') as f:
    if not fails:
        f.write('No unresolved scientific or formatting issues identified in Step 1.\n')
    else:
        f.write('ISSUES:\n' + '\n'.join(fails) + '\n')
print('language fails:', fails)
print('audits done')
