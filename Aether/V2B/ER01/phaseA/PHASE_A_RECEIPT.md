# ER01 Phase A receipt: M2 handoff and conformance (2026-10-05)

Order: roles/Aether/prompts/2026-10-05_er01 (AETH-V2B-ER01), section 0 and section 10.
Seat instance: Aether[m2-95eba442] on SPECTREX5 (M2). Worktree D:/Prometheus-worktrees/aether-m2,
branch aether/mwo0001-2026-09-28, base 05a46d2af (BUCKKEEP handoff SHA; writer transfer 96f84c1a7).

## Environment
- GPU: NVIDIA GeForce RTX 5060 Ti, 16311 MiB. Driver reports CUDA 12.8+.
- Python 3.14.4 (system). numpy (system), cupy-cuda12x 14.2.0 with the [ctk] extra (the plain wheel fails at
  first kernel compile with "Failed to find CUDA headers"; the [ctk] extra supplies them), torch 2.11.0+cu128
  (not used by ER01). hypothesis installed for the property tests.
- CUDA_PATH is unset. CuPy warns "CUDA path could not be detected" and then works via the ctk wheels.

## Checks (order section 0, items 1-6)

| # | check | result |
|---|---|---|
| 1 | repository/worktree continuity | PASS: worktree at origin/aether/mwo0001-2026-09-28 = 05a46d2af, clean |
| 2 | Aether test suite | PASS with 2 non-physics failures: 1426 passed, 5 skipped. (a) terminology audit: 35 deprecated-term hits in V2-B/AETH-03 docs committed before the handoff ("lineage", "survive"); pre-existing on the branch, not host-dependent. (b) large-artifact test: `ValueError: path is on mount 'C:', start on mount 'D:'` because pytest basetemp was on C: and the repo on D:; re-run with basetemp on D: passes (2/2). |
| 3 | reproduce a known result | PASS: `aeth02_falsifiers.py control` (B_balanced, 256^2, 2500 ticks, historical seeds) reproduces 41 of 44 committed values in AETH-01/evidence/2026-09-24_aeth02_falsifiers/falsifiers_256.json bit-for-bit (activity_density 0.1917266845703125, energy_gini, entropy, change_rate, edge_fraction, ...). The 3 that differ are one metric, contested_of_edges (observed, reference, relative_error), whose definition and reference constant were changed in code after that evidence was written. Instrument drift, not physics. |
| 3b | the ~92% figure | `aeth02_falsifiers.py h1b` reproduces frozen_fraction_all_sites = 0.9259185791015625 (256^2, warmup 2500, window 64). The AETH-02 closing report quotes 0.923 with no committed artifact; the committed lattice_size_scan.log gives 0.9219-0.9252 at 128-384^2 (900 ticks). 0.926 lies in that spread. Recorded as a provenance gap in the historical record (the 0.923 cannot be regenerated as quoted), not as a continuity failure. Flight 1 adds an exact cell for it (cont_R0P1_hist). |
| 4 | CUDA/CuPy on the 5060 Ti | PASS: cupy 14.2.0 sees the device; kernels compile and run. |
| 5 | CPU/GPU conformance on the ER01 path | PASS: er01_conformance.py, n=64, 300 ticks, all 4 regimes x 2 perturbation arms: CuPy kernel (runpod/aeth01_canary/aeth01_gpu_kernel.py) vs independent NumPy text (test/reference/gpu_aeth01.py) give identical state digests at 31 checkpoints each AND identical measurement output (series + late window). phaseA/conformance_n64_t300.json. |
| 6 | Thread/Campaign state | read: Aether/V2B/CAMPAIGN_STATE.json, TEST-3 RESULT + OPERATOR_REVIEW, ops/campaigns/C-002 E-008..E-012 in WORK_STATE. |

## Memory accounting (single process, R0 P0, 300 ticks)
| n | ms/tick | CuPy pool | host RSS |
|---|---|---|---|
| 512 | 16.0 | 60 MiB | 403 MiB |
| 1024 | 17.3 | 248 MiB | 401 MiB |

The kernel is launch-bound at these sizes (per-tick time barely depends on area), so throughput comes from running
several worlds concurrently. Flight 1 measures that.

## Minimum runner changes
None to the kernel. New ER01 files only: er01_run.py (one unit; regime table; observables), er01_conformance.py,
er01_flight.py (concurrent driver, resume, wall cap, not_before guard). The kernel already takes write cost,
maintenance, replenishment numerator/amount and perturbation numerator as run parameters.
