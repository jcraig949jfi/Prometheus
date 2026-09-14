"""Batch 06 finalize (2026-09-13): fill observability + nyx_handoff from records+receipts.
    python -m techne.fossils.batches.batch06_finalize
ORACLE_BACKED per specimen from whether the receipt grades against an independent expectation."""
from __future__ import annotations

from .. import record as R
from . import batch04_finalize as F4
from . import batch06

ORACLE = {
    "bsd-4.2-distribution-tape-1983": False, "bsd-4.3-distribution-tape-1986": True,  # kernel banner + 317 files restored
    "bsd-4.3-reno-distribution-tape-1990": False,
    "go-runtime-deadlock-fixtures-1.22": True, "valgrind-helgrind-fixtures-3.19": True,
    "glibc-rwlock-writer-starvation-2.36": True,
    "dmtcp-3.1.2": True, "hashicorp-memberlist-0.5.4": True, "redlock-py-redis-2014": True, "cocagne-plain-paxos": True,
    "pid-autotune-hirschmann": True, "indirect-self-tuning-regulator-liaosteve": True,
    "l1-adaptive-control-basics-xkhainguyen": True, "libdai-mooij": True,
    "gnu-apl-2.0": True,
}
SOURCE_ONLY = {
    "bsd-4.2-distribution-tape-1983": "PRESERVED + hashed; the boot procedure is identical to the 4.3 tape (proven) but this tape was not individually booted this pass -- TECHNE-69b.",
    "bsd-4.3-reno-distribution-tape-1990": "PRESERVED + hashed; not individually booted this pass -- TECHNE-69b.",
}


def main():
    F4.ORACLE = ORACLE
    F4.SOURCE_ONLY = SOURCE_ONLY
    for sid in [r["specimen_id"] for r in batch06.S]:
        probs = F4.fill(sid)
        rec = R.load(sid)
        print("%-40s %-24s obs=%s %s" % (sid, rec["run_classification"],
              "".join("1" if v == "yes" else ("0" if v == "no" else "?") for v in rec["observability"].values()),
              "ok" if not probs else probs))


if __name__ == "__main__":
    main()
