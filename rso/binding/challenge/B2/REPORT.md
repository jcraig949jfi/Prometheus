# C-009-T034 CC3 re-check on FREEZE_B2 -- REPORT

Reviewer: Pallas[harry1-2b71b1e1], claude-fable-5-1 (Q3), harry1 (M4), headless (comms boot 07:17Z, launches
07:36Z-07:44Z); finished by Pallas[harry1-2a918949], same model, host and lease (comms boot 08:17Z), after the first
instance ended its turn with the acceptance run in the background and the headless session exited. 2026-10-07. Frozen surface: rso/binding/FREEZE_B2.md (code 1b69dd04a;
rso/binding v1.1.0 = v1.0.0 + s6 v1.0.1 + s7 BX5b); 48 hashes verified three ways before the set was written (at
HEAD 0ad2d1a6f, at 1b69dd04a, LF-normalised working tree: 48 equal, 0 mismatch each). Branch pallas/c009-t034 from
0ad2d1a6f. Caveat printed with every closure record: cell member, writes no production code, same vendor family as
the builders (T031 claude-opus-5-5, T033 claude-opus-5-5). Exposure: EXPOSURE.md beside this file (the binding
unit test file was read, including T031's new classes; no file under rso/slice001/tests/ or rso/witness/tests/ was
opened; the witness client and runner were read before the set because the packet asks for applicability to them).

## 1. Ordering evidence (git; times UTC)

    6b02d25a0  exposure record EXPOSURE.md (branch)                                           07:27:58Z
    13d7c344c  claim of C-009-T034 (CLAIMED, LEASE.json; main)                                 ~07:30Z
    a9ef80a07  set: cases.py, expected.json, edits.json, witnesses.py, run_cases.py,
               run_mutation.py, CHALLENGE_SET.md with predictions (branch, pushed)             07:35:46Z
    63d4c06c5  state: IMPLEMENTING (main)                                                      ~07:36Z
    build chk  run_cases.py --check-build: constructs both cases on both bases, calls no consumer,
               observes no verdict (rows check_build_2026-10-07T073607Z.jsonl; unledgered)     07:36:07Z
    launch 1   run_cases.py     B2-CASES-20261007T073656Z-6888                        07:36:56Z-07:36:59Z
    launch 2   run_mutation.py  B2-MUTATION-20261007T073714Z-10300, 3 children        07:37:14Z-07:43:44Z
    acceptance the three suites on the merged tree 83bc92338, first started in the BACKGROUND by harry1-2b71b1e1
               (died with the session; its partial acceptance_stdout.txt is REPLACED, not kept), then RE-RUN in the
               FOREGROUND by harry1-2a918949, one suite per process in the command's order: slice001 426 tests OK
               (skipped=1, 263.5 s), binding 21 OK, witness 81 OK (23.1 s); 528 run, 0 failures
               (acceptance_stdout.txt)                                                       08:19:22Z-08:24:34Z
    (then)     results rows, ledger rows, this report, journal, work state, comms bodies -- one commit on the
               branch (merged origin/main 63d4c06c5, which holds only this packet's own state commits; origin/main
               2c292d3c4 at the resume changed nothing under rso/); receipt, GREEN (carrying the resume note: the
               lifecycle refuses IMPLEMENTING -> IMPLEMENTING) and INTEGRATION_READY as state commits on main.

The four data files (cases.py, expected.json, edits.json, witnesses.py) are byte-identical to a9ef80a07
(`git diff --quiet a9ef80a07 HEAD -- <the four>`: identical). No driver repair was needed. Two of the three
permitted launches were used; the third was held for a driver-repair rerun and is unused. No launch was torn.

## 2. Score (denominators are the set's: 1 sound, 1 broken, 1 edit, 2 controls; no probe)

Every case ran on two bases: r1 (the committed C-009 fresh produce rso/binding/R1/G0: real executions, 26-row
inventory, producer-bound) and synthetic (fixtures.evidence_cases G0). The r1 base is fully scored; on the
synthetic base the claim-type checks are recorded unscored (B1's finding: G-RECOMP fails on the fixture traces for
every CL-RET claim, baseline included) and the line, witness_binding and identical checks are scored.

    r1 base        sound 1 of 1   broken 0 of 1   controls 2 of 2
    synthetic      sound 1 of 1   broken 0 of 1   controls 2 of 2

    SOUND  FAILED_RERUN_DIGEST   CORRECT   G-INV PASS; every decision byte-identical to the baseline (both bases).
                                           A FAILED re-execution AFTER the cited row, carrying a digest, is provenance.
    BROKEN NESTED_SIBLING        ADMITTED  the survivor of this set (s4): G-INV PASS "inventory terminal; every run
                                           reported", witness null; CL-RET(REG) ELIGIBLE / SATISFIED on r1; PKTD, LAGD,
                                           CAL, TWIN identical to the baseline (both bases).

    edits  proposed 1 | applicable 1 | duplicate 0 | executed 1 | killed 0 | survived 1 | equivalent 0 |
           unresolved 0 | error 0 | timeout 0 | cap not exhausted
           baseline (targeted suite, 218 tests): rso.binding.binding child PASSED 42.3 s
           E6 digestless-sibling-ignored  SURVIVED  targeted 218 run / 0 failures (51.5 s); FULL frozen suite (the
                                                    three acceptance suites, 528 run, 0 failures, 1 skipped; 295.2 s);
                                                    witness DIFFERS: (['BIND_SIBLING_UNREPORTED'],
                                                    ['launch-A/rcpt:REG:PRESERVE:STANDARD#2'], []) -> ([], [], []).
                                                    NOT_EQUIVALENT_WITNESSED.

