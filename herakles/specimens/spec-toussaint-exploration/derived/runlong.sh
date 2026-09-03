#!/bin/bash
cd "$(dirname "$0")"
CK=0,100,300,500,1000,2000,3000
N=0
for B in 0.1 0.0; do for S in $(seq 1 12); do
  f=sens_long/a0.03_b${B}_s${S}.csv
  [ -s "$f" ] || { ./hct01.exe run L 0 3000 100 30 0.03 1.0 $B 2000 $S $((S+4000)) 1 1 0.1 0.0 $CK > "$f" & N=$((N+1)); [ $((N%12)) -eq 0 ] && wait; }
done; done
wait
echo "DONE $(ls sens_long/*.csv | wc -l)"
