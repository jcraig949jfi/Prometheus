#!/bin/bash
cd "$(dirname "$0")"
CK=0,5,10,15,20,30,40,50,65,80,100,125,150,175,200,250,300,350,400,500,600,700,800,900,1000
N=0
for A in 0.03 0.06; do for B in 0.1 0.0; do for S in $(seq 1 30); do
  f=grid/a${A}_b${B}_s${S}.csv
  if [ ! -s "$f" ]; then
    ./hct01.exe run A${A}_B${B}_S${S} 0 1000 100 30 $A 1.0 $B 2000 $S $((S+4000)) 1 1 0.1 0.0 $CK > "$f" &
    N=$((N+1)); if [ $((N % 12)) -eq 0 ]; then wait; fi
  fi
done; done; done
wait
echo "DONE $(ls grid/*.csv | wc -l) files"
