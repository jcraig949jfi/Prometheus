# C-004-T030 S3 first-sight challenge -- REPORT

Reviewer: Pallas[m2-e7da6bde], claude-fable-5-1 (Q3), host SPECTREX5. 2026-10-05.
Frozen surface: rso/slice001/FREEZE_S2.md (code b220c7e39, contract v1.0.3). Branch pallas/c004-t030.
Independence caveat (CONTRACT.md s6, printed with every first-sight record): Pallas is a member of the RSO
Builder Cell that writes no production code and is a different model family from the Opus/Sonnet builders;
same model family as the closure reviewer and the FABLE corpora. Exposure: EXPOSURE.md.

This report records mechanics and scores with denominators. It classifies nothing as IMPLEMENTATION, CONTRACT
or TABLE defect: that is T040's (Palamedes) and, where a case expectation would change, the operator's.

## 1. Ordering evidence (git, branch pallas/c004-t030)

    9af90c053  EXPOSURE.md, before the contract or any source was read
    99084714a  attack set (cases, expected.json, edits, witnesses, predictions), 2026-10-05T06:02:39Z
    53e65a17e  unchanged-suite record, case results, ledger rows
    (this commit)  mutation rows, results.jsonl, REPORT.md, receipt

No file under rso/slice001/tests/ was opened at any time in this task, before or after the attack-set commit.
The unchanged suite ran first (06:02:48Z-06:06:13Z), then the cases, then the edits.
Nothing under rso/slice001/ outside challenge/S3/ was modified, except rows appended to s2/LEDGER.jsonl as the
packet requires. No driver was repaired after the attack-set commit; all four data files are as committed.

## 2. Unchanged suite

    python -B -m rso.slice001.ci --ledger rso/slice001/s2/LEDGER.jsonl --node-id S3-UNCHANGED-SUITE
    PASSED: 356 tests run, 355 passed, 0 failed, 0 errored, 1 skipped; 187.7 CPU-s (suite_unchanged.json)

## 3. Cases: first-sight score

    sound cases    4 correct of 5
    broken cases   3 correct of 5
    controls       2 of 2 (real G0 baseline; single-manifest keeper case)
    probes         3 recorded, unscored

    case                        polarity  result     what happened
    --------------------------  --------  ---------  ---------------------------------------------------------
    S3.SOUND.LATCH              sound     CORRECT    ELIGIBLE; PRESERVE PASS, 0 of 6144 applicable, printed
                                                     "(vacuous: 0 applicable)"; all counts as derived
    S3.SOUND.BEACON             sound     CORRECT    ELIGIBLE; constant packet across every boundary accepted
    S3.SOUND.MIGRATE            sound     CORRECT    OBSERVER(REG, S3_MIGRATE) PASS, 196608 eligible
    S3.SOUND.W_OTHER_VERSION    sound     CORRECT    all 6 decisions byte-identical to the baseline
    S3.SOUND.TWO_MANIFESTS      sound     INCORRECT  FALSE REJECTION. G-BIND FAIL on CL-CAL, CL-CUST, and all
                                                     three CL-RET claims, while custody reads QUALIFIED
    S3.BROKEN.INVERT            broken    INCORRECT  refused, primary verdict right (RESTART FAIL, reason and
                                                     witness as derived), plus a WRONG extra line: G-RECOMP
                                                     FAIL OUTCOME_MISMATCH:value on an honestly built bundle
    S3.BROKEN.SHADOW            broken    CORRECT    CHANNEL FAIL, reason and witness {0, j 1, v 1} as derived
    S3.BROKEN.LOGDEP_BOOKKEEP   broken    CORRECT    OBSERVER FAIL "observer BOOKKEEP changes output at
                                                     (1, PROBE_A)"
    S3.BROKEN.RUN_BORROW        broken    INCORRECT  FALSE ADMISSION. G-INV PASS; CL-RET(REG) ELIGIBLE
    S3.BROKEN.W_CALIBRATION     broken    CORRECT    CALIBRATION and 3 RETENTION lines WITHDRAWN; 4 claims
                                                     NOT_ELIGIBLE; TWIN(REG) byte-identical

