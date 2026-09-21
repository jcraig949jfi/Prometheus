# AETH-01 RunPod canary package

Status: **LOCAL VALIDATION ONLY; NO GPU OR RUNPOD RUN.** No image build or
push has been performed; the Docker daemon is unavailable. The spend ledger
remains **$0**. The operator-stated $19.93 balance is not live-verified.

## Entry points and migration

`age_controller.py` is the stdlib programmatic launch/recovery entry point.
From this directory, `python age_controller.py --help` lists its four commands:

- `plan --config CONFIG --run-dir FRESH_DIRECTORY`: zero network and zero
  credential reads. Parent directory must exist. Writes nonsecret `plan.json`
  (random run UUID, exact source hashes, plan SHA-256 summary) AND
  `reaper_manifest.json` (the B3 pre-create handoff for `independent_reaper.py`).
- `run --run-dir DIRECTORY --approval APPROVAL --execute-paid-run`: **future
  paid operation, NOT authorized now**. Validates approval and local source
  bytes, locks the run, journals intent, confirms the independent reaper has
  durably armed (`reaper_ack.json` matching `reaper_manifest.json`, HMAC-bound
  with `AGE_REAPER_SHARED_SECRET` -- see "Independent reaper" below), then
  attempts exactly one POST.
- `recover --run-dir DIRECTORY`: cleanup only, never POST; allowed even after
  approval expires. Requires the same durable plan/state directory. Recovery
  returns nonzero even after confirmed cleanup; it never upgrades science.
- `combine --run-dir ORIGINAL_DIRECTORY --local-outcome LOCAL_JSON
  --reaper-report REAPER_JSON`: no provider or credential access. After the
  independent window, hold the controller's existing exclusive run lock,
  reload authoritative durable state and refuse any stale local snapshot.
  Atomically writes `cleanup_seal.json`; exit 0 only for operational confirmation.

Run directories are private local operational records, not repository artifacts.
Do not edit, duplicate, delete or reuse them. `state.json` retains owned IDs,
per-pod cleanup evidence (`pod_evidence`), artifact hashes, `science_verdict`,
`cleanup_status`, a bounded secret-safe `diagnostics` journal, and a sanitized
failure code. Artifacts are saved under `artifacts/<pod_id>/` before normal
teardown.

### Cleanup evidence contract (cleanup policy v1; B1/B2/B3)

The current contract is [CLEANUP_EVIDENCE_MODEL.md](../../AETH-01/CLEANUP_EVIDENCE_MODEL.md).
It supersedes cleanup semantics in earlier review packets, which remain
historical records. `cleanup_evidence.py` is the shared pure policy; deploy it
beside both the controller and the independent reaper, with `runpod_api.py`.
It is not an on-pod image payload. Controller state schema 3 and reaper schema 2
require replayable append-only histories; legacy states are explicitly refused,
not promoted. No paid runs require legacy migration at this stage.
Review 03 reaper evidence also requires `observation_policy=LIST_AND_KNOWN_GET_V1`;
old LIST-only snapshots/reports are refused, not silently credited. Do not add
that marker by hand to old evidence: generate a fresh dual-endpoint horizon.

`cleanup_status` is `LOCAL_CLEANUP_CONFIRMED` or `LOCAL_CLEANUP_UNRESOLVED` --
this controller's own bounded evidence ONLY. A pod's cleanup evidence
(`state.json["pod_evidence"][pod_id]`) reaches `CONFIRMED` only via (a) a
positive `TERMINATED` observation, or (b) an acknowledged DELETE (`ACK_204`)
corroborated by independent inventory reconciliation (two full, successful
scans that do not see the pod, with no intervening reappearance). An
ambiguous 404 alone -- "not found or not accessible" per the official
NotFoundError semantics -- NEVER confirms termination on its own, and a
pod's evidence is demoted back to `UNRESOLVED` if it later reappears.
Reconciliation now runs every cleanup round unconditionally, even after an
apparently clean create; it is never disarmed by an optimistic response.

Three distinct propositions must not be collapsed:

