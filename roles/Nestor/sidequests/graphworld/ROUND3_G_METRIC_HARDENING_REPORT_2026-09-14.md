# Round 3 builder G -- metric hardening report

Currency: 2026-09-14, Nestor-G[m1-c77819fe] (claude-opus-5), lane G, worktree
F:/Prometheus-worktrees/nestor-bld-g. Brief: DELEGATION_BRIEFS_R3_R6.md s0 and sG; items from
ROUND3_BACKLOG_2026-09-14.md s2. Record of work: journal/G.md. Everything below is on the integration
branch nestor/sidequest-graphworld-2026-09-14 (last G commit adfdd0f6a). The session paused for the
operator-ordered reboot of SKULLPORT.

## 1. Headline

The held64 metric that clause A was judged on has a trivial-policy floor above every baseline.

- A zero-byte always-abstain policy beats every held64 baseline on w1, w3 and w4, and every round 2
  clause A candidate. It also beats the committed elites on the TRAIN seeds, so the QD runs never
  reached the do-nothing policy.
- On w1, a 4-byte two-action gate (act only when observation feature 1 reads 0) scores 170.47 held64:
  1.9x abstain and 2.7x the best w1 baseline.
- Read against the floor, all 28 recorded clause A cells (w1, w3, w4) are BELOW_FLOOR, including all
  8 of B's 8-byte cells.
- The conductor re-derived the abstain floor with separate code and got identical numbers
  (bus 1789426590314-0). It put round 4 clause A on hold on these worlds and objective, and held M2.

## 2. Package status

| id | item | status | where |
|---|---|---|---|
| C2 | sampler_seed mandatory; elites saved per run seed | DONE | primordial/qd/archive.py |
| M1 | trivial-policy floors + floor-aware `check` | DONE | primordial/metric/floors.py, floors_run.py, gate_run.py; primordial/ops/qd_ledger.py |
| D-open | easy-metric discriminator (anomaly 1789419655457-0) | DONE, RESOLVED | as M1 |
| M3 | bootstrap CI of the median in `check` | DONE | primordial/metric/ci.py; qd_ledger.check(held=) |
| C1 | powered brain cheats as THE brain oracle; skip-odd raises | DONE | primordial/cohorts/e/oracles.py brain_verdict |
| C4 | variable-length genomes in the archive | DONE | primordial/qd/archive.py VarArchive |
| M2 | re-seed baselines (>= 8 run seeds) + honest open-loop bytes | HELD by conductor pending operator | not started |

Tests: 268 passed, 1 skipped on the full suite at df06f6e45. Receipts: G-M1-floors-w134 PASS
(bus 1789426892062-0), G-M1-gate-floor-w134-v2 PASS (bus 1789428113082-0); both mirrored in
primordial/ledger/G.jsonl.

## 3. Floors (held64 per seed, E6 HELD64 = seeds 30000..30063)

| world | abstain | best fixed action (on TRAIN) | random action (median of 8) | best 2-action gate | best baseline |
|---|---|---|---|---|---|
| w4 | 107.75 | abstain | 11.49 | 107.75 (= abstain) | 98.76 |
| w1 | 88.28 | abstain | 0.00 | **170.47** (obs[1] < 1 -> [0,4,7]) | 63.94 |
| w3 | 122.63 | abstain | 0.89 | 122.63 (= abstain) | 105.58 |

Abstain on TRAIN versus the committed elites: w4 train8 153 vs E9 about 145; w4 train128 112.4 vs B
about 105.5; w1 train8 236 vs at most 167; w3 train8 34.5 vs at most 31.

Definitions:
- abstain: every slot abstains every tick.
- best fixed action: one action vector on every slot every tick, exhaustive over 8^W (the world reads
  action % 8), selected on the pressure's TRAIN seeds, scored on HELD64.
- random action: uniform per slot per tick, 8 seeded policies.
- 2-action gate: act with one fixed action iff obs[f] >= theta (or < theta), else abstain. It is
  exactly an A=2 linear genome with one nonzero weight. Thresholds are 16 quantiles of feature f seen
  by the abstain policy on TRAIN8. Search: screen every gate on TRAIN8, rescore the top 64 on the
  pressure's TRAIN, score the best on HELD64.

How the numbers were checked:
- The batched constant scorer equals wforge replay (test_floors.py).
- An all-abstain genome through numpy E7.rollout and FusedRollout (the scorers the baselines used)
  gives the same floors.
