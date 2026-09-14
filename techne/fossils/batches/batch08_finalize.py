"""Batch 08 finalize (2026-09-13): fill observability + nyx_handoff from records+receipts.
    python -m techne.fossils.batches.batch08_finalize
Run ONCE after batch08.py and after all runs. ORACLE_BACKED per specimen = whether the receipt
grades the result against an independent expectation."""
from __future__ import annotations

from .. import record as R
from . import batch04_finalize as F4
from . import batch08

ORACLE = {
    "eliza-anthay-1966": True,   # the exact 1966 CACM dialogue (IN WHAT WAY / pronoun reflection)
}
SOURCE_ONLY: dict = {}


def main():
    F4.ORACLE = ORACLE
    F4.SOURCE_ONLY = SOURCE_ONLY
    for sid in [r["specimen_id"] for r in batch08.S]:
        probs = F4.fill(sid)
        rec = R.load(sid)
        print("%-22s %-22s obs=%s %s" % (sid, rec["run_classification"],
              "".join("1" if v == "yes" else ("0" if v == "no" else "?") for v in rec["observability"].values()),
              "ok" if not probs else probs))


if __name__ == "__main__":
    main()
