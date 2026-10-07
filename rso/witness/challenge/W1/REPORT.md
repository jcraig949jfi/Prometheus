# C-010-T014 W1 challenge on FREEZE_W1 -- REPORT

Reviewer: Pallas[harry1-14289af6], claude-fable-5-1 (Q3), harry1 (M4), headless (comms boot 10:44Z; launches 11:11Z-11:26Z;
2026-10-07). Frozen surface: rso/witness/FREEZE_W1.md (code 98345e104: evaluate.py, ruler.py, ares_client.py, run_witness.py,
make_configs.py, their tests, 11 dependencies); 33/33 hashes and lengths verified against the committed LF blobs at
17b03160d before the set and again on the merged tree 3434117cf before this report. Branch pallas/c010-t014 from 17b03160d.
Caveat printed with every closure record: cell member, writes no production code, same vendor family as the builders (T010
Cadmus, T012 Argus, T013 Palamedes: claude-opus-5-5). Exposure: EXPOSURE.md (test_evaluate.py and test_ares_client.py were
read in full before the set; the other witness test bodies were not). No registered subject was run, no registered arm ran
on a registered seed (every seed >= 5,000,000), and no accuracy, retention or ruler value of POS / NULL / SHUF / RECUR
appears in this report or in any committed row.

## 1. Ordering evidence (git; times UTC)

    2ff41b5d9  claim of C-010-T014 (CLAIMED, LEASE.json; main)                                    ~10:45Z
    9b10d0b4d  exposure record EXPOSURE.md (branch)                                                 10:53:56Z
    931be915f  set: cases.py, expected.json, edits.json, witnesses.py, run_cases.py, run_mutation.py,
               CHALLENGE_SET.md with predictions (branch, pushed)                                   11:06:58Z
    34b89538e  state: IMPLEMENTING (main)                                                           ~11:08Z
    check      run_cases.py --check-build: builds every synthetic bundle and the S1 configs, verifies
               B3's premises, calls NO evaluator (check_build_2026-10-07T110909Z.jsonl; unledgered)  11:09:09Z
    e624104e4  driver repair: the mutation launch split per target module across three foreground
               invocations sharing ONE ledger launch (headless 600 s rule; 3 baselines + 6 children
               exceed it); edits_<module>.json = byte-identical subsets of edits.json, verified at load;
               the four data files untouched (git diff --quiet 931be915f HEAD: IDENTICAL)             11:11:14Z
    launch 1   W1-CASES-20261007T111116Z-2100 (TOP_LEVEL, rso/witness/LEDGER.jsonl)                 11:11:16Z-11:13:43Z
    launch 2   W1-MUTATION-20261007T111422Z-16848 (TOP_LEVEL; 9 MUTATION_CHILD rows)                11:14:22Z-11:26Z
    diag       unledgered, disclosed: (a) which test kills E4 (test_ares_client alone under the edit);
               (b) E2 on the driver path (node ids under the edit; no evaluator, no accuracy)         ~11:28Z
    3434117cf  merge origin/main 0206a3bf5 (nothing under rso/ or ares/ changed upstream); acceptance
               133 + 21 OK in the foreground (acceptance_stdout.txt)                                  ~11:30Z

Headless rule: no run_in_background anywhere; every command in the foreground with a timeout <= 600 s; no turn ended with
anything running. Comms: the claim push was the claim; no separate CLAIMED comms note was posted (omission, disclosed); the
INTEGRATION_READY note and a completion heartbeat are the task notes.

## 2. Results

