# HT-47f4c02be4 / W4 -- implementation notes (written before any run)

Prompt: hecate/programs/_prompts/probe_impl_v1.md
(sha256 cf4bd374bce1b817a12d3607063278183ce0a8b7c4a7b771061dc8ce133bcea2).
Bound by roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.

## Spec field -> code

- hypothesis: inference work / generation work falls with temporal
  predictability of hidden factors under a predictive prior ordering.
  Generation work = 1 multiplication per sample, so the lens-L6 ratio
  infer/generate equals the number of trial divisions per sample. Both
  are recorded (`mean_ratio_infer_over_generate` == mean cost).
- mechanism (M5): `make_stream()` in world.py. Prime table = all primes
  < 10^4 (1229, from sympy.primerange). Two independent random walks over
  the prime INDEX, i_t and j_t; n_t = P[i_t] * P[j_t].
  The solver `prior_ordered_cost()` tries divisors in order of prior
  probability built from the recent factors.
- intervention: prior-ordered trial division vs ascending trial division;
  s in {1, 3, 10}.
- control: `ascending_cost()`: divide n_t by primes in ascending order,
  count divisions until the first exact divisor (inclusive).
- positive_control: s = 0 (constant factors). Detected iff the fraction of
  samples where the prior-ordered solver succeeds on its first trial
  division is >= 0.99 (pooled over seeds, all samples including t = 0).
- null_twin: the SAME drift stream (same seed, same s) with the sample
  order randomly permuted (the (p, q) pairs kept together). Marginal of
  (p, q) identical; temporal order destroyed. Prior-ordered and ascending
  solvers both run on it.
- observable: mean number of trial divisions per sample.
- success_criterion (as applied): at s = 1, pooled over 5 seeds x 10000
  samples, R_drift = mean(prior cost, drift) / mean(ascending cost, drift)
  <= 0.5 AND R_null = mean(prior cost, null twin) / mean(ascending cost,
  null twin) >= 0.9.
- failure_criterion: R_drift > 0.5 or R_null < 0.9 (exact complement of
  success, so no third region exists).
- CHEAT: the s = 1 drift stream; the observable for the prior arm is
  overwritten with 1 division per sample (oracle; no mechanism run).
  Cheat detected iff R_cheat = mean(cheat) / mean(ascending, same stream)
  <= 0.5, i.e. the drift half of the success criterion fires on it.

## Outcome logic (evaluate.py, per PREREG)

The PREREG treats "treatment meets success criterion" and "null twin meets
the success criterion" separately. The spec's success criterion contains a
null-twin clause; I read the TREATMENT part as the drift clause
(R_drift <= 0.5) and "null twin meets the success criterion" as the null
twin passing the same drift clause, i.e. R_null <= 0.5. (The spec's own
second clause, R_null >= 0.9, is also reported and is part of the
full-criterion pass/fail.) Order of decision:
1. positive control or cheat not detected -> INSTRUMENT_FAIL
2. null twin R_null <= 0.5 (null twin meets success) -> CONFOUNDED
3. full success criterion met (R_drift <= 0.5 and R_null >= 0.9) -> SIGNAL
4. otherwise -> NULL

## Ambiguities and readings chosen

1. "random walks over the prime index, step size s": each step is +s or
   -s with probability 1/2 each (Rademacher, magnitude exactly s), with
   reflection at the ends of the index range [0, 1228]. p and q walk
   independently. Initial indices uniform on [0, 1228]. s = 0 gives
   constant factors, matching the positive control.
2. "order of prior probability from recent factors": recent factors = the
   two factors (p_{t-1}, q_{t-1}) of the immediately preceding sample
   (window 1; the solver has recovered both after factoring the previous
   sample). Prior over candidate prime index k is decreasing in
   d(k) = min(|k - idx(p_{t-1})|, |k - idx(q_{t-1})|) (a symmetric,
   unimodal-per-factor random-walk prior that does not know s). Candidate
   order: ascending d, ties broken by ascending prime. All 1229 primes are
   in the order, so the solver always terminates. At t = 0 (no history)
   the prior-ordered solver falls back to ascending order.
   For the null twin the "recent factors" are those of the previous sample
   in the shuffled order (the solver sees the stream as presented).
3. Cost counting: an actual n % prime is computed for each candidate in
   order, and the cost is the 1-based position of the first zero
   remainder. Since n = p q with p, q prime, the first divisor found is
   whichever of p, q comes first in the order. Prior maintenance (building
   the order) is NOT counted in the observable (spec: observable is
   trial divisions); it is reported separately as a diagnostic
   (1229 distance evaluations + sort per sample).
4. "ratio" = ratio of pooled means (mean prior cost / mean ascending
   cost), not a mean of per-sample ratios. Per-seed ratios are also
   reported.
5. Rows: one JSON row per (arm, seed, s) -- s is part of the arm's
   configuration; arms TREATMENT, CONTROL, NULL_TWIN (two solvers inside
   one row: prior and ascending), POSITIVE_CONTROL, CHEAT, plus a
   pre-declared diagnostic arm MEMO (not in any criterion): try the two
   previous factors first, then ascending -- this addresses the spec's
   alternative_explanation (memoization vs prediction).
   TREATMENT and CONTROL rows at s in {1,3,10}; NULL_TWIN at s in
   {1,3,10} (criterion uses s = 1); POSITIVE_CONTROL at s = 0 (both
   solvers); CHEAT at s = 1; MEMO at s in {1,3,10}.

## Parameters (all from the spec's `size` field)

- primes < 10^4 (1229); 10000 samples per condition; s in {1, 3, 10}
  (+ s = 0 for the positive control); 5 seeds: 0, 1, 2, 3, 4.
- Per seed and s, the RNG is numpy default_rng(seed * 1000 + s) for the
  walk and default_rng(seed * 1000 + s + 500) for the null-twin
  permutation.
- Thresholds: 0.5, 0.9, 0.99 exactly as in the spec.

## Compute

Cost estimate ~1 core-minute; vectorized numpy over samples x 1229. Wall
and process CPU time are measured in world.py and written to
run_meta.json; evaluate.py copies them into OUTCOME.json.

## A priori note (not a result)

Because a walk with s = 1 over 10000 steps stays within a small band of
indices, the shuffled null twin still has concentrated magnitudes, so the
prior may beat ascending there too. The spec prescribes this null twin;
I implement it as written and do not alter it after running.

## Run log (appended after runs)

- Attempt 1 (bug, no treatment result read): world.py merged a `common`
  parameter dict into every row whose key "prior" (a description string)
  overwrote the row's "prior" statistics; evaluate.py crashed on it
  before printing any statistic. Fix: that parameter key renamed to
  "prior_rule". No threshold or parameter changed. Attempt 2 reruns
  everything. Attempt 1 used 0.24 core-minutes.
- Attempt 2 completed: 0.23 core-minutes; total over both attempts ~0.47 core-minutes (OUTCOME.json core_minutes records attempt 2 only).
