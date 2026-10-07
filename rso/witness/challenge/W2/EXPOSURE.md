# C-010-T034 exposure note (Pallas[harry1-dc8e608d], claude-fable-5-1, harry1 / M4, headless)

STATUS: EXTENDED at the set commit (the INITIAL section below was committed first, e9f14ae21, before any repaired
witness material was opened; the EXTENSION records what was read between that commit and the set).

## Initial (committed e9f14ae21, before FREEZE_W2.md was opened)

Fresh HEADLESS session (comms boot 2026-10-07T13:36Z; same-seat relaunch on Fable under the operator directive of
2026-10-07 s10; launch note roles/Palamedes/prompts/2026-10-07_wake_pallas_c010_t034/WAKE_Pallas.md). It inherits
no in-context memory from the Pallas instance harry1-14289af6 that ran C-010-T014 (W1) or from any earlier Pallas
session; what it knows of them it read from the committed tree. Task worktree pallas-c010-t034 created from
origin/main 32586420a (fetch only; no pull). Claim 27b3d2f82 on main (ancestor verified). Comms on M1
(EW_DB_HOST=192.168.1.202).

Read BEFORE the initial note was written, in order:
- The wake prompt and Palamedes' launch note (13:40Z); ops/work_orders/CURRENT.md (MWO-0004); the base-role chain
  (RESPONSIBILITIES boot sequence s1, s2b, s7; WORKING_CONTRACT s1-s8; DISTRIBUTED_WORK s9); rso-builder-role
  RESPONSIBILITIES s8; roles/Pallas RESPONSIBILITIES and WORK_STATE.json (as left by the W1 instance).
