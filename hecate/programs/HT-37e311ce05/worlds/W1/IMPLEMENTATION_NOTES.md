# HT-37e311ce05 / W1 -- implementation notes (written before any run)

Prompt: hecate/programs/_prompts/probe_impl_v1.md (sha256 cf4bd374...cbea2).
Bound by roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.

## Spec field -> code

- hypothesis: steep CS benefit stabilises pooled budgets vs a smooth
  matched-mean benefit. Tested by comparing TREATMENT (CS table) against
  CONTROL (null-twin table) under identical dynamics and seeds.
- mechanism (M1): `evolve()` in world.py. 100 agents, heritable integer
  m_i in 0..60 and a pooling bit. Each generation: random perfect pairing
  (50 pairs). If both pool, each partner's success = P(m_1+m_2);
  otherwise each partner's success = P(m_i). fitness_i = success_i - c*m_i.
  Wright-Fisher resampling of 100 offspring, then mutation.
- intervention: `omp_table()` estimates P(m, k) for m = 0..120 by OMP on
  Gaussian A (n=100, k=8, 40 trials per m).
- control: same dynamics with the null-twin table (arm CONTROL).
- null_twin: arm NULL_TWIN, same null-twin table, independent seed block
  (see ambiguity 6).
- positive_control: arm POSITIVE_CONTROL, step table P(m) = 1[m >= m*].
- CHEAT: arm CHEAT writes f_pool = 1.0, T = m*, mean_success = 1.0
  directly into the observables without running the dynamics.
- observable: at the final generation (gen 500): f_pool = fraction of
  agents with pooling bit 1; T = mean(m_1+m_2) over pairs in which both
  pool (from the final generation's pairing, the one used for its
  selection); mean_success = mean over all 100 agents of success_i in
  that same final pairing.
- success_criterion (evaluate.py): TREATMENT meets it iff
  (a) in >= 8 of 10 seeds: f_pool >= 0.8 AND |T/m* - 1| <= 0.15, AND
  (b) mean over seeds of mean_success(TREATMENT) minus mean over seeds of
      mean_success(CONTROL) >= 0.3.
- failure_criterion: f_pool < 0.5 in >= 5 of 10 TREATMENT seeds OR the
  success difference in (b) < 0.1. Recorded; per PREREG any
  non-success is NULL (failure_criterion only reported).

## Ambiguities and the reading chosen

1. m* is not defined in W1. Reading: m* = smallest m in 0..120 with
   P_CS(m) >= 0.5 (midpoint of the empirical OMP transition). The same
   m* is used for the step positive control and for all |T/m*-1| tests.
2. OMP "success": relative l2 error ||x_hat - x|| / ||x|| < 1e-4. OMP runs
   min(k, m) greedy steps with least-squares refit; m = 0 gives success 0.
   A has i.i.d. N(0,1) entries, columns normalised; a fresh A and x per
   trial; x has a uniformly random support of size k with N(0,1) values.
   m > n (up to 120) is allowed (overdetermined).
3. Null twin "linear ramp between P(0) and P(120), rescaled to equal
   mean": a linear ramp cannot generally match both endpoints and a
   different mean. Reading: r(m) = P(0) + (P(120)-P(0)) m/120, then
   multiplied by a factor alpha and clipped to [0,1], alpha found by
   bisection so that mean_m r(m) equals mean_m P_CS(m). P(0) is kept
   exactly (it is 0 for OMP); P(120) is kept if clipping reaches 1.
   The achieved mean and endpoints are written to the rows.
4. "success" in fitness is the table probability (expected success),
   not a Bernoulli draw; the spec calls it "a lookup benefit table".
5. Wright-Fisher weights: w_i = max(fitness_i, 0); if all are 0, uniform.
   (Fitness as specified is used directly as the WF weight; clipping only
   because WF weights cannot be negative.)
6. The spec's control and null twin are the same table. CONTROL uses the
   same seeds as TREATMENT (0..9, paired initial populations) and is the
   "null" in the success difference. NULL_TWIN uses seeds 1000..1009 as an
   independent replicate and is checked against part (a) of the success
   criterion only (with m* of the CS table). Part (b) is dropped for the
   null-twin check because it is a difference against the null itself
   (identically ~0 by construction); this makes CONFOUNDED easier, not
   harder, to reach.
7. Initial population (not specified): m_i uniform integer on 0..60,
   pooling bit Bernoulli(0.5), independently per agent.
8. Mutation: each offspring's m changes by +1 or -1 (equal probability)
   with probability 0.05, clipped to [0,60]; pooling bit flips with
   probability 0.01. Mutation applied after resampling.
9. Positive control detected iff in >= 8/10 seeds T is defined and
   |T/m* - 1| <= 0.15 (the spec's "+-15% of m*" with the success
   criterion's seed rule).
10. CHEAT detected iff the full success criterion (a and b, b against
    CONTROL) passes when CHEAT is put in the TREATMENT role.
11. T undefined (no pooling pair at the end) counts as failing
    |T/m* - 1| <= 0.15 in that seed.
12. Arms not named in the spec's size (NULL_TWIN, CHEAT) also get 10 seeds.

## Parameters (all from the spec's "size" line unless noted)

n=100, k=8, 40 OMP trials per m, m=0..120, N=100 agents, 500
generations, mutation m +-1 at 0.05, pooling flip 0.01, c=0.005,
m_i range 0..60, 10 seeds per arm. Table seed 12345 (chosen here).
Evolution seeds: TREATMENT, CONTROL, POSITIVE_CONTROL: 0..9;
NULL_TWIN: 1000..1009; CHEAT: none (no dynamics). BLAS threads = 1.

## Outcome decision (evaluate.py, in code)

if not (positive_control_detected and cheat_detected): INSTRUMENT_FAIL
elif null_twin_meets_success: CONFOUNDED
elif TREATMENT meets success_criterion: SIGNAL
else: NULL

## Compute

Estimated well under 1 CPU core-minute; measured with time.process_time
and recorded in rows and OUTCOME.json.

## Run log

(attempts appended below after runs)

- Attempt 1 (world.py + evaluate.py, 0.035 core-min): no crash. Outcome
  INSTRUMENT_FAIL: POSITIVE_CONTROL and CHEAT both not detected.
  Diagnosis: (i) CONTROL mean success = 0.990, so part (b) of the success
  criterion (difference >= 0.3) cannot be met by any arm; CHEAT at the
  maximum (1.0) reaches only 0.010. (ii) With OMP at n=100, k=8, the
  measured m* = 25, below the individual cap 60, and c = 0.005 makes
  rows nearly free, so lone agents hold m ~ 26-27. Under the step table
  pooling is unnecessary and pooled totals are ~2m* (T/m* ~ 2.1), not m*.
- Instrument repair: NOT MADE. The evaluator applies the criteria as
  written; both failures come from the spec (threshold unattainable vs
  its own control; m* within a single agent's reach). Any repair would
  mean changing a threshold or a size parameter (c, m range, n, k) after
  the TREATMENT result, which the PREREG faithfulness guard forbids.
  After attempt 1, evaluate.py gained two diagnostic anomaly strings.
  The decision logic is unchanged and only the evaluator was re-run.
  The world was not re-run.
