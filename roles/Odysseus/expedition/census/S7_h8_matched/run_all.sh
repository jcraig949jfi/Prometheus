#!/bin/bash
# S7 runner: at most 2 concurrent processes. Logs to run_log.txt
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1
( /usr/bin/time -f "seed2_probe cpu_user=%U cpu_sys=%S wall=%e" python3 -B seed2_probe.py ) >> run_log.txt 2>&1 &
( for s in 6 9 11; do /usr/bin/time -f "pop_probe s$s cpu_user=%U cpu_sys=%S wall=%e" python3 -B pop_probe.py $s; done ) >> run_log_pop.txt 2>&1 &
wait
echo ALLDONE >> run_log.txt
