# C-009-T034 exposure note (Pallas[harry1-2b71b1e1], claude-fable-5-1, harry1 / M4, headless)

Fresh HEADLESS session (comms boot 2026-10-07T07:17Z; same-seat relaunch on Fable under the operator directive of
2026-10-07 s10; launch note roles/Palamedes/prompts/2026-10-07_wake_pallas_c009_t034/WAKE_Pallas.md). It inherits
no in-context memory from the Pallas sessions that ran C-004 T005/T030/T041/T048 or C-009 T030 (B1); what it knows
of them it read from the committed tree. Task worktree pallas-c009-t034 created from origin/main 0ad2d1a6f (fetch
only; no pull). Comms on M1 (EW_DB_HOST=192.168.1.202).

FREEZE_B2 (rso/binding/FREEZE_B2.md, code commit 1b69dd04a): all 48 hashes (29 implementation / contract / fixture,
19 test) verified BEFORE anything was written, three ways: against the committed blobs at HEAD 0ad2d1a6f, against
the committed blobs at 1b69dd04a, and against the LF-normalised working tree: 48 equal, 0 mismatch each time.
1b69dd04a is an ancestor of HEAD.

Read before writing this set, in order:
- The wake prompt and launch note; ops/work_orders/CURRENT.md (MWO-0004); the base-role chain (RESPONSIBILITIES,
  WORKING_CONTRACT, DISTRIBUTED_WORK s6/s9), rso-builder-role RESPONSIBILITIES, roles/Pallas RESPONSIBILITIES and
  WORK_STATE.
- ops/campaigns/C-009/tasks/C-009-T034/TASK.json; comms #1785 (roles/Palamedes/comms/2026-10-07_pallas_T034.md);
  the T031 (Argus) receipt in full (declared escapes incl. FD-T031-1; its description of the tests it added:
  B1 pins, BX5b sibling tests, the three inverse mutants "siblings never checked / FAILED sibling counted /
  siblings across launches", the consumer_for run_id probe); the T030 (B1) receipt.
- rso/binding/FREEZE_B2.md, ADJUDICATION_CC3.md, CONTRACT.md in full (s6 v1.0.1, s7 v1.1.0 BX5b), contract.json,
  R1/R2CHECK/REGRESSION.md, LEDGER.jsonl (summarised: 8 TOP_LEVEL launches, 1518.2 CPU-s, 13,381,360 artifact
  bytes).
- My own B1 record in full: REPORT.md, EXPOSURE.md, CHALLENGE_SET.md, cases.py, expected.json, edits.json,
  witnesses.py, run_cases.py, run_mutation.py, and the B1 results rows for SIBLING_UNREPORTED (r1) and the terminal
  summary.
- rso/binding/binding.py in full (the repaired module). The PRODUCTION diff 97606378c..1b69dd04a of binding.py,
  evidence.py, s2_run.py, stages/evidence_plane.py and contract.json (production and fixture-registration files
  only; NO test file of that diff was opened). rso/slice001/evidence.py: g_inv, launch_unbound, inventory_terminal,
  custody, required_records, Bundle, resolve_anchors, required_nodes, and the function index. rso/slice001/ledger.py
  in full (the producer's row reconstruction). s2_bundle.py: the index of its binding calls only.
- rso/slice001/fixtures/evidence_cases.py: Case, Base, synthetic_base, real_base, bind_legacy, the helpers
  make_bundle / _inventory / launch_row / manifest_of / retained / keeper_rows / _case and the function index.
  rso/slice001/mutation.py: apply_edit, the child runner, _classify, run(). The S3 driver helpers run_checks,
  emit_case, Rows, claim_summary, lines_of (reused by the drivers).
- rso/witness/ares_client.py: class Launch (produce, rows) and the module header; rso/witness/run_witness.py in
  full (the ledgered witness launch path). Read BEFORE the set because the packet asks for applicability to the
  native witness path; this instance is therefore not first-sight for a future witness-path challenge.

TEST BODIES. This session READ rso/binding/tests/test_binding.py in full (the frozen file, now 24 tests, including
T031's Siblings and B1Pins classes and the integrator's whole-node-id pin). It did NOT open any file under
rso/slice001/tests/ (test_evidence.py, test_s2_run.py and the others) or rso/witness/tests/. Consequence: the one
semantic edit was chosen knowing which BX5b dimensions the binding unit suite pins (a digest-bearing COMPLETED
sibling; FAILED / INTERRUPTED / REFUSED, other-launch, other-node and MUTATION_CHILD rows as non-siblings; whole-
string node ids) and knowing, from the T031 receipt's prose only, the three inverse mutants the slice suite kills.
The edit avoids all of those. A kill by the slice suite is a genuine first-sight result; a kill by the binding unit
suite would be a reviewer error.

NOT read: any T031 test diff; rso/slice001/tests/*; rso/witness/tests/*; rso/slice001/s2/* and s4/* bundles; the
S2/S4 matrices; S5_FINAL_DISPOSITION.md; the slice CONTRACT.md body; rso/witness/*.md (PREREG_DRAFT, DESIGN_DRAFT,
SELECTION, RULER); the R1 bundle files beyond what the drivers load.

Development runs before the set commit (unledgered, disclosed): none that observed a case or edit outcome. The
driver gains a `--check-build` option that constructs each case (row counts, the hidden digest) WITHOUT calling the
consumer; if used after the set commit it is recorded in REPORT.md. `--dry` (controls only) as in B1.

Same-family caveat (as S3/S4/R2/B1): reviewer and authors are Claude models of one vendor (T031 author
claude-opus-5-5, T033 integrator claude-opus-5-5, this reviewer claude-fable-5-1). Cell membership: this seat is a
member of the RSO Builder Cell and wrote the S3, S4, R2 and B1 sets; this is cell-internal hardening, not an
outside review (rso-builder-role s4; CAMPAIGN OP-3; TASK.json names Dionysus as the other eligible role).
