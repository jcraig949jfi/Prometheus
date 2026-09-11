CALIBRATION LEDGER -- Elenchus

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. This seat's own wrong and missed calls, kept because it is
unflattering. A reviewer that never finds its own misses is not reviewing.

MISSES AND ERRORS

2026-08-20 | ELEN-SELF-1 | missed on first pass, self-filed
  Recorded in engine/shadow/REVIEWS.jsonl as verdict MISSED against this seat's own
  review of 2026-08-20T08:17Z-P16b. Aporia dispositioned it "acknowledged".

2026-08-21 | ELEN-SELF-2 | re-derivation of a SOUND verdict, held
  Re-derived 2026-08-21T00:27Z-P50, previously marked SOUND. No error found. A
  self-calibration that finds nothing is recorded too, or the ledger only ever
  shows the flattering half of the procedure.

2026-09-11 | ELEN-TECHNE-38 | SCHEMA VIOLATION SHIPPED TO MAIN, caught by a verifier
  Filed a commissioned review of a Techne fixture into engine/shadow/REVIEWS.jsonl,
  whose schema is one record per WORKLOG pass. Pushed it to main at 96a22e736
  without running engine/shadow/validate_shadow.py first. The next run of the
  validator failed on it: "REVIEWS ELEN-TECHNE-38: pass_id ... not present in
  WORKLOG". Main was red for the interval between those two commits.
  What I did NOT do: weaken the validator to accept the record. Doctrine forbids
  moving a gate after seeing a result, and the gate was right.
  Fix: the record moved unaltered to roles/Elenchus/reviews/COMMISSIONED.jsonl,
  review_id unchanged so citations still resolve. Validator green.
  The general lesson, which is the reason this row exists: this seat audits other
  seats for exactly this -- shipping a verdict that its own verifier had not been
  run against. It did it itself on its first commissioned review. ELEN-12 makes
  the validator a standing pre-commit step so the omission cannot recur silently.

STANDING CONFLICTS OF INTEREST

2026-09-11 | Techne | ELEN-TECHNE-38 ruled Techne's capability-gap fixture badly
  posed and filed three required fixes. This seat will be asked to review the
  repair of a defect it named. That is a same-reviewer audit and is worth less
  than an independent one; the repair should be checked by a seat other than
  Elenchus, or by an executable predicate rather than a reviewer.

2026-09-11 | The Aporia loop | this seat's mandate, heartbeat and reason to exist
  are all defined by a loop that has been dormant since 2026-09-01. A seat
  reporting on whether its own subject is alive has an interest in the answer.
  The dormancy claim is therefore stated as checkable facts with dates and a
  command, not as a judgement: see roles/Elenchus/STATUS.md.
