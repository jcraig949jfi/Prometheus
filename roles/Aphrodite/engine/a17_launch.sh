#!/usr/bin/env bash
# AMENDMENT 17 stage launcher. Usage: a17_launch.sh <stage> <workers>
# A17_FASTEVAL is set from A17_GATE_2026-09-26.json (s0.3c), never by hand.
cd "$(dirname "$0")" || exit 1
FE=$(python -c "import json;print(1 if json.load(open('A17_GATE_2026-09-26.json'))['FASTEVAL_ADMITTED'] else 0)")
export A17_FASTEVAL=$FE A17_WORKERS=$2
python -u a17.py "$1" > "A17_$(echo "$1" | tr a-z A-Z)_2026-09-26.log" 2>&1
echo "EXIT=$?" >> "A17_$(echo "$1" | tr a-z A-Z)_2026-09-26.log"
