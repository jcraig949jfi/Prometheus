#!/bin/bash
# Apollo v2 — Resume from checkpoint (no cleanup)
#
# Usage: bash apollo/resume_v2.sh
# Monitor: python apollo/src/dashboard.py
# Logs:   tail -f apollo/apollo_v2_run.log

set -e

cd "$(dirname "$0")/.."
echo "Apollo v2 — resuming from $(pwd)"
echo "Start time: $(date)"

# Show latest checkpoint
LATEST=$(ls -1 apollo/checkpoints/checkpoint_gen_*.pkl 2>/dev/null | tail -1)
if [ -z "$LATEST" ]; then
    echo "WARNING: No checkpoint found — will start from scratch"
else
    echo "Resuming from: $LATEST"
fi

# Launch with nohup so it survives terminal close
PYTHONUNBUFFERED=1 nohup python apollo/src/apollo.py > apollo/apollo_v2_run.log 2>&1 &
PID=$!
echo "Apollo v2 PID: $PID"
echo "$PID" > apollo/apollo_v2.pid
echo "Log: apollo/apollo_v2_run.log"
echo ""
echo "Monitoring commands:"
echo "  tail -f apollo/apollo_v2_run.log"
echo "  python apollo/src/dashboard.py"
