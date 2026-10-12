"""Phase 3 audit builder (diagnostic, not application code).
Reads actual repository datasets and emits the availability matrices.
All status claims below are grounded in files inspected 2026-09-28.
"""
import csv, os
OUT = 'research_audit'
os.makedirs(OUT, exist_ok=True)

# (id, group, name, status, source_dataset, org, report, table, years, geo, unit,
#  raw_derived, formula, join_key, coverage, missingness, definition, use, limits, evidence, confidence)
R = []
def row(*a): R.append(a)

# ---- A. Accident identification ----
row('A-01','A','Accident ID / Case ID','UNAVAILABLE','-','-','-','-','-','-','-','-','-','-','none','-','Per-record ID lives in restricted eDAR/iRAD portal','-','Access restricted to authorities; no public file','DATA_AVAILABILITY.csv','DOCUMENTED')
row('A-02','A','Accident date (exact day)','UNAVAILABLE','-','NCRB','ADSI (month buckets only)','1A.5','-','-','-','-','-','-','none','-','Only month aggregates published','-','No per-accident dates anywhere public','DATA_AVAILABILITY.csv','DOCUMENTED')
row('A-03','A','Accident time (hour bucket)','PARTIAL','MoRTH AR 2024 chart 7.4 (India); NCRB PDF (state)','MoRTH/NCRB','AR 2024','chart 7.4','2024','India (+state PDF-only)','bucket','Raw','-','-','2024 only, PDF-only','state not machine-readable','8x3-hour buckets','Seasonality proxy','Not extracted to CSV','DATA_AVAILABILITY.csv','PARTIAL')
row('A-04','A','Accident location (address/segment)','UNAVAILABLE','-','-','-','-','-','-','-','-','-','-','none','-','Road-segment location not in any verified file','-','Only Bengaluru station-wise exists (not in repo)','DATA_AVAILABILITY.csv','DOCUMENTED')
# ---- B. Geography ----
row('B-01','B','India total','DIRECT','MoRTH_Primary_Dataset_3.xlsx CLEAN','MoRTH','AR 2018-2024','state tables','2018-2024','India','count','Raw','-','-','254 state-years sum','none','Aggregate of state panel','All India trends','-','CLEAN sheet verified 254 rows','VERIFIED')
row('B-02','B','State / UT','DIRECT','MoRTH_Primary_Dataset_3.xlsx CLEAN','MoRTH','AR 2018-2024','state tables','2018-2024','State/UT (38 entities)','name','Raw','-','-','38 entities x7y','none','Year-aware entities (DNH-DD merged 2020+)','Core panel key','Legacy splits preserved, not forced','CLEAN + Phase 2C crosswalk','VERIFIED')
row('B-03','B','Zone (6-zone mapping)','DERIVED','app mapping over CLEAN','Project','Phase 1','-','2018-2024','Zone','name','Derived','State->Zone map','State','6 zones','none','N/S/E/W/Central/NE mapping','Zone analysis','Mapping choice documented','loader.py','VERIFIED')
row('B-04','B','District','UNAVAILABLE','-','-','-','-','-','-','-','-','-','-','none','-','Only TN publishes district CSV (not in repo)','-','No district file in repo','DATA_AVAILABILITY.csv','DOCUMENTED')
row('B-05','B','City (million-plus)','SUPPORTING_DATA','road-accidents-2024-cities-accidents-fatalities.csv','MoRTH via OpenCity','AR 2024 Sec 6','city tables','2023-2024','50 cities','count','Raw','-','City+Year','50 cities x2y','none','Source city classification kept','CT-01','City definitions per source vintage','Phase 2.7 validation','VERIFIED')
row('B-06','B','Police jurisdiction / station','UNAVAILABLE','-','-','-','-','-','-','-','-','-','-','none','-','Not in any verified file','-','-','DATA_AVAILABILITY.csv','DOCUMENTED')
row('B-07','B','Latitude / Longitude','UNSAFE_TO_INFER','-','-','-','-','-','-','-','-','-','-','none','-','Coords exist only in restricted eDAR; city/state centroids would fabricate precision','-','Must not geocode aggregates to points','project rule','DOCUMENTED')
# ---- C. Severity ----
row('C-01','C','Accidents (count)','DIRECT','MoRTH_Primary_Dataset_3.xlsx CLEAN','MoRTH','AR 2018-2024','state tables','2018-2024','State/UT','count','Raw','-','-','254 obs','none','Recorded accidents','Core outcome','-','CLEAN verified','VERIFIED')
row('C-02','C','Fatalities (deaths)','DIRECT','MoRTH_Primary_Dataset_3.xlsx CLEAN','MoRTH','AR 2018-2024','state tables','2018-2024','State/UT','count','Raw','-','-','254 obs','none','Persons killed','Core outcome','-','CLEAN verified','VERIFIED')
row('C-03','C','Injured (state level)','YEAR_LIMITED','MoRTH_Primary_Dataset_3.xlsx CLEAN','MoRTH','AR 2018-2024','state tables','2018-2022 verified; 2023-24 state N/A','State/UT','count','Raw','-','-','179 state-years','75 cells (2023-24) missing','State injuries stop at 2022 in source','Severity w/ bounds','Must never be filled from India totals','Phase 9 injury audit','VERIFIED')
row('C-04','C','Injured (India level)','DIRECT','MoRTH_Primary_Dataset_3.xlsx / AR tables','MoRTH','AR 2018-2024','Table 1.1','2018-2024','India','count','Raw','-','-','7 years','none','India injured 2018:464715 ... 2024:471441','India trends','Not splittable to states','CLEAN + brief','VERIFIED')
row('C-05','C','Fatalities per 100 accidents','DERIVED','CLEAN (Fatalities_per_100_Accidents)','Project','Phase 9','-','2018-2024','State/UT+India','deaths/100 acc','Derived','Fatalities/Accidents x 100','State+Year','254 obs','none','Severity conditional on recorded accidents','Severity core','Not a population rate','Phase 9','VERIFIED')
row('C-06','C','Grievous / minor / non-injury split','UNAVAILABLE','-','MoRTH','AR Table 8 (India PDF-only)','Table 8','-','-','-','-','-','-','none','-','India-level PDF-only, not extracted','-','Would need Table 8 extraction','visualization_agent.py','DOCUMENTED')
# ---- D. Temporal ----
row('D-01','D','Year','DIRECT','CLEAN','MoRTH','AR 2018-2024','-','2018-2024','all','year','Raw','-','-','full','none','Calendar year','Trend key','-','CLEAN','VERIFIED')
row('D-02','D','Month','UNAVAILABLE','-','NCRB','ADSI Table 1A.5 (PDF-only)','1A.5','2024','State (PDF)','month','-','-','-','none (not extracted)','-','Month-wise state counts exist PDF-only','-','Needs NCRB PDF extraction','DATA_AVAILABILITY.csv','DOCUMENTED')
row('D-03','D','Day / Day-of-week / Hour exact','UNAVAILABLE','-','-','-','-','-','-','-','-','-','-','none','-','Not published at any verified granularity','-','-','DATA_AVAILABILITY.csv','DOCUMENTED')
row('D-04','D','Day/night','UNAVAILABLE','-','-','-','-','-','-','-','-','-','-','none','-','Not in verified files','-','-','DATA_AVAILABILITY.csv','DOCUMENTED')
row('D-05','D','Calendar season (derived from month)','UNSAFE_TO_INFER','-','-','-','-','-','-','-','-','-','-','none','-','No month data to derive from; pan-India season labels invalid','-','Blocked until D-02 available','Phase 8 rule','DOCUMENTED')
# ---- E. Road ----
row('E-01','E','Road category (NH/SH/Other) counts','UNAVAILABLE','-','MoRTH/NCRB','AR Table 1.3 / NCRB 1A.7 (PDF-only)','Table 1.3','-','-','-','-','-','-','none','-','PDF-only, not extracted','-','Needs Table 1.3 extraction','visualization_agent.py','DOCUMENTED')
row('E-02','E','Road length (state)','YEAR_LIMITED','phase2b_road_2021_2022.csv (BRSI 2020-22)','MoRTH TRW','BRSI 2020-22','Annex 1.1.2/2.1.2','2021-2022','State','km','Raw','-','State+Year','68 usable rows; 4 UNRESOLVED cells','all years except 2021-22 N/A','Total + surfaced km','Road normalization 2021-22','No interpolation outside 2021-22','Phase 2B/2D','VERIFIED')
row('E-03','E','Road surface/condition/junction/control/width/lanes/lighting/urban-rural','UNAVAILABLE','-','-','AR annexures 22-23 (PDF-only)','-','-','-','-','-','-','-','none','-','State annexure tables exist PDF-only','-','Needs annexure extraction','search result (AR 2024 TOC)','DOCUMENTED')
# ---- F. Vehicle ----
row('F-01','F','Vehicle/road-user category (fatalities)','SUPPORTING_DATA','road-accidents-2024-fatality-road-user.csv','MoRTH via OpenCity','AR 2024 road-user table','-','2023-2024','India','deaths','Raw','-','Category+Year','9 cats','none','Victim mode fatalities','VH-01','India-level only','Phase 2.7','VERIFIED')
row('F-02','F','Causing-vehicle x victim matrix','SUPPORTING_DATA','road-accidents-2024-victims-crime-vehicle.csv','MoRTH via OpenCity','AR 2024 annexure','-','2024','India','deaths','Raw','-','Victim x CrimeVeh','81 cells','none','Row=victim, col=causing vehicle','VH-02','India-level only','Phase 2.7','VERIFIED')
row('F-03','F','Number of vehicles / vehicle age / manoeuvre','UNAVAILABLE','-','-','-','-','-','-','-','-','-','-','none','-','Not in verified files','-','-','DATA_AVAILABILITY.csv','DOCUMENTED')
row('F-04','F','Registered vehicles (stock)','PARTIAL','road-accidents-registrations-density-2014-24.csv','MoRTH via OpenCity','AR 2024 decadal table','-','2014-2022 (2023-24 NA)','India','000 vehicles','Raw','-','Year','9 years','2023-24 NA; state split absent','India stock incl. dead vehicles','EX-01','No state split; includes inactive','Phase 2.7','VERIFIED')
# ---- G. Driver ----
row('G-01','G','Licence status','SUPPORTING_DATA','road-accidents-2024-type-of-license.csv','MoRTH via OpenCity','AR 2024 Table 3.2','Table 3.2','2020-2024','India','accidents','Raw','-','Category+Year','4 statuses x5y','none','Accidents by driver licence status','DL-01','India-level; values are accidents','Phase 2.7','VERIFIED')
row('G-02','G','Driver age / gender / experience / alcohol / distraction / fatigue','UNAVAILABLE','-','-','-','-','-','-','-','-','-','-','none','-','Not in verified files; must not infer from licence/cause','-','-','DATA_AVAILABILITY.csv','DOCUMENTED')
row('G-03','G','Speeding / wrong-side (as violation counts)','SUPPORTING_DATA','road-accidents-2024-type-of-violation.csv','MoRTH via OpenCity','AR 2024 Table 3.1','Table 3.1','2023-2024','India','counts','Raw','-','Category+Year','6 causes','none','Violation counts (Over-speeding 70.7% acc 2024)','CS-01','Violation, not proved causation','Phase 2.7','VERIFIED')
# ---- H. Cause ----
row('H-01','H','Cause/violation categories (source-defined)','SUPPORTING_DATA','road-accidents-2024-type-of-violation.csv','MoRTH via OpenCity','AR 2024 Table 3.1','Table 3.1','2023-2024','India','counts','Raw','-','Category+Year','6 source categories','none','Exact source categories kept','CS-01','All-India; not NH-only','Phase 2.7','VERIFIED')
# ---- I. Collision ----
row('I-01','I','Collision types (source-defined)','SUPPORTING_DATA','road-accidents-2024-type-of-collision.csv','MoRTH via OpenCity','AR 2024 Table 1.5','Table 1.5','2023-2024','India','counts','Raw','-','Category+Year','9 types','none','Exact source types (Hit from Back etc.)','CL-01','India-level','Phase 2.7','VERIFIED')
# ---- J. Environment ----
row('J-01','J','Annual rainfall (state)','INTEGRABLE','state_weather_annual.csv + weather_morth_join.csv (236 matched)','IMD via project pipeline','CMPG grids','-','2018-2024','State (34 entities)','mm','Derived-spatial','area-weighted state mean of daily grids','State+Year','236 state-years; 18 excluded','Andaman/Lakshadweep/legacy-DNH excluded','Equal-cell weighting (<=0.6% sensitivity)','W1/W4/W5','Observational only','Phase 7','VERIFIED')
row('J-02','J','Annual mean Tmax','INTEGRABLE','state_weather_annual.csv','IMD via project pipeline','CMPG TMAX1','-','2018-2024','State (28 entities w/ cells)','degC','Derived-spatial','state mean of daily Tmax','State+Year','6 small UTs NO_VALID_TEMP_CELL','6 entities temp-NaN','1-degree grid limits small UTs','W2/W6/W7','Observational only','Phase 7','VERIFIED')
row('J-03','J','Annual mean Tmin','INTEGRABLE','state_weather_annual.csv','IMD via project pipeline','CMPG TMIN1','-','2018-2024','State (28 entities w/ cells)','degC','Derived-spatial','state mean of daily Tmin','State+Year','6 entities temp-NaN','as above','-','W3/W8/W9','Observational only','Phase 7','VERIFIED')
row('J-04','J','Humidity / Visibility / Fog / Wind','UNAVAILABLE','-','-','-','-','-','-','-','-','-','-','none','-','Not in IMD grids acquired; must not proxy from rain/temp','-','-','Phase 6','VERIFIED')
row('J-05','J','Lighting conditions','UNAVAILABLE','-','-','-','-','-','-','-','-','-','-','none','-','-','-','-','DATA_AVAILABILITY.csv','DOCUMENTED')
# ---- K. Exposure ----
row('K-01','K','Population (projected)','INTEGRABLE','phase2b_population_2018_2024.csv (RGI Table 11)','RGI/MoHFW','Pop. Projections 2011-2036','Table 11','2018-2024','State (37 entities)','000 persons','Raw','-','State+Year','254 matched (5 SUM/MEDIUM)','DNH-DD merge arithmetic','PROJECTIONS not census','Pop normalization','No Census 2021','Phase 2B/2D','VERIFIED')
row('K-02','K','Traffic volume / AADT / vehicle-km','UNAVAILABLE','-','-','-','-','-','-','-','-','-','-','none','-','No verified source','-','-','Phase 10 gaps','DOCUMENTED')
row('K-03','K','Road length (exposure use)','YEAR_LIMITED','phase2b_road_2021_2022.csv','MoRTH TRW','BRSI 2020-22','Annex 1.1.2/2.1.2','2021-2022','State','km','Raw','-','State+Year','68 usable','rest N/A','-','Road normalization','-','Phase 2B/2D','VERIFIED')
# ---- L. Spatial/GIS ----
row('L-01','L','State geometry (boundaries)','INTEGRABLE','SOI ABDB (local phase7_raw; vintage post-reorg)','Survey of India','ABDB','-','vintage ~2020+','State polygons','polygon','Raw','-','State name','36 polygons; legacy splits absent','2018-19 splits unreconstructible','Modern vintage only','Weather aggregation','Not for historicalLon/Lat','Phase 7','VERIFIED')
row('L-02','L','Hotspot / blackspot analysis','UNSAFE_TO_INFER','-','-','-','-','-','-','-','-','-','-','none','-','Needs coordinates (L B-07 unavailable)','-','State aggregates cannot yield hotspots','project rule','DOCUMENTED')
# ---- M. Statistical/derived ----
for mid, name, form in [
('M-01','India accident/fatality share','State value / India total x 100'),
('M-02','YoY % change','(cur-prev)/prev x 100'),
('M-03','OLS slope / R2 / p / CI (state trends)','OLS accidents-or-rate vs year'),
('M-04','Pooled Pearson/Spearman','corr across state-years'),
('M-05','Fatalities per lakh projected pop','Fatalities/Population x 100000'),
('M-06','Accidents per 1000 km road','Accidents/RoadLength x 1000'),
]:
    row(mid,'M',name,'DERIVED','phase CSVs (phase3/4/8/9 outputs)','Project','Phases 3/4/8/9','-','per-phase coverage','per-phase','per-metric','Derived',form,'per-phase','per validation reports','as documented','see phase reports','association readout (no causality)','no causal interpretation','phase workbooks','VERIFIED')
