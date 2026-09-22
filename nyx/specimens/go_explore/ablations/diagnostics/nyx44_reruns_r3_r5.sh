#!/bin/sh
# Repeat the repaired frozen controls (sha256 6ce4ed61...) unaltered; keep every receipt under its own name.
for r in 3 4 5; do
  start=$(date +%s)
  python /w/n3_c04_controls.py /pin > /dev/null 2> /w/_stderr_repaired_r$r.txt
  rc=$?
  cp /w/RECEIPT_N3_c04_2026-09-15.json /w/RECEIPT_N3_c04_2026-09-15_repaired_r$r.json
  echo "run r$r rc=$rc secs=$(( $(date +%s) - start ))"
done
