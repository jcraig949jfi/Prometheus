#!/bin/bash
# Round 3 M1 — Run all 28 tests across 4 batches
# Usage: bash m1_r3_run_all.sh
# Each batch loads its data domain once and runs all tests in that domain.

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================================"
echo "ROUND 3 — M1 (Skullport) — 28 tests, 4 batches"
echo "Started: $(date)"
echo "============================================================"

echo ""
echo "[1/4] KNOT BATCH (9 tests) ..."
python m1_r3_batch_knots.py 2>&1 | tee v2/r3_knot_batch_log.txt
echo ""

echo "[2/4] NUMBER FIELD BATCH (5 tests) ..."
python m1_r3_batch_nf.py 2>&1 | tee v2/r3_nf_batch_log.txt
echo ""

echo "[3/4] EC/MF BATCH (7 tests) ..."
python m1_r3_batch_ecmf.py 2>&1 | tee v2/r3_ecmf_batch_log.txt
echo ""

echo "[4/4] FORMAL BATCH (7 tests) ..."
python m1_r3_batch_formal.py 2>&1 | tee v2/r3_formal_batch_log.txt
echo ""

echo "============================================================"
echo "ALL BATCHES COMPLETE — $(date)"
echo "Results in: cartography/shared/scripts/v2/r3_*_batch_results.json"
echo "============================================================"
