# Builder brief, lane Q, round 8 phase R8-BUILD -- TRACK-3 (ops/)

You are Nestor-Q, the OPS builder. Worktree F:/Prometheus-worktrees/nestor-bld-q (branch nestor/bld-q-2026-09-14).
- Run `git fetch origin && git merge --ff-only origin/nestor/sidequest-graphworld-2026-09-14`.
- Never force. Never git stash. Never pip install into gw-venv.

Read, in order:
- BUILD_R8.md -- G8 (yours, FIRST), G7, G4, and the ownership table;
- BOOT_R8.md s1 (new rules), s2 (the seven that bit in r7), s3 (gate -> blocked work);
- SWARM_R8.md s0.1 (ADAPT-14/15 archival sufficiency), s3 (gate order), s17 rulings R14, R16, R17, R18;
- LAUNCH_R8.md s4 (clock arithmetic) and s9 (launch preconditions);
- prompts/2026-09-14_graphworld_swarm/28_OPERATOR_R8_BUILD_RULING_FAIL_CLOSED.md.

STAGE: R8 BUILD. HARD CAP 10:00 local (T0 09:00 + 60 min). Post "Q R8 BUILD STATUS" to A at 09:40.
At the cap, STOP. Unfinished items become PRODUCTION_CANDIDATE via envelope.file_candidate. Do not extend.

YOU OWN, EXCLUSIVELY: `primordial/ops/round_clock.py`, `primordial/ops/bus_export.py`,
`primordial/ops/epoch.py`. You own nothing else in `primordial/ops/` -- `residue.py` is E's this round.
You may not edit another builder's file, not even to fix an obvious bug, not even if your gate depends
on it. A missed gate is PERMANENT for the round. Raise cross-file needs on the bus; do not reach across.

YOUR TRACK IS THE CRITICAL PATH. G8 blocks the clock itself, therefore everything.

## Order

