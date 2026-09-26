# EXPOSURE GEOGRAPHY COMPATIBILITY

| Source | Year | Entity structure | Compatible with MoRTH? | Required transformation | Potential issue | Decision |
|---|---|---|---|---|---|---|
| MoRTH panel (Dataset_3) | 2018–2024 | 38 rows: DNH legacy (2y) + Diu legacy (2y) + merged DNH-DD (5y); Ladakh from 2019 (2018 acc=0) | reference | none | legacy rows have N<7 | USE AS-IS |
| RGI/MoHFW projections 2011–2036 | 2018–2024 slice | Undivided J&K pre-2019; separate DNH, Diu; no Ladakh pre-2019 | NO (direct) | Year-aware map: split J&K→J&K+Ladakh from 2019; merge DNH+Diu→DNH-DD from 2020; exclude Ladakh-2018 | Projection (not count); 1 Mar vs 1 Jul vs 1 Oct vintages | MAP THEN JOIN (pending file) |
| MoRTH RTYB vehicle register | annual 31 Mar | State/UT incl. merged UTs per edition | PARTIAL | Edition-aware entity map per year | Cumulative register incl. dead vehicles; edition entity changes | MAP PER EDITION (pending file) |
| MoRTH Basic Road Statistics | annual 31 Mar | State/UT per edition | PARTIAL | Edition-aware entity map per year | Surfaced/unsurfaced mix; edition changes | MAP PER EDITION (pending file) |

Rule: no blind state-name merge. Every join must pass this matrix row first.
