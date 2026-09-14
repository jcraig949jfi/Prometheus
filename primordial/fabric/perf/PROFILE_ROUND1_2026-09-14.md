# Where round 1's time went (lanes A-E), and what to build or cache

Currency: 2026-09-14 ~13:45, Nestor-A[m1-449a9e76]. Authority: the operator
request, verbatim in roles/Nestor/prompts/2026-09-14_graphworld_swarm/05_OPERATOR_WHERE_DOES_THE_TIME_GO.md.
Measured on the quiesced host. The profiler is `lane_timeprof.py`, next to
this file.

## 1. Session wall clock (transcripts: B 5b2d34d4, C b36900c1, E f333105f, D 5ab220e6, A 918ab2b0)

Method: replay each transcript in time order. While a tool call is open,
the gap is charged to that tool. With no call open, a gap ending in a
model entry is model time; gaps over 15 min are long idle. Parallel calls
are charged once.

    spans 1108 min total; long idle (>15 min gaps) 418 min; attributed 690 min
    model steps (thinking + generation + API)   315.5 min  45.7%
    other: queue ops 204 min, system 83, attach 15  302.0 min  43.8%  (mostly waiting: see 2)
    pytest                                        22.6 min   3.3%
    python runs (foreground)                      22.3 min   3.2%
    git fetch/rebase/push/commit                  12.5 min   1.8%
    bus CLI calls                                  8.0 min   1.2%
    Edit/Write/Read/wsl/other                     < 6 min    <1%

- Model: ~2,900 steps and 7.06 M output tokens over 49 receipts, i.e.
  ~60 steps and ~6.4 model-minutes per receipt.
- Median model step 2.9 s, p90 16 s. Context median 376k tokens, max 890k.
  Median latency by context: <100k 1.7 s, 100-250k 2.8 s, 250-500k 3.3 s,
  >500k 3.5 s. 60% of steps ran above 250k.
- Boot: 23-34 model steps and ~70-74k tokens of context before the first
  bus hello. Paste to hello took 3:45-5:01; paste to first receipt
  15:19-32:40.
- Tools are NOT the bottleneck: git is 0.06-0.34 s per operation
  (preflight hook 0.34 s, fetch 0.27 s), and Edit/Write take ~0.1 s.

## 2. Waiting

- Background experiment jobs: 39 jobs, 280 min, 235 of them Python runs
  (E 214.7 min, longest 66 and 63 min; C 52 min).
- Waits that ended on a task notification: C 26 gaps / 99 min, E 14 / 47 min.
- Loop wakeups requested: B 12 calls / 214 min, C 41 / 986 min, E 19 /
  340 min (fallback timers while jobs ran).
- Operator-side: ~18 min from session open to paste per clone; several
  11-21 min gaps around operator questions.

A lane is mostly either thinking (model) or waiting on one long job. It
seldom has a second experiment queued behind the first.

## 3. Fixed cost per Python process (measured now)

    Redis connect to "localhost" (default host)   10.0 s   vs 127.0.0.1: 15 ms
    numba JIT, B6 fused kernel, first call          6.2 s   warm call: 0.06 s (100x)
      same kernel with cache=True, fresh process    0.32 s  (fitness identical, 517,984)
    FusedRollout.__init__ (128x128 envs)            0.37 s  per construction (6x a warm run)
    import primordial.qd.e10_run                    0.66 s  (numba 0.21, e4_run self 0.19)
    E5.rollout numpy reference, P=128 x 8 seeds     0.15 s

- 18 call sites use `redis.Redis(port=...)` with the default host,
  including every lane E run script and the lane D/E test fixtures. On
  this host "localhost" costs 10 s per connection (IPv6 first, then
  fallback). The same fixtures make up 30 s of the 40 s full test suite
  (six 5 s setups); lane E ran pytest 36 times (18.4 min).
- `_fused` (B6) and the C4 row kernels / C5 forward_fast are njit WITHOUT
  cache=True. Of the 7 njit decorators, 3 are cached (nb_world). Every
  experiment process recompiles.
- E8/E10 build a new FusedRollout inside score functions
  (`closed_score` constructs one per call), each re-seeding per-env
  streams in Python.

A small experiment in a fresh process pays ~17 s of fixed overhead (10 s
connect + 6.2 s JIT + ~0.7 s import/init) before any science. Under a
5-10 min task TTL that is 3-6% of the budget per attempt, on every attempt.

## 4. What to build or cache (ranked by measured payoff per unit of work)

1. 127.0.0.1 everywhere: a `primordial.core` connect helper, with the 18
   call sites switched to it. Saves 10 s per process and ~30 s per test
   run. One-line changes, but they sit in lane D and E directories.
2. `cache=True` on every njit kernel (B6 `_fused`, C4 row kernels, C5
   forward kernels), plus a warm-up script run once per host after a pull.
   Saves ~6 s per process per kernel; measured 6.33 -> 0.32 s. Lane B/C
   directories.
3. A warm experiment worker: one long-lived Python process per lane that
   holds imported modules, compiled kernels, a Redis pool, and in-memory
   caches of world/seed structures (FusedRollout init arrays keyed by
   (world id, seeds, family)). Experiments arrive as job specs on a Redis
   Stream (the predicate from R1) and return rows on another stream. This
   is what Streams are for here: it removes all fixed per-process cost,
   lets a lane queue many small variants instead of waiting on one job,
   and gives the task TTL (T1) a clean kill target. Lane A (fabric).
4. Precomputed seed/world tables: per-env stream states and init registers
   are pure functions of (world id, seed). Build them once as packed arrays
   (Redis string or np.memmap) and share them across lanes and processes.
   Saves ~0.37 s per construction, and more at higher P x k.
5. Cut model steps per receipt (the largest cost, ~6.4 model-min each):
   - a generic runner + receipt builder driven by predicates and rows (L3),
     instead of each lane writing run/score/receipt scripts per experiment
     (lane C has 21 c*_ experiment scripts, lane E 14 e*_ scripts, counted);
   - a compact generated boot pack instead of ~70k tokens of doc reading;
   - a fresh context per epoch with state in the ledger (step latency
     halves from >500k to <100k context).
6. Tests: fixtures on 127.0.0.1, and a `-m fast` marker for the loop's
   pre-commit check.

Not measured, not claimed: Lua/C rewrites of the world step. B1 already
measured Lua per tick at ~1.4-1.7 ms per call and numba fastest in every
cell, so the in-memory wins above come before any new substrate. Where
Lua and Redis earn their place is the job/result fabric and the shared
caches (3, 4), not the inner loop.

## 5. Ownership

Items 1, 2 and 6 edit lane B, C, D and E files. The swarm rule is that
nobody edits another lane's directory, so they go to the owners as
bounties or asks, unless the operator authorizes the conductor to land
them while the lanes are quiesced. Items 3 and 4 are lane A (fabric).
