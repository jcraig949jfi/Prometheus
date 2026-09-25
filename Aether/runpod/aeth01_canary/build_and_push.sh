#!/bin/bash
# AETH-01 RunPod canary -- operator-invoked image build and push only.
#
# NOT RUN during local validation: no Docker daemon is available.
# Authenticate Docker out of band; never put credentials in this script
# or its arguments. This helper does not launch a pod or approve a run.
#
# Supply REGISTRY and an explicit IMAGE_TAG in the operator environment.
# A tag is only a publishing handle: deployment requires the pushed digest.

set -euo pipefail

: "${REGISTRY:?set REGISTRY to the destination registry/namespace (no credentials)}"
: "${IMAGE_TAG:?set IMAGE_TAG to an explicit version or run-specific tag}"

IMAGE="${REGISTRY}/aeth01-canary:${IMAGE_TAG}"
cd "$(dirname "$0")"

echo "[build_and_push] building ${IMAGE}"
docker build --platform linux/amd64 -t "${IMAGE}" .

echo "[build_and_push] pushing ${IMAGE}"
docker push "${IMAGE}"

echo "[build_and_push] done: ${IMAGE}"
echo '[build_and_push] Retrieve the pushed digest from the registry or inspect local RepoDigests:'
printf '  docker image inspect --format '\''{{json .RepoDigests}}'\'' %s\n' "${IMAGE}"
echo '[build_and_push] Bind the run-specific plan and approval to registry/repository@sha256:<digest>, not a tag.'
echo '[build_and_push] No pod was launched. Consult: python age_controller.py --help'
