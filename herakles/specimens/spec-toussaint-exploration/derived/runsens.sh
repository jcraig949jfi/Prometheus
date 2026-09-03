#!/bin/bash
cd "$(dirname "$0")"
CK=0,50,100,200,500,1000
N=0
# beta sensitivity: 0.01 instead of 0.1, paired against beta=0
for A in 0.03 0.06; do for B in 0.01 0.0; do for S in $(seq 1 30); do
  f=sens/b01_a${A}_b${B}_s${S}.csv
  [ -s "$f" ] || { ./hct01.exe run X 0 1000 100 30 $A 1.0 $B 2000 $S $((S+4000)) 1 1 0.01 0.0 $CK > "$f" & N=$((N+1)); [ $((N%12)) -eq 0 ] && wait; }
done; done; done
# promoter sensitivity: promoters do not mutate
for A in 0.03; do for B in 0.1 0.0; do for S in $(seq 1 30); do
  f=sens/nopm_a${A}_b${B}_s${S}.csv
  [ -s "$f" ] || { ./hct01.exe run X 0 1000 100 30 $A 1.0 $B 2000 $S $((S+4000)) 0 1 0.1 0.0 $CK > "$f" & N=$((N+1)); [ $((N%12)) -eq 0 ] && wait; }
done; done; done
wait
echo "DONE $(ls sens/*.csv | wc -l)"
