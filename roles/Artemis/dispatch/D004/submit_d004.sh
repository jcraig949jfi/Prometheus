#!/bin/sh
# One submission for D004 (script executor). usage: sh submit_d004.sh BASE_SHA  (BASE = the freeze commit)
set -e
BASE="$1"; D="$(dirname "$0")"
python3 - "$D/BATCH.json" <<'PY' | while IFS='|' read id thr wall caps argv; do
import json,sys
b=json.load(open(sys.argv[1]))
for t in b['tasks']:
    argv=' '.join(['roles/Artemis/dispatch/D004/scripts/'+t['script'], t['cwd']]+t['args'])
    print('|'.join([t['id'], t['thread'], str(t['wall_s']), ' '.join(t['caps']), argv]))
PY
  set -- ; for c in $caps; do set -- "$@" --cap "$c"; done
  for a in $argv; do set -- "$@" "--arg=$a"; done  # = form: values may start with --
  python3 -m fabric submit --as Artemis --cap fabric.runtime==0.2 --cap compute.cpu.light "$@" \
    --executor script --script roles/Artemis/dispatch/run_frozen.py --wall-s "$wall" --base "$BASE" \
    --thread "$thr" --key "$id" --title "Artemis D004 $id (run frozen D003 analysis)" \
    --instruction "Run the frozen worker-authored analysis for $id unmodified (roles/Artemis/dispatch/D004/PLAN.md)." \
    --max-attempts 1 --replicas 1
done
