# ENSORAIN E0 -- preregistration, part 2 (constants frozen; no gate moved)

Currency: 2026-09-23. Committed AFTER dev-seed engineering (seeds 0-999)
and BEFORE any evolution run (seeds 1000-1999) or confirmatory run (world
instances 10000-10039). Part 1 (20a4bab5c) gates, thresholds, seed split
and verdict rule are unchanged. This file sets constants and resolves
three ambiguities in part 1, each named below, each resolved toward the
stricter reading.

## 1. What dev engineering found (dev rows, NOT evidence for any gate)

Rows: ensorain/runs/dev_r1.jsonl, dev_r2.jsonl, dev_offline.jsonl,
dev_als_ceiling.jsonl, dev_tune.jsonl.

- Economy r1 (theta 0.5, horizon 2000): every learner starved before it
  learned; the ORACLE itself starved in a greedy local basin at theta 0.5.
- Learner (offline, iid samples, planted latent order, C=168): joint NLMS
  reaches R^2 ~0.8-0.94 only after 8000 samples (the world has 4096
  cells). Round 1 (exact per-core NLMS) diverged. Round 2 (lr/init scan,
  clipped SGD) no better than 0.94 @8000. Round 3 (rank-1-path init) no
  better. The three permitted rounds are USED. The TT learner is
  SGD-limited: B2 risk is live and recorded, not hidden.
- Literature ceiling: batch ALS TT completion reaches R^2 0.997 from 800
  samples in the latent order, 0.64 from 1600 in the observed order.
  An ALS organism would need ~1600 floats of stored samples, above every
  gated cap. Mode order is a large lever (H2 is not vacuous).
- dev_r2 (long horizon): LOWRANK (64x64 matrix factorisation) harvested
  15.3k at C=384 vs ORACLE 16.4k and TT_PLANTED 11.3k. LRU harvested LESS
  than NOMEM (memory of depleted good cells is a trap). In R every
  learner <= RANDOM. TT_SVD_INJECT thrived in C and not in R.
- ADDITIVE is weak by construction: the field is a product of zero-mean
  cores, so it has ~no main effects. It stays in the matrix; it is not a
  strong baseline and is not counted as one in any narrative.

## 2. Frozen constants

Economy (life.py ECON_DEFAULT overridden by tune.ECON):
  theta 0.0, energy0 100, metabolism 0.8, gain 3.0, regrow 500,
  kappa 0.0005, horizon 12000, noise 0.1, epsilon 0.1 (arms without their
  own epsilon), tabu 8, audit every 250 steps.
TT_FIXED: observed order, uniform ranks filling the cap, joint NLMS,
  lr 0.3, init_scale 0.8, no buffer.
TT_TUNED (ensorain/e0/tt_tuned.json, best of a 20-point dev grid on
  instances 20-25, caps 96+168): observed order, uniform ranks filling
  the TT share of the cap, mode sgd, lr 0.1, init_scale 0.8, buf_frac 0.5,
  replay 2, epsilon 0.3.
Other learners: ADDITIVE lr 0.3; RF lr 0.5; LOWRANK lr 0.5 (NA below
  cap 128: rank-1 on a 64x64 unfolding needs 128 floats).

## 3. Evolution procedure (ensorain/e0/evolve.py)

Class 0 only. Caps 96 and 168, one run each. Population 32, 25
generations, K=3 fresh training worlds per generation (seeds 1000+),
tournament 3, 2 elites re-evaluated each generation, mutation as coded
(order swap p .5, one bond rank +-1 p .6 repaired to cap, lr/init/epsilon
log-normal p .4, buffer/replay steps p .3, mode flip p .1). Initial
population: TT_TUNED constants with random orders and random ranks.
Champion = best mean over 6 further training worlds. Evolution never
sees a confirmatory seed.

## 4. Ambiguities in part 1, resolved (stricter reading)

A1. H1 "At C in {96, 168}" -> H1 must pass at BOTH caps (H2 says "or"
    explicitly; H1 does not).
