"""Phase 4 output builder (research documentation, not application code)."""
import csv, hashlib, os
OUT = 'research_acquisition'
os.makedirs(OUT, exist_ok=True)

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

inv = [
['TN district accidents/deaths 2021-23', 'TN SCRB/Transport via OpenCity CKAN', 'TN Road Accidents Analysis 2023 (parent PDF)', 'district CSV table', 'https://data.opencity.in/dataset/tamil-nadu-road-accidents-reports', '-', '2021-2023', '38 TN districts', 'District/Accidents/Deaths', 'counts', 'district sums == MoRTH TN exactly', '01_RAW_DATA/phase4/tamilnadu_district/tn_district_2021_23.csv', sha('01_RAW_DATA/phase4/tamilnadu_district/tn_district_2021_23.csv'), 'VERIFIED-MIRROR'],
['NCRB ADSI 2024 Table 1A.5 month-wise (PDF raw)', 'NCRB via OpenCity CKAN', 'ADSI 2024', 'Table 1A.5', 'https://data.opencity.in/dataset/accidental-deaths-and-suicides-in-india-2024', '-', '2024', 'States/UTs/Cities x 12 months', 'monthly traffic-accident counts', 'counts', 'PDF text inspected; structure confirmed', '01_RAW_DATA/phase4/ncrb_adsi2024/NCRB_ADSI2024_Table1A5_MonthWise_StateUT_City.pdf', sha('01_RAW_DATA/phase4/ncrb_adsi2024/NCRB_ADSI2024_Table1A5_MonthWise_StateUT_City.pdf'), 'VERIFIED-MIRROR'],
['NCRB month-wise traffic accidents 2024 (extracted)', 'NCRB via OpenCity CKAN', 'ADSI 2024', 'Table 1A.5', 'see above', '-', '2024', 'States/UTs/Cities x 12 months', 'Section/Scope/State/Jan-Dec/Total', 'counts', '4/4 sections states+UTs==TOTAL; 4/4 cities==TOTAL', '02_VERIFIED_DATA/phase4/ncrb_monthwise_traffic_accidents_2024.csv', sha('02_VERIFIED_DATA/phase4/ncrb_monthwise_traffic_accidents_2024.csv'), 'VERIFIED-MIRROR'],
['NCRB ADSI 2024 time-wise table (PDF)', 'NCRB via OpenCity CKAN', 'ADSI 2024', 'Table 1A.6', 'https://data.opencity.in/dataset/accidental-deaths-and-suicides-in-india-2024', '-', '2024', 'States/UTs/Cities x time buckets', 'time-of-day counts', 'counts', 'discovered, not downloaded', '-', '-', 'DISCOVERED'],
['OGD state registered vehicles 2010-2020', 'MoRTH via data.gov.in OGD (RTYB 2019-20 catalog)', 'Road Transport Year Book 2019-20', 'Sec 3 / Annex 3.2 family', 'https://www.data.gov.in/resource/statesuts-wise-total-registered-motor-vehicles-india-2010-2020-figures-31st-march', '-', '2010-2020', 'States/UTs x Year', 'registered vehicle stock', 'counts', 'page confirmed; direct CSV behind JS/API key', '-', '-', 'DISCOVERED'],
['MoRTH AR 2014-2017 PDFs (state tables)', 'MoRTH via OpenCity CKAN', 'AR 2014/2015/2016/2017', 'state tables', 'https://data.opencity.in/dataset/road-accidents-in-india', '-', '2014-2017', 'States/UTs', 'accidents/fatalities/injuries', 'counts', 'PDFs confirmed present; no extraction performed', '-', '-', 'DISCOVERED'],
['eDAR accident-level system', 'MoRTH/NIC (Parivahan)', '-', '-', 'https://edar.parivahan.gov.in/ (DNS-unresolvable here)', '-', '-', '-', '-', '-', 'authority-only portal; no bypass attempted', '-', '-', 'ACCESS-RESTRICTED'],
['IMD humidity/visibility/fog/wind grids', 'IMD', '-', '-', 'https://dsp.imdpune.gov.in/home_gridded_climatology.php (offers temp/rain only)', '-', '-', '-', '-', '-', 'gridded climatology covers temp+rain only; station data is request/paid', '-', '-', 'NOT AVAILABLE'],
]
with open(f'{OUT}/DATA_SOURCE_INVENTORY.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Dataset','Organization','Report','Table','Source_URL','Mirror_URL','Coverage','Geography','Variables','Units','Validation','Local_Path','SHA256','Status'])
    w.writerows(inv)

