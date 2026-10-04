# RSO-METHODS-SLICE-001 -- S1 contract v1.0.0 (FROZEN)

Campaign C-004, packet C-004-T004. Frozen by Palamedes[harry1-679179c6] (claude-opus-5-5), 2026-10-03.
Machine-readable form: contract.json in this directory (frozen: true). Hashes: MANIFEST.md in this directory.

Authority: operator directive 2026-10-03 (roles/Achilles/prompts/2026-10-03_rso_builder_cell/); operator
rulings C-004-OP1 (caps, APPROVED), C-004-OP2 (custody), C-004-OP3 (reviewer), all recorded and CLOSED in
ops/campaigns/C-004/tasks/. Sources: NEXT_ROUND_PLAN_v0.4 (3bd02f393) s2-s6; CLOSURE_REVIEW_v0.4 (09dc8c38b)
C1-C5, F, G.

## 0. What this contract is

The bounded S1 contract the plan asks for (plan s2 S1, s3): claim, state, truth, reset, receipt, anchors,
gate, scope, concrete files and finite bounds, expected outcomes, source/exposure record, trust boundary,
approved caps, challenge minimums and reviewer ownership, with closure amendments C1-C5 written in. It is
committed before any S2 implementation test (plan s2 S1).

The normative text is three documents read together:

    rso/slice001/contract/drafts/A_world_reset_observer.md        (Cadmus, C-004-T001)  world, runtime boundary,
                                                                  truth model, predicates P0-P8, ruler,
                                                                  T01-T08/E06 cases, C3 reset model
    rso/slice001/contract/drafts/B_evidence_receipt_authority.md  (Argus, C-004-T002)   receipt, C1 verdict, C4
                                                                  stages, C5 custody, evidence graph, claims,
                                                                  eligibility, C2 render, E01-E05 cases
    this file                                                     reconciliation R1-R6, which amend the drafts

The drafts are incorporated as they stand at the blob hashes in contract.json `normative_text`. Their header
line "Status: DRAFT. Not frozen." is superseded by this freeze; their text is otherwise unchanged. Precedence
when anything conflicts: R1-R6 below, then contract.json, then draft A for the world/predicate/ruler plane,
then draft B for the evidence plane. The reconciliation found no conflicting shared field between A and B;
R1 and R2 resolve the two questions the drafts left to T004.

## 1. Coverage (plan s3 items and closure amendments)

    item                                         where
    -------------------------------------------  ----------------------------------------------------
    claim                                        A1; contract.json claim
    state (organism, pending channel, schedule)  A2, A3
    truth (world-side, separate from ruler)      A4
    reset vs restart, separate predicates        A5 P3/P4 vs P6; couplings A5
    receipt                                      B3
    anchors + attempted-run inventory            B5, B6.4 G-INV
    gate: typed verdict + reason                 B3.4, B7
    scope: deterministic finite only             A1, B3.4 (no INDETERMINATE slot)
    concrete files + finite bounds               A2, A8, B11; contract.json files, reset_model
    expected outcomes                            A6, B9, B8.2 (author-expected); T005 (independent, R4)
    source / exposure record                     A header, B header, section 3 below
    trust boundary                               B5.4
    approved caps                                section 5 (OP-1)
    challenge minimums + reviewer                section 6 (OP-3)
    C1 execution / authority / outcome           B3.3-B3.5, B7.2
    C2 relative rendering                        B8
    C3 registered reset model (H, R, escapes)    A7, B10
    C4 authority stage                           B4
    C5 anchor keeper / custody                   B5 + R3
    T01-T08, E06                                 A6 (E06 reported, not an exit criterion; closure F)
    E01-E05                                      B9

## 2. Reconciliation decisions

R1  FD-A3 (CHANNEL clamp, P5) ACCEPTED. CHANNEL(M) PASS is an unconditional prerequisite of CL-RET(M); the
    bracketed "[iff T004 keeps FD-A3]" in B7.1 is resolved to "kept", and the B8.2 instrument count of 11
    stands. Reason: the plan's claim (s3) already reads "with an explicitly allowed channel"; P5 makes that
    clause testable rather than adding a new one. Without it draft A's QCARRY -- the right answer carried
    through the FORBIDDEN pending channel -- passes ERASE (only allowed content moves) and would render as
    "carried by the declared allowed component a", which is false. Cost: 24576 clamped runs, small against
    the cap. Coupling stated in A5: P5 is applied through restore and is trusted only with RESTART PASS.
    Uncertainty: P5 assumes the allowed state is settable through restore, which a native runtime may not
    offer. Reversible: dropping P5 removes one predicate and one prerequisite line. Revisit: the reviewer
    rejects it at T005/S3, or the native witness cannot expose a restore of its allowed state.

