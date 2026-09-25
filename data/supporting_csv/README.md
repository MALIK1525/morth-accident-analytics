# Supporting CSV drop-in folder

Place MoRTH Annual Report 2024 derived CSVs here (exact filenames expected):

- `03_road_accidents_2024_type_of_collision.csv` → unlocks CL-01
- `04_road_accidents_2024_type_of_violation.csv` → unlocks CS-01
- `05_road_accidents_2024_type_of_license.csv` → unlocks DL-01
- `06_road_accidents_2024_safety_device.csv` → unlocks SD-01
- `07_road_accidents_2024_fatality_road_user.csv` → unlocks VH-01
- `08_road_accidents_2024_victims_crime_vehicle.csv` → unlocks VH-02 (table)
- `11_road_accidents_2024_cities_accidents_fatalities.csv` → unlocks CT-01
- `12_road_accidents_2024_cities_fatalities_mode.csv` → unlocks CT-02 (table)
- `13_road_accidents_2024_cities_fatalities_traffic_violation.csv` → unlocks CT-03 (table)
- `14_road_accidents_registrations_density_2014_24.csv` → unlocks EX-01
- `02_road_accidents_annual_2020_2024.csv` → annual cross-check

Rules (enforced by `app/data_pipeline/supporting_loader.py`):
- Indian comma numbers (`4,87,707`), BOM, `% share` annotation rows,
  `NA` / `(P)` provisional markers are handled automatically.
- `% share` rows are never treated as data.
- Missing values stay missing (never zero-filled).
- India totals are cross-checked against MoRTH benchmarks where applicable.
- Unrecognised files are listed, never visualised.

No fabricated data is accepted: charts activate only from real files placed here.
