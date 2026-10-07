# C-009-T030 exposure note (Pallas[harry1-b97f1fc4], claude-fable-5-1, harry1 / M4, headless)

Fresh session (comms boot 2026-10-07T03:28Z; same-seat relaunch on Fable under the operator directive of
2026-10-07 s10). It inherits no in-context memory from the Pallas sessions that ran C-004 T005, T030, T041 or
T048; what it knows of them it read from the committed tree. Task worktree pallas-c009-t030 created from
origin/main 5fefee452 (fetch only; no pull). Claim commit 4aaa10bbb (CLAIMED, LEASE.json) on main.

FREEZE_B1 (rso/binding/FREEZE_B1.md): all 48 hashes verified before anything was written, against the committed
LF blobs at 5fefee452, against the committed blobs at the freeze code commit 97606378c, and against the
LF-normalised working tree: 48 equal, 0 mismatch (the five commits origin/main gained during this boot touch
rso/witness/, ops/campaigns/C-009 and roles/Palamedes/comms only).

Read before writing this set, in order:
- ops/campaigns/C-009/tasks/C-009-T030/TASK.json, C-009-T020/TASK.json, the operator directive
  (roles/Palamedes/prompts/2026-10-07_rso_completion_push/01_OPERATOR_DIRECTIVE_verbatim.md), the T011 (Argus)
  and T010 (Eupalamus) attempt receipts in full (declared escapes, choices, evidence prose).
- rso/binding/CONTRACT.md (BX1-BX7, s3 CC1-CC4, s6 v1.0.1 clarification), contract.json, FREEZE_B1.md,
  R1/REGRESSION.md, PREDICTIONS_CC2.md, LEDGER.jsonl, R1/G0 (inventory.json, MANIFEST.json head, run.json),
  R1/PRODUCE.json.
- rso/binding/binding.py in full. rso/slice001/evidence.py in full (g_inv, launch_unbound, custody, Anchors,
  resolve_anchors, required_nodes, Bundle). rso/slice001/ledger.py in full. rso/slice001/s2_bundle.py in full.
  rso/slice001/s2_run.py in full (consumer_for: the production consume path). receipt.py: function index and
  module header only. checker.py: function index and the Consumer class.
- rso/slice001/fixtures/evidence_cases.py in full (the helpers every case is built from), fixtures/cc1_cases.py
  in full (the CC1 shapes this set must NOT replay), mutation.py in full.
- rso/slice001/challenge/R2/ (this seat's prior set): EXPOSURE.md, CLOSURE_SET.md, REPORT.md, cases.py,
  expected.json, edits.json, witnesses.py, run_cases.py, run_mutation.py; from challenge/S3/attack_set/
  run_cases.py the helper functions reused by the drivers (Rows, run_checks, decide_case, emit_case, lines_of).

TEST BODIES. This session READ rso/binding/tests/test_binding.py in full (13 tests, 4224 bytes; it is one of the
19 FREEZE_B1 test files). It did NOT open any file under rso/slice001/tests/ (420 tests), nor
rso/witness/tests/. Consequence, stated so the reader can weigh it: the five semantic edits were chosen knowing
which BX1/BX2 dimensions the binding unit suite pins (digest, status FAILED, node id, foreign launch, missing
digest, no/ambiguous row, unanchored/absent/FAILED launch, TOP_LEVEL cited as a node run) and which it does not;
they were NOT chosen with knowledge of the slice suite's fire cases (TestBX1Launch, TestBX5OwnLaunch,
TestBX7InventoryCustody, TestCC1Binding are known by name and count from the T011 receipt only). A kill by the
slice suite is therefore a genuine first-sight result; a kill by the binding suite would be a reviewer error.

NOT read: any T010/T011 diff (the implementation was read in its frozen final form only); rso/slice001/s2/* and
s4/* bundles; the S2/S4 matrices; S5_FINAL_DISPOSITION.md; the slice CONTRACT.md body and its amendments
(clause numbers only, via the code's comments); rso/witness/*; any file outside rso/, ops/campaigns/C-009,
roles/Pallas, roles/Palamedes/prompts and the base-role chain.

Development runs before the set was committed (unledgered, disclosed): none that observed a case outcome. One
import/dry check of the drivers against the two CONTROL bundles (the unedited G0 under the frozen code, whose
decisions CC2 already published) is permitted by CHALLENGE_SET.md and recorded there if used. No case, probe or
edit was executed before the set commit.

Same-family caveat (as S3/S4/R2): reviewer and authors are Claude models of one vendor; the T010 author ran
claude-sonnet-5-5, the T011 author claude-opus-5-5, the T020 integrator claude-opus-5-5, this reviewer
claude-fable-5-1. Cell membership: this seat is a member of the RSO Builder Cell and wrote the S3, S4 and R2
sets; this is cell-internal hardening, not an outside review (rso-builder-role s4; CAMPAIGN OP-3).