Rows: results_cases.jsonl (one row per check with the actual values); decisions_S3W.json.

### Finding F1 (S3.BROKEN.INVERT): the bound clamp trace is not the trace the CHANNEL outcome is computed from

s2_bundle.build_bundle takes the CHANNEL outcome from reset.channel, which clamps `a` by capture / edit /
restore INTO THE SAME instance (reset.clamp_answers), and binds trace:clamp from adapter.world_runs, which
restores INTO A FRESH instance (adapter._clamp_hook). For a runtime with state the capture omits the two
differ. S3_INVERT: receipt CHANNEL FAIL at {history 0, j 1, v 0}; recomputation from the bound trace PASS;
G-RECOMP FAIL OUTCOME_MISMATCH:value, witness rcpt:S3_INVERT:CHANNEL:STANDARD. The producer was honest. The
claim is NOT_ELIGIBLE either way (RESTART FAIL), so no false admission results; the defect is a consumer gate
accusing a faithful producer, and a receipt whose outputs are not "every output trace the outcome is computed
from" (B3.1). Which restore P5 means (same instance or fresh) is not stated in A5; both sides must use one.
Not run, predicted from the same code path: the committed S2 EXTRA bundle's HCOUNT (CHANNEL FAIL at j = 2 in
its receipt, hidden counter not captured) should show the same G-RECOMP line; the S2 matrix did not compare it.

### Finding F2 (S3.SOUND.TWO_MANIFESTS): the keeper's LAST manifest row is taken as this bundle's anchors

evidence.anchors_from_keeper uses rows[-1] of kind EVIDENCE_MANIFEST. With a second bundle's manifest
registered later (before the first check), the consumer anchors G0 to the other bundle's manifest: G-BIND
fails on five claims, and custody still reads QUALIFIED, on the row of the OTHER manifest
(EVIDENCE_MANIFEST:25f9f613e16c), because custody() looks up the blob of whatever anchors it was handed.
Custody QUALIFIED was therefore printed for a bundle none of whose nodes are in the manifest it was qualified
against. The real T020 consumer (s2_run.consumer_for) does not call anchors_from_keeper; it labels the
bundle's own MANIFEST.json "keeper" and lets custody() match the blob, so the S2 matrix is not affected.
Related, from s2/CLASSIFICATION.md (not fresh, not scored): unregistered bundles read ROW_BLOB_MISMATCH, not
KEEPER_ROW_MISSING, as soon as any other manifest is registered.

### Finding F3 (S3.BROKEN.RUN_BORROW): G-INV does not tie a receipt's run to that receipt

evidence.g_inv checks that each required receipt's run_id occurs exactly once in the inventory. It never
compares the inventory row's node_id (V7) with the receipt's. A receipt citing another node's run, with its
own run row absent, passes: CL-RET(REG) ELIGIBLE with a PRESERVE receipt that has no run. Derivation of the
expected FAIL rests on B3.3 + V7 (ATTACK_SET.md s4); if the coordinator rules B6.4's own sentence governs, this
is a contract gap, not an implementation defect, and the case moves to the probes.

### Probes (unscored)

    VERSION_DRIFT     as read: ERASE(REG) UNQUALIFIED NO_STAGE_RECORD; CL-RET(REG) NOT_ELIGIBLE; PKTD identical
    MEASUREMENT_LIE   admitted: cell.measurement naming a hash that is not the predicate version binds, and
                      CL-RET(REG) is ELIGIBLE and byte-identical to the baseline (measurement is not checked
                      against predicate.code anywhere)
    OBS_TRANSPLANT    refused: G-BIND FAIL IDENTITY_MISMATCH:node_id (a reason code B6.3 does not list)

### Observation O1 (S3.SOUND.LATCH), for S5

A runtime with RETENTION POSITIVE passes PRESERVE with 0 applicable pairs when its reset is the step that
writes the allowed component. This is correct by A5 P4 as written and is printed as vacuous. P4 then says
nothing about that runtime; draft A's remark that "RETENTION carries the meaning" was written for runtimes that
carry nothing.

