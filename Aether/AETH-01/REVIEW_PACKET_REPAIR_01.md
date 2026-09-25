# AETH-01 -- Repair cycle handoff packet (final review packet)

Status: repair cycle COMPLETE against `ASTRA_REVIEW_01.md`. No Runpod
spend has occurred. No implementation beyond the CPU oracle, the
GPU-shaped local implementation, and their test suites. This packet is
the entry point for the next independent (Astra) review of the REPAIR,
not a restatement of the original design (`ASTRA_REVIEW_PACKET.md`
remains the entry point for that).

Reviewed design commit: `5e41c1d679fc52394cbb6efd2f56a41bd8483604`.
Controlling review: `Aether/AETH-01/ASTRA_REVIEW_01.md` (verdict
`PROCEED_TO_REPAIR`). This packet does not edit or erase that review.

## 1. What was repaired, and against what

Every item Astra raised is individually dispositioned in
`REPAIR_LEDGER_01.md`: **21 items** (S01-S06, M01-M09 with M02/M03
merged into one entry, N01-N04, B01-B03) -- **19 ACCEPT, 2
ACCEPT_WITH_QUALIFICATION, 0 REJECT**. No item was rejected by appeal
to intent; the ledger requires a counterexample or derivation for any
REJECT, and none was used because none was needed. Kill gates K1-K8 are
handled separately (below), not inside this ledger.

## 2. Kill gates run this cycle

`KILL_GATES_01.md`, scoped per instruction to **K1 (accounting), K2
(mutation/accessibility), K3 (relay vs. constructed capacity), K6
(provenance composition)**: all four hand-worked against the repaired
law, **all PASS**, no `INFERENCE_CONTRACT_UNRESOLVED` outcome, nothing
left unresolved. K4/K5/K7/K8 are explicitly DEFERRED (not silently
dropped) -- each requires a running sweep, a completed campaign, or a
production trace implementation that do not exist yet; they are
preconditions for using AETH-01 as *scientific evidence*, not
preconditions for this repair cycle's own deliverables.

## 3. Repaired freeze candidate

`AETH01_REPAIRED_FREEZE_CANDIDATE.md` states the full repaired
`aeth01.v1` semantics: the single authoritative energy identity
(`E[t+1] = E[t] + R - X - A + C - D`, replacing the reviewed draft's
double-counting formula), the corrected copy-coupled mutation
accessibility description, the mod-5 target-field selector, and the
provenance-composition rules. **`aeth01.v1` is still a CANDIDATE, not
frozen** -- this document is the freeze proposal, not a freeze order.

## 4. Independent implementations and test evidence

- `Aether/test/reference/oracle_aeth01.py` -- naive, directly-readable
  CPU oracle restating the repaired law from the frozen-candidate text
  (not imported by the GPU module, so the differential test compares
  two independent implementations of the same specification).
- `Aether/test/reference/gpu_aeth01.py` -- whole-grid vectorized
  (NumPy) GPU-shaped implementation, same gather/no-atomics shape as
  `Aether/production/aeth00.py`.
- Test files: `test_aeth01_kill_gates.py`, `test_aeth01_properties.py`
  (Hypothesis property tests, including the zero-tolerance accounting
  identity), `test_aeth01_gpu_differential.py` (fixtures + 500
  randomized CPU-vs-GPU-shape trials, dims 1-4, multi-tick trajectories).
- **Result: 27 AETH-01-specific tests pass.** Full suite including all
  inherited AETH-00/AETH-00A/AETH-00B tests: **112 passed, 0 failed**
  (`python -m pytest Aether/test -q`). No AETH-00 file was modified.

## 5. RunPod canary package

`Aether/runpod/aeth01_canary/` -- **package only, not launched, $0
spent.** Full detail in its own `README.md`; summarized here per the
handoff requirement:

- **Package inventory:** `README.md`, `Dockerfile` (CUDA 12.4 +
  Python 3.11 + CuPy), `aeth01_gpu_kernel.py` (backend-agnostic port of
  `gpu_aeth01.py`, CuPy if importable else NumPy fallback),
  `aeth01_cpu_oracle.py` (verbatim copy of `oracle_aeth01.py`),
  `run_canary.py` (on-pod entry point, 200-trial preregistered
  differential corpus, writes `receipt.json`), `watchdog.sh` (hard
  wall-clock kill switch), `build_and_push.sh`, `launch_pod.sh`,
  `terminate_pod.sh` (none run), `receipt_schema.json`.
