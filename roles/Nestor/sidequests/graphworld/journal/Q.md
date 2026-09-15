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

## 2026-09-14 iteration 4 -- Q4 (PASS); package green; PAUSE

Predicate 1789427597891-0 posted before the run. Rows f436c6ba8.
B6b fused linear w4 P=128: every GPU feature is exactly 0, the metered rollout ==
E7.rollout 128/128, and a host sleep adds +50.5 ms. Six refusal rows are re-filed
as aborted and reclassified by code. Defect: stderr_first is empty for the three
ncu rows (ncu writes to stdout). The verdicts are unaffected. Fixed in code, and
the committed rows were left as they are.
Acceptance check (README table): the capture is a documented REFUSAL,
unprivileged features are DONE, and the cheats are DONE. Counter features are
BLOCKED(ERR_NVGPUCTRPERM). Package green -> pause per s0.8. Reopen trigger:
A posts 'Q2b go' after the operator's counter toggle.
Lessons: (1) I ran Q3 before its predicate. Posting the claim is now the first
tool call of each item. (2) A first-use cost inside a timed region reads as a
false host stall. Warm the meter first. (3) Rebasing right before a busy
integration push raced twice. Re-fetch and push immediately after the suite.

## 2026-09-14 19:33 -- Q2c after the operator's registry change (INDETERMINATE)

The Control Panel has no "Enable Developer Settings" on this driver (the setting moved to the
NVIDIA App). The operator set RmProfilingAdminOnly=0 from an admin shell in both NVTweak keys
(verified). Predicate 1789428782661-0. Last boot 2026-09-11 13:33, so there has been no reboot.
ncu 2025.2.1 is still perm_gpu_counters and CUPTI is still invalid_device. Per the predicate
that is INDETERMINATE (driver not reloaded). Rows Q2c-ncu-after-regkey. Next: reboot
(A schedules it, since it stops the swarm) -> Q2d, the same probe.

## 2026-09-14 20:03-20:35 -- Q2d after the reboot (PASS; counters still empty) -- Nestor-Q[m1-b5b65cc2], new session

Boot: ff no-op at d97020e12; comms boot -> PM_TAG m1-b5b65cc2; bus hello; inbox had A's 'Q2d go'
(1789430520491-0). Last boot 19:55, RmProfilingAdminOnly=0 verified.
Predicate 1789430655670-0 posted first. Ran smoke.py --only control_torch,ncu_torch,cupti_torch with the
user-space ncu 2025.2.1 under the O5 lease (released). Rows 84a42fae0 (rebased), receipt 1789431111818-0.
- control_torch ok; ncu_torch rc 0, no ERR_NVGPUCTRPERM, 3 kernels x 9 passes, 20 MB report.
- DEFECT: the row verdict reads 'failed'. smoke.py required a '.ncu' file and ncu 2025 writes '.ncu-rep'
  (my predicate text also said '.ncu'). Fixed by report_ok + judge_capture with tests. The committed rows are
  re-judged by code, not rewritten: Q2d PASS, Q2c REFUSAL:perm_gpu_counters.
- Loaded the report with NVIDIA's extras/python/ncu_report (py3.12 pyd loads). 66 of 418 non-attribute
  metrics per kernel are filled, all launch config/occupancy/numa. gpu__time_duration, sm__cycles_elapsed
  and throughput have 0 instances. The capture works; counter-derived N2 features are still NOT measured.
- CUPTI side readout is still INVALID_DEVICE, so its cause was not the counter permission (claim WRONG).
- ncu_b6 was not run: B6 is a CPU numba kernel with no CUDA context, and Q4 already has its GPU features at 0.
- Integration: A's replay fix 052aeeb84 had landed. Before the rebase, H's test failed on receipts 42 vs 37.
  After the rebase the suite is 155 passed, pushed ff e7b872e29 (ancestor verified).
Next: Q2e under its own predicate. Capture the torch forward with `--set detailed` and parse via ncu_report.
If duration/cycle metrics fill, the parser + copy/sleep cheats follow. If they stay empty, record the bound and pause.
