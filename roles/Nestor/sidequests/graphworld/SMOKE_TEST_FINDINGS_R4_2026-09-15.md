# Round 4 smoke test: findings, measured scale, and a sized plan for the real run

Currency: 2026-09-15, Nestor-A[m1-449a9e76] (conductor). DRAFT: written while G runs the last
checkpointed job. Two sections get filled when G posts "G R16 CHECKPOINT": s1 (w13 verdict) and s4
(measured per-job wall).

Authority: operator messages 17 and 18 (verbatim in prompts/2026-09-14_graphworld_swarm/):
- "a session that was intended to kick the tires for a subsequent run and to smoke out issues... what
  we're smoking out is the scale of these experiments";
- "stop at a checkpoint... find ways to run smaller campaigns for early round testing... allocate large
  windows of time... or find ways to multi-thread or parallelize the work".

## 0. What this session was, and what it drifted into

- It was intended as a tire-kick for a later run: find defects and size the work.
- It became a full science campaign:
  - an 8-seed world screen (~3 h), then a 70-minute cohort launch;
  - after statistical problems surfaced, a 74-cell 32 x 4 re-screen (10.2 h cleared);
  - a 37 h follow-up was proposed.
- The conductor cleared compute without first restating the stage. That is now a standing rule (memory
  feedback_smoke_test_stage_bounds_compute).
- The re-screen stops at a checkpoint after the w13 learner.

## 1. The one scientific result worth carrying forward

- w13 train128_held64 is the only world x pressure that looked hard enough. Its 8-seed survival was a
  draw property: 13.6% of 8-seed draws (D-R4-2).
- Recomputed from scratch at 32 run seeds x 4 RNG families (G, cross-checked against D's independent
  rows):
  - baseline median 183.91, CI [170.95, 188.56];
  - gate floor 166.47.
- Verdict at the checkpoint: [PENDING -- G's 32 x 4 train128 learner; SURVIVED iff learner median
  < 170.95].
- Nothing is promoted. B's 16 B and 36 B clause A claims on w13 were invalidated by the operator
  (message 15) and have not been re-scored.

## 2. Defects found, and their status

Measurement and statistics:

| # | finding | status |
|---|---|---|
| S1 | Always-abstain beats every round 1/2 baseline, so the round 2 "8-byte parity" was below a trivial floor (round 3). | FIXED in design: floor suite + progress-above-floor (operator 12) |
| S2 | The baseline readout was never specified (top-16 mean); the progress scale moves ~1.4x between readouts (D-R4-1/4). | FIXED: one reader top1_train for baseline + candidates, READOUT_MISMATCH refusal (E a70fcd841) |
| S3 | 8-seed baselines: verdicts and IQRs are draw properties across RNG families (D-R4-2). | FIXED in rule: >= 32 runs, >= 4 families, >= 8 per family, BASELINE_N refusal in judge + F12 (E c0a1404b4, H e26668c8b); screen not re-run in full |
| S4 | n = 8 candidate seed sets flip clause A verdicts (B anomaly 1789450127495-0). | OPEN: candidate seed minimum not yet ruled |
| S5 | The transfer control rand_graft underperforms scratch, so it is not a valid cheat (E-R4-1 INDETERMINATE). | OPEN: redesign the control |
| S6 | QD archives do reach abstain; the baseline < floor gap is selection + readout (D-R4-1). | RESOLVED |

Fabric and operations (each fix has a repro test shown to fail on the old code):

| # | finding | fix |
|---|---|---|
| F1 | An idle F7 worker died: redis-py 8 socket_timeout 5 s == XREADGROUP block. | 519d081c8 |
| F2 | A rows commit crashed on the Windows \\?\ long-path form. | 7fa40eec9 |
| F3 | The worker liveness key expired during long jobs. | 54c2d95fc |
| F4 | Push race: the epoch controller cleared the stop flag mid-rebase. | 898900b4e (pm:push:lock) |
| F5 | The round 2 score replays were open-ended; round 4 rows leaked in. | 45847459e (ROUND2_END) |
| F6 | graphworld_b2 had no obs/action/charge interface, so 25% of C's grid aborted. | draw grid 267fea584; adapter built (E de91fbd52, oracles PASS); not yet screened |
| F7 | The epoch controller runs in the conductor worktree and dirties it, blocking rebases. | OPEN (workaround: commit the log) |
| F8 | Drain stragglers at epoch boundaries (C, E; jobs longer than 120 s drain). | OPEN: size drain_timeout to job TTL |
| F9 | A bus watch blocking XREAD timed out on the socket. | conductor polls instead |
| F10 | Two field-name proposals (E vs G) and a missing per-family condition caught before data existed. | resolved by review |

