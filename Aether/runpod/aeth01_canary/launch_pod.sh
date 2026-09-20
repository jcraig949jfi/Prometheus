#!/bin/bash
# AETH-01 RunPod canary -- exact proposed launch command, with
# fail-closed budget-derived cost control and automatic pod cleanup.
#
# NOT RUN by this repair cycle. This is the single command README.md
# proposes; running it requires: (1) explicit operator approval for
# this specific run, per AETHER_RUNPOD.md's "no Runpod spend without
# explicit operator approval, per run"; (2) `runpodctl` already
# authenticated out-of-band (this script never reads or embeds an API
# key); (3) IMAGE_NAME below pointing at an image already pushed by
# build_and_push.sh.
#
# Usage:
#   IMAGE_NAME=<registry>/aeth01-canary:latest \
#   HOURLY_RATE=0.17 \
#   MAX_DOLLAR_BUDGET=3.00 \
#   ./launch_pod.sh
#
# HOURLY_RATE and MAX_DOLLAR_BUDGET have NO default: this script fails
# closed rather than silently launching against a stale EXAMPLE-ONLY
# rate (README.md's cost-control calculation is illustrative, not a
# live quote). The operator must read the actual $/hr price for
# GPU_TYPE off the RunPod console at launch time and pass it in.

set -euo pipefail

: "${IMAGE_NAME:?set IMAGE_NAME, e.g. IMAGE_NAME=docker.io/yourname/aeth01-canary:latest ./launch_pod.sh}"
: "${HOURLY_RATE:?set HOURLY_RATE to the ACTUAL $/hr price for GPU_TYPE, read off the RunPod console at launch time (no default -- README.md's rate is EXAMPLE ONLY, not live)}"
: "${MAX_DOLLAR_BUDGET:?set MAX_DOLLAR_BUDGET, e.g. MAX_DOLLAR_BUDGET=3.00 -- must be <= the \$3 canary sub-cap in this package's README.md, itself inside the \$19.93 hard cap (AETHER_RUNPOD.md)}"

# GPU type is the single cheapest CUDA-capable option available at
# launch time; this value is a placeholder for "cheapest available,"
# not a hard requirement (README.md).
GPU_TYPE="${GPU_TYPE:-NVIDIA RTX A4000}"

# Fraction of MAX_DOLLAR_BUDGET this script will let the CONTAINER'S
# OWN compute time consume; the remainder is margin for pod boot/image
# pull time (billed, but not controllable by an in-container timeout)
# and for HOURLY_RATE estimation error. Not itself a hard guarantee --
# see "Known unresolved risks" in README.md.
SAFETY_FACTOR="${SAFETY_FACTOR:-0.5}"

# Fail closed on non-numeric or non-positive inputs -- a typo here must
# abort, not silently compute a bogus (or worse, unbounded) timeout.
_is_positive_number() {
    case "$1" in
        ''|*[!0-9.]*) return 1 ;;
        *) awk -v v="$1" 'BEGIN { exit !(v > 0) }' ;;
    esac
}
for _name in HOURLY_RATE MAX_DOLLAR_BUDGET SAFETY_FACTOR; do
    _val="${!_name}"
    if ! _is_positive_number "${_val}"; then
        echo "[launch_pod] ${_name}='${_val}' is not a positive number -- aborting, nothing launched" >&2
        exit 1
    fi
done

# Derived hard wall-clock cap, in seconds, passed into the container so
# watchdog.sh enforces THIS run's actual budget rather than its own
# generic 600s default.
MAX_RUNTIME_SECONDS=$(awk -v b="${MAX_DOLLAR_BUDGET}" -v r="${HOURLY_RATE}" -v s="${SAFETY_FACTOR}" \
    'BEGIN { printf "%d", (b / r) * 3600 * s }')
if [ "${MAX_RUNTIME_SECONDS}" -le 0 ]; then
    echo "[launch_pod] derived MAX_RUNTIME_SECONDS=${MAX_RUNTIME_SECONDS} <= 0 -- aborting, nothing launched" >&2
    exit 1
fi
# Poll deadline for THIS script's own wait loop below: the in-container
# budget above, plus a fixed grace window for pod boot/image-pull time
# (which does not count against the container's own timer).
POLL_DEADLINE_SECONDS=$((MAX_RUNTIME_SECONDS + 300))

echo "[launch_pod] hourly rate (operator-supplied, NOT fetched live):  \$${HOURLY_RATE}/hr"
echo "[launch_pod] dollar budget cap:                                 \$${MAX_DOLLAR_BUDGET}"
echo "[launch_pod] safety factor:                                     ${SAFETY_FACTOR}"
echo "[launch_pod] derived in-container hard timeout (watchdog.sh):   ${MAX_RUNTIME_SECONDS}s"
echo "[launch_pod] this script's own poll deadline (timeout + margin): ${POLL_DEADLINE_SECONDS}s"
echo "[launch_pod] about to create a RunPod pod. This WILL incur cost."
echo "[launch_pod] image:    ${IMAGE_NAME}"
echo "[launch_pod] gpu type: ${GPU_TYPE}"
read -r -p "[launch_pod] type 'yes' to proceed: " confirm
if [ "${confirm}" != "yes" ]; then
    echo "[launch_pod] aborted, nothing launched"
    exit 1
