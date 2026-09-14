# Nestor-W journal: N3 Warp MVP (builder W)

Instance W[m1-b83a86fc], model claude-opus-5, worktree nestor-bld-w, branch
nestor/bld-w-2026-09-14. Brief: DELEGATION_BRIEFS_R3_R6.md s0 + sW; backlog N3.
Venv C:/Users/jcrai/lab/nv-venv-w (uv, not a site-packages clone): warp-lang 1.17.0,
numpy 2.5.3, numba 0.67.0, pytest, redis. Threads: 1 (conductor budget contract
1789425755152-0 overrides the boot prompt's 2).

## 2026-09-14 epoch 1, iteration 1 -- W1 smoke + B world step in Warp, exact vs wforge (PASS)

Smoke (primordial/nv/warp/smoke.py): Warp 1.17.0 sees the RTX 5060 Ti as sm_120,
CUDA toolkit 12.9 / driver 12.9. The wforge xorshift64* step (uint64 wraparound) on
cpu and cuda:0 equals Python big-int arithmetic, 8 rounds x 4096 states.

Kernel (primordial/nv/warp/world.py): nb_world.run_all semantics line for line, one
Warp kernel over envs, advancing ticks [t0, t1) with state in device arrays, so
run(t, t+1) is one world tick. Warp gotchas met: range() takes int32 only; a bool
mutated in a loop must be declared bool(False); % truncates (all operands are
non-negative in wforge worlds, stated in the header).

Oracle (primordial/nv/warp/oracle.py), B1's episodes (40 worlds x 12 envs, random
actions, abstain 0.6), trace hash + final charge + done tick vs the wforge Encounter:

    form                        exact     trace_eq  charge_eq  worlds failing
    warp cpu                    480/480   480       480        0
    warp cuda:0                 480/480   480       480        0
    warp cuda:0, 1 tick/launch  480/480   480       480        0
    warp cpu  skip_lin          0/480     0         453        40/40
    warp cuda skip_lin          0/480     0         453        40/40

skip_lin leaves final charge equal in 27/480 episodes: only the trace hash catches
those (same as E4). Rows: primordial/ledger/rows/W/W1-warp-world-oracle-*.jsonl
(RowWriter commits 934973c7f..3a1132255). Code 6701b7984.

Tests: primordial/nv/warp/tests (nv-venv-w; importorskip warp) 8 passed;
primordial/tests (gw-venv) 43 passed after rebasing onto F's O3 + O5.

Scope note: this is the OPEN-LOOP world step (B1). The oracle does not yet replay
E4/E7 brain-recorded actions; B1 random actions cover delay, stochastic kicks,
regime flips and two-slot worlds (tested).

## 2026-09-14 epoch 1, iteration 2 -- W2 crossover harness (predicate posted)

Predicate 1789426347225-0 posted before any timing. Harness
primordial/nv/warp/crossover.py: numba (nb_world.run_all, 1 thread) vs warp_cpu vs
warp_cuda, n_envs 1..65536, worlds 1-5. Gate per cell: done_tick equal across forms,
charge cpu == cuda, charge == numba's log at n <= 1024. Disclosed deviation from the
predicate text: above n = 1024 numba's final charge is not logged (T x n x R log), so
the numba charge/regs check is skipped there.

Gate v1 FAILED its own cheat test: done_tick + final charge (cpu == cuda == numba)
PASSED a skip_lin Warp kernel at world 4, n = 64. The gate was aimed beside the claim
(the same blind spot W1 measured: charge equal in 27/480 skip_lin episodes). Gate v2
adds (a) 8 sampled envs of the timed Warp encounters, logged inside the timed run,
trace-hash equal to the wforge Encounter, and (b) final registers equal across
devices and vs numba's log. The test that caught v1 stays in the suite.
Tests after v2: primordial/nv/warp/tests 13 passed.