- **Question it answers:** does the GPU-shaped algorithm produce
  bit-identical results to the CPU oracle when its array backend is
  swapped to real CuPy on real CUDA hardware (the open half of R12 --
  no GPU implementation of any AETH candidate has been run on real GPU
  hardware yet).
- **Exact proposed RunPod command** (not executed):
  ```
  runpodctl create pod \
    --name aeth01-canary \
    --imageName <registry>/aeth01-canary:latest \
    --gpuType "NVIDIA RTX A4000" \
    --gpuCount 1 \
    --containerDiskSize 10 \
    --volumeSize 0 \
    --args "bash /app/watchdog.sh python3 /app/run_canary.py"
  ```
  `<registry>` and any credential are supplied by the operator's own
  `runpodctl` auth, never embedded here or passed as a literal.
- **Cost-control calculation (EXAMPLE ONLY, rates fluctuate, not fetched
  live):** RTX A4000 community-cloud rate ~= $0.17/hour (2026-09
  ballpark) => $3.00 cap / $0.17/hr ~= 17.6 minutes maximum runtime.
  `watchdog.sh` enforces a **10-minute hard wall-clock kill**, inside
  that budget with margin for boot/image-pull time; the canary script
  itself is expected to finish in under 2 minutes. A killed run still
  counts as spend and must be logged in `AETHER_RUNPOD.md`'s ledger.
- **Expected receipt (`receipt.json`, schema `receipt_schema.json`):**
  `semantics_id="aeth01.v1"`, `backend` (`"cupy"` or
  `"numpy_fallback"` -- fallback on a real GPU pod is itself a finding),
  `cases_run`/`cases_matched` (must be equal to pass),
  `gpu_kernel_seconds`/`cpu_oracle_seconds` (informational only),
  `mismatches` (empty on success, full state diff on any disagreement).
  Locally smoke-tested this cycle on the NumPy fallback path: 200/200
  matched, `mismatches: []` (no CuPy/GPU hardware available in this
  workspace, so the CuPy code path itself remains untested until run
  on an actual pod).
- **Known unresolved risks:** CuPy's `uint64` bitwise/wraparound
  semantics on the actual pod's CUDA version are unverified against
  this package's NumPy-derived assumption; CuPy's support for
  2-D-index fancy-index gather is documented but unexercised on real
  hardware; pod boot/image-pull time is unmeasured and could consume a
  meaningful share of the $3 cap; this canary is one differential-match
  data point, not a throughput benchmark or campaign-readiness proof.

## 6. What this handoff does not ask Astra to do

Does not ask for approval to freeze `aeth01.v1` -- that is a separate,
later decision gated on K4/K5/K7/K8 as well as this cycle's K1/K2/K3/K6.
Does not ask for approval to spend on RunPod -- the canary package is
prepared, not authorized; launch requires separate, explicit,
per-run operator approval per `AETHER_RUNPOD.md`. Does not pre-judge
whether the two ACCEPT_WITH_QUALIFICATION items in `REPAIR_LEDGER_01.md`
need further work before a freeze; that judgment is left open.

## 7. Supporting documents (this cycle's new/changed artifacts)

- `REPAIR_LEDGER_01.md` -- full 21-item disposition ledger.
- `KILL_GATES_01.md` -- K1/K2/K3/K6 adjudication, K4/K5/K7/K8 deferral.
- `AETH01_REPAIRED_FREEZE_CANDIDATE.md` -- repaired semantics statement.
- `Aether/test/reference/oracle_aeth01.py`,
  `Aether/test/reference/gpu_aeth01.py` -- independent CPU/GPU-shape
  implementations of the repaired law.
- `Aether/test/test_aeth01_kill_gates.py`,
  `Aether/test/test_aeth01_properties.py`,
  `Aether/test/test_aeth01_gpu_differential.py` -- 27 executable tests.
- `Aether/runpod/aeth01_canary/` -- self-contained RunPod canary
  package (not launched).
- All previously repaired AETH-01 design documents (`PHYSICS_SPEC_DRAFT.md`,
  `ECONOMICS.md`, `EXPERIMENTS.md`, `HABITABILITY.md`, `OBSERVATORY.md`,
  `HEREDITY_REQUIREMENTS.md`, `ADVERSARIAL_ANALYSIS.md`, `REQUIREMENTS.md`,
  `GPU_RUNPOD.md`, `DECISIONS.md`, `PHYSICS_CANDIDATES.md`) per
  `REPAIR_LEDGER_01.md`'s per-item "Affected docs" columns.
