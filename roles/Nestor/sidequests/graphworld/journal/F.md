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

## 2026-09-15 10:06 -- F R6 BUILD DONE (posted to A), 26 min of the 95 min build window

- F-R6-1 ae47bb4f1, F-R6-5 4ad0b8980, F-R6-2/3/4 + r6 clock 9842c4f7b, F-R6-6 + refs guard 0f2bdb92a, F9 test b65d46aba.
- Full primordial suite on b65d46aba: 732 passed, 9 skipped, rc 0.
- No worker, clock or controller started for round 6. Lane F idle on asks.

## 2026-09-15 ~12:30 (round 6 live) -- D4 gap: PRODUCTION_CANDIDATE 1789489827401-0 filed (no code, no push)

- D 1789489737094-0: job d6eecdc3a3c8 ran a stale IMPORTED module (fn module fingerprint matched, helper r6_4 was
  edited): TypeError, 0 rows (80292450a). A 1789489756428-0: D4 PARTIALLY FIXED; no mid-round fabric change.
- My error: the contract said the child keeps the sha of each module it imported. The shipped check covers the fn
  module only, and my test edited only the fn module, so the test never touched an imported module.
- Filed through envelope.file_candidate (stub XADDed first, no refusal existed): import-closure fingerprint +
  respawn/refuse. Measured cost: 240 primordial .py files, 1.62 MB, 12.7 ms warm hash. Estimates: 3600 s build,
  900 s tests. Test plan: helper edited between jobs in one serve(). This commit stays local until round close.

# Round 7 R7-BUILD -- Nestor-F[m1-7aa3e77b], start 16:29 (A-new request, synced to dfdb22a8a via push of the r6 journal), cap 18:35

Contract 1789504304514-0 (hook, stub flag, registration, ceilings); H agreed the admit hook (H adds the line);
A accepted with 2 changes (declared lane repos; gpu arbiter registers). F-R7-1 by a fork of this session (in flight).

## 2026-09-15 R7 iteration 1 -- F-R7-2 + F-R7-5 (DONE)

- envelope.CEILINGS gains cpu_wall_noncheckpointable_s (900 in every row); a non-checkpointable cpu job above it is
  refused NONCHECKPOINTABLE_WALL_OVER_CEILING (D15). PRODUCTION = REPLICATION cpu_budget_s 36000, segment 2400, gpu 600
  per lease segment. admit() returns stub (True only for STAGE_BUDGET_REFUSAL). validate() owns evidence_class values
  (VERDICT/OBSERVATION; else ENVELOPE_BAD_VALUE:evidence_class, per A).
- round_clock ROUNDS r7 = PRODUCTION 3600 x 8, drain 1800, close 1800; DEFAULT_ROUND r7; r7 row declares lane_repos
  (B-E,R nestor-r7-<l>; G nestor-bld-g; gpu nestor-r7-e/nestor-r6-e) for residue.
- Tests updated where they pinned the old row or used a non-checkpointable 2400 s job (the new rule refused them
  correctly). metric/r16_cells.py CPU_BUDGET_S = 14400 is G's copy of the old budget: told G (1789504767181-0).
- 89 passed rc 0 on the envelope/clock/R6/receipt-guard/r16_cells subset.

## 2026-09-15 R7 iteration 2 -- F-R7-3 import-closure fingerprint + D18 current-round fix (DONE locally)

- F-R7-3 worker.py: the warm child snapshots every in-repo module it has loaded (primordial.*; PM_CLOSURE_PREFIXES
  for tests), each as (file, sha256 at first sight), refreshed each loop; the probe returns {sha, stale, repo}. A
  stale closure or fn sha mismatch -> respawn + CODE_RELOADED {changed}; still stale -> refused
  CODE_FINGERPRINT_MISMATCH. submit stamps code_repo (the sys.path root the fn was imported from); a child importing
  from another repo -> refused CODE_REPO_MISMATCH at once (D14 guard). Test replays D-R6-5 inside one serve(): helper
  signature changed + new job module -> runs, CODE_RELOADED names the helper; unchanged -> no respawn; 14 passed rc 0.
