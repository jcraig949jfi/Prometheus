#!/usr/bin/env bash
# E-003 BEE production driver (GO record aa958093 @ 232ebe399). Runs the FROZEN pipeline in order, each step's output into
# $OUT. Stops at the first failure (set -e). The start receipt must already be written and must PASS.
# Usage: bash run_production.sh <OUT dir> <workers>
set -euo pipefail
OUT="$1"; W="${2:-10}"
PY=/c/Users/James/AppData/Local/Python/pythoncore-3.14-64/python.exe
HERE="$(cd "$(dirname "$0")" && pwd)"; D="$(dirname "$HERE")"
mkdir -p "$OUT"
cd "$D"
$PY tools/traced_world.py --config inputs/r022153.config.json --births inputs/r022153.births.jsonl.gz \
    --out "$OUT/r022153_births_export.jsonl.gz" --receipt "$OUT/traced_world_receipt.json"
$PY tools/q4.py --export "$OUT/r022153_births_export.jsonl.gz" --out "$OUT/q4.jsonl.gz" --workers "$W"
$PY tools/s4_tests.py --mode arms --export "$OUT/r022153_births_export.jsonl.gz" --out "$OUT/arms.jsonl.gz" --workers "$W"
$PY tools/e003_analysis.py --make-sample --export "$OUT/r022153_births_export.jsonl.gz" --q4 "$OUT/q4.jsonl.gz" --out "$OUT/sample.json"
$PY tools/s4_tests.py --mode flip --export "$OUT/r022153_births_export.jsonl.gz" --sample "$OUT/sample.json" --out "$OUT/flip.jsonl.gz" --workers "$W"
$PY tools/s4_tests.py --mode completeness --export "$OUT/r022153_births_export.jsonl.gz" --sample "$OUT/sample.json" --out "$OUT/compl.jsonl.gz" --workers "$W"
$PY tools/sample_prestate_export.py "$OUT/r022153_births_export.jsonl.gz" "$OUT/sample.json" "$OUT/S4_SAMPLE_PRE.jsonl"
$PY tools/agreement_export.py "$OUT/S4_SAMPLE_PRE.jsonl" "$OUT/S4_SAMPLE_OWNER.jsonl"
$PY tools/e003_analysis.py --export "$OUT/r022153_births_export.jsonl.gz" --q4 "$OUT/q4.jsonl.gz" --arms "$OUT/arms.jsonl.gz" \
    --flip "$OUT/flip.jsonl.gz" --compl "$OUT/compl.jsonl.gz" --sample "$OUT/sample.json" \
    --v0-schema "$OUT/attribution_schema_v0.py" --out "$OUT/E003_RESULTS.json"
echo "PRODUCTION_DONE"
