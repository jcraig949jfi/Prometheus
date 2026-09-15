# THE PRIMORDIAL MACHINE -- round 4: SCREENED WORLDS, FLOOR-RELATIVE CLAUSE A

Currency: 2026-09-14, Nestor-A[m1-449a9e76] (conductor). Supersedes SWARM_R2.md
for round 4; SWARM_R2.md stays the round 2 record, and its rules (s4) carry
over except where this file changes them.

Authority, verbatim in roles/Nestor/prompts/2026-09-14_graphworld_swarm/:
04 (contract, epoch/TTL), 07 (cohorts, clause A), and 12 (world screen,
35/25/25/15 split, trivial policy suite, normalized clause A). The contract
roles/Nestor/PROMETHEUS_SUCCESS_CONTRACT.md is never edited by agents.

## 0. What changed from round 2

- Worlds are SCREENED before any cohort sees them (s3). A world where the
  float linear baseline does not definitively beat the trivial floor is
  culled from every cohort's grid. Round 3 evidence: abstain beats every
  baseline on w1, w3 and w4 (G report, s3).
- Clause A is scored as PROGRESS ABOVE FLOOR (s4), replacing
  median >= baseline - 0.5 x IQR.
- Split 35/25/25/15: D gains 5 points from B (message 12).
- Every cohort experiment runs as a job on its F7 warm worker, so budget
  enforcement (F13) meters real CPU. Epochs are closed by the F14 epoch
  controller, long jobs checkpoint (F9), and sessions boot from the F15 boot
  pack.
- Round 4 has two phases. P0 (builders G and H, pre-launch) produces the
  screened world list and the new scoring. P1 is the cohort launch, and it
  waits for the P0 launch gate (s2).

## 1. Cohorts

    lane  cohort               share  cores  GPU        reads first
    ----  -------------------  -----  -----  ---------  -----------------------------------
    B     HILL CLIMBERS          35%      4  lease      qd_ledger pareto on SCREENED worlds
    C     ANTI-PRIOR             25%      3  lease      draw_cell (screened grid)
    D     ANOMALY HUNTERS        25%      3  lease      bus anomaly list --status OPEN
    E     WATCHMAKERS            15%      2  lease      bus inbox (asks for tools)
    A     conductor (logistics)   --     --  --         liveness, integration, asks

12 threads in total, as in round 2. The GPU goes through the O5 lease
(`bus lease take` / `bus.gpu_lease`) for everyone; there is no default
holder.

## 2. Phase P0 (pre-launch builders) and the launch gate

G (metric), worktree nestor-bld-g:
- G-R4-1 INPUT-INVARIANT LEARNER floor. The E4 open-loop action tensor
  (T x S x W actions, observations never read) is evolved on the pressure's
  TRAIN seeds at the round 1 baseline's budget, over >= 8 run seeds, and
  scored on HELD64. The floor value is the median over run seeds. It is the
  class that B's 8-byte int2 brains fell into.
- G-R4-2 FLOOR SUITE per world x pressure: floor = max(abstain, best
  constant action, uniform random median, input-invariant learner). The
  2-action gate (M1) is computed and reported beside it as `gate_held64`.
  See s7 Q1 for whether it belongs in the floor.
- G-R4-3 CANDIDATE BATCH AND SCREEN (AOT):
  - Candidates are the existing graphworld worlds w1..w5 plus new gen_seeds
    (batch of 32 via E4.Spec, excluding any gen_seed used as a TRAIN or
    HELD seed).
  - Stage 1 (cheap): the floor suite on every candidate.
  - Stage 2 (M2): re-seed the float linear baseline, >= 8 run seeds at the
    round 1 budget, with elites saved (C2), on every stage-1 candidate.
    Order them by gate headroom (gate - floor), and stop at 8 survivors or
    at the batch end.
  - A world SURVIVES iff the bootstrap 95% CI low of the baseline median
    (M3) is > floor, on the pressure scored.
- G-R4-4 SCREEN LIST AND JIT GUARD:
  - Write primordial/ledger/qd/worlds_r4.json: per world x pressure, floor
    parts, floor, gate_held64, baseline median/CI/bytes, verdict
    SURVIVED|CULLED, and the exp/rows that produced it. Commit it with the
    floor and baseline rows.
  - `qd_ledger check` returns INELIGIBLE(UNSCREENED|CULLED) for any other
    world, from the file and without recomputing (JIT lookup guard).
    `draw_cell` draws graphworld worlds only from the survivors.