1. **G8 FIRST -- the `ROUNDS["r8"]` row and FAIL-CLOSED round ids.** `round_clock.py`.
   Measured now, by A, on this tip: `ROUNDS` has r5/r6/r7 only, `DEFAULT_ROUND = "r7"`, and line 47 is
   `row = ROUNDS.get(round_id, ROUNDS[DEFAULT_ROUND])`. So today `plan(t, round_id="r8")` returns
   **epochs 8, epoch_s 3600** -- 8 science hours instead of the ruled 12, with r7's lane_repos, raising
   NOTHING. `plan(t, round_id="r9")` does the same. This is the D18 shape: a stale definition producing
   confident, wrong behaviour.
   Land the row:

       "r8": {"stage": "PRODUCTION", "epoch_s": 3600.0, "epochs": 12,
              "drain_s": 1800.0, "close_s": 1800.0, "lane_repos": {...}}

   `lane_repos` -- A's logistics declaration, complete this round (r7 declared only B,C,D,E,G,R,gpu and
   left A,F,H,P,Q undeclared; a worker from an undeclared repo is FOREIGN_REPO residue, D14):

       B,C,D,E,R  ->  F:/Prometheus-worktrees/nestor-r8-{b,c,d,e,r}   (created, verified, clean)
       G          ->  F:/Prometheus-worktrees/nestor-bld-g            (G's screen worker, as in r7)
       H          ->  F:/Prometheus-worktrees/nestor-bld-h
       F          ->  F:/Prometheus-worktrees/nestor-bld-f
       P          ->  F:/Prometheus-worktrees/nestor-bld-p
       Q          ->  F:/Prometheus-worktrees/nestor-bld-q
       A          ->  F:/Prometheus-worktrees/nestor-sidequest-graphworld
       gpu        ->  F:/Prometheus-worktrees/nestor-r8-e

   Acceptance (all testable):
   1. `plan(t, round_id="r8")` -> `epochs == 12`, `epoch_s == 3600.0`, span `12*3600 + drain + close`.
   2. A test asserts `"r8" in ROUNDS` -- the fallback never defines a live round.
   3. `residue.allowed_repos(r, "r8")` resolves from `ROUNDS["r8"]["lane_repos"]` and its source string
      names r8. (Read `residue.py`; do not edit it -- it is E's. If it needs a change, raise it on the bus.)
   4. A test asserts every lane above that runs a worker has a declared repo, so FOREIGN_REPO cannot fire
      on a legitimate lane.
   5. **UNKNOWN ROUND IDS FAIL CLOSED (R18).** `plan(..., round_id="r9")` must RAISE/REFUSE until r9 is
      explicitly defined. A warning is NOT sufficient. A convenience fallback may remain for DEVELOPMENT
      utilities, but a production campaign clock never infers its identity, and `DEFAULT_ROUND` may not
      supply a live round's parameters. Tests assert both.
   6. **Reconcile `epochs` with the cap.** The row holds the NOMINAL 12; `plan()` knows nothing about the
      cap. The launcher computes the ACTUAL epoch count from the remaining cap at start time and passes
      it explicitly (`plan()` already accepts `epochs` as an override). A test asserts a launch at
      `T0 + 2h20m` yields `end_ts <= T0 + 14h` and that no epoch boundary falls after it.
      Arithmetic, frozen: build 60 + gate 20 + refine 60 = 2h20m; `min(science_start + 12h, T0 + 15h -
      60min) = T0 + 14h`; 42,000 s = 11.67 epochs of 3600 s. The science clock is ~11 h 40 min and that
      is RULED AND ACCEPTED (R17). Do not "fix" it back to 12.

2. **G7 -- export + cursor.** `bus_export.py`, `epoch.py`.
   Measured: `export()` calls `r.xrange(bus.SWARM)` with NO start argument and opens each file with `"w"`,
   so every boundary re-dumps each stream from the beginning (r7 wrote nine near-identical swarm copies,
   1,295 / 1,296 / 1,303 rows). There is **NO export of the job done stream at all** -- `epoch.py` reads
   DONE only to aggregate `cpu_s`. So `cpu_s`, `wall_s`, `granted_threads`, `segment`, `sha`,
   `predicate_id`, `rows_path` and every telemetry field exist ONLY in a Redis stream capped at
   `maxlen=100_000, approximate=True`, and age out. The bus is not an archive.
   Acceptance:
   1. `pm:jobs:<L>:done` for every lane is exported to committed rows.
   2. Epoch N's export contains ONLY rows with ids after epoch N-1's cursor.
   3. The cursor state is itself durable (committed), so a reproduction can replay the exact partition.
   4. The close produces one full dump per stream, byte-identical to concatenating the per-epoch deltas
      in order. A test asserts this.
   5. Regression: the conductor's r7 cost analysis read `pm:jobs:G:done` from Redis and is therefore
      unreproducible from the repo. It must become reproducible from committed rows alone.

3. **G4 -- close/watch protocol + lint.** `epoch.py`, protocol lint.
   D31 is the CONDUCTOR's defect: A's own close note told lanes to stop their watchers, a lane complied,
   and its gpuq arbiter exited ~1 min after a ruling said to keep it. Measured deaf window 683 s. It ended
   harmlessly by luck, not by a working channel.
   Acceptance:
   1. A protocol lint FAILS on any close sequence that stops the ask watch before workers or shared services.
   2. Stopping a service listed as shared without a confirmation record is flagged by residue or close sweep.
   3. A lane's watcher emits explicit start and stop beacons. **The beacons are EMITTED by P** (worker.py is
      P's file). You own the LINT that checks them. Agree the beacon field names with P on the bus before
      coding; do not edit worker.py.

## Rules

- Every item ships with a regression test AIMED AT THE CLAIM.
- Write every check script as a quoted heredoc (`python - <<'PY' ... PY`). A backtick inside a bash
  double-quoted `python -c` silently DELETED 2 of 12 checks during R8 launch prep and the gate still
  printed PASS. Print `checks run: N` and assert N equals the number you wrote. Read the lines ABOVE a
  verdict, not just the verdict.
- Commits are gated on pytest's OWN rc, never a pipe's (`pytest | tail && commit` gates on tail).
- Push with ops.push. Do NOT start any worker, clock or controller. A does the clock at launch.
- `bus inbox` is NEVER piped -- r7 lost 70 minutes to `bus inbox | tail`.
- Restart nothing of another lane's. Production seats (SFE/Daedalus, Vivarium, wforge) are READ ONLY.

Each iteration: bus beat, bus inbox (unpiped), one item, tests, push, 3-8 lines in journal/Q.md.
Done: post "Q R8 BUILD DONE" to A with shas, the suite rc, and G8/G7/G4 each marked LANDED or NOT LANDED.
