# PHASE 2B — EXTRACTION VALIDATION

## Population (Table 11)
| Check | Result |
|---|---|
| Source rows expected | 38 × 7 = 266 |
| Extracted | 266 |
| Duplicates | 0 |
| Missing | 0 |
| Invalid numerics | 0 |
| India reconciliation (computed vs published, '000) | 2018 −1; 2019 −3; 2020 +7; 2021 +2; 2022 −1; 2023 0; 2024 +1 → PASS (rounding only) |
| Unit | '000 persons, preserved |

## Road length (Annex 1.1.2 / 2.1.2)
| Check | Result |
|---|---|
| Source rows expected | 37 × 2 = 74 |
| Extracted | 74 |
| Duplicates | 0 |
| 2021 computed vs published Total* | 5,598,284 vs 5,598,284 → diff 0 PASS |
| 2022 computed vs published Total* | 5,692,801 vs 5,692,801 → diff 0 PASS |
| 2021 surfaced | 4,070,190 (matches); 2022 surfaced 4,138,472 (matches) |
| Stale footnotes in extracted rows | none observed |

## Originals preservation
- RGI PDF hash unchanged: bf867a34…0e8417 ✓
- BRSI PDF hash unchanged: 3288df12…242fda73 ✓

## Unresolved (NOT guessed)
M+F rounding; BRSI J&K/Ladakh double-count check; DNH/Diu→merged join rule; road coverage 2 of 7 years; vehicles absent.