## 4. Semantic edits

    proposed 10 | applicable 10 | duplicate 0 | executed 10 | killed 5 | survived 5 | equivalent 0 |
    syntax/import/test error 0 | timeout 0 | not run 0

Phase 1 ran each edit against targeted test modules (suite A 48 tests, suite B 127 tests; baselines PASSED).
Every phase-1 survivor was then run against the full frozen suite (356 tests): all five survived there too.
Every survivor has a behavioural witness that DIFFERS between original and mutant (runner class
NOT_EQUIVALENT_WITNESSED); none is adjudicated equivalent; none is unresolved as to equivalence.

    id   area             status    full suite  witness, original -> mutant
    ---  ---------------  --------  ----------  ------------------------------------------------------------
    E01  ERASE horizon    SURVIVED  SURVIVED    erase(S3_LAG3_EP3): FAIL -> PASS
    E02  ERASE sends      SURVIVED  SURVIVED    erase(S3_RELAY): (FAIL, CUE) -> (PASS, None)
    E03  RESTART cuts     KILLED    --          (1 failure of 48)
    E04  OBSERVER state   KILLED    --          (2 failures of 48)
    E05  B6.2 edge        KILLED    --          (2 failures of 127)
    E06  slot identity    KILLED    --          (1 failure of 127)
    E07  G-RECOMP horizon SURVIVED  SURVIVED    recompute_erase(lag-3 traces): FAIL -> PASS
    E08  closure depth    KILLED    --          (1 failure, 1 error of 127)
    E09  gate withdrawal  SURVIVED  SURVIVED    gate_authority(G-BIND): UNQUALIFIED [WITHDRAWN] -> QUALIFIED
    E10  suspension       SURVIVED  SURVIVED    A4 reasons, unresolved = 1: [SUSPENDED] -> []

What the survivors show (each is a missing fire test, not a defect of the frozen code):
- E01, E07: nothing in the frozen suite has a forbidden influence at lag exactly H = 3, on the producer side or
  in the consumer's recomputation. The registered horizon could be 2 in either place and every test passes.
- E02: no fixture leaks forbidden content only through sends; ERASE could ignore the CUE output.
- E09: no test withdraws a consumer gate's own stage record.
- E10: no test has a challenge record with unresolved = 1 (or any value that separates > 0 from > 1).

