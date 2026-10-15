C-019-T040 INTEGRATION_READY -- Argus[harry1-666e5dbc], claude-opus-5-5 (Q2), harry1

- Branch: argus/c019-t040 @ 86f0f4640 (base 0546be826).
- State commit: c9e6be13d on main.
- Receipt: ops/campaigns/C-019/tasks/C-019-T040/attempts/A-001/RECEIPT.json.
- Everything is in rso/gen5/ananke/eval/ (README.md first).

RESULTS (all read-only; owner records via git show @ f58362c5e; pops/C5T never opened)

1. Independent evaluator on the CPU oracle (no torch, no venv needed).
   - All 40 owner admission readings were reproduced: max |diff| in mean and lo99 is 0.0, and every status matches,
     including FLIP-0099 RELAY_LATCH INDETERMINATE.
2. Known answers: 108/108 PASS.
   - hold_latch on GATE: FALSE (new check).
   - DLIB: live lines 15/15; plant / reassembled / ctx-only / cue-only read TRUE / TRUE / FALSE / FALSE at 4 cells.
   - 56/56 library modules alone: not TRUE.
   - The reduce recomputes from per-trial arrays; 4 plan-fixed rows were replayed identically.
3. Rung-4 mechanics on the plants: 32/32 KNOWN.
   - USE-DISABLED keeps the module bytes and executes them, but redirects their writes to the dead O.chan. It loses
     competence on both GATE halves at 2 cells and on all of P_FLIP; a dead line use-disabled gives identical output.
   - One KNOWN expectation of mine was wrong. Offset transplant at FLIP-0004 was TRUE but not identical, because
     mut_site .001 perturbs Kp at a hashed instruction index. The failing reduce is preserved, the precondition is now
     computed from the physics, and the point is carried into the prereg's falsifiability table: library insertion
     changes moved lines' dynamics at that cell.
4. Accessibility statistics (17 synthetic known-answer tests).
   - Exact CP and Fisher; right-censored Kaplan-Meier (an all-censored arm stays finite: median NOT_REACHED);
     log-rank; paired McNemar on (cell, idx); exact power; a search-table contract.
5. PREREG_DRAFT_PARTS_SUITABILITY.md, status DRAFT -- REQUIRES OWNER SIGN-OFF, not frozen.
   - Contents: 6 arms, the six claims separated (claim 6 narrowed), a falsifiability table, a completeness manifest
     template, and the s11 block with measured throughput.
   - Key number: detecting the designed-halves rate (2/32) against 0 needs 107 searches per arm for 80% power; at
     n = 32 the power is .05.
   - So I recommend a budget-calibration stage (CONSTRUCTED-POSITIVE vs CONTROL at 72 / 144 generations) before any
     comparison.
6. Adversary kit on the evaluator: exit 0.
   - 12 REJECTED, 1 LIMITATION (argus-c019t040-ka-replay-sample), 1 N/A, 0 SURVIVED, 0 VACUOUS.
   - The targets are registered in memory from my package. Making them permanent is a 2-line change for rso/adversary's
     owner (README s6).

Tests: 43 OK. Cost: about 7.6 CPU-h on harry1, at most 2 processes.

FOR YOU (coordinator):
- (a) Integrate the branch.
- (b) Owner contact (#2249) can now point Ananke at the draft. Decisions only the owner can make are in its s9.
- (c) Registry entry proposal: ananke-c4-independent-evaluator, AUTHOR_TESTED (README s6).
- No escalation, no operator decision required.
