# Lane F journal (Nestor-F[m1-5d465c7f], FABRIC builder, round 3)

Threads: 3 (conductor contract 1789425755152-0 overrides the boot prompt's 5).

## 2026-09-14 iteration 1 -- O3 RowWriter PM_TAG guard + ff-only push (DONE)

- rows.py: RowWriter.__init__ and commit_path raise without a real PM_TAG
  (unset, blank, or "untagged"); nothing is written before the check.
- A live writer keeps a marker in its worktree's git dir
  (<git-dir>/pm-rowwriters/<pid>-<id>.json), removed on close; markers of
  dead pids are pruned on read (psutil; never os.kill(pid, 0), which
  terminates on Windows). `python -m primordial.fabric.rows live` lists them.
- ops/push.py: the integration push. No live writer: fetch, rebase if
  behind, push. Live writer: push only if HEAD already contains the tip,
  else exit 3 naming the writers, no rebase. Rebase conflict: abort, exit 4.
  Never forces. Target defaults to nestor/sidequest-graphworld-2026-09-14
  (PM_INTEGRATION_BRANCH overrides).
- Tests: test_o3_push_guard.py (8, bare remote + two clones): tag guard x4,
  marker lifecycle + dead-pid prune, refuse-while-live then rebase-after-close,
  ff while live, conflict abort. Suite 37 passed, with and without PM_TAG
  in the environment.
- Lanes should push with `python -m primordial.ops.push` from now on.

## 2026-09-14 iteration 2 -- O5 GPU lease (DONE)

- bus.py: `pm:gpu:lease` = {holder, lane, tag, purpose, since, until, token},
  SET NX PX. A lease whose `until` has passed is taken over even if the key
  lingers (CAS in Lua); release and renew are compare-and-set on the stored
  record, so a taken-over holder cannot delete or extend its successor.
- `gpu_lease(purpose, ttl_s=600, wait_s=0)` context manager: renews every
  ttl/3 on a daemon thread; the yielded record's `lost` flag marks a failed
  renewal (the number is then INDETERMINATE for speed). Taking the lease
  posts a bus note.
- host_load() now records `gpu_lease` {holder, purpose, until} or null, so
  every receipt shows whether its timing was leased.
- CLI: `bus lease show | take SECONDS PURPOSE [--wait S] | release RECORD_JSON`.
- Tests: test_o5_gpu_lease.py (6, live db 15): second holder blocks then
  gets it after release; expired lease taken over, old record cannot
  release/renew; Redis TTL expiry frees it; context manager renews past 2
  TTLs; host_load records holder; CLI round trip. Suite 43 passed.

## 2026-09-14 iteration 3 -- O1 scheduled-task launcher (DONE)

- ops/schtask_launch.py: `launch L --worktree W [--prompt-dir D]` writes
  the .cmd with Python (CRLF, ASCII, quoted paths), then schtasks
  /Create ONCE /IT -> /Run -> /Change /DISABLE (always, even after a failed
  run) -> verify from the task XML (<Settings><Enabled>, locale-free).
  Still enabled -> exit 5. `audit` lists PM_* tasks still enabled.
- `selftest`: the real schtasks path with a dummy cmd.exe /c exit 5 and a
  private launch log; requires start logged, exit_code 5, task disabled,
  then deletes the task.
- Live self-test 18:51 FAILED exit_code_5 (got 1): under `powershell -File`
  an array argument '/c','exit 5' binds as ONE literal string. The dummy
  args are now one string ("/c exit 5"; launch_lane.ps1 joins them anyway),
  and launch_lane.ps1's own self-test example carried the same bug (fixed).
- Live self-test 18:52 PASS (launched, start logged, exit 5, disabled,
  deleted). audit: no enabled PM_* tasks (the conductor's PM_bld_* are
  disabled).
- Tests: test_o1_schtask_launch.py (7 with schtasks faked + 1 live behind
  PM_LIVE_SCHTASKS=1). Suite 50 passed, 1 skipped.

## 2026-09-14 iteration 4 -- F7 warm worker per lane (DONE)

- fabric/worker.py: a supervisor per lane reads job specs from pm:jobs:<L>
  (consumer group worker-<L>) and owns the RowWriter. One long-lived spawned
  child holds imports, kernels, a Redis pool and ctx.cache, runs
  `module:function(ctx, **kwargs)`, and XADDs rows to pm:rows:<L>. The
  supervisor watches the child's CPU time (psutil). Past ttl_cpu_s it kills
  the child tree, drains the rows already emitted, appends status=timeout,
  commits, and respawns a child for the next job. Job errors and child
  deaths end with an aborted row. Outcomes go to pm:jobs:<L>:done.
  CLI: `python -m primordial.fabric.worker serve --lane L | submit ...`.
- Measured (temp repo, db 13): jit_probe call 607.40 ms in job 1, then
  0.01 ms in jobs 2 and 3 (one child). burn with ttl_cpu_s=2.0: killed at
  2.05 CPU-s, 41 partial rows plus the timeout row committed, wall 2.13 s.
- Found on the way:
  (1) Other builders' suites FLUSH db 15 while mine runs: my first F7 run
      lost its job stream mid-test (NOGROUP). Moved F7 and O5 tests to db 13
      with unique keys that delete only their own keys. Cause inferred, not
      caught in the act: no pytest was running when I looked.
  (2) Spawned children cannot re-import a __main__ read from stdin. The
      worker records such a job as died/aborted, and the CLI runs via -m,
      so it is not affected.
  (3) The fabric hygiene test rejects static njit without cache=True. The
      probe kernel is compiled at runtime and held in memory, the exemption
      the test documents.
- Tests: test_f7_worker.py (3). Suite 53 passed, 1 skipped.

## 2026-09-14 iteration 5 -- F8 seed/world table cache (DONE)

- Profile first (19:00): FusedRollout.__init__ at 128 genomes x 128 seeds
  took 0.37-0.39 s, and 87% of it was init_regs: 229k wforge stream()
  hashes for 16,384 envs, although only the 128 seeds differ.
- fabric/worldcache.py: `tables(mech, wid, seeds)` -> regs, stoch, corr for
  each seed. They are computed once per (world id, mechanics digest, seed),
  held in process memory (the F7 warm child keeps them), and stored as one
  .npz per (world id, digest) in PM_WORLDCACHE_DIR, written atomically and
  shared across processes. The digest guards against a world id reused with
  other mechanics. PM_WORLDCACHE=0 turns the disk layer off.
  `cold_tables` is the old computation, kept verbatim as the oracle.
- soup/b6/fused.py (F owns this id): __init__ builds the k-seed tables from
  the cache and tiles them over P. No other change.
- Measured (temp cache dir): the old per-env path took 0.45-0.49 s. Builds
  from the memory cache took 0.4-0.5 ms (1102x); from disk with fresh memory,
  about 1 ms (470x). The first build on an empty cache took 5 ms (the win
  from computing each unique seed once).
- Tests: test_f8_worldcache.py (4). Arrays are bytes-equal to the cold
  per-env build via cold, memory and disk, for tt_digits and linear, with a
  repeated seed; run() fitness, cells and done ticks match the uncached
  path; the digest keeps worlds that share an id apart; the cache is >= 5x
  faster. Suite 76 passed, 1 skipped (the 1 warning is from U's torch test).

## 2026-09-14 EPOCH 1 posted 19:07: done=[O3,O5,O1,F7,F8] tests=76 open=[F14,F9,F15,X]

## 2026-09-14 iteration 6 -- F14 epoch controller (DONE) + O5 tests load-stable

- ops/epoch.py `EpochController(lanes, epoch_s=1800)`. At T + n x epoch_s it
  posts EPOCH n (to ALL) and sets pm:jobs:<L>:stop. It waits until every live
  worker reports `stopped` (stragglers are recorded after drain_timeout_s),
  exports the bus into <out>/epoch_<n>/, and writes <out>/EPOCH_<n>.json.
  It commits that directory, clears the flags, and sets pm:epoch:state
  running n+1. Every step is logged to <out>/epoch_log.jsonl.
  CLI: `python -m primordial.ops.epoch run --lanes B,C,D,E [--epoch-min 30]`
  or `boundary N --lanes ...`.
- worker.py: no job is taken while the stop flag exists. State goes to
  pm:worker:<L> {idle|busy|stopped} with a 30 s TTL. A job received before
  the flag runs to completion before `stopped`. Done records carry
  started/ended. serve() gains deadline_s and exit_requested.
- Test (acceptance): 2 simulated epochs of 4 s with 2 real workers and a
  submitter feeding 0.25 s jobs. Checked: event order start + 2 x (post,
  stop_set, drained, exported, committed, resumed); no stragglers; no job
  interval overlaps [drained, resumed]; each worker ran jobs in all 3
  windows; EPOCH-1/EPOCH-2 commits present; log file == events; flags
  cleared. First version took 61 s because workers waited for their
  deadline; exit_requested brings it to 11 s.
- O5 tests: A, P and W reported renew/expiry flakes under 8-builder load.
  Most were the shared-db flush (A fixed it: per-lane test dbs 660ab7f38 +
  fb15cc3a2). The fixed sleeps are gone too: the TTL-expiry test polls up to
  5 s, and the renew test uses ttl 1.5 s and polls for 2 renewals with the
  same token.
- My F7/O5 move to db 13 collided with U's per-lane db (13); A's live_url()
  supersedes it, and F14 uses live_url().
- Suite on the integration tip, PM_LANE=F: 115 passed, 1 skipped.

## 2026-09-14 iteration 7 -- F9 checkpointed long jobs (DONE) + X liveness BUSY (DONE)

- F9, worker.py: ctx.should_pause() reads the epoch stop flag. ctx.pause(state)
  pickles the state atomically to <ckpt_dir>/<lane>/<job_key>.pkl and ends
  the segment `paused`. The supervisor requeues the job as the next segment
  (same job_key, segment + 1, cpu_prior += this segment's CPU), so
  ttl_cpu_s bounds the whole job, and ctx.load_checkpoint() resumes it.
  A finished job deletes its checkpoint. Done and end rows carry job_key,
  segment and cpu_prior, so F13 can charge the whole job to its cohort.
- Test (acceptance): a deterministic RNG walk (60 steps, seed 11). It ran
  once uninterrupted, then again across 3 epochs, with EpochController
  boundaries at 15 and 35 rows while it was running. Done statuses were
  paused, paused, ok (segments 0,1,2); the rows carry segments {0,1,2} and
  are EXACTLY the uninterrupted rows (ts/job_id/exp_id/segment excluded);
  the checkpoint is removed at the end. A second test: a segment with
  cpu_prior 0.9 and ttl 1.0 times out after < 0.1 CPU-s of its own.
- X, ops/liveness.py: E was flagged STALE at 16:53 during a background run
  (transcript quiet 618 s; heartbeat lapsed while it waited; nothing looked
  at the run itself). A lane with a quiet transcript and no heartbeat is
  now sampled once more: CPU gained by its session's process tree over
  sample_s (psutil) or a live F7 worker state makes it BUSY, not STALE.
  BUSY never posts `missing`. All quiet lanes share one sample window.
- Tests: test_f9_checkpoint.py (2), test_x_liveness.py (3, all sources
  faked). Suite 133 passed, 1 skipped.

## 2026-09-14 iteration 8 -- F15 boot pack (DONE); PACKAGE GREEN, lane F pauses

- ops/bootpack.py `build(lane, epoch)` generates the pack from live state:
  boot block (fetch/merge, comms boot, env with the lane's threads,
  hello), the lane's charter + SWARM_R2 s4 rules extracted by heading at
  generation time (headings demoted under the pack's own sections), open
  claims, inbox digest (last 15 addressed to the lane via XREVRANGE:
  nothing consumed, group untouched; bodies cut at 400 chars), the QD
  ledger Pareto front per world (top 3) + floor, OPEN anomalies, and the
  lane's last journal entry. The pack warns if it exceeds 16 KB. With
  EpochController(bootpack=True), every boundary writes
  epoch_<n>/bootpack/<L>.md into the committed epoch directory.
- Measured (live bus, lane F): pack 14.2 KB / 124 lines (vs ~70-74k tokens
  of round 1 boot reading), generated in 0.38 s; read pack + comms boot +
  comms instance + bus hello = 5.45 s, hello rc 0. This is tool time
  only; model reading time is not measured.
- Tests: test_f15_bootpack.py (2): every section present, only the lane's
  claims and messages, a long body cut, front/floor line, demoted
  headings, no consumer group touched, < 16 KB; a boundary with
  bootpack=True commits one pack per lane. Suite 147 passed, 1 skipped.

PACKAGE F: O3 0712083bc, O5 98f8bf705, O1 a96830abc, F7 00586cf91,
F8 ec6322c07, F14 13802b096, F9 + X 0bdc60259, F15 (this commit): all green.
Stopping per brief s0.8 (package green before epoch 4). No open claims,
nothing running, all pushed.

# Round 5 P-BUILD -- Nestor-F[m1-7aa3e77b], hello 06:13:16, cap 08:13

Interfaces posted to G,H,E,A 06:14 (1789467306628-0).

## 2026-09-15 R5 iteration 1 -- F-R5-1 envelope + stage admission (DONE)

- fabric/envelope.py: the 11 mandatory fields, one CEILINGS table (PILOT cpu wall 900, gpu 600,
  cpu_budget 1200), ALLOWED stages per active stage, admit() -> {ok, event, reasons}; refuse()
  writes STAGE_BUDGET_REFUSAL to pm:events + a PRODUCTION_CANDIDATE stub to pm:production_candidates.
- worker.py: serve() admits before running (a round clock makes the envelope mandatory; no clock and
  no envelope = legacy); refused jobs get a done record status=refused, no rows file, worker survives.
  The envelope caps ttl_cpu_s at cpu_budget_s and kills past wall_budget_s (limit=wall, TIMEOUT event).
  Done records carry cohort/campaign_stage/experiment_class/predicate_id.
- ops/round_clock.py (used by admission; F-R5-2 wires the controller).
- Tests test_r5_f1_envelope.py (12, incl. A pins: PRODUCTION refused, SMOKE/REPLICATION at PILOT ceilings, unlisted stage refused) + F7/F9/F14 regression: 23 passed rc 0.

## 2026-09-15 R5 iteration 2 -- F-R5-2 round clock + NO_NEW_WORK (DONE)

- ops/round_clock.py: pm:round:r5 {start_ts, epoch_s 1500, epochs 4, no_new_work_ts +6000, drain_ts +6600,
  end_ts +7200, stage PILOT}; start() is idempotent (a second start cannot move or extend the clock).
- epoch.py run_round(clock): boundaries 1..3 resume; at no_new_work_ts a flag + event; at drain_ts
  boundary 4 without resume (stop flags stay: F9 jobs pause); at end_ts ROUND_<id>.json committed.
  Every EPOCH record now carries budget by cohort and lane. CLI: `epoch round --lanes B,C,D,E`.
- Worker refusal after no_new_work_ts is admit()'s NO_NEW_WORK (event NO_NEW_WORK_REFUSAL); a
  continuation segment runs only if it can finish by drain_ts.
- Test (scaled 2.5 s epochs, real worker + feeder): 3 resumes, NO_NEW_WORK before drain_hold, work in
  epochs 1-3, every post-NNW job refused NO_NEW_WORK_REFUSAL and none admitted, EPOCH-1..4 + ROUND
  commits. With F14/F9/F15: 9 passed rc 0.

## 2026-09-15 R5 iteration 3 -- F-R5-3 resumable job object (DONE)

- worker.py: a paused job (or a timeout that left a checkpoint) writes pm:resumable[job_key] with the ten
  operator-19 s4.5 fields + lane, exp_id, envelope, ttl, next segment, code_file_sha256, queued_job_id;
  CHECKPOINTED event. ctx.progress()/pause(completed_units=, remaining_units=) feed the units (kept in
  Redis, so a killed job still has them). A finished job deletes the object.
- resume(r, job_key) requeues from the object alone; refuses NO_OBJECT / ALREADY_QUEUED / CODE_CHANGED
  (module source hash; HEAD moves with rows commits) / NO_CHECKPOINT. A refused queued segment (NO_NEW_WORK)
  clears queued_job_id, so the object stays resumable. Worker(auto_requeue=False) leaves resume to code.
- Test: walk 40 steps paused after 5+ rows by the stop flag, object complete, fresh worker resumes, rows ==
  uninterrupted run exactly, object + checkpoint gone. With F-R5-1/2, F7, F9, hygiene: 33 passed rc 0.

## 2026-09-15 R5 iteration 4 -- F-R5-4 liveness states + F-R5-6 drain/controller repo (DONE, built by forks of this session)

- F-R5-4 liveness.py: DEAD / BUSY_COMPUTE / DRAINING / ACTIVE (transcript <= 120 s) / IDLE / STALE;
  holds_job(r, L) = pm:worker job_id or XPENDING on worker-<L>. post_changes pages A only on a change into
  STALE or DEAD of a lane holding a job. Tests: test_r5_f4_liveness.py (4), test_x_liveness.py renamed and
  tightened (OK -> ACTIVE / IDLE).
- F-R5-6 epoch.py (defect F8): drain_timeout_s=None sizes the drain to max(remaining envelope wall budget of
  busy jobs; no envelope -> 900) + 30 s; the value lands in the drained event and EPOCH record. (Defect F7)
  CLI run/boundary/round need --repo / PM_EPOCH_REPO, refuse (rc 2, before Redis) ROOT, a path inside it, or
  a non-git dir; records commit there and push from there (push_failed logged, clock continues). The
  controller worktree (e.g. nestor-epoch) is the conductor's to create. Tests: test_r5_f6_drain.py (7).
- Combined run (all R5 + F7/F9/F14/F15/X/hygiene), db 6: 60 passed rc 0.

## 2026-09-15 R5 iteration 5 -- F-R5-5 probe run: NODE_CAPACITY_PROFILE_R5 k*=2 x 8 threads (DONE)

- Burst 06:33:52. Plumbing smoke (k=1, 20 gens) clean, then the probe: calibration 400 gens 4.96 s -> gens 1613.
  k=1 thr8 9917 u/s p95 20.82 s; k=2 thr8 13260 u/s (1.34x) p95 31.14 s (limit 31.23); k=3 thr5 14855 u/s
  (1.12x) p95 41.70 s -> fails both clauses; stopped (O9). 0 errors. Probe wall ~2 min (budget 15).
- DEFECT (mine): the profile row's `status: OK` overwrote the row status -> ValueError after the 3 step rows
  committed. Fixed (profile_status; row status set last) with a regression test on the measured values; the
  profile was rebuilt from the committed rows by from_rows (rule re-applied, nothing re-measured).
  Pushed 19de31605 / rows 7d36e0cb7 / JSON 119508e87; pm:capacity:profile sha corrected to the pushed sha.
- DEFECT: rss_peak/ctx_switches sampled the venv python.exe launcher, not its child (near zero in these rows;
  not used by the rule). Sampling now includes children; not re-run.
- Review fix to F-R5-6: the job-sized final drain (<= 930 s) is capped at end_ts - now (test_r5_f6_drain_cap).
- Open for A: admission horizon end_ts vs drain_ts (operator 19 s14); controller worktree to create.
- A ruled 06:38 (1789468596599-0): admission horizon = drain_ts (operator 19 s14). admit() refuses
  PROJECTED_PAST_ROUND_END when now + wall > drain_ts (name kept for H/E), checked only before no_new_work_ts;
  past it NO_NEW_WORK alone decides (keeps the single-reason NO_NEW_WORK_REFUSAL). Tests F-R5-1/2 18 passed rc 0.

## 2026-09-15 06:42 -- F R5 BUILD DONE (posted to A 1789468904084-0), 29 min of the 2 h cap

- F-R5-1 16e510f91 (+ horizon aa053dd77->pushed c6e130c66), F-R5-2 6b8747794, F-R5-3 f27dd9258, F-R5-4 e2f7756d6,
  F-R5-5 999083dee + 19de31605 (profile 7d36e0cb7 / 119508e87, k*=2 x 8 threads), F-R5-6 a1c9a3c87.
- Full primordial suite on 119508e87: 660 passed, 9 skipped, rc 0.
- Open for A: controller worktree + `epoch round --repo`; restart F7 workers after pulling (broker live).
- Lane F stopped: nothing running, all pushed.

# Round 6 R6-BUILD -- Nestor-F[m1-7aa3e77b], start 09:40 (A-new request, ff db1cab836), cap 11:15

Interfaces posted to G,H,A 09:44 (1789479761855-0). F-R6-1 and F-R6-5 built by forks of this session (no git),
reviewed by their reports + the combined run; F-R6-2/3/4 + round id by this session.

## 2026-09-15 R6 iteration 1 -- F-R6-1..5 + pm:round:r6 (DONE, one combined run 109 passed rc 0)

- F-R6-1 (D3) epoch.py: events go to a log OUTSIDE the repo (PM_EPOCH_LOGDIR, log_dir arg); copied into
  <out>/epoch_log.jsonl just before each commit, so nothing is written in the repo after a commit; _push runs this
  code's push.py against the controller repo (push_branch -> PM_INTEGRATION_BRANCH, PM_LANE cleared). Test vs a bare
  remote: clean + `pushed` + origin == HEAD after every boundary and close. test_f14_epoch adapted (it asserted the
  old in-repo-after-commit log).
- F-R6-2 (D4) worker.py: submit carries code_file_sha256; the warm child records the sha of each module it imports
  and answers a probe; mismatch -> respawn + CODE_RELOADED; still mismatched -> refused CODE_FINGERPRINT_MISMATCH (no
  stub). Segments and resume carry the original sha. My first test ran the two jobs in two serve() calls, which stop
  the child, so job 2 got a fresh child and never exercised the stale path (CODE_RELOADED count 0 exposed it);
  rewritten as one serve() with a feeder thread editing the module between jobs.
- F-R6-4 envelope.CEILINGS PRODUCTION = REPLICATION = segment wall 2400, gpu 600, cpu_budget 14400; wall_budget_s is
  the SEGMENT wall (not cumulative); a checkpointable job gets should_pause() at it (killed only SEGMENT_GRACE_S 60 s
  later) and continues by segment (test: 1 s segments reproduce an unsegmented walk exactly). Lint test: no
  ceiling-table copy outside envelope.py.
- F-R6-3 (D6) envelope.file_candidate(r, stub_id, measured_cost, basis) / open_candidates / filed_candidates;
  refuse() returns stub_id; NO_STUB / BAD_COST / NO_BASIS / ALREADY_FILED refused; CANDIDATE_FILED event.
- F-R6-5 launch_lane.ps1 -DryRun: parse, resolve, print one JSON line, exit 0, no log/env/process; every
  contract.LANES letter rc 0, Z refused, prompt_exists reported.
- Gate 16: round_clock.ROUNDS {r5 PILOT 4x1500, r6 PRODUCTION 5x2400 drain 1200 close 1200}, DEFAULT_ROUND r6; CLIs
  default r6; R5 tests pinned to "r5".

## 2026-09-15 R6 iteration 2 -- F-R6-6 round shape flags + refs/pm guard (DONE)

- A 1789479834686-0: `epoch round` gains --epoch-s/--epochs/--drain-s/--close-s (default None = the ROUNDS row of
  --round, so --round r5 is exactly R5); parser()/round_shape() split out so the launch command is tested without
  Redis. A's launch line (r6 PRODUCTION 2400 x epochs, drain 1200, close 1200) reaches the plan verbatim.
- A 1789479784925-0 (for H-R6-1 D7): static scan -- no --prune/--mirror/--delete/empty-source ref push in
  primordial/ops or fabric; bare-remote test: a controller boundary push that must rebase keeps refs/pm/pred/P-test
  at the cited sha, and the cited commit is an ancestor of the pushed branch.
- Pushed F-R6-1..5 at 09:53 (ae47bb4f1, 4ad0b8980, 9842c4f7b) after one lost push race (remote moved, rejected, re-run
  rebased; never forced). Tests: 22 passed rc 0 (epoch-related + round id).
- Full suite on 0f2bdb92a: 728 passed, 1 FAILED (test_f9_checkpoint cpu_prior > 0 read 0.0). Cause is mine (F-R6-2):
  the fingerprint probe imports the fn module BEFORE the segment's CPU clock starts, so a sleep-heavy walk segment
  can measure 0.0 CPU-s at Windows timer resolution (it passed solo). The assertion is re-aimed at the claim: the
  carry is exact (segment n cpu_prior == sum of earlier segments' cpu_s); 3 back-to-back runs green. Disclosure:
  job cpu_s no longer includes the fn module's first import in a fresh child (the probe pays it outside the job).
