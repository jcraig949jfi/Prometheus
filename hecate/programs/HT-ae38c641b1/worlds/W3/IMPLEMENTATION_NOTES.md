# HT-ae38c641b1 / W3 -- implementation notes (written before any run)

Prompt: hecate/programs/_prompts/probe_impl_v1.md (sha256 cf4bd374...cea2).
Bound by roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.

## Spec field -> code

- hypothesis / mechanism (M4): `world.py::analyzer()`. 2-D loop
  x <- r R_theta x + b, r = 0.9, analysed with box (interval) abstract
  interpretation. Abstract state = box [lo, hi]^2. Loop-head iterate:
  Y_k = X0 join F(X_k) join X_k (F = interval image of the affine map).
  For k < d the next iterate is Y_k (plain join); for k >= d the next
  iterate is X_k widen_T Y_k (threshold widening: a bound that grows is
  moved to the next threshold beyond it, or to +-inf if none). Ascent stops
  at the first post-fixpoint (Y_k subset of X_k). Then 2 narrowing steps
  X <- X meet (X0 join F(X)). Output W(theta) = width of the final box.
- intervention: rows for every (d, threshold set) in {1,3,6} x {13,50}
  (arm TREATMENT_VARIANT). The DEFAULT analyzer (d = 3, 13 thresholds, as
  in the mechanism text) is arm TREATMENT and is the one the success
  criterion is applied to ("for the default analyzer").
- control: arm CONTROL, W*(theta) = width of the axis-aligned hull of the
  concrete orbit x_0 = X0 point, 5000 points (x_0..x_4999).
- positive_control: arm POSITIVE_CONTROL, Cantor staircase (middle-thirds
  Cantor function, 40 ternary digits) sampled on exactly the same t grids;
  detected iff |beta - log2/log3| <= 0.05 for every seed.
- null_twin: arm NULL_TWIN. Kleene iteration X <- X join X0 join F(X) (no
  widening) until the max bound change < 1e-12, then outward rounding of
  each bound to the threshold set (lo -> largest threshold <= lo, hi ->
  smallest threshold >= hi, +-inf if none). Default 13-threshold set.
  Divergent or bound > 256 (monotone ascent, so rounding would give inf)
  -> inf. Iteration cap 20000; unconverged at cap -> inf (counted in rows).
- CHEAT: arm CHEAT, W = generalized Cantor staircase with base 4 keeping
  digits {0,3} (dimension log2/log4 = 0.5), same grids. It bypasses the
  analyzer entirely. Detected iff it meets the treatment-side success
  conditions (beta >= 0.2, R^2 >= 0.95, power AIC better than log and
  saturating by >= 10) for every seed.
