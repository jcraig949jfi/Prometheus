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