- G-R4-5 clause A scoring per s4 in `qd_ledger check`, with tests: planted
  candidates at progress 0.94 / 0.95 / -0.01, a bytes tie, and a world not
  on the list.

H (measurement), worktree nestor-bld-h:
- H-R4-1 budget.py: round-versioned shares (SHARES_R2 = 40/25/20/15 keeps
  replay-round2 exact; SHARES_R4 = 35/25/25/15 is the default for `report`).
- H-R4-2 F12 scorer reads worlds_r4.json and the s4 verdict. It never
  re-derives floors, and never scores a CULLED or UNSCREENED world.
- H-R4-3 replay G's screen from committed rows (independent check): every
  SURVIVED/CULLED verdict recomputed from rows, 0 mismatches.

LAUNCH GATE (conductor checks; all must hold before any cohort launches):
1. worlds_r4.json on the integration branch with >= 1 SURVIVED world x
   pressure, and H-R4-3 replay 0 mismatches.
2. Suite green on the integration tip (rc of pytest itself).
3. budget report defaults to SHARES_R4.
4. Operator answers to s7 Q1-Q2, or an explicit "launch on defaults".
5. Worktrees nestor-r4-{b,c,d,e} verified (prepare_worktrees --round r4) and
   fast-forwarded to the gate tip. The tip must contain 519d081c8 (the F7
   worker socket_timeout fix), 7fa40eec9 (the rows commit fix for Windows
   long paths; a failed commit no longer kills the worker) and 54c2d95fc
   (pm:worker refreshed during long jobs).
6. Worker smoke check in one cohort worktree at the gate tip: a worker left
   idle for more than 60 s is still alive (pm:worker:<L> present). Before
   519d081c8, redis-py 8's 5 s default socket_timeout killed idle workers.

If no world survives, round 4 does not launch. The conductor reports the
screen table to the operator.

## 3. The world screen (definitions)

- HELD64 = seeds 30000..30063. TRAIN8/TRAIN128 = 9100.. (floors.py).
  Scores are per-seed means of summed clipped final charge.
- Trivial suite (message 12, exact): abstain; best constant action
  (exhaustive over 8^W, selected on TRAIN); uniform random (median of 8
  policy seeds); input-invariant learner (G-R4-1).
