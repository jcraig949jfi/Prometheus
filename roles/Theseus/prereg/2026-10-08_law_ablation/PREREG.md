# THESEUS-28 preregistration -- does the generated k-ary law erode structure with depth?

Currency: 2026-10-08. Committed before the run. Code: theseus/synth/collide.py
(law flag) and run_v0.py (--no-law, --ecology-only); blob ids in CODE_SHA256.txt.
One smoke run (7 generations) proved the path (0 law rules in any child); its
outputs were deleted; only row counts were read.

## Why

Post-hoc R5 (THESEUS-23a, 8814bb4b0): deep descendants carry LESS graded causal
structure than one-shot collisions (AUC .438 [.404, .472]). One candidate cause:
every collision inserts a freshly generated k-ary react law with random gains,
i.e. each generation adds random wiring. If so, removing the law should remove
the erosion.

## Design

- ON  = run v0_1_2026-09-30 (committed rows; law inserted; PYTHONHASHSEED=0).
- OFF = PYTHONHASHSEED=0 python -m theseus.synth.run_v0 --tag v0_1_nolaw_2026-10-08
        --no-law --ecology-only --workers 4. Same master seed and config; the law is
        still generated (identical RNG draws) but not inserted.
- Rows: viable ecology children; R5 = share of the 22 intervention responses in
  (0.05, 0.9) from the stored fingerprint (frozen definition, 23a).
- Statistics, computed identically for ON and OFF:
  rho      = Spearman(generation, R5) over viable DEEP + VERY_DEEP children
  medD     = median R5 of viable DEEP + VERY_DEEP children
  bootstrap (1000) CIs for rho_OFF - rho_ON and medD_OFF - medD_ON.

## Decision rule

- LAW-ERODES (supported): rho_ON < 0 with CI below 0, AND rho_OFF - rho_ON > 0
  with CI above 0.
- LAW-NOT-THE-CAUSE: rho_OFF - rho_ON CI contains 0 or lies below 0.
- NO-EROSION-TO-EXPLAIN: rho_ON CI contains 0 (the post-hoc arm difference is
  not a within-lineage trend), whatever OFF does.
- Report viable fraction and max generation reached for both runs.

## Predictions

L1 rho_ON is negative with CI below 0.                       p = 0.5
L2 LAW-ERODES is supported.                                  p = 0.35
L3 OFF has a higher viable fraction than ON.                 p = 0.5

Compute: ecology only, ~20 min wall, ~1.2 CPU-hours (MWO R2).
