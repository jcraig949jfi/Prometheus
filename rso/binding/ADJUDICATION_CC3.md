# C-009 CC3 adjudication (Palamedes, 2026-10-07) -- T030 result -> the one registered repair round

Input: rso/binding/challenge/B1/REPORT.md (Pallas, claude-fable-5-1, Q3), authoritative for its observations.

Ruling on CC3 ("no unresolved applicable survivor on the binding path"): NOT MET. I agree with the reviewer's
reading of the letter: a witnessed edit that survives the full frozen suite is unresolved (only EQUIVALENT resolves
a survivor), and E2-E4 sit in binding.py / evidence.g_inv, which is the binding path. SIBLING_UNREPORTED is a
behavioural admission on BX5; it is not reachable through the witness client as drafted, but BX6 invites runtimes
that give re-executions distinct run ids, so it is applicable. The consumer_for run_id gap is not claim-critical
(BX1 uses the anchored launch either way) but it makes the production path blind to a self-inconsistent bundle,
and fixing it is a one-line wiring change.

FAILED_RETRY_KEEPER: scored INCORRECT under the reviewer's committed check; the reviewer diagnosed it as a
check-design error (the custody object, embedded in every decision, cites a different registered RUN_INVENTORY by
construction). I accept that diagnosis: the frozen code's behaviour there is the correct acceptance BX7 requires.
The score stays as written (2 of 3 sound); the substance is recorded here.

Disposition (CONTRACT.md s3 CC3: one repair round inside C-009, then one fresh 1+1+1 re-check, no further rounds):
  R1  pin E2, E3, E4 with the reviewer's committed fire cases (B1.BROKEN.LAUNCH_IS_NODE_RUN, CHILD_AS_NODE_RUN,
      LEGACY_ROW) in the slice suite AND in the rso/binding unit suite; E2-E4 applied verbatim must be killed.
  R2  BX5b (CONTRACT.md s7, v1.1.0): for every required node WITH a presented receipt, every COMPLETED RECEIPT row
      of that node under the anchored launch must be the cited row; otherwise G-INV FAIL
      RECEIPT_WITHOUT_RUN:<node_id> with BIND_SIBLING_UNREPORTED beside it. FAILED / INTERRUPTED attempts of the
      node remain provenance (B1.SOUND.FAILED_RETRY must still bind identically to its baseline).
  R3  s2_run.consumer_for passes run_id=g.run_id, so the production consume path raises LAUNCH_UNBOUND for a
      run.json that names another launch (B1.PROBE.PRODUCTION_RUNJSON paths agree).
  Regression: consume-only over rso/binding/R1 (the producer is unchanged, so no new produce), stage records
  regenerated and registered, FREEZE_B2. Then the fresh re-check (Pallas, Q3; new shapes, not B1's).

Surfaces now: BX7 CLOSED within coverage; BX1, BX2, BX5 NOT CLOSED pending the repair; producer side unchallenged
(its record is CC2). If the re-check leaves an applicable survivor, C-009 closes INCOMPLETE and the native witness
does not open from it (directive s6); a survivor outside the witness path is recorded, not repaired.