- The gate scorer equals E7.rollout on the equivalent A=2 linear genome (test_gate.py).
- Each selected gate: numpy equals fused on HELD64 and TRAIN128; E7.world_oracle on HELD8 has
  0 failing episodes; the brain oracle has 0 mismatched of 256 clear rows.
- The conductor's independent re-derivation of abstain matches.

Limits:
- The gate floor is best-found, not exhaustive over train128. The TRAIN8 screen was tied at the
  abstain score in every world, so the top 64 were an arbitrary slice of ties. 170.47 is a lower bound
  on the w1 two-action floor.
- The first gate run (G-M1-gate-floor-w134) was uninformative. Threshold-0 gates always or never fire
  (observations are uint16), and the never-firing ones filled the top-64 screen, so it returned
  abstain everywhere. The fix was posted before the rerun (bus 1789427850951-0). v1 rows stay
  committed.

Rows: primordial/ledger/rows/G/G-M1-floors-w134.jsonl, G-M1-gate-floor-w134.jsonl (v1),
G-M1-gate-floor-w134-v2.jsonl. Floor cells (status control, `floor` = abstain / best_fixed /
random_action / gate) are in primordial/ledger/qd/cells.jsonl.

## 4. What changed in shared code

`qd_ledger check`:
- Keeps the raw clause A verdict and adds `floor` = {verdict, floor_held64, floor_kind, normalized}.
- `floor_of` takes the highest floor row for the world and pressure.
- It adds no new threshold. BELOW_FLOOR if the candidate's lower band <= floor. NO_HEADROOM if every
  front baseline is <= floor. INELIGIBLE and NO_BASELINE pass through. Otherwise the raw verdict.
- With `held=` (the candidate's per-run-seed values, CLI `--held`), the band is the bootstrap 95% CI
  of the median (10,000 resamples, seed 20260914). Parity: CI high >= baseline median at fewer bytes.
  Better: CI low > baseline median at <= bytes. Without `held=`, the old 0.5 x IQR band runs and is
  labelled `band_rule: iqr`.
- Round 1 baselines carry no per-run values, so the CI is on the candidate side only.
- D3 w1 regression pinned: float [47.63, 67.81], int4 [47.77, 65.63].

Archive (C2):
- LuaArchive, RacyArchive and E2's LineageArchive need `sampler_seed`. Omitting it is a TypeError;
  None, or a string other than UNSEEDED, is a ValueError.
- 19 frozen pre-C2 harnesses pass `archive.UNSEEDED` explicitly: same behaviour, `replayable=False`.
- `save_elites` / `load_elites` / `restore_elites` write one canonical JSON per run seed. Same seeds
  give a byte-identical file.

C1:
- `oracles.brain_verdict(g7, g, seeds)` is clean only if honest has 0 mismatched rows, shift_action
  catches every elite, and ablate_top catches >= ceil(14/16 of elites). Input-invariant elites never
  count as caught.
- Any cheat other than `powered` raises.

C4:
- `archive.VarArchive(r, run, max_len, sampler_seed)` holds 1..max_len-byte genomes.
- The Lua compare is byte-wise; a shorter genome wins on an equal prefix. For equal-length
  multiple-of-4 genomes that is the old u32 order, so archives written by LuaArchive load and keep
  their elites.

## 5. Process notes

- My first pushes went to my own branch, not integration, and the receipt guard needs integration.
  I rebased and pushed with `python -m primordial.ops.push`. SHAs changed twice; I posted a
  correction (bus 1789426896669-0). The remote branch nestor/bld-g-2026-09-14 is stale (never force);
  integration is the record.
- `bus.receipt` writes primordial/ledger/G.jsonl but does not commit it. The first receipt's mirror
  sat untracked until iteration 6. Commit the mirror right after filing.
- My first C1 test assumed 4 random elites are all caught by ablate_top on 2 seeds; they were not. I
  replaced it with tests aimed at the rule itself plus the real input-invariant case.

## 6. Open and resume

- M2 is held until the operator rules on the world screen and floor-relative clause A.
- Not assigned: why the QD archives never reach the abstain cell (the conductor filed the anomaly).
- Resume (also in journal/G.md, QUIESCE section): read the inbox. If the operator rules for a world
  screen, run `python -m primordial.metric.floors_run --worlds <list>` and
  `python -m primordial.metric.gate_run --worlds <list>` (about 2 min per world on 4 threads). Then do
  M2 on worlds with headroom above the floor. Push with ops.push; file receipts only after the push,
  and commit the ledger mirror.