- D18 (A): round_clock.read(r) without a round id returns None past end_ts or when pm:epoch:state marks that round
  closed (a closed r6 in pm:round:current refused every build job NO_NEW_WORK); read(r, id) stays history;
  active() reads by explicit id so the receipt guard's close-out grace survives. The close unsets current and scan
  flags it (fork, in flight). test_r6_round_id asserted read(r) of a past round: corrected.
- Push blocked 16:45 (PUSH_RC 4): ops.push will not rebase over the fork's uncommitted files; no stash, no WIP
  commit of fork work; cc10210d1 (F-R7-2/5) waits to push with F-R7-1.

## 2026-09-15 R7 iteration 3 -- F-R7-1 residue hygiene (DONE, built by a fork of this session) + batch push

- worker.py registers pm:worker:reg:<L>:<pid> {pid, lane, repo, round_id, cmdline, host, started_ts, tag} (TTL 90 s,
  refreshed with the heartbeat, deleted on stop). ops/residue.py: scan (read-only, rc 1) kinds STOP_FLAG,
  FOREIGN_REPO (per-lane declared repos: --allow-repos, else ROUNDS[r]["lane_repos"]), MULTI_CONSUMER (live =
  registered, alive, argv tokens verified), DEAD_CONSUMER, UNARCHIVED_PRIOR_KEY, CURRENT_POINTS_AT_CLOSED_ROUND;
  stop (registered pids only, argv tokens, own pid skipped; unregistered decoys survive in tests); clear
  --prior-round (flags only for a closed prior round at its final epoch value, DELCONSUMER only pending 0 and no
  live pid, current only if it names a closed prior round; pm:prior:* never; RESIDUE_CLEARED events; rc 2 on refusal);
  register/refresh/unregister for the gpu arbiter (lane gpu, argv -m primordial.nv.gpuq serve).
- epoch round refuses rc 3 on residue before any clock write; the close: commit, push, stop registered workers, clear
  flags, unset current (outside-log events only). --round default = round_clock.DEFAULT_ROUND.
- Fork found its own defect: the argv check required >= 5 tokens, so a bare 4-token gpuq serve never counted live.
- Combined run (R7 + R5/R6 fabric + liveness + receipt guard + r16_cells), db 6: 180 passed rc 0.
- Live store (fork, read-only): E runs an F7 worker from nestor-r6-e (pids 8668, 28760) -> FOREIGN_REPO under the r7
  map; told A. Not touched.

## 2026-09-15 R7 iteration 4 -- D19 granted threads + residue recency + F-R7-4 prep (DONE)

- D19 (A, E 1789505689927-0: numba 3 under an 8-thread token): worker._spawn puts the grant into the CHILD env
  (NUMBA/OMP/MKL/OPENBLAS_NUM_THREADS; spawn lock; parent env restored), a child with another thread count is
  respawned, the child calls numba.set_num_threads(grant); rows and done records carry granted_threads and effective
  numba_threads. Helpers thread_env()/apply_child_threads() for E's gpuq. Test from a parent env of 3: grant 8 -> 8
  (numba + OMP), no grant -> 3 (control), grant change -> respawn.
- Live read-only scan 16:55 (posted 1789505863151-0): rc 1, 16 DEAD_CONSUMER, nothing else; 2 were LIVE unregistered E
  processes (idle 31 ms / 43 s). A scan/clear gap: residue now reports an unbound consumer that read < 120 s ago as
  UNREGISTERED_ACTIVE_CONSUMER and clear refuses CONSUMER_RECENTLY_ACTIVE.
- capacity.py: exp/budget flags (NODE_CAPACITY_PROFILE_R7, --budget-s 1200); the profile key keeps sha_local + rows
  path instead of a sha a later rebase orphans (R5 lesson).
