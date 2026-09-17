# Stage 2 self-critique -- attacking the narrowed Vivarium design before migrations are finalized

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-17 (Vivarium m2-fce3fe0b). Operator's Stage 1/2 direction s19. Each
question is answered against the eight design documents beside this file; the
verdict is KEEP / MODIFY / DROP / ADD and the change, if any, has been applied
to the document named.

## Q1  Are we duplicating Archaeon's runner instead of absorbing stable mechanics?

Evidence: the transaction model absorbs exactly six mechanics (numbered
attempts, parent attempt, design-keyed step key, replayed/recomputed status,
receipt-after-every-step, Idempotency-Key = step key), each with a campaign
ledger id, and declines everything scientific in c2base (seal/prereg
content, reach_row, disposition, funnel, ledger candidates). The step
vocabulary is the loop's OWN stages, not Archaeon's harness steps
(startup/world/publish/import_fetch/record/teardown map onto them but are
not copied). The runner's world/session multiplicity is explicitly a major
version. Where the two could drift -- the step-key derivation -- the
design uses the identical algorithm ("idem:" + sha[:32] over
(design, kind, parts)) so a producer's key and mine coincide by construction.
Verdict: KEEP. One MODIFY: step_key derivation must be a shared function in
one place both can import (viv/stepkey.py, re-exported; Archaeon's
runner.step_key can alias it in the qualification run). Applied to
EXPERIMENT_TRANSACTION_MODEL.md s2.2 by reference.

## Q2  Is start_bundle becoming an untyped junk drawer?

Risk is real: 14 top-level keys, several "producer-declared". Mitigations in
the schema: CLOSED key set per bundle_version (unknown keys refused at
enqueue); every key mandatory with the literal "UNKNOWN" instead of absence;
Vivarium fills only four sub-keys; extension is a new version. Remaining
hazard: `factors` and `schedule.parameters` are free objects. Verdict:
MODIFY: `factors` values are restricted to scalars (string/number/bool) --
a stratum label is a label; `schedule.parameters` keeps free shape but its
hash is what matters and Vivarium never reads inside it. Applied.

## Q3  Is intervention_receipt generic enough to survive future worlds?

Tested against: imports (C3-SFE-10), opcode rewrites (C3-SFE-07), lesions
(C3-SFE-09), a hypothetical message-drop world, a schedule change
(C3-SFE-05 p-then-0). All fit: kind is a string, intended/realised are
key-matched objects, logical time is tagged, targets are ids. Weak point:
`result` derived by numeric equality fails for value-typed interventions
(a schedule change has no count). Verdict: MODIFY: `result` derivation
applies only to numeric keys; a receipt with no numeric key and a
non-error applier answer is APPLIED iff the applier said so, else
UNKNOWN. Applied to INTERVENTION_RECEIPT_SCHEMA.md s1 by note.

## Q4  Does the gate receipt accidentally make Vivarium a scientific judge?

Vivarium evaluates a producer-declared predicate over a producer-named
measurement against a producer-supplied reference and takes the
producer-declared action. The only Vivarium-owned semantics are the
comparison operators and the NOT_EVALUABLE branch -- identical to
outcome_rule today, which has been accepted as mechanical since v0. The
L3-030 shape (a reference equal to the measurement) is recorded, not
refused: refusing would be a judgment. Verdict: KEEP.

## Q5  Can old queue rows retain their exact historical meaning?

Every addition is a new table or a nullable column; the backfill is a
separate reversible migration that writes attempt_number 1 with
termination_reason UNKNOWN and no steps; spec_hash, result_summary, events
are untouched; `viv.cli show` output for an old row is byte-identical
before and after (acceptance test). The ONE semantic change --
BUDGET_EXHAUSTED becomes COMPLETED-and-censored instead of FAILED -- applies
to attempts opened after the migration only; the 79 historical failed rows
keep status failed and error text, and the backfill maps them to
termination_reason UNKNOWN, never to BUDGET_EXHAUSTED by parsing error
strings. Verdict: KEEP, with that parsing explicitly forbidden (added to
TERMINATION_ENVELOPE.md s5 "old rows").

## Q6  Can the outbox grow without bound during a long PEW outage?

Yes, and it should: dropping is losing fossils. Bounded by disk; ~1 MB per
campaign-day of outage at C3 rates; PARK + report at a declared backlog
count (10,000 rows). Verdict: KEEP; ADD a `viv.cli outbox --stats` line to
the MONITORS row so the backlog is a freshness fact, not a surprise.

## Q7  Can attempt/step identity survive process and host restart?

All identity is in PostgreSQL: attempt rows, step rows, keys. A worker that
dies leaves an OPEN attempt whose pid is dead (the dead-man and the
heartbeat's pid make this observable); recovery is STRANDED -> NEW ATTEMPT
with parent pointer; step replay reads prior step rows from the database,
not from a local receipt file (the one place this design is STRONGER than
the runner it absorbs, whose receipt is a file in a worktree). A host
restart loses nothing but the in-flight step, which is RECOMPUTED under the
new attempt unless its kind declares it replayable and its verifier passes.
Verdict: KEEP.

## Q8  Are we recording enough for selection-vs-construction experiments without storing every organism-generation?

C4-2 needs: the population that ENTERED (bundle.population manifest_hash +
lineage_composition + gen0_provenance), the interventions (receipts), the
per-transition probes (the kind's observations, which the producer designs),
and the realised origin shares (supplied in receipts / observations).
Vivarium stores pointers (manifest_hash, post_ref) and the numbers the
applier reports, never the trace. Whether that is ENOUGH is Proteus's
manifest contract (s12) and Archaeon's probe design; the slots exist.
Verdict: KEEP; the gap is named as UNKNOWN until Proteus answers A7.

## Q9  Are we accidentally coupling Vivarium to Campaign 3 vocabulary?

Audit of the eight documents for C3 terms used as TYPES: "reward_mode" (an
example value in START_BUNDLE evaluator, not a key), "stop-on-solve" (an
EXAMPLE of a stop condition; the envelope's field is stopped_on_condition
with a producer id), "origin share" (a supplied realised measurement, key
named by the producer), FLOOR/SHELF/SUMMIT (appear only in "what this is
not"). Closed vocabularies I own: step kinds (loop stages), termination
reasons (execution facts), outbox event kinds (execution facts), receipt
results (APPLIED/PARTIAL/...), gate results (PASS/FAIL/NOT_EVALUABLE). None
is a landscape or a capability word. Verdict: KEEP.

## Q10 (added) Does anything here need the coordinated window, and what does not?

Needs the window: migrations 006-009 (schema), the loop change that opens
attempts/steps, the outbox switch (stage 6), the termination semantic
change, deploying the 09-16 fixes, credential bootstrap on the production
ledger. Does not: the documents, the shared stepkey module, tests against
throwaway schemas, the deliverer as a program (not registered), the
PRODUCTION.json draft. Verdict: ADD -- this split is the deploy plan's first
line.

## Summary

    KEEP    transaction model, gate receipt, termination envelope, outbox growth policy, identity-in-database, vocabulary audit
    MODIFY  shared step-key module (Q1); factors scalars-only (Q2); intervention result derivation for non-numeric keys (Q3)
    DROP    nothing this pass
    ADD     outbox backlog on the MONITORS row (Q6); explicit ban on parsing old error strings into termination reasons (Q5);
            the window / no-window split (Q10)
