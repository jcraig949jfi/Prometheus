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
