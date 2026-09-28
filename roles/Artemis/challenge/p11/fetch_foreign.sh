#!/bin/sh
# Read-only copies of the pinned NPE files into the scratch directory (PREREG_P11.md s6.1).
set -e
SCR=/tmp/claude-1000/-home-jcraig-Prometheus/78a7bd7b-da69-4758-859e-8a39e0df5734/scratchpad/p11
mkdir -p "$SCR/d764" "$SCR/aa58"
env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE git -C /home/jcraig/Prometheus archive d7641744d \
  roles/Nestor/campaigns/z80atlas-verify-2026-09-22/p11.py \
  roles/Nestor/campaigns/z80atlas-verify-2026-09-22/constants.py \
  roles/Nestor/campaigns/z80atlas-verify-2026-09-22/z8.py \
  roles/Nestor/campaigns/z80atlas-verify-2026-09-22/world.py \
  roles/Nestor/campaigns/z80atlas-verify-2026-09-22/grammar.py \
  roles/Nestor/campaigns/z80atlas-verify-2026-09-22/tasks.py \
  roles/Nestor/campaigns/z80atlas-verify-2026-09-22/anticheat.py \
  roles/Nestor/campaigns/z80atlas-forensics-2026-09-23/substrate/z8.py \
  roles/Nestor/campaigns/z80atlas-forensics-2026-09-23/P11_REASSAY.jsonl | tar -x -C "$SCR/d764"
env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE git -C /home/jcraig/Prometheus archive aa5833488 \
  roles/Nestor/campaigns/z80atlas-2026-09-19/z8.py roles/Nestor/campaigns/z80atlas-2026-09-19/grammar.py \
  | tar -x -C "$SCR/aa58"
find "$SCR/d764" "$SCR/aa58" -type f -name '*.py' -o -type f -name '*.jsonl' | sort | xargs sha256sum
