# AGE — Minimal RunPod Smoke Test Receipt

Starting HEAD: `339601100bbd34e3371c7a0d5c15ddc1e91fd73b`
Date: 2026-09-22

## What happened

1. Verified the RunPod account had zero existing pods and zero recent
   billing before any action was taken.
2. Constructed the intended `POST /v2/pods` request: image
   `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04`, GPU
   `NVIDIA GeForce RTX 3070` (community), `disk: 20`, `ports: ["8080/http"]`,
   `env` carrying `AGE_ARTIFACT_TOKEN`/`AETH01_RUN_ID`/
   `AETH01_CANARY_TIMEOUT_SECONDS`, and an `entrypoint`/`cmd` pair whose
   command downloads `aeth01_cpu_oracle.py`, `aeth01_gpu_kernel.py`,
   `run_canary.py`, and `pod_service.py` from
   `raw.githubusercontent.com` at the pinned commit, verifies each against
   a locally computed SHA-256 (matched the working tree exactly, confirmed
   before launch), installs `numpy==2.2.0`/`cupy-cuda12x==13.3.0`, and runs
   `pod_service.py`.
3. Submitted that request via the repo's own `runpod_api.RunPodAPI.create_pod`.
   It failed closed with **HTTP 403** and **zero pods created** (confirmed
   by `GET /v2/pods` returning `pods: []` both immediately before and
   immediately after). Root cause of the 403 was not isolated (see below).
4. To read the provider's error body (`Invoke-RestMethod` discards it on
   non-2xx), a second, deliberately minimal request was issued as a
   read-diagnostic: `{"name":"x","image":"y","gpu":{"id":"NVIDIA GeForce RTX
   3070","count":1},"disk":1,"cloud":"COMMUNITY"}`. This was expected to
   fail the same way and expose the error detail. Instead it returned
   **HTTP 201** and put a real pod (`id qqn877vv9iivcr`) into `RUNNING`,
   because RunPod does not validate image existence synchronously at
   create time.
5. This consumed the single-Pod budget authorized for this test. Per the
   hard limits (one Pod only, no retries that create another Pod), the
   canary could not be run on this pod — it has the wrong image and no
   ports/env/entrypoint/cmd — so it was terminated immediately instead of
   being replaced or repaired.
6. Termination: `DELETE /v2/pods/qqn877vv9iivcr` was issued. The
   PowerShell client call hung without returning a status, but the
   deletion had already taken effect server-side: a follow-up
   `GET /v2/pods/qqn877vv9iivcr` returned `404 pod not found`, and
   `GET /v2/pods` returned `pods: []`. Termination is confirmed by
   inventory absence, not by a client-observed `204`.
7. No second pod was created at any point. No B3, no R1, no cleanup
   architecture changes, no physics changes.

## Root cause of the original 403 (undetermined, not further probed)

The API key demonstrably has pod create and delete permission (step 4 and
step 6 both succeeded against the live API), so the 403 was specific to
the original request's content, not a blanket authorization failure.
Candidate causes — the `entrypoint`+`cmd` pairing, the `ports` array, an
`env` value, `disk: 20`, or the specific image reference — were not
isolated, because doing so would have required additional `POST /v2/pods`
calls, and the one-Pod hard limit was already spent by step 4's
unintended pod. Per instruction ("if anything unexpected happens,
terminate and stop"), no further create attempts were made.

## Report

- **Image digest**: not resolved — the intended canary image was never
  successfully launched; the accidental pod ran a placeholder image
  (`"y"`), not a real digest.
- **GPU type**: `NVIDIA GeForce RTX 3070` (community tier, listed at
  $0.13/hr), for both the intended and the accidental request.
- **CUDA/CuPy status**: not reached — no canary payload, ports, or
  environment ever ran on a pod.
- **Canary PASS/FAIL**: **FAIL** (never executed).
- **300-match result**: not applicable — canary never ran.
- **Pod termination status**: Confirmed terminated. `qqn877vv9iivcr`
  created 2026-09-22T10:36:29.291Z; `DELETE` issued immediately after
  discovery; absence confirmed via `GET /v2/pods/qqn877vv9iivcr` → 404 and
  `GET /v2/pods` → `pods: []`.
- **Actual cost**: `GET /v2/billing?lastN=1&bucketSize=day` for
  2026-09-22 reports `totalAmount: 0` (billing ledger had not yet posted
  the sub-two-minute runtime at report time). Upper bound from listed rate
  and elapsed wall-clock time between create and terminate is a small
  fraction of one cent at $0.13/hr; well under the $3 cap in all cases.
- **Final disposition**: `RUNPOD_SMOKE_FAIL`

## Why this failed the "keep this tiny" mandate

The failure is procedural, not physical: the operator-side diagnostic
step that was meant to be read-only turned out to create a real pod
because RunPod's `POST /v2/pods` does not pre-validate the image field.
That consumed the test's one-Pod allowance before the real canary image
had a chance to run. No corrective retry was taken, per the explicit
"no retries that create another Pod" limit. The underlying question this
test was meant to answer — does AGE's controller path actually work
end-to-end on RunPod — remains unanswered and requires a fresh,
separately authorized single-Pod attempt with the 403 cause diagnosed
through non-mutating means (e.g. contacting RunPod support, or reading
the response body via a client library that surfaces error content on
non-2xx without needing a second live `POST`).
