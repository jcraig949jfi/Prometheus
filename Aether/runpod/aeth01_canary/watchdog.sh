#!/bin/bash
# AETH-01 RunPod canary cost-control watchdog.
#
# Hard wall-clock kill switch: runs the given command, and if it has not
# exited within HARD_TIMEOUT_SECONDS, kills it. This bounds worst-case
# spend independently of whatever `run_canary.py` itself does (a hang,
# infinite loop, or CuPy install/import stall must not silently consume
# the whole $19.93 budget). README.md's cost-control calculation sizes
# this at 10 minutes, well under the ~17.6 minutes the $3 canary cap
# buys at the EXAMPLE-ONLY rate quoted there.
#
# Usage: watchdog.sh <command> [args...]
# A killed run still counts as spend (AETHER_RUNPOD.md) and must be
# logged in AETHER_RUNPOD.md's spend ledger regardless of outcome --
# this script does not do that logging itself (no network access
# assumed); the operator logs it after the pod is terminated.

set -u

HARD_TIMEOUT_SECONDS="${AETH01_CANARY_TIMEOUT_SECONDS:-600}"

if [ "$#" -lt 1 ]; then
    echo "usage: watchdog.sh <command> [args...]" >&2
    exit 2
fi

echo "[watchdog] hard timeout: ${HARD_TIMEOUT_SECONDS}s"
echo "[watchdog] running: $*"

timeout --signal=KILL "${HARD_TIMEOUT_SECONDS}" "$@"
status=$?

if [ "$status" -eq 137 ]; then
    echo "[watchdog] KILLED at ${HARD_TIMEOUT_SECONDS}s hard timeout -- this is a cost-control event, not a normal exit" >&2
fi

exit "$status"
