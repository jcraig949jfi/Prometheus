#!/usr/bin/env bash
# Repo-wide prior-work search for a packet or a claim (Odysseus READY protocol).
#   prior_work_search.sh REPO OUTFILE term [term ...]
# Greps origin/main fully, then for every other remote ref only the files it
# changed relative to its merge-base with main (branch-unique work), plus
# commit messages on all refs. Read-only.
set -uo pipefail
REPO=$1; OUT=$2; shift 2
g() { git -C "$REPO" "$@"; }
MAIN=origin/main
REFS=$(g for-each-ref --format='%(refname:short)' refs/remotes/origin | grep -v -e HEAD -e '^origin/main$')
{
  echo "# prior-work search $(date -u +%FT%H:%MZ)"
  echo "main = $(g rev-parse --short $MAIN); other refs searched (branch-unique files): $(echo "$REFS" | wc -l)"
  for t in "$@"; do
    echo; echo "## term: $t"
    echo "### origin/main (first 40 files)"
    g grep -l -i -F -e "$t" $MAIN 2>/dev/null | sed "s#^$MAIN:##" | head -40
    echo "### branch-unique hits"
    for r in $REFS; do
      base=$(g merge-base $MAIN "$r" 2>/dev/null) || continue
      files=$(g diff --name-only "$base" "$r" 2>/dev/null | head -2000)
      [ -z "$files" ] && continue
      echo "$files" | xargs -r git -C "$REPO" grep -l -i -F -e "$t" "$r" -- 2>/dev/null | sed "s#^#  #" | head -10
    done
    echo "### commit messages, all refs (first 15)"
    g log --all --oneline -i -F --grep="$t" 2>/dev/null | head -15
  done
} > "$OUT"
echo "wrote $OUT"
