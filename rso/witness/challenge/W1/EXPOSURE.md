# C-010-T014 exposure note (Pallas[harry1-14289af6], claude-fable-5-1, harry1 / M4, headless)

Fresh HEADLESS session (comms boot 2026-10-07T10:44Z; same-seat relaunch on Fable under the operator directive of
2026-10-07 s10; launch note roles/Palamedes/prompts/2026-10-07_wake_pallas_c010_t014/WAKE_Pallas.md). It inherits
no in-context memory from the Pallas sessions that ran C-004 T005/T030/T041/T048 or C-009 T030 (B1) / T034 (B2);
what it knows of them it read from the committed tree. Task worktree pallas-c010-t014 created from origin/main
17b03160d (fetch only; no pull). Claim 2ff41b5d9 on main. Comms on M1 (EW_DB_HOST=192.168.1.202).

FREEZE_W1 (rso/witness/FREEZE_W1.md, code commit 98345e104): all 33 hashes and byte lengths (22 witness files, 11
frozen dependencies) verified BEFORE anything was written, against the committed LF blobs at HEAD 17b03160d via
`git show HEAD:<path> | sha256sum`: 33 equal, 0 mismatch. 98345e104 is an ancestor of HEAD; `git diff --stat
98345e104 HEAD -- rso/ ares/` lists only FREEZE_W1.md itself. The CRLF working copy of PREREGISTRATION.md hashes
to ac72d8f2... (127 bytes longer); the committed blob hashes to the registered 099f408f6e7c1c3e6c1e3b885a2db42f
58efd5a0a941a7d8e23205ab623bc1f7 (CAMPAIGN.json, contract.json, FREEZE_W1.md agree). rso/witness/LEDGER.jsonl
does not exist yet (0 launches charged to C-010 before this packet).

Read before writing this set, in order:
- The wake prompt and launch note; ops/work_orders/CURRENT.md (MWO-0004); the base-role chain (RESPONSIBILITIES
  boot sequence, WORKING_CONTRACT s1-s8, DISTRIBUTED_WORK s9), rso-builder-role RESPONSIBILITIES (s8 bootstrap),
  roles/Pallas RESPONSIBILITIES and WORK_STATE.
- ops/campaigns/C-010/tasks/C-010-T014/TASK.json; CAMPAIGN.json; the T013 TASK.json history; the T010, T011,
  T012 receipts (notes / declared scope only); ops/campaigns/C-010/escalations/C-010-T012_1_RESPONSE.md.
- rso/witness/FREEZE_W1.md, PREREGISTRATION.md (frozen; s0-s10), RULER.md, ERASE_PROBES.md, contract.json,
  dry_run.py (read, NOT run); rso/binding/CLOSURE.md.
- The witness path IN FULL: rso/witness/evaluate.py, ruler.py, ares_client.py, run_witness.py, make_configs.py;
  rso/binding/binding.py in full.
- Frozen dependencies, the parts the attacks turn on: ares/substrate.py Population (copy, genome, from_genomes;
  the genome carries cfg) and Runtime (__init__, reset: v := 0 and W1 := pop.W1; step: reset_each_step zeroes
  v[:, OBS_DIM:] only, plasticity still writes W1); ares/worlds.py World base, W4HiddenRegime (cue steps 0-2,
  T 40, r drawn first in both modes), W15Interrupt (4 interrupts in [5, 34], drawn per episode);
  ares/search.py rollout (step order identical to run_episodes), balanced_seeds_for, EVAL_SEEDS location.
- rso/slice001: ledger.py (from_contract, begin, finish, inventory), evidence.py (FixtureStore, store_rows,
  inventory_terminal, REGISTRY_LOCATOR), receipt.canonical_bytes, adapter.file_code_ref, mutation.py (load_edits,
  apply_edit, run, _run_child, _classify, the child protocol).
- My own B2 record: CHALLENGE_SET.md, EXPOSURE.md, REPORT.md, edits.json, run_mutation.py, run_cases.py (header);
  the C-009-T034 receipt (format).

TEST BODIES. This session READ rso/witness/tests/test_evaluate.py and test_ares_client.py IN FULL, and the test
NAMES (grep of `def test_`) plus a few boundary lines of test_ruler.py, test_run_witness.py (header and names),
test_make_configs.py (names) and test_launch_inventory.py (names). Consequence: the semantic edits below were
chosen KNOWING which dimensions the witness evaluator suite pins (registered-seed check on P-RET by a reversed
list; SEEDS_NOT_PAIRED; the three P-FLAT shapes; receipt digest; artifact byte flip; P-RET oracle counterfeit;
custody missing/late; one missing node; > 1 organism) and which it does not (P-CAL arm seeds; duplicate nodes
across bundles; P-ERASE/P-PRES probe shape; node-id vs receipt-field agreement; RUN_UNREPORTED; the LAST
interrupt as the window boundary; the one-sided P-CAL margin in the 1074-1077 zone). A kill of a predicted
survivor by a test I did not open is a first-sight result; a kill by test_evaluate or test_ares_client would be a
reviewer error.

NOT read: rso/witness/CANDIDATES.md, DESIGN_DRAFT.md, PREREG_DRAFT.md, SELECTION.md; the bodies of test_ruler.py,
test_run_witness.py, test_make_configs.py; ares/search.run (the GA) beyond its signature; rso/binding/CONTRACT.md
body; any rso/slice001 test; ares/carriers.py; ares/tests/.

Development runs before the set commit (unledgered, disclosed): the acceptance command once on the frozen tree
(witness 133 OK in 67 s, binding 21 OK) as the baseline; the hash verification; `python -m workgraph ready`.
No case, construction or edit outcome was observed. dry_run.py was not run. After the set commit the driver's
`--check-build` constructs the synthetic bundles and verifies fixture PREMISES only (shapes, hashes, that a
construction's two arrays are equal where the case requires equality); it calls no evaluator and observes no
verdict; it is recorded in REPORT.md if used.

HARD GATE observed throughout (TASK.json; PREREGISTRATION s10): no registered subject configuration is run (no
`run_witness subject`, no ares.search.run at all); no registered arm runs on a registered seed; every seed this
set uses lies at or above 5,000,000 (registered witness seeds scan upward from 900,000; P-ERASE/P-PRES seeds lie
in [800,000, 900,000)); make_configs is NOT invoked (its output would be the registered-range lists). Organisms are
hand-wired (the test suite's leak construction, the POS/RECUR carriers), one random P = 1 population, and
synthetic action arrays. No count, accuracy, retention or ruler value of any registered-arm construction (POS,
NULL, SHUF, RECUR) is committed or printed: rows for driver-produced bundles record structure only (refusals,
binding, custody, which gates were evaluated, that a class exists), with every numeric field redacted.

Same-family caveat (as S3/S4/R2/B1/B2): reviewer and authors are Claude models of one vendor (T010 Cadmus and
T012 Argus claude-opus-5-5, T011 Eupalamus, T013 Palamedes claude-opus-5-5, this reviewer claude-fable-5-1). Cell
membership: this seat is a member of the RSO Builder Cell; this is cell-internal hardening, not an outside review
(rso-builder-role s4; CAMPAIGN OP-3; TASK.json names Dionysus as the other eligible role).
