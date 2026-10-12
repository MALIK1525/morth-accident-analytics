"""Phase 6 harmonization builder (research documentation, not application code)."""
import csv
import pandas as pd

cand = list(csv.DictReader(open(
    '02_VERIFIED_DATA/phase5/historical_2014_2017/HISTORICAL_STATE_PANEL_CANDIDATE.csv',
    encoding='utf-8')))
bench = pd.read_excel('data/MoRTH_Primary_Dataset_3.xlsx', 'CLEAN', header=2)

MERGED_DD = 'Dadra & Nagar Haveli and Daman & Diu'
out = []
# 2014-2017 from candidate
for r in cand:
    st, y = r['State_UT'], int(r['Year'])
    a, f, i = int(r['Accidents']), int(r['Fatalities']), int(r['Injured'])
    if st in ('Dadra & Nagar Haveli', 'Daman & Diu'):
        continue  # handled as merged sum below
    if st == 'Jammu & Kashmir':
        out.append([st + ' (pre-reorg, incl. Ladakh region)', y, a, f, i,
                    'AR2017 vintage', 'JK_UNDIVIDED', 'Direct pre-2019 administrative definition'])
    else:
        out.append([st, y, a, f, i, 'AR2017 vintage', 'DIRECT', 'Stable entity'])
# DNH+Diu sums 2014-2017 (candidate) + 2018-2019 (benchmark legacy splits)
for y in [2014, 2015, 2016, 2017]:
    sel = [r for r in cand if int(r['Year']) == y and r['State_UT'] in ('Dadra & Nagar Haveli', 'Daman & Diu')]
    out.append([MERGED_DD, y, sum(int(r['Accidents']) for r in sel),
                sum(int(r['Fatalities']) for r in sel), sum(int(r['Injured']) for r in sel),
                'AR2017 vintage', 'SUM_HISTORICAL', 'Arithmetic sum of separate UTs (MEDIUM, mirrors Phase 2C)'])
for y in [2018, 2019]:
    sel = bench[(bench.Year == y) & (bench.State_UT.isin(['Dadra & Nagar Haveli', 'Daman & Diu']))]
    out.append([MERGED_DD, y, int(sel.Accidents.sum()), int(sel.Fatalities.sum()), int(sel.Injured.sum()),
                'benchmark (revised vintage)', 'SUM_HISTORICAL', 'Arithmetic sum of legacy split rows (MEDIUM)'])
# 2018-2024 from benchmark
for _, r in bench.iterrows():
    y = int(r['Year'])
    a, f = r['Accidents'], r['Fatalities']
    inj = r['Injured']
    inj = None if str(inj).strip() in ('NV', 'nan', '') else int(inj)
    if str(a).strip() == 'NV':
        out.append([r['State_UT'], y, None, None, inj, 'benchmark (revised vintage)',
                    'NV_SOURCE', 'Not verified in benchmark (Ladakh 2018-2020)'])
        continue
    st = r['State_UT']
    if st == 'Jammu & Kashmir' and y <= 2019:
        flag = 'JK_UNDIVIDED'
    elif st == 'Jammu & Kashmir':
        flag = 'JK_UT_BREAK'
    elif st == 'Ladakh':
        flag = 'LADAKH_START_2021'
    elif st == MERGED_DD:
        flag = 'DIRECT_MERGED'
    elif st in ('Dadra & Nagar Haveli', 'Daman & Diu'):
        flag = 'LEGACY_SPLIT'
    else:
        flag = 'DIRECT'
    out.append([st, y, int(a), int(f), inj, 'benchmark (revised vintage)', flag, ''])

with open('02_VERIFIED_DATA/phase6/HARMONIZED_PANEL_2014_2024_CANDIDATE.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh)
    w.writerow(['State_UT_Harmonized', 'Year', 'Accidents', 'Fatalities', 'Injured',
                'Source_Vintage', 'Harmonization_Flag', 'Note'])
    w.writerows(out)

# India totals check (numeric rows only, merged DD counted once)
pub = {2014: (489400, 139671, 493474), 2015: (501423, 146133, 500279),
       2016: (480652, 150785, 494624), 2017: (464910, 147913, 470975),
       2018: (470403, 157593, 464715), 2019: (456959, 158984, 449360),
       2020: (372181, 138383, 346747), 2021: (412432, 153972, 384448),
       2022: (461312, 168491, 443366), 2023: (480583, 172890, 462825),
       2024: (487707, 177175, 471441)}
print('Year | acc_sum acc_pub | fat_sum fat_pub | inj_sum inj_pub | result')
for y in range(2014, 2025):
    rows = [r for r in out if r[1] == y and r[2] is not None and 'LEGACY_SPLIT' not in r[6]]
    # avoid double count: drop pre-reorg split rows (already merged); JK_UNDIVIDED kept
    sa = sum(r[2] for r in rows)
    sf = sum(r[3] for r in rows)
    si = sum(r[4] for r in rows if r[4] is not None)
    pa, pf, pi = pub[y]
    ok = (sa == pa and sf == pf and (y >= 2023 or si == pi))
    print(y, sa, pa, '|', sf, pf, '|', si, pi, 'MATCH' if ok else 'CHECK')
print('rows:', len(out))
