#!/bin/sh
export CUDA_VISIBLE_DEVICES=-1 OMP_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1
timeout 600 python n_runs.py ka 2a776b0a3245a735 inbox 256 || { echo KA_FAIL; exit 3; }
for ns in 4e01 4e02 4e03; do
 for ga in 2a776b0a3245a735:inbox 6edf00dccf85ffd6:inbox 48c5f7d48604ca8b:site_all 047aa8ed8357fa1c:channel_all b7e296268480ebee:inbox 561ed71c41350fe1:site_all; do
  g=${ga%%:*}; a=${ga##*:}
  timeout 600 python n_runs.py run $g $a 256 $ns || echo "FAIL $g $a $ns"
 done
done
echo BATCH_DONE