- 64 passed rc 0 (residue, D19, closure, capacity, epoch/round, F7).
- Full suite on 606df2613 (17:03-17:08): 896 passed, 9 skipped, 1 FAILED = G's test_r16_learner_plan
  ::test_committed_plan_file_reproduces. Cause (not F): the committed R16_LEARNER_PLAN_R7.json stores an absolute
  nestor-bld-g path for the order file, so the regenerated plan differs in any other worktree (gate 41 would fail).
  Told G + A with a repo-relative fix (1789506520992-0). H R7 BUILD DONE 17:08; F-R7-4 waits for G + E DONE or 18:10.

## 2026-09-15 R7 iteration 5 -- F-R7-4 NODE_CAPACITY_PROFILE_R7: run 1 CONTAMINATED and aborted; run 2 on a quiet host

- 17:16:47 run 1 started (burst announced, D19 in: a k=1 smoke copy reported numba_threads 8 / pool 8 / env 8).
  Calibration 400 gens 5.25 s -> gens 1523; k=1 thr8 9309 u/s p95 20.94 s util 75.5%; k=2 thr8 13720 u/s p95 28.42 s.
- A disclosed a gate dry run on the host ~17:15-17:17, and G ran a targeted pytest (pids 17528/10412 from 17:16:58,
  then a second run from 17:17:43 at 100% of one core). k=1 (~17:16:53-17:17:14) sat inside both. It is the base of
  both O3 clauses, so run 1 is CONTAMINATED as a whole. Its numbers above are NOT the profile.
- I stopped only my own probe + copy processes by argv tokens (`-m primordial.ops.capacity probe|copy`, own pid
  skipped, no other lane touched) at ~17:18, during k=2. Rows are written only at the end, so no run-1 rows or
  profile were committed (tree clean, no R7 rows). Copies clear their own archive keys.
- Run 2: a background watcher waits until no pytest process runs and host CPU < 15% over 3 s (gives up 17:32), then
  announces a burst and runs `capacity probe --exp NODE_CAPACITY_PROFILE_R7 --budget-s 1200`.
- RUN 2 (the profile): quiet host from 17:18:28 (no pytest, cpu 5.7%), burst announced; calibration 400 gens 5.03 s ->
  gens 1591. k=1 thr8 10085 u/s p95 20.19 s util 57%; k=2 thr8 17513 u/s (1.74x) p95 23.26 s; k=3 thr5 19218 u/s
  (1.10x < 1.15) p95 31.79 s (> 1.5 x 20.19 = 30.29) -> fails both clauses, stop (O9), 4/6/8 untested; 0 errors.
  k* = 2 workers x 8 threads (same as R5; now measured with D19 in and builders idle). Wall 17:18:28-17:19:58.
- Effective threads verified from the committed rows (each copy stamps numba.get_num_threads): {"steps": [[1, 8, [8], 0], [2, 8, [8, 8], 0], [3, 5, [5, 5, 5], 0]], "threads_ok": true, "k_star": 2, "exp": "NODE_CAPACITY_PROFILE_R7", "untested": [4, 6, 8]}
- Rows 8c088ea39 + JSON d3a6cc3c3 (local shas; rebased by the push). pm:capacity:profile exp NODE_CAPACITY_PROFILE_R7,
  k_star 2, threads_per_worker 8, sha_local only (no orphanable pushed sha).

## 2026-09-15 17:27 -- F R7 BUILD DONE (posted to A, G), about 58 min of the 2 h build window

- F-R7-2/5 af3b42c74; D18 2e13d4014; F-R7-1 + D18 parts 2/3 + F-R7-3 19e34af1e; D19 7cff32250; residue recency + probe
  prep 606df2613; probe thread stamps 1d969c64a; NODE_CAPACITY_PROFILE_R7 rows 8c088ea39 / JSON d3a6cc3c3.
- k* = 2 workers x 8 threads.
- Full suite on 703ee6c8b: 910 passed, 9 skipped, 1 FAILED (G's worktree-absolute plan path; G's fix d30bf1cf6 not
  on integration yet), pytest rc 1. No F test fails. Gate 41 needs G's push.
- No worker, clock or controller started by F. Lane F idle on asks.

## 2026-09-15 ~18:07 (round 7 live) -- D22 broker not FIFO: PRODUCTION_CANDIDATE 1789510034347-0 filed (no code, no push)

