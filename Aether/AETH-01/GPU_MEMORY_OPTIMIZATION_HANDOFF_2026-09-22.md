# AETH-01 GPU Memory-Wall Optimization — Session Handoff (2026-09-22)

Resume point for the memory-wall optimization round. Read this first when the
new session starts.

## Where we are (one line)

Phase 1 done and pushed. Phases 2–6 not yet materialized on disk. No kernel
edits have been made — the optimization analysis so far exists only as reasoning,
not as code.

## Git state

- Branch: `aether/base-role-adopt-2026-09-19`
- `HEAD = 85e6b4c81` (`AETH-01: preserve A40 scaling instrument + baseline
  receipt`) — committed **and pushed** to `origin`.
- Working tree clean except `.gitignore` (unstaged `M`, unrelated to this round).
- Round starting HEAD of record: `ec63af505` (baseline characterization commit).

## Goal (unchanged)

Preserve exact `aeth01.v1` behavior while pushing AGE past the A40 memory wall.
Target: fit **16384²** (268 M sites) on 48 GB by cutting peak per-tick memory
roughly in half (~261 B/site → ~120 B/site).

Hard limits for the paid run: **one pod at a time, ≤ $3 total**, no
pod-creating retries, terminate + verify zero active pods on any anomaly.
Do **not** modify `pod_service.py`. Do **not** redesign AGE physics.

## Real-hardware baseline (A40 48 GB, from RUNPOD_SCALE_RECEIPT_2026-09-22.md)

- Canary: **300/300 PASS**, backend `cupy`.
- Largest lattice: **8192²** (67.1 M sites) @ **3.1615 s/tick**,
  **21.23 M sites/sec**, **~16.3 GB** used.
- **16384² → OOM** (first limiting boundary; memory, not compute/time).
- Footprint ≈ **~261 B/site** of used pool vs ~5 B/site of real state.
- Baseline digests (numpy-fallback == A40 cupy) for 16..2048 are in the receipt
  table — these are the falsification oracle for the optimized kernel.

## Phase status

| Phase | State | Notes |
|------:|:------|:------|
| 1 Preserve instrument + baseline commit | **DONE** | committed 85e6b4c81, pushed |
| 2 Profile memory amplification | analysis only, **not written down** | see accounting below |
| 3 Optimize kernel (semantics frozen) | **NOT STARTED** | no edits to either file yet |
| 4 Falsification (local differential + digest parity) | not started | |
| 5 Bounded A40 RunPod run of optimized kernel | not started | |
| 6 Report + disposition | not started | doc name below |

## Phase 2 analysis (captured before session restart — NOT yet validated)

Approximate peak bytes/site in `gpu_step`, dominated by full-lattice int64/uint64
temporaries. Largest reducible allocations identified:

- Coordinate grids via `meshgrid` materialize full H×W int64 (16 B/site
  persistent). → build packed coords by broadcasting thin 1-D row/col reshapes
  through `pack_coords_vec` (no full meshgrid).
- Neighbor gathers use fancy-index int64 arrays. → replace with `np.roll`
  (bit-exact toroidal permutation, no index arrays materialized). Applies to the
  5 slot arrays (active, direction, target_field, value, packed).
- `direction`, `target_field`, template fields (opcode/arg0/arg1/payload) all fit
  in **uint8**; `value`/`n_value`/`best_value`/`transfer_amt` fit in **int16**
  (range −255..255). Energy stays int64 for safe `total_energy` sum.
- Arbitration `mix64_vec` uint64 temporaries (~40 B/site transient) are the
  largest remaining hotspot; low-risk gain is marginal — leave `mix64_vec`
  untouched.

Estimated optimized peak ≈ **~118 B/site** → 16384² ≈ ~31.6 GB (fits 48 GB).

## Critical constraints for Phase 3 (why this is delicate)

- Two files MUST stay AST-identical (enforced by
  `Aether/test/test_aeth01_canary_parity.py`), apart from the backend shim and
  the dropped annotations:
  - `Aether/runpod/aeth01_canary/aeth01_gpu_kernel.py` (bundled)
  - `Aether/test/reference/gpu_aeth01.py` (reference)
- Preserve the annotated helper signatures the parity test allowlists. `mix64_vec`
  / `pack_coords_vec` keep bodies; `arbitration_priority_vec`, `mu_vec`, `rho_vec`
  carry only a return annotation (params unannotated → safe to change param list).
- No new module-level statements (would break AST match). Comments/docstrings are
  stripped in comparison, so they may differ between files.
- Every physics statement must be written **identically** in both files.

## Immediate next steps (new session)

1. Mark Phase 1 task `[x]`, Phase 2 `[/]`.
2. Read the two kernel files + `test_aeth01_canary_parity.py` fresh; re-verify the
   Phase 2 allocation accounting against the actual current code before editing.
3. Implement Phase 3 edits identically in both files.
4. Phase 4: run `pytest Aether/test/test_aeth01_gpu_differential.py
   test_aeth01_canary_parity.py test_aeth01_properties.py` and re-check the
   numpy-backend digests for 16..2048 against the receipt table. Any mismatch =
   `SEMANTIC_PARITY_FAILURE`, stop.
5. Phase 5: update orchestrator per-file checksums, one pod ≤ $3, sizes
   256..16384. Terminate + verify + reconcile.
6. Phase 6: write `Aether/AETH-01/GPU_MEMORY_OPTIMIZATION_01_2026-09-22.md` with
   final disposition (`MEMORY_WALL_MOVED` / `NO_MATERIAL_GAIN` /
   `SEMANTIC_PARITY_FAILURE`). If `MEMORY_WALL_MOVED`, stop.

## Key files

- `Aether/runpod/aeth01_canary/aeth01_gpu_kernel.py` — bundled kernel (edit here).
- `Aether/test/reference/gpu_aeth01.py` — reference kernel (mirror edits).
- `Aether/test/test_aeth01_canary_parity.py` — AST parity enforcement.
- `Aether/runpod/aeth01_canary/aeth01_bench.py` / `aeth01_bench_server.py` /
  `aeth01_scale_orchestrate.py` — preserved scaling instrument.
- `Aether/AETH-01/RUNPOD_SCALE_RECEIPT_2026-09-22.md` — baseline + digest oracle.
