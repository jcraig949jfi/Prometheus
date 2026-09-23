# AETH-01 RunPod Scaling Receipt — 2026-09-22

Real-hardware characterization of the **frozen** `aeth01.v1` GPU kernel
(`Aether/runpod/aeth01_canary/aeth01_gpu_kernel.py`) on a single RunPod A40.
This is the pre-optimization baseline that the memory-wall optimization round
(`GPU_MEMORY_OPTIMIZATION_01_2026-09-22.md`) is measured against. No physics was
changed; this is characterization of the implementation as it stands at
`HEAD = ec63af505`.

## Run identity

- `run_id`: `aeth01-20260922T162452Z-3834e597`
- Starting `HEAD`: `ec63af505b4f1af0af3b0d54317a1ac29e9e975e`
- Pod: `dc21hvohu9f79j` (created, used, terminated — absence independently
  re-confirmed, `ACTIVE_POD_COUNT 0`)
- GPU: **NVIDIA A40, 48 GB**, SECURE cloud, **$0.49/hr**
- Image: `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04`
- On-pod stack: Python 3.11.10, NumPy 2.2.0, CuPy 13.3.0 (`cupy-cuda12x`)
- Boot fix (unchanged `pod_service.py`): `unset RUNPOD_API_KEY
  RUNPOD_API_TOKEN RUNPOD_TOKEN` immediately before `python3 pod_service.py`.

## Canary — PASS

Frozen 300-case CPU-oracle vs GPU-kernel differential corpus, run on the real
GPU before any benchmarking:

- status: **PASS**, backend **cupy**
- cases: **300 / 300** matched, 0 mismatches
- `gpu_kernel_seconds`: 14.746881019324064
- source hashes (frozen): `aeth01_cpu_oracle.py`
  `1b28db2a10a9b9eb112af1a2addb162e63afa7cce214292dbff7401074df5f75`;
  `aeth01_gpu_kernel.py`
  `0b7c89bd35912c82cae9c3baca10d0e56eef3cf72222c9da045026f58c3195e3`;
  `run_canary.py`
  `751d5a20f324cc862e5b1fe29c3c40e11b41a50a040b418f6953ed14ea4b0399`

## Scaling curve (square lattices, doubling)

Fixed benchmark parameters: `SEED=0x1234ABCD`, `WRITE_COST=10`, `MAINT=1`,
`REPL_NUMER=MUT_NUMER=2**31`, `REPL_AMT=5`, 2 warmup + 5 measured ticks per size.
Digest = sha256[:16] of the 5 uint8 fields after 7 ticks.

| size | sites | tick_med (s) | sites/sec | GPU mem used (MB) | parity | digest |
|-----:|------:|-------------:|----------:|------------------:|:------:|:-------|
| 16   | 256        | 0.028436 | 9,002.6      | 270.2    | PASS    | 1000219c591e1595 |
| 32   | 1,024      | 0.030276 | 33,822.7     | 270.2    | PASS    | 9f65f15cb87b630f |
| 64   | 4,096      | 0.029580 | 138,471.2    | 270.2    | PASS    | 3ce333436da923b0 |
| 128  | 16,384     | 0.028844 | 568,018.8    | 274.2    | PASS    | 3ab66c98546a3a95 |
| 256  | 65,536     | 0.029244 | 2,240,989.7  | 286.2    | SKIPPED | 7383c7d828504a30 |
| 512  | 262,144    | 0.028879 | 9,077,435.7  | 334.2    | SKIPPED | a04b1321280b0b97 |
| 1024 | 1,048,576  | 0.053388 | 19,640,637.0 | 526.2    | SKIPPED | 87b8194c84a440d0 |
| 2048 | 4,194,304  | 0.202625 | 20,699,842.4 | 1,298.2  | SKIPPED | f2ad4a9ec9dbac4f |
| 4096 | 16,777,216 | 0.794837 | 21,107,750.6 | 4,382.2  | SKIPPED | 3741cde26ed38979 |
| 8192 | 67,108,864 | 3.161471 | 21,227,101.3 | 16,718.2 | SKIPPED | 2f787e64bf323091 |

Parity ("PASS") = bit-exact agreement with the pure-Python CPU oracle, checked
only where the oracle is practical (≤128). Digests 16..2048 are additionally
reproduced bit-identically by the local NumPy-fallback backend (cross-backend
determinism beyond the canary's 300 cases).

## Boundary

- **Largest successful lattice: 8192 × 8192** (67,108,864 sites).
- **Peak throughput: 21,227,101 sites/sec** (at 8192²).
- **First limiting boundary: GPU OOM at 16384²**
  (`AETH01_BENCH_STOP reason=OOM size=16384 err=OutOfMemoryError`).
- The limit is **memory capacity, not compute and not the 60 s/tick guard**:
  8192² used ~16.3 GB; 16384² (4× the sites) needs ~65 GB > 48 GB.
- Apparent implementation footprint at 8192²: 16,718 MB / 67.1 M sites ≈
  **~261 bytes/site of used pool** (peak transient higher), vs **5 bytes/site**
  of actual AETH-01 state — a large amplification from full-lattice int64/uint64
  temporaries.

## Cost / safety

- Pod wall time: **113 s → ≈ $0.015** (≪ $3 cap).
- One pod only (`dc21hvohu9f79j`); two transient 400/500 create errors each
  reconciled to **0 pods** before retry (no duplicate/concurrent pod).
- Terminated `ACK_204`; absence independently re-confirmed (`ACTIVE_POD_COUNT 0`).
- No secrets on argv or in logs; `pod_service.py` and the kernel unchanged.

## Preserved instrument

Committed alongside this receipt under `Aether/runpod/aeth01_canary/`:

- `aeth01_bench.py` — scaling benchmark (imports the frozen kernel + oracle).
- `aeth01_bench_server.py` — minimal bearer-authed static server for `bench.log`.
- `aeth01_scale_orchestrate.py` — one-pod, terminate-guaranteed, ≤$3 orchestrator
  (adapted to be self-contained: repo-relative sources, `AETH01_COMMIT` /
  GPU overridable via env, per-file checksums computed from the local checkout).