- `KNOWN_OWNED_CLEANUP`: current evidence for every exact-owned ID. All
  exact-owned duplicates are retained and cleaned; a partial match is unrelated.
  A live reappearance invalidates CURRENT termination/ACK/absence evidence,
  while historical TERMINATED observations and DELETE results are preserved.
- `RECONCILIATION_WINDOW`: a full healthy, complete, empty-inventory horizon
  after cutoff, independently observed by the reaper.
- `OPERATIONAL_CLEANUP`: validated agreement of both reports plus both claims
  above, under this bounded policy; NOT proof of perpetual absence or billing stop.

`LOCAL_CLEANUP_CONFIRMED` is only local cleanup. `reconciliation_required`
stays `true` as a durable obligation the independent reaper also carries. Use
`age_controller.combine_operational_cleanup(local_outcome, reaper_report, run_dir=original_directory)`
(an operator/CI step run after the reaper's own reconciliation window) to
merge this controller's outcome with `independent_reaper.py`'s
`REAPER_CLEANUP_CONFIRMED`/`REAPER_CLEANUP_UNRESOLVED`/`REAPER_PENDING`
report into one `OPERATIONAL_CLEANUP_CONFIRMED`/`_UNRESOLVED` verdict.
The combiner replays structured histories, verifies matching manifests/digests,
unions known IDs, and recomputes the horizon; CONFIRMED strings alone are refused.
The window must start after the controller's last provider evidence and its
latest sample must be <=60 seconds old at aggregation (never future-dated).
Neither side nor their agreement proves that provider charges have stopped.

Review 03 uses the **post-window local seal** contract (Option C). The local
outcome contains `state_sha256` (canonical durable state) and `generated_at_utc`.
The combiner verifies BOTH the hash and replay-derived report contents against
the original run directory while holding `RunLock`, which launch and recovery
hold for their entire provider lifecycle. New durable state B makes old report A
unusable, even when A's own history looks clean. Missing/unavailable source,
unfinished state, concurrent recovery, stale hash or failed seal write refuses.
The seal binds the state, both input reports and sealing UTC; sealing performs
no provider interactions. Later controller activity requires fresh aggregation
and, if its evidence overlaps the window, a fresh independent horizon.

Only the original, single authoritative run directory may be used; never copy
or roll it back to resurrect an old report. B3 must restrict writers to the
lock-obeying entry points and invoke aggregation on that authoritative host.
While the host is unavailable the reaper can still delete, but operational
aggregation must refuse. This is not a distributed authenticated store.
Saved seals are point-in-time evidence, not reusable standing authorization.
The pure `cleanup_evidence.aggregate()` evaluator returns
`authoritative_local_state=False`; it is NOT the operational sealing workflow.

### Independent reaper (B3)

`independent_reaper.py` is a separate, cleanup-only module with no import
dependency on `age_controller.py` and no `create_pod` capability anywhere in
its own code path (`ReaperProvider` never exposes one). Deploy it on any
host/process/scheduler independent of this controller's process, filesystem,
power, network session, and artifact proxy:

1. `arm --manifest reaper_manifest.json --out-ack reaper_ack.json
   --scheduler-id ID` (reads `AGE_REAPER_SHARED_SECRET`): durably
   acknowledges an exact plan BEFORE the controller may POST. Copy
   `reaper_ack.json` back into the run directory (or keep the run directory
   on storage both hosts can reach) so `run()`'s `_require_reaper_armed`
   gate can read it.
2. `sweep --manifest reaper_manifest.json --out-evidence reaper_evidence.json
   [--ack reaper_ack.json] [--rounds N] [--poll-seconds S]` (reads
   `RUNPOD_API_KEY`): the future independent worker must sustain ONE invocation
   for a complete healthy `reconciliation_horizon_seconds` after cutoff,
   whether or not any pods were found. The six-round default is only a short
   cleanup pass, NOT an operational horizon. For a 3600-second horizon at
   10-second polling, at least 361 healthy scans are needed in the ideal case;
   allow bounded headroom for discovery/failure resets and escalate on exhaustion.

Each qualifying round needs complete LIST **and GET for every known reaper ID**,
including previously confirmed IDs. LIST discovers unknown duplicates; GET
tries to falsify cleanup of known IDs. Empty LIST cannot substitute for GET.
Any exact-owned GET positive (including TERMINATED) resets the empty window;
live responses also demote confidence and enable same-round DELETE. GET
transport/auth/schema failure makes the round non-qualifying; ambiguous GET
404 is MISSING, never an added absence witness. No qualifying sample is
published before all required GETs finish. Budget request latency so complete
rounds remain within the 60-second maximum observation gap.

Per-pod histories survive restart, but window credit does not. Repeated short
cron jobs CANNOT accumulate a qualifying horizon. A fully successful empty scan
starts a new window after failure, any owned discovery (even TERMINATED), a
gap >60 seconds, or clock discontinuity. Require both UTC and monotonic spans
>= the horizon, >=6 samples, adjacent gaps <=60 seconds, and adjacent elapsed
clock deltas agreeing within 2 seconds. A blind hour plus 50 seconds of empty
scans covers only 50 seconds. UTC alone never earns elapsed observation credit.

The CLI holds a single-writer evidence lock and checkpoints provider evidence
with atomic fsynced writes. Journal or runtime clock failure prevents confirmation
without suppressing best-effort deletion of positively owned targets. Malformed
persisted evidence is refused; do not edit it into success. Missing timestamped
facts after a broken clock require operator remediation and independent fresh
evidence, not automatic confidence repair. A known-ID identity conflict blocks
DELETE until a fresh exact binding is observed and remains an unresolved anomaly.

The HMAC `arm` file proves a bound handoff, NOT that a scheduler is running,
credentials are usable, a separate host survives failure, or billing has stopped.
Deployment, controller-host-loss rehearsal, credential/alert/operator-fallback
proof and provider charge reconciliation remain B3 operational admission gates.
None is authorized or claimed completed by these offline tests.

Timing terms are distinct: `cutoff_utc` / `independent_cutoff_deadline_utc` is
the **forced-cleanup start/deadline**, not provider-enforced billing cessation.
The **post-cleanup reconciliation horizon** runs at/after that time; normal
confirmation is no earlier than cutoff + 3600 seconds, later after resets.
**Charge-reconciliation completion** is a separate provider/accounting check.

Before R1, the qualification oracle in
`Aether/test/reference/cleanup_aeth01_oracle.py` independently checks endpoint
traces and the authoritative current-state hash without importing shared
production policy. Supply the complete known-ID union and actual endpoint
trace; it checks necessary invariants, not ownership authentication or billing.
An omitted probe/ID or stale source fails qualification, never counts as MISSING.

See `independent_reaper.py`'s module docstring and
`Aether/test/test_aeth01_independent_reaper.py` (including a host-offline
rehearsal test) for the full contract and offline-tested scenarios.

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

Only a future live `run` reads `RUNPOD_API_KEY`, `AGE_ARTIFACT_TOKEN`, and
`AGE_REAPER_SHARED_SECRET` from the operator's privately supplied environment.
Generate each independently with a cryptographic RNG (at least 32 printable
non-whitespace characters). Never reuse any of the three for another; never
put any of them in JSON, shell arguments, logs, review packets or commits.
`AGE_REAPER_SHARED_SECRET` never reaches the provider or the pod -- it only
HMACs the local `reaper_manifest.json`/`reaper_ack.json` handoff with the
independent reaper (see "Independent reaper" below) and must also be
supplied to that separate process via its own environment. Recovery can
terminate without the artifact token, but cannot download artifacts without it.

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
   `terminate_pod()` returns `ACK_204` or `NOT_FOUND_404` -- these are never
   collapsed into each other, since **404 also means "not accessible to the
   caller," not solely "no longer exists"** (official v2 semantics). Neither
   a DELETE response alone, nor a single ambiguous GET 404, is verified
   cleanup; see "Cleanup evidence contract" above for what actually is.
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
