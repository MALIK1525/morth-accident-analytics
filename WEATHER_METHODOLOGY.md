# Weather Methodology (specified, NOT yet active)

## Status
No IMD/grid files exist in this workspace; project audit marks IMD sources NOT ACQUIRED.
The Weather tab therefore shows an honest unavailable state. No weather values are
 synthesised anywhere in the app.

## Required pipeline (to activate)
1. Acquire IMD 0.25° gridded daily rainfall NetCDF (LND-{year}.nc) and/or DSP station CSVs.
2. Spatial overlay against official State/UT boundaries (note J&K/Ladakh split 2019,
   DNH+Daman&Diu merger 2020, small-UT grid-cell coverage).
3. Aggregate grid → State/UT → daily → monthly → annual (rainfall total, rainy days,
   Tmax/Tmin means). Only variables present in source files.
4. Validate join on (State_UT, Year) against the MoRTH panel; record boundary/CRS/method.
5. Produce STATE_WEATHER_ANNUAL_2018_2024 (+MONTHLY) into `data/supporting_csv/`
   with full provenance row, then extend `supporting_loader.py` with a weather schema.

## Analysis rules once joined
Association only (scatter, correlation with N/p-values); never "weather caused crashes".
Annual accidents must never be distributed into months.
Humidity/visibility/wind/fog stay unavailable unless real data arrives.