Predictions (CHALLENGE_SET.md, before any outcome): 2 of 2 cases (ACCEPTED; ADMITTED), 1 of 1 edit (SURVIVES both
suites, witness differs). Calibration ledger: S3/S4/R2 5/5, 4/4+2/3, 5/5; B1 9/9 and 5/5 with one check-design
error; B2 2/2 and 1/1.

## 3. CLOSED / NOT CLOSED per binding surface (FREEZE_B2's list: binding.py; evidence.py g_inv / launch_unbound /
custody; producer side ledger.py + s2_bundle.py)

    BX1  launch identity (binding.launch_reasons; evidence.launch_unbound)
         CLOSED within coverage. B1's survivor E2 is killed by both frozen suites (T031 receipt: E2 verbatim after
         the repair KILLED in test_evidence and in the binding suite; B1.BROKEN.LAUNCH_IS_NODE_RUN is in the G-INV
         fire record and B1Pins). T033's regression held (R1/R2CHECK/REGRESSION.md Q1-Q4). This set places no fresh
         BX1 case or edit (s4 of CHALLENGE_SET.md says why: every dimension BX1 names is implemented literally and
         now pinned); both of this set's cases leave the anchored launch's TOP_LEVEL row exactly as the baseline
         and bind as the baseline. No survivor on this surface. Coverage boundary stated: no fresh shape beyond
         B1's and CC1's was tried.

    BX2  cited-row binding (binding.binding_reasons; evidence.g_inv's reading of it)
         CLOSED within coverage. B1's survivors E3 and E4 are killed by the frozen suites (T031: E3 in both suites;
         E4 in test_evidence, the binding suite gaining B1Pins.test_e4_missing_digest_alone); CHILD_AS_NODE_RUN and
         LEGACY_ROW are in the G-INV fire record. In this set the victim's cited row is sound in both cases and
         binds identically to the baseline with a digest-bearing extra row of the same node beside it (the sound
         case): BX2 does not confuse a FAILED row's digest with the cited row's. Same coverage boundary as BX1.

    BX5 / BX5b  own-launch rows, the unreported-run check, the sibling rule (binding.own_launch_rows,
         unreported_siblings, sibling_reasons; g_inv RUN_UNREPORTED and the BX5b branch)
         NOT CLOSED, two survivors:
           (a) B2.BROKEN.NESTED_SIBLING, behavioural, ADMITTED on both bases: a second COMPLETED RECEIPT row of a
               presented required node, recording the digest of an unpresented FAIL receipt, is invisible to BX5b
               when its parent_run_id is the presented execution's own row rather than the launch (s4). Class:
               contract-vocabulary gap ("under the anchored launch", CONTRACT s7, is implemented as parent == launch,
               BX2's definition of a node execution row; the contract never says what a row whose parent is a node
               execution of the launch is). Applicability: s5 -- NOT reachable through the native witness path as
               committed; reachable by an adapter that nests.
           (b) E6-digestless-sibling-ignored, witnessed edit survivor of all 528 frozen tests: BX5b as implemented
               reads status, kind, node and parent of a sibling, never its digest, and no frozen test builds a
               COMPLETED sibling WITHOUT a digest. Class: test-coverage (the frozen code refuses the shape; nothing
               pins it). The reusable fixture is witnesses.e6 (module level); an end-to-end fire case would be
               B1.BROKEN.SIBLING_UNREPORTED with the sibling's receipt_sha256 removed (not in this set: the packet
               allows one broken case, spent on (a)).
         The sound direction holds: FAILED_RERUN_DIGEST is accepted identically to the baseline, so BX5b's
         status filter and BX4's order-blindness are as the contract says, and a digest on a FAILED row does not
         make it a sibling (the false-rejection risk of a stricter implementation is absent).

    BX7  custody -- not in this packet's list (CLOSED within coverage at B1; unchanged code; T033 Q3 held).

    producer side (ledger.py + s2_bundle.py)
         UNCHALLENGED by this set, as by B1: consumer-only cases and edit. The controls (producer-bound r1 rows bind
         under the frozen consumer, 4/4 and 3/3) and T033's consume-only regression are the record. Read in full
         for applicability (s5); nothing found that a case here would measure.