- D 1789509934842-0 / A 1789509956511-0: D starved behind E's O8 calibration burst. Measured read-only at 18:06:31:
  E took slot 1 13x in a row (17:58:35-18:06:19), G took slot 0 once, D job e2a0a3510473 (queued 17:57:56) had 0 grants
  and waited >= 515 s. SWARM_R7 O4 assumed FIFO.
- My defect (R5 broker): acquire is SET NX with no queue; a worker releases and re-acquires in the same loop while
  waiters sleep 0.1 s; no wait-start is stamped. The R5 broker test checked the cap and idle-cohort sharing, never
  fairness.
- Filed via envelope.file_candidate. Design: cross-lane wait set, oldest-waiter Lua grant, re-queue on release,
  dead-waiter drop, wait_s stamps. Estimates: 2700 s build, 900 s tests. Test plan: a burst on one lane must alternate
  with a waiter. No broker change until round 7 closes (A ruling). This commit stays local until close.

## 2026-09-15 ~18:30 (round 7 live) -- D24 supervisor dies on child EOF: PRODUCTION_CANDIDATE 1789511386497-0 filed (no code, no push)

- C 1789511278131-0 / A 1789511323172-0: C terminated its own job child; worker.run_job pipe.recv() raised EOFError,
  serve() let it through, supervisor exited rc 1; no job_end row, no done entry. Live read-only at 18:29: the job
  message is still PENDING in worker-C (1154 s since delivery), 0 done entries, tokens held by G and D only.
- My defect: run_job polls the pipe before child.is_alive(), so a dead child's closed pipe reads as "result ready";
  _child_cpu() on a dead pid is a second crash path. I never tested an externally killed child.
- Correction to the report: serve() reads only new entries (XREADGROUP >), so a plain restart does not rerun the
  PEL entry; the defects are the dead supervisor, the lost close record and a PEL leak.
- Filed: died handling + sanctioned cancel via a cancel key + close_job helper. Estimates: 2400 s build, 900 s tests.
- MY FILING ERROR: a backticked CLI example inside a bash double-quoted string ran as command substitution (the worker
  CLI started, argparse rejected "cancel", no side effect) and blanked that span of the stored basis. Filings cannot
  be amended; the bus post to A and C restates the missing text. From now on, filing text goes through a quoted
  heredoc or a file, never through bash double quotes.
- This commit stays local until round 7 closes.

## 2026-09-15 ~19:27 (round 7 live) -- D26 + D27 filed as siblings (no code, no push)

- D26 1789514839378-0: a filing cannot be superseded by measured actuals. Verified: stub 1789486665691-0 holds the r6
  ESTIMATE (wall 2132.4 s, cpu 6315.8 s); tonight's run measured 1560 s / 11709 CPU-s (job 90f1b50b9cb2, rows
  e7d095a19, receipt 1789514378793-0) -> wall 0.732x, cpu 1.854x. file_candidate returns ALREADY_FILED (HSETNX, one
  filing per stub). Design: keep the hash as current, add an append-only filings stream, kind estimate|measured,
  supersede + measured_at + supersedes, drift() and a tally line. 1800 s build / 600 s tests.
