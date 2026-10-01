cd "$(dirname "$0")"
V=$1
for c in 0 1 2 3; do W2L_M=32 python t1_flip.py $c 4 $V > out/t1_${V}_$c.log 2>&1; done
