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
failing set each time. Pushed on the green run; asked F to namespace the test key. Table runs inside bus.gpu_lease;
a cell is INDETERMINATE for speed if the lease is lost or nvidia-smi showed > 10%
utilisation just before it.
