# Phase 5 vehicle-exposure finding (state split NOT acquired)

## Candidate investigated
- OGD data.gov.in: "States/UTs-wise Total Registered Motor Vehicles 2010-2020" (RTYB 2019-20 catalog, Tier 1).
  Page confirmed live; direct CSV behind JS-render/API-key wall; api.data.gov.in SSL-timeout from here.
- RTYB 2019-20 PDF (morth.nic.in old deep link): dead (returns SPA shell, 41 KB HTML). morth.nic.in
  year-book pages render no direct PDF links (JS-driven).
- Dataful/Vahan state-maker datasets (2020/2023/2024/2025): annual REGISTRATIONS (flow), not stock.
  Rejected as stock denominator (would misstate exposure).

## Outcome
State-level registered-vehicle STOCK 2018-2024: still DISCOVERED, not acquired.
India-level stock stands via EX-01 (2014-2022, 2023-24 NA).

## Formulas reserved for later (design only, NOT computed)
- Accidents per 10,000 registered vehicles = Accidents / Registered_Vehicles x 10000
- Fatalities per 10,000 registered vehicles = Fatalities / Registered_Vehicles x 10000
- Preconditions: state-matched vintage, stock (not flow) definition, dead-vehicle caveat recorded.

## Next acquisition step
Manual browser download from data.gov.in resource page, or RTYB PDF Tables 3.1/3.2 via
current morth.gov.in documents library.
