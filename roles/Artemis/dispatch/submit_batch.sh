#!/bin/sh
# One submission per dispatch batch (MWO-0001 s10 ARTEMIS; MWO-0004 R2 envelope). usage: sh submit_batch.sh BATCH BASE_SHA
set -e
B="$1"; BASE="$2"; D="$(dirname "$0")/$B"
python3 - "$D/DRAW.json" <<'PY' | while read id thr; do
import json,sys
for r in json.load(open(sys.argv[1]))['draw']: print(r['id'], r['thread'] or 'thr-artemis-dispatch')
PY
  python3 -m fabric submit --as Artemis --cap research.repo_readonly --cap fabric.runtime==0.2 \
    --executor claude --model claude-opus-5-5 --wall-s 5400 --base "$BASE" \
    --thread "$thr" --key "$B-$id" --title "Artemis dispatch $id" --prompt-file "$D/$id.package.md" --replicas 1
done
