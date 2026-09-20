#!/bin/bash
# AETH-01 RunPod canary -- exact proposed launch command.
#
# NOT RUN by this repair cycle. This is the single command README.md
# proposes; running it requires: (1) explicit operator approval for
# this specific run, per AETHER_RUNPOD.md's "no Runpod spend without
# explicit operator approval, per run"; (2) `runpodctl` already
# authenticated out-of-band (this script never reads or embeds an API
# key); (3) IMAGE_NAME below pointing at an image already pushed by
# build_and_push.sh.
#
# Usage: IMAGE_NAME=<registry>/aeth01-canary:latest ./launch_pod.sh

set -euo pipefail

: "${IMAGE_NAME:?set IMAGE_NAME, e.g. IMAGE_NAME=docker.io/yourname/aeth01-canary:latest ./launch_pod.sh}"

# GPU type is the single cheapest CUDA-capable option available at
# launch time; this value is a placeholder for "cheapest available,"
# not a hard requirement (README.md).
GPU_TYPE="${GPU_TYPE:-NVIDIA RTX A4000}"

echo "[launch_pod] about to create a RunPod pod. This WILL incur cost."
echo "[launch_pod] image:    ${IMAGE_NAME}"
echo "[launch_pod] gpu type: ${GPU_TYPE}"
echo "[launch_pod] hard wall-clock cap enforced inside the container by watchdog.sh"
read -r -p "[launch_pod] type 'yes' to proceed: " confirm
if [ "${confirm}" != "yes" ]; then
    echo "[launch_pod] aborted, nothing launched"
    exit 1
fi

runpodctl create pod \
  --name aeth01-canary \
  --imageName "${IMAGE_NAME}" \
  --gpuType "${GPU_TYPE}" \
  --gpuCount 1 \
  --containerDiskSize 10 \
  --volumeSize 0 \
  --args "bash /app/watchdog.sh python3 /app/run_canary.py"

echo "[launch_pod] pod creation requested. Remember to run terminate_pod.sh when done."
echo "[launch_pod] log this run in Aether/AETHER_RUNPOD.md's spend ledger regardless of outcome."
