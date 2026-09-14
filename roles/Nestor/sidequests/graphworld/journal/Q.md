# Lane Q journal (Nestor-Q[m1-b67b3f28], NSIGHT TELEMETRY MVP, axis N2)

## 2026-09-14 iteration 1 -- Q1 capture smoke + Blackwell version check (REFUSAL)

Boot: ff to c70c3c2b2; comms boot, PM_TAG m1-b67b3f28, PM_LANE Q, bus hello.
A's core contract (1789425755152-0) sets Q to 1 thread, so
OMP=NUMBA=torch=1 (it overrides the boot prompt's 2). Own venv
C:/Users/jcrai/lab/nv-venv-q (uv, py3.12): numpy 2.5.3, numba 0.67.0,
torch 2.11.0+cu128; cuda available, cc (12, 0).

Predicate posted before the recorded run (1789426335593-0), with the
exploratory probes of 18:45-18:50 disclosed. Result = the predicted
REFUSAL (prior 0.9). Rows ab777f142:
- control_torch ok: the target itself works;
- nsys 2024.4.2 refused_admin even on `cmd /c echo` with `-t none -s none`.
  The refusal is GPU-independent, so "does nsys support Blackwell" is untested;
- ncu 2024.3.0 cuda_modules_failed and the target crashed (0xC0000005).
  NVIDIA's notes put Blackwell support at Nsight Compute 2024.4;
- the fallback is dead too: torch's bundled CUPTI 2025.1.1 returns
  CUPTI_ERROR_INVALID_DEVICE with 0 CUDA events.
The B6 fused rollout was not probed. It is a numba CPU kernel with no CUDA
context: ncu has nothing to attach to, and nsys CPU tracing is the admin
path that is refused.

Code: primordial/nv/telemetry/smoke.py. classify() turns exit code + tool
text into a verdict, with 7 tests on the captured strings. README there
holds the table and the unblock options. Suite: 36 passed.

Open / next:
- Q2 try Nsight Compute >= 2024.4 in user space (conda package
  nvidia::nsight-compute, own prefix, no admin). If it captures, parse
  kernel share / H2D-D2H bytes / peak memory from its report.
- Operator ask: one elevated nsys capture, or "GPU perf counters: all users".
  Posted to A; the lane does not elevate itself.
- The parser + cheat (host sleep / extra device copy) wait on any working
  capture path.

## 2026-09-14 iteration 2 -- Q2 user-space Nsight Compute (operator: "Try c")

Unpacked nvidia::nsight-compute .conda packages into C:/Users/jcrai/lab/ncu-user
with no admin (sha256 in README). Predicate 1789426652019-0, amended to
1789426740978-0 before the second tool was run.
- ncu 2026.2.1: "Cuda driver is not compatible with Nsight Compute" and the
  target crashed. Driver 576.88 is too old. Row Q2-ncu-2026-2-1 reads
  target_crashed because the driver_incompatible verdict was added after
  that row.
- ncu 2025.2.1: connects on cc 12.0 with no crash, then
  ERR_NVGPUCTRPERM (user lacks GPU performance counter access). Row
  Q2b-ncu-2025-2-1 reads failed; perm_gpu_counters was added after it.
Verdict: REFUSAL. The Blackwell and version question is settled (2025.2.1 loads),
and the one blocker left is the Windows counter permission, an operator
admin setting (option b). Classifier +2 verdicts, +2 tests. smoke.py now
takes --ncu/--exp, and binary reports go to lab/pm-data, not git.
Next, when the operator enables counters: rerun Q2b; if ok -> Q3 parser
(kernel share, H2D/D2H bytes, peak mem) on the torch forward.

## 2026-09-14 iteration 3 -- EPOCH 1 posted; integrated; Q3/Q3b unprivileged features (PASS)

A (1789426824366-0): the operator is on mobile. The counter toggle is queued, so
finish N2 unprivileged and mark counter features BLOCKED. Integration: rebased
twice. The first suite run after the rebase hit A's transient test_fabric_hygiene
syntax error, fixed upstream in fb15cc3a2. Pushed ff to the integration branch:
33d837b82 (verified ancestor).
unpriv.py: exact dispatch-level H2D/D2H bytes, per-op synchronized timing,
kernel_share, peak memory, memory_bound, dmon.
MISTAKE: Q3 ran before its predicate was posted. It is disclosed in the Q3b
predicate and not used. It also exposed a first-use artifact that reads like a
false host stall (997 ms, share 0), fixed by warming up.
Q3b (predicate 1789427122926-0, 8 reps x 3 arms, lease held, lease_lost 0):
judge_q3b gives PASS. Copy cheat 8/8 exact +147456 bytes, sleep cheat 8/8, no false
stall. The memory_bound flag is unstable here and not trusted.
Open: Q4 B6 fused rollout host-only row plus aborted-status refusal rows (A asked
for status aborted on Q1/Q2 evidence); Q2b rerun on 'Q2b go'.
