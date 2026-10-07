# C-009-T034 CC3 re-check set on FREEZE_B2 (committed before any outcome is observed)

Reviewer: Pallas[harry1-2b71b1e1], claude-fable-5-1 (Q3), harry1 (M4), headless. Frozen surface:
rso/binding/FREEZE_B2.md (code 1b69dd04a; rso/binding v1.1.0: v1.0.0 + s6 v1.0.1 clarification + s7 BX5b); its 48
hashes were verified against the committed blobs at 0ad2d1a6f and at 1b69dd04a and against the LF-normalised working
tree before this file was written (48 equal, 0 mismatch, three times). Branch pallas/c009-t034 from 0ad2d1a6f; claim
13d7c344c on main. Exposure: EXPOSURE.md beside this file (the binding unit test file WAS read; no slice or witness
test body was).

Packet rule (TASK.json; CONTRACT.md s3 CC3; ADJUDICATION_CC3.md): the ONE re-check CC3 allows: 1 fresh sound,
1 fresh broken, 1 semantic edit on the repaired binding surfaces (BX1 / BX2 / BX5-BX5b), committed before outcomes;
fresh = not the CC1 shapes (fixtures/cc1_cases.py) and not the B1 shapes (challenge/B1/cases.py), which are T031's
regressions. Files: cases.py (1 sound, 1 broken), expected.json (answer key and scoring rule, as B1), edits.json
(1 edit), witnesses.py, run_cases.py, run_mutation.py. Drivers may be repaired after this commit; the four data
files (cases.py, expected.json, edits.json, witnesses.py) may not.

## Where the re-check is aimed, and why these shapes

