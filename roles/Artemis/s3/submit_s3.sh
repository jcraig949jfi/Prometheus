#!/bin/sh
# S3 ONE SUBMISSION (principal Artemis, MWO-0004 G1). Frozen with S3_PROTOCOL.md s3; run once, after Odysseus
# confirms the canaries are planted. usage: sh submit_s3.sh <BASE_SHA>
set -e
BASE="$1"; [ -n "$BASE" ] || { echo "usage: submit_s3.sh BASE_SHA"; exit 2; }
D="$(dirname "$0")/draft"
for q in Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8 Q9 Q10 IP1 IP2; do
  python3 -m fabric submit --as Artemis --cap research.repo_readonly --cap fabric.runtime==0.2 \
    --executor claude --model claude-opus-5-5 --wall-s 5400 --base "$BASE" \
    --thread thr-s3 --key "s3-$q" --title "S3 $q" --prompt-file "$D/$q.package.md" --replicas 1
done
