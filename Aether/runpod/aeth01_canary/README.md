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
- `launch_pod.sh` -- the exact proposed RunPod launch command, with
  fail-closed budget-derived cost control (requires `HOURLY_RATE` and
  `MAX_DOLLAR_BUDGET`, no defaults) and automatic pod cleanup on exit.
  Not run.
- `terminate_pod.sh` -- explicit manual pod termination; independent
  fallback to `launch_pod.sh`'s own automatic cleanup. Not run.
- `receipt_schema.json` -- JSON Schema for `receipt.json`'s required shape.

## Exact proposed RunPod command (NOT executed)

`launch_pod.sh` wraps the command below with fail-closed budget
derivation and automatic cleanup (next section); this is the
underlying `runpodctl` call it makes:

    runpodctl create pod \
      --name aeth01-canary \
      --imageName <registry>/aeth01-canary:latest \
      --gpuType "NVIDIA RTX A4000" \
      --gpuCount 1 \
      --containerDiskSize 10 \
      --volumeSize 0 \
      --cost <HOURLY_RATE> \
      --env "AETH01_CANARY_TIMEOUT_SECONDS=<derived>" \
      --args "bash /app/watchdog.sh python3 /app/run_canary.py"

`<registry>` and any API key/token are supplied via the operator's own
`runpodctl` authentication (never embedded in this repo, never passed
as a command-line literal -- `runpodctl` reads its API key from its own
config file, set up out-of-band by the operator, not by this package).
GPU type is the single cheapest CUDA-capable option available at
launch time; `A4000` is a placeholder for "cheapest available," not a
hard requirement. `--cost` is `runpodctl`'s own $/hr price ceiling,
passed through as a second, provider-side check that the actual price
never exceeds the operator-supplied `HOURLY_RATE`.

## Cost-control calculation (EXAMPLE ONLY -- rates fluctuate)

    EXAMPLE ONLY: RTX A4000 community-cloud rate ~= $0.17/hour (2026-09
    ballpark, NOT fetched live, NOT a quote)
    $3.00 cap / $0.17 per hour ~= 17.6 HOURS maximum runtime

(Corrected from an earlier draft of this file, which mis-stated the
result as "17.6 minutes" -- $3.00 / $0.17/hr is 17.6 **hours**, not
minutes, at this EXAMPLE-ONLY rate. The actual binding constraint in
practice is `watchdog.sh`'s wall-clock cap below, not this arithmetic
by itself.)

`launch_pod.sh` now REQUIRES the operator to supply `HOURLY_RATE` (read
off the RunPod console at launch time -- no default, no silent fallback
to the example rate above) and `MAX_DOLLAR_BUDGET` (must be `<=` the $3
canary sub-cap). It fails closed (aborts, launches nothing) if either
is missing or non-numeric. From these it derives an in-container hard
timeout: `MAX_DOLLAR_BUDGET / HOURLY_RATE * 3600 * SAFETY_FACTOR`
seconds (`SAFETY_FACTOR` defaults to `0.5`, i.e. at most half the
dollar budget is allowed to be consumed by the container's own compute
time; the rest is margin for pod boot/image-pull time, which is billed
but not covered by an in-container timer). This derived value is passed
into the container as `AETH01_CANARY_TIMEOUT_SECONDS`, which
`watchdog.sh` reads instead of its generic 600s standalone default. The
canary script itself is expected to complete in under 2 minutes (it is
a few hundred tiny-world differential comparisons plus one timing loop,
not a campaign); the derived timeout at the example rate/budget above
is far larger than that, so in practice `watchdog.sh` is not expected
to be the thing that stops a normal run -- it exists purely as the
fail-safe for a hang.

