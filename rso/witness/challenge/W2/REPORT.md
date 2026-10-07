# C-010-T034 W2 short re-check on FREEZE_W2 -- REPORT

Reviewer: Pallas[harry1-dc8e608d], claude-fable-5-1 (Q3), harry1 (M4), headless (comms boot 13:36Z; the one launch
14:05Z-14:12Z; 2026-10-07). Frozen surface: rso/witness/FREEZE_W2.md (code 9dd4e9671: evaluate.py, ruler.py,
ares_client.py, run_witness.py, make_configs.py, their tests, 11 dependencies); 36/36 hashes and lengths verified against
the committed LF blobs at 32586420a before the set and again on the merged tree f9d3866ee before this report. Branch
pallas/c010-t034 from 32586420a. Caveat printed with every closure record: cell member, writes no production code, same
vendor family as the builders (T031 Argus, T032 Cadmus, T033 Palamedes: claude-opus-5-5). Exposure: EXPOSURE.md
(test_evaluate.py's fixture and TestW1Repairs bodies were read before the set; no other test body was). No registered
subject was run, no registered arm ran on a registered seed (every seed >= 5,000,000), and no accuracy, retention or
ruler value of POS / NULL / SHUF / RECUR appears in this report or in any committed row.

This is NOT a second repair round (ADJUDICATION_W1; TASK.json): survivors are recorded for RESULT.md as known
escapes, each with whether it would make the registered run UNEVALUABLE or MIS-CLASSIFIED.

## 1. Ordering evidence (git; times UTC)

    27b3d2f82  claim of C-010-T034 (CLAIMED, LEASE.json; main)                                          13:39:47Z
    e9f14ae21  exposure record EXPOSURE.md, INITIAL, before FREEZE_W2.md was opened (branch)              13:41:38Z
    (verify)   FREEZE_W2 36/36 hashes against committed blobs; 9dd4e9671 ancestor; nothing else under
               rso/ ares/ above it                                                                        ~13:45Z
    19a18b936  set: cases_w2.py, expected.json, edits.json, witnesses.py, run_w2.py, CHALLENGE_SET.md
               with predictions, EXPOSURE.md extended (branch, pushed)                                    14:02:55Z
    check 1    run_w2.py --check-build (no evaluator, unledgered): B1a / B1b / E1 bundles build, S1 configs
               load (4, 6, 6 entries; P-OBS 2048 seeds); the edit's two-line find matched 0 times
               (CRLF working copy) -> NOT_APPLICABLE                      check_build_2026-10-07T140259Z  14:02:59Z
    5b4b75247  state: IMPLEMENTING (main)                                                                 14:03Z
    2933f4477  SET REPAIR BEFORE ANY OUTCOME, disclosed: edits.json find anchored to the FIRST occurrence
               of the single for-line (`occurrence: 1`); same edit, same fault; expected.json, cases_w2.py,
               witnesses.py untouched (branch, pushed)                                                    14:04:27Z
    check 2    --check-build again: edit applicable, find_count 2, occurrence 1 (second loop untouched,
               verified)                                                  check_build_2026-10-07T140429Z  14:04:29Z
    launch     W2-RECHECK-20261007T140519Z-12684 (the ONE TOP_LEVEL launch; rso/witness/LEDGER.jsonl)
               phase cases    14:05:19Z-14:08:22Z   results_w2.jsonl
               phase mutation 14:09:03Z-14:12:29Z   mutation_rows_w2.jsonl (2 MUTATION_CHILD rows); launch
                                                    finished COMPLETED
    f9d3866ee  merge origin/main 5b4b75247 (only this seat's two state commits upstream; nothing under rso/
               or ares/ changed); data files byte-identical to 2933f4477 (git diff --quiet); FREEZE_W2
               36/36 re-verified; acceptance 149 + 21 OK in the foreground (acceptance_stdout.txt)        14:13Z-14:15Z

Headless rule: no run_in_background anywhere; every command in the foreground with a timeout <= 600 s; no turn ended
with anything running. The one launch was shared by two foreground invocations (cases; mutation --finish) for that
reason, as W1's mutation launch was. Comms: CLAIMED note #1834 and a start heartbeat #1835 were posted; the
INTEGRATION_READY note and a completion heartbeat are the task notes.

## 2. Results

### 2.1 Cases (results_w2.jsonl; expected.json is the answer key)

    case                                              kind       observed                                           score
    ------------------------------------------------  ---------  -------------------------------------------------  -----------
    W2.S1.FAILED_LAUNCH_RERUN_PAIR                    sound      the SA launch killed 25.0 s in: 2 receipts and 4   AS_EXPECTED
                                                                 artifacts on disk, 3 node START rows and the
                                                                 launch START row open, no MANIFEST / inventory /
                                                                 run.json; re-run w2-s1-SA-attempt2 COMPLETED (6
                                                                 nodes), CONTROLS (4), SB (6); all FOUR directories
                                                                 to the evaluator: the failed one refused with
                                                                 BUNDLE_FILE_MISSING:MANIFEST.json, launch id None,
                                                                 no node id; 3 clean bundles P-FLAT PASS, custody
                                                                 QUALIFIED, nothing refused; 16/16 receipts bind;
                                                                 no EVIDENCE_DUPLICATE anywhere; supplied_by 16
                                                                 nodes = CONTROLS 4 + SA-attempt2 6 + SB 6 (every
                                                                 registered node present; SA's six from the re-run);
                                                                 P-CAL evaluated; S4 gates P-CHAN P-ERASE P-OBS
                                                                 P-PRES P-RET, S15 P-ERASE P-OBS P-PRES P-RET; a
                                                                 class for both, neither UNQUALIFIED (values
                                                                 redacted). R4: all 4 CONTROLS receipts rebuild
                                                                 their node id from their own fields, subject = SA.
                                                                 R5 by construction: reset_each_step True, runtime
                                                                 plastic False, R all zero = S-NOPL's R, W1
                                                                 unwritten over 4 episodes, shared subject's R
                                                                 untouched; NULL's arm genome digest differs from
                                                                 the subject's (R zeroed), SHUF's equals it.
                                                                 Temp ledger: 4 launches (1 open), 233,765 bytes.
    W2.B1a.PAIR_EVIDENCE_SHORTER_THAN_DECLARED_LIST   broken     nothing refused; DA POSITIVE; P-OBS PASS           SURVIVOR
                                                                 (0 differing), P-PRES PASS (0 differing), P-ERASE
                                                                 PASS qualified (D = 0, leak D = 1) -- on arrays of
                                                                 ONE episode / probe / pair under declarations of
                                                                 2048 / 64 triples / 32 pairs; DB NEGATIVE
    W2.B1b.RULER_EVIDENCE_SHORTER_THAN_DECLARED_LIST  control    DA UNQUALIFIED: SHAPE:...:S:P-RET:W15:trace:        AS_EXPECTED
                                                                 actions must be (n, 40, 1); DB NEGATIVE

### 2.2 Edit (mutation_rows_w2.jsonl; suite = both acceptance suites, 170 tests per child; baseline PASSED 170/170, 101.7 s)

    edit                                           module     status    tests/fail  witness original -> mutant
    ---------------------------------------------  ---------  --------  ----------  ---------------------------------------------
    W2.E1-r1-presenters-only-from-clean-bundles    evaluate   SURVIVED  170 / 0     XY {UNQUALIFIED, duplicate} ->
                                                                                    {POSITIVE, no duplicate, no refusal};
                                                                                    YX {UNQUALIFIED, duplicate} ->
                                                                                    {UNQUALIFIED, refused}            DIFFERS
                                                                                    (NOT_EQUIVALENT_WITNESSED; 103.9 s)

Predictions (CHALLENGE_SET.md / expected.json, written before outcomes): 3/3 cases, 1/1 edit, witness values exact.

## 3. Verdict per repaired surface (rule fixed in CHALLENGE_SET.md before outcomes)

    R1  duplicate refusal / supplied_by     NOT CLOSED   S1: no over-refusal of the s10 (failed, re-run) pair; supplied_by
        (evaluate.evaluate)                 (coverage)   complete and names the re-run. E1 SURVIVES: the presenter census is
                                                         pinned for two CLEAN bundles only; a (clean, refused) pair is
                                                         unpinned. The FROZEN code handles it correctly (witness original:
                                                         EVIDENCE_DUPLICATE in both orders).
    R2  registered lists required           NOT CLOSED   S1: the honest lists (P-OBS on all 2048) are accepted. B1a SURVIVES:
        (evaluate._check_seeds / _pair_gate)             the list is enforced on the receipt's seeds FIELD; on the three pair
                                                         gates the evidence BYTES are not tied to it (_pair_gate checks
                                                         a.shape == b.shape only). B1b: the ruler path IS tied (episodes
                                                         pins (len(seeds), 40, 1)).
    R3  probe regime patterns               CLOSED       S1: registered-shape triples / pairs accepted; the R3 check reads
        (evaluate._check_probe_shape)       within       regimes from the world for the declared seeds. No fresh shape against
                                            coverage     the pattern itself; B1a's finding (bytes vs declaration) is R2's.
    R4  node id rebuilt from receipt fields CLOSED       S1: 16 real driver receipts (4 arms incl. NULL / SHUF / RECUR on SA)
        (evaluate._rebuilt_node_id)         within       rebuild their ids and bind; no fresh broken shape against it.
                                            coverage
    R5  NULL per AMENDMENT_v1.0.1           CLOSED       S1: by construction on the plastic POS carrier, NULL has R = 0 (=
        (ares_client.arm("NULL"))           within       S-NOPL's), runtime non-plastic, reset_each_step, live W1 unwritten;
                                            coverage     the shared subject untouched; through the driver the NULL node binds,
                                                         evaluates and carries a digest distinct from the subject's. Code
                                                         read: substrate.step writes all OBS_DIM slots each step and zeroes
                                                         v[:, OBS_DIM:]; with R = 0 nothing else persists.

## 4. Survivors, class, and whether each bears on the registered witness run

S-1  W2.B1a PAIR-GATE EVIDENCE NOT TIED TO THE DECLARED LIST (evaluate._pair_gate; behavioural, producer-trust class).
     R2 compares `rec["seeds"]` with the registered list and R3 recomputes the regimes for those seeds, but for P-OBS,
     P-PRES and P-ERASE the only check on the action arrays is that the two arrays share a shape. A P-OBS node that
     declares all 2048 witness seeds with a correct full oracle and carries two equal (1, 40, 1) arrays PASSES; the same
     for P-PRES and P-ERASE with one probe / pair, and the leak member fires on one differing byte. The ruler path does
     not have this gap (B1b: SHAPE). UNEVALUABLE? No. MIS-CLASSIFIED? Not by the frozen driver: node_execution stacks one
     row per seed group, and the receipt it writes is the one bound; the gap needs a producer that runs fewer episodes
     than it declares (the B5 / B6 trust class). Cheapest closure: in _pair_gate require a.shape == (len(seeds) // k,
     40, 1) with k = 1 / 2 / 3 by predicate (the driver's shapes; the evaluator test fixture's own (n, T) pair arrays
     would need the trailing dimension). Known escape for RESULT.md.
S-2  W2.E1 R1 PRESENTER CENSUS UNPINNED FOR A (CLEAN, REFUSED) PAIR (test-coverage; the frozen code is correct). The
     mutant counts only clean bundles as presenters and passes all 170 tests; the witness shows the registered rule
     ("no argument-order resolution") then fails exactly where W1.B1 failed before the repair, in the one configuration
     the pin does not cover. UNEVALUABLE / MIS-CLASSIFIED? Neither on the frozen code (witness original: UNQUALIFIED
     with EVIDENCE_DUPLICATE in both orders). Reachable on the registered run only with a refused bundle beside a clean
     one presenting the same nodes (a tampered copy handed in with the original; a failed-launch directory that somehow
     acquired a MANIFEST). One pinning test closes it: two bundles, one refused (custody), same node ids, both orders.

## 5. What held (the sound direction, which is what T020 needs)

The s10 protocol is evaluable under the repaired R1: a killed launch leaves a directory with receipts and artifacts
but no MANIFEST, inventory or run.json; the evaluator refuses it with a typed reason, assigns it no launch id and no
node id, and R1 does not fire on the re-run's nodes. The honest three-launch path at n = 2048 with P-OBS on every
witness seed (the integrator's reading of s5, FD-T031-W1 not taken) passes every repaired check end to end on real
driver output: lists (R2), probe patterns (R3), id rebuild (R4), binding, P-FLAT, custody, and supplied_by names the
launch of each of the 16 nodes. The amended NULL is no-carry by construction (R5). The ruler path ties bytes to the
declared list (B1b). Cost observed for T020's budget: the three complete launches charged 174.7 CPU-s on the temp ledger
(P-OBS on all seeds is 2 x 2048 episodes per subject).

## 6. Repair-round suggestions

None requested: this is not a second repair round (ADJUDICATION_W1). For RESULT.md's known-escape list: S-1 (one
shape check in _pair_gate) and S-2 (one pinning test). Both are one-line / one-test items an owner may take at any
later freeze; neither blocks T020.

## 7. Limits of this challenge

One sound, one broken (+ control), one edit, as the packet sized it. No fresh shape against R3's pattern check itself
(a (1, 0) triple pattern, or an unbalanced probe set, would pass R3 as written: the probe episode's regime and the
balance of the probe set are not checked; the registered generator produces the right shape, and the committed
SEED_LISTS.json is the tie). No fresh broken shape against R4 or R5 (both read as closed by construction; the time
budget went to the s10 sound case, which is the one that could have made the registered run unevaluable). The
reviewer read test_evaluate.py's fixture and TestW1Repairs before choosing E1 (EXPOSURE.md), so E1 is an informed
coverage probe, not first-sight. Same vendor family as the builders; cell-internal hardening (CAMPAIGN OP-3).
The set needed one pre-outcome repair (2933f4477: the edit's find anchored by occurrence after check-build showed the
two-line find did not match the CRLF working copy); no outcome had been observed, and the edit's semantics are
unchanged. Minor accounting note, not chased: the temp ledger's 16 node rows sum to 174.7 CPU-s while the parent's
process_time over the whole cases phase was 156.6 s; the campaign ledger was charged the larger composite (387.2 s =
156.6 process + 25.0 killed-child wall + 205.6 mutation-children wall, all conservative).

## 8. Resources

1 of 1 permitted launch on rso/witness/LEDGER.jsonl: W2-RECHECK-20261007T140519Z-12684, COMPLETED, 387.2 charged
CPU-s (composite above), 2,914,569 scratch bytes (deleted; no bundle committed), 2 MUTATION_CHILD rows (101.7 s
baseline, 103.9 s mutant). C-010 ledger after this packet: 3 launches of 10, 1379.1 CPU-s of 3600, 10,090,877 artifact
bytes of 200 MB. Unledgered and disclosed: the hash walks (~5 s); two --check-build runs (~6 s each); the development
checks before the set (edit find-count; temp-ledger open-run tolerance; imports); the acceptance run on the merged
tree 99.5 s. Reviewer about 40 min wall (13:36Z boot to this report) against the packet's 25: the base-role bootstrap
chain plus reading the repaired evaluator in full took ~20 min before the set. No paid compute; no Fabric task;
nothing registered with Aporia (fixture keeper store throughout).
