# Provenance - HARMONIZED_PANEL_2014_2024_CANDIDATE.csv (396 rows)
- Inputs: 02_VERIFIED_DATA/phase5/.../HISTORICAL_STATE_PANEL_CANDIDATE.csv (AR2017 vintage, 2014-17)
  + data/MoRTH_Primary_Dataset_3.xlsx CLEAN (benchmark revised vintage, 2018-24)
- Harmonization rules:
  - 34 stable entities + Telangana: DIRECT all years.
  - Jammu & Kashmir 2014-2019: JK_UNDIVIDED (pre-reorg administrative definition, incl. Ladakh region).
    2020+ J&K UT: JK_UT_BREAK (series break at 2019->2020, values not comparable across break).
  - Ladakh: NV_SOURCE 2018-2020 (as in benchmark); values 2021-2024 (LADAKH_START_2021).
  - DNH & Daman & Diu: SUM_HISTORICAL arithmetic sums 2014-2019 (MEDIUM, mirrors Phase 2C);
    DIRECT_MERGED 2020+; legacy split rows retained with LEGACY_SPLIT flag (excluded from totals).
- Validation: harmonized India sums == published totals for all 11 years (acc/fat exact;
  inj exact except 2023-24 state-N/A by design). 2017->2018 continuity: acc +1.2%, fat +6.6%,
  inj -1.3% (no vintage cliff).
- 2019 vintage: AR2017 vintage (2014-17) documented separately from benchmark revised vintage;
  no mixing within any year.
- Status: VERIFIED CANDIDATE. Production integration explicitly excluded; benchmark untouched.
