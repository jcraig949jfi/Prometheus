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
