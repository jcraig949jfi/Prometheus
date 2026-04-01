#!/usr/bin/env bash
# Charon Phase 1: The First Crossing
# Ingests elliptic curves + modular forms, builds bridges, constructs landscape.
# Usage: bash charon/scripts/run_phase1.sh [max_conductor]
#
# One script to rule them all. James doesn't babysit terminals.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

MAX_CONDUCTOR="${1:-50000}"

echo "============================================================"
echo "CHARON — THE FIRST CROSSING"
echo "Max conductor: $MAX_CONDUCTOR"
echo "Started: $(date)"
echo "============================================================"

# Stage 1 + 2: Ingest + Build invariant vectors + Known bridges
echo ""
echo "[Stage 1-2] Ingesting from LMFDB and building bridges..."
python -c "
from charon.src.ingest import run_phase1
result = run_phase1(max_conductor=$MAX_CONDUCTOR)
print(f'Ingestion result: {result}')
"

# Stage 3: Embed + Test + Search
echo ""
echo "[Stage 3-4] Building geometric landscape..."
python -c "
from charon.src.embed import run_embedding
result = run_embedding(version=1)
if result:
    print(f'Embedding result: n={result[\"n_objects\"]}, clusters={result[\"n_clusters\"]}, recovery={result[\"recovery_rate\"]:.1%}')
    if not result['gate_passed']:
        print('WARNING: Quality gate FAILED. Embedding needs work.')
    else:
        print('Quality gate PASSED.')
else:
    print('ERROR: Embedding failed — insufficient data.')
"

echo ""
echo "============================================================"
echo "CROSSING COMPLETE: $(date)"
echo "============================================================"