A2. The 10% margin: mean_i TT / mean_i B - 1 >= 0.10, where i ranges over
    the 40 confirmatory instances (organism seeds 0-1 averaged within an
    instance), B = the non-TT bounded arm with the HIGHEST mean harvest
    at that cap in that world, chosen on the confirmatory rows (the most
    conservative choice for TT). CI: paired bootstrap over instances,
    10,000 resamples, of mean(TT - B); lower 2.5% bound > 0.
    Interaction: per instance (TT - B_C) in C minus (TT - B_R) in R (B_R
    = best non-TT in R), same bootstrap.
A3. Positive control "planted TT with the dev-tuned constants and true
    ranks": the true ranks (3) need all 168 floats, so TT_PLANTED uses
    TT_TUNED's learning constants (lr, init_scale, mode, epsilon) with
    buf_frac 0 and replay 0. Threshold unchanged (R^2_unvisited >= 0.5 at
    C=168, median over instances).
A4. H2 order recovery: required TT parameter count of the TRUE field
    under the evolved order (numerical TT-SVD ranks at tol 1e-8, summed as
    n_params) < median of the same over 200 uniformly random orders
    (seeded 5150), on confirmatory instance 10000's field.
A5. H2 cross-class: class 1 (a different latent order), same confirmatory
    instance seeds. gain_k = mean(TT_EVOLVED) - mean(TT_TUNED) on class k.
    Pass iff gain_1 <= 0.5 * gain_0.

## 5. Confirmatory matrix

M1: class 0, lam in {0, 1}, caps {48, 96, 168, 384, 4096}, all arms
    (TT_EVOLVED only at its evolved cap; LOWRANK NA below 128),
    instances 10000-10039, organism seeds 0-1.
M2 (H3 dose): class 0, lam in {.25, .5, .75}, cap 168, arms TT_TUNED,
    LRU, HASH, KNN, ADDITIVE, RF, LOWRANK (M_0 and M_1 from M1).
M3 (cross-class): class 1, lam 0, caps 96 and 168, TT_TUNED and
    TT_EVOLVED (class-0 genomes).
M4 (secondary, NOT gated): M1 at cap 168, lam {0,1}, kappa 0 -- how much
    of each arm's rank is compute charge rather than prediction.

Scorer: ensorain/e0/score.py, committed before M1 runs; its output and
the rows ship in the verdict commit.

## 6. Seat's updated expectation (written before evolution; losable)

H1 FAILS: LOWRANK beats TT_TUNED at both caps (dev: 10.4k/15.3k vs
~6.4k). Verdict by rule then = B regardless of H2/H3. Expected
secondary: H2's order recovery PASSES (selection finds physics) even
though the harvest gate is moot. Probability of verdict A under the
frozen rule: <= 0.1.

## 7. Addendum A6 (written 2026-09-23 BEFORE any confirmatory row; evolution
## was running, no confirmatory seed touched). A declared LOOSENING, with
## the literal reading still scored and reported beside it.

Two control clauses of part 1 s5 test the wrong property, as dev_r2 shows:

- NEGATIVE "every structural learner's unvisited-cell R^2 is within 0.05
  of 0 in R": a learner that is merely miscalibrated in R has R^2 << 0
  (dev_r2: TT_FIXED -83, LOWRANK -33) without having found any signal.
  The property the control exists for is "no false signal". GOVERNING
  reading: median R^2_unv in R <= 0.05 for every structural learner.
- NEGATIVE "no learner beats LRU on harvest in R by more than the
  run-to-run sd": LRU is handicapped in every world by the depletion trap
  (dev: LRU < NOMEM in C and R), so beating LRU is not evidence of signal.
  GOVERNING reading: no learner beats NOMEM (same policy, no memory) in R
  by more than one sd of NOMEM's per-instance harvest.
- POSITIVE "ORACLE has the top harvest": TT_SVD_INJECT is a cheat control
  carrying the true field and is excluded from that comparison.
- CHEAT (SVD inject within 10% of ORACLE) is scored at C=168 and C=384,
  where the true ranks fit (at 168 exactly).

The scorer prints the literal part-1 reading AND the governing reading for
each clause; a disagreement is reported in the verdict, not buried.
