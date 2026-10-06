# C-004-T041 S4 closure challenge -- REPORT

Reviewer: Pallas[m2-e7da6bde], claude-fable-5-1 (Q3), SPECTREX5. 2026-10-06. Frozen repaired surface:
rso/slice001/FREEZE_S4.md (code 0e1943bff, contract v1.0.4). Branch pallas/c004-t041.
Caveat printed with every closure record (CONTRACT.md s6): cell member, writes no production code, different
model family from the builders; same family as the closure reviewer, the T005 table and the FABLE corpora.
First-sight scores (S3) are preserved unchanged in challenge/S3/REPORT.md; the figures here are post-repair
closure figures, reported separately (plan s5). Nothing here is classified; that is S5's (C-004-T050).

## 1. Ordering evidence (git, branch pallas/c004-t041)

    d92546849  claim (main)
    be673092d  closure set: cases, expected.json, edits, witnesses, predictions   2026-10-06T01:34:11Z
    (next)     case results + ledger rows; then mutation rows, results.jsonl, this report, receipt

No file under rso/slice001/tests/ was opened in this task (nor in S3). No separate unchanged-suite launch
was made: T045's regression run (s4/REGRESSION.md) and the runner's two baselines (120 tests each, PASSED)
stand for it; the full suite (378 tests) ran once, as the confirmation child of the survivor, and passed
there apart from nothing (0 failures on the mutant means the suite does not pin the edited behaviour).

## 2. Closure score

    sound cases    1 correct of 2      (REPRODUCED: FALSE REJECTION; RETRY_ROW correct)
    broken cases   2 correct of 2      (OBS_RUN_BORROW, VERSION_OF_ANOTHER refused with the expected reason)
    controls       2 of 2              (S4 G0 baseline; S4 single-manifest keeper case)
    probe          1 recorded, unscored (STALE_RUN: admitted)

    edits          proposed 3 | applicable 3 | duplicate 0 | executed 3 | killed 2 | survived 1 |
                   equivalent 0 | error 0 | timeout 0
                   X1 (adapter clamp point) KILLED 2 failures; X2 (custody guard) KILLED 3 failures;
                   X3 (G-INV observer-insensitive) SURVIVED the targeted suite and the FULL suite (378 tests),
                   witness DIFFERS: (FAIL, RECEIPT_WITHOUT_RUN:rcpt:REG:OBSERVER:NULL:STANDARD) -> (PASS, ..)

Exit criteria (packet; plan s5): zero unresolved false admissions / rejections -- NOT MET (one false
rejection, S4.SOUND.REPRODUCED); correctly typed reasons -- met on every refused line; no unresolved
applicable survivor on a claim-critical path -- NOT MET (X3, G-INV, witnessed non-equivalent). By the plan's
own words this is INCOMPLETE CLOSURE, not acceptance, and not a failure of the slice either: the repaired code
handled the two broken cases, the retry row and two of three edits; the two open items are below.

## 3. Open item C1 (S4.SOUND.REPRODUCED): the earliest exact-node-set manifest anchors a reproduced bundle

