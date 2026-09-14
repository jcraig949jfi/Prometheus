# Lane U journal (Nestor-U[m1-d0d8a29c], CUDA GRAPHS MVP builder, round 6 axis N5)

Threads: 1 (conductor contract 1789425755152-0 overrides the boot prompt's 2).
Venv: C:/Users/jcrai/lab/nv-venv-u (uv, python 3.12, torch 2.11.0+cu128; cuda available,
capability (12, 0), arch list includes sm_120). Epoch 1 started 18:49.

## 2026-09-14 iteration 1 -- U1 B world step as torch integer ops, exact vs wforge (DONE)

- primordial/nv/cudagraph/world.py: TorchWorld, NpEncounter semantics batched over envs
  (quirks kept: an unaffordable slot is charged 0 but its writes land; stoch draw 2 is the
  value, draw 3 the index). Graph-ready: state updated in place, tick is a 0-d device tensor,
  every per-env/per-tick choice is torch.where or a ring mask, no host sync. uint64 xorshift
  emulated on int64 (masked logical right shift; unsigned mod by sign-bit split).
- primordial/nv/cudagraph/oracle.py: trace hash AND obs hash vs the wforge Encounter, zero
  tolerance, reusing B1's sampler/actions/hashing read-only.
- Oracle, 40 worlds x 12 envs (B1 scale): cpu 480/480 trace, 480/480 obs; cuda 480/480,
  480/480. Rows: C:/Users/jcrai/lab/pm-data/u1/oracle_{cpu,cuda}.jsonl (not committed).
- Cheats on cuda (trace_eq of 480): skip_lin 0, fix_unaffordable 227, no_regime_flip 404,
  stoch_swap 273 -- all caught.
- Tests: test_u1_torch_world.py (8): xorshift + unsigned mod == numpy uint64 on cpu/cuda
  (edge states 1, 2^63, 2^64-1); world == wforge cpu/cuda (16x4); the sample covers delay,
  stoch, regime, corrupt and obs_delay; skip_lin caught cpu/cuda; step+observe run under
  torch.cuda.set_sync_debug_mode("error") (no host sync). nv-venv-u 8 passed; full suite in
  gw-venv 45 passed.
- No timing claims (none taken). Next: U2, brain forward (linear) + codebook decode +
  descriptor counters in torch, fitness and cells == E's rollout / B6 fused on one world.
- Pushed: edb276363, rebased onto integration as 438b2e8ba. O5 GPU lease is on the
  integration branch (F 98f8bf705); timing work will hold bus.gpu_lease.

## 2026-09-14 iteration 2 -- U2 linear closed loop on device == E7.rollout (DONE)

- primordial/nv/cudagraph/rollout.py: TorchRollout (linear family). tick() = float32 linear
  logits -> argmax (first max) -> codebook gather -> E7 descriptor counters on
  alive & ~done slots -> U1 world step -> observe. Fixed shapes, in-place, no host sync:
  the unit U3 captures.
- Exact by construction, not tolerance: E7 takes argmax of np.einsum("nd,nda->na") + b in
  float32; non-optimized einsum accumulates products in feature order from zero, then adds
  b. The torch forward repeats that op sequence, so logits are BITWISE equal (tested, honest
  and the skip-odd cheat, including negative charge-channel obs). Note C's njit row kernel
  starts the sum from b, a different float order.
- E7 comparison (CLI, cuda, 128 genomes = init + 3 mutations, PCG64 [770, world, 0]):
  worlds 4, 1, 3 x {train 8 seeds, held64}: fitness 128/128 and cells 128/128 in all six.
  Rows: C:/Users/jcrai/lab/pm-data/u1/u2_compare_cuda.jsonl (not committed).
- Tests: test_u2_torch_rollout.py (7): logits bitwise == numpy cpu/cuda; world 4 fitness
  and cells == E7 128/128 cpu/cuda; brain cheat and skip_lin each move >= 64/128 genomes;
  tick() under sync_debug_mode("error"). Suite in gw-venv: 65 passed, 1 skipped.
- Limits: genomes are mutated random, not evolved elites (near ties are covered by the
  bitwise logits test, not by elite sampling). sync_debug_mode is a torch prototype that
  misses some syncs; the capture in U3 is the real proof of no host sync.
- Next: U3, capture tick() as a torch CUDA graph (static inputs, graph replay == eager
  bitwise, fitness/cells 128/128), then tt_digits.
- Pushed as 7bd138fe7 on integration. Inbox: conductor confirmed the abstain-only floor
  beats every clause A baseline (clause A on hold). U's acceptance is exactness vs E7 and
  throughput, so it is unaffected; no U number is a science claim about brains.

## 2026-09-14 iteration 3 -- U3 closed-loop tick captured as a CUDA graph (DONE)

- primordial/nv/cudagraph/graph.py: GraphRollout(TorchRollout). Brain forward + action
  decode + counters + world update captured as ONE torch.cuda.CUDAGraph per step
  (ticks_per_graph=1) or a static multi-step graph (K ticks per replay; T % K leftover ticks
  eager). 3 warmup ticks on a side stream, then capture; state restored afterwards by copying
  a fresh eager load into the captured tensors. New genomes/seeds of the same shape are
  copied in (no re-capture); a new shape or brain cheat re-captures.
- rollout.py: tick() now writes obs in place (a captured graph owns that tensor).
- Tests: test_u3_cuda_graph.py (5): K = 1, 7 and whole-horizon: fitness and cells == E7
  128/128 AND all 17 state tensors bitwise == eager after the rollout; reload of new genomes
  + a different seed set into the same graph object == E7 128/128 and differs from the
  previous batch on >= 64 genomes (a stale replay would fail); brain cheat re-captures and
  == E7's cheat rollout 128/128 while moving >= 64 vs honest. Suite in gw-venv: 84 passed,
  1 skipped (O1 live schtasks).
- Still open for the MVP: tt_digits in the graph; VRAM budget table (envs x T in 16 GB);
  throughput vs B6 fused numba under the O5 lease.
- Pushed as dff53e8cf on integration. The conductor's 660ab7f38 broke collection of
  test_fabric_hygiene.py; the integrated tree ran 88 passed with that file ignored, then
  the fix fb15cc3a2 landed and the full suite runs again with PM_LANE=U (own test db 13).

## 2026-09-14 iteration 4 -- U4 tt_digits brain on device, eager and captured (DONE)

- primordial/nv/cudagraph/brains.py: LinearBrain, TTDigitsBrain. Each repeats the float32
  op sequence of E7's numpy forward (einsum sums from zero in index order; tt: digits of
  obs & 0xFFFF MSB first, per core v = sum_r v_r G[c, digit][r], v /= max(max|v|, 1e-30),
  logits = sum_r v_r Wo[r]; the cheat skips odd cores), so logits are bitwise equal. G is
  indexed per env by genome id, not replicated per env.
