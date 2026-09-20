# AETH-01 RunPod canary package

Status: **PACKAGE ONLY, NOT LAUNCHED.** No RunPod spend has occurred.
This package exists so a single, small, operator-approved run can
happen with one command, inside the $19.93 hard cap (AETHER_RUNPOD.md)
and a **$3 canary-specific sub-cap**. Nothing here runs itself.

## What this canary answers

The single question (AETHER_RUNPOD.md's 5-item run-proposal
requirement): **does the GPU-shaped algorithm
(`test/reference/gpu_aeth01.py`, already verified against the CPU
oracle locally via NumPy) produce bit-identical results to the CPU
oracle when its array backend is swapped to an actual CUDA array
library (CuPy) on real GPU hardware?** This is the open half of R12
(REQUIREMENTS.md): the gather-shape feasibility argument is strong, but
"no GPU implementation of ANY AETH candidate has been built or
measured" until this runs.

## Package inventory

- `README.md` -- this file.
- `Dockerfile` -- CUDA + Python 3.11 + CuPy + NumPy image; copies the
  canary payload in; no other dependencies.
- `aeth01_gpu_kernel.py` -- backend-agnostic port of
  `test/reference/gpu_aeth01.py`: uses CuPy if importable, else falls
  back to NumPy (so the identical file can be smoke-tested locally
  before ever touching a pod). **No physics change from
  `gpu_aeth01.py`** -- this file must be kept byte-identical to it
  except for the backend-selection shim at the top; any divergence
  invalidates the local differential-test evidence already gathered.
- `aeth01_cpu_oracle.py` -- verbatim copy of `test/reference/oracle_aeth01.py`,
  bundled so the pod can verify against the SAME CPU reference without
  a network dependency at run time.
- `run_canary.py` -- on-pod entry point: runs a small preregistered
  differential corpus (same shape as
  `test/test_aeth01_gpu_differential.py`) CPU-oracle vs GPU-kernel on
  whatever backend is active, times the GPU path, writes `receipt.json`.
- `watchdog.sh` -- hard wall-clock kill switch (cost control).
- `build_and_push.sh` -- builds and pushes the container image. Not run.
- `launch_pod.sh` -- the exact proposed RunPod launch command. Not run.
- `terminate_pod.sh` -- explicit pod termination. Not run.
- `receipt_schema.json` -- JSON Schema for `receipt.json`'s required shape.

## Exact proposed RunPod command (NOT executed)

    runpodctl create pod \
      --name aeth01-canary \
      --imageName <registry>/aeth01-canary:latest \
      --gpuType "NVIDIA RTX A4000" \
      --gpuCount 1 \
      --containerDiskSize 10 \
      --volumeSize 0 \
      --args "bash /app/watchdog.sh python3 /app/run_canary.py"

`<registry>` and any API key/token are supplied via the operator's own
`runpodctl` authentication (never embedded in this repo, never passed
as a command-line literal -- `runpodctl` reads its API key from its own
config file, set up out-of-band by the operator, not by this package).
GPU type is the single cheapest CUDA-capable option available at
launch time; `A4000` is a placeholder for "cheapest available," not a
hard requirement.

## Cost-control calculation (EXAMPLE ONLY -- rates fluctuate)

    EXAMPLE ONLY: RTX A4000 community-cloud rate ~= $0.17/hour (2026-09
    ballpark, NOT fetched live, NOT a quote)
    $3.00 cap / $0.17 per hour ~= 17.6 minutes maximum runtime

`watchdog.sh` enforces a **10-minute hard wall-clock kill** (well under
the $3/rate budget above, leaving margin for pod boot/image-pull time,
which is billed but does not run the canary itself). The canary script
itself is expected to complete in under 2 minutes (it is a few hundred
tiny-world differential comparisons plus one timing loop, not a
campaign). If `run_canary.py` has not exited by the watchdog's deadline,
the watchdog kills the container and the pod is still terminated by
`terminate_pod.sh`; a killed run still counts as spend
(AETHER_RUNPOD.md) and must be logged in `AETHER_RUNPOD.md`'s spend
ledger regardless of outcome.

## Expected receipt (`receipt.json`)

See `receipt_schema.json` for the enforced shape. Expected contents:
`semantics_id="aeth01.v1"`, `backend` (`"cupy"` or `"numpy_fallback"` --
a `numpy_fallback` result on an actual GPU pod would itself be a
finding, meaning CuPy failed to install/import, not a silent success),
`cases_run`, `cases_matched` (must equal `cases_run` to pass），
`gpu_kernel_seconds` vs `cpu_oracle_seconds` (throughput comparison,
informational only, not itself a pass/fail gate), and
`mismatches` (empty list on success; full CPU/GPU state diff on any
disagreement, never silently dropped).

## Known unresolved risks

- CuPy's `uint64` bitwise/wraparound semantics on the actual pod's CUDA
  version have not been checked against this package's assumption that
  they exactly mirror NumPy's (verified locally in NumPy only,
  REQUIREMENTS.md R12 note).
- Fancy-index gather (`array[n_row, n_col]` with 2-D index arrays) is
  used identically to the NumPy version; CuPy documents this as
  supported, but it has not been exercised on real hardware here.
- Pod boot / image pull time is unmeasured and could consume a
  meaningful fraction of the $3 cap before the canary itself starts;
  the watchdog's 10-minute budget assumes this is small.
- This canary establishes ONE differential-match data point on ONE GPU
  type; it is not a throughput benchmark or a campaign-readiness proof.
