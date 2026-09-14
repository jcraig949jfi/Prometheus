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
