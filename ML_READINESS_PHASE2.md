# ML READINESS — PHASE 2 UPDATE (no training performed)

| Feature | Source | Coverage | Level | Missingness | Leakage risk | Suitable? |
|---|---|---|---|---|---|---|
| Year | MoRTH panel | 2018–2024 | state-year | 0 | none (known at prediction time) | YES |
| State / Zone | MoRTH panel + mapping | 2018–2024 | state | 0 | none | YES (encode carefully) |
| Accidents lagged (t−1) | MoRTH panel | 2019–2024 derivable | state-year | first year per state | none if strictly lagged | YES |
| Fatalities lagged (t−1) | MoRTH panel | 2019–2024 derivable | state-year | first year per state | none if strictly lagged | YES |
| Injured lagged | MoRTH panel | 2019–2022 derivable | state-year | 2023/24 + UT gaps | none if strictly lagged | PARTIAL (2018–2022 window) |
| Population | NOT ACQUIRED (RGI projections identified) | — | — | 100% | low (projections published ex-ante) but vintage must predate target year | PENDING FILE |
| Registered vehicles | NOT ACQUIRED (RTYB identified) | — | — | 100% | CAUTION: yearbook published with lag — verify release date precedes target year | PENDING FILE |
| Road length | NOT ACQUIRED (BRSI identified) | — | — | 100% | CAUTION: same publication-lag check | PENDING FILE |

Target candidate unchanged: annual state accident count. Design constraints: chronological split,
naive previous-year baseline mandatory, no future-year/target leakage, N≈213 usable rows.
KNN = supervised; K-Means = unsupervised.
