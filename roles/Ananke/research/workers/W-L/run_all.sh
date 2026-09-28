#!/bin/sh
cd "$(dirname "$0")"
for a in "0 0" "1 0" "2 0" "1 1" "2 1" "1 2" "2 2" "1 3" "2 3" "0 1"; do
  set -- $a
  python run_search.py --n $1 --seed $2 --device cuda > out/log_n$1_s$2.txt 2>&1 || echo "FAIL n$1 s$2" >> out/run_all.status
  echo "done n$1 s$2 $(date -u +%H:%M:%S)" >> out/run_all.status
done
echo ALLDONE >> out/run_all.status
