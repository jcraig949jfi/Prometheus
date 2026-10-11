#!/bin/sh
# Pilot driver for one world: generate, then qualify in resumable runs of <= 13 CPU-min each.
set -e
SEED=$1
OUT=${2:-pilot}
export OMP_NUM_THREADS=1
cd "$(dirname "$0")"
[ -f "$OUT/W$SEED/WORLD_SEALED.json" ] || python qualify.py world --seed "$SEED" --out "$OUT"
for i in 1 2 3 4 5 6; do
  python qualify.py qualify --seed "$SEED" --out "$OUT" --cpu-min 13 > "$OUT/W$SEED/qualify_run$i.log" 2>&1
  if grep -q "^done" "$OUT/W$SEED/qualify_run$i.log"; then echo "W$SEED complete after run $i"; exit 0; fi
done
echo "W$SEED not complete"