- rollout.py and graph.py are family-generic: TorchRollout.state() lists every captured
  tensor, including the brain's; GraphRollout copies a fresh load through it.
- E7 comparison (CLI, cuda, 128 genomes): tt_digits, worlds 4, 1, 3 x {train, held64}:
  fitness 128/128 and cells 128/128 in all six. Rows:
  C:/Users/jcrai/lab/pm-data/u1/u4_compare_cuda.jsonl.
- Tests: test_u4_tt_digits.py (5): logits bitwise == numpy cpu/cuda (honest and cheat,
  negative obs); rollout == E7 128/128 cpu/cuda; CUDA graph (K=1) == E7 128/128, all state
  bitwise == eager, cheat graph == E7's cheat rollout and moves >= 64. U2/U3 still pass.
  Suite in gw-venv (PM_LANE=U): 114 passed, 1 skipped (O1 live schtasks).
- MVP acceptance 1 and 2 met: linear then tt_digits captured as one graph per step (or a
  static multi-step graph), fitness and cells == E7 128/128 on worlds 4/1/3. Open: U5 VRAM
  budget table, U6 throughput vs B6 fused numba under the O5 lease.

## 2026-09-14 iteration 5 -- U5 VRAM budget table, U6 throughput vs B6 (leased)

- Harness primordial/nv/cudagraph/bench.py (361b262b6). Rollout gained snapshot/restore/
  replay: the per-env host stream seeding is done once, like B6's constructor; the timed
  unit is device copy of the initial state + T ticks + fitness/cells to host. Unleased dev
  runs first showed the untimed-init asymmetry (graph K=1 == K=T wall, init-dominated) and
  were used only to fix the harness; they are not evidence.
