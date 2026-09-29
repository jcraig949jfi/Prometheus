#!/bin/sh
cd /f/Prometheus-worktrees/ananke-base-role
export PYTHONDONTWRITEBYTECODE=1
W=roles/Ananke/research/workers/W-S
(python $W/run.py 2dccdaa5 256 630 4,5 champ_2dccdaa5 > $W/logs/champ_2dccdaa5.log 2>&1; python $W/run.py 8c37f32e 256 630 4,5 champ_8c37f32e > $W/logs/champ_8c37f32e.log 2>&1) &
python $W/run.py c16d5231 256 630 4,5 champ_c16d5231 > $W/logs/champ_c16d5231.log 2>&1
wait
