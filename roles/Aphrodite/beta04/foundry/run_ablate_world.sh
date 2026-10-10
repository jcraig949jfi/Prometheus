#!/bin/sh
# Mechanism-ablation step for one world, in resumable runs of <= 13 CPU-min each.
SEED=$1
OUT=${2:-pilot}
export OMP_NUM_THREADS=1
cd "$(dirname "$0")"
for i in 1 2 3 4; do
  python qualify.py ablate --seed "$SEED" --out "$OUT" --cpu-min 13 > "$OUT/W$SEED/ablate_run$i.log" 2>&1
  if grep -q "^done ablation" "$OUT/W$SEED/ablate_run$i.log"; then echo "W$SEED ablation complete after run $i"; exit 0; fi
done
echo "W$SEED ablation not complete"
