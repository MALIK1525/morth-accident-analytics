# PHASE 13.4 — Government Data Watch Report

## Sources & endpoints
| Source | Mechanism | Auth | Status (verified live Oct 2026) |
|---|---|---|---|
| OpenCity CKAN | `GET data.opencity.in/api/3/action/package_search?q=…&rows=20` (6 keyword queries) | None (open) | WORKING — 55 datasets returned on first live scan |
| data.gov.in | `GET api.data.gov.in/catalogs` | `DATA_GOV_IN_API_KEY` env | Honest `awaiting_key` without key; attempted only when key present |
| MoRTH | Content-hash watch of `morth.nic.in/en/road-accident-in-india` | None | WORKING — fetched + hashed on first live scan |
| NCRB ADSI | Content-hash watch of `ncrb.gov.in/en/accidental-deaths-suicides-india-adsi` | None | Page blocks automated fetch → honest `SOURCE_UNAVAILABLE`, manual-review card |
| PIB | No verified machine feed | n/a | Manual-check card with link |

## Scan frequency & caching
- Browser "Scan Now" → `/api/live/watch/scan`; server scan cache 10 min; full
  source re-scan interval 6 h (`SCAN_TTL_S`); page/CKAN history persisted in
  `research_watch/scan_history.json` (runtime state, git-ignored).

## Classification logic
- NEW (id never seen) / UPDATED (CKAN `metadata_modified` changed or page hash
  changed) / KNOWN / SOURCE_UNAVAILABLE / MANUAL_REVIEW (PIB).
- Relevance: keyword hit → RELEVANT else NOT_RELEVANT.
- Vintage from text (MoRTH/NCRB/IMD/OTHER); NCRB items carry an explicit
  never-merge-with-MoRTH warning.
- Exposure: vehicle keywords → EXPOSURE_CANDIDATE; flow-like wording flagged
  "FLOW — must NOT substitute for stock".

## Compatibility logic
Metadata-level guess only (geography/time/measures/vintage + definition note).
Every card states definitions must be verified before any use.

## Safety rules (enforced by tests)
- Watch code contains no research/benchmark write paths (static test).
- Review downloads land ONLY in `research_watch/review_queue/` (32 MB cap,
  http/https only, path-traversal rejected).
- No auto-integration surface exists in routes (static test).
- New ≠ verified · incident ≠ accident record · NCRB ≠ MoRTH · flow ≠ stock.

## Failure handling
Per-source try/except: CKAN partial-query failures reported, not fatal; page
404/timeout → SOURCE_UNAVAILABLE card; data.gov.in without key → awaiting_key
(no hammering); scan endpoint 502 only if the whole scan crashes.

## Test results
22 new tests (`tests/test_data_watch.py`): discovery, dedup, update detection,
classification, vintage separation, geography, stock/flow, review-queue
containment, protected paths, key handling, timeout/429/malformed/unavailable,
no-integration surface, freshness, filters, watch UI, PIB card. Full suite: 118/118.

## Known limitations
- NCRB page blocks bots → manual checks needed until an accessible feed exists.
- PIB has no verified feed → manual card only.
- data.gov.in needs a user-supplied key.
- CKAN relevance is keyword-based; human review required (by design).
- History file is local/ephemeral on Render free tier (first scan = all NEW).
