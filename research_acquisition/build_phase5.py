"""Phase 5 output builder (research documentation, not application code)."""
import csv
open('research_acquisition/PHASE5_HISTORICAL_GEO_MAP.csv', 'w', newline='', encoding='utf-8').write(
    'Historical_State,Canonical_State,Year,Transformation,Reason,Safe_to_harmonize\n'
    'Telangana,Telangana,2014-2017,NONE,separate in source all years,YES\n'
    'Jammu & Kashmir,"Jammu & Kashmir + Ladakh (2018+ panel split)",2014-2017,SPLIT_REQUIRED,undivided pre-2019 reorganisation,CONDITIONAL\n'
    'Dadra & Nagar Haveli,DNH & Daman & Diu (2020+ merged entity),2014-2017,AGGREGATE_REQUIRED (2020+),separate pre-2020 merger,CONDITIONAL\n'
    'Daman & Diu,DNH & Daman & Diu (2020+ merged entity),2014-2017,AGGREGATE_REQUIRED (2020+),separate pre-2020 merger,CONDITIONAL\n'
    'All other states/UTs,same name,2014-2017,NONE,stable names/definition,YES\n')

val = [
    ['2014', '489400', '489400', '0', '139671', '139671', '0', '493474', '493474', '0', 'MATCH'],
    ['2015', '501423', '501423', '0', '146133', '146133', '0', '500279', '500279', '0', 'MATCH'],
    ['2016', '480652', '480652', '0', '150785', '150785', '0', '494624', '494624', '0', 'MATCH'],
    ['2017', '464910', '464910', '0', '147913', '147913', '0', '470975', '470975', '0', 'MATCH'],
]
with open('research_acquisition/PHASE5_HISTORICAL_RECONCILIATION.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Year', 'Computed_acc', 'Published_acc', 'Diff_acc', 'Computed_fat', 'Published_fat', 'Diff_fat', 'Computed_inj', 'Published_inj', 'Diff_inj', 'Result'])
    w.writerows(val)

compat = [
    ['2014', 'CONDITIONAL', '36 entities incl Telangana; J&K undivided; DNH/Diu separate; exact total reconciliation'],
    ['2015', 'CONDITIONAL', 'as 2014'],
    ['2016', 'CONDITIONAL', 'as 2014'],
    ['2017', 'CONDITIONAL', 'as 2014'],
]
with open('research_acquisition/PHASE5_YEAR_COMPATIBILITY.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Year', 'Compatible_2018_2024', 'Reason'])
    w.writerows(compat)

integ = [
['MoRTH 2018-24 benchmark', 'Historical 2014-17 candidate', 'State+Year', '2014-17 vs 2018-24', 'CONDITIONAL geography', 'counts', 'J&K split + DNH merge handling required', 'none', 'CONDITIONAL', 'Join allowed only with documented SPLIT/AGGREGATE transforms; benchmark untouched'],
['MoRTH accidents', 'State registered vehicles', 'State+Year', 'no verified state file', '-', '-', '-', 'all years missing', 'UNSAFE (no data)', 'No verified state-level vehicle denominator acquired'],
['MoRTH accidents (India)', 'Registered vehicles India (EX-01)', 'Year', '2014-22', 'India', 'counts vs 000', 'stock incl dead vehicles', '2023-24 NA', 'CONDITIONAL (descriptive only)', 'India-level comparison only; not a state rate'],
]
with open('research_acquisition/PHASE5_INTEGRATION_RESULTS.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Dataset_A', 'Dataset_B', 'Join_Key', 'Years', 'Geography', 'Unit_Compat', 'Definition_Compat', 'Missingness', 'Safe_Integration', 'Reason'])
    w.writerows(integ)

with open('research_audit/PHASE5_COVERAGE_UPDATE.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Parameter', 'Phase4_Status', 'Phase5_Status', 'Evidence'])
    w.writerows([
        ['2014-2017 state acc/fat/inj', 'DISCOVERED PDF-only', 'VERIFIED CANDIDATE (AR2017 vintage, 12/12 MATCH)', '02_VERIFIED_DATA/phase5/historical_2014_2017/HISTORICAL_STATE_PANEL_CANDIDATE.csv'],
        ['State registered vehicles', 'DISCOVERED (OGD)', 'DISCOVERED (OGD + RTYB identified; download blocked)', 'research_acquisition/PHASE5_VEHICLE_FINDING.md'],
        ['2019 vintage control', 'documented', 'preserved (AR2017 vintage separate; benchmark untouched)', 'provenance file'],
    ])
print('phase5 outputs written')
