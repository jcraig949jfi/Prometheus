"""Batch 07 finalize (2026-09-13): fill observability + nyx_handoff from records+receipts.
    python -m techne.fossils.batches.batch07_finalize
Run ONCE after batch07.py and after all runs; do NOT re-run batch07.py afterward.
ORACLE_BACKED per specimen = whether the receipt grades the result against an independent expectation."""
from __future__ import annotations

from .. import record as R
from . import batch04_finalize as F4
from . import batch07

ORACLE = {
    "eprover-2.6": True,          # SZS status Unsatisfiable/Theorem on shipped TPTP problems
    "pari-gp-2.17": True,         # known number-theoretic values (2^67-1 factors, prime(1000))
    "ssw-smith-waterman": True,   # optimal local-alignment score of an exact-substring pair
}
SOURCE_ONLY: dict[str, str] = {}


def main():
    F4.ORACLE = ORACLE
    F4.SOURCE_ONLY = SOURCE_ONLY
    for sid in [r["specimen_id"] for r in batch07.S]:
        probs = F4.fill(sid)
        rec = R.load(sid)
        print("%-24s %-24s obs=%s %s" % (sid, rec["run_classification"],
              "".join("1" if v == "yes" else ("0" if v == "no" else "?") for v in rec["observability"].values()),
              "ok" if not probs else probs))


if __name__ == "__main__":
    main()