- observable (L5): t grid on [0,1), theta = 2 pi t. Finest grid delta =
  2^-16 (65536 points, the spec's "up to 65536 theta values"), coarse
  grids are its dyadic subsamples. N(delta) = number of adjacent grid
  pairs (no wrap-around) with |dW| > 1e-9 * median(W). beta = OLS slope of
  log2 N vs log2(1/delta). AIC for three models fitted in log N space.
- success_criterion: see "Criterion as applied".
- failure_criterion: see "Criterion as applied".

## Ambiguities and the readings chosen

1. b, initial state: not given. b = (1, 0); X0 = the point (0,0) (box of
   zero width). Chosen as the simplest non-trivial affine offset.
2. Parameter range: theta = 2 pi t, t in [0,1) (one full rotation).
3. Seeds: the analyzer is deterministic, so a seed draws a random phase
   offset phi in [0,1); grid points are t_j = (phi + j delta) mod 1.
   Seeds 0..4 for every arm (5 per arm).
4. "13 vs 50 thresholds": 13 or 50 MAGNITUDES, each used with both signs.
   13 = {2^k, k=-4..8}; 50 = 2^(-4 + 12 i/49), i = 0..49 (same span,
   geometric). No threshold at 0.
5. "width of the final box": max of the two side widths. inf if unbounded.
6. Infinite W: two equal infinities are not a jump; finite vs inf is a
   jump. median(W) is taken over finite W values (if none finite: median
   := 1). Rows record the finite fraction.
7. "last 6 octaves": the 7 finest resolutions delta = 2^-10..2^-16
   (6 octave intervals). beta, R^2 and all AICs use this window. If any
   N = 0 in the window, beta is undefined and the success criterion fails.
8. AIC models (all 2 parameters, fitted by least squares on log N, x = 1/delta):
   power  log N = c + beta log x (OLS);
   log    N = a + b ln x;
   sat    N = Nmax (1 - exp(-x/x0)), Nmax in (0, 1e6 max N], x0 in (0, 1e6 max x].
   AIC = n ln(RSS/n) + 2k (RSS floored at 1e-300). Best of several starts
   for the nonlinear fits. "Better by >= 10": AIC_other - AIC_power >= 10.
9. Iteration safety: widening ascent capped at 500 iterations (cannot be
   reached: at most 2x(26 or 100)+d threshold moves); cap hits are recorded.
10. Interval product with coefficient exactly 0 gives [0,0] (avoids 0*inf).
11. Lens L4 (Sobol split) is named in lens_ids but not in the observable or
   either criterion; it is not computed. Only L5 is used.

## Criterion as applied (per seed, then aggregated)

Per seed s of an arm: S(s) = beta >= 0.2 AND R^2 >= 0.95 AND
AIC_log - AIC_pow >= 10 AND AIC_sat - AIC_pow >= 10.
Treatment SUCCESS = S(s) for all 5 TREATMENT seeds AND median NULL_TWIN
beta < 0.1.
Treatment FAILURE (any of): for any treatment seed, the last 3 octaves add
< 5% new breakpoints, i.e. (N(2^-16) - N(2^-13)) / N(2^-16) < 0.05 (N16=0
counts as finite staircase); or AIC_pow - AIC_log >= 10 for any seed; or
|median beta_T - median beta_NULL| < 0.1.
null_twin_meets_success = S(s) for all 5 NULL_TWIN seeds.
positive_control_detected = |beta - 0.6309| <= 0.05 for all 5 seeds.
cheat_detected = S(s) for all 5 CHEAT seeds.
Outcome (PREREG classes, in code): not (pc and cheat) -> INSTRUMENT_FAIL;
else null_twin_meets_success -> CONFOUNDED; else SUCCESS and not FAILURE
-> SIGNAL; else NULL.

## Pre-run analytic expectations (recorded, not used to tune)

- Box analysis of a rotation has expansion factor c = r(|cos|+|sin|),
  which exceeds 1 for most theta at r = 0.9, so W = inf over most of the
  circle; finite only near multiples of pi/2 (roughly 15% of theta).
- The narrowing steps make W continuous in theta inside finite regions
  (X meet F(X) depends continuously on theta). With the 1e-9*median jump
  rule, ANY continuously varying W registers a jump at nearly every
  adjacent pair, so N ~ (finite fraction)/delta and beta ~ 1. The CONTROL
  arm (continuous by construction) is recorded to expose this; a CONTROL
  beta >= 0.2 is reported as an anomaly about the observable, not used to
  change the outcome class (the PREREG classes do not use CONTROL).

## Stupid explanations: how addressed

1. FP jitter: 64 finest-grid adjacent pairs of TREATMENT seed 0 (32 jump,
   32 non-jump, fixed rng 12345) recomputed in exact rational arithmetic
   (Fraction of the float cos/sin/r/b); agreement of jump classification
   reported.
2. Threshold set as the only step source / short window: 13 vs 50
   threshold variants and the NULL_TWIN are reported; saturation is only
   tested by the saturating AIC and the 3-octave rule inside the window.
3. Iteration-count changes: fraction of finest-grid jumps of TREATMENT at
   which the ascent iteration count also changes is reported.

## Compute

Single process, OMP/MKL threads = 1, measured with time.process_time,
budget 10 core-minutes.
