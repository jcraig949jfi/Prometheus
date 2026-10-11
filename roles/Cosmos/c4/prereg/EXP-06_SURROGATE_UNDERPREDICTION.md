# EXP-06 -- INSTRUMENT QUALIFICATION: why does the EXP-04 surrogate underpredict? (prereg 2026-10-11, before data)

Origin: EXP-04 (results/EXP-04_RESULT.md): the nonlinear one-step surrogate underpredicted B excess in every family
and every k (e.g. sediment k=2 .28 vs .67); its 10-08 planted check had already shown underprediction on
high-memory reservoirs. This is an INSTRUMENT question on PLANTED systems only (no family data, no labels reused).

Systems (planted, linear-Gaussian, known truth): planted.Reservoir a in {.5, .7, .85, .95} x sigma in {.1, .3} x
wseed in {1, 2} (16) and planted.RotReservoir a in {.7, .85, .95} x sigma .3 x wseed {1, 2} (6); k in {2, 4, 8}
-> 66 (system, k) cells. Actual = Certificate B linear accuracy. Excess = (acc - .25) / .75.

Variants (all else frozen; defaults reproduce EXP-04 bit-for-bit, checked):
  V0 frozen instrument;  V1 composition noise_scale 0 (is the fitted residual noise too large?);
  V2 no clip to the stationary range;  V3 ridge 1e-4 (is the one-step fit over-regularised?);
  V4 n_train 16384 (is it sample size?).
Metric per variant: median |pred excess - actual excess| (MAE) and median signed error (SE) over the 66 cells.

Decisions fixed now:
- V0 underprediction CONFIRMED on planted systems if V0 SE < -.05. If not confirmed, the EXP-04 underprediction is
  NOT an instrument property visible on linear systems -> recorded; no cause is assigned.
- A variant IDENTIFIES a cause if its MAE <= .5 x V0 MAE AND |its SE| <= .05. Several may qualify; all are reported.
- V1 qualifying would mean the residual covariance is inflated by model misfit (noise where there should be
  dynamics). V1 overpredicting (SE > +.05) means real noise matters and is NOT the cause.
- No variant qualifies -> INSTRUMENT_DEFECT UNEXPLAINED; the surrogate stays unqualified for cross-family use.
- Whatever the outcome: no EXP-04 rescoring. An adopted fix is a NEW instrument version, requalified on fresh
  worlds before any use.
