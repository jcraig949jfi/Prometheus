#!/bin/bash
cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
export PYTHONPATH=.
C=tyche/runs/v1_2026-09-30
run() { python -m tyche.v1.run_v1 --arm $1 --seed $2 --out $C/$1_s$2 --workers 13; echo "FINISHED $1_s$2 rc=$?"; }
run DE 1 & run V0 1 & wait
run DENR 1 & run DE 2 & wait
run V0 2 & run DENR 2 & wait
echo ALL_DONE
