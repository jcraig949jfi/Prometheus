# HT-37e311ce05 / W5 probe round 3 -- implementation notes

Prompt: hecate/programs/_prompts/probe_impl_v3.md (sha256 a34a8c61...21685),
{TID}=HT-37e311ce05, {W}=W5. Written BEFORE any treatment code was run.
Frozen inputs (not edited): spec.json, controls.py, ATTAINABILITY.json,
control_rows.jsonl. Everything here lives in probe/.

## Arms (world.py)

world.py imports ../controls.py as a module (import has no side effects
except reading spec.json; controls.main() is NOT called, because it
would overwrite the frozen control_rows.jsonl). Every arm uses the
frozen functions world(), reward(), benefit(), gap_of(), l1min(),
curve_stats() and the frozen parameters from spec.json.

- TREATMENT: evolution under fitness = reward(A x) - c*||x||_1. The loop
  is a line-for-line copy of controls.evolve_l2_twin with the cost term
  C*(X**2).sum(1) replaced by C*np.abs(X).sum(1) and nothing else:
  population 60 initialised at x_good, 2000 generations, truncation 50%
  (stable argsort), parents resampled uniformly, per-gene mutation prob
  0.1 with N(0, 0.05^2). ||x_good||_1 = ||x_good||_2^2 = 10, so both arms
  start at the same fitness.
- CONTROL = NULL_TWIN: the spec's "control" field and its "null_twin"
  field describe the same arm (L2 cost). It is re-run by calling
  controls.evolve_l2_twin unchanged. It is written once with arm
  "NULL_TWIN" (not duplicated as a separate CONTROL arm).
- POSITIVE_CONTROL: controls.l1min per (seed, m), unchanged.
- CHEAT: gap injected 0.8 for m < m*, 0 otherwise, genome = x_good, as
  in controls.py.
- CALIBRATION: m* recomputed with controls.l1min on calibration seeds
  1000-1019 (bp exact recovery frac per m).

## Seeds and RNG

Seeds 0-9 for all arms (spec: treatment 0-9, controls 0-9). World for
(seed, m) is controls.world(seed, m). Treatment mutation/selection RNG:
np.random.default_rng([seed, m, 7]) -- the SAME stream key the twin uses
(common random numbers; the two arms differ only in the cost term). This
is a choice made here, before any run; the spec does not name a stream.

## Rows

probe/rows.jsonl, one row per (arm, seed), flushed after each row. A row
holds, per m in the grid: gap (population median of reward - benefit, via
controls.gap_of), and for evolved arms median reward, median benefit,
median ||x||_1, and the final population rounded to 4 d.p. (as the
controls store it) so evaluate.py can audit every gap from its genome;
PC rows hold the LP genome rounded to 6 d.p. CALIBRATION is one row
(seed = null). Every row carries the parameters used.

## Ambiguities and readings (no threshold changed)

1. "one row per (arm, seed)": the observable is per (seed, m); the 13
   m-values are stored inside the seed row as a dict keyed by m.
2. Outcome decision (evaluate.py), in this order:
   a. Reproducibility: recompute S1_completion and S2_high_m_gap for PC
      and NULL_TWIN from rows.jsonl; attainable = PC meets clause,
      discriminating = twin does not; also recompute cheat_detected
      (ruler fires on CHEAT AND audit flags every injected-and-different
      CHEAT row with 0 flags on PC/twin/treatment) and the calibrated m*.
      Any status differing from ATTAINABILITY.json -> INSTRUMENT_FAIL
      (reproducibility), stop. Numeric drift with equal status is
      recorded as an anomaly only.
   b. positive_control_detected = PC meets S1 and S2; cheat_detected as
      above. Either false -> INSTRUMENT_FAIL.
   c. null_twin_meets_success (S1 AND S2) -> CONFOUNDED.
   d. Treatment meets S1 AND S2 and no failure clause -> SIGNAL.
   e. Otherwise NULL (fails a success clause and/or meets a failure
      clause); which clauses fired is recorded. (With the frozen
      thresholds a success clause and its failure counterpart cannot
      both hold.)
3. Clauses are read on the 10-seed mean curve gbar(m), through the frozen
   controls.curve_stats (completion defined 0 when total drop < 0.3).
4. Audit tolerance 1e-3 on recomputed gap, as in controls.py.

## Budget

Expected: twin ~130 runs + treatment ~130 runs + LPs, ~1 core-minute
total, single-threaded (controls.py pins BLAS threads to 1).
