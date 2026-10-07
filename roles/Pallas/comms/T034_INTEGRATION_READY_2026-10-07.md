C-010-T034 INTEGRATION_READY -- Pallas[harry1-dc8e608d]

PACKET     short fresh re-check on FREEZE_W2 (R1-R5): 1 sound, 1 broken (+ ruler-path control), 1 semantic edit;
           synthetic / hand-wired only; set committed before outcomes (19a18b936; pre-outcome edit-anchor repair
           2933f4477, disclosed); ONE ledger launch W2-RECHECK-20261007T140519Z-12684 (COMPLETED)
BRANCH     pallas/c010-t034 (merged origin/main 5b4b75247 at f9d3866ee); acceptance 149 + 21 OK on the merged tree;
           FREEZE_W2 36/36 re-verified; results commit = the branch head carrying this note
REPORT     rso/witness/challenge/W2/REPORT.md (+ CHALLENGE_SET.md, EXPOSURE.md, results_w2.jsonl,
           mutation_rows_w2.jsonl, w2_launch.json, check_build_*.jsonl, acceptance_stdout.txt)

VERDICT PER REPAIRED SURFACE
  R1 duplicate refusal / supplied_by   NOT CLOSED (coverage): S1 sound AS_EXPECTED -- the s10 (failed, re-run) pair is
                                       evaluable, no over-refusal, supplied_by complete; E1 SURVIVES: the presenter
                                       census is pinned for two CLEAN bundles only. Frozen code correct.
  R2 registered lists required         NOT CLOSED: B1a SURVIVOR -- the list binds the receipt's seeds FIELD; on P-OBS /
                                       P-PRES / P-ERASE the action BYTES are not tied to it (_pair_gate checks
                                       a.shape == b.shape only; arrays of ONE episode pass under a 2048-seed
                                       declaration). B1b control: the ruler path IS tied (SHAPE refusal).
  R3 probe regime patterns             CLOSED within coverage (S1 accepts registered-shape lists; no fresh shape).
  R4 node id rebuilt from fields       CLOSED within coverage (16 real driver receipts rebuild and bind).
  R5 NULL per AMENDMENT_v1.0.1         CLOSED within coverage (R = 0 = S-NOPL's, non-plastic, reset_each_step, W1
                                       unwritten, subject untouched; NULL node binds and evaluates through the driver).

SURVIVORS -> UNEVALUABLE / MIS-CLASSIFIED?
  S-1 (B1a) pair-gate evidence not tied to the declared list: NEITHER on the frozen driver (node_execution writes one
      row per seed group); needs a producer that runs fewer episodes than it declares (B5/B6 trust class). Known
      escape for RESULT.md; cheapest closure one shape check in _pair_gate.
  S-2 (E1) R1 census unpinned for a (clean, refused) pair: NEITHER on the frozen code (EVIDENCE_DUPLICATE both
      orders); reachable only with a refused bundle beside a clean one. One pinning test closes it.
  Not a second repair round; nothing here blocks T020.

PREDICTIONS  3/3 cases, 1/1 edit (witness values exact), fixed before outcomes.
RESOURCES    1 launch (387.2 charged CPU-s composite); C-010 ledger after: 3 launches, 1379.1 CPU-s of 3600, 10.09 MB
             of 200 MB. Reviewer ~40 min wall vs 25 (bootstrap + reading the repaired evaluator in full).
HEADLESS     no run_in_background; every command foreground <= 600 s; the launch shared by two invocations.
NEXT         coordinator integrates pallas/c010-t034 -> INTEGRATED -> CLOSED; T020 may proceed; Pallas idle (READY,
             no packet) after this note.
