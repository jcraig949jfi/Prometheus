# HT-8a87057933 / W5 -- probe round 3 implementation notes

Prompt: hecate/programs/_prompts/probe_impl_v3.md (sha256 a34a8c61...1685).
Written BEFORE any code ran. spec.json, controls.py, ATTAINABILITY.json and
control_rows.jsonl are frozen and untouched; everything here is in probe/.

## Arms

- CONTROL_REF, POSITIVE_CONTROL, NULL_TWIN, CHEAT: produced by calling the
  frozen `controls.run(arm, seed)` (imported, not copied), seeds 0..9. Their
  rows go to probe/rows.jsonl, NOT to the frozen control_rows.jsonl.
- TREATMENT: `world.run(arm, seed)` is a line-for-line copy of controls.run's
  world loop (same RNG streams seed*1000+{1,2,3}, same switch/task/sensor draws,
  same controller, same FIFO window of 32, same UNSAT trigger, same counters)
  with one extra repair branch. Faithfulness check: world.run is also executed
  for CONTROL_REF, POSITIVE_CONTROL and NULL_TWIN, and every row must equal
  controls.run's row exactly; any mismatch is recorded as an anomaly and the
  outcome becomes INSTRUMENT_FAIL (the treatment would not be in the same code
  path).
- TREATMENT repair (spec.mechanism): while the window is UNSAT: extract ONE MUS
  by deletion -- S := window; for each clause c of the window, oldest-first:
  if S \ {c} is UNSAT, S := S \ {c}; the result S is a minimal unsatisfiable
  subset -- then delete from the window the clause in S with the smallest
  timestamp. Each deletion increments deleted and, if the clause equals the
  true current theta of its channel, valid_deleted. The MUS routine uses only
  the generic SAT test (controls' `sat` semantics); it does not exploit the
  channel structure and never reads theta.

## Readings of the spec (no threshold changed)

1. "Oldest clause in that MUS" = smallest timestamp t. Window order is
   insertion order, so this is also the first MUS member in window order.
2. Success criterion = S1 AND S2 AND S3. Failure = F1 OR F2 OR F3. Values of
   S1..S3 use the frozen controls.clause_values (X = TREATMENT, ref =
   CONTROL_REF of this run); F1 = S1's statistic, F3 = S3's statistic,
   F2 = sum errors(TREATMENT) / sum errors(NULL_TWIN).
3. Reproducibility check (first step of evaluate.py): recompute clause values
   for POSITIVE_CONTROL and NULL_TWIN from rows.jsonl and the attainable
   (PC passes) / discriminating (twin fails) status of every clause, plus
   cheat_detected (CHEAT meets all success clauses AND trips the frozen error
   floor: some seed with errors < 0.5 x switches) and the PC/twin floor flags.
   Any status differing from ATTAINABILITY.json -> INSTRUMENT_FAIL
   (reproducibility), stop. Numeric values are also compared (reported;
   determinism means they should be identical).
4. Outcome, decided in code in this order:
   INSTRUMENT_FAIL if reproducibility fails, or the faithfulness check fails,
   or positive control not detected (PC fails any success clause), or cheat
   not detected, or the TREATMENT trips the frozen error floor (physically
   implausible -> bug);
   CONFOUNDED if NULL_TWIN meets all success clauses;
   SIGNAL if TREATMENT meets S1, S2, S3 and no failure clause holds;
   NULL otherwise (fails the success criterion or meets a failure clause).
   NOT_BUILT is not expected: the mechanism is fully specified.
5. positive_control_detected = POSITIVE_CONTROL meets S1..S3.
   null_twin_meets_success = NULL_TWIN meets S1..S3.

## Seeds and budget

Seeds 0..9 for every arm (the spec's list). One attempt planned; a rerun only
for a described crash or bug. Budget <= 10 CPU core-minutes; the MUS by
deletion is O(|window|^2) per deletion, expected well under 1 core-minute.

## Post-run record (attempt 1, no rerun)

- Importing controls.py wrote W5/__pycache__/ (outside probe/). It was deleted
  and `sys.dont_write_bytecode = True` was added before the import in world.py
  and evaluate.py. No computation changed; rows.jsonl and OUTCOME.json are from
  attempt 1 and were not regenerated.