### 2.1 Cases (results_cases.jsonl; expected.json is the answer key)

    case                                                   kind              observed                                   score
    -----------------------------------------------------  ----------------  -----------------------------------------  -----------
    W1.S1.DRIVER_END_TO_END                                sound             3 launches COMPLETED (4 + 6 + 6 nodes),     AS_EXPECTED
                                                                             16/16 receipts bind, P-FLAT PASS x3,
                                                                             custody QUALIFIED x3, nothing refused,
                                                                             P-CAL evaluated, S4-role gates P-CHAN /
                                                                             P-ERASE / P-OBS / P-PRES / P-RET, S15-role
                                                                             P-ERASE / P-OBS / P-PRES / P-RET, a class
                                                                             for both, neither UNQUALIFIED (values
                                                                             redacted; temp ledger 3 launches, 116.2 CPU-s)
    W1.S2.PRE_INTERRUPT_ONLY                               sound             P-RET NEGATIVE, 0 correct, 0 wrong; NEGATIVE AS_EXPECTED
    W1.S3.MID_WINDOW                                       sound             P-RET NEGATIVE, 0 correct, 0 wrong; NEGATIVE AS_EXPECTED
    W1.B1.DUPLICATE_NODE_ACROSS_BUNDLES                    broken            no refusal; [X,Y] -> DA NEGATIVE,           SURVIVOR
                                                                             [Y,X] -> DA POSITIVE (argument order)
    W1.B2.P_CAL_SEEDS_UNREGISTERED                         broken            P-CAL PASS computed on the unregistered     SURVIVOR
                                                                             list (--seeds given); DA POSITIVE, DB NEGATIVE
    W1.B3.LEAKY_SUBJECT_PASSES_ERASE_ON_SAME_REGIME_TRIPLES broken           premise D_same = 0, D_reg = 2560; P-ERASE   SURVIVOR
                                                                             PASS (D = 0), qualified (leak D = 2560);
                                                                             DA POSITIVE; nothing refused
    W1.B4.TWO_BACK_LEAK_ESCAPES_ERASE_AND_PRES             declared escape   TwoBack: P-ERASE 0, P-PRES 0, three-episode AS_EXPECTED
                                                                             carry 640; LeakyReset: 2560 / 1280;         (escape real)
                                                                             S.Runtime: 0 / 0 / 0
    W1.B5.NODE_ID_FIELDS_DISAGREE                          broken            accepted as DA's S/P-RET; DA POSITIVE        SURVIVOR
    W1.B6.COUNTERFEIT_TRACE_FOR_BUNDLED_GENOME             contract limit    admitted; DA POSITIVE                        AS_EXPECTED
                                                                                                                         (limit real)
    W1.B7.STORAGE_TAMPER  artifact_swap                    broken            ARTIFACT_MISMATCH:oracle:regimes             AS_EXPECTED
                          receipt_file_swap                broken            NODE_ID_MISMATCH + RUN_UNREPORTED            AS_EXPECTED
                          inventory_digest_edit            broken            CUSTODY_UNQUALIFIED + BIND_DIGEST_MISMATCH   AS_EXPECTED
                          inventory_digest_edit_reregist.  broken            BIND_DIGEST_MISMATCH                         AS_EXPECTED
    W1.B8.NULL_ARM_IS_NOT_NO_CARRY                         semantic          reset_each_step set, plastic flag True, W1   SURVIVOR
                                                                             written during the episode; NULL(POS) vs
                                                                             S(POS): 0 differing actions (8 x 40 steps);
                                                                             S-NOPL(POS) vs S(POS): 49 differing
                                                                             post-interrupt actions

### 2.2 Edits (mutation_rows_{evaluate,ares_client,ruler}.jsonl; suite = both acceptance suites, 154 tests per child)

    edit                                 module       status    tests/fail  witness original -> mutant
    -----------------------------------  -----------  --------  ----------  ------------------------------------------------------
    W1.E1-window-on-first-interrupt      evaluate     SURVIVED  154 / 0     decisions [0, 0, 0, 0] -> [1, 2, 1, 2]       DIFFERS
    W1.E2-nopl-mutates-shared-subject    ares_client  SURVIVED  154 / 0     subject plastic after arm(): True -> False   DIFFERS
    W1.E3-run-unreported-dropped         evaluate     SURVIVED  154 / 0     ['RUN_UNREPORTED:.../hidden-node'] -> []     DIFFERS
    W1.E4-interrupt-before-step          ares_client  KILLED    154 / 1     (control) killed by TestRunner.
                                                                            test_runner_reproduces_ares_rollout_actions
    W1.E5-erase-pres-oracle-unchecked    evaluate     SURVIVED  154 / 0     ['ORACLE_MISMATCH:...:S:P-ERASE:W15'] -> []  DIFFERS
    W1.E6-pcal-margin-two-sided          ruler        SURVIVED  154 / 0     P-CAL FAIL (NULL) -> PASS (no witness arm)  DIFFERS

Baselines PASSED 154/154 for all three modules. Every survivor is NOT_EQUIVALENT_WITNESSED. Predictions (CHALLENGE_SET.md,
written before outcomes): 11/11 cases, 6/6 edits.

