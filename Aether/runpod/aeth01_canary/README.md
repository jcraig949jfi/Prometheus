# AETH-01 RunPod canary package

Status: **LOCAL VALIDATION ONLY; NO GPU OR RUNPOD RUN.** No image build or
push has been performed; the Docker daemon is unavailable. The spend ledger
remains **$0**. The operator-stated $19.93 balance is not live-verified.

## Entry points and migration

`age_controller.py` is the stdlib programmatic launch/recovery entry point.
From this directory, `python age_controller.py --help` lists its three commands:

- `plan --config CONFIG --run-dir FRESH_DIRECTORY`: zero network and zero
  credential reads. Parent directory must exist. Writes nonsecret `plan.json`
  with a random run UUID, exact source hashes and a plan SHA-256 summary.
- `run --run-dir DIRECTORY --approval APPROVAL --execute-paid-run`: **future
  paid operation, NOT authorized now**. Validates approval and local source
  bytes, locks the run, journals intent, then attempts exactly one POST.
- `recover --run-dir DIRECTORY`: cleanup only, never POST; allowed even after
  approval expires. Requires the same durable plan/state directory. Recovery
  returns nonzero even after confirmed cleanup; it never upgrades science.

Run directories are private local operational records, not repository artifacts.
Do not edit, duplicate, delete or reuse them. `state.json` retains owned IDs,
artifact hashes, `science_verdict`, `cleanup_status`, and sanitized failure code.
Artifacts are saved under `artifacts/<pod_id>/` before normal teardown.

### Configuration and approval (nonsecret JSON)

Config keys are exact; unknown keys, boolean numbers and nonfinite values fail.

| Config key | Required value |
|---|---|
| `image` | Immutable registry/repository reference with `@sha256:<64 lowercase hex>` |
| `gpu_id`, `cloud` | Current operator-selected GPU; `COMMUNITY` or `SECURE` |
| `hourly_rate_usd` | Positive, current conservative **all-in** hourly estimate |
| `canary_budget_usd` | Positive, at most 3 |
| `remaining_budget_usd` | At least canary budget and at most 19.93; operator reconciles prior spend |
| `max_lifetime_seconds` | Integer, at most 900; starts before create, including boot/pull |
| `canary_timeout_seconds` | Integer 1..600 |
| `independent_cutoff_deadline_utc` | Absolute UTC timestamp for the independently armed cutoff |
| `independent_cutoff_reference` | Nonsecret identifier for that cutoff/recovery arrangement |

Lifetime reserves 60s for retrieval and 120s for cleanup; boot/pull remainder
must be at least 30s. Quoted lifetime cost must be <= half the canary budget.
Cutoff must follow lifetime and fit the full budget/rate window measured from
plan creation. Approval expires before cutoff; the full lifetime must still
fit before cutoff at launch. These are conservative admission checks, not
account-wide budget reservation or observed billing. Only one operator-approved
canary is in scope; this is not a multi-run scheduler or campaign engine.

Approval has exactly `approved: true`, the generated `run_id`, `plan_sha256`
(hash of exact plan bytes), `expires_at_utc`, and `independent_billing_cutoff`.
The latter has exactly `attested: true`, `deadline_utc`, and `reference`;
deadline and reference must equal the config. Do not attest a cutoff that has
not actually been armed independently of this host. None was armed here.

Only a future live `run` reads `RUNPOD_API_KEY` and `AGE_ARTIFACT_TOKEN` from
the operator's privately supplied environment. Generate the latter independently
with a cryptographic RNG (at least 32 printable non-whitespace characters).
Never reuse the API key as the artifact token. Never put either value in JSON,
shell arguments, logs, review packets or commits. Recovery can terminate without
the artifact token, but cannot download artifacts without it.

`launch_pod.sh` and `terminate_pod.sh` are **disabled migration stubs**:
they print guidance to stderr, exit nonzero, and make no provider calls.
Neither is a fallback paid path. For an existing pod, use controller
recovery or terminate it in the RunPod console and verify termination.

## Required controller contract

These are launch gates and lifecycle requirements, not a claim that a paid
end-to-end run has been validated:

1. A run-specific plan and explicit operator approval bind the `run_id`,
   immutable image reference (`registry/repository@sha256:<digest>`), source
   hashes, hardware, duration, cost estimate, and acceptance criteria.
   The canary sub-cap is **$3**, within the **$19.93 total policy cap** in
   [AETHER_RUNPOD.md](../../AETHER_RUNPOD.md). No standing approval applies.
2. Before create, require an **operator-attested independent provider-side
   or external cutoff**, with a run-specific deadline and recovery path
   independent of the controller host. Without that attestation, fail closed.
   A local timer or cleanup trap alone does not meet this requirement.
