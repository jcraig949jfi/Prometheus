#!/bin/sh
# R4_A-001 full run, sequential arms, 4 procs each. Logs wall and peak RSS per arm.
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1
for spec in "POS 16" "N 8" "RW 8" "RS 8" "NEG 4"; do
  set -- $spec
  /usr/bin/time -f "$1 wall %e s peakRSS(parent) %M KB" -a -o run_times.txt python3 walks.py --arm $1 --walkers $2 --P 4 --out runs_$1.jsonl >> run_log.txt 2>&1
done
echo DONE >> run_log.txt
