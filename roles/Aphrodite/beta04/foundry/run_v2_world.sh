#!/bin/sh
# E1 v2 pilot driver for ONE world: world -> qualify -> chain -> ablate, each in resumable runs of <= 13 CPU-min.
# Usage: run_v2_world.sh SECRETS_FILE SET INDEX [OUT]. The secret seed is read by qualify2.py and never printed.
SECRETS=$1; SET=$2; IDX=$3; OUT=${4:-pilot_v2}
export OMP_NUM_THREADS=1
cd "$(dirname "$0")"
mkdir -p "$OUT/logs"
WID=$(python qualify2.py world --secrets "$SECRETS" --set "$SET" --index "$IDX" --out "$OUT" | awk "{print \$1}")
echo "world $WID"
for step in qualify chain ablate; do
  for i in 1 2 3 4 5 6; do
    python qualify2.py $step --world "$WID" --out "$OUT" --cpu-min 13 > "$OUT/logs/${WID}_${step}_run$i.log" 2>&1
    if grep -q "^done $step" "$OUT/logs/${WID}_${step}_run$i.log"; then echo "$WID $step complete after run $i"; break; fi
    if grep -q Traceback "$OUT/logs/${WID}_${step}_run$i.log"; then echo "$WID $step TRACEBACK"; exit 1; fi
  done
done