- ops/campaigns/C-010/tasks/C-010-T034/TASK.json.
- My seat's own W1 record: rso/witness/challenge/W1/REPORT.md and EXPOSURE.md in full; the W1 directory listing.
- `git log 17b03160d..HEAD -- rso/witness rso/binding ares` (the repair round's commit subjects only).
- The file listings of ops/campaigns/C-010/tasks/C-010-T031, T032, T033 (names only).

Consequence already in force: this reviewer knows W1's ten survivors and W1's shapes (B1-B8, E1-E6) from its own
seat's report. The packet forbids re-using W1's shapes (they are regressions now, owned by the repair's own pins);
W2's three items must be FRESH shapes on the repaired surfaces.

## Extension (read between e9f14ae21 and the set commit)

FREEZE_W2 (rso/witness/FREEZE_W2.md, code commit 9dd4e9671): all 36 hashes and byte lengths (25 witness files, 11
frozen dependencies) verified against the committed LF blobs at HEAD via `git show HEAD:<path>` + sha256: 36 equal,
0 mismatch. 9dd4e9671 is an ancestor of HEAD; `git diff --stat 9dd4e9671 HEAD -- rso/ ares/` lists only
FREEZE_W2.md and rso/witness/challenge/W2/EXPOSURE.md. PREREGISTRATION.md's committed blob hashes to the registered
099f408f... (unchanged). rso/witness/LEDGER.jsonl: 22 rows, 2 TOP_LEVEL launches (W1), 786.2 CPU-s charged.

Read, in order:
- rso/witness/ADJUDICATION_W1.md and AMENDMENT_v1.0.1.md in full; the T031 and T032 receipts (A-001) in full; the
  T031 / T032 / T033 TASK.json histories (incl. the integrator's notes: FD-T031-W1 prefix reading NOT taken, P-OBS on
  every witness seed; integrator mutations killed by the new pins).
- `git diff 98345e104 9dd4e9671 -- rso/witness/evaluate.py` (the whole repair) and `-- rso/witness/ares_client.py`
  (R5); `git show 9dd4e9671` for evaluate.py / tests (the integrator's P-OBS change).
- rso/witness/evaluate.py IN FULL as frozen (header, decode, world_oracle, _check_oracle, _rebuilt_node_id, p_flat,
  witness_custody, check_bundle, _node, _check_seeds, _check_probe_shape, _validate_lists, episodes, _pair_gate,
  _p_cal, evaluate_subject, evaluate, main).
- rso/witness/ares_client.py: node_id, _array_artifact, _json_artifact, _groups, node_execution, receipt_dict,
  Launch, the count functions, regime_of, _scan, erase_probe_set, pres_seed_set, _probe_actions, p_erase_count,
  p_pres_diffs, and the arm() diff (NULL); not the carriers' bodies.
- rso/witness/run_witness.py: load_config, launch_inventory, launch (the failure path: inventory written, no
  MANIFEST), _default_launch_id; the module's def list.
- rso/witness/make_configs.py in full; rso/witness/ERASE_PROBES.md in full; PREREGISTRATION.md s4-s6, s8, s10.
- rso/slice001/mutation.py: load_edits, _is_committed, apply_edit, the child protocol, _run_child, _classify, run;
  rso/slice001/ledger.py: begin, the def list; rso/witness/contract.json.
- ares/substrate.py and ares/worlds.py: grep of Runtime.__init__/reset/step (reset_each_step zeroes v[:, OBS_DIM:];
  `v[:, :OBS_DIM] = obs` every step; plastic := allow_plasticity and any(R != 0)) and the worlds' _obs builders
  (OBS_DIM zeros filled per step) -- to judge whether any carry channel survives the amended NULL.
- My own W1 files: cases.py, run_cases.py, run_mutation.py, witnesses.py (head), edits_evaluate.json,
  CHALLENGE_SET.md, expected.json; the T014 receipt (format).

TEST BODIES. This session READ rso/witness/tests/test_evaluate.py lines 93-268 (Spec, the synthetic builders,
plan, write_bundle, keeper, seed_lists, Base) and lines 457-600 (TestW1Repairs IN FULL), plus the test NAMES of
test_evaluate.py, test_ares_client.py and test_ruler.py (grep of `def test_`). It did NOT read the bodies of
TestClasses / TestGateFailures / TestRefusals / TestTrustNothing (test_evaluate.py 269-456), nor any body in
test_ares_client.py, test_ruler.py, test_run_witness.py, test_make_configs.py, test_launch_inventory.py.
Consequence: W2.E1 was chosen KNOWING that the R1 pin (test_r1_b1_duplicate_node_across_bundles) uses two CLEAN
bundles and that no TestW1Repairs test pairs a refused bundle with a clean one; a kill by a test in the unread
classes would be a first-sight result; a kill by TestW1Repairs would be a reviewer error. The B1 shape (pair-gate
arrays shorter than the declared list) was chosen from the frozen code of _pair_gate and episodes, not from a test;
the test fixture's own _pair_node arrays are (n, T) rather than the driver's (n, T, 1), which is itself evidence
that _pair_gate pins no shape beyond a.shape == b.shape.

NOT read: rso/witness/CANDIDATES.md, DESIGN_DRAFT.md, PREREG_DRAFT.md, SELECTION.md, RULER.md body, dry_run.py body,
FREEZE_W1.md body; rso/binding/*; ares/search.py, ares/carriers.py bodies; any rso/slice001 test.

Development runs before the set commit (unledgered, no evaluator, no verdict, disclosed): the FREEZE_W2 hash walk;
`python -m workgraph ready`; the edit's find-string count in evaluate.py (1); a TEMP ledger check that a second
Ledger can begin and finish a launch after an earlier launch's START rows were left open (usage counts both, 4
inventory rows); import of cases_w2 / witnesses for syntax. No case, construction or edit outcome was observed.
After the set commit the driver's --check-build builds the B1 / E1 bundles and loads the S1 configs (no evaluator);
it is recorded in REPORT.md.

HARD GATE observed throughout (TASK.json non_goals; PREREGISTRATION s10): no registered subject configuration is
run (no `run_witness subject`, no ares.search.run); no witness episode on a registered arm; no statistic on any
registered arm; no edit of ares/ sources or of PREREGISTRATION.md; every seed this set uses lies at or above
5,000,000 (registered witness seeds scan upward from 900,000; P-ERASE / P-PRES seeds lie in [800,000, 900,000));
make_configs is NOT invoked. Organisms: the test suite's hand-wired leak construction, the POS carrier, one random
P = 1 population, synthetic action arrays. No count, accuracy, retention or ruler value of any registered-arm
construction is committed or printed: driver-produced results are redacted to structure.

Same-family caveat (as W1): reviewer and authors are Claude models of one vendor (T031 Argus, T032 Cadmus, T033
Palamedes claude-opus-5-5; this reviewer claude-fable-5-1). Cell membership: this seat is a member of the RSO
Builder Cell; this is cell-internal hardening, not an outside review (CAMPAIGN OP-3).