## 3. Measured scale (5 threads on SKULLPORT unless noted)

| job | size | wall |
|---|---|---|
| stage 1 floor suite, 8 seeds | 74 cells | ~1 h |
| stage 2 baselines, 8 seeds | 74 cells | ~3 h |
| train128 input-invariant learner, 8 seeds | 1 cell (T=64) | ~0.36-2.8 h depending on T |
| R16 floors, 32 x 4 | 37 worlds | 1.9 h (G estimate) |
| R16 baselines, 32 x 4 | 74 cells | 6.9 h (G estimate) |
| R16 train128 learner, 32 x 4 | 1 cell (w13) | 1.42 h (G estimate) |
| R16 phase 2 HELD/CULLED deciders | 5 cells | ~37 h (G estimate), DEFERRED |
| cohort test launch | 4 cohorts x 2 epochs | ~70 min of work |
| boot to hello (suite at boot) | per session | ~2 min |

[s4 to be filled: G's measured per-job wall from the checkpoint post]

## 4. Smaller campaigns for early-round testing (operator 18)

A smoke campaign exercises every code path once. It does not fill the landscape.

- CELLS: 4 world x pressure cells chosen to hit every verdict branch: one SURVIVED (w13 t128), one HELD
  (w1 t8), one CULLED (w4 t8), one degenerate (w19 t8).
- SEEDS: 8 run seeds x 2 RNG families. That is enough to exercise the family plumbing and the
  BASELINE_N refusal. The rule the campaign runs under is marked SMOKE, so the judge refuses nothing,
  but a verdict is labelled "smoke, not science".
- LEARNERS: train8 only. The train128 learner is replaced by a planted bound so the PENDING/exact paths
  still run.
- COHORTS: 1 epoch of 15 min. Each cohort does ONE job through its worker. The epoch boundary, push
  lock, receipt guard and replay all fire once.
- BUDGET: <= 1 h total CPU. A hard stop at 90 min wall. No clearance above 15 min without the operator.
- DONE when every stage has produced a row and a receipt, and every refusal path has been hit once
  deliberately (planted cells).

This would have found S2, S3 (with 2 families, the family spread shows), F1-F5, F7 and F8 in about an
hour. S1 and S6 needed the full floors.

## 5. The production run: time windows, or parallelism

Option A, scheduled windows on SKULLPORT alone:
- Window 1, ~12 h overnight: R16 floors + baselines (74 cells, 32 x 4) + survivor-deciding learners.
- Window 2, ~40 h (a weekend): the phase 2 HELD/CULLED deciders, if the operator wants them.
- Window 3, per cohort round: epochs sized to the jobs (clause A candidates at >= 8 seeds x families).

Option B, parallelize. The screen is embarrassingly parallel: cells and run seeds are independent.
- Same host: with cohorts idle, 16 logical cores allow ~3 screen workers x 5 threads instead of 1, so
  ~10 h becomes ~3.5-4 h. Needs a job splitter over the F7 queue: per-cell jobs, one per worker.
- GPU (round 6 MVPs, measured):
  - Warp CUDA world kernel: 12-36x over 1-thread numba at 16k-65k envs;
  - CUDA graphs closed loop: 2.4-3.7x over 1-thread numba at 65k envs, ~2.3M TT envs fit in 16 GB.
  - Batching all run seeds of a cell into one device population turns the 32 x 4 baseline into one
    large batched rollout. This is the biggest lever, and exactly the round 6 roadmap.
- Other machines: the account shows other hosts (M2 WSL, M4 cloud). A second host running cells in
  parallel over the shared bus halves the wall. Needs the bus reachable off-host, which it currently is
  not (127.0.0.1:6390).

Recommendation for the next session:
1. Run the section 4 smoke campaign first (<= 1 h).
2. Then one overnight window with Option B same-host parallelism (3 workers) for the R16 screen
   (~4 h).
3. Then a cohort round with epochs sized to the job TTL.
4. Keep phase 2 deferred until a GPU-batched learner exists.

## 6. Parked, with resume pointers

- The R16 re-screen is parked at G's checkpoint: J2 baselines partially done, J1 floors partially done.
  Resume steps are in "G R16 CHECKPOINT" (bus) and journal/G.md.
- The B2 screen has not started. It needs a genome/linear-baseline wiring (G, or E on request).
- Phase 2 HELD/CULLED deciders: deferred (operator 17).
- B re-score of w13 (operator 15/16): after a full v2 screen + H replay.
- Open design questions:
  - the candidate seed minimum (S4);
  - the transfer control (S5);
  - the epoch controller worktree (F7);
  - drain timeout (F8);
  - the learner floor readout, top1_train by the operator-15 principle, flagged.
