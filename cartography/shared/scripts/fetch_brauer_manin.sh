#!/bin/bash
# =============================================================================
# Brauer-Manin Obstruction Data — Clone & Extract
# =============================================================================
# There is no centralized "BM obstruction dataset." The data lives in
# researcher repos containing Magma/Sage scripts that catalog specific curves.
#
# This script clones the canonical sources and organizes them under
# cartography/physics/data/brauer_manin/ for Charon's consumption.
#
# Usage:
#     bash fetch_brauer_manin.sh           # Clone all repos
#     bash fetch_brauer_manin.sh --status  # Check what's already cloned
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DEST_DIR="$REPO_ROOT/cartography/physics/data/brauer_manin"

mkdir -p "$DEST_DIR"

# Researcher repositories with Brauer-Manin obstruction computations
declare -A REPOS=(
    # Sutherland: extensive rational point and Hasse principle computations
    ["sutherland_primes"]="https://github.com/AndrewVSutherland/primegaps"
    ["sutherland_smalljac"]="https://github.com/AndrewVSutherland/smalljac"

    # LMFDB contributors: curve databases with obstruction data
    ["lmfdb_scripts"]="https://github.com/LMFDB/lmfdb"

    # Explicitly BM-related computational data
    ["varilyalvarado_bm"]="https://github.com/avarilly/brauer-manin"

    # Poonen's rational points / obstruction data
    ["poonen_qpoints"]="https://github.com/bjorn-poonen/qpoints"
)

# Status-only mode
if [[ "${1:-}" == "--status" ]]; then
    echo "=== Brauer-Manin Repository Status ==="
    for name in "${!REPOS[@]}"; do
        target="$DEST_DIR/$name"
        if [ -d "$target/.git" ]; then
            cd "$target"
            commit=$(git log -1 --format='%h %s' 2>/dev/null || echo "unknown")
            echo "  OK: $name — $commit"
            cd "$DEST_DIR"
        else
            echo "  MISSING: $name — ${REPOS[$name]}"
        fi
    done
    exit 0
fi

echo "=== Fetching Brauer-Manin Obstruction Data ==="
echo "Destination: $DEST_DIR"
echo ""

CLONED=0
SKIPPED=0
FAILED=0

for name in "${!REPOS[@]}"; do
    url="${REPOS[$name]}"
    target="$DEST_DIR/$name"

    if [ -d "$target/.git" ]; then
        echo "  SKIP: $name (already cloned)"
        # Pull latest
        cd "$target"
        git pull --quiet 2>/dev/null || true
        cd "$DEST_DIR"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    echo "  Cloning $name..."
    echo "    URL: $url"

    # Shallow clone to save bandwidth (we want data, not full history)
    if git clone --depth 1 --quiet "$url" "$target" 2>/dev/null; then
        echo "    OK"
        CLONED=$((CLONED + 1))
    else
        echo "    FAILED — repo may not exist or be private"
        FAILED=$((FAILED + 1))
        # Some of these repos may not exist under these exact names.
        # That's expected — the researcher may use different naming.
        # Log the failure but continue.
    fi
done

echo ""
echo "=== Complete ==="
echo "  Cloned: $CLONED"
echo "  Skipped: $SKIPPED"
echo "  Failed: $FAILED"
echo ""
echo "NOTE: Brauer-Manin data is fragmented across active research."
echo "Some repos may not exist under the guessed names above."
echo "Check these canonical sources manually if clones fail:"
echo "  - Andrew Sutherland: math.mit.edu/~drew/"
echo "  - Anthony Varilly-Alvarado: math.rice.edu/~av15/"
echo "  - Bjorn Poonen: math.mit.edu/~poonen/"
echo ""
echo "After cloning, scan for .sage, .m (Magma), and .gp (PARI/GP) files:"
echo "  find $DEST_DIR -name '*.sage' -o -name '*.m' -o -name '*.gp' | head -50"

# Write manifest
cat > "$DEST_DIR/manifest.json" <<EOF
{
  "source": "Researcher repositories (GitHub)",
  "description": "Brauer-Manin obstruction computations and rational point catalogues",
  "fetched": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "repos": {
$(for name in "${!REPOS[@]}"; do
    echo "    \"$name\": \"${REPOS[$name]}\","
done)
    "_note": "Some repos may fail — data is fragmented across active research"
  },
  "status": {
    "cloned": $CLONED,
    "skipped": $SKIPPED,
    "failed": $FAILED
  }
}
EOF
echo "Manifest → $DEST_DIR/manifest.json"
