# C-010-T034 W2 short re-check on FREEZE_W2 (committed before any outcome is observed)

Reviewer: Pallas[harry1-dc8e608d], claude-fable-5-1 (Q3), harry1 (M4), headless. Frozen surface: rso/witness/
FREEZE_W2.md (code 9dd4e9671; 25 witness files + 11 dependencies); its 36 hashes and lengths were verified against the
committed LF blobs at HEAD 32586420a before FREEZE_W2.md itself was read past its header, and 9dd4e9671 is an ancestor
with only FREEZE_W2.md and this directory above it under rso/ and ares/. Branch pallas/c010-t034 from 32586420a; claim
27b3d2f82 on main. Exposure: EXPOSURE.md beside this file. Not a second repair round (ADJUDICATION_W1; TASK.json).

Set: ONE fresh sound, ONE fresh broken (with a ruler-path control sub-case), ONE semantic edit, all on the repaired
surfaces R1-R5. None of W1's shapes (B1-B8, E1-E6) is re-run: those are regressions now and belong to the repair's own
pins (TestW1Repairs, TestArmsApplied, TestCalibrationMargin). Resource: ONE TOP_LEVEL launch on rso/witness/LEDGER.jsonl
(W2-RECHECK), shared by two foreground invocations (cases; mutation --finish); the S1 driver launches run on a TEMP
ledger inside it; the mutation children are MUTATION_CHILD rows parented to it.

## Answer key (expected.json is the machine-readable form; rows are scored against it, never the reverse)

W2.S1  FAILED_LAUNCH_RERUN_PAIR  (sound; R1-R5)
    The real driver (run_witness.launch) on hand-wired SA (the test suite's leak construction) and a random P = 1 SB,
    n = 2048, P-OBS on EVERY witness seed, this set's seed lists (>= 5,000,000; registered shapes). The SA launch is
    started in a child process and KILLED 25 s in: a launch that FAILED for a reason outside its inputs. It is then
    re-run with identical inputs (PREREGISTRATION s10: "a failed launch is re-run once with identical inputs and both
    are reported"); CONTROLS and SB run once. ALL FOUR bundle directories go to the evaluator, with seed_lists.
    PREDICTION: AS_EXPECTED. The driver writes no MANIFEST for a failed launch (run_witness.launch: "no MANIFEST
    written"; a kill writes even less), so check_bundle refuses the failed directory with BUNDLE_FILE_MISSING and lists
    no node id for it; R1 therefore does NOT fire on the s10 pair; nothing on the three complete bundles is refused;
    16/16 receipts bind; supplied_by names every registered node and maps SA's six to the re-run launch; P-CAL is
    evaluated; both subjects are classed and neither is UNQUALIFIED (values redacted); NULL by construction (R5) shows
    R = 0, runtime non-plastic, reset_each_step, W1 unwritten over 4 episodes, the shared subject untouched; every
    CONTROLS receipt's node id rebuilds from its own fields (R4).
    IF SURVIVOR: an over-refusal of the s10 pair would make the registered run UNEVALUABLE whenever a launch has to be
    re-run -- the operator could only recover it by withholding the failed bundle, against s10.

W2.B1a PAIR_EVIDENCE_SHORTER_THAN_DECLARED_LIST  (broken; R2, R3)
    DA's S/P-OBS, S/P-PRES, S/P-ERASE and S-LEAK/P-ERASE receipts declare the FULL registered-shape lists and carry the
    full world oracle for them (R2's list check and R3's regime-pattern check are satisfied on the fields), but the
    action arrays cover ONE episode / probe / pair: P-OBS equal, P-PRES equal, S/P-ERASE equal, S-LEAK differing.
    PREDICTION: SURVIVOR. evaluate._pair_gate checks a.shape == b.shape and nothing else: no first-dimension check
    against len(seeds) (P-OBS), len(seeds) / 3 (P-ERASE), len(seeds) / 2 (P-PRES), and no (T, 1) trailing-shape check.
    DA is classed (not UNQUALIFIED) with P-OBS PASS, P-PRES PASS, P-ERASE PASS qualified. R2 pins the receipt's seeds
    FIELD to the registered list; the evidence bytes are not tied to it on the three pair gates.
    Reachability: not producible by the frozen driver (node_execution stacks one row per seed group). A producer that
    runs fewer episodes than it declares: the B5 / B6 trust class. Does not make the registered run unevaluable or
    mis-classified by itself; it is a missing cheap check.

W2.B1b RULER_EVIDENCE_SHORTER_THAN_DECLARED_LIST  (broken, control; R2)
    The same shortening on DA's S/P-RET node (trace 1 x 40 x 1 under a 2048-seed declaration).
    PREDICTION: AS_EXPECTED. evaluate.episodes pins trace:actions to (len(seeds), 40, 1): SHAPE refusal, DA UNQUALIFIED.
    (Shows the asymmetry: the ruler path ties bytes to the list, the pair-gate path does not.)

W2.E1  r1-presenters-only-from-clean-bundles  (semantic edit; R1; evaluate.evaluate)
    `for nid in set(c["node_ids"])` -> `for nid in set(c["nodes"])` in the presenter census: only bundles that passed
    every bundle check count as presenting a node. A node presented by one clean and one REFUSED bundle is no longer
    EVIDENCE_DUPLICATE; the pooling loop then resolves it by ARGUMENT ORDER (clean first: evaluated; refused first:
    EVIDENCE_REFUSED, UNQUALIFIED). The registered rule is "no argument-order resolution" (ADJUDICATION_W1 R1).
    PREDICTION: SURVIVED on the full acceptance suite (test_r1_b1_duplicate_node_across_bundles uses two CLEAN
    bundles, both orders), NOT_EQUIVALENT_WITNESSED. Witness (witnesses.e1): X clean, Y refused (unregistered with the
    keeper), same node ids. Original: XY and YX both {"class": "UNQUALIFIED", "duplicate": true}. Mutant: XY
    {"class": "POSITIVE", "duplicate": false}, YX {"class": "UNQUALIFIED", "refused": true}.
    Bearing: reachable on the registered run only with a refused bundle beside a clean one (a tampered copy handed in
    with the original; a failed-launch directory that somehow acquired a manifest). The frozen code refuses both; the
    mutant lets the argument order decide. A one-line pin closes it (two bundles, one refused, both orders).

## Rules fixed now

- Verdict per repaired surface (REPORT.md s3): CLOSED if every W2 item on it reads as predicted for a sound surface
  (AS_EXPECTED on sound, refusal on broken, KILLED on the edit) and NOT CLOSED otherwise; a survivor is reported
  with whether it would make the registered run UNEVALUABLE (over-refusal / blocked) or MIS-CLASSIFIED (wrong class),
  or neither (not reachable by the frozen driver).
- A kill of W2.E1 by a test the reviewer did not open is a first-sight result; a kill by test_evaluate.py's
  TestW1Repairs (read; EXPOSURE.md) would be a reviewer error.
- No numeric outcome of any registered-arm construction (POS, NULL, SHUF, RECUR) is committed: S1 rows record
  structure (refusals, binding, custody, gates evaluated, that a class exists, supplied_by launch ids).
- Driver repairs after this commit may touch run_w2.py only; cases_w2.py, expected.json, edits.json and
  witnesses.py are frozen (git diff --quiet against this commit is quoted in REPORT.md).
