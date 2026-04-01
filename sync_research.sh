#!/bin/bash
# Sync research files from working directory to private repo backup
# Usage: bash sync_research.sh
# Or from Claude Code: ! bash sync_research.sh

SRC="F:/prometheus"
DST="F:/prometheus-research"

echo "Syncing research to private repo..."

# Sync each research directory
for dir in papers noesis docs journal; do
    if [ -d "$SRC/$dir" ]; then
        mkdir -p "$DST/$dir"
        cp -r "$SRC/$dir"/* "$DST/$dir/" 2>/dev/null
        echo "  $dir synced"
    fi
done

# Commit and push from the private repo
cd "$DST"
git config core.longpaths true
git add -A
git commit -m "Research sync $(date '+%Y-%m-%d %H:%M')" 2>/dev/null
git push origin research-full 2>/dev/null

echo "Done. Private repo updated."