Rows: mutation_rows_A.jsonl, mutation_rows_B.jsonl (the runner's), mutation_confirm.jsonl, results.jsonl.

## 5. Per-gate first-sight components (for the C4 FIRST_SIGHT_CHALLENGED records, draft B B4.1)

Cases are counted under every gate whose verdict they exercise; "open" lists what this reviewer considers not
closed for that gate (false admission / rejection, mistyped line, or an applicable non-equivalent survivor).
Whether "open" maps to the stage record's `unresolved` field is the registrar's reading, not decided here.

    gate         sound c/t  broken c/t  edits: prop appl exec kill surv equiv err t/o  open
    -----------  ---------  ----------  ---------------------------------------------  ----------------
    P0 BOUNDS    1/1        0/0         0    0    0    0    0    0     0   0            -
    P1 CALIBR.   0/0        0/0         0    0    0    0    0    0     0   0            - (not challenged)
    P2 RETENTION 2/2        0/0         0    0    0    0    0    0     0   0            -
    P3 ERASE     2/2        0/0         2    2    2    0    2    0     0   0            E01, E02
    P4 PRESERVE  2/2        0/0         0    0    0    0    0    0     0   0            - (O1)
    P5 CHANNEL   2/2        1/1         0    0    0    0    0    0     0   0            - (F1 producer side)
    P6 RESTART   2/2        1/1         1    1    1    1    0    0     0   0            -
    P7 OBSERVER  1/1        1/1         1    1    1    1    0    0     0   0            -
    P8 TWIN_EQ   0/0        0/0         0    0    0    0    0    0     0   0            - (not challenged)
    G-BIND       1/2        0/0         2    2    2    2    0    0     0   0            F2
    G-INV        1/1        0/1         0    0    0    0    0    0     0   0            F3
    G-RECOMP     2/2        0/1         1    1    1    0    1    0     0   0            F1, E07
    custody      0/1        0/0         0    0    0    0    0    0     0   0            F2
    authority /  1/1        1/1         3    3    3    1    2    0     0   0            E09, E10
    invalidation

Notes on the table. G-BIND sound 1/2: W_OTHER_VERSION correct, TWO_MANIFESTS not (the wrong anchors come from
the keeper-fetch helper, not from the binding checks). G-INV sound 1/1 is W_OTHER_VERSION. G-RECOMP sound 2/2
are LATCH and BEACON; broken 0/1 is the mistyped extra line on INVERT. RESTART broken 1/1 is INVERT's primary
verdict. Authority / invalidation (B4.2 A3-A4, B6.5) is code in evidence.py and has no stage record of its
own; its figures belong with whichever instrument the registrar attaches evidence.py to. P1 and P8 were not
challenged: no first-sight figures exist for them.

## 6. Predictions (ATTACK_SET.md s7), scored

Cases: 10 of 10 predicted outcomes held, including the three failures and their mechanisms. Probes: 3 of 3.
Edits: 6 of 10. Wrong: E03, E04 and E06 were predicted to survive and were killed (the frozen tests are
stronger there than this reviewer assumed); E10 was predicted killed and survived.

## 7. Limits of this challenge

- Ten cases and ten edits buy a small challenge, not an error rate (plan s5).
- Evidence-plane cases use fixture stores (V8: logic only). No case touched the live custody registry.
- The subject CodeRef of the S3W receipts names fixtures/world_cases.py although the fixtures live in
  challenge/S3/attack_set/cases_world.py (attached in memory for the build). The S3W bundle is challenge
  evidence only and must not be registered or cited as a producer bundle.
- Mutation children were charged wall seconds (an upper bound on CPU).
- CALIBRATION, TWIN_EQ, render.py, ledger.py, matrix.py and receipt.py's schema checks were not attacked.
- Same-family caveat: agreement between this reviewer's derivations and the T005 table or the FABLE corpora is
  not independent evidence.

## 8. Resources (slice ledger rso/slice001/s2/LEDGER.jsonl, rows with run ids starting "S3-")

    launches (TOP_LEVEL)    3   unchanged suite; cases; mutation driver
    RECEIPT rows           46   45 receipts of the S3W build + 1 row for the consume phase
    MUTATION_CHILD rows    19   4 baselines, 10 targeted children, 5 full-suite confirmations
    CPU charged            2027.4 s (33.8 CPU-minutes): TOP_LEVEL 197.7, RECEIPT 40.5, MUTATION_CHILD 1789.3
    slice ledger after S3  8 of 12 launches; 2299.2 s of the 4800 s left for ledgered launches (v1.0.3 U2);
                           artifact bytes 18.4 MB of 100 MB; no cap exhausted
    reviewer time          about 55 minutes (claim 05:43Z to results 06:38Z), plus this report

The packet's older ceiling line ("< 10 CPU-minutes incl. mutation children") was exceeded; its 2026-10-05 note
(about 75 ledgered CPU-minutes for S3 + S4) was followed. About 41 CPU-minutes and 4 launches remain for S4.

## 9. What would falsify this report; what to stop

- F1 is wrong if the contract is ruled to define P5's restore as "into a fresh instance": then the producer's
  outcome, not the trace, is the side to change, and the mismatch is still a defect, on the other side.
- F3 is wrong as an implementation finding if B6.4's literal sentence is ruled to govern over B3.3 + V7.
- Any survivor is wrong if a test body, which this reviewer never read, does pin the behaviour and the full
  suite run here did not load it; the confirmation ran the 16 modules named in FREEZE_S2.md by name (356 tests,
  the same count as ci discovery).
- Not worth continuing: more world-plane fixtures of the SHADOW / LOGDEP kind. The reset and observer
  predicates handled every fresh runtime correctly; the open items are in the evidence plane and in what the
  suite does not pin.
