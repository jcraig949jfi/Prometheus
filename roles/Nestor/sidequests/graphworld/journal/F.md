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
