#!/bin/bash
# AETH-01 RunPod canary -- explicit pod termination.
#
# NOT RUN by this repair cycle. Must be run as soon as `run_canary.py`
# has finished (or the watchdog has killed it) and `receipt.json` has
# been retrieved -- a pod left running past the canary's completion is
# pure wasted spend against the $19.93 / $3 caps (AETHER_RUNPOD.md).
#
# Usage: POD_ID=<id from launch_pod.sh output> ./terminate_pod.sh

set -euo pipefail

: "${POD_ID:?set POD_ID, e.g. POD_ID=abc123 ./terminate_pod.sh}"

echo "[terminate_pod] terminating pod ${POD_ID}"
runpodctl remove pod "${POD_ID}"
echo "[terminate_pod] done. Log actual cost and result in Aether/AETHER_RUNPOD.md's spend ledger now."
