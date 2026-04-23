#!/bin/bash
# ============================================================
# Apollo v2 — Launch Script
# Evolutionary search over Frame H primitive compositions.
#
# Usage:
#   cd F:/Prometheus/apollo && bash launch_apollo.sh          # resume or start
#   cd F:/Prometheus/apollo && bash launch_apollo.sh --fresh   # clear old state, start from gen 0
#
# To stop:  Ctrl+C (checkpoint saves every 10 gens, you lose at most 10)
# To resume: just run the same command again (auto-recovers from checkpoint)
# ============================================================

set -euo pipefail

APOLLO_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$APOLLO_DIR/src"
LOG_DIR="$APOLLO_DIR/logs"
CKPT_DIR="$APOLLO_DIR/checkpoints"
FRESH=false

for arg in "$@"; do
    case $arg in
        --fresh) FRESH=true ;;
    esac
done

echo "============================================================"
echo "  APOLLO v2 — Evolutionary Primitive Routing"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"
echo ""

# ── Preflight checks ──────────────────────────────────────────
echo "[preflight] Checking GPU..."
python -c "
import torch
assert torch.cuda.is_available(), 'No CUDA GPU!'
name = torch.cuda.get_device_name(0)
vram = torch.cuda.get_device_properties(0).total_memory / 1e9
print(f'  GPU: {name} ({vram:.1f} GB)')
" || { echo "FATAL: No GPU available"; exit 1; }

echo "[preflight] Checking forge_primitives..."
python -c "
import sys; sys.path.insert(0, '$SRC_DIR')
from apollo import _resolve_path, load_config
config = load_config('$APOLLO_DIR/configs/manifest.yaml')
prim_dir = _resolve_path(config['primitives_dir'])
sys.path.insert(0, prim_dir)
import forge_primitives as fp
n = len([x for x in dir(fp) if not x.startswith('_') and callable(getattr(fp, x))])
print(f'  forge_primitives: {n} functions')
" || { echo "FATAL: forge_primitives not importable"; exit 1; }

echo "[preflight] Checking trap_generator..."
python -c "
import sys; sys.path.insert(0, '$SRC_DIR')
from apollo import _resolve_path, load_config
config = load_config('$APOLLO_DIR/configs/manifest.yaml')
trap_path = _resolve_path(config['trap_generator'])
from pathlib import Path
assert Path(trap_path).exists(), f'Not found: {trap_path}'
print(f'  trap_generator: OK')
" || { echo "FATAL: trap_generator not found"; exit 1; }

# ── Handle --fresh flag ───────────────────────────────────────
if [ "$FRESH" = true ]; then
    echo ""
    echo "[fresh] Clearing old state..."
    rm -f "$CKPT_DIR"/checkpoint_gen_*.pkl 2>/dev/null && echo "  Cleared checkpoints" || true
    rm -f "$APOLLO_DIR"/lineage/lineage_v2.jsonl 2>/dev/null && echo "  Cleared lineage" || true
    rm -f "$APOLLO_DIR"/graveyard/graveyard_v2.jsonl 2>/dev/null && echo "  Cleared graveyard" || true
    rm -f "$APOLLO_DIR"/dashboard/status_v2.jsonl 2>/dev/null && echo "  Cleared dashboard" || true
    rm -f "$LOG_DIR"/apollo_run.jsonl 2>/dev/null && echo "  Cleared run log" || true
    echo "  Starting from generation 0."
fi

# ── Handle existing checkpoints ───────────────────────────────
if ls "$CKPT_DIR"/checkpoint_gen_*.pkl 1>/dev/null 2>&1; then
    LATEST=$(ls -t "$CKPT_DIR"/checkpoint_gen_*.pkl | head -1)
    GEN=$(python -c "
import pickle
with open('$LATEST', 'rb') as f:
    d = pickle.load(f)
print(d.get('generation', '?'))
")
    echo ""
    echo "[checkpoint] Found existing checkpoints (latest: gen $GEN)"
    echo "  Apollo will RESUME from gen $GEN."
    echo "  To start fresh: bash launch_apollo.sh --fresh"
    echo ""
fi

# ── Create output directories ─────────────────────────────────
mkdir -p "$LOG_DIR" "$CKPT_DIR" "$APOLLO_DIR/lineage" "$APOLLO_DIR/graveyard" "$APOLLO_DIR/dashboard"

# ── Launch ────────────────────────────────────────────────────
echo "[launch] Starting Apollo v2 (no generation limit)"
echo "  Logs:        $LOG_DIR/apollo_run.jsonl"
echo "  Console log: $LOG_DIR/apollo_console_$(date '+%Y%m%d_%H%M%S').log"
echo "  Checkpoints: $CKPT_DIR/"
echo "  PID file:    $APOLLO_DIR/apollo_v2.pid"
echo ""
echo "  Stop:   Ctrl+C"
echo "  Resume: bash launch_apollo.sh"
echo ""
echo "============================================================"
echo ""

# Save PID for external monitoring
echo $$ > "$APOLLO_DIR/apollo_v2.pid"

# Run with unbuffered output so logs flush immediately
cd "$SRC_DIR"
exec python -u apollo.py 2>&1 | tee -a "$LOG_DIR/apollo_console_$(date '+%Y%m%d_%H%M%S').log"
