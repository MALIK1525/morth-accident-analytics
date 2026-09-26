# PHASE 2 — EXPOSURE REPORT (re-runnable: `python phase2_exposure_analysis.py`)

MoRTH panel re-verified: 38 entities, 254 obs, India benchmarks reconcile exactly.
`phase2_raw/` contains 0 files — direct MoRTH PDF download returned an SPA shell (blocked);
data.gov.in RTYB group page is JS-only with no extractable resource links. Sources identified, none yet extracted.

## Identified sources (not yet acquired — DO NOT treat as data)
- Population: RGI Technical Group on Population Projections 2011–2036 (MoHFW, July 2020), Tables 8/11/14 (state × year, 1 March/1 July/1 Oct). Projections, not census counts — must be labeled as such. URL: https://mohfw.gov.in/sites/default/files/Population%20Projection%20Report%202011-2036%20-%20upload_compressed_0.pdf
- Vehicles: MoRTH Road Transport Year Book, Annex Tables 3.1/3.2 (state-wise registered vehicles, annual). Note: cumulative registers include scrapped/unrenewed vehicles in some states — not a traffic-flow measure.
- Road length: MoRTH Basic Road Statistics (state-wise total/surfaced length, annual). Note: surfaced/unsurfaced mix varies by edition — edition consistency required.

## Geography compatibility (summary; full matrix in EXPOSURE_GEOGRAPHY_COMPATIBILITY.md)
- MoRTH: 38 rows incl. DNH (N=2 legacy) + Diu (N=2 legacy) + merged DNH-DD (N=5); Ladakh 2018 accidents=0 kept as-is.
- RGI projections use undivided J&K pre-2019 and separate DNH/Diu — year-aware mapping required; Ladakh 2018 join excluded.
- No blind state-name merge permitted. No join attempted (no denominator files).

## Normalized measures / correlations / regressions / within-state / panel
NOT COMPUTED — no verified denominator joined. Workbook shells + exact column schemas ready
(`Acc_per_100k_pop`, `Acc_per_10k_veh`, `Acc_per_1000km`, ...). Pooled-vs-within-state design and
fixed-effects assessment specified in report §9/11/14 but not estimated until denominators arrive.

## 2020 / injuries
2020 retained as structurally unusual (Phase 1 split trends stand). State injury normalization
limited to 2018–2022 when denominators arrive; 2023/24 state injuries never estimated.

## Interpretation
No geographical-normalization conclusion can be drawn yet. No causal language used.