# ---- N. ML ----
row('N-01','N','ML target: next-year state accidents','DERIVED','phase5_ml_dataset.csv (lag-only)','Project','Phase 5','-','targets 2020-2024','State','count','Derived','t+1 accidents','State+TargetYear','N=175','9 rows excluded (panel gaps)','Chronological split; naive wins','Phase 5 modeling','Small-N; no weather/vehicle features','Phase 5','VERIFIED')
row('N-02','N','KNN / clustering features','PARTIAL','phase5_ml_dataset.csv','Project','Phase 5','-','2020-2024','State','mixed','Derived','lag features','State+Year','N=175','few features; scale-dominated','KNN supervised only','Readiness only','Needs richer features','Phase 5','PARTIAL')

cols = ['Parameter_ID','Parameter_Group','Parameter_Name','Status','Source_Dataset','Source_Organization','Report','Table','Years','Geography','Unit','Raw_or_Derived','Formula','Join_Key','Coverage','Missingness','Definition','Research_Use','Limitations','Evidence','Confidence']
with open(f'{OUT}/MASTER_PARAMETER_AVAILABILITY.csv','w',newline='',encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(cols); w.writerows(R)

# Year x parameter matrix
years = ['2014','2015','2016','2017','2018','2019','2020','2021','2022','2023','2024']
Y = [
('Accidents state-level','N','N','N','N','ok','ok','ok','ok','ok','ok','ok'),
('Fatalities state-level','N','N','N','N','ok','ok','ok','ok','ok','ok','ok'),
('Injured state-level','N','N','N','N','ok','ok','ok','ok','ok','N','N'),
('Injured India-level','ok','ok','ok','ok','ok','ok','ok','ok','ok','ok','ok'),
('Population projected state','N','N','N','N','ok','ok','ok','ok','ok','ok','ok'),
('Road length state','N','N','N','N','N','N','N','ok','ok','N','N'),
('Registered vehicles India','ok','ok','ok','ok','ok','ok','ok','ok','ok','N','N'),
('Weather state (rain/temp)','N','N','N','N','ok','ok','ok','ok','ok','ok','ok'),
('Violation/Collision/Road-user (India)','N','N','N','N','N','N','N','N','N','ok','ok'),
('Licence (India)','N','N','N','N','N','N','ok','ok','ok','ok','ok'),
('Cities 50 (acc/fat)','N','N','N','N','N','N','N','N','N','ok','ok'),
('Safety devices (India)','N','N','N','N','N','N','N','N','N','N','ok'),
('Month/Day/Hour/Cause-detail/District/Coords','N','N','N','N','N','N','N','N','N','N','N'),
]
with open(f'{OUT}/YEAR_PARAMETER_MATRIX.csv','w',newline='',encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['Parameter']+years)
    for pid in Y:
        w.writerow([pid[0]]+[('✓' if v=='ok' else 'N') for v in pid[1:]])

G = [
('Accidents','ok','ok','ok','N','N','N','N'),
('Fatalities','ok','ok','ok','N','N','N','N'),
('Injured (<=2022 state; all-year India)','ok','ok','part','N','N','N','N'),
('Severity per 100 acc','ok','ok','ok','N','N','N','N'),
('Population projected','ok','ok','ok','N','N','N','N'),
('Road length','N','N','ok','N','N','N','N'),
('Vehicles registered','ok','N','N','N','N','N','N'),
('Violation/Collision/Road-user/Licence/Safety','ok','N','N','N','part','N','N'),
('Cities','N','N','N','N','ok','N','N'),
('Weather rain/temp','N','ok','ok','N','N','N','N'),
('Month/Day/Hour/Coords/District/Driver-detail','N','N','N','N','N','N','N'),
]
with open(f'{OUT}/GEOGRAPHY_PARAMETER_MATRIX.csv','w',newline='',encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['Parameter','India','Zone','State_UT','District','City','Police','Coordinates'])
    for r in G:
        w.writerow([r[0]]+[('✓' if v=='ok' else ('~' if v=='part' else 'N')) for v in r[1:]])

I = [
('Accidents','Population projected','State+Year','ok','ok','ok','counts vs 000','sum-vs-published rounding only','none','YES','Phase 2D join; 5 SUM/MEDIUM rows flagged'),
('Accidents','Road length','State+Year','2021-22 only','ok','Total km','-','4 UNRESOLVED JK/Ladakh cells','YES (2021-22 only)','Outside 2021-22 is unsafe'),
('Accidents','Weather','State+Year','2018-24','34 entities','annual means','-','18 excluded rows','YES (matched only)','Excluded islands/legacy splits stay out'),
('Accidents','Registered vehicles','Year','India only','unit mismatch state','000 stock','state split absent','-','NO (state level)','India-level comparison descriptive only'),
('Accidents','City data','City+Year','city names','city','counts','state-city nesting','-','NO (as join)','Separate city analysis only'),
('Accidents','NCRB variables','-','different definitions/totals','-','-','-','YES as separate source only','Never merge silently; label source'),
('State injuries 2023-24','India injuries','-','no allocation key','-','-','missingness','NO','UNSAFE: would fabricate state values'),
('Monthly accidents','Annual totals','-','no month split key','-','-','-','NO','UNSAFE: would invent monthly values'),
]
with open(f'{OUT}/INTEGRATION_COMPATIBILITY.csv','w',newline='',encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['Dataset_A','Dataset_B','Join_Key','Time_Compat','Geo_Compat','Unit_Compat','Definition_Compat','Risk','Safe_To_Join','Reason'])
    w.writerows(I)

P = [
('India consolidated yearly trend','READY','254 state-years aggregate; 2018-2024'),
('State-wise yearly trend','READY','Full panel'),
('Individual state graphs','READY','G9 pattern'),
('All-state consolidated graph','READY','G8 pattern'),
('Regression/trend lines','READY','Phase 4 slopes + CI + FDR'),
('Slope comparison','READY','34 slopes, 9 FDR-robust; no ranking'),
('Growth/change rate','READY','YoY tables'),
('Time-to-threshold analysis','PARTIALLY READY','Descriptive only; no forecasting license'),
('Multiple regression algorithms','READY','Phase 5 comparison incl. naive baseline'),
('Supervised regression','READY','N=175 lag-only; naive wins'),
('KNN','PARTIALLY READY','Supervised use only; small-N limits'),
('Unsupervised analysis','DATA REQUIRED','No suitable unlabeled feature set justified'),
('Weather','READY','236 matched; observational only'),
('Seasonality','DATA REQUIRED','Needs NCRB month extraction (PDF-only)'),
('Severity','READY','Phase 9 complete'),
('Cause/violation','READY','India-level 2023-24 only'),
('Road-user fatalities','READY','India-level 2023-24 only'),
('Collision type','READY','India-level 2023-24 only'),
('Exposure','PARTIALLY READY','Pop full; road 2021-22; vehicles India-only'),
('Safety devices','READY','India 2024 counts'),
('Licence status','READY','India 2020-24 accidents'),
('Million-plus cities','READY','50 cities 2023-24'),
]
with open(f'{OUT}/PROFESSOR_REQUIREMENTS_MATRIX.csv','w',newline='',encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['Requirement','Readiness','Evidence'])
    w.writerows(P)

from collections import Counter
c = Counter(r[3] for r in R)
print('total params:', len(R))
print(dict(c))
print('files written to', OUT)
