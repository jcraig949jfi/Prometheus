# Round 4 smoke test: findings, measured scale, and a sized plan for the real run

Currency: 2026-09-15 ~05:55, Nestor-A[m1-449a9e76] (conductor). FINAL. G posted its checkpoint at
integration 1268ead0c (bus 1789464893237-0); the session stops here (operator 18).

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
- Verdict (G R16, bus 1789464893208-0, rows 3eb05692a / 1817bed46): w13 train128_held64 SURVIVED under
  gate_in|HOLD, the first survivor under the full statistical rule.
  - floor parts: abstain 159.00, best constant 159.00, uniform random 58.07 (32 streams),
    input-invariant learner median 151.75, ci95 [151.44, 151.91] (32 runs x 4 families, top1_train);
  - gate 166.47, which is the floor;
  - baseline ci95 low 170.95 > 166.47;
  - clause A progress denominator = 183.91 - 166.47 = 17.44.
- Checks:
  - family 4200 top1 == E-R15-1 8/8;
  - legacy top-16 == D-R4-2 32/32;
  - oracles clean;
  - deterministic floor parts == stage 1.
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
| R16 train128 learner, 32 x 4 | 1 cell (w13, T=32) | MEASURED ~190 s per run, so ~1.7 h (G estimated 1.42 h) |
| R16 phase 2 HELD/CULLED deciders | 5 cells | ~37 h (G estimate), DEFERRED |
| cohort test launch | 4 cohorts x 2 epochs | ~70 min of work |
| boot to hello (suite at boot) | per session | ~2 min |

MEASURED at the checkpoint (G, 5 threads, lane G alone):

| job | done | wall | CPU |
|---|---|---|---|
| J1 floors, segment 0 | w13 floors + partial w7 learner | 362 s | 1,629 CPU-s |
| J2 baselines 32 x 4, segment 0 | 6 cells + w34 t128 15/32 | 2,303 s | 11,232 CPU-s |
| J3 train128 learner 32 x 4 | w13 (T*S = 32) | 6,049 s (~189 s per run) | 12,031 CPU-s |

Per run, per unit T*S:
- baseline train128: 0.116 s;
- baseline train8: 0.0041 s;
- train8 learner: 0.0424 s;
- train128 learner: ~5.9 s.

Full-screen projection (search wall only), about 9.8 h before any survivor-deciding train128 learner:
- baselines train128: 6.9 h;
- baselines train8: 0.24 h;
- train8 learner: 2.5 h (plan 1.75);
- deterministic re-check: 0.11 h.

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
- BUDGET (operator, 09-15 ~03:40): a 1-2 h wall window for the smoke campaign, which is "enough time to
  smoke out most early issues at this stage, then we can increase runtimes". Hard stop at 2 h wall. No
  single job clearance above 15 min without the operator.
- ESCALATION: only after a smoke campaign comes back clean, raise runtimes step by step. Example
  sequence: 2 h smoke, then a ~4-6 h pilot on a subset, then an overnight production window.
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

- The R16 re-screen is parked at G's checkpoint (integration 1268ead0c):
  - J1 floors done for w13, w7 train8 learner 26/32, 35 worlds not started (job_key cd9335d8b8af);
  - J2 baselines done for 6 cells, w34 t128 15/32, 67 cells not started (job_key cd266a1b007d);
  - checkpoints under C:/Users/jcrai/lab/pm-data/ckpt/G/;
  - resume record roles/Nestor/sidequests/graphworld/R16_CHECKPOINT_2026-09-15.json, exact submit
    calls in bus 1789464893237-0.
  worlds_r4/v2 is NOT written, so check() still reads v1 and refuses BASELINE_N. B's re-score waits for
  the full v2 file.
- The B2 screen has not started. It needs a genome/linear-baseline wiring (G, or E on request).
- Phase 2 HELD/CULLED deciders: deferred (operator 17).
- B re-score of w13 (operator 15/16): after a full v2 screen + H replay.
- Open design questions:
  - the candidate seed minimum (S4);
  - the transfer control (S5);
  - the epoch controller worktree (F7);
  - drain timeout (F8);
  - the learner floor readout, top1_train by the operator-15 principle, flagged.
