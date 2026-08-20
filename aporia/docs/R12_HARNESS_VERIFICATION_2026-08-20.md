# R12 grader harness — verification run (mock leg), 2026-08-20
Consumer: LAD-R12-RUN thread + Canon Band-G/R12 grader design + Harmonia (instrument owner)
Operator: Aporia loop (verification only; the instrument remains Harmonia's)

## What was run
harmonia/experiments/{r12_grader,r12_universe,run_r12,test_r12}.py — the built-but-never-run
R12 instrument (conjecture emission + falsification-test proposal, graded deterministically:
safe AST-whitelist evaluator, held-out prediction with naive-baseline penalty, version-space
entropy reduction). Self-tests: 17/17 pass. Offline mock suite: 9 trials (3 seeds x 3 mock
providers) on the 64-object tuples universe.

## Pre-stated readings
- CALIBRATED: good-provider trials score high on both graders; overfit and naive collapse
  toward 0 conjecture-quality; naive probes earn ~0 info-gain (the harness's own stated
  read criteria).
- MISCALIBRATED: any inversion (naive/overfit outscoring good) or degenerate grader.

## Result: CALIBRATED — full three-way separation, deterministic, no LLM judging
    provider | conjecture-quality (3 seeds) | test-quality efficiency
    good     | 0.344 / 0.526 / 0.238 (all exact-partition, holdout 1.000) | 1.000 / 1.000 / 1.000
    overfit  | 0.000 / 0.000 / 0.000 (baseline penalty)                   | 0.000 / 0.566 / 0.647
    naive    | 0.000 / 0.000 / 0.000                                      | 0.000 / 0.000 / 0.000
Notables: (a) the overfit provider's PROBES retain partial information value (0.57-0.65
efficiency) while its conjectures score zero — the two graders measure genuinely different
capacities, as designed; (b) the naive const-true conjecture reaches jaccard 0.656 on one
seed yet still scores 0.000 — the baseline penalty does its job exactly where naive
similarity is highest; (c) good's conjecture-quality varies 0.24-0.53 across seeds despite
perfect holdout accuracy — the score's information-theoretic component is universe-dependent,
so CROSS-SEED COMPARISONS of absolute scores need seed-matched designs (grader caveat for
any future live protocol).

## The live leg (PARKED)
The --live single-shot (real Opus calls, ~3 trials) is the thread's endpoint and remains
gated on the standing budget decision ($0 until ignition, DECISION pending with James).
Estimated cost: cents. Parked with ELI5; one budget word unblocks it. The mock leg proves
the harness will grade whatever the live model emits, deterministically and safely.

## Trace-vector record
problem_id: LAD-R12-RUN (mock leg) | tier_probe: instrument-calibration | answer_correct: 9/9 expected orderings
domain_constraints_detected: [seed-dependent-score-scale, paid-live-leg-gated]
operations_used: [self-test-suite, three-provider-mock-battery, separation-check, grader-caveat-extraction]
kill_pattern: none (CALIBRATED) | repair_available: n/a
confidence_calibration: deterministic; exact reproduction expected from same seeds
residue: the seed-matched-design caveat for live protocols; the overfit-probes-retain-value
  observation (probing skill and conjecturing skill dissociate — directly relevant to the
  Canon's R12-as-valuation-instrument re-scope)
