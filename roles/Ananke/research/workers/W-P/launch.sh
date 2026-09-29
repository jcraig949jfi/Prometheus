#!/bin/sh
cd F:/Prometheus-worktrees/ananke-base-role/roles/Ananke/research/workers/W-P
python run_champ.py 369f5a5b main 1 2 3 4 5 6 7 8 9 10 11 > logs/main_369.log 2>&1 &
python run_champ.py 4781b0a1 main 1 2 3 4 > logs/main_4781_a.log 2>&1 &
python run_champ.py 4781b0a1 main 5 6 7 8 > logs/main_4781_b.log 2>&1 &
( python run_champ.py 4781b0a1 main 9 10 11; python run_champ.py 4781b0a1 verify 6 ) > logs/main_4781_c.log 2>&1 &
wait
echo ALLDONE
