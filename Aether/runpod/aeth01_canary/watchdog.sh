#!/bin/bash
# AETH-01 legacy command timeout wrapper; NOT a pod billing watchdog.
#
# Kills the command on timeout, not the pod. Stopping a command or container
# does NOT stop pod billing or bound spend. Only external controller/operator
# termination does that. Use pod_service.py for authenticated artifact retrieval
# before teardown; do NOT wrap that service in this timeout (it must stay alive).
#
# Usage: watchdog.sh <command> [args...]
# A killed run still counts as spend (AETHER_RUNPOD.md) and must be
# logged in AETHER_RUNPOD.md's spend ledger regardless of outcome --
# this script does not do that logging itself (no network access
# assumed); the operator logs it after the pod is terminated.

set -u

HARD_TIMEOUT_SECONDS="${AETH01_CANARY_TIMEOUT_SECONDS-600}"

# GNU timeout treats zero as disabled: explicitly reject zero, empty, fractions,
# negatives, and values outside the same 1..600 contract as pod_service.py.
if [[ ! "$HARD_TIMEOUT_SECONDS" =~ ^[0-9]{1,3}$ ]]; then
    echo "[watchdog] AETH01_CANARY_TIMEOUT_SECONDS must be an integer in 1..600" >&2
    exit 2
fi
if (( 10#$HARD_TIMEOUT_SECONDS < 1 || 10#$HARD_TIMEOUT_SECONDS > 600 )); then
    echo "[watchdog] AETH01_CANARY_TIMEOUT_SECONDS must be an integer in 1..600" >&2
    exit 2
fi

if [ "$#" -lt 1 ]; then
    echo "usage: watchdog.sh <command> [args...]" >&2
    exit 2
fi

echo "[watchdog] hard timeout: ${HARD_TIMEOUT_SECONDS}s"
echo "[watchdog] pod billing continues until external termination" >&2

timeout --signal=KILL "${HARD_TIMEOUT_SECONDS}" "$@"
status=$?

if [ "$status" -eq 137 ]; then
    echo "[watchdog] command killed; pod still requires external termination" >&2
    status=124
fi

exit "$status"
