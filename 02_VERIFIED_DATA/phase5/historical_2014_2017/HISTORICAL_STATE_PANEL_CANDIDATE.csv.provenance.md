# Provenance - AR2014/2015/2016/2017 PDFs + HISTORICAL_STATE_PANEL_CANDIDATE.csv
- Source_Organization: Ministry of Road Transport and Highways (MoRTH), Government of India
- Reports: Road Accidents in India 2014 / 2015 / 2016 / 2017 (official PDFs)
- Original_Publisher: morth.gov.in / morth.nic.in
- Mirror_URL: https://data.opencity.in/dataset/road-accidents-in-india (OpenCity CKAN; file sizes match CKAN metadata: 2794594 / 8279522 / 7475522 / 9232314 bytes)
- Candidate_Extract: AR2017 Annexure-2 (p58, accidents), Annexure-3 (p59, killed), Annexure-4 (p60, injured); single-vintage extraction (cols 2014/2015/2016/2017); share/rate columns ignored
- Geography: Telangana separate all years; Jammu & Kashmir undivided (no Ladakh); Dadra & Nagar Haveli and Daman & Diu separate. Footnote: Telangana population NA (included in Andhra Pradesh) - exposure joins need care.
- Validation: state sums == published India totals EXACTLY for all 4 years x 3 variables:
  2014: 489400 / 139671 / 493474; 2015: 501423 / 146133 / 500279;
  2016: 480652 / 150785 / 494624; 2017: 464910 / 147913 / 470975. Result: MATCH x12.
- Vintage_Note: AR2017-vintage values adopted; AR2016-vintage cross-check NOT PERFORMED (p63 text layout splinters rows; unreliable with available tooling). No header/total mismatch in adopted vintage.
- Compatibility: CONDITIONAL - harmonizable to 2018-2024 panel only with documented J&K split handling and DNH/Diu merge handling; NOT merged into benchmark.
- Status: VERIFIED-MIRROR (candidate dataset; production integration explicitly excluded)
