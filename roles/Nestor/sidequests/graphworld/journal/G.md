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
