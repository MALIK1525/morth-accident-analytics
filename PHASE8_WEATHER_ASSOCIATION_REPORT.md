# PHASE 8 — Weather–Accident Association Report (observational; no causal claims)

## 1–5. Objective, data, population
Question: how do validated IMD rainfall/Tmax/Tmin relate to MoRTH accidents/fatalities across states, 2018–2024?
Analytical N=**236** matched state-years (34 entities × 7 y minus exclusions); 18 excluded (Andaman 7 masked, Lakshadweep 7 masked, legacy DNH/Diu 4 unreconstructible). Population denominators from Phase 2D (projected). No imputation.

## 6. Descriptives — see phase8_weather_descriptive.csv.

## 7/10. Pooled associations (N=236, all survive BH-FDR per family)
- Rainfall vs Accidents r=-0.234 (p 2.9e-4); vs Fatalities r=-0.376 (p 2.5e-9). Spearman -0.343/-0.393.
- Tmax vs Accidents r=+0.452 (p 2.7e-13); vs Fatalities +0.498. Tmin +0.366/+0.340.
- Normalized: rainfall vs Acc/lakh +0.275 but vs Fat/lakh -0.181 (sign flip — scale confounding, see §8); Tmax vs Fat/lakh +0.348; Tmin vs Fat/lakh +0.268.
- WARNING: pooled values mix between-state scale/geography with weather; must not be read as within-state effects.

## 8. Within-state (408 valid state-level tests, N≤7, low power)
- Rainfall–accidents negative in **73.5%** of states; Tmax–accidents positive in **88.2%** — directionally consistent with pooled, but per-state estimates are noisy. No state ranking. Full table: phase8_within_state_associations.csv.

## 9. Fixed effects (within-estimator, SEs unclustered, descriptive)
- Accidents on rainfall: -1.21/yr per mm (p 0.020); on Tmax: +948 (p 0.0035); on Tmin: +742 (p 0.075, insufficient evidence).
- Fatalities on Tmin: +459 (p 1.3e-4); on Tmax +234 (p 0.014); on rainfall -0.16 (p 0.28, insufficient evidence).
- Normalized outcomes show the same pattern at smaller scale. Observational — not causal identification.

## 10. 2020 sensitivity
Excluding 2020 changes no direction and barely moves magnitudes (max |Δr|=0.033, tag J). Associations are not 2020-driven.

## 11. FDR
BH per family (Rainfall/Tmax/Tmin): all 12 pooled associations remain significant after adjustment.

## 13. Monthly
Monthly weather–accident association NOT AVAILABLE FROM VERIFIED DATA (MoRTH panel is annual; monthly accidents must not be inferred).

## 14. Nonlinearity
Not pursued beyond Spearman (rank) agreement with Pearson direction in all 12 pairs; no curvature analysis forced on N=236 pooled data.

## 17–19. Non-findings & limitations
- No evidence on humidity/visibility/fog/wind (unavailable). No causal interpretation licensed. Equal-cell weighting (sensitivity ≤0.6%). Projected population. No vehicles. 2020 retained throughout. Small per-state N.
- Cross-check note: independent re-aggregation reproduced committed Phase 7 rainfall within ~26 mm mean abs diff; Lakshadweep cell-count differs (16 all-masked vs 0 found) with identical analytical outcome (excluded).

## Conclusion
Detectable pooled associations (wetter↔fewer, hotter↔more) survive FDR and 2020-exclusion and are directionally echoed within states, but between-state scale confounding and low within-state power mean these are associations only — insufficient evidence for any causal or predictive claim.
