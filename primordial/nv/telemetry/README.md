# N2 telemetry (lane Q)

Goal (DELEGATION_BRIEFS_R3_R6.md sQ): hardware telemetry as engineering
descriptors, not fitness.

## Q1 capture smoke -- REFUSAL (2026-09-14, Nestor-Q[m1-b67b3f28])

Host SKULLPORT: RTX 5060 Ti (cc 12.0), driver 576.88, Windows 11, session
NOT elevated. Rows: primordial/ledger/rows/Q/Q1-capture-smoke.jsonl
(ab777f142). Predicate: bus 1789426335593-0. Code: smoke.py (`classify` is
the verdict).

| probe | rc | verdict | what it means |
|---|---|---|---|
| control_torch | 0 | ok | the torch CUDA target runs on cc 12.0 without a profiler |
| nsys_trivial (`-t none -s none` on `cmd /c echo`) | 1 | refused_admin | nsys 2024.4.2 exits with no report for ANY target when not elevated: `ReflexStatsTraceLoggingProvider provider requires administrator privileges`. GPU-independent |
| nsys_cuda_torch | 1 | refused_admin | same refusal; the CUDA trace was never reached |
| ncu_torch | 0xC0000005 | cuda_modules_failed | ncu 2024.3.0: `Failed to load Nsight Compute CUDA modules`, then the target crashes |
| cupti_torch (torch 2.11 cu128, bundled cupti64_2025.1.1) | 0 | cupti_invalid_device | `CUPTI_ERROR_INVALID_DEVICE (2)`: zero CUDA events, so torch.profiler is no fallback |

First versions that name Blackwell (NVIDIA release notes, read 2026-09-14):
- Nsight Compute: **2024.4** ("Added support for the Blackwell
  architecture."). The installed 2024.3.0 predates it.
- Nsight Systems: no release note names Blackwell. The 2024.4.2 failure
  here is the non-admin refusal, so the GPU check is untested.

## Q2 user-space Nsight Compute (operator chose option c) -- blocked on GPU counter permission

Packages from the nvidia conda channel, unpacked to C:/Users/jcrai/lab/ncu-user with no admin.
Predicates: bus 1789426652019-0, then 1789426740978-0 (amended).

| ncu | package sha256 | rc | verdict | stderr (verbatim) |
|---|---|---|---|---|
| 2026.2.1.0 | 4eab2e47...2e0a2d03 | 0xC0000005 | driver_incompatible (the row reads target_crashed, recorded before this verdict existed) | `Cuda driver is not compatible with Nsight Compute.` |
| 2025.2.1.0 | 996128b4...14c5e41a | 1 | perm_gpu_counters (the row reads failed, same reason) | `ERR_NVGPUCTRPERM - The user does not have permission to access NVIDIA GPU Performance Counters on the target device 0.` |

ncu 2025.2.1 connects to the process on cc 12.0, the target runs to completion,
and no report is written. Driver 576.88 / CUDA 12.9 is too old for ncu 2026.2.
**The only blocker left is the counter permission**
(https://developer.nvidia.com/ERR_NVGPUCTRPERM): NVIDIA Control Panel ->
Desktop -> Enable Developer Settings -> Developer -> Manage GPU Performance
Counters -> "Allow access to the GPU performance counters to all users". This
needs admin once. The same permission is the likely cause of torch CUPTI
INVALID_DEVICE (untested).

What would unblock capture (operator decisions, not taken by the lane):
1. nsys: one elevated capture (admin shell), or a newer nsys that does not
   abort on the Reflex ETW provider (unverified).
2. ncu: Nsight Compute >= 2024.4 (system install, or the user-space conda
   package `nvidia::nsight-compute`, which Q can try in its own prefix).
3. CUPTI INVALID_DEVICE also hit the 2025.1.1 CUPTI. It may be the Windows
   GPU performance-counter permission (NVIDIA Control Panel: "Allow access
   to GPU performance counters to all users"). This is untested.
