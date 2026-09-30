#!/bin/bash
# W-T launch: 4 processes x 2 torch threads, ns 0x640, M 256
cd /f/Prometheus-worktrees/ananke-base-role/roles/Ananke/research/workers/W-T
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
( for P in PLANT_P1_J1 PLANT_P1_J0 PLANT_PF_J1 PLANT_PL_J1; do python wt.py $P 256 640 4,5 $P; echo "$P RC=$?"; done ) > logs/plants.log 2>&1 &
echo "plants shell $!" >> logs/pids.txt
python wt.py 4781b0a1 256 640 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15 4781b0a1 > logs/4781b0a1.log 2>&1 &
echo "4781b0a1 $!" >> logs/pids.txt
python wt.py 78f3b0ec 256 640 9,10,11,14,15 78f3b0ec > logs/78f3b0ec.log 2>&1 &
echo "78f3b0ec $!" >> logs/pids.txt
python wt.py e06701a5 256 640 5 e06701a5 > logs/e06701a5.log 2>&1 &
echo "e06701a5 $!" >> logs/pids.txt
wait
echo ALLDONE >> logs/pids.txt