Suite flake (not W's code): primordial/tests/test_o5_gpu_lease.py flushes the shared
redis db 15 at setup and teardown, and every builder runs the suite concurrently.
Four consecutive W runs: 3 failed, 1 failed, 4 failed, 43 passed, with a different
failing set each time. Pushed on the green run; asked F to namespace the test key.

## 2026-09-14 epoch 1, iteration 3 -- W2 crossover table (H1 PASS 4/4 eligible, H2 PASS 5/5)

45 cells (worlds 1-5 x n_envs 1..65536), 5 alternating reps, compile excluded, each
world one process inside bus.gpu_lease. Gate v2 ok 45/45 (wforge hash sample of the
timed kernel, done_tick, charge + regs cpu == cuda, == numba log at n <= 1024). Lease
lost 0/45. INDETERMINATE for speed 8/45: w2 n <= 4096 (nvidia-smi 17% before the
cell) and w5 n = 65536. Rows primordial/ledger/rows/W/W2-warp-numba-crossover.jsonl
(RowWriter commits 6f36bd416, 914ffeba5, 4d088a810, d48ac4ee5, 1e87a9847).

Million slot-steps per second (numba / warp_cpu / warp_cuda), * = INDETERMINATE:

    n_envs     w1 (T128 S1)       w2 (T32 S2)          w3 (T64 S1)        w4 (T64 S1)        w5 (T256 S1)
    1          3.3/0.6/0.2        4.4/1.0/0.4*         1.1/0.2/0.1        4.1/0.7/0.2        4.6/0.7/0.3
    64         20/14/7            39/32/14*            20/14/6            13/9/6             25/19/4
    256        21/23/19           45/48/48*            12/15/21           22/23/24           33/32/14
    1024       19/26/68           46/56/174*           18/24/93           17/21/69           32/34/52
    4096       36/27/228          38/51/623*           32/26/317          27/19/259          52/41/206
    16384      36/26/609          65/53/1763           32/24/846          27/22/664          53/41/650
    65536      36/26/436          65/56/1724           31/26/1131         30/23/451          52/40/940*

Crossover (first n where warp_cuda > numba, VALID cells): w1 1024, w3 256, w4 256
(1.09x, marginal), w5 1024; w2 has no VALID cell below 16384. Peak cuda/numba: w1 16.8x,
w2 27x, w3 36x, w4 24x, w5 12x (VALID).
Verdict vs predicate 1789426347225-0:
- H1 (warp_cuda beats numba at some n <= 4096 in >= 4/5 worlds): PASS, 4/4 eligible
  worlds (w2 INDETERMINATE there, not counted).
- H2 (warp_cpu within 2x of numba at n >= 1024 in >= 4/5): PASS 5/5; warp_cpu is
  0.72-1.36x numba, ahead at n <= 1024-4096, behind at large n.

Qualifications that bound these numbers:
- numba runs at 1 thread (W's budget). B6 ran numba at 3 threads, so this is NOT
  "Warp beats B6"; a threaded numba would move the crossover right.
- B1 random-action episodes die early (mean 20-27 ticks of T 32-256), so the
  kernel mostly skips dead envs; long-lived brain episodes will weigh differently.
- H2D of the action tensor is outside the timed wall (h2d_s in rows): at n = 65536
  it was 37 ms in w1 against 3 ms of kernel. Closed-loop use needs actions made on
  the GPU, or the transfer eats the win.
- cuda throughput FALLS from 16384 to 65536 in w1 and w4 (609 -> 436, 664 -> 451):
  unexplained; candidate is the 0.4 GB int32 action tensor's memory traffic.
  Not investigated.

Package status: both MVP items have rows. Open: the brief says "reuse the E4/E7
world oracle" -- W1 used B1's random-action episodes. W3 = replay brain-recorded
actions (E7 rollout log) through the Warp kernel vs wforge, honest + skip_lin.

Bus 1789426590314-0 (A: abstain-only floor beats every clause A baseline) does not
touch N3: W measures world-kernel exactness and throughput on B1 random-action
episodes, never policy fitness, so no W row is evidence about brains either way. Table runs inside bus.gpu_lease;
a cell is INDETERMINATE for speed if the lease is lost or nvidia-smi showed > 10%
utilisation just before it.
