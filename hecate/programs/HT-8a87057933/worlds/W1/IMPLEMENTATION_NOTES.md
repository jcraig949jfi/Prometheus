# HT-8a87057933 / W1 -- implementation notes (written before any run)

Prompt: hecate/programs/_prompts/probe_impl_v1.md (sha256 cf4bd374...bcea2).
Bound by roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.
Read: W1, mechanisms M1 and M8, lenses L1 and L4. Nothing else.

## Spec field -> code

- hypothesis: core-guided forgetting (TREATMENT) recovers from a plant switch
  faster than drop-oldest (CONTROL) and random-drop (NULL_TWIN).
- mechanism: `world.py`. Scalar plant x' = a x + b u + e, e ~ U(-0.05, 0.05).
  256 candidate models (a_i, b_j) on a 16x16 grid, model index = 16*i + j.
  A clause is the 256-bit set of models whose one-step prediction
  a_m x_t + b_m u_t is within 0.1 of the observed x_{t+1} (models that miss
  by > 0.1 are excluded). Window = list of clauses, capacity 40 (on append,
  if length > 40 the oldest clause leaves). SAT iff the AND of all clause
  masks in the window is non-empty (exact, brute force over 256 bits).
  Controller: certainty-equivalence deadbeat with the lowest-index consistent
  model (a^, b^): u_t = (r_{t+1} - a^ x_t) / b^. Empty window -> all models
  consistent -> model 0.
- MUS by deletion (M1): start with all window clauses (UNSAT); for each
  clause in stored (chronological, oldest-first) order, tentatively remove
  it; if the remainder is still UNSAT keep it removed, else restore it.
  The result is a minimal unsatisfiable subset.
- TREATMENT (core-guided): on UNSAT, repeat { extract one MUS; delete the
  oldest clause in that MUS } until the window is SAT. k = number deleted.
- CONTROL (drop-oldest): on UNSAT, compute k = the count core-guided would
  delete on this same window (run the core-guided procedure on a copy);
  delete the k oldest window clauses; if still UNSAT, keep deleting the
  oldest one at a time until SAT. Both k and the extra count are recorded.
