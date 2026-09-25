# RunPod launch kit -- ACCEL_CANARY_RUNPOD_v1 (WRITTEN, NOT EXECUTED)

Engineering/conformance only. No result from a pod may enter the science branch;
the pod only re-runs the frozen canary and returns `ACCEL_EQUIVALENCE_*.json`.
No cloud call has been made from this kit. There is no RunPod key on M4.

## Files
| file | role |
|---|---|
| `orchestrate_runpod_canary.py` | controller: $3 ceiling check, reaper arm, ONE pod create, poll, fetch, ALWAYS terminate + verify absence, receipt |
| `runpod_api.py` | stdlib REST client (no redirects, bounded reads, non-default UA, key only from env, no transport retries) |
| `independent_reaper.py` | detached, create-less reaper: terminates the pod (and any pod named with the run prefix) at the hard deadline even if the controller dies |
| `pod_serve.py` | on-pod bearer-authed read-only server (status.json, ACCEL_EQUIVALENCE.json, canary.log) on :8080; refuses to run if a RunPod credential is in its env |

## What the pod does
1. `unset RUNPOD_API_KEY RUNPOD_API_TOKEN RUNPOD_TOKEN` -- FIRST line (RunPod injects
   the key into every pod; AETH-01 smoke receipt 2026-09-22, lines ~137-180).
2. Downloads the 13 pinned files from `raw.githubusercontent.com/.../<SHA>/roles/Aphrodite/engine/...`
   and verifies each sha256 (taken locally from `git show <SHA>:...`). Any mismatch aborts.
3. `pip install numpy==2.4.3` (optional; fasteval is exact with or without numpy).
4. `timeout <wall> python3 accel/run_canary.py --workers <vCPUs>` -> parts (a)(b)(c).
5. Serves the outputs until the controller terminates the pod.

## Cost / runtime (ASSUMED prices -- operator must confirm the live quote)
- Default kind `cpu`: 8 vCPU CPU pod (`cpu3c`/`cpu5c`, SECURE), assumed **$0.40/hr**.
  Hard wall-clock `--max-wall-min 90` -> worst-case estimate
  `0.40 x 1.5 h x 1.25 + 0.05 = $0.80`. The controller REFUSES if the estimate > $3.00.
  Under the $3 ceiling at $0.40/hr the absolute maximum would be ~5.9 h; the kit caps at 90 min.
- Expected actual runtime: boot + fetch + pip ~3-5 min; canary ~6-12 min on 8 vCPU
  (M4, 2 workers under contention: see ACCEL_EQUIVALENCE_runpod-backend_M4.json).
  Expected spend **~$0.10-0.15**.
- Fallback kind `gpu-host` (cheapest community GPU pod, ~$0.13-0.20/hr) uses the v2
  body shape that WAS smoke-tested on 2026-09-22; only its CPUs are used.

## What the operator must provide
1. **RunPod API key** in the controller's environment as `RUNPOD_API_KEY`
   (never on argv, never in a file in the repo). Not present on M4 today.
2. **Authorisation to spend** up to the printed estimate (<= $3.00): the
   `--i-accept-cost` flag, and the live **$/hr quote** for the chosen pod type via
   `--hourly` (the defaults above are assumptions).
3. **A pushed, public commit SHA** of branch `aphrodite/accel-runpod-2026-09-23`
   containing the 13 files (`--commit <SHA>`). The pod fetches from
   `github.com/jcraig949jfi/Prometheus` raw URLs, so the SHA must be reachable there
   anonymously.
4. **Confirmation of the CPU-pod create body** (REST v1: `computeType: CPU`,
   `cpuFlavorIds`, `vcpuCount`, `imageName`, `dockerEntrypoint`, `dockerStartCmd`).
   This dialect is UNVERIFIED on this account -- inspect it with `--print-body`
   (no provider call) against current RunPod docs, or choose `--kind gpu-host`.
5. **An empty pod inventory** at launch (the controller refuses otherwise), and a
   machine that stays up for the run (the detached reaper covers controller death,
   not host power loss -- check the console if the host goes down).

## Run
```
python orchestrate_runpod_canary.py --commit <SHA> --print-body          # dry run
python orchestrate_runpod_canary.py --commit <SHA> --hourly <quote> --i-accept-cost
```
Verdict is `EQUIVALENT` only if the pod's canary reports zero mismatches in (a), (b)
and (c). `NO_RESULT` or any mismatch is NOT equivalence.