If `run_canary.py` has not exited by the watchdog's deadline, the
watchdog kills the container. `launch_pod.sh` also registers its own
automatic cleanup: a shell trap that runs `runpodctl remove pod` when
the script exits for ANY reason (normal completion, error, or an
operator interrupt), so a pod is not left running just because the
launching script stopped. This is defense in depth, not a replacement
for `watchdog.sh`'s in-container timer, and it is not an absolute
guarantee either -- see "Known unresolved risks" below. A killed or
auto-terminated run still counts as spend (AETHER_RUNPOD.md) and must
be logged in `AETHER_RUNPOD.md`'s spend ledger regardless of outcome.
`terminate_pod.sh` remains available as an independent manual fallback
if the automatic cleanup ever fails or warns.

## Expected receipt (`receipt.json`)

See `receipt_schema.json` for the enforced shape. `status` is the
single authoritative verdict, drawn from a closed vocabulary: `PASS`,
`FAIL_MISMATCH` (a case disagreed), `FAIL_ENVIRONMENT` (`backend` fell
back to `numpy_fallback` when a real GPU was required -- CuPy failed to
import; this is ALWAYS a fail on a real pod, never inferred as a pass
even if the fallback arithmetic happens to match the CPU oracle),
`FAIL_ERROR` (an unhandled exception), or `FAIL_INCOMPLETE` (the
placeholder written before the run starts -- finding this on disk means
the run never reached a verdict, e.g. `watchdog.sh` killed it; it must
never be read as a pass by omission). `run_canary.py`'s own process
exit code is 0 iff `status == "PASS"`.

Other contents: `semantics_id="aeth01.v1"`; `cases_run` /
`cases_matched` (must be equal for `PASS`) covering both the
`single_tick_trials` corpus and the `multi_tick_trials` x
`multi_tick_steps` trajectory corpus (compared at every intermediate
tick, not just the final one); `gpu_kernel_seconds` vs
`cpu_oracle_seconds` (throughput comparison, informational only, not
itself a pass/fail gate); `mismatches` (empty list on success; full
CPU/GPU state diff, including which tick of a trajectory, on any
disagreement, never silently dropped); `source_hashes` (sha256 of the
bundled physics/harness files actually present on the pod, so a
reviewer can confirm which revision ran without git history there);
`cost_context` (echo of the `HOURLY_RATE`/`MAX_DOLLAR_BUDGET`/derived
timeout `launch_pod.sh` used for this run, if launched that way);
`started_at_utc` / `finished_at_utc`; and `python_version` /
`numpy_version` / `cupy_version`.

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
  `launch_pod.sh`'s derived timeout budgets only half of
  `MAX_DOLLAR_BUDGET` for in-container compute time specifically to
  leave margin for this, but the actual boot/pull duration on real
  hardware is still unmeasured.
- This canary establishes ONE differential-match data point on ONE GPU
  type; it is not a throughput benchmark or a campaign-readiness proof.
- **Residual provider-side billing risk (fundamental, not fixed by this
  package):** `launch_pod.sh`'s cleanup trap and `watchdog.sh`'s
  in-container timeout are both LOCAL mechanisms. If the machine
  running `launch_pod.sh` loses network connectivity or power before
  the trap fires, or if `runpodctl remove pod`/`stop pod` itself fails
  silently on the provider side, no local script can detect or correct
  that -- the pod keeps billing until an operator checks the RunPod
  console directly. Neither this package nor any client-side script can
  fully close this gap; the operator must check the console after every
  run regardless of what the scripts report.
- `launch_pod.sh`'s parsing of `runpodctl create pod`/`get pod` output
  (to extract `POD_ID` and to detect when the pod stops running) is
  best-effort text matching, not a documented, versioned API contract;
  it has not been exercised against real `runpodctl` output and may
  need adjustment the first time it is actually run.
- `launch_pod.sh` does not itself copy `receipt.json` off the pod; the
  printed summary (all fields except `mismatches`) is expected to be
  visible via the pod's own stdout/logs, but retrieving the full
  `receipt.json` file (needed to see mismatch detail on a FAIL) is the
  operator's responsibility and must happen before the cleanup trap
  terminates the pod.
