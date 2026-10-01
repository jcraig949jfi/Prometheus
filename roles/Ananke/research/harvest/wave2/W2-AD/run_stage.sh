#!/bin/bash
# usage: run_stage.sh STAGE N FAM [FAM...]   -- loops <10-min python invocations (1 thread each) until done
cd "$(dirname "$0")"
STAGE=$1; N=$2; shift 2
for F in "$@"; do
  for k in 1 2 3 4 5 6 7 8; do
    out=$(timeout 590 python census.py $F 0 $N $STAGE 1 2>&1)
    echo "$out" >> out/log_${STAGE}_${F}.txt
    echo "$out" | grep -q "STOP: wall budget" || break
  done
  echo "DONE $STAGE $F" >> out/log_${STAGE}_${F}.txt
done
