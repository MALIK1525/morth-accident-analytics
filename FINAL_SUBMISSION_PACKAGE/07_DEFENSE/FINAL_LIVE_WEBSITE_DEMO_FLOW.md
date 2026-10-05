# FINAL — Live Website Demo Flow (professor demo, ~10 minutes)

## Before the demo
- Open `https://morth-accident-analytics.onrender.com/` (if cold, wait ~60 s and refresh).
- Hard-refresh (Ctrl+Shift+R) so the latest bundle loads.
- Keep this file open on a second screen.

## STEP 1 — Research Dashboard (4 min)
1. Point to the **VERIFIED RESEARCH DATA · MoRTH 2018–2024** badge: frozen benchmark.
2. Scroll G1 (India trend, area+line) → G6 zone trajectories (each zone has its own
   marker + line dash — print-safe) → G9 state trajectories.
3. Open Audit tab: reconciliation shows MATCH, zero mismatches.
4. Say: "Observational analysis — association, not causation; counts are not risk."

## STEP 2 — Live Monitor (3 min)
1. Click **🔴 LIVE Monitor** (header). Note the **LIVE EXTERNAL DATA** badge.
2. Map: toggle Weather / Traffic / Incidents layers; click a city marker → detail panel.
3. Point to source badges (Open-Meteo LIVE; TomTom awaiting-key if no key set).
4. Hazards panel: derived only from loaded feeds.

## STEP 3 — Government Data Watch (2 min)
1. Scroll to **Government Data Watch** → Scan Now (or show cached scan).
2. Show NEW/KNOWN cards, vintage badges (NCRB never-merge warning), exposure flags.
3. Emphasize: "DISCOVERED ≠ VERIFIED — nothing auto-enters the benchmark."

## STEP 4 — Integrity + limitations (1 min)
1. "Live and research never mix — tested automatically (130+ tests)."
2. Limitations: no public live accident feed; city-proxy weather; NCRB blocked;
   TomTom needs a key; watch history ephemeral on free tier.

## If something fails live
- Weather red → "provider outage; cached timestamp shown, research unaffected."
- Traffic awaiting-key → expected without key; weather still works.
- Never claim a failed layer as data.