## 3. Verdict per surface (rule fixed in CHALLENGE_SET.md / expected.json before outcomes)

    evaluate.py                  NOT CLOSED   B1, B2, B5 admitted; E1, E3, E5 survive
    ruler.py                     NOT CLOSED   S2, S3 read as registered; E6 survives (one-sided P-CAL margin unpinned)
    ares_client node executions  NOT CLOSED   E4 killed (the W15 interrupt pin is load-bearing); E2 survives; B3 admitted
                                              by the evaluator; B4 escape real but NOT reachable under S.Runtime; B8 semantic
    run_witness storage /        CLOSED       S1 accepted end to end at n = 2048 on real driver output; B7 4/4 refused.
      inventory / seed refusals  within       The seed-refusal surface rests on the frozen T016 tests and S1's honest
                                 coverage     path; it was not re-challenged with a fresh shape.
    make_configs.py              read only    deterministic; no case. B2 shows the evaluator cannot verify its P-CAL /
                                              P-OBS / P-ERASE / P-PRES lists, so the committed configs are the only tie.

## 4. Survivors, class, and whether each bears on the registered witness run

S-1  B1 DUPLICATE NODE ACROSS BUNDLES (evaluate.evaluate; behavioural). `pool.update(c["nodes"])` lets the last bundle in
     argument order silently replace a node another bundle presented; P-FLAT refuses duplicates within a launch only.
     BEARS ON THE REGISTERED RUN: PREREGISTRATION s10 says a failed launch is re-run once and both are reported; a launch
     that fails writes no MANIFEST and is refused (so the pair failed + completed is handled), but a launch that completed
     twice (an accidental double launch, a repair-round re-launch, two bundles of one config passed to the evaluator) is
     resolved by argument order with no record. Cheapest closure: refuse a node id presented by more than one bundle
     (typed reason), or require the caller to name which launch per node and record it in the RESULT.
S-2  B2 P-CAL ARM SEEDS UNVERIFIED (evaluate._p_cal / episodes; behavioural). `registered_seeds` is enforced for the
     subject's P-RET and S-NOPL/P-CHAN nodes only; NULL / SHUF / POS run on any balanced 2048 list, and P-OBS / P-ERASE /
     P-PRES lists are never compared with the committed SEED_LISTS.json. BEARS ON THE REGISTERED RUN: a P-CAL arm on
     seeds other than the registered list would be evaluated as if registered; P-CAL FAIL unqualifies everything, so the
     arms that can launder the instrument's qualification are exactly the unchecked ones. Today the only tie is that
     make_configs writes the lists into the configs and the configs are committed. Also: `--seeds` is OPTIONAL on the
     evaluate CLI; without it even P-RET's list is unchecked. Closure: pass the committed SEED_LISTS (all four lists),
     require --seeds, check the P-ERASE / P-PRES groups against the registered generator's output.
S-3  B3 A LEAK THAT PASSES P-ERASE (evaluate.evaluate_subject / _check_oracle; behavioural, config-conditional). A
     hand-wired leaky runtime passes P-ERASE with D = 0 when X's probe triples pair SAME-regime pre-episodes, while
     X-LEAK (the same leaky runtime) fires D = 2560 on registered-shape triples; the evaluator checks neither that pre_a
     draws r = 0 and pre_b r = 1 (it already computes both regimes) nor that X and X-LEAK ran on ONE probe set.
     Applicability: reachable only if the launched config deviates from make_configs' output (which is correct); the
     evaluator is the last line and does not hold it. Closure: in _check_oracle require regs[:, 0] == 0, regs[:, 1] == 1
     for P-ERASE (and the warm-up opposite to the seed for P-PRES), and in evaluate_subject require the S and S-LEAK
     P-ERASE nodes to declare identical seeds.
S-4  B5 NODE ID vs RECEIPT FIELDS (evaluate.check_bundle; behavioural, producer-forgery class). The evaluator files a
     receipt under the id the manifest and its own node_id field carry, and reads arm / world / seeds / subject from the
     receipt body without checking they rebuild that id. A receipt with arm SHUF and subject DB was evaluated as DA's S
     node, on shuffled-mode interrupt steps. Applicability: not producible by the frozen driver (receipt_dict derives the
     id from the same fields); it needs a producer that lies consistently, the same trust level as B6. Closure is one
     line: `AC.node_id(rec["subject"]["genome_sha256"], rec["arm"], rec["predicate"], rec["world"]["name"]) == nid`,
     plus genome_sha256 == the subject digest the node is looked up under.
