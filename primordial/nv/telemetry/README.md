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

## Q3 / Q3b unprivileged features -- PASS (conductor direction 1789426824366-0)

unpriv.py measures a region with no GPU-counter access. It counts H2D/D2H bytes
exactly at the aten dispatch, times each CUDA op with a synchronize, and also records
kernel_share, peak memory from torch.cuda, a memory_bound flag, and nvidia-smi dmon
utilisation. Counter-derived features are BLOCKED(ERR_NVGPUCTRPERM).
The workload is a torch linear-brain forward, 4096 x 9 -> 16.

- Q3 (rows becadb8c0 era, 5 reps) ran WITHOUT a predicate, which breaks rule 5.
  It is disclosed and not used for the verdict. It also showed an artifact:
  honest rep0 took 997 ms with share 0.000, which is first-use cost and reads as a
  false host stall. Fix: warm measure() before the lease, and let dmon settle.
- Q3b (predicate 1789427122926-0; rows file Q3b-unpriv-features.jsonl, whose
  commit message reuses the exp id Q3-unpriv-features; 8 reps x 3 arms under the
  GPU lease): judge_q3b.py gives **PASS**. copy_caught 8/8
  (h2d +147456 bytes exactly), sleep_caught 8/8 (share 0.29 -> 0.008, +50 ms,
  bytes equal), honest_false_stall 0, lease_lost 0.
- Caveat: memory_bound is unstable on this tiny, transfer-heavy region. It flips
  in 1/8 copy-cheat reps and 7/8 sleep reps. It is reported but not trusted as a discriminator.
- Not done: a B6 fused rollout row. B6 is a CPU numba kernel, so its GPU features
  are trivially zero. It gets a wall/host-only row next.

## Q4 B6 fused rollout row + aborted refusal rows -- PASS (predicate 1789427597891-0, rows f436c6ba8)

- B6b fused linear, world 4, P=128, 8 train seeds, metered by unpriv.measure:
  h2d = d2h = cuda ops = peak memory = 0 for the CPU numba kernel. Fitness and
  cells == E7.rollout 128/128 under the meter. A host sleep adds +50.5 ms of wall
  (3.0 -> 53.5 ms).
- Six refusal rows are re-filed with status aborted (nsys x2, ncu 2024.3, CUPTI,
  ncu 2026.2.1, ncu 2025.2.1). They are reclassified by today's classify(),
  which A asked for.
  Defect: stderr_first is empty on the three ncu rows because ncu writes to stdout.
  The verdicts are correct, since classify reads both streams. Fixed in code
  afterwards; the committed rows were not rewritten.

## Package Q acceptance (DELEGATION_BRIEFS_R3_R6.md sQ)

| item | state |
|---|---|
| ncu/nsys capture of one B6 fused rollout and one torch GPU forward, or a documented refusal naming the first cc 12.0 version | REFUSAL documented: nsys needs admin. ncu first supports Blackwell in 2024.4. ncu 2025.2.1 loads but is blocked by ERR_NVGPUCTRPERM. ncu 2026.2.1 needs a newer driver |
| parser: kernel time share, H2D/D2H bytes, peak memory, memory-bound flag -> engineering rows | DONE unprivileged (Q3b, Q4). memory_bound is unstable. Counter-derived features are BLOCKED(ERR_NVGPUCTRPERM) |
| cheat: injected host sleep or extra device copy moves the right feature | DONE: copy 8/8 exact bytes, sleep 8/8 (Q3b). Sleep on B6 (Q4) |

GREEN with BLOCKED counter features. Reopen when the operator enables GPU
counters for all users: `smoke.py --only control_torch,ncu_torch --ncu <2025.2.1 ncu.exe>`
(A posts 'Q2b go').

What would unblock capture (operator decisions, not taken by the lane):
1. nsys: one elevated capture (admin shell), or a newer nsys that does not
   abort on the Reflex ETW provider (unverified).
2. ncu: Nsight Compute >= 2024.4 (system install, or the user-space conda
   package `nvidia::nsight-compute`, which Q can try in its own prefix).
3. CUPTI INVALID_DEVICE also hit the 2025.1.1 CUPTI. It may be the Windows
   GPU performance-counter permission (NVIDIA Control Panel: "Allow access
   to GPU performance counters to all users"). This is untested.
