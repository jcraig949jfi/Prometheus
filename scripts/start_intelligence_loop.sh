#!/bin/bash
# Background launcher for the Intelligence Loop (Linux / macOS).
# Companion to start_intelligence_loop.bat. Uses nohup so no terminal
# attachment; logs to docs/intelligence_loop.log.
#
# Usage:
#   ./scripts/start_intelligence_loop.sh           # detached, no console
#   ./scripts/start_intelligence_loop.sh --foreground   # attached, see logs live
#
# To stop: `kill $(cat docs/intelligence_loop.pid)` or `pkill -f intelligence_loop.py`.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Env vars matching the on-disk .env defaults
export AGORA_REDIS_HOST="${AGORA_REDIS_HOST:-192.168.1.176}"
export AGORA_REDIS_PASSWORD="${AGORA_REDIS_PASSWORD:-prometheus}"
export PROMETHEUS_MACHINE="${PROMETHEUS_MACHINE:-$(hostname)}"
export PYTHONPATH="$REPO_ROOT"
export PYTHONIOENCODING="utf-8"

LOG="$REPO_ROOT/docs/intelligence_loop.log"
PID_FILE="$REPO_ROOT/docs/intelligence_loop.pid"
mkdir -p "$(dirname "$LOG")"

if [[ "${1:-}" == "--foreground" ]]; then
    echo "Intelligence loop starting in foreground. Ctrl+C to stop."
    exec python "$REPO_ROOT/scripts/intelligence_loop.py" --immediate
fi

# Background launch
nohup python "$REPO_ROOT/scripts/intelligence_loop.py" --immediate >> "$LOG" 2>&1 &
echo $! > "$PID_FILE"
echo "Intelligence loop launched in background (PID $(cat "$PID_FILE"))."
echo "Logs: $LOG"
echo "To stop: kill \$(cat $PID_FILE)"