- D27 1789514839383-0: no code path opens a PC without a refusal. envelope.refuse (envelope.py:159) is the only API
  and needs a refusal event; nv/gpuq.py:234 raw-XADDs a second copy of the schema. 4 hand-written stubs tonight
  (E's D25 + my D4-closure, D22, D24). Design: envelope.open_candidate(...) in the refuse() record shape, origin
  classifier REFUSAL/OPENED/HAND_WRITTEN with tally counts, gpuq moved onto it. 1200 s build / 600 s tests.
- Filing text came from a script file as Python literals, and both stored bases were checked byte-identical to the
  source (the D24 backtick loss made that check necessary). E's D25 stub untouched, per A.
- Local commits held for close: 6b6c03829 (D22), f4d3a6e39 (D24), this one.

## 2026-09-15 ~19:44 (round 7 live) -- D29 row-status vs evidence-class vocabulary: PC 1789515839791-0 filed (no code, no push)

- D-R7-3 job 74bc27094543 emitted status 'observation'; rows.py:44 STATUSES has no such member, so every row was
  refused at rows.py:184. Verified from origin rows + the live done stream:
  * the rows are RECOVERABLE -- _drain (worker.py:416) wraps each refusal in an aborted row carrying the original
    payload verbatim; all 3 (2 case + summary, decision d24:BRAIN_NEAR_TIE|d31:BRAIN_NEAR_TIE) are on origin;
  * the job reported status ok, rows 3, cpu_s 2.34, wall_s 0.654 -- the INDETERMINATE was D's receipt decision.
    A job can have every row refused and still finish ok: my defect, the worse half of D29;
  * measured loss 0.654 s / 2.34 CPU-s, not a full anomaly job; D-R7-3b rows are not on origin, so the re-run is
    unmeasured. D disclosed it correctly and lost one small job.
- The collision is literal: the refused summary row carries evidence_class OBSERVATION and status observation.
- Filed design: emit-time validation in the child with a message naming evidence_class; alias observation -> record
  (my recommendation) or keep refusing; any refused row ends the job status error, never ok; a lint test that
  rows.STATUSES and evidence_n.EVIDENCE_CLASSES never share a member. 1200 s build / 600 s tests.
- Local commits held for close: 6b6c03829 (D22), f4d3a6e39 (D24), 20dd00d74 (D26+D27), this one.

## 2026-09-15 ~21:28 (round 7 live) -- D24 sibling: periodic rows commit kills the supervisor. PC 1789522077070-0 filed

- D 1789521893565-0 diagnosed it sharper than my D24: RowWriter.write commits the rows file every 60 s via
  commit_path (git add/commit in the SAME worktree); commit_path raises RuntimeError (rows.py:146 non-index.lock
  failure, rows.py:149 after 10 lock retries); that call is inside _drain, which catches only ValueError
  (worker.py:416); nothing above catches it, so the supervisor exited 1 and orphaned D-R7-10b (29 of 169 rows).
  ANY git write in the worktree races the writer -- my round 5 rule ("never rebase while a writer is live") was too
  narrow, and this belongs in the fabric, not in lane discipline.
- Not data loss: write() flushes each row; a failed commit loses the commit, not the rows; close() already retries
  and run_job catches a close failure (commit_error). The PERIODIC commit was the unguarded path.
- Second supervisor death tonight from outside the job's own code (C's killed child was D24). Both times the lane
  paid: D hand-closed the job and filed INDETERMINATE. Verified after: worker D pid 30388, 0 pending, no job without
  a done record, no stuck token.
- Filed as a SIBLING: file_candidate refuses ALREADY_FILED, so D24's filing cannot be extended -- D26
  (1789514839378-0) is now blocking a real filing. Design: commit degrades to deferred; _drain/run_job end the job
  status error rows_commit_failed; serve gets a last-resort per-job guard; the rows commit takes pm:push:lock:<lane>.
  1200 s build / 900 s tests.
- Local commits held for close: 6b6c03829 (D22), f4d3a6e39 (D24), 20dd00d74 (D26+D27), ddf3995a7 (D29), this one.

## 2026-09-15 ~22:16 (round 7 live) -- D30 continuation queue position: PC 1789524989582-0 filed (no code, no push)

- Mine, confirmed in code: submit XADDs to the END of pm:jobs:<L> (worker.py:105) and the pause path requeues through
  it (worker.py:584); stream ids are time-ordered, so a continuation cannot be placed before an existing entry.
- Live proof: pm:jobs:G has 260 entries and its last four ARE the four continuations (w19 1789511871187-0, w12
  1789515471033-0, w16 t8 1789519070704-0, w23 1789522670352-0, all segment 1), while the learner entries ahead of
  them were submitted earlier (1789508325591/2-0). Group worker-G: 1 consumer, 1 pending, lag 48. All four hold live
  F9 checkpoints. G: w19 30/32 runs, w23 13/32, w12 1/32, w16 t8 ~328 CPU-s.