fi

POD_ID=""
# Fail-closed cleanup: fires on ANY exit path of this script -- normal
# completion, an error (set -e), or an interrupt (Ctrl-C/SIGTERM) -- so
# a pod is never left running just because this script stopped. This
# is defense in depth alongside watchdog.sh's in-container timeout, not
# a replacement for it: if BOTH this script's process and its trap are
# killed uncleanly (e.g. the host running this script loses power), no
# local mechanism fires and the pod keeps billing until the operator
# checks the RunPod console directly (residual provider-side billing
# risk, README.md "Known unresolved risks" -- unavoidable from a local
# script alone).
cleanup() {
    local status=$?
    if [ -n "${POD_ID}" ]; then
        echo "[launch_pod] cleanup: terminating pod ${POD_ID} (exit status ${status})" >&2
        if ! runpodctl remove pod "${POD_ID}"; then
            echo "[launch_pod] WARNING: automatic termination FAILED for ${POD_ID}." >&2
            echo "[launch_pod] terminate it manually NOW: POD_ID=${POD_ID} ./terminate_pod.sh" >&2
            echo "[launch_pod] then verify on the RunPod console directly -- do not assume this trap's failure was harmless." >&2
        fi
    fi
    exit "${status}"
}
trap cleanup EXIT INT TERM

CREATE_OUTPUT=$(runpodctl create pod \
  --name aeth01-canary \
  --imageName "${IMAGE_NAME}" \
  --gpuType "${GPU_TYPE}" \
  --gpuCount 1 \
  --containerDiskSize 10 \
  --volumeSize 0 \
  --cost "${HOURLY_RATE}" \
  --env "AETH01_CANARY_TIMEOUT_SECONDS=${MAX_RUNTIME_SECONDS}" \
  --env "AETH01_CANARY_HOURLY_RATE=${HOURLY_RATE}" \
  --env "AETH01_CANARY_MAX_DOLLAR_BUDGET=${MAX_DOLLAR_BUDGET}" \
  --args "bash /app/watchdog.sh python3 /app/run_canary.py")
echo "${CREATE_OUTPUT}"

# runpodctl's exact stdout format for `create pod` is UNVERIFIED by
# this package (no prior real run) -- this extraction is best-effort
# text scraping, not a parsed structured field. If it fails, this
# script aborts rather than guessing, because an unknown POD_ID means
# the cleanup trap above cannot terminate anything.
POD_ID=$(printf '%s\n' "${CREATE_OUTPUT}" | grep -oE '[a-z0-9]{10,}' | tail -1 || true)
if [ -z "${POD_ID}" ]; then
    echo "[launch_pod] FAILED to parse a pod ID from the output above." >&2
    echo "[launch_pod] if a pod WAS created, it is now running with NO automatic cleanup registered." >&2
    echo "[launch_pod] find it manually NOW: runpodctl get pod   (or check the RunPod console)" >&2
    echo "[launch_pod] then terminate it manually: POD_ID=<id> ./terminate_pod.sh" >&2
    exit 1
fi
echo "[launch_pod] pod created: ${POD_ID}"
echo "[launch_pod] the cleanup trap above will now terminate ${POD_ID} when this script exits, for any reason."

echo "[launch_pod] polling pod status (best-effort; 'runpodctl get pod' output format is unverified by this package) until it stops, or ${POLL_DEADLINE_SECONDS}s elapses..."
elapsed=0
while [ "${elapsed}" -lt "${POLL_DEADLINE_SECONDS}" ]; do
    sleep 15
    elapsed=$((elapsed + 15))
    STATUS_OUTPUT=$(runpodctl get pod "${POD_ID}" 2>&1 || true)
    echo "[launch_pod] poll at ${elapsed}s: ${STATUS_OUTPUT}"
    if ! printf '%s' "${STATUS_OUTPUT}" | grep -qi 'RUNNING'; then
        echo "[launch_pod] pod no longer reports RUNNING -- assuming the canary process finished"
        break
    fi
done
if [ "${elapsed}" -ge "${POLL_DEADLINE_SECONDS}" ]; then
    echo "[launch_pod] poll deadline (${POLL_DEADLINE_SECONDS}s) reached without the pod leaving RUNNING -- terminating now regardless; cost control takes precedence over waiting longer" >&2
fi

echo "[launch_pod] retrieve receipt.json / logs NOW, before this script exits and the cleanup trap terminates the pod:"
echo "[launch_pod]     runpodctl get pod ${POD_ID}   # confirm status"
echo "[launch_pod]     (the printed receipt summary, minus any mismatches payload, is also on stdout -- retrievable via the pod's log output if the template/image exposes it)"
echo "[launch_pod] log this run in Aether/AETHER_RUNPOD.md's spend ledger regardless of outcome, BEFORE this script's trap terminates the pod."
