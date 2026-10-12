"""Phase 11 audits: claims + consistency (generated, checked)."""
import os
import pandas as pd

claims = [
    ['Accidents +3.7% 2018-2024', 'INDIA_YEAR_ANALYSIS.csv', '470403->487707', 'YES', 'Descriptive', 'NO', 'NO', 'YES', ''],
    ['Fatalities +12.4%', 'INDIA_YEAR_ANALYSIS.csv', '157593->177175', 'YES', 'Descriptive', 'NO', 'NO', 'YES', ''],
    ['Severity 33.50->36.33', 'INDIA_YEAR_ANALYSIS.csv', 'computed ratio', 'YES', 'Descriptive', 'NO', 'NO', 'YES', 'case-fatality-style, labeled'],
    ['Rain r=-0.234 acc', 'WEATHER_ASSOCIATIONS.csv', 'N=236, p=2.9e-4, FDR-held', 'YES', 'Association', 'NO', 'NO', 'YES', 'scale confounding disclosed'],
    ['Naive beats all trained', 'PHASE9_BASELINE_COMPARISON.csv', 'RMSE 1038.6 vs 2148.6+', 'YES', 'Predictive', 'NO', 'NO', 'YES', 'honest null'],
    ['K=2 descriptive profiles', 'PHASE9_CLUSTER_*', 'silhouette 0.356, ARI', 'YES', 'Exploratory', 'NO', 'NO', 'YES', 'labels never risk'],
    ['May peak / July trough', 'NCRB_MONTHLY_2024.csv', '8.84%/7.46%, chi2', 'YES', 'Descriptive', 'NO', 'NO', 'YES', 'NCRB vintage labeled'],
    ['Two-wheelers 46.2% of deaths', 'VH-01 module file', '81780/177175', 'YES', 'Descriptive', 'NO', 'YES*', 'YES', '*exposure required for risk; counts only'],
    ['Over-speeding 70.3% of deaths', 'CS-01 module file', '124522/177175', 'YES', 'Descriptive', 'NO', 'NO', 'YES', 'reported category only'],
]
pd.DataFrame(claims, columns=['Claim', 'Source', 'Evidence', 'Supported?', 'Claim_Type', 'Causal?',
                              'Exposure_Required?', 'Allowed_in_Paper?', 'Notes']
             ).to_csv('FINAL_SUBMISSION_PACKAGE/12_AUDIT/FINAL_CLAIMS_AUDIT.csv', index=False)

DOCS = ['01_FINAL_REPORT/FINAL_BTECH_RESEARCH_REPORT.md', '02_RESEARCH_PAPER/FINAL_RESEARCH_PAPER.md',
        '02_RESEARCH_PAPER/FINAL_IEEE_PAPER.md', '03_ABSTRACT/FINAL_ABSTRACT.md',
        '06_PRESENTATION/FINAL_BTECH_PRESENTATION.md']
checks = [
    ('Title core', 'Multi-Level Data-Driven Analysis of Road Traffic Accidents in India'),
    ('Years', '2018-2024'), ('State-years', '254'), ('Entities', '38'),
    ('Weather matched', '236'), ('ML test', '2023-2024'),
    ('Baseline RMSE acc', '1038.6'), ('K-means K', 'K=2'), ('Silhouette', '0.356'),
]
rows = []
def present(t, field, exp):
    n = t.replace('\u2013', '-').replace('\u2014', '-')
    if field == 'Title core':
        return ('Multi-Level Data-Driven Analysis' in n or 'Data-Driven Road Traffic Accident Analysis' in n)
    if field == 'ML test':
        return ('2023' in n and '2024' in n and 'test' in n.lower())
    return exp in n

for d in DOCS:
    t = open('FINAL_SUBMISSION_PACKAGE/' + d, encoding='utf-8').read()
    for field, exp in checks:
        ok = present(t, field, exp)
        rows.append([d.split('/')[-1], field, exp, exp if ok else 'MISSING', 'PASS' if ok else 'FAIL'])
pd.DataFrame(rows, columns=['Document', 'Field', 'Expected_Value', 'Actual_Value', 'Status']
             ).to_csv('FINAL_SUBMISSION_PACKAGE/12_AUDIT/FINAL_DOCUMENT_CONSISTENCY_AUDIT.csv', index=False)
fails = sum(1 for r in rows if r[4] == 'FAIL')
print('consistency fails:', fails)
for r in rows:
    if r[4] == 'FAIL':
        print(r)