- "Definitively beats" = the bootstrap 95% CI low of the float linear
  baseline median is > floor (M3's CI, 10,000 resamples). No new threshold
  is introduced; the operator may substitute another.
- Timing: AOT screen before launch (G-R4-3), plus a JIT lookup guard in
  check/draw_cell (G-R4-4). Recomputing the suite inside the harness on
  every cell was the other option in message 12; it is not built this round.
- Culled means removed from every cohort grid for round 4. Its rows stay
  committed: the failure landscape is kept.
- Non-graphworld domains in the draw grid (graphworld_b2, signal_world_d1,
  nk_stub) have no floor suite yet. C may draw them as landscape rows; no
  clause A claim may be made on them.

## 4. Contract clause A: the round 4 binding

For a candidate on a SURVIVED world x pressure, with baseline = the M2
float linear baseline on that cell:

    progress = (median_candidate - floor) / (median_baseline - floor)

- The denominator is > 0 by construction (the screen).
- median_candidate is over >= 8 run seeds on HELD64. Its bootstrap CI is
  mapped through the same formula and reported, not judged.
- PASS iff progress >= 0.95 AND bytes < baseline bytes (packed genome,
  codebook included).
- BELOW_FLOOR iff progress < 0. FAIL otherwise. INELIGIBLE if an oracle is
  unclean, a cheat control does not fail, or the world is UNSCREENED or
  CULLED.
- Oracles and cheats, >= 8 run seeds, rows at every status, and Holm across
  worlds for multi-world claims are all as in SWARM_R2 s2.
- `qd_ledger check` is the only judge. No cohort scores itself.

## 5. Cohort charters (deltas from SWARM_R2 s3)

- B (35%): only SURVIVED world x pressure cells. First item: the smallest-
  bytes cell at progress >= 0.95 on the best-headroom survivor. Report the
  progress CI. Input-invariant genomes are expected to land BELOW_FLOOR or
  near 0; that is the point.
- C (25%): unchanged. `draw_cell` now draws graphworld worlds only from the
  survivors. Priors are posted before every run.
- D (25%): first claims, in order:
  (1) why the QD archives never reach the abstain cell (G report s6);
  (2) 1789418772053-0 (8-seed IQR instability, now testable with a seeded
      sampler);
  (3) 1789417664459-0 (symbol-split valleys);
  then the rest of the OPEN queue.
  The extra 5 points go to throughput on the queue, not to new lines.
- E (15%): clause B transfer on screened worlds only (the E-T1b rule:
  graft vs both cheats, Holm). Tools on request. No clause A cells.

## 6. Rules (round 4 physics; SWARM_R2 s4 applies except as below)

- Jobs: every experiment is submitted to your F7 worker
  (`python -m primordial.fabric.worker submit <L> module:fn --exp E --rows
  PATH --ttl-cpu-s S`). The worker's TTL kill replaces `timeout 600`, and
  default ttl_cpu_s is 600. Work longer than that checkpoints (F9) and is
  declared in the hypothesis.
- Epochs: 30 min, closed by the F14 epoch controller (push rows, EPOCH post,
  budget report --warn).
- Budget: F13 warns an OVER cohort once per epoch. An OVER cohort finishes
  its job in hand and yields the next epoch's first slot.
- Test launch 1 of round 4 is 2 epochs, then the conductor quiesces and
  reports.
- Git: branch nestor/r4-<l>-<date>; integrate with `python -m
  primordial.ops.push` (fast-forward only, never force, never during a live
  RowWriter job). Never `git stash`.
- Tests via per-lane live dbs (primordial/tests/_live.py). Never db 0, never
  flushdb a shared db.

## 7. Operator rulings (message 13): Q1 GATE IN, Q2 HOLD

The active variant is `gate_in|HOLD`, and `qd_ledger check` reads it. G and
H still write all four variants.

- Floor = max(abstain, best constant, uniform random, input-invariant learner,
  2-action gate) for that pressure.
- SURVIVED iff the baseline's ci95 low > that floor. Only SURVIVED worlds
  carry clause A (B), are drawn by C, and host E's transfer work.
- HELD iff the gate beats the four-policy floor but the baseline does not
  beat the full floor: the world rewards reaction and the baseline search
  missed it.
  - Each HELD world x pressure is filed by the conductor as an OPEN anomaly
    for D.
  - It carries no clause A: the progress denominator is <= 0.
  - It stays out of B and C's grids until D resolves it and G re-screens it.
- CULLED otherwise.
- PENDING (conductor scheduling, 21:5x): the baseline ci95 low is <= a
  bound made of the pressure's own parts, so the cell cannot SURVIVE, but
  HELD vs CULLED needs the expensive learner.
  - It is recorded as PENDING, not computed from the bound.
  - check() and F12 treat it as INELIGIBLE(PENDING).
  - It does not block the launch. Its learner runs after test launch 1
    quiesces, then the file is updated and H re-replays it.
- Launch: operator "launch when G and H are ready", so gate item 4 is met.
  If the screen yields 0 SURVIVED but >= 1 HELD, the conductor asks the
  operator before launching B, since B would have no cells.

Original questions (kept as the record):

- Q1 GATE IN THE FLOOR? Message 12 lists a four-policy suite, and also names
  w1's 170.47 (the 2-action gate) as the floor.
  - Gate out: w1's floor is 88.28 (abstain) plus the input-invariant learner.
  - Gate in: w1's floor is >= 170.47, and the baseline must beat it.
  Default for the screen table: the listed four; the gate is a column.
- Q2 WEAK WORLD OR WEAK BASELINE? If a gate beats the floor but the float
  linear baseline does not, the world demands reaction but the baseline
  search failed. Round 3's w1 is exactly this: gate 170.47 > abstain 88.28 >
  baseline 63.94.
  - Literal message 12: CULL.
  - Alternative: HOLD until D resolves claim (1).
  Default: CULL, and the table marks such worlds CULLED(BASELINE).

## 8. Conductor A (logistics only)

Owns:
- the P0 builder launches and the launch gate check;
- worktrees;
- liveness (`--watch 60 --post --export-every-min 10`);
- integration, asks and the WSL keepalive window.

Does not own the floor suite, the screen verdicts, the progress threshold or
any scoring. Production seats (SFE, Vivarium, PEW, wforge) are read-only and
never started or stopped by Nestor.
