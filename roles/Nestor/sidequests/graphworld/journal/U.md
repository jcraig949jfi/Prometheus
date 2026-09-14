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