The repair round changed exactly one behaviour: BX5b (every COMPLETED RECEIPT row of a presented required node
under the anchored launch must be the cited row; FAILED / INTERRUPTED / REFUSED attempts stay provenance). It also
pinned E2-E4 with my B1 fire cases and wired run_id through consumer_for; those are test and wiring changes whose
regressions T033 ran. BX1 and BX2 themselves are unchanged code with (now) every B1 dimension pinned; a fresh
BX1/BX2 shape would be a new single-dimension deviation, and every dimension the contract names is checked by the
frozen code (read in full), so the only place a fresh shape can find daylight is in what BX5b's words leave open.
Reading CONTRACT s7 against binding.py, the conjuncts "COMPLETED", "RECEIPT", "of that node", "must be the cited
row" are each implemented literally; "under the anchored launch" is implemented as parent_run_id == the launch
(own_launch_rows; BX2's definition of a node execution row). That is the one letter-vs-implementation gap, and the
digest is the one field BX5b's words do not mention at all. The set measures exactly those two things, from both
sides, on the same two bases as B1 (synthetic G0; the committed C-009 fresh produce rso/binding/R1/G0).

## Cases (VICTIM: REG's PRESERVE receipt; it cites its OWN fully-bound row in both)

SOUND (must be accepted; a false rejection is a finding):

  B2.SOUND.FAILED_RERUN_DIGEST   the launch re-executed the victim's node AFTER the presented attempt; the
                                 re-execution FAILED and its row records receipt_sha256 of the (unpresented) PRESERVE
                                 FAIL receipt it had built before failing. Provenance by BX5b's own words; no order
                                 or timestamp is read (BX4); a digest on a non-COMPLETED row is not an execution.
                                 Not B1.SOUND.FAILED_RETRY (before; no digest).

BROKEN (must be rejected; an admission is a survivor):

  B2.BROKEN.NESTED_SIBLING       a SECOND COMPLETED RECEIPT row of the victim's node, recording the digest of an
                                 unpresented PRESERVE FAIL receipt, whose parent_run_id is the victim's own cited
                                 row (depth 2: a re-execution spawned by the presented attempt), not the launch.
                                 Not B1.BROKEN.SIBLING_UNREPORTED (parent = the launch; now refused) and not
                                 B1.BROKEN.NESTED_PARENT (the victim's OWN row nested; refused FOREIGN_LAUNCH).

Why NESTED_SIBLING is the one broken case: every other fresh shape I can state inside CONTRACT s7's words is
refused by a conjunct the frozen code implements literally (status, kind, node id, run id), and every shape outside
its words (a sibling of another launch_kind, of another status spelling, of a differently-spelled node id) is
provenance by the contract's own definitions and would be a complaint about the contract, not a survivor. The
nested re-execution is the one shape where the words ("under the anchored launch") plausibly cover it and the code
(parent == launch) does not. It is scored as broken because the harm is the B1 harm unchanged: a launch that ran a
required node twice and reports the attempt it prefers qualifies, and the hidden row says so in the inventory.

## Edit (edits.json; on the repaired code; with a behavioural witness)

    id                              module    edit                                           witness original -> mutant
    ------------------------------  --------  ---------------------------------------------  ----------------------------
    E6-digestless-sibling-ignored   binding   unreported_siblings counts a COMPLETED sibling  ([SIBLING_UNREPORTED],
                                              row only if it records receipt_sha256           [RID#2], []) -> ([], [], [])

Placed on binding.unreported_siblings, where the frozen binding unit suite (read; EXPOSURE.md) does not pin it:
its Siblings cases all give the sibling a digest (receipt_sha256 of the bytes "another receipt"), and its
non-sibling cases vary status, launch, node and kind, never the digest. The T031 receipt names the slice suite's
three inverse mutants (siblings never checked; FAILED sibling counted; siblings across launches); this edit is none
of them. Whether the slice suite's BX5b tests (test_evidence; the G-INV fire record's B1 SIBLING case, whose sibling
carries a digest) kill it is the first-sight question. The fault is the natural refactor "only digest-bearing rows
are real executions"; its consequence is a hidden second completion recorded as a digest-less row (E4's row shape as
the sibling instead of as the cited row).

## Execution plan

Launch 1: run_cases.py (consumer-only: 2 controls x 2 bases, 2 cases x 2 bases; no probe). Launch 2:
run_mutation.py (baseline + E6 on the targeted suite: binding tests, test_evidence, test_checker_render,
test_stages_evidence, test_ledger, test_s2_run; a survivor then against the FULL frozen suite = the three
acceptance suites including rso/witness/tests, within a 20 CPU-minute allowance of this packet). Two of the three
permitted launches; the third is held for a driver-repair rerun and otherwise not used. Both launches and every
mutation child are charged to rso/binding/LEDGER.jsonl (rso/binding/contract.json; 8 of 12 launches and 1518.2 of
5400 CPU-s used before this packet). No separate unchanged-suite launch: T033's regression and the runner's own
baseline stand for it; the acceptance command runs once more, unledgered, on the merged tree before integration and
is reported in the receipt.

Pre-outcome checks after this commit (unledgered, disclosed in REPORT.md if used): run_cases.py --check-build
(constructs each case, records row counts and the inserted row, calls NO consumer and observes NO verdict);
run_cases.py --dry (controls only, as B1).

## Predictions (written to be lost)

Cases. FAILED_RERUN_DIGEST: ACCEPTED on both bases, every decision identical to the baseline (unreported_siblings
filters status == COMPLETED before anything else; nothing reads the digest of a non-cited row; own_launch_rows and
inventory_terminal are indifferent to order). NESTED_SIBLING: ADMITTED on both bases (G-INV PASS "inventory
terminal; every run reported"; CL-RET(REG) identical to the baseline on r1): own_launch_rows requires
parent_run_id == the anchored launch, so a depth-2 row is neither a sibling nor an own-launch row; the frozen code
behaves exactly as B1's code did on SIBLING_UNREPORTED. The survivor of this set, for adjudication: whether CONTRACT
s7's "under the anchored launch" means the transitive closure. Applicability (REPORT.md will state it after the
run): NOT reachable through rso/witness/run_witness.py, which gives every node row parent_run_id = the launch and
whose ledger refuses a repeated run_id; reachable by any adapter that records a re-execution under the attempt that
spawned it (ledger.begin accepts any parent_run_id).

Edit. E6 SURVIVES the targeted suite (no binding unit test and, I predict, no slice test builds a digest-less
COMPLETED sibling: T031's tests were written against B1's SIBLING shape, whose sibling has a digest) and the FULL
suite; witness DIFFERS (NOT_EQUIVALENT_WITNESSED). If the slice suite kills it, the kill is a first-sight result and
BX5b is better pinned than I predict. Calibration ledger: S3/S4/R2 5/5, 4/4+2/3, 5/5; B1 9/9 cases and 5/5 edits
with one check-design error.

## Verdict rule for the report (fixed now)

BX1, BX2: CLOSED within coverage iff T033's regression held (it did: REGRESSION.md Q1-Q4) AND this set's two cases
leave the BX1/BX2 dimensions of the victim's cited row bound exactly as the baseline (the identical checks), with
E2-E4 now killed by the frozen suites (T031 receipt). No fresh BX1/BX2 case is in this set, and the report says so.
BX5/BX5b: CLOSED iff NESTED_SIBLING is refused and E6 is killed; NOT CLOSED otherwise, with each survivor's class
(behavioural / test-coverage / contract-vocabulary) and its applicability to the native witness path stated.
