# PHASE 6 — WEATHER VALIDATION REPORT

## Outcome: data VERIFIED, integration PENDING boundaries (between Outcome A and B: acquire+verify succeeded, join deferred)

Acquired 21 official IMD Pune files (2018–2024): 7 daily rainfall NetCDF (0.25°, Pai et al. 2014 product, 135×129)
+ 7 Tmax + 7 Tmin GrADS binaries (1°, 31×31, 99.9 = missing). All hashes manifest-recorded.

## Validation
- Rainfall: day counts exact incl. leap 2020/2024 (366); 0 NaN; range 0–979 mm/day plausible; ocean cells unflagged 0.0 (land mask required).
- Temperature: byte-size shape verified (365/366×31×31 f32LE); 63% flagged (ocean/outside mask); valid Tmax 2.9–46.8°C, Tmin −6.9–32.1°C.
- Units: mm/day, °C — no conversion needed. Mean temp NOT derived yet.
- Humidity/visibility/fog/wind: NOT AVAILABLE FROM VERIFIED SOURCE. No proxies invented.

## Compatibility
- Temporal: FULL 2018–2024 daily. Geographic: grids cover all-India; state assignment UNRESOLVED (no verified boundary polygons in repo).
- Proposed aggregation: area-weighted state mean (documented, NOT executed). J&K/Ladakh + DNH-DD inherit Phase 2C crosswalk once polygons arrive.
- Join: NOT PERFORMED (correctly — boundary precondition unmet). No correlations, no ML, no causal claims, website untouched.