S-5  B8 THE NULL ARM IS A NO-OP ON A PLASTIC CARRIER (ares_client.arm("NULL"); SEMANTIC; the registered P-CAL design).
     reset_each_step zeroes v[:, OBS_DIM:] at the start of every step (substrate.Runtime.step) and nothing else: the
     plastic update still writes W1 every tick, W1 survives interrupts and steps, and a carrier that re-derives its
     hidden node from inputs each step (POS: h = cue + W1[h, 5]) acts IDENTICALLY under NULL and under S (0 of 320
     actions differ; S-NOPL differs in 49 post-interrupt actions on the same episodes). RULER.md s5.1 calls NULL "a
     no-carry organism"; ares_client's docstring says "no persistent state"; both are true only of activation carriers.
     BEARS ON THE REGISTERED RUN in the unqualifying direction: NULL is built from S4; if S4 retains through plastic W1,
     NULL(S4) retains too, P-CAL FAILS and both subjects are DETECTION_UNQUALIFIED -- the instrument declares itself
     unqualified precisely when the subject carries by the allowed channel. If S4 carries by activations only (the
     designers' expectation), NULL does what it should. Either way P-CAL's NULL conjunct tests "no activation carry",
     not "no carry". This is a question about what the gate means (Pallas RESPONSIBILITIES s4: to the operator through
     Palamedes), not a code repair: PREREGISTRATION s4 reads "NULL reset_each_step / random population", and s10 allows
     a recorded amendment before any outcome. Options the operator may weigh: NULL := subject with reset_each_step AND
     plasticity zeroed; or the random-population reading; or keep NULL as is and read P-CAL's NULL conjunct narrowly in
     RESULT.md. I do not choose.
S-6  E1 WINDOW BOUNDARY UNPINNED THROUGH THE EVALUATOR (test-coverage). min(steps) for max(steps) survives 154 tests
     because every synthetic evaluator trace answers only after the LAST interrupt; S3 (correct between the first and the
     last interrupt, abstain after) is the fire case and reads NEGATIVE 0/0 on the frozen code. Not a defect in the
     frozen code; a missing pin on the registered rule.
S-7  E2 S-NOPL WITHOUT copy() (test-coverage; fail-closed on the frozen path). The arm tests inspect the returned
     population only. Consequence on the frozen DRIVER path (diagnostic, no evaluator): receipt_dict recomputes the
     subject digest AFTER the arm runs, so once S-NOPL has zeroed the shared subject's R in place, the S-NOPL node and
     every later node of that subject carry a DIFFERENT digest (f186cfac... -> 8cd1d44d...) and node ids that no longer
     match the plan, the ledger rows or the manifest: evaluation refuses the bundle (NODE_ID_MISMATCH / RUN_UNREPORTED),
     UNQUALIFIED, not a wrong class. Silent at launch, loud at evaluation. Still worth one pinning test (a subject with
     R != 0 passed through arm("S-NOPL") keeps its R).
S-8  E3 RUN_UNREPORTED DROPPED (test-coverage). No evaluator test removes a manifest entry while keeping its COMPLETED
     row. On the frozen driver every node that runs is presented, so the reachable shape is a hand-edited manifest
     (which custody then refuses, as B7 receipt_file_swap shows when the manifest is NOT re-registered) -- the check
     matters against a re-registered manifest. Pin it.
S-9  E5 P-ERASE / P-PRES ORACLE UNCHECKED (test-coverage). The oracle-counterfeit test flips a P-RET node only. Combined
     with S-3 the probe set's shape becomes unauditable from the bundle. Pin it (flip a P-ERASE node's regimes).
S-10 E6 ONE-SIDED P-CAL MARGIN UNPINNED (test-coverage; the registered rule FD-T014-3). `x > k_neg` -> `x >= k_pos`
     survives 154 tests; a NULL or SHUF arm with 1074-1077 correct would PASS calibration under the mutant and FAIL as
     registered ("the gate never passes by default"). Pin at 1074 and 1077.