- CONTROL_SW10 (the spec's second control, "fixed 10-step sliding window"):
  window capacity 10; on UNSAT delete oldest until SAT. Reported only; it is
  not named in the success criterion.
- NULL_TWIN (random-drop): on UNSAT, compute k as above; delete k clauses
  chosen uniformly without replacement from the window; if still UNSAT,
  repeat (recompute k on the current window, delete k uniform) until SAT.
- POSITIVE_CONTROL (oracle reset): window cleared exactly at each switch
  (before the first post-switch clause). If UNSAT ever occurs otherwise it
  is handled by drop-oldest-until-SAT (expected never: true model is always
  consistent since |noise| <= 0.05 < 0.1).
- CHEAT: runs the TREATMENT world but overwrites each switch's recovery time
  with 10 (the minimum possible under my observable reading), bypassing the
  mechanism.
- intervention: (a, b) resampled uniformly from the 256 grid models every
  200 steps, excluding the current model (so every switch is a real change);
  10 switches per run.
- observable: recovery time per switch = number of steps after the switch
  until |x - r| < 0.1 has held for 10 consecutive steps (counted to the
  10th good step; minimum 10). Step 1 = the first state produced by the new
  plant. If not recovered before the next switch / end, censored at 200.
- success_criterion (as applied in evaluate.py): over 300 switches per arm,
  median(TREATMENT) <= 0.7 * median(NULL_TWIN) AND
  median(TREATMENT) <= 0.85 * median(CONTROL) AND one-sided Mann-Whitney
  (TREATMENT less) p < 0.01 against NULL_TWIN AND against CONTROL.
- failure_criterion: median(TREATMENT)/median(CONTROL) >= 0.95 OR
  one-sided MW p (vs CONTROL) >= 0.05.
- Outcome (PREREG classes, in code, in this precedence):
  INSTRUMENT_FAIL if positive or cheat not detected; else CONFOUNDED if
  null twin meets success; else SIGNAL if treatment meets success;
  else NULL (fails criterion or meets failure criterion; the band between
  them also reads NULL since "treatment fails the criterion").
- positive_control_detected: POSITIVE_CONTROL, put in place of TREATMENT,
  meets the full success criterion (vs NULL_TWIN and CONTROL).
- cheat_detected: CHEAT, in place of TREATMENT, meets the full success
  criterion.
- null_twin_meets_success: the criterion component that does not reference
  the null twin itself: median(NULL_TWIN) <= 0.85 * median(CONTROL) and
  one-sided MW p < 0.01. (The 0.7 x random-drop clause is vacuous for the
  null twin against itself.)

## Ambiguities and readings chosen

1. Grid ranges not given. a in linspace(-1.2, 1.2, 16) (spans stable and
   unstable open loop, so L4 is not vacuous); b in linspace(0.5, 2.0, 16)
   (bounded away from 0 so deadbeat is defined). Chosen from the spec's
   needs, not from results.
2. Square-wave reference not specified: amplitude +-1, half-period 25 steps
   (period 50; 4 periods per regime). Deadbeat targets r_{t+1}.
3. "10 switches per run" with "2000 steps": first regime runs steps
   0..199, switches at t = 200, 400, ..., 2000, run length 2200, so 2000
   steps follow the first switch. Initial x = 0.
4. "Drop oldest member(s) until SAT": iterated MUS extraction + drop the
   oldest in each MUS until the whole window is SAT.
5. MUS deletion order = oldest-first (stored order). This biases the MUS
   toward newer clauses; it is the default order of the algorithm, chosen
   before any run.
6. Matched timing/count: arms run their own closed loops (the controller
   depends on the window, so trajectories diverge); "matched" is read as
   same event (each arm's own UNSAT events) and same count (k computed by
   the core-guided procedure on that arm's own window). Common random
   numbers: for a given seed, the plant schedule and the noise sequence are
   identical across arms; random-drop uses a separate RNG stream.
7. Mann-Whitney: scipy.stats.mannwhitneyu(alternative="less"), asymptotic
   with tie correction (recovery times are discrete).
8. No clipping of u or x; max |x| per run is recorded as a check.

## Parameters (all from the spec unless noted above)
noise 0.05, miss threshold 0.1, grid 16x16, window 40, 200 steps/regime,
10 switches, 30 seeds per arm (seeds 0..29), recovery tolerance 0.1 for 10
consecutive steps, censor 200. Thresholds 0.7, 0.85, 0.01, 0.95, 0.05.

## Secondary lens observables (recorded, not used for the outcome)
L1: per UNSAT event, MUS size and Jaccard turnover vs the previous MUS
(TREATMENT computes the MUS; other arms compute it for k anyway); fraction
of deleted clauses that were pre-switch. L4: closed-loop pole
a - b a^/b^ per step; fraction of recovery-interval steps with |pole| < 1.

## Compute budget
Estimated well under 10 core-minutes (pure Python bitmask ops, single
core). Measured with time.process_time in both scripts; written to rows
and OUTCOME.json.

## Attempt 1 result and the ONE instrument repair (written after attempt 1)

Attempt 1 (rows_attempt1.jsonl, OUTCOME_attempt1.json): INSTRUMENT_FAIL.
Medians (n=300): TREATMENT 12, CONTROL 12, NULL_TWIN 14, POSITIVE_CONTROL 12,
CHEAT 10. Neither positive control nor cheat detected. Note: these were
seen for ALL arms, including TREATMENT, before the repair was chosen.

Diagnosis (instrument): under my observable reading (count to the 10th good
step, minimum 10), the 0.7 x NULL_TWIN clause needs a median <= 9.8, below
the floor of 10, so NO arm - not even CHEAT - can meet the success
criterion. The floor is an artifact of my reading, not of the spec.

Repair (the single one allowed): recovery time = steps after the switch
until the 10-consecutive-good run BEGINS (step index of its first good step;
minimum 1; censored at 200 if no such run completes in the regime). This is
the other literal reading of "steps until |x-r|<0.1 for 10 consecutive
steps". CHEAT injects the new minimum, 1. Nothing else changes: no world
parameter, no threshold, no seed. Rerun everything once (attempt 2). If
attempt 2 is again INSTRUMENT_FAIL, the PREREG makes the world NOT_BUILT.
Attempt 1 distribution shows POSITIVE_CONTROL median equal to CONTROL, so
the positive control may still not be detected after this repair; the repair
addresses only the floor that made the cheat undetectable.

## Attempt 2 (after repair) -- final

INSTRUMENT_FAIL again: CHEAT detected (median 1), POSITIVE_CONTROL not
detected (oracle median 3 = drop-oldest median 3; its distribution is
shifted, p=1.2e-12, but the 0.85 x median clause fails on integer-valued
medians). Per PREREG, a second INSTRUMENT_FAIL -> NOT_BUILT; evaluate.py
applies this rule in code (attempt >= 2). The evaluator was edited after
attempt 2 only to add that rule; no threshold or parameter changed.
Treatment readings are recorded but, per PREREG, not a verdict: medians
TREATMENT 3 / CONTROL 3 / NULL_TWIN 5; treatment vs drop-oldest ratio
1.00, p=0.41 (would meet the failure criterion); pre-switch fraction of
dropped clauses = 1.00 for both TREATMENT and CONTROL.
Total compute ~0.14 CPU core-minutes, 2 attempts.
