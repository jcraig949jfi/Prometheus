# Nestor-G journal -- METRIC HARDENING builder (round 3)

Seat: Nestor[m1-c77819fe], PM_LANE=G, worktree F:/Prometheus-worktrees/nestor-bld-g, branch
nestor/bld-g-2026-09-14. Package (ROUND3_BACKLOG s2): M1, M2, M3, C1, C2, C4, D-open (easy-metric
discriminator). Threads: 4 (conductor contract 1789425755152-0 overrides the boot prompt's 5).

## 2026-09-14 epoch 1, iteration 1 -- C2 sampler_seed mandatory

- primordial/qd/archive.py: `sampler_seed` has no default in `_Base`/`LuaArchive`; omitting it is a
  TypeError, `None` a ValueError, any string other than `UNSEEDED` a ValueError. `UNSEEDED` is the
  explicit label for a frozen pre-C2 harness: it keeps the round 1 ZRANDMEMBER sampler and the
  archive reports `replayable=False`.
- Elites per run seed: `save_elites(arch, path, run_seed)` writes one canonical JSON document
  (schema qd-elites-v1: run, run_seed, sampler_seed, replayable, glen, cells ascending with fit,
  genome hex, meta hex); `load_elites`, `restore_elites` read it back.
- Callers: 19 frozen harnesses (qd/e1,e2,e4,e4b,e5..e10; cohorts b1, c r2_01..05/08, d3, d4) now
  pass `UNSEEDED` explicitly -- behaviour unchanged, the non-replayability is labelled in code.
  C-R2-09 already seeds. D4's DetArchive forwards its seed; E2's LineageArchive takes one.
- Tests: primordial/qd/tests/test_archive_c2.py -- no-seed raises (Lua, Racy, Lineage); UNSEEDED
  not replayable; array seed ok; replay: two runs at the same (run_seed, sampler_seed) give
  identical elites and a byte-identical elites file, a different sampler seed differs; saved
  elites restore into a fresh archive with an equal dump; glen mismatch raises.
- New harnesses from round 4 on must pass a real seed and save elites per run seed.
- Pushed 3ee6df577; suite 138 passed.

## 2026-09-14 epoch 1, iteration 2 -- M1 floors (w4, w1, w3): abstain beats every baseline

Predicate posted before the run (bus 1789426397961-0, G-M1-floors-w134). primordial/metric/floors.py:
abstain; best fixed action (exhaustive over 8^W, selected on the pressure's TRAIN seeds, scored on
HELD64); uniform random action (8 policy seeds). Tests: the batched constant scorer == wforge
replay; chunking invisible; random policy seeded.

| world | pressure | abstain held64 | best fixed | random median | best baseline held64 |
|---|---|---|---|---|---|
| w4 | train8 | 107.75 | abstain | 11.49 | 89.94 |
| w4 | train128 | 107.75 | abstain | 11.49 | 98.76 |
| w1 | train8 | 88.28 | abstain | 0.00 | 35.46 |
| w1 | train128 | 88.28 | abstain | 0.00 | 63.94 |
| w3 | train8 | 122.63 | abstain | 0.89 | 103.16 |
| w3 | train128 | 122.63 | abstain | 0.89 | 105.58 |

Aimed at the claim, not beside it: an all-zero-codebook G7 genome (linear and tt_feat) scored by
the production scorers, numpy E7.rollout and FusedRollout, gives exactly these numbers (w4 held64
107.75, train8 153, train128 112.375) -- so it is the metric the baselines were scored with.
The committed elites are below abstain on TRAIN too (w4 E9 train8 ~145 vs 153; B train128 ~105.5 vs
112.4; w1 <=167 vs 236; w3 <=31 vs 34.5): the QD runs never reached the do-nothing policy.
Predicate prior (w4 const ceiling >= 90): TRUE, and stronger than posed -- the ceiling IS abstain.
Consequence: every round 2 clause A PASS was measured against a baseline below a 0-byte floor.
Rows: primordial/ledger/rows/G/G-M1-floors-w134.jsonl; 18 floor cells (status control, floor=<kind>)
in cells.jsonl. Not explained here: why the archives miss the abstain cell.
Next: `qd_ledger check` reports raw and floor-normalized verdicts (BELOW_FLOOR / NO_HEADROOM); B's
8 B cells re-judged.
Pushed 3869d7442 (suite 142); anomaly 1789419655457-0 RESOLVED on the queue with this discriminator.

## 2026-09-14 epoch 1, iteration 3 -- M1 check reads every verdict against the floor

- primordial/ops/qd_ledger.py: `check` keeps the raw clause A verdict and adds `floor`:
  {verdict, floor_held64, floor_kind, normalized}. `floor_of` takes the highest floor row
  (floor=<kind>, status control) for the world x pressure. No new threshold: BELOW_FLOOR if
  median - 0.5*IQR <= floor; NO_HEADROOM if every front baseline is <= floor; INELIGIBLE and
  NO_BASELINE pass through; otherwise the raw verdict. normalized = (median - floor) /
  (baseline - floor), None where the baseline is at or below the floor. Floor rows never enter
  `top` or `pareto` (status control).
- Tests: primordial/tests/test_qd_ledger_floor.py (6). Suite 148 passed.
- Re-judgment of every non-baseline w1/w3/w4 train*_held64 cell in cells.jsonl (31 rows):
  23 raw PASS, 5 raw FAIL, 3 INELIGIBLE (status cheat). Under the floor, all 28 record rows are
  BELOW_FLOOR. B's 8 B cells (8 record rows) are all BELOW_FLOOR:

| world | pressure | mechanism | median | raw | floor |
|---|---|---|---|---|---|
| w4 | train128 | int2 a2 | 97.19 | PASS | BELOW_FLOOR (107.75) |
| w4 | train8 | int2 a2 | 91.80 | PASS | BELOW_FLOOR (107.75) |
| w1 | train128 | int2 a2 | 58.59 | FAIL | BELOW_FLOOR (88.28) |
| w1 | train8 | int2 a2 | 55.21 | PASS | BELOW_FLOOR (88.28) |
| w3 | train128 | int2 a2 | 103.97 | PASS | BELOW_FLOOR (122.63) |
| w3 | train128 | int3 a2 | 103.13 | PASS | BELOW_FLOOR (122.63) |
| w3 | train8 | int2 a2 | 106.88 | PASS | BELOW_FLOOR (122.63) |
| w3 | train8 | int3 a2 | 109.89 | PASS | BELOW_FLOOR (122.63) |

- M1 still open: the "best 2-action brain" floor (the backlog's third floor kind). Abstain
  already beats every learned cell, so it can only raise the floor; lower priority than M2.

## 2026-09-14 epoch 1, iteration 4 -- conductor confirmation, receipt, integration, M3

- A[m1-449a9e76] re-derived the abstain floor with separate code: identical (bus 1789426590314-0).
  A's rulings: round 4 clause A ON HOLD on these worlds/objective; G files the receipt and does NOT
  start M2 re-seeding until the operator rules. H's F12 will read floor rows (BELOW_FLOOR, NO_FLOOR).
- Integrated: rebased onto the integration branch (clean; suite 194 passed, 1 skipped with F/H/U/W
  work), pushed with `python -m primordial.ops.push` (F's O3) -> 5d846f9ce. ops.push rebased a second
  time, so SHAs changed twice; the pre-rebase SHAs I posted were corrected on the bus
  (1789426896669-0). My remote branch nestor/bld-g-2026-09-14 is stale (never force); the integration
  branch is the record.
- Receipt G-M1-floors-w134 PASS filed through bus.receipt (guarded: git 5d846f9ce on integration,
  rows present), bus 1789426892062-0. Not board-eligible: no cheat control was run, and none is
  claimed (controls: wforge oracle, random-action negative, independent re-derivation by A).
- M3: primordial/metric/ci.py median_ci -- percentile bootstrap, 10,000 resamples, PCG64 seed
  20260914. D3 w1 CIs pinned in test_ci.py: float [47.63, 67.81], int4 [47.77, 65.63]. Wiring it into
  `check`: `held=` (the candidate's per-run-seed values) switches the band to the CI of the candidate
  median (parity: CI high >= baseline median at fewer bytes; better: CI low > baseline median at <=
  bytes; floor: CI low <= floor -> BELOW_FLOOR). Without `held` the old IQR band runs and is labelled
  band_rule=iqr. Round 1 baselines carry no per-run values, so the CI is on the candidate side only.
- Pushed 34f00a160 (suite 206 passed, 1 skipped). CLI smoke: B's w4 train128 8 B cell with its 8 run
  values -> CI [97.00, 97.52], raw PASS vs open loop 94.04, floor BELOW_FLOOR (107.75).

## 2026-09-14 epoch 1, iteration 5 -- C1 powered brain oracle, C4 variable-length genomes

- C1: primordial/cohorts/e/oracles.py `brain_verdict(g7, g, seeds, cheat="powered")` -- the brain
  oracle a harness may use for a verdict. clean = honest 0 mismatched AND shift_action caught on every
  elite AND ablate_top caught on >= ceil(14/16 x elites) (input-invariant elites never count as caught;
  B-R2-8's rule). Any other cheat name, skip_odd included, raises ValueError. Existing harnesses still
  record E7's skip-odd as a row field; the helper is the gate for new verdicts.
- My first C1 test assumed 4 random linear elites (2 seeds, 64 rows) are all caught by ablate_top;
  they were not (the rule needs 4/4 at P=4). That was my test's premise, not a helper defect. Replaced
  with synthetic cheat counts aimed at the rule (14/16 clean, 13/16 not, honest 1 not, shift 15/16 not,
  P=4 needs 4) plus the real-path W=0 input-invariant case.
- C4: primordial/qd/archive.py `VarArchive(r, run, max_len, sampler_seed)` -- genomes of 1..max_len
  bytes; insert takes a list of bytes, sample returns bytes. The Lua compare is byte-wise via
  string.byte (never Lua `<`, which goes through strcoll), a shorter genome winning on an equal
  prefix: Python's bytes order. For equal-length multiple-of-4 genomes that equals INSERT_LUA's u32
  big-endian order, so an archive LuaArchive wrote loads under the same run key and keeps its elites.
  restore_elites handles VarArchive.
- Tests test_archive_var.py: a 5-byte genome round-trips (insert, dump, sample, save/restore);
  mixed-length ties resolve to min(bytes) in 48 arrival orders and in one batched insert; fitness
  still wins first; lengths 0 and > max raise; an old LuaArchive archive reads identically through
  VarArchive, and continuing it with VarArchive equals serial_reference over all offers.
- Pushed 370ced3cd (suite 232 passed, 1 skipped). EPOCH 1 posted (1789427350325-0).

## 2026-09-14 epoch 2, iteration 6 -- receipt mirror; M1 third floor (2-action gate)

- Found primordial/ledger/G.jsonl (bus.receipt's ledger mirror) untracked: the receipt was on the bus
  but its committed line was not. Committed and pushed 8b6751cb7.
- Gate floor = the backlog's "best 2-action brain": act with one fixed action iff obs[f] >= / < theta,
  else abstain. It is exactly an A=2 linear genome with one nonzero weight (W[f,1] = +-65535,
  b[1] = +-(32768 - theta)); test_gate.py checks the batched gate scorer against E7.rollout on that
  genome, and against const_scores at the always/never extremes. Thresholds: 16 quantiles of feature f
  under the abstain policy on TRAIN8. Search: screen every gate on TRAIN8, rescore the top 64 on the
  pressure's TRAIN, score the best on HELD64 -- best-found, not exhaustive over train128.
  Predicate 1789427594545-0 (prior: w4 gate held64 <= 112.75).
- v1 (G-M1-gate-floor-w134) was uninformative, and I say so: threshold-0 gates are always-on or
  never-on because obs are uint16. The D x 511 never-gates tied at the abstain train8 score and filled
  the whole top-64 screen, so the train128 rescore saw only abstain-equivalents and every world
  returned abstain. Amendment posted before the rerun (1789427850951-0); v1 rows stay committed.
- v2 (thr 0 dropped; G-M1-gate-floor-w134-v2), 96 s:

| world | best gate | train8 | train128 | held64 | abstain held64 | best baseline held64 |
|---|---|---|---|---|---|---|
| w4 | obs[6] < 58 -> [0,0,1] | 153.00 | 112.34 | 107.75 | 107.75 | 98.76 |
| w1 | obs[1] < 1 -> [0,4,7] | 236.25 | 271.80 | 170.47 | 88.28 | 63.94 |
| w3 | obs[1] < 1 -> [4,7] | 34.50 | 70.22 | 122.63 | 122.63 | 105.58 |

- Aimed at the claim: each selected gate as an A=2 linear genome through numpy E7.rollout AND
  FusedRollout gives identical held64 and train128 (w1 170.4688 / 271.7969); E7.world_oracle on HELD8
  0 failing episodes (wforge trace hash + charge); brain oracle 0 mismatched of 256 clear rows.
- Prior (w4 <= 112.75): TRUE. Report-only w1: a 4-byte gate that acts only when feature 1 reads 0
  scores 170.47 on held64, 2.7x the best w1 baseline and 1.9x abstain. floor_of takes the highest
  floor row, so `check` now reads w1 against 170.47.
- Still best-found: the TRAIN8 screen is tied at the abstain score in every world (screen top =
  abstain score), so the top 64 are an arbitrary slice of ties. A higher gate floor may exist; this
  one is a lower bound on the 2-action floor.
- Pushed df06f6e45; receipt G-M1-gate-floor-w134-v2 PASS (1789428113082-0), ledger mirror 179dfec6f.

## 2026-09-14 QUIESCE -- paused, then operator reboot of SKULLPORT (EPOCH 2 final)

Conductor 1789428158910-0 (pause instead of idle-polling) and 1789428959319-0 (operator-ordered
reboot quiesce). No task in hand; nothing started after the gate floor. No live RowWriter.

Carry-forward (for the next G session):
- DONE on integration: C2, C1, C4, M3 (bootstrap CI in check via held=), D-open (anomaly
  1789419655457-0 RESOLVED), M1 floors: abstain, best fixed action, random action, 2-action gate.
  Receipts: G-M1-floors-w134 PASS, G-M1-gate-floor-w134-v2 PASS.
- Floors (held64): w4 abstain 107.75 = gate (no headroom: every baseline 98.76 and all B cells below);
  w3 abstain 122.63 = gate (no headroom); w1 gate 170.47 (abstain 88.28, best baseline 63.94).
  All 28 recorded clause A cells are BELOW_FLOOR. The gate floor is best-found (TRAIN8 screen tied at
  abstain), a lower bound.
- HELD: M2 (re-seed baselines with >= 8 run seeds + information-honest nibble-packed open-loop bytes).
  Conductor: do not start until the operator rules (open decision: world screen + floor-relative
  clause A).
- Open, not assigned: why the QD archives never reach the abstain cell (A filed the anomaly).

RESUME: read this section; bus inbox; if the operator ruled for a world screen, re-run
`python -m primordial.metric.floors_run --worlds <new>` and `python -m primordial.metric.gate_run
--worlds <new>` (about 2 min per world, 4 threads), then M2 on worlds that have headroom above the
floor. Push with `python -m primordial.ops.push`; file receipts only after the push.

# Round 4 phase P0 -- Nestor-G[m1-c8188115] (claude-opus-5), METRIC builder

Brief: prompts_bld_r4/G.md; items SWARM_R4 s2 G-R4-1..5. Threads 5. M2 unheld (G-R4-3 stage 2).

## 2026-09-14 P0 epoch 1, iteration 1 -- G-R4-1 input-invariant learner; screen cost ruling

- Cost probe (w4, 5 threads): E4b open-loop QD at the E10 budget = 32 s / 40 gens -> ~320 s per run seed,
  scaling with T x S. Over w1..w5 + 32 new gen_seeds x 8 run seeds: train128 learner ~74 h, train8 ~1.2 h.
  The literal "floor suite on every candidate" in stage 1 is not cheap.
- Posted (1789433793789-0); A APPROVED as scheduling (1789433825087-0): cheap parts + gate + M2 baseline on
  every candidate; the train128 learner only on cells whose verdict it can change under any Q1/Q2 variant.
  A's correction: a pressure's bound uses only its own parts (the train8 learner never enters train128).
  Before the rest of the train128 batch: post cell count, hours, burst plan; run if <= 8 h, else wait.
- Schema: accepted H's worlds_r4/v1 + A's per-variant verdicts, plus floor_is_bound, bound_parts, learner
  status (1789433928197-0). Bootstrap = M3's median_ci (PCG64 seed 20260914).
- G-R4-1: primordial/metric/invariant.py. E4b MAP-Elites exactly (init/mutate/descriptor, NbEncounter
  fitness) with a SEEDED sampler (C2) and elites saved per run seed; budgets train8 100x256 (E6 open),
  train128 400x256 (E10 open), asserted against the committed rows; per run seed = top-16 by train, per-seed
  mean on HELD64 (round 1's open score); floor part = median over >= 8 run seeds. F9: pause polled every 10
  gens, archive kept in Redis, RNG states checkpointed. Worker job `invariant:job` emits a run row per run
  seed (oracle on run seed 0: wforge hash+charge, nb == np) and one floor_invariant row per cell.
- Tests test_invariant.py (7): budget from rows; nb_fit == E4b == numpy; wforge oracle 0 failing; replay
  byte-identical elites; pause/resume == uninterrupted; job pause/resume rows == uninterrupted; median rule.
- Suite 345 passed, 9 skipped (rc 0). Pushed 187b4b471.
- Next: G-R4-2 floor suite (cheap parts + gate + train8 learner) per world x pressure, via the F7 worker.

## 2026-09-14 P0 epoch 1, iteration 2 -- F7 worker idle death fixed; G-R4-2 floor suite

- My F7 worker died idle within seconds: redis TimeoutError in serve's XREADGROUP. This venv's redis-py 8.1
  defaults socket_timeout to 5 s, equal to block_ms=5000. Fix: worker._redis socket_timeout=30
  (SOCKET_TIMEOUT_S) + test_f7_worker_timeout.py (a 5.5 s idle blocking read). F7/F9/F14 tests 8 passed.
  Pushed 519d081c8; A accepted it as a shared-library change (1789434198534-0) and added "worker idle > 60 s
  still alive" to the launch check. Also seen: host "localhost" costs a 5 s first connect; use 127.0.0.1.
- G-R4-2: primordial/metric/suite.py. floor_of_parts = max over the parts run (ties -> PARTS order);
  learner missing -> floor_is_bound true, bound_parts names the parts. Parts are the pressure's own
  (best_constant and gate selected on its TRAIN; train8 learner never in a train128 bound). The gate is a
  column only. cheap_parts reuses M1's floors/gate code; job emits suite_cheap rows, learner run rows
  (invariant.learner_cell, factored out of invariant.job), and one floor_suite row per pressure.
- Tests test_suite.py (5): max/bound/gate-column logic; w3 cheap parts == committed G-M1 floor cells
  (abstain, best_fixed, random, gate v2) to 4 dp; job learner only on train8, train128 a bound without the
  learner, pause/resume rows == uninterrupted.
- Full suite: first run 1 failed (test_f14_epoch: RowWriter.close relative_to on a \\?\ long path killed a
  worker thread), passes 3/3 alone; rerun 354 passed, 9 skipped, rc 0. Committed only on the green rc.
  Flake reported to A,F (1789434512258-0). Pushed fc1ebf81c.
- Next: G-R4-3 stage 1 on 37 candidates (w1..w5 + gen_seeds 6..37) through the worker; predicate posted first.

## 2026-09-14 P0 epoch 2, iteration 3 -- stage 1 running; stage 2, screen, worlds_r4, r4 check, draw built

- Stage 1 (predicate 1789434570568-0) submitted as 8 jobs to my worker. First push gap used the F14 stop
  flag: job 1 paused at an F9 checkpoint in 4 s, ops.push rebased with no live writer (bc7d66b37), flag
  cleared, worker resumed. The paused segment requeues at the end of the queue (w2/w5 finish last).
- Monitor false alarm WORKER_GONE: pm:worker:G has TTL 30 s and is refreshed only between jobs, so a
  busy worker looks dead 30 s into a job (supervisor pid 15368 and child alive, rows growing). Reported
  (1789434887289-0); A patches run_job; I check the process, not the key.
- Stage 1 so far (9 worlds): cheap parts + gate for w4/w1 MATCH the committed G-M1 cells to 4 dp; learner
  oracles clean (wforge 0 failing, nb == np) on every run seed 0. Abstain is the floor in every cell; the
  train8 learner is below abstain everywhere (w4 88.59 vs 107.75, w1 42.69 vs 88.28, w6 190.16 vs 229.53).
  The gate column is below abstain in several worlds (w8 62.44 vs 70.44; w10 train8 0.00): a gate is
  selected on TRAIN over non-abstain actions and can generalise worse; under gate_in it cannot lower the
  floor. w7 gate 1482.50 vs abstain 189.19 (7.8x).
- M2 stage 2 code: primordial/metric/baseline.py (E9 200x128 / E10 800x128, seeded sampler, elites per run
  seed, top-16 fused held64, M3 CI, bytes = G7 linear glen). 6 tests.
- OPERATOR RULED (message 13 via A 1789434918331-0): Q1 GATE IN, Q2 HOLD -> active gate_in|HOLD.
  My screen draft was WRONG for gate_in|HOLD: HELD compared the gate with the variant floor, which under
  gate_in contains the gate, so HELD could never occur. Fixed to A's text before any verdict was written
  (1789435058202-0): HELD iff gate > four-policy floor and CI low <= variant floor.
- screen.py: four variants, strict survival, needs_learner = CI low > bound or gate > bound (brute-force
  test: verdicts from a bound equal those from every true floor >= bound when false), gate-headroom order,
  per-variant NOT_REACHED after 8 survivors. worlds.py (G-R4-4): records from rows only, PENDING_LEARNER
  blocks write, guard -> INELIGIBLE UNSCREENED|CULLED|HELD. qd_ledger.check_r4 (G-R4-5): progress above
  floor, PASS iff >= 0.95 and fewer bytes, BELOW_FLOOR iff < 0; check() attaches it as clause_a_r4 for F12
  (H ask 1789435262391-0); CLI check defaults to r4. draw_cell: graphworld worlds only from survivors.
- Tests green (pytest rc 0 each): screen 5, qd_ledger r4 + draw + floor + ci 32. Commits local, pushing at
  the next worker gap with the full suite.
- Pushed acfa9dd78 through a second stop-flag gap (full suite 378 passed, rc 0); it carries A's F14 fix.

## 2026-09-14 P0 epoch 3, iteration 4 -- stage 1 DONE (74/74), table to A, receipt; stage 2 submitted

- Stage 1 finished: 8 jobs + 2 resumed segments, 444 rows, 0 aborted/timeout, 296 learner runs at budget,
  learner oracle clean on run seed 0 of all 37 train8 cells. Void condition not triggered: w1/w3/w4
  abstain, best_constant, random and gate == committed G-M1 cells to 4 dp.
- Table: SCREEN_R4_STAGE1_2026-09-14.md (pushed e365d4fa3, suite 393 passed rc 0). Abstain is the floor in
  all 74 cells; train8 learner <= max(abstain, best_constant) in 37/37 (prior TRUE); w4 learner 88.59 vs
  E6 87.32 (TRUE). gate > four-policy floor in 10 cells (w7 both +1293.31, w26 t128 +96.84, w1 both
  +82.19, w34 t128 +63.19 / t8 +16.00, w10 t128 +11.98, w13 both +7.47). Degenerate: w19, w24, w25 (0 everywhere).
- Posted table + stage 2 plan to A,H (1789436794057-0). Receipt G-R4-3-stage1 PASS (1789436817120-0),
  ledger mirror pushed b2bcb165d.
- Stage 2 driver primordial/metric/stage2.py (4d5f7ed71): baselines in gate-headroom order, train128
  learner only for A-cleared gen_seeds (else PENDING, reported), stop at 8 exact survivors under
  gate_in|HOLD; baseline_cell factored out. Tests 3 + baseline 6, rc 0. Cost probe: w4 train128 baseline
  ~21 s per run seed at 2 threads -> all 74 cells ~4.8 h at 2 threads.
- Predicate G-R4-3-stage2 posted before the run (1789436803186-0); prior: no survivor on w1/w3/w4.
- Restarted the idle worker (fresh modules, A's worker fixes), burst announced, submitted job 5af1dacd7c5d
  (ttl_cpu_s 120000, learner_train128 [1,3,4]). Monitor watches job ends, stage2_cell rows, worker death.

## 2026-09-14 P0 epoch 4, iteration 5 -- stage 2 verdicts; first survivor candidate w13 t128; PENDING ruling

- Stage 2 cells so far, gate_in|HOLD (exact unless marked):
  HELD: w7 t8 (CI [153.67, 192.57] vs gate 1482.50), w1 t8 (CI [32.13, 47.99]), w1 t128 (cleared learner ran,
  below abstain, floor 88.28 exact; CI [55.36, 71.65]), w34 t8, w13 t8 (CI [144.25, 154.79] vs floor 159.00).
  CULLED: w2 t8, w2 t128, w3 t8, w3 t128, w4 t8 (prior "no survivor on w1/w3/w4" holding).
  PENDING non-survivable (CI low <= bound, gate > bound): w7, w26, w34, w10 t128.
  PENDING survivable: w13 t128 -- CI [173.41, 188.11] above gate 166.47 and bound 159.00; SURVIVES iff the
  train128 learner median < 173.41 (train8 learner 147.97).
- Posted the pending list + hours (1789440078650-0). A (1789440120713-0, operator asleep, standing order 14):
  w13 t128 learner cleared as the next job; standing clearance for survivor-deciding learners <= 1 h;
  non-survivable cells are written as PENDING (INELIGIBLE(PENDING) in check/F12), their learners run after
  test launch 1 quiesces. Acked with exact strings (1789440338587-0).
- Predicate G-R4-3-stage2-learner posted (1789440353405-0). Queued the w13 learner job 34bcd7c509e6 behind
  the running stage 2 job, set the stop flag: stage 2 paused at its F9 checkpoint in 2 s and requeued
  behind w13. Pushed the local commits in that gap (036a80333, suite 396 passed rc 0), cleared the flag;
  the worker took the w13 learner next.
- Code (f8607f25f, tests 35 rc 0): status string PENDING; survivable pending blocks worlds.write,
  non-survivable pending is written (HOLD variants PENDING, CULL variants CULLED with cull_reason PENDING,
  learner not_run + est_hours + reason); guard and clause_a_r4 give INELIGIBLE(PENDING);
  invariant.est_hours; screen_run reads cleared learner rows from G-R4-3-stage2-learner.jsonl.
- Dry run on real rows (15 stage 2 cells): blocking = w13 t128 only (0.36 h); non-survivable = w7 (2.84 h),
  w26 (0.71 h), w34 (2.84 h), w10 (1.42 h). The running child still has the old modules loaded, so its
  stage2_cell rows say PENDING_LEARNER; worlds_r4.json is rebuilt from baseline/floor/learner rows, never
  from that string.

## 2026-09-15 P0 final, iteration 6 -- stage 2 DONE; worlds_r4.json written, audited, pushed; G P0 DONE

- Stage 2 finished (job 5af1dacd7c5d in 3 segments + w13 learner 34bcd7c509e6): 74/74 cells, 749 stage 2
  rows (last rows commit da8c5312a), 0 aborted. No cell NOT_REACHED (1 survivor < 8).
- A (1789442653996-0): no 4-epoch cap in round 4 P0; operator asleep, standing order to launch when G and H
  are ready. H found 2 small defects (PENDING screen label, PENDING_LEARNER string) -- both already fixed
  locally; pushed through a stop-flag gap (1f3c550d3, suite 397 rc 0).
- worlds_r4.json (primordial.metric.screen_run --write --commit da8c5312a), active gate_in|HOLD:
  SURVIVED 1: w13 train128 (floor 159.00 abstain exact after learner 151.41; gate 166.47; baseline median
  182.72, CI [173.41, 188.11], 200 bytes). HELD 5: w7 t8, w1 t8, w1 t128, w34 t8, w13 t8. PENDING 4
  (non-survivable, learners deferred, ~7.81 h): w7 t128 2.84, w26 t128 0.71, w34 t128 2.84, w10 t128 1.42.
  CULLED 64 (incl. degenerate w19/w24/w25). Notable: w28 t128 baseline == abstain exactly (170.88) -> tie
  culled; w30 t128 CI high == floor 660.19.
- Independent audit (scratchpad script, recomputes medians + bootstrap CIs from raw run rows and the four
  variant rules without screen/worlds code): 74/74 cells, 0 problems. Live checks: guard w13 t128 None,
  w1 t8 HELD, w7 t128 PENDING, w99 UNSCREENED; draw_cell survivors ['w13']; check_r4 w13 t128 at the
  baseline median with 199 bytes -> PASS.
- Pushed ee86620f4 (suite 408 passed, 9 skipped, rc 0); sha256 f007f4e23d356a202cf5097bd2bdda139893b6a56e5769511cb8563eaac6d4e4
  identical on integration. Receipts PASS: G-R4-3-stage2 (1789447347341-0), G-R4-4-worlds-r4
  (1789447348162-0), G-R4-5-clause-a-progress (1789447348881-0); ledger mirror 45c46442f.
- G-R4-1..5 green. G P0 DONE posted to A.

RESUME (after test launch 1 quiesces, per A): submit primordial.metric.invariant:job for [[7,"train128_held64"],
[26,"train128_held64"],[34,"train128_held64"],[10,"train128_held64"]] (rows G-R4-3-stage2-learner.jsonl,
predicate first, burst ~7.8 h at 5 threads, or ask A for the order), then
`python -m primordial.metric.screen_run --write --commit <rows sha>`, rerun the scratchpad-style raw-row audit,
full suite, push, receipt, and tell H to re-replay. Push under a live RowWriter only through a stop-flag gap.

## 2026-09-15 R16 (operator 16) smoke test, stopped by operator 18 -- CHECKPOINT

- Operator 16 via A: every baseline and stochastic floor part at 32 runs x 4 RNG families (4200, 2101, 3303,
  5501), read top1_train, worlds_r4/v2. Plan posted 1789455371443-0; A cleared phase 1 (1789455401413-0).
- Code: family-aware runs (D-R4-2 convention; family 4200 == the v1 M2 stream, v1 rows reproduce) and pooled
  32x4 summaries refusing < 32 runs / < 4 families / < 8 per family / duplicate ids / mixed readouts (205dedfed);
  r16.py jobs; worlds_r4/v2 assembly with families, n_per_family, n_runs, floor_stats, no stop, write refuses
  < 32x4x8 (bd70319bb). E's BASELINE_N judge reads those names. Full suite 470 passed rc 0 at the rebased tip.
- Ran: J1 floors (w13 complete: det parts == stage 1; random pooled 58.07; train8 learner pooled 151.27 top1),
  J2 baselines (6 cells: w13 t128 183.91 [170.95, 188.56]; w7 t8 189.19 [160.50, 189.19]; w7 t128 188.67
  [184.62, 189.19]; w26 t128 197.83 [192.22, 201.73]; w1 t8 67.15 [52.69, 74.68]; w1 t128 75.40 [65.23, 78.78]).
- Cross-checks on w13 t128: family 4200 top1 == E-R15-1 committed 8/8 (median 189.53); legacy top-16 == D-R4-2
  32/32 exactly; top1 == D held64_elite[0] within D's 4 dp. My quoted D CI [171.02] was MY ordering artifact:
  M3 median_ci is not permutation invariant; the stamped order (family 4200, 2101, 3303, 5501, then run seed)
  gives [170.95] (1789456804803-0).
- The push gap requeued J1's remainder behind J2/J3 (reported to A 1789456288436-0; no values change).
- Operator 18 via A: stop at a checkpoint (smoke test). Stop flag -> J2 paused in 2 s; J1 remainder + J2 parked
  (removed from pm:jobs:G, exact entries in R16_CHECKPOINT_2026-09-15.json, 419da07a9); only J3 ran.
- J3 w13 train128 learner 32x4 (rows 1817bed46): median 151.75, CI [151.44, 151.91], IQR 0.98 (legacy top-16
  151.64); oracle clean; 6,049 s wall (~189 s/run; plan said 1.42 h). VERDICT w13 train128 under gate_in|HOLD:
  floor = max(159.00, 159.00, 58.07, 151.75, gate 166.47) = 166.47 < ci95[0] 170.95 -> SURVIVED (every variant).
- Measured walls (5 threads): J1 seg0 362 s, J2 seg0 2,303 s, J3 6,049 s. Projection for the full phase 1:
  baselines ~7.2 h, train8 learner ~2.5 h (plan 1.75), plus overhead and survivor-deciding train128 learners.
- A process note: my first attempt at the checkpoint chain died on a bash quoting error before running anything
  (nested heredoc + Python in one -c string); state was verified clean before retrying with a script file.
- No worlds_r4/v2 written (partial screen). No B2. Paused. Resume steps: G R16 CHECKPOINT post + the resume record.

## 2026-09-15 R5 P-BUILD (SMOKE stage, hard cap 2 h: 06:12:59 -> 08:12:59 local)

Brief prompts_bld_r5/G.md; SWARM_R5 s3 G-R5-1..4 with overrides O2, O4; prompt 19 s2, s3, s7, s8 read. R16 stays parked.
- Coordination before coding: G's names posted to H/F/A (1789467274589-0): runs_total, rng_family_count,
  runs_per_family top-level; CANDIDATE_N payload + judge order. A (1789467299042-0): no second list spelling --
  ONE list 'families' + ONE map 'n_per_family'. A (1789467765694-0): no red tip -- H pushes its 5 judge-vs-F12
  fixture updates first, then G's CANDIDATE_N. F asked for the O3 probe workload; sized (w13 train128, gens
  ~6400 x batch 128 ~30 s at 5 threads, distinct run keys per concurrent copy). A (1789468003264-0) fixed the B2
  pilot sample before data: first 4 specs above E's validation range, families 4200 + 2101, train128_held64,
  R16 floor paths incl. the gate; over PILOT ceilings -> PRODUCTION_CANDIDATE, never trimmed.
- G-R5-4 w13 eligibility lookup: primordial/metric/eligibility.py -- r16_doc(cells) builds an in-memory
  worlds_r4/v2-shaped doc from committed R16 rows (complete cells only; w13 train128_held64 today), never writes
  worlds_r4.json; check(..., doc=r16_doc()) judges w13 alone, other cells UNSCREENED. Pushed 1791a6655 (suite 489
  passed rc 0); B told (1789467520528-0).
- G-R5-2 CANDIDATE_N: check_r4/check/CLI take runs_total, rng_family_count, runs_per_family, n_per_family; refusal
  why CANDIDATE_N with candidate_* / need_* payload; order screen -> BASELINE_N -> CANDIDATE_N -> READOUT_MISMATCH ->
  oracles/cheats -> progress; old runs < 8 removed. 13 tests went red on first run (8 my fixtures, 5 H's); my
  fixtures moved to the explicit sample (41 calls), test_candidate_n.py added. Committed locally, held for H.
- G-R5-1 seed schema: primordial/metric/sample.py (stamp, invariant, meets/refusal, N x M run-count lint) +
  suite lint over receipts since the round 5 start and R5 tables. Committed locally.
- G-R5-3 B2 admission rule: primordial/metric/b2_screen.py -- four verdicts in fixed precedence, never SURVIVED,
  pilot-sample + readout checks, gate_in floor, full_screen_cost / pilot_cost. Committed locally. B2 episode wall
  measured timing-only (no scores read): ~1.6 ms per reference episode (planted spec, 64 ticks).
- A (1789468233897-0) relabelled the B2 outcome: B2's instrument is valid (E-R15-2 oracles pass), only slow.
  INSTRUMENT_FAIL now only when an oracle RAN and FAILED; a spec not run on stage budget ->
  B2_SCREEN_INDETERMINATE(NOT_RUN_STAGE_BUDGET) with the PRODUCTION_CANDIDATE id; oracles not run -> INDETERMINATE.
  PRODUCTION_CANDIDATE filed on pm:production_candidates 1789468339986-0: B2 batched/compiled rollout (owner E,
  a later round), measured cost attached (pilot ~746 h single worker; full screen ~1,491 h).
- G-R5-1 finished: producers (pooled baselines, pooled learner, R16 floor_stats, worlds cells, eligibility) stamp
  runs_total / rng_family_count / runs_per_family; test checks the invariant on each.
- Push: H pushed its 5 real-judge fixture updates + F12 CANDIDATE_N mirror first (e3412c04b), per A's no-red-tip
  order. G rebased its stack onto it, full suite 618 passed rc 0, pushed; ops.push re-rebased over 12 concurrent
  commits, so G re-ran the full suite on the actual tip bf88d7387: 658 passed, 9 skipped, pytest rc 0. Posted and
  corrected on the bus (the first rc was on the pre-push tree).
- ROUND 5 P-BUILD G: G-R5-1..4 all green on integration at 06:39 (cap 08:12:59). R16 re-screen stays parked.
