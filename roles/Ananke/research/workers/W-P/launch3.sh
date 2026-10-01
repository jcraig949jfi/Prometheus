#!/bin/sh
cd F:/Prometheus-worktrees/ananke-base-role/roles/Ananke/research/workers/W-P
( python stage2.py 4781b0a1 6 S,Msum 1 2 5 6 9 10; python stage2.py 4781b0a1 1 S,Msum 1 2 5 6 9 10; python stage2.py 4781b0a1 15 inbox,Msum 1 2 5 6 9 10 ) > logs/s2_4781.log 2>&1 &
( python stage2.py 369f5a5b 9 S,Msum 1 2 3 4 5; python stage2.py 369f5a5b 1 S,Msum 1 2 3 4 5; python stage2.py 369f5a5b 13 S,Msum 1 2 3 4 5 ) > logs/s2_369.log 2>&1 &
wait
echo ALLDONE
