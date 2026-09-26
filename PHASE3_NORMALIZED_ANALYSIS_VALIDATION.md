# PHASE 3 — VALIDATION

| Check | Result |
|---|---|
| Duplicate State-Year keys | 0 PASS |
| Negative population / accidents / fatalities | 0 PASS |
| Zero/invalid denominators | 0 (all pop > 0; road > 0) PASS |
| Unit conversion (persons = thousands×1000) | exact PASS |
| Projection flag retained | True on all 254 PASS |
| Road years restricted to 2021–2022 | yes PASS |
| 4 UNRESOLVED road cells excluded from usable set | yes (68 usable) PASS |
| Vehicle fields | absent PASS |
| Population usable set complete | 254/254 PASS |
| Injury values fabricated | none (179 valid, rest NaN) PASS |
| Road values outside 2021–2022 | none PASS |
| India totals consistent with MoRTH benchmarks | TRUE PASS |
| Neutral language (no best/worst/caused) | verified in outputs PASS |
