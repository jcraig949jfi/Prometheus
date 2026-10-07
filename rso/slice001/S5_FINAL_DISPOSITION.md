+============================================================================+
| C-004 RSO-METHODS-SLICE-001 -- FINAL DISPOSITION (S5 addendum)             |
| Author: Palamedes (coordinator), harry1/M4, claude-opus-5-5,               |
|         instance harry1-679179c6                                           |
| Date:   2026-10-07                                                         |
| For:    the operator (HITL) and external reviewers                         |
| Status: CLOSED -- INCOMPLETE CLOSURE (scoped result). Methods only.        |
| Self-contained; extends S5_REPORT.md (unchanged) with OP6's outcome.       |
+============================================================================+

0. DISPOSITION
---------------
C-004 closes as INCOMPLETE CLOSURE. That is the result it earned: the slice
built a working evidence path whose verdict values agree with an
independent answer key on every registered case, and two rounds of
independent attack showed that its run-attribution gate (G-INV) is still
not closed. The native-witness condition of OP6 ("only if that re-check
closes C1/C2 with no new unresolved claim-critical survivor") is NOT met.
OP6 authorizes no third repair round, and none is opened here. The
successor is a separate campaign (C-009, operator directive of
2026-10-07, roles/Palamedes/prompts/2026-10-07_rso_completion_push/).

All earlier records are preserved unchanged: FREEZE_S2.md, FREEZE_S4.md,
FREEZE_R2.md, challenge/S3, challenge/S4, challenge/R2, S5_REPORT.md.

1. WHAT HAPPENED AFTER S5 (OP6 = (b), then conditionally (c))
--------------------------------------------------------------
- AMENDMENT_v1.0.5 (post-observation operator amendment): B3.3 governs;
  an earlier window's run of the same node does not satisfy a later
  receipt. The S4 record (STALE_RUN admitted under v1.0.4) stands.
- T046 (Argus), second and final repair: C1 manifest choice by artifact
  match; C2 G-INV run bound to the receipt's observer; B3.3 refused an
  earlier-window run, operationalised as run.end_utc >= receipt.created_at.
  Author RED then GREEN; suite 393 OK on the merge.
- T047 (Palamedes): consume-only regression of the S4 bundles; no change
  in outcome, eligibility, standing or custody status over 30 claims; the
  table matrix identical (32/8/8, OP-5 items only). FREEZE_R2.
- T048 (Pallas, claude-fable-5-1, Q3): fresh 1 sound + 1 broken + 1 edit,
  plus 2 unscored probes, committed before outcomes (c8f702862).

2. T048 RESULT (authoritative; challenge/R2/REPORT.md)
-------------------------------------------------------
  sound   1 of 1 correct   (three keeper manifests; anchors to the right one)
  broken  0 of 1 correct   LATER_WINDOW_RUN admitted (G-INV PASS)
  edit    1 executed, 0 killed, 1 survived: Y1 (G-INV ignores the world
          component) survives all 393 tests; witness shows a STANDARD
          receipt admitted on a TWINWORLD run
  probes  2 admitted: OVERLAP_RUN (declared FD-T046-1), FAILED_ROW_CITED
          (undeclared: a FAILED row of the receipt's node is accepted)

  C1    CLOSED within the re-check
  C2    NOT CLOSED (world axis unpinned)
  B3.3  NOT CLOSED (the time bound is one-sided; binds nothing to the
        receipt's own launch)
  Design fact (Pallas): in real bundles a receipt's created_at PRECEDES its
  own run's start (bundle build time), so no timestamp rule can identify
  the producing launch. The only honest bound is the bundle's own launch.

3. FINAL STATE OF EACH SURFACE
-------------------------------
  surface                         state at close
  ------------------------------  -------------------------------------------
  world predicates P0-P8          AUTHOR_TESTED; P0, P2-P7 first-sight
                                  challenged (S3); P1, P8 not challenged
  CHANNEL clamp (F1) / G-RECOMP   candidate CLOSED_AFTER_REPAIR (S4: repaired,
                                  re-challenged, no open item)
  custody + G-BIND anchor (C1)    candidate CLOSED_AFTER_REPAIR (R2 closed
                                  it; one sound case, no edit on it)
  G-INV run attribution           NOT CLOSED: Y1 (world), LATER_WINDOW_RUN,
                                  FAILED_ROW_CITED, OVERLAP_RUN open
  The stage-record files are not rewritten in C-004. Every claim whose
  qualification depends on G-INV attributing a receipt to its own launch
  is, by this disposition, NOT QUALIFIED for that attribution. In the live
  registry's actual state today (one world variant, the slice's own
  launches) no wrong verdict was observed; the defect is demonstrated on
  constructed inventories.

4. WHAT C-004 ESTABLISHED (carried forward, operator directive s2)
-------------------------------------------------------------------
  - The finite matrix is useful for conformance, insufficient as an
    adversarial validator (it agreed on every value; S3/S4/R2 still found
    a false admission, a false rejection and four admissions).
  - Live keeper/registry state finds failures static matrices miss (C1).
  - Manifest selection must bind actual artifacts, not node sets (C1).
  - Execution evidence must bind the complete identity of what ran; the
    observer alone is insufficient if the world can be substituted (Y1).
  - Temporal heuristics do not establish which launch produced a receipt
    (LATER_WINDOW_RUN, OVERLAP_RUN); run status must be bound (FAILED_ROW).
  - Cumulative provenance must not become an accidental evidence oracle
    (O-S4-1, STALE_RUN).
  - Author regression is not final authority for claim-critical machinery
    (each repair passed its author's tests and its replay, then failed
    fresh attack).

5. COSTS (final; caps OP-1, OP-4, OP-7)
----------------------------------------
  launches        17 of 20 (S2/S3 8; S4 7; R2 2)
  ledgered CPU    3187.2 s = 53.1 of 80 ledgered minutes; plus 40 booked
                  development minutes = 93.1 of 120
  artifacts       31.8 MB of 100 MB        GPU / cloud   0 / $0
  repair rounds   2 (the second by OP6)
  reviewer time   about 2 h 10 m of 3 h (T005 20 m, S3 55 m, S4 25 m,
                  R2 30 m)
  seat-hours      not metered; no claim
  elapsed         OP-1 2026-10-03T21:48Z to close 2026-10-07T00:4xZ: about
                  3.1 calendar days against the 3-working-day cap. Recorded
                  as a slight overrun, not separately authorized.

6. WHAT THIS DOES NOT ESTABLISH
--------------------------------
Nothing about native runtimes, stochastic settings or any organism class.
No claim of a qualified run-attribution gate. The challenge sizes (S3 10+10,
S4 4+3, R2 2+1+2) buy a small challenge, not an error rate; every reviewer
and the table author are of the builders' model vendor family.

7. NEXT
--------
C-009 RSO-EXEC-BINDING-001 (successor, not a repair round of C-004): a
first-class execution binding so that a receipt cannot borrow launch,
node execution, subject, predicate, observer, world/runtime, status,
artifact or custody identity from another execution. If C-009 closes, the
native retained-information witness opens as its own campaign.

+============================================================================+
| "Not worth continuing" remains a first-class answer for the successor.     |
+============================================================================+
