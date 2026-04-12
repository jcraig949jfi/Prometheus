#!/bin/bash
# =============================================================================
# Charon Data Pipeline — One-shot Runner
# =============================================================================
# Runs all Charon data acquisition scripts in sequence.
# Designed for fire-and-forget execution per feedback_rhea_scripts.md
#
# Usage:
#     bash run_charon_pipeline.sh           # Full execution
#     bash run_charon_pipeline.sh --dry-run # Preview only
#     bash run_charon_pipeline.sh quick     # Picard-Fuchs + McKay-Thompson only (fast)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/../../logs"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG="$LOG_DIR/charon_pipeline_${TIMESTAMP}.log"

DRY_RUN=""
MODE="full"

for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN="--dry-run" ;;
        quick)     MODE="quick" ;;
    esac
done

echo "=== Charon Data Pipeline ===" | tee "$LOG"
echo "Started: $(date -u)" | tee -a "$LOG"
echo "Mode: $MODE" | tee -a "$LOG"
echo "Log: $LOG" | tee -a "$LOG"
echo "" | tee -a "$LOG"

# Track timing
SECONDS=0

# -----------------------------------------------
# Step 1: Picard-Fuchs (fast — single file download)
# -----------------------------------------------
echo "[1/4] Picard-Fuchs operators..." | tee -a "$LOG"
python "$SCRIPT_DIR/fetch_charon_blockers.py" picard-fuchs $DRY_RUN 2>&1 | tee -a "$LOG"
echo "" | tee -a "$LOG"

# -----------------------------------------------
# Step 2: McKay-Thompson coefficients (fast — ~26 OEIS queries)
# -----------------------------------------------
echo "[2/4] McKay-Thompson series..." | tee -a "$LOG"
python "$SCRIPT_DIR/fetch_charon_blockers.py" mckay-thompson $DRY_RUN 2>&1 | tee -a "$LOG"
echo "" | tee -a "$LOG"

if [[ "$MODE" == "quick" ]]; then
    echo "=== Quick mode complete (${SECONDS}s) ===" | tee -a "$LOG"
    echo "Skipped: hmf-hecke (slow), brauer-manin (clones)" | tee -a "$LOG"
    exit 0
fi

# -----------------------------------------------
# Step 3: HMF Hecke eigenvalues (SLOW — ~1.37M records)
# -----------------------------------------------
echo "[3/4] HMF Hecke eigenvalues (this will take hours)..." | tee -a "$LOG"
echo "  Checkpoint-safe: ctrl-C and re-run to resume" | tee -a "$LOG"
python "$SCRIPT_DIR/fetch_charon_blockers.py" hmf-hecke $DRY_RUN 2>&1 | tee -a "$LOG"
echo "" | tee -a "$LOG"

# -----------------------------------------------
# Step 4: Brauer-Manin repos (network-dependent)
# -----------------------------------------------
echo "[4/4] Brauer-Manin obstruction repos..." | tee -a "$LOG"
bash "$SCRIPT_DIR/fetch_brauer_manin.sh" 2>&1 | tee -a "$LOG"
echo "" | tee -a "$LOG"

echo "=== Pipeline complete (${SECONDS}s) ===" | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "Remaining manual step:" | tee -a "$LOG"
echo "  sage $SCRIPT_DIR/compute_hecke_charpolys.sage" | tee -a "$LOG"
echo "  (requires SageMath installed)" | tee -a "$LOG"
