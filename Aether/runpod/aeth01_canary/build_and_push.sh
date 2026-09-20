#!/bin/bash
# AETH-01 RunPod canary -- build and push the container image.
#
# NOT RUN by this repair cycle (README.md "Status"). Requires the
# operator to supply a registry to push to; no default is embedded so
# this cannot be run by accident against someone else's registry.
#
# Usage: REGISTRY=<your-registry> ./build_and_push.sh

set -euo pipefail

: "${REGISTRY:?set REGISTRY, e.g. REGISTRY=docker.io/yourname ./build_and_push.sh}"

IMAGE="${REGISTRY}/aeth01-canary:latest"
cd "$(dirname "$0")"

echo "[build_and_push] building ${IMAGE}"
docker build -t "${IMAGE}" .

echo "[build_and_push] pushing ${IMAGE}"
docker push "${IMAGE}"

echo "[build_and_push] done: ${IMAGE}"
echo "[build_and_push] next: edit launch_pod.sh's IMAGE_NAME to match, then review it before running"
