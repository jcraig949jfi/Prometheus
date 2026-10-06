+============================================================================+
| C-004 RSO-METHODS-SLICE-001 -- S5 METHODS REPORT                           |
| Author: Palamedes (Lead RSO Engineer, coordinator), harry1/M4,             |
|         claude-opus-5-5, instance harry1-679179c6                          |
| Date:   2026-10-06                                                         |
| For:    the operator (HITL) and external reviewers                         |
| Status: S1-S4 executed. Exit criteria NOT MET -> INCOMPLETE CLOSURE.       |
|         Methods result only; no scientific claim. Operator decision OP6.   |
| Self-contained: no repository access needed to read this.                  |
+============================================================================+

0. SUMMARY
-----------
The slice asked one methods question: can one small evidence path admit
lawful retained information, reject a forbidden delayed leak without
destroying allowed state, and refuse a claim whose receipt provenance was
rewritten? On a finite world of 4096 histories, the built path does all
three: lawful retention is admitted, delayed and split leaks are rejected,
rewritten provenance is refused, and outcome values agree with an
independent answer key on every registered case.

The independent attack found real defects. One repair round fixed every
S3 finding as S3 defined it, and a fresh closure challenge then found two
open items in the evidence plane. C1 is a false rejection when one bundle
is produced twice: the earlier manifest is chosen. C2 is a missing fire
test. By the plan's own exit rule this is INCOMPLETE CLOSURE: not
acceptance, and not a failure of the slice.

1. WHAT WAS BUILT, AND IN WHAT ORDER
-------------------------------------
- S1 contract v1.0.0 frozen at 595916f9c, before any S2 file existed. 48
  registered cases; closure amendments C1-C5 written in. Amendments, each
  recorded beside the original:
    v1.0.1  spellings, formats, omissions; before any S2 code (3287bff17)
    v1.0.2  custody store locator, M1 Postgres, hash-chained (OP-2)
    v1.0.3  CPU cap 30 -> 120 CPU-minutes (OP-4)
    v1.0.4  launch cap 12 -> 20, repair window only (OP-7)
- Independent expected-answer table: Pallas (Fable 5.1), 48 rows. It was
  committed before its author read the authors' expected columns.
- S2 implementation: 24 modules and 17 test files, frozen in FREEZE_S2
  (c91e39e85). Stage records were registered with the custody keeper.
- S3 first-sight challenge (Pallas): its exposure record and attack set were
  committed before any result. No test body was ever opened.
- S4: one repair round (Argus, Cadmus), a full regression rerun of all five
  S2 bundles, FREEZE_S4 (8b98c2702), and a fresh closure challenge.

2. RESULTS, WITH DENOMINATORS
------------------------------
Independent table vs authors' columns (T005), primary value:
  43 agree, 0 contradict, 5 unscorable, of 48. Six agreements are not
  independent.

S2 matrix vs the independent table (real run, live store):
  48 registered, 45 gating. AGREE 32, PARTIAL 8, DISAGREE 8.
  Outcome values agree in every case. OP-5 classified the 8 as follows:
    TABLE         X02, X06 (reason, standing), X18 (x3 cases), X19 (x3)
    CONTRACT GAP  X06 authority of an absent receipt (carried here)
  Real-store custody: CL-CUST(G0) ELIGIBLE (custody QUALIFIED).

S3 first sight (frozen S2 code):
  sound cases   4 of 5     broken cases   3 of 5     controls 2 of 2
  edits         10 proposed / 10 applicable / 10 executed /
                5 killed / 5 survived / 0 equivalent / 0 error
  findings
    F1  G-RECOMP falsely accuses an honest producer: the trace clamp and
        the outcome clamp restore differently
    F2  custody QUALIFIED for a bundle anchored to another bundle's
        manifest
    F3  G-INV admits a receipt that borrows another node's run:
        a FALSE ADMISSION
  probe: a cell naming a false measurement version still binds

S4 repair (one round): 4 implementation fixes and 5 fire tests or
fixtures. The S3 cases replayed on the repaired code:
  sound 5 of 5, broken 5 of 5, controls 2 of 2. All 5 S3 survivors are now
  killed.
S4 regression on the repaired code, all five bundles:
  vs the table: identical to S2 (32 / 8 / 8, OP-5 items only)
  vs S2, every claim of every bundle: 1 difference, the predicted one.
    EXTRA CL-RET(HCOUNT) G-RECOMP went FAIL -> PASS (F1 fixed); no
    eligibility changed.

S4 fresh closure (frozen repaired code):
  sound cases   1 of 2     broken cases   2 of 2     controls 2 of 2
  edits         3 executed / 2 killed / 1 survived / 0 equivalent
  open
    C1  FALSE REJECTION. The live registry holds two manifests with one
        node set (S2 G0 and S4 G0). The repaired anchor choice takes the
        earliest, so a reproduced bundle fails G-BIND on 5 claims while
        custody reads QUALIFIED on the wrong row. F2's repair closed the
        S3 case, not the case the registry is actually in.
    C2  edit X3 survived the full suite: the G-INV run check is not
        pinned per observer. A missing fire test, not a code defect.
  probe: a receipt citing an earlier window's run of its own node is
         admitted (B3.3 vs B6.4 reading; see 4)

Exit (plan s5): "zero unresolved false admissions/rejections ... no
unresolved applicable survivor on a claim-critical path". NOT MET (C1, C2).