gaps = [
['Monthly/Seasonal (A)', 'P1', 'NCRB month-wise 2024 extracted (Road section, States)', 'ACQUIRED+VERIFIED', 'Only 2024; NCRB vintage separate from MoRTH; no MoRTH monthly exists'],
['Monthly/Seasonal (A)', 'P1', 'NCRB time-wise buckets', 'DISCOVERED', 'PDF-only; download on demand'],
['District (B)', 'P2', 'TN 38 districts 2021-23', 'ACQUIRED+VERIFIED', 'Single state only; post-2019 splits visible'],
['District (B)', 'P2', 'Other states district panels', 'NOT FOUND', 'No verified multi-state source located'],
['Accident-level (C)', 'P1', 'eDAR', 'ACCESS-RESTRICTED', 'No public path; no bypass'],
['Driver/Vehicle (D)', 'P2', 'Beyond licence table', 'NOT FOUND', 'No verified age/gender/age-of-vehicle file located'],
['Exposure (E)', 'P1', 'State vehicles 2010-2020 (OGD)', 'DISCOVERED', 'Needs API key or manual download; RTYB PDF is fallback source'],
['Environment (F)', 'P2', 'Humidity/visibility/fog/wind', 'NOT AVAILABLE', 'IMD grids cover temp/rain only'],
['2014-2017 (G)', 'P4', 'AR PDFs 2014-2017', 'DISCOVERED (PDF-only)', 'State extraction not performed; geography reconciliation pending'],
]
with open(f'{OUT}/DATA_GAP_STATUS.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Gap','Priority','Finding','Acquisition_Status','Note'])
    w.writerows(gaps)

val = [
['TN district 2021 acc sum', '55682', '55682 (MoRTH TN 2021)', '0', 'MATCH'],
['TN district 2022 fat sum', '17884', '17884 (MoRTH TN 2022)', '0', 'MATCH'],
['TN district 2023 acc sum', '67213', '67213 (MoRTH TN 2023)', '0', 'MATCH'],
['NCRB Road states+UTs 2024', '467967', '467967 (TOTAL ALL INDIA)', '0', 'MATCH'],
['NCRB Road cities 2024', '71239', '71239 (TOTAL CITIES)', '0', 'MATCH'],
['NCRB RailX/Rail/Grand sections', 'all match', 'published totals', '0', 'MATCH'],
['NCRB road vs MoRTH 2024', '467967', '487707 (MoRTH)', '-19740', 'MISMATCH (definition)'],
]
with open(f'{OUT}/VALIDATION_SUMMARY.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Check','Computed','Published','Difference','Result'])
    w.writerows(val)

cand = [
['MoRTH benchmark', 'TN district 2021-23', 'State(TN only)+Year', '2021-23 overlap', 'district sums == state totals exactly', 'counts', 'none', 'MAYILADUTHURAI 2021 NaN', 'none', 'CONDITIONAL', 'TN-only district drill-down; national join unsafe'],
['MoRTH benchmark', 'NCRB month-wise 2024', 'State+Year(2024)', '2024 only', 'state names; NCRB DAMAN&DIU label', 'counts', 'high (definition drift)', 'NCRB total 467967 vs MoRTH 487707', 'none', 'NO (as merge)', 'Keep as parallel NCRB-vintage seasonality source only'],
['MoRTH benchmark', 'NCRB cities month-wise', 'City+Year', '2024', '50 vs NCRB city lists differ', 'counts', 'medium', '-', 'city-definition mismatch', 'NO', 'Separate analysis only'],
]
with open(f'{OUT}/INTEGRATION_CANDIDATES.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Dataset_A','Dataset_B','Join_Key','Year_Compat','Geography','Unit_Compat','Definition_Compat','Missingness','Boundary_Issue','Safe_Integration','Reason'])
    w.writerows(cand)

upd = [
['D-02 Month', 'UNAVAILABLE', 'PARTIAL (NCRB 2024 Road-states extracted; separate vintage)', '02_VERIFIED_DATA/phase4/ncrb_monthwise_traffic_accidents_2024.csv'],
['B-04 District', 'UNAVAILABLE', 'PARTIAL (TN 2021-23 verified; single state)', '01_RAW_DATA/phase4/tamilnadu_district/tn_district_2021_23.csv'],
['A-03 Time bucket', 'PARTIAL', 'PARTIAL (NCRB Table 1A.6 discovered PDF-only)', '-'],
['F-04 Registered vehicles state split', 'PARTIAL', 'DISCOVERED (OGD 2010-2020, not yet downloaded)', '-'],
['2014-2017 state panel', 'UNAVAILABLE', 'DISCOVERED (AR PDFs; extraction pending)', '-'],
['A-01 Accident ID / coords', 'UNAVAILABLE', 'ACCESS-RESTRICTED (eDAR)', '-'],
['J-04 Humidity etc.', 'UNAVAILABLE', 'NOT AVAILABLE (IMD grids temp/rain only)', '-'],
]
with open('research_audit/PHASE4_COVERAGE_UPDATE.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Parameter', 'Phase3_Status', 'Phase4_Status', 'Evidence'])
    w.writerows(upd)
print('phase4 outputs written')
