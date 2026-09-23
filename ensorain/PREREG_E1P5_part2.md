# ENSORAIN E1.5 -- preregistration part 2 (constants only)

Currency: 2026-09-23. Committed after the TT_LATENT calibration (dev seeds
300-305) and BEFORE tuning (seeds 3000+) or any confirmatory run (sets
A/B). Part 1 (bde3f4237) unchanged.

TT_LATENT constants (own calibration, never inherited; objective median
held-out R^2 on dev; rows ensorain/runs/e1p5_calibrate.jsonl; frozen in
ensorain/runs/e1p5_latent_constants.json):
  128: lam 100, sweeps 10 (dev R^2_ho 0.48; ranks shrunk below truth)
  160: lam 30,  sweeps 10 (0.60; ranks shrunk below truth)
  192..512: lam 30, sweeps 20 (0.97). At every cap >= 192 TT_LATENT has
  the SAME architecture (true ranks 3,3,3 = 192 floats): only its
  constants could differ, and they do not.

DEV OBSERVATION, recorded before tuning, not evidence: with the latent
order known, a TT at EXACTLY 192 floats learns the held-out region to R^2
0.97. E1's TT_LATENT@384 success (R^2 0.98) and TT_LATENT@192 failure
(0.48) used the SAME 192-float architecture and differed only in
inherited constants (10 vs 2 sweeps). The "headroom" seen for the
latent-order control in E1 was a constants artifact. Whether the
ORDER-SEARCHING TT_TUNED needs headroom is what the sweep now tests.

Tuning, economy, compute, tolerance: exactly as part 1 s1-s2.
