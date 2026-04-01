#!/usr/bin/env bash
# Charon Full Audit — Phases 1-4
# Fixes data, audits integrity, reruns all tests, produces methods doc.
# Usage: bash charon/scripts/run_audit.sh
#
# Output: charon/reports/audit_YYYYMMDD_HHMMSS.md (report)
#         charon/reports/audit_journal_YYYYMMDD_HHMMSS.jsonl (structured log)

set -euo pipefail
cd "$(cd "$(dirname "$0")/../.." && pwd)"

echo "============================================================"
echo "CHARON FULL AUDIT — Phases 1-4"
echo "Started: $(date)"
echo "============================================================"
echo ""
echo "Phase 1: Fix zero-fill bug at source"
echo "Phase 2: Audit data integrity + LMFDB spot-checks"
echo "Phase 3: Clean test rerun (all tests, zeros-only, no metadata leak)"
echo "Phase 4: Methods document generation"
echo ""
echo "This will take ~10-15 minutes (mostly Phase 2 LMFDB queries + Phase 3 ML)."
echo ""

python -m charon.scripts.full_audit

echo ""
echo "============================================================"
echo "AUDIT COMPLETE: $(date)"
echo "Reports in charon/reports/"
echo "============================================================"
