#!/bin/bash
# W-V launch: 4 procs x 1 thread, ns 0x650 M 128 (PLAN s1/s4)
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1 WV_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python wv.py 4781b0a1 128 650 2,4,6,8 champA > logs/champA.log 2>&1 &
python wv.py 4781b0a1 128 650 10,12,14 champB > logs/champB.log 2>&1 &
python wv.py PMAJ 128 650 2,4,6,8,12 pmaj > logs/pmaj.log 2>&1 &
python wv.py PDICT 128 650 2,4,6,8,12 pdict > logs/pdict.log 2>&1 &
wait
echo ALLDONE