Declared escape and contract limit, confirmed (not scored as survivors):
D-1  B4 TWO-BACK LEAK. A reset that hands episode k the live W1 of episode k-2 reads 0 on both one-step gates and carries
     (640 differing probe actions over 16 three-episode probes); the production one-back leak fires both gates (2560 /
     1280); S.Runtime reads 0 everywhere. ERASE_PROBES s1 declared this. NOT reachable for the registered subjects:
     S.Runtime.reset does `v[:] = 0; W1[:] = pop.W1` and the runtime holds no other per-episode state (code read). Note for
     any future runtime: the registered witness list ALTERNATES r = 0 / r = 1, so an even-delay carry delivers the CORRECT
     regime to every episode -- the parity of the seed list and the delay of a leak interact.
D-2  B6 COUNTERFEIT TRACE. The evaluator verifies integrity (hashes, rows, custody, oracle), not provenance: an
     always-correct trace filed under a real bundled genome is POSITIVE. PREREGISTRATION s7's "nothing it uses comes from
     a field the producer computed" is true of counts and outcomes, not of the trace bytes. The driver is deterministic
     and the genome is in the bundle, so a K-episode replay check would close it at the cost of K x 40 steps.

Vocabulary notes (no case): a mis-paired S-NOPL (SEEDS_NOT_PAIRED) yields P-CHAN FAIL and the class "POSITIVE (channel
unidentified)", a scientific class for a protocol defect (rso-builder 2.5); the frozen driver refuses the config, so it is
unreachable today, but a refusal (UNQUALIFIED) would be the honest vocabulary.

## 5. What held

The storage and binding plane on real driver output: 16 receipts bind; the content-addressed artifacts, the per-launch
inventory (C-010-T012_1 option 2) and custody fail closed under every tamper tried, including the two re-registered
tampers where custody cannot help and binding / node identity catch it. The ruler's window semantics as implemented
(S2, S3). The W15 interrupt pin (E4 killed by the carrier test, as predicted). The honest path at n = 2048 end to end,
which the dry run had not reached.

## 6. Repair-round suggestions (owners decide; one round, PREREGISTRATION s8)

evaluate.py (Argus): refuse a node id presented by > 1 bundle; enforce the committed SEED_LISTS.json for P-CAL, P-OBS,
P-ERASE, P-PRES as well as WITNESS_SEEDS for P-RET / P-CHAN; check the P-ERASE triple regime pattern and the P-PRES
warm-up pattern in _check_oracle; require the S and S-LEAK P-ERASE nodes to share one seed list; rebuild and compare the
node id from the receipt's fields; make --seeds required; tests for the S3 shape, RUN_UNREPORTED, a flipped P-ERASE
oracle. ruler.py (Argus): pin p_cal at 1074 / 1077. ares_client.py (Cadmus): pin arm("S-NOPL") leaving the subject's R.
The NULL arm (S-5) is the operator's call through Palamedes, before T020 runs the subjects.

## 7. Limits of this challenge

No fresh shape against the seed-refusal logic of load_config or against make_configs' exclusion arithmetic (both rest on
the frozen T016 / T013 tests). B4 and B8 are construction demonstrations, not evaluator cases. B5 and B6 need a producer
that lies consistently; their value is the missing cheap checks, not a reachable exploit. The reviewer read two witness
test files before choosing the edits (EXPOSURE.md), so E1 / E3 / E5 are informed probes of coverage, not first-sight. A
Fable session of the same vendor family as the builders; cell-internal hardening (CAMPAIGN OP-3).

## 8. Resources

2 of 2 permitted launches on rso/witness/LEDGER.jsonl: W1-CASES 142.8 CPU-s (process CPU; the S1 driver's three launches
ran on a temp ledger inside it, 116.2 CPU-s of that); W1-MUTATION 9 children, 643.4 charged wall-seconds (conservative:
wall, not CPU). C-010 ledger after this packet: 2 launches, 786.2 CPU-s of 3600, 7,176,308 artifact bytes of 200 MB
(the scratch tree; deleted; no bundle committed). Unledgered and disclosed: check-build 13 s; diagnostics (a) ~15 s and
(b) ~2 s; the acceptance run 70 s. Reviewer about 60 min wall against the packet's 45: the headless split of the
mutation launch and the real driver run at n = 2048 are the overrun. No paid compute; no Fabric task; nothing registered
with Aporia (fixture keeper store throughout).