CC3's registered closure condition (CONTRACT.md s3): "no unresolved applicable survivor on the binding path". This
re-check leaves, for adjudication (there is no further repair round; ADJUDICATION_CC3.md: an applicable survivor
closes C-009 INCOMPLETE, a survivor outside the witness path is recorded, not repaired):
  1 behavioural survivor      NESTED_SIBLING on BX5b -- NOT on the path the native witness as committed uses (s5);
                              applicable-conditional to a nesting adapter, which no committed runtime is.
  1 witnessed edit survivor   E6 on BX5b -- test-coverage class; the frozen code refuses the shape; the witness path
                              cannot produce the shape (s5); a later edit to unreported_siblings could introduce the
                              fault without a test failing.
This reviewer's reading, for the adjudicator: neither survivor is reachable by rso/witness/run_witness.py as
committed (s5 gives the two mechanical reasons), so on the contract's own rule both are recorded, not repaired, and
the letter of CC3 turns on whether "applicable" means the witness path (then met) or any BX6 adapter (then not met,
by (a)). I state both readings and decide neither; the base doctrine says no LLM adjudicates.

## 4. The admitted nested sibling, in detail (rows: results_cases.jsonl, case_claims B2.BROKEN.NESTED_SIBLING)

r1 base. The victim is REG's PRESERVE receipt; its own row g0-ce1f8716cc5d-14660/rcpt:REG:PRESERVE:STANDARD is fully
bound (parent = the anchored launch, kind RECEIPT, COMPLETED, exact node id, digest of the presented bytes). The case
inserts directly after it a second COMPLETED RECEIPT row of the SAME node, run_id ...~nested, parent_run_id = the
victim's own run id (not the launch), recording the digest 3e1cf84ecfed8900... of a receipt that was NOT presented
(the victim's receipt with execution.run_id = that row and outcome PRESERVE FAIL; hidden.how = FAIL_TRANSPLANT on
both bases; synthetic digest 38d44567f308f655...). Terminal count updated (28 rows). The consumer: G-INV PASS
"inventory terminal; every run reported"; CL-RET(REG) ELIGIBLE / SATISFIED; every other claim byte-identical to
the baseline -- the admission is the only effect. Custody is UNQUALIFIED here (KEEPER_ROW_MISSING on the stage-rows-
only store, as in every broken case of S3/S4/R2/B1), so by v1.0.1 this is a logic result, never qualified evidence;
a registered inventory holding both rows would qualify just the same, because custody checks the inventory's
registration and launch binding, not the parentage of its rows.

Why the repaired code admits it: binding.unreported_siblings reads own_launch_rows, which keeps rows with
parent_run_id == the anchored launch and launch_kind RECEIPT; the nested row's parent is a node execution, so it is
neither a sibling (BX5b) nor an own-launch row (BX5 RUN_UNREPORTED), and BX2 never looks at rows other than the
cited one. Under the frozen code it is exactly as invisible as B1's SIBLING_UNREPORTED was under FREEZE_B1. Why the
contract's letter is unclear: s7 says "every COMPLETED RECEIPT row of that node under the anchored launch"; BX2
defines a node execution row by parent_run_id == the launch; BX5 speaks only of "rows whose parent is another
launch". A row whose parent is a node execution of the launch is in none of these categories. The repair shape, if
the operator reads "under" transitively, is one line in own_launch_rows or unreported_siblings (walk parent_run_id
up to the launch; a cycle or a dangling parent is not under it); it is NOT asked for here and would be a second
repair round, which CC3 forbids. The alternative is a contract sentence: "a row whose parent is not a launch is
malformed provenance and never a node execution of any launch" -- which leaves this admission in place by rule.

## 5. Applicability to the path the native witness will use (rso/witness/run_witness.py launch(),
rso/witness/ares_client.py class Launch; read before the set, EXPOSURE.md)

