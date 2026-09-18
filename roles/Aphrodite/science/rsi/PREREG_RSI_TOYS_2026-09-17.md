# Preregistration: four RSI mechanism toys (Aphrodite, 2026-09-17)

Committed BEFORE any experiment code was run. Directive:
roles/Aphrodite/prompts/2026-09-17_rsi_research/OPERATOR_DIRECTIVE.md.

## Scope and honesty clause

These are deterministic, stdlib-only Python toys with NO language model.
They test MECHANISMS that recursive-self-improvement (RSI) claims rest
on, not the claims about GLM, RSIAgent, Dream-RSI or ModularRSI
themselves. A toy that behaves as predicted shows the mechanism is
coherent and that our instruments can see it; it is not evidence about
any frontier system. Several predictions below are near-analytic (E1,
E3); the seat says so, and treats them as instrument checks. E2 is the
one with a genuinely open outcome.

Per the north star, these are INSTRUMENTS and PRESSURES (feedback
channels, verifiers, dataset guards), not a reasoner.

Common rules:
- Success is judged by a harness-side ORACLE that is independent of the
  feedback channel the improver sees (base role: verify the property,
  never the label). Evaluations are counted by a wrapper around the
  objective, never by the improver.
- Every result row is written to ledgers/ and committed with the verdict.
- Statistics: medians/means over seeds; paired 95% bootstrap CI (2000
  resamples, fixed seed 12345). A hypothesis whose CI straddles its
  boundary is INDETERMINATE, and that word is reported.
- Each experiment has a POSITIVE, a NEGATIVE and a CHEAT control as
  pytest tests (science/rsi/tests/). Tests must pass before results are
  read.

## E1 -- Feedback density and attribution (source: GLM "dense feedback")

Environment: K components, V=8 values each, hidden target drawn
uniformly; start configuration drawn uniformly. One evaluation = one
call to evaluate(config). Budget B = 40*K*V evaluations.
K in {2,4,8,16}; 200 seeds per (K, regime).

Regimes (same propose-one-change/evaluate/accept-or-revert skeleton):
- PASSFAIL: one bit, all components correct. Accept any change (random
  walk).
- SCALAR: count of correct components (an end-to-end metric). Random
  component, random different value; accept if score does not drop.
- DENSE: per-component pass vector (local, attributable). Lowest-index
  failing component; next untried value; keep if its flag passes, else
  revert; tried-set resets when exhausted.
- DENSE_NOISY: DENSE with each flag independently flipped w.p. 0.1 per
  evaluation. EXPLORATORY: no prediction.
- DENSE_MISATTRIBUTED: DENSE whose flag vector is permuted by a hidden
  fixed derangement per run (plentiful but misattributed feedback).

