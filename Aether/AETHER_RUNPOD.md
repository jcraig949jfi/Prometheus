# Aether -- Runpod benchmarks, hardware, costs, deployment

Currency: 2026-09-21. No paid runs yet. Recorded spend: **$0** of the
**$19.93** policy budget. The balance is operator-stated, not live-verified.

## Budget

- Policy hard cap: $19.93 total (2026-09-20 operator-stated account balance,
  not a top-up commitment or a provider-enforced billing guarantee).
- AETH-01 canary sub-cap: $3, inside the total cap, not additional funds.
- No Runpod spend without explicit operator approval, per run.
- Before proposing any paid run, state: the question it answers; expected
  duration; hardware; estimated maximum cost; what result determines the
  next step. A run proposal missing any of these five is incomplete.
- Failed or inconclusive runs still count as spend and must still produce
  a useful measurement (logged below regardless of outcome).

## AETH-01 programmatic canary contract

See [the canary README](runpod/aeth01_canary/README.md) for the lifecycle and
scientific gates. `age_controller.py` implements plan/run/recover; consult
`python age_controller.py --help` from the canary directory.
The old launch and termination shell scripts are disabled, nonzero-exit
migration stubs, not paid fallbacks. Existing pods require controller
recovery or console termination, followed by independent verification.

- Each approved plan binds a unique `run_id`, immutable `@sha256` image,
  expected source hashes, hardware, duration, cost estimate, and result gate.
- An operator-attested **independent provider/external cutoff** is required
  before create. RunPod API v2 documents no create-time maximum-price or
  hard-expiry field here. The controller is **not an absolute billing
  guarantee**; a local timeout is not a substitute for that cutoff.
- Persist ownership before create. Use structured RunPod API v2
  `https://api.runpod.io/v2/pods` responses: POST 201, paginated GET listings,
  DELETE 204 followed by GET 404 or `TERMINATED` verification. Reconcile a
  lost create response against durable ownership; never blindly retry POST.
- Collect bounded `receipt.json`, `canary.log`, and `result.json` via the
  port-8080 HTTPS proxy, authenticated with a distinct environment-supplied
  artifact token. The controller API key never goes on-pod or into logs.
  Require final `finished: true` and correct run binding; never trade an
  unbounded artifact wait for continued billing.
- The container service limits the canary process group to at most 600s,
  then remains up serving artifacts and **billing until external termination**.
  Verify termination and account for boot, pull, artifact collection, failures,
  and cleanup time, not just compute duration.
- GPU evidence requires CuPy, **200 + 20 x 5 = 300 matches**, approved source
  hashes and `run_id`, and a final run-bound result. NumPy PASS is smoke-only.

Validation is local only: no GPU/RunPod run, image build, or image push has
occurred. A Docker daemon is unavailable. Existing dependencies and the CUDA
base version are unchanged. Offline controller/transport and Linux process-group
tests have passed; the closure packet records exact coverage and remaining gates.

## Spend ledger

| date | run | question | hardware | est. max cost | actual cost | result -> next step |
|---|---|---|---|---|---|---|
| (none yet) | | | | | | |

## Benchmarks planned (once there is something to run)

- Correctness (does the remote build match the local/tested semantics).
- GPU compatibility.
- Throughput.
- Memory use.
- Cost per useful unit of simulation.
- Suitable GPU / serverless / Pod configuration for the workload shape.

## Topology decision (Pods vs. serverless/autoscaling)

Undecided (AETHER_OPEN_QUESTIONS.md, question 14). Deferred until a
workload shape exists to benchmark against.

## Principle

Optimize for learning per dollar, not scale. Start extremely small; do
not assume expensive GPUs are better than cheap ones until measured.