3. Persist durable run ownership and create intent **before** sending POST.
   A lost or ambiguous create response must trigger reconciliation against
   structured, paginated pod listings using that ownership, **not a POST
   retry**. Do not guess a pod ID from text or terminate an unrelated pod.
   Positive ownership is journaled page by page, so a later listing failure
   cannot erase a pod already found. Incomplete inventory never confirms cleanup.
4. Use RunPod API v2 at `https://api.runpod.io/v2/pods`: create expects
   **POST 201**; GET returns structured data; listing must handle pagination.
   Termination expects **DELETE 204**, followed by GET verification of
   **404 or `TERMINATED`**. A DELETE response alone is not verified cleanup;
   stopped, unreachable, or missing artifacts do not establish termination.
5. Fetch **bounded** `receipt.json`, `canary.log`, and `result.json` over the
   pod's **HTTPS proxy for port 8080**, using a distinct artifact token
   supplied to the container through its environment. Bound request time,
   response sizes, and total collection time; do not delay cutoff indefinitely
   for artifacts. The controller's RunPod API key must **never** reach the pod,
   artifacts, or logs. Never print tokens or raw provider responses that may
   contain environment secrets.
6. Require a final `result.json` with `finished` equal to `true` and the
   approved run binding. Cross-check its `run_id` with the receipt and plan;
   an incomplete, stale, or wrong-run artifact is not success. Retrieve
   artifacts before termination when possible, but prioritize the cutoff.
   Verify cleanup and record actual spend even on failure or missing evidence.
   Known owned IDs receive cleanup before further inventory scans. Expired
   recovery gets a 120s cooperative emergency-cleanup scheduling window (up to
   three rounds). In-flight calls can overrun that window; it is not hard
   preemption. Original-lifetime overrun still prevents controller PASS.

## Billing boundary

No maximum-price or hard-expiry field is documented for this API create
contract. The v2 returned `cost` is checked against the quote at create/status,
but does not reserve a rate. A rate estimate, image tag, local timeout, or client-side budget
calculation is not provider-enforced protection. **The controller is not an
absolute billing guarantee**, even with independent cutoff attestation.
Provider failure, network loss, boot/image-pull delays, and failed cleanup
remain risks; the operator must independently check termination and charges.

`pod_service.py` supervises the canary process group with a maximum **600s**
compute deadline. When the child finishes or is killed, the service remains
up to serve artifacts. **The pod continues billing until externally
terminated**; process exit and the in-container watchdog do not stop billing.

## Scientific acceptance

The canary asks whether the CuPy GPU implementation matches the bundled CPU
oracle for `aeth01.v1`: **200 single-tick comparisons + 20 trajectories x 5
intermediate ticks = 300 matches**. A GPU PASS requires actual **CuPy**,
all 300 comparisons matched, no mismatches, the approved source hashes and
`run_id`, and the final run-bound result above. Receipt shape alone is not
sufficient; see `receipt_schema.json` and the controller validation.

A **NumPy PASS is a local smoke result, not GPU evidence**. GPU fallback,
incomplete results, and incorrect hashes or run binding cannot pass the GPU
gate. Timings are informational: one small correctness canary is neither a
throughput benchmark nor campaign-readiness proof.

## Image preparation and local validation

`build_and_push.sh` is for a separate, explicit operator invocation only. It
requires `REGISTRY` and `IMAGE_TAG`, builds with `--platform linux/amd64`,
then pushes that tagged image. Registry authentication is configured out of
band; no credentials belong in the script or command arguments. Retrieve
the pushed digest from the registry or the printed RepoDigests inspection
instruction, and bind approval to **`@sha256`**, never a mutable tag. Image
publication does not approve or launch a pod.

The existing dependencies and CUDA base version are unchanged. Local
`.gitattributes` forces LF for Python, shell, Dockerfile, and JSON files so
Windows checkout conversion does not break Linux scripts or raw source-hash
agreement. Validate actual worktree bytes before building or hashing.

Validation is local only, not a GPU, authenticated provider API, image build, or
registry-push validation. Run `python -m pytest Aether/test -q` from the repository
root. Linux-specific service/process-group tests also run directly with
`python3 Aether/test/test_aeth01_pod_service.py`; Windows skips those cases.
The closure packet records exact results. No paid action is authorized here.

Public contracts consulted (not live provider validation):
- https://docs.runpod.io/api-reference-v2/pods/create-a-pod
- https://docs.runpod.io/api-reference-v2/pods/list-pods
- https://docs.runpod.io/api-reference-v2/pods/trigger-a-pod-state-transition
- https://docs.cupy.dev/en/v13.5.1/reference/comparison.html