H1a: median evaluations-to-success DENSE < SCALAR at K = 4, 8, 16.
H1b: the ratio median(SCALAR)/median(DENSE) strictly increases over
     K = 4, 8, 16. (Seat's analytic expectation: ~2.3*H_K, harmonic.)
H1c: success-within-budget rate DENSE_MISATTRIBUTED < SCALAR at every
     K >= 4 ("attribution, not volume").
Eligibility: DENSE can always succeed within B (worst case K*(V-1) <
B), so a DENSE failure is a defect, not a result.

## E2 -- A self-referential improver: compounding or saturating?
## (sources: STOP-style self-improvement; RSI framing in the directive)

Base tasks: minimise f on R^6; families sphere, rastrigin, rosenbrock,
ellipsoid (condition 1e3), each shifted by U[-3,3]^6, start U[-5,5]^6.
Train: 12 instances (3 per family); test: 40 held-out instances (10 per
family), disjoint seeds. Task score = log10(f_best + 1e-12); utility
U(theta) = mean task score (lower is better). Base budget 400 real
evaluations per task.

Improver I(theta): a (1+lambda) evolution strategy over a box with
theta = (log10 sigma0 in [-3,1], step-adaptation factor a in [1.01,2],
lambda in 1..16, restart patience p in 5..200). The SAME I is used on
base tasks and on the meta-problem g(theta') = U_train(theta') with a
meta budget of 60 U-evaluations.

theta_0 (deliberately poor): sigma0 = 10^-2.5, a = 1.02, lambda = 1,
p = 200. Generations G = 4. Ten chains (meta RNG seeds 0..9; tasks
fixed).
- RECURSIVE: theta_{g+1} = I(theta_g).optimise(U_train, start theta_g).
- FIXED-META: theta'_{g+1} = I(theta_0).optimise(U_train, start
  theta'_g).
Delta_g = U_test(theta_{g-1}) - U_test(theta_g) (positive = better).

H2a: U_test(theta_1) < U_test(theta_0) in >= 9 of 10 chains.
H2b (the seat's stand, saturation): median Delta_2 < median Delta_1.
     The COMPOUNDING alternative (Delta_2 >= Delta_1 and Delta_3 >=
     Delta_2 in medians) is thereby rejected if H2b holds.
H2c (no recursion dividend by g=4): paired CI of U_test(theta_4) -
     U_test(theta'_4) includes 0 or favours FIXED-META. If it excludes 0
     in favour of RECURSIVE, the stand is falsified and reported so.
H2d (evaluator gaming, the cheat arm): with LEAKY accounting (the
     evaluator charges the base budget per STEP, so lambda candidates
     per step are free), a RECURSIVE chain drives lambda >= 8 in >= 8 of
     10 chains; the counting wrapper reports real/declared evaluations
     >= 4 for the final theta; and under HONEST accounting on test the
     leaky-trained theta is not better than the honest-trained theta
     (paired CI includes 0 or favours honest).

## E3 -- Verifier-gated memory distillation (source: "RSIAgent" claim,
## unverified; mechanism: curriculum/actor/verifier + memory pool)

World: colors C=6, shapes S=6, actions A=4. COLOR-worlds: action =
R[color] (shape is a distractor). SHAPE-worlds: action = R[shape].
Training: 24 states with shapes 0..2; the actor tries actions in order
until rewarded. Test: 60 states with UNSEEN shapes 3..5, one shot.
200 seeds per condition.

Memory: NONE; RAW (exact (color,shape) -> action); DISTILLED (color ->
majority action among training successes). VERIFIED distillation admits
a color rule only if 2 probes at training shapes different from its
source succeed (probe interactions are counted). POISON: before
distillation, false color rules for half the colors are injected
(peer memory); UNVERIFIED admits them, VERIFIED probes them.

H3a: COLOR-worlds: mean test accuracy DISTILLED_VERIFIED >= 0.9;
     RAW <= 0.4; NONE <= 0.4 (chance 0.25).
H3b: COLOR-worlds with POISON: VERIFIED - UNVERIFIED >= 0.25.
H3c (negative control, wrong abstraction): SHAPE-worlds: VERIFIED admits
     a mean <= 0.5 color rules of 6, UNVERIFIED admits 6; and VERIFIED
     test accuracy is not below NONE by more than 0.05.

## E4 -- Disjoint-dataset guard against a leak (source: "ModularRSI"
## claim, unverified; mechanism: evolve against disjoint datasets)

Items: integers in [0, 10^4); label = parity of digit sum, flipped w.p.
0.15 (so the true rule attains ~0.85). A "hint" field equals the label
w.p. 0.95 in dataset A only; random in B and in test set C. A, B, C are
disjoint; |A| = 900, |B| = 100, |C| = 1000.

Harness genome: integer weights in [-2,2] over six binary features
(hint, last-digit parity, digit-sum parity, divisible by 3, n > 5000,
first-digit parity); predict 1 iff the weighted +-1 vote > 0. (1+4)
evolution, 200 generations, mutate one weight by +-1, start all zero.
200 seeds per regime.

Regimes: SINGLE (fitness = acc on A); POOLED (acc on A u B);
DISJOINT (fitness = min(acc_A, acc_B)).

H4a: SINGLE: mean acc on C <= 0.65.
H4b: DISJOINT: mean acc on C >= 0.80.
H4c: POOLED: mean acc on C <= 0.65 (pooling does not guard when the
     leaky set dominates the pool).
Leak detector: the A-minus-B accuracy gap >= 0.3 flags >= 90% of SINGLE
harnesses and <= 5% of DISJOINT harnesses.
Positive control: with no leak (hint random in A), all three regimes
reach mean C acc >= 0.80.

## What would falsify the seat's overall reading

"RSI's leverage sits in the feedback and verification harness, not in
self-reference per se" would be falsified by: H1c failing (misattributed
dense feedback as good as scalar), H2c failing (a recursion dividend),
or H3b/H4b failing (verification/disjointness not protective).
