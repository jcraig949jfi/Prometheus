cd "$(dirname "$0")"
for c in 0 1 2 3; do python t1_flip.py $c 4 base > out/t1_base_$c.log 2>&1; done