3. AUTHORITY STAGES (closure C4)
---------------------------------
Every instrument is AUTHOR_TESTED, with a registered stage record. S3 gives
FIRST_SIGHT_CHALLENGED components for P0, P2-P7, G-BIND, G-INV, G-RECOMP
and authority/invalidation; P1 and P8 were not challenged.
Candidates for CLOSED_AFTER_REPAIR, i.e. a surface the repair touched,
re-challenged with no open item: the CHANNEL clamp surface (F1) and G-RECOMP.
Not closable: G-BIND (anchors) and custody (C1); G-INV (C2).
The registrar records stages only after OP6.

4. CARRIED FOR RECONCILIATION (no repair, no amendment before now)
-------------------------------------------------------------------
Table corrections: X02, X06 (x2), X18, X19.
Contract gaps and wording:
  X06 authority of an absent receipt
  X16 Q = 8 is not the reachable maximum (6 is)
  X17 no PASS reason forms
  B6.3 lacks IDENTITY_MISMATCH:node_id
  G01 fixture definitions share the blinded column
  B3.3 vs B6.4 on a cumulative ledger: is an earlier window's run of the
    same node valid for a later receipt? (the S4 probe; T045 O-S4-1)
Observations:
  O1 PRESERVE is vacuous for a runtime whose reset writes `a`
  tests that pin the live contract version broke at 3 amendments
Process: an expected-row seeding bug in my own driver was caught before
the real run; a stage-record identity mismatch (file bytes vs canonical)
was caught before the real run.

5. COSTS (caps: OP-1, OP-4, OP-7)
----------------------------------
  launches        15 of 20: S2/S3 window 8 of the original 12;
                  repair window 7 (S4 regression 5, closure 2)
  ledgered CPU    48.7 of 80 minutes; plus 40 booked development minutes,
                  88.7 of 120 in total
  artifacts       31.8 MB of 100 MB
  GPU / cloud     0 / $0
  reviewer time   about 1 h 40 m of 3 h (T005 20 m, S3 55 m, S4 25 m)
  seat-hours      not metered; estimate only, no claim made
  elapsed         about 2.3 of 3 working days since OP-1

6. WHAT THIS DOES AND DOES NOT ESTABLISH
-----------------------------------------
Does: on one finite world, an evidence path whose verdicts agree with an
independent answer key on every outcome value. It separates execution,
authority and outcome. It refuses unbounded quantifiers, binds complete
nodes against keeper anchors, and invalidates descendants on withdrawal.
Its gates have been first-sight challenged and partly closed after one
repair.
Does NOT: say anything about native runtimes, unlike physics, stochastic
settings, recursion or any class of organisms. Custody establishes byte
identity since registration only: every seat is the same database
superuser, so tampering is detected, not prevented. S3's 10 cases and 10
edits and S4's 4 cases and 3 edits buy a small challenge, not an error
rate. Reviewer and table author are the same model family.

7. THE DECISION (OP6), WITH PALAMEDES'S LEAN
---------------------------------------------
  (a) Accept the narrower scope. Close as INCOMPLETE CLOSURE with C1/C2
      recorded. Custody and G-BIND anchoring of reproduced bundles, and
      G-INV per-observer attribution, are SUSPENDED for any claim.
  (b) Authorize one bounded second repair: C1 (choose the manifest whose
      node artifacts match the presented receipts) and C2 (pin the
      per-observer check). Also rule on the B3.3/B6.4 probe. Then a 1+1+1
      closure re-check. Fits the remaining caps: 5 launches, about 31
      ledgered CPU-minutes, about 1 h 20 m reviewer time.
  (c) Authorize the native retained-information witness now, under (a)'s
      narrowed scope, as its own campaign and budget.
  (d) Stop.
Lean: (b), then (c). C1 is a false rejection in the custody path that the
registry already exhibits, and its fix is small. A native witness built
on a known custody defect would inherit it.

8. QUESTIONS FOR THE REVIEWER (written to resist agreement)
------------------------------------------------------------
Q1  The S2 matrix agreed on every outcome value, yet S3 found a false
    admission and S4 a false rejection the matrix could not see. What
    does that say about the matrix as an instrument?
Q2  F2's repair passed its own tests and the S3 replay, then failed on the
    registry's real state. Should closure cases be drawn from the live
    registry by rule?
Q3  Is a toy that needed amendments to its CPU and launch caps a fair test
    of the plan's budget discipline, or evidence the caps were never
    calibrated?
Q4  What, beyond C1/C2, would make you refuse a native witness built on
    this path?
Q5  Is this worth continuing at all?

9. ARTIFACTS
------------
rso/slice001/contract/ (v1.0.0-1.0.4)   rso/slice001/expected/ (T005)
rso/slice001/s2/ (S2 run, MATRIX, CLASSIFICATION)   FREEZE_S2.md
rso/slice001/challenge/S3/REPORT.md     ops/campaigns/C-004/TRIAGE_S3.md
rso/slice001/s4/ (regression, MATRIX, REGRESSION.md)   FREEZE_S4.md
rso/slice001/challenge/S4/REPORT.md     ops/campaigns/C-004/DISAGREEMENTS.md
Operator rulings: ops/campaigns/C-004/tasks/C-004-OP1 .. OP7

+============================================================================+
| "Not worth continuing" remains a first-class answer. If the reviewer       |
| judges that a finite toy cannot discriminate the defects that matter for a |
| native witness, say so; the plan says publish the scoped result and stop.  |
+============================================================================+
