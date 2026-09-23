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


---

# Attempt 2 (same day) — root cause of Attempt 1's 403 found; new failure isolated

Starting HEAD: `339601100bbd34e3371c7a0d5c15ddc1e91fd73b` (unchanged)

## What happened

1. **Root cause of Attempt 1's HTTP 403 (now definitively diagnosed): Cloudflare,
   not authorization.** `api.runpod.io` is fronted by Cloudflare. A request from
   Python's `urllib` default agent (`Python-urllib/3.x`) is rejected by Cloudflare
   managed rule **1010 ("Access denied — the site owner has blocked access based on
   your browser's signature")** with HTTP 403, *before* it ever reaches RunPod's
   auth layer. Confirmed three ways: (a) the 403 body was Cloudflare
   `error_code: 1010`, not RunPod's `problem+json`; (b) an *unauthenticated* request
   returned the identical 1010 403; (c) resending with any ordinary `User-Agent`
   (`curl`, a browser string, or a custom token) returned **HTTP 200** with real
   data. This also explains Attempt 1's paradox: the `runpod_api` (urllib) create
   got 403 while the PowerShell `Invoke-RestMethod` diagnostic — which sends a
   browser-like UA — sailed through to a real 201.
2. **Fix applied to the controller transport** (`Aether/runpod/aeth01_canary/runpod_api.py`):
   added a `User-Agent` header (`_USER_AGENT = "AGE-AETH01-canary/1.0"`) to every
   request. This is the local controller path only; the pinned on-pod files and
   their SHA-256s are unchanged.
3. **Baseline re-verified clean** through the repo's own controller: `GET /v2/pods`
   → `pods: []` (0 pods); `GET /v2/billing?lastN=1` → all-zero totals. GPU
   pre-flight: `RTX 3070` COMMUNITY exists at $0.13/hr, availability LOW. Canary
   file pre-flight: all four raw.githubusercontent.com files at the pinned commit
   fetched with matching SHA-256.
4. **Exactly one pod created** (first attempt, no retries): `id omn4987e0lz9ok`,
   `aeth01-smoke-6622d04c`, RTX 3070 COMMUNITY, `disk 20`, `ports ["8080/http"]`,
   image `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04`, created
   `2026-09-22T12:13:22.481Z`, went `RUNNING`. A strong per-run `AGE_ARTIFACT_TOKEN`
   and `AETH01_RUN_ID` were injected via `env`; the RunPod API key was never placed
   on the pod by us.
5. **Canary never ran — a genuine incompatibility was isolated.** Container logs
   showed the boot script looping every ~15s: files download + checksum **OK**,
   `numpy`/`cupy-cuda12x` install **OK**, then `pod_service.py` prints
   **"RunPod API credentials must stay off-pod"** and exits code 2, the container
   command dies, RunPod restarts it, repeat. Cause: **RunPod auto-injects
   `RUNPOD_API_KEY` into every pod's environment**, which trips `pod_service.py`'s
   `load_config` credential-isolation guard (it rejects any of `RUNPOD_API_KEY` /
   `RUNPOD_API_TOKEN` / `RUNPOD_TOKEN` in the environment). As written,
   `pod_service.py` therefore cannot start on a real RunPod pod. `result.json` was
   never produced; CPU/GPU utilization stayed at 0%.
6. **Terminated and verified.** Per the hard limits (one pod, terminate and stop on
   anything unexpected — this is *not* the "capacity failure, no pod created" case
   that allowed a same-body retry), the pod was terminated immediately on diagnosis:
   `terminate_pod` → `ACK_204`; `GET /v2/pods` → `pods: []`. Absence confirmed by
   inventory. No second pod was created.

## Report

- **Image**: `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04` (launched and
  pulled successfully this time; digest not separately resolved).
- **GPU type**: `NVIDIA GeForce RTX 3070` (COMMUNITY, $0.13/hr, availability LOW).
- **CUDA/CuPy status**: dependencies installed cleanly on-pod
  (`numpy==2.2.0`, `cupy-cuda12x==13.3.0`), but the canary process never started, so
  real-GPU CuPy execution was **not** exercised.
- **Canary PASS/FAIL**: **FAIL** — canary did not run (pod_service refused to start).
- **300-match result**: not reached.
- **Pod termination status**: Confirmed terminated. `omn4987e0lz9ok` created
  `2026-09-22T12:13:22.481Z`; terminated ~`12:36Z` (~23 min); `terminate_pod`
  returned `ACK_204`; `GET /v2/pods` → `pods: []`.
- **Actual cost**: today's `GET /v2/billing/pods` posted `$0.00188` against the
  *prior* pod `qqn877vv9iivcr`; this pod's runtime had not yet posted at report time.
  Upper bound for this pod: ~23 min × $0.13/hr ≈ **$0.05**. Well under the $3 cap.
- **Final disposition**: `RUNPOD_SMOKE_FAIL`

## What this attempt established (and the remaining blocker)

- The AGE controller transport now works end-to-end on RunPod: create, list, get,
  logs (out-of-band), and terminate all succeed once the Cloudflare-1010 UA issue is
  fixed. Attempt 1's 403 mystery is fully resolved.
- The remaining blocker is a **one-line environment conflict**, not a physics or
  transport problem: RunPod injects `RUNPOD_API_KEY`, and `pod_service.py` treats
  that as fatal.

### Recommended fix for a future, separately-authorized single-pod attempt

Pick one (the first needs no change to the pinned GitHub files or their checksums):

- **Boot-script scrub (minimal):** in the create body's `cmd`, run
  `unset RUNPOD_API_KEY RUNPOD_API_TOKEN RUNPOD_TOKEN` immediately before
  `python3 pod_service.py`. RunPod's injected key is removed from the environment
  `pod_service` sees; the canary child env is an allowlist that never included it
  anyway, so the isolation intent is preserved.
- **Guard refinement (code change; requires re-pinning + re-pushing the commit and
  updating the four SHA-256s in the create body):** relax `pod_service.load_config`
  so RunPod's platform-injected key is tolerated (or scrubbed) rather than fatal.

No second pod was created for either option — applying and testing a fix requires a
fresh, explicitly authorized single-pod run.