The real registry already holds two manifests with the same 25 node ids: the S2 G0 manifest and the S4 G0
manifest (T045). evidence.resolve_anchors chooses among the keeper's candidates by node identity only; with
two exact matches it takes the earliest registered (FD-T042-2), here the S2 manifest. Against it every S4
receipt is BYTES_MISMATCH:receipt: G-BIND FAIL on CL-CAL, CL-CUST, CL-RET(REG), CL-RET(PKTD), CL-RET(LAGD)
(TWIN(REG) has no gate line and stays ELIGIBLE) -- while custody reads QUALIFIED, on the S2 manifest row
(EVIDENCE_MANIFEST:d2dbf1afe8cc; the S4 manifest is 924f6cc3392e). So the F2 repair closed the S3 case
(another bundle's node set) and left the case the registry is actually in: the same bundle reproduced. A
candidate whose artifact hashes match the presented receipts is the bundle's manifest; node ids alone cannot
tell two productions of one node set apart. Rows: results_cases.jsonl (case_claims S4.SOUND.REPRODUCED).

## 4. Open item C2 (edit X3): G-INV's node-id comparison is not pinned per observer

The F3 repair compares the cited row's node_id with the receipt's. No test fails when that comparison drops
the observer segment: a receipt for OBSERVER(M, o1) may cite the run of OBSERVER(M, o2). The case
S4.BROKEN.OBS_RUN_BORROW is the fixture that pins it (refused by the frozen code; admitted by the mutant --
the witness value above). This is a missing fire test, not a defect of the frozen code.

## 5. Probe (unscored): S4.PROBE.STALE_RUN

The S4 PRESERVE receipt citing the S2 run of the same node, inventory intact: admitted (CL-RET(REG) ELIGIBLE,
G-INV PASS). Whether that is right turns on how a cumulative inventory is to be read (T045 O-S4-1): under B3.3
the cited row did not launch this receipt and the S4 row of that node is COMPLETED with no receipt; under the
implementation's reading of B6.4 only nodes without a receipt are checked. For S5.

## 6. Per-gate closure components (for the C4 CLOSED_AFTER_REPAIR records, draft B B4.1)

    gate / surface          sound c/t  broken c/t  edits: prop appl exec kill surv equiv err t/o  open
    ----------------------  ---------  ----------  ---------------------------------------------  ------
    CHANNEL (adapter, F1)   0/0        0/0         1    1    1    1    0    0     0   0            -
    G-BIND (measurement)    0/0        1/1         0    0    0    0    0    0     0   0            -
    G-BIND (anchors, F2)    0/1        0/0         0    0    0    0    0    0     0   0            C1
    custody (F2)            0/1        0/0         1    1    1    1    0    0     0   0            C1
    G-INV (F3)              1/1        1/1         1    1    1    0    1    0     0   0            C2 (X3)
    authority A1 (version)  0/0        1/1         0    0    0    0    0    0     0   0            -

The S3 per-gate table (challenge/S3/REPORT.md s5) is the first-sight object a closure record must carry
unchanged. Which gates may be recorded CLOSED_AFTER_REPAIR is the registrar's (Palamedes) and, under the
plan's exit rule, the operator's at S5; this reviewer records only that G-BIND-anchors / custody and G-INV
have open items and the other challenged surfaces do not.

## 7. Predictions (CLOSURE_SET.md), scored

Cases 4 of 4 (REPRODUCED refused by the predicted mechanism; the others as expected); probe 1 of 1 (admitted).
Edits 2 of 3: X1 was predicted to survive and was killed (test_adapter pins the clamp point); X2 killed and
X3 survived as predicted.

## 8. Resources (ledger rows with run ids starting "S4-")

    launches (TOP_LEVEL)   2   cases (consumer-only, 1.3 s); mutation driver
    MUTATION_CHILD rows    6   2 baselines, 3 targeted children, 1 full-suite confirmation (260.5 s)
    CPU charged            459.1 s (7.7 CPU-minutes), wall seconds for children
    slice ledger after     15 of 20 launches; 2924.7 s ledgered CPU (48.7 min of the 80 ledgered); 31.8 MB
    reviewer time          about 25 minutes (claim 01:27Z to results 01:42Z, plus this report)

## 9. Limits; what would falsify; what to stop

- Two sound and two broken cases and three edits are the plan's minimum; this is a small closure challenge,
  not a rate. Evidence-plane only: the world predicates were not re-challenged (S3's cases replay clean per
  REGRESSION.md s3, run by the coordinator, not by this reviewer).
- C1 is wrong if the registrar never registers two manifests with one node set; the registry does (S2 and S4
  G0), so the case is in the registered domain.
- C2 is a missing test, falsified by a test that fails on X3.
- Not worth continuing: more G-INV borrow variants; the one open shape (same node id, earlier window) is the
  probe, and it is a contract question, not a fixture question.