- Predicates posted before the runs (1789427622959-0). Rows: primordial/ledger/rows/U/
  U5-vram-budget.jsonl (20, d28098d51) and U6-throughput-vs-b6.jsonl (6, ceadaecaa); every
  measured row has gpu_lease_lost False, lease holder U; host CPU 21-27% (other lanes), GPU
  1-5% at start. World 4, T = 64, 8 train seeds, P = n_envs / 8.
- U5 VRAM (peak torch allocation of one captured-graph rollout, MiB):

      n_envs        4096   16384   65536   262144
      linear        12.2    49.9   195.8    783.0
      tt_digits     28.9   116.6   462.8   1851.0

  identical for K = 1 and K = 64 in every cell. Budget (linear extrapolation from 65536 and
  262144): linear 3132 B/env, ~5.49M envs in 16 GiB (~5.00M in the free memory);
  tt_digits 7404 B/env, ~2.32M (~2.08M). Measured up to 262144 envs only.
- U6 median wall of 5 rollouts (s); B6 numba at 1 thread (the lane budget):

      family     n_envs  eager    graph_k1  graph_kT  b6_numba  graph_k1 vs b6
      linear       1024  0.208    0.0163    0.0163    0.0027    0.17x
      linear       8192  0.316    0.0186    0.0189    0.0218    1.17x
      linear      65536  0.168    0.0717    0.0720    0.1705    2.38x
      tt_digits    1024  0.902    0.0488    0.0500    0.0087    0.18x
      tt_digits    8192  0.533    0.0559    0.0565    0.0731    1.31x
      tt_digits   65536  0.522    0.1596    0.1585    0.5901    3.70x

  every path exact vs B6 and eager in all 6 cells (including the timed restore path).
- Predicate scoring: U5-P1 (tt_digits >= 1M envs in 16 GiB, prior 0.7) PASS, 2.32M
  (extrapolated). U5-P2 (K=T peak <= 1.10 x K=1, prior 0.8) PASS, 1.00 -- but the byte-equal
  peaks say the peak is state + snapshot copy, so this does not show long graphs are free
  in general. U6-P1 (exact 6/6, prior 0.95) PASS. U6-P2 (graph_k1 >= B6 at 65536, prior
  0.8) PASS, 2.38x / 3.70x, AGAINST B6 HELD TO 1 THREAD. U6-P3 (eager/graph_k1 >= 5 in all
  cells, prior 0.9) FAIL 4/6: 12.7x, 17.0x, 2.34x (linear 65536), 18.5x, 9.5x, 3.27x
  (tt_digits 65536) -- at large batch eager's per-kernel launch cost is amortized.
- Reading: the graph path is flat in n_envs up to ~8k (launch-bound, ~0.25-0.8 ms/tick)
  and loses to single-core B6 below ~4k envs. B6 stops envs at their done tick; the torch
  paths step every env for T ticks.
- U6b WITHDRAWN, not run: predicate 1789427870219-0 (graph_k1 >= B6 at 8 numba threads,
  65536 envs, prior 0.35) with burst 1789427870515-0. The run waited on the GPU lease held
  by T (N4 timing, until ~19:30) and was killed at the 280 s timeout with no rows. The burst
  window then expired. No result either way; the 1-thread comparison above is the only
  B6 speed evidence. Carry-forward: rerun U6b under a fresh burst when the lease is free.
- N5 MVP package: all four acceptance items met (graph capture linear then tt_digits;
  fitness and cells == E7 128/128; VRAM budget table; throughput vs B6 under the lease).
  Tests in lane U: 28 (U1 8, U2 7, U3 5, U4 5, U5 3).