- Cost: 4 nearly-finished cells would lose their verdicts to queue position, and G had to XDEL 36 undelivered entries
  (A approved after an audit post) -- lane surgery for a fabric defect.
- Design: continuation class pm:jobs:<L>:cont drained first, bounded by CONT_BURST so fresh work cannot starve,
  ordered by the ORIGINAL queue_ts, with queue_wait_s in done records; 1800 s build / 600 s tests.
- A's note adopted: third scheduling defect tonight (D22 broker fairness, D15 drain sizing, D30 requeue position).
  Round 8 should design ONE scheduler, not three patches.
- Also observed: G's resumable objects carry no progress units (the cell job never calls ctx.progress), so a stranded
  continuation is invisible in the object until a boundary; the filing adds those calls.
- Local commits held for close: 6b6c03829, f4d3a6e39, 20dd00d74, ddf3995a7, d021a3efd, this one.

# Round 8 R8-BUILD TRACK-1 -- Nestor-F[m1-8c85d063], T0 09:15, cap 10:15 (synced ff 6c02b89a9)

## 2026-09-16 09:25 -- G1 + GE + G6 in envelope.py, one iteration (tests 30/30)

- G1 (D29): frozen ROW_STATUSES / ROW_EVIDENCE_CLASSES; vocabulary_reasons(row, index) names value AND index;
  prepare_row(row, index, env) raises RowRefused at EMIT (no alias: 'observation' in any case is refused) and stamps
  predicate_id + predicate_event_id; lint_vocabulary + `python -m primordial.fabric.envelope lint` (tables agree
  with rows.STATUSES and evidence_n; AST over primordial/**/*.py minus tests; optional --rows JSONL). Tree: 281 checks, 0.
- Real-worker regression: a job emitting 4 'observation' rows ends `error`, data rows 0. HONEST LIMIT: that job
  calls prepare_row itself -- a job calling bare ctx.emit is covered only once P puts prepare_row in Ctx.emit and
  makes _drain's refused row end the job `error` (worker.py is P's). Asked on the bus 1789564627164-0 / 1789564931110-0.
- GE: admit(..., gates=None, r=None) -> gate_reasons() BEFORE evidence/ceilings, event GATE_REFUSAL, stub False.
  State = gates arg, else redis pm:round:<rid>:gates, else committed GATE_MAP_<RID>.json (round_id must match).
  Missing/unreadable/bad value -> GATE_STATE_UNAVAILABLE. No clock -> nothing. Enforced for campaign ids rN, N >= 8
  (r5-r7 and test clock ids 't-r7-1' are pre-gate; without that every existing clock test refuses). Topology
  constant: G1 rows>0, G2 ANTI_PRIOR|BETA*, G3 kind cpu, C1 kind gpu, C2 CLAUSE_B non-OBSERVATION (n=32 = MC branch).
- G6 (D27): open_candidate(r, lane, question, basis, requested_cost, dependencies, experiment_class, source_event)
  -> stub + one CANDIDATE_OPENED lineage event, never *_REFUSAL; refuse() now shares _stub(); file_candidate works on it.

## 2026-09-16 09:59 -- P interface agreed; the disclosed G1 limit is closed (tests 31/31)

- Pushed ea3d56cd5 (G1/GE/G6). A confirmed the topology readings (G3 = every cpu job, G2 = ANTI_PRIOR|BETA*,
  C2 = CLAUSE_B unless OBSERVATION) and the rN >= 8 scope, and took ownership of the state source (lanes ff-merge
  GATE_MAP_R8.json before their workers start).
- P agreed in full (1789565860490-0) and pushed e0601f0bf: Ctx.emit calls EV.prepare_row; a refused row in _drain ends the job `error`.
- New real-worker test on that tip, using the ACTUAL D29 shape: a bare ctx.emit job with 4 'observation' rows ends
  `error` with no data row, and a good bare job's rows carry predicate_id + predicate_event_id from the envelope.
- Suite on the synced tip 0ebb3c6ca + this test: 1131 passed, 9 skipped, pytest rc 0.