R2  FD-B3 KEPT. Custody is printed on every rendered claim and is a prerequisite only of CL-CUST. Reason:
    closure C5 and plan s4 already let E01-E05 run and report with custody UNQUALIFIED when no keeper holds
    anchors, so retention is not conditioned on custody in this methods slice. Revisit: the operator wants
    custody on CL-RET (one prerequisite line).

R3  Custody store. OP-2 named the operator as authority and Aporia as registrar, so B5.1's custody field is
    adopted as written. The `store` locator is UNSET at freeze. Aporia fixes it before the first T020 matrix
    run (a delegation from Palamedes); until then every custody result is UNQUALIFIED with
    KEEPER_ROW_MISSING, which the plan allows. Setting the locator is a versioned amendment (v1.0.1) that
    changes that one field only.

R4  Independence of the expected-answer table (C-004-T005). The drafts carry the authors' expected values
    (A6 "expected"/"outcomes" columns, B9 "expected"/"reason codes" columns, B8.2). The independent author
    (Pallas; Dionysus fallback) derives its table from the definitions -- A1-A5, A7, B1-B8, B10 and the case
    list in contract.json -- and COMMITS it before opening those author-expected columns, recording the
    order in EXPOSURE.md. Disagreements between the two tables are the S1 truth check (plan s2 S1); T020
    classifies each one as implementation, contract or table defect and escalates; nothing is resolved
    silently.

R5  Case identities. contract.json `cases` is the registered case list (48 cases). Each case names its
    fixture, world, the draft row that defines it, polarity (true / false / coupling / stated_limit) and
    whether it is an exit criterion (E06 rows are not). Fixture names in the drafts are proposals for the
    S2 packets; behaviour, not name, is binding (A6).

R6  Caps and challenge minimums (sections 5, 6) are copied from the operator rulings and the plan and bind
    every C-004 packet. T019's ledger reads them from contract.json.

## 3. Exposure record of the assembler

Palamedes read, before freezing: both drafts in full; NEXT_ROUND_PLAN_v0.4, SYNTHESIS_AND_DECISIONS_v0.4,
CLOSURE_REVIEW_v0.4 in full; the ASTRA reference_harness README. Palamedes read no code or test of either
corpus and ran no prototype. Palamedes wrote every C-004 packet, so it is not independent of the case list.

## 4. Trust boundary (from B5.4, restated so no report can drop it)

Custody QUALIFIED establishes only that the bytes and complete nodes checked are those registered with the
keeper at the recorded time. It never establishes execution, the truth of an observation, the absence of an
internally consistent fabrication made before registration, or authorship. All S2 anchors in unit tests are
in-memory software fixtures and are never custody evidence.

## 5. Caps (C-004-OP1, APPROVED 2026-10-03)

30 CPU-minutes; 0 GPU-hours; $0 cloud; 100 MB new artifacts; 12 top-level validation launches; one repair
round; 12 aggregate Opus seat-hours; 4 Sonnet seat-hours; 3 reviewer hours; 3 working days. Failures,
retries, mutation children, analysis and confirmation attempts are charged. Stop at the first exhausted cap
and keep partial results (plan s6).

## 6. Challenge minimums and reviewer (plan s5; C-004-OP3)

S3 (C-004-T030): 5 fresh sound cases, 5 fresh broken cases, 10 distinct applicable semantic edits spanning
reset/observer, binding and invalidation. S4 (C-004-T041): 2, 2 and 3 covering touched claim-critical
predicates. Reviewer: Pallas (Fable 5.1); fallback Dionysus. Pallas is a cell member that writes no production
code and is a different model family from the Opus/Sonnet builders; that caveat is printed with every
first-sight and closure record. Attack contents are not frozen here; their rules are plan s5.

## 7. Amendment rule

After this commit the contract changes only by a versioned amendment recorded beside the original (base
doctrine: corrections are annotations). A change to a claim, threshold, case expectation or predicate after
any S2 outcome is observed is a hard gate (MWO-0004 Part 4) and goes to the operator.
