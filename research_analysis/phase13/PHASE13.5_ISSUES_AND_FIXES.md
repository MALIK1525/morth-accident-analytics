# PHASE 13.5 — Issues Found and Fixes

1. `renderChartById` refactor orphaned the main dispatch — FIXED (shared dispatcher,
   fallback renders identically). Found by code review; verified via tests.
2. Test `FakeResp.read()` missing size arg vs 32 MB cap read — FIXED in test double.
3. Test read HTML with wrong encoding (emoji) — FIXED (utf-8).
4. Frontend "awaiting key" text contained env var name — reworded to neutral
   server-configuration message (defense in depth; name is not secret).
5. Secret-guard test over-matched docstring mentions — rewritten to detect only
   assigned literal values.
6. `.gitignore` had a UTF-16LE-encoded appended line (from an earlier PowerShell
   `echo >>`), making git treat it as binary — rebuilt as clean ASCII; pattern
   `research_watch/scan_history.json` now effective (verified with `git check-ignore`).
7. NCRB page blocks automated fetch — NOT fixable without bypassing (refused);
   honest SOURCE_UNAVAILABLE + manual-review card instead.
8. No headed browser in this environment — visual/screenshot QA impossible;
   recorded as PARTIAL with structural checks instead. No screenshots fabricated.

No research data, statistics, ML outputs, or conclusions were touched at any point.
