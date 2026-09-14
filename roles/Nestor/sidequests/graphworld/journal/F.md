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
