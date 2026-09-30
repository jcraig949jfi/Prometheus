# W6 -- is the sign-flip boundary of an iterative estimator fractal? (M8; lens L1)

Generator: Pass 3 v2 (prompt pass3_v2.md, sha256 2adcfc8d...d461). Layer: implemented
candidate design. No treatment exists; the Newton estimator was not run.

## What the world tests
M8, which P1 called "strange and possibly empty": for an iterative (fixed-point)
estimator, the set of misspecification parameters on which the estimate keeps its sign
has a fractal boundary, so sound robustness certification of the sign costs a steeper
power law than for a smooth boundary. The world uses the smallest honest case: a
two-cluster Cauchy-location M-estimator, solved by undamped Newton from the median,
with two subgroup bias parameters. Observable: the uncertainty exponent alpha (L1's
Monte-Carlo pair-disagreement exponent; alpha = 2 - D). S1 asks for a fractal boundary,
S2 asks that the ITERATION causes it (the global-maximiser twin has the same estimand
and data but no iteration).

Link to abstract interpretation (kept explicit, not claimed as tested): any sound
certifier must leave undecided every cell that contains both signs, so the undecided
fraction of an eps-grid is at least the boundary-cell fraction, which scales as
eps^alpha. The world measures the geometric premise; it does not build the certifier.

## Why it can fail cleanly
P1's own knockout says the smooth case is likely common. Newton from a fixed start in
PARAMETER space (not start space) may give only finitely many smooth branches in this
window; then alpha ~ 1 and F1 fires. The twin reads alpha 0.99 (0.97 coarse, 1.02 fine),
so a smooth answer has a measured reference.

## How it avoids the earlier failures
- W3: its breakpoint counter fired on the continuous control (beta 1.0). Here the
  observable is a label-disagreement rate, which is exactly 0 for a constant label and
  gives alpha ~ 1 for a smooth boundary; the twin was measured (0.99).
- W4: its positive control depended on a grid-alignment convention and missed a 10%
  window. Here pairs are random in position and angle (no grid) and the positive
  control reads 0.55 (D = 1.45, close to the known Newton z^3 - 1 Julia-set dimension
  of about 1.42) against a threshold of 0.80; no tolerance band around a theoretical
  value is scored.
- W4 deferred definitions to another world: every definition is in spec.json.

## Ambiguities resolved
1. "Iterative estimator of a confounded effect": a Cauchy-location M-estimator of the
   treated-minus-control difference with subgroup bias parameters; Newton from the
   median, 100 undamped steps. Non-convergence is its own label (0), not dropped.
2. Data choice (revisions.json): symmetric clusters made the twin's local maxima tie
   exactly for every g (degenerate); rigid group shifts gave a 4% minority label. Groups
   that cut across clusters (0,0,1,1,0,1) change cluster tightness, giving a 46%/54%
   split and a boundary of length ~2.5 in the square. The data were chosen for the
   TWIN's balance only; the treatment was never evaluated.
3. Relative clause S2: the twin's own value is computed as twin (seeds 0-4) minus a
   replicate twin (seeds 5-9) = -0.017, so "discriminating" is tested against sampling
   noise and not against a trivially zero difference.
4. "Cheat detected" = the clause evaluator reports success when a power law of slope
   0.5 is written straight into f(eps): alpha 0.50, S2 gap 0.49.
5. Base points lie in the inner square [-0.75, 0.75]^2 so every partner (eps <= 1/4)
   stays in [-1, 1]^2; no reflection or clipping.
6. Values of alpha between 0.80 and 0.90 are INCONCLUSIVE.
