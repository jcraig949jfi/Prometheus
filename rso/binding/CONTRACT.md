# C-009 RSO-EXEC-BINDING-001 -- contract v1.0.0 (frozen at campaign open)

Written by Palamedes[harry1-679179c6], 2026-10-07, under the operator directive of 2026-10-07 (C-004-OP8;
roles/Palamedes/prompts/2026-10-07_rso_completion_push/01_OPERATOR_DIRECTIVE_verbatim.md). Successor to C-004
(closed INCOMPLETE CLOSURE, rso/slice001/S5_FINAL_DISPOSITION.md); NOT a repair round of C-004.

## 1. Question

Can a first-class execution binding make it impossible for a receipt to qualify while borrowing any of its launch,
node execution, subject, predicate, observer, world/runtime, run status, artifact or custody identity from another
execution -- without the shared machinery knowing anything about a runtime's internal ontology?

## 2. Mechanism (reference: rso/binding/binding.py)

BX1 Launch. Each bundle is produced by exactly one top-level launch. The keeper-registered EVIDENCE_MANIFEST names
    it (`launch_run_id`); the consumer takes the launch from the ANCHORED manifest, never from bundle-supplied files.
    The inventory must hold exactly one TOP_LEVEL row with that run_id, status COMPLETED. A bundle whose own
    run.json names another launch than its anchored manifest: LAUNCH_UNBOUND.
BX2 Node execution. Each receipt cites one run_id. The cited inventory row binds the receipt iff: exactly one row
    carries that run_id; kind RUN, launch_kind RECEIPT; parent_run_id == the anchored launch; status COMPLETED;
    node_id == the receipt's node id (exact string); receipt_sha256 == sha256(receipt canonical bytes).
BX3 One digest binds every recorded dimension. The receipt's canonical bytes include subject, predicate (code
    refs), observer, world (variant, code), producer/runtime code, inputs, outputs (artifact sha256s), oracle and
    claimed execution status. The row records their digest when the node execution finishes. Artifact bytes are
    bound to the receipt by the existing byte check (G-BIND BYTES_MISMATCH), hence to the execution.
BX4 No timestamp decides attribution. AMENDMENT_v1.0.5's operationalisation (end_utc >= created_at) is retired;
    v1.0.5's meaning ("the launch that produced the receipt") is carried by BX1/BX2.
BX5 Historical rows are provenance. Rows whose parent is another launch are never evidence for this bundle and
    never errors; RUN_UNREPORTED (a required node without a presented receipt) reads the anchored launch's rows only.
BX6 Thin federation. rso/binding sees opaque node ids, statuses and bytes. Parsing a node id into subject /
    predicate / observer / world stays in the client (slice001: evidence.parse_node_id). A native runtime client
    supplies canonical receipt bytes and ledger rows; it is never asked what its states mean.
BX7 Custody closes the loop. A claim that relies on G-INV is QUALIFIED only if the inventory it read is the
    keeper-registered RUN_INVENTORY of the anchored manifest's launch (otherwise the rows themselves could be
    forged consistently). The fixture store (V8) remains a logic fixture, never custody evidence.

Slice001 reason spelling is kept: G-INV FAIL RECEIPT_WITHOUT_RUN:<node_id>, with the binding reasons (BIND_*)
recorded beside it so the table's spellings do not change.

## 3. Registered closure condition (fixed before any C-009 outcome)

CC1 Fire cases. Each C-004 survivor shape has an end-to-end G-INV fire case, RED on the FREEZE_R2 code
    (ad6b3fa96) where that code admits it, GREEN on C-009 code: S3.BROKEN.RUN_BORROW, S4.BROKEN.OBS_RUN_BORROW
    (edit X3), S4.PROBE.STALE_RUN, R2 edit Y1 (world), R2.BROKEN.LATER_WINDOW_RUN, R2 OVERLAP_RUN,
    R2 FAILED_ROW_CITED; plus two new shapes: ARTIFACT_SWAP (receipt edited after its run) and LAUNCH_SUBSTITUTION
    (bundle run.json names another launch than its anchored manifest). Mutants X3 and Y1 are killed.
CC2 Regression. A fresh produce of the five slice bundles under the binding (new launches, C-009 ledger); matrix
    vs the independent table identical to S4 (32/8/8, OP-5 items only) and claim-by-claim identical to S4 apart
    from differences predicted in writing before the run.
CC3 Independent challenge. Pallas (Q3) on the frozen binding surface (FREEZE_B1): at least 1 sound, 2 broken and
    2 semantic edits on the binding path, committed before outcomes. Closure: no unresolved applicable survivor on
    the binding path. If CC3 finds one, ONE repair round inside C-009 and ONE fresh re-check (1+1+1) are allowed;
    no further rounds. A survivor outside the path the native witness will use is recorded, not repaired.
CC4 Stage records regenerated for every instrument whose pinned files change, canonical, registered with the
    keeper before the CC2 first check.

C-009 closes when CC1-CC4 hold (then the native retained-information witness opens as its own campaign), or as
INCOMPLETE when its caps or the 72-hour window end first.

## 4. Caps (contract.json; $0; stop at the first exhausted cap; keep partial results)

top-level launches 12; CPU 90 minutes (ledgered, rso/binding/LEDGER.jsonl); new artifacts 150 MB; GPU 0;
cloud $0; repair rounds 1; reviewer hours 2; window: by 2026-10-10T00:25Z at the latest (target 2026-10-08).

## 5. Non-goals

No scheduler, no universal state or cognition schema, no change to world predicates, the expected-answer table, or
the S2 case expectations; C-004 records and freezes are not rewritten.

## 6. v1.0.1 clarification (Palamedes, 2026-10-07, before any CC2/CC3 outcome; CC1 evidence already in)

BX7 as implemented (C-009-T011): the inventory/launch binding is a condition of bundle CUSTODY (INVENTORY_UNBOUND,
LAUNCH_UNBOUND in custody's why; KEEPER_ROW_MISSING:RUN_INVENTORY when unregistered). The slice keeps custody as its
own claim row (CL-CUST), so the S2 table and case expectations are unchanged (s5 non-goal). Reading of BX7 for every
report and for the native witness: a claim that relies on G-INV is QUALIFIED only together with its bundle's custody
QUALIFIED; a G-INV PASS on an unregistered inventory is a logic result, never qualified evidence. No predicate,
threshold or expectation changes. The declared escape (T011 receipt) -- a forged row consistent with an
unregistered inventory binds -- is therefore inside the "not qualified" region, not a qualified admission.

## 7. v1.1.0 amendment -- BX5b (Palamedes, 2026-10-07; POST-OBSERVATION, inside C-009's one registered repair round)

Made after the CC3 challenge (rso/binding/challenge/B1/REPORT.md) observed B1.BROKEN.SIBLING_UNREPORTED admitted;
recorded as a post-observation amendment. The B1 record stands as observed under v1.0.1. Adjudication:
rso/binding/ADJUDICATION_CC3.md.

BX5b For every required node WITH a presented receipt, every COMPLETED RECEIPT row of that node under the anchored
     launch must be the cited row. A second COMPLETED execution of the node under the same launch that the bundle
     does not present: G-INV FAIL RECEIPT_WITHOUT_RUN:<node_id>, binding reason BIND_SIBLING_UNREPORTED. FAILED,
     INTERRUPTED and REFUSED attempts remain provenance (a failed retry before the presented run binds). Rows of
     other launches remain provenance (BX5). No timestamp is read (BX4).