The committed witness path writes rows ONLY through rso/slice001/ledger.py: one TOP_LEVEL begin() for the launch,
then for each config entry one RECEIPT begin() with parent_run_id = the launch and run_id = "<launch>/<node_id>",
finished COMPLETED with receipt_sha256 of the canonical bytes (or FAILED without a digest, which fails the whole
launch: top FAILED, no MANIFEST). The config loader refuses a duplicate node before any row is written; the ledger
refuses a repeated run_id ("run_id already inventoried"). Therefore:

    NESTED_SIBLING (a)   NOT reachable: every node row's parent is the launch (run_witness.launch passes
                         parent_run_id=launch_run_id; ares_client.Launch.produce does the same in memory), and a
                         second execution of a node under one launch cannot be inventoried at all (duplicate run_id
                         -> LedgerError; duplicate node -> WitnessError). Reachable only by an adapter that calls
                         ledger.begin with a node's run id as parent_run_id, which ledger.begin accepts unchecked
                         (any non-empty string). Record as applicable-conditional (nesting adapters), narrower than
                         B1's SIBLING condition (any adapter with per-attempt run ids).
    E6 (b)               the shape (a digest-less COMPLETED sibling) is not producible by the witness path: a
                         COMPLETED node row there always carries the digest (finish() is given receipt_sha256 in the
                         same call), and a second row of the node cannot exist (above). It bears on the witness only
                         as unpinned behaviour of code the witness's consumer will call.
    FAILED_RERUN_DIGEST  the sound shape is likewise not producible there (a FAILED node fails the launch); its
                         acceptance tells the C-010 consumer author that BX5b will not falsely reject an adapter that
                         records digests on failed attempts.
    the honest hole      the witness path's own way to drop an unfavourable execution is a NEW launch: launch A
    (not a survivor)     (node N unfavourable; or a later node fails and A is FAILED without MANIFEST) then launch B
                         re-runs everything and B's manifest is registered. Launch A's rows stay in the shared
                         ledger as provenance (BX5), visible to a human reading the inventory and to nothing in
                         G-INV. This is the contract's design (one anchored launch per bundle), not a defect of the
                         binding; it is stated so the preregistration's author can decide whether the keeper should
                         see the count of launches of a node, which rso/binding does not provide.

## 6. The edit, in detail (rows: mutation_rows.jsonl, mutation_confirm.jsonl; stdout mutation_stdout.txt)

E6 replaces unreported_siblings' filter with one that also requires r.get("receipt_sha256"). Targeted suite (binding
unit tests + test_evidence, test_checker_render, test_stages_evidence, test_ledger, test_s2_run): 218 tests, 0
failures. Full suite (B1's 16 slice modules + the binding suite + the three rso/witness test modules): 528 tests, 0
failures, 1 skipped (the opt-in live custody smoke). Witness at module level DIFFERS as predicted; binding_reasons on
the cited row is [] under both (the cited row is sound in the witness, so the edit changes only the sibling verdict).
Which suite would have had to kill it: test_binding.Siblings (read) builds every sibling with a digest; the G-INV fire
record's B1 SIBLING case carries a digest (B1 cases.py, mine); T031's test_evidence sibling tests were not read, and
the survival says none of them strips the digest. The kill would have been a first-sight result; the survival is a
first-sight gap. The fault is the natural refactor "only digest-bearing rows are real executions" and its consequence
is a hidden second completion recorded as a digest-less row.

## 7. Per-surface components

    surface                         sound c/t  broken c/t  edits: prop appl exec kill surv   open
    ------------------------------  ---------  ----------  ------------------------------   ----------------
    BX1 launch identity             0/0        0/0         0    0    0    0    0            - (B1's E2 pinned)
    BX2 cited-row binding           0/0 (*)    0/0         0    0    0    0    0            - (B1's E3, E4 pinned)
    BX5 / BX5b sibling rule         1/1        0/1         1    1    1    0    1            NESTED_SIBLING, E6
    BX7 custody                     not in this packet's list
    producer (ledger/s2_bundle)     controls 2/2 only                                       unchallenged
    (*) the sound case's cited row exercises BX2 beside a digest-bearing FAILED row; it is counted under BX5b.

## 8. Resources (rso/binding/LEDGER.jsonl; contract.json caps)

    launch 1  B2-CASES-20261007T073656Z-6888          COMPLETED   2.9 s
    launch 2  B2-MUTATION-20261007T073714Z-10300      COMPLETED   top-level 0.03 s + 3 children 389.0 s:
              baseline 42.3; E6 targeted 51.5; E6 confirm 295.2
    packet    2 of 3 launches; 391.9 CPU-s charged of the 1200 s allowance run_mutation.py reserves for B2
    campaign  10 of 12 top-level launches; 1910.2 CPU-s of 5400 (31.8 of 90 minutes); artifact bytes unchanged at
              13,381,360 (this packet wrote no artifacts to the ledger)
    reviewer  about 0.5 h of model time (07:17Z-07:50Z) against the packet's 45 min and the contract's 2 h (B1 used
              about 1.0 h; contract total about 1.5 h)
    unledgered, disclosed: --check-build (about 2 s, no consumer call); the acceptance command on the merged tree
              (first attempt torn with the session, about 4 min wasted; foreground re-run 5.2 min; 528 run, 0 failures).
    reviewer  second instance about 0.3 h (08:17Z-08:35Z): acceptance re-run, report and receipt completion, state commits.
