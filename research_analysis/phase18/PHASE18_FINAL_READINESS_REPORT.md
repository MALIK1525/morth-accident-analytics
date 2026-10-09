# PHASE 18 — Final Readiness Report

## Manual browser QA results
Headed browser unavailable in this environment: all interactive items
(map fit/hover/click/search/reset, markers, chips, denial flow, responsive
widths, console) recorded as NOT TESTED (honest). Structural + API + unit
coverage passes; human pre-demo run of PHASE17_BROWSER_QA_CHECKLIST.md required.

## Weather failure diagnostics (evidence)
- Local: Open-Meteo healthy (200, current data, ~ms latency).
- Render: persistent failure across 3 checks / 60+ min, all 10 cities.
- New failure classifier reported: `HTTPError 429 Too Many Requests`.
- Root cause: per-IP rate limiting on Render's shared egress — our old code
  sent 10 sequential requests/scan (plus retries), amplifying the shared
  quota pressure. Not DNS/TLS/blocking, not our payload.
- Fix deployed in this phase: single batched request per scan (10 cities, 1
  call; ~288 calls/day, far under the 10k/day limit) + existing retry/stale
  badge retained. Verified working from here; production recovery pending
  redeploy + next scan (shared-IP pressure may still occasionally 429; the
  STALE path now covers that truthfully).

## Option comparison (no paid service added)
- A. Keep Open-Meteo (batched): free, no key, verified working, CC-BY.
  RECOMMENDATION — adopted. Risk: shared-IP 429s recur; mitigated by
  1-call scans + stale fallback.
- B. Key-based alternative (e.g. WeatherAPI.com free 1M calls/mo): reliable
  but needs user signup + server key. Only if A proves unstable. NOT implemented.
- C. Move hosting: unjustified — limitation is provider rate policy, not
  Render-specific breakage; migration cost exceeds benefit. NOT recommended.

## Post-deploy outcome (recorded, not predicted)
After deploying the single-call batch fix, production still returns HTTP 429
(classified live at 20:48 IST). Conclusion: the shared Render egress IP itself
is over Open-Meteo's per-IP quota regardless of our volume — no further
code-side reduction is possible. Standing recommendation: Option A (honest
STALE/UNAVAILABLE states) unless the user approves Option B (key-based provider).
## Tests: 163/163. Deployment: verify below.
## Unresolved: production weather recovery unconfirmed until post-deploy scan;
browser QA manual; TomTom/data.gov.in keys absent (by design, awaiting user).
## Recommendation: demo with research map + Data Watch as centrepiece; weather
as supporting layer with honest STALE/UNAVAILABLE states if shown.
