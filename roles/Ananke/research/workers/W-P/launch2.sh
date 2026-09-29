#!/bin/sh
cd F:/Prometheus-worktrees/ananke-base-role/roles/Ananke/research/workers/W-P
python run_champ.py 369f5a5b main 2 3 > logs/l2_369_a.log 2>&1 &
python run_champ.py 369f5a5b main 4 5 > logs/l2_369_b.log 2>&1 &
( python run_champ.py 4781b0a1 main 2 6; python run_champ.py 4781b0a1 verify 6 ) > logs/l2_4781_a.log 2>&1 &
( python run_champ.py 4781b0a1 main 10; python run_champ.py 369f5a5b verify 6 ) > logs/l2_mix.log 2>&1 &
wait
echo ALLDONE
