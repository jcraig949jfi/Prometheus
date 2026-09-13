"""Batch 09 finalize (2026-09-13): fill observability + nyx_handoff from records+receipts.
    python -m techne.fossils.batches.batch09_finalize
ORACLE_BACKED per specimen = whether the receipt grades the result against an independent expectation."""
from __future__ import annotations

from .. import record as R
from . import batch04_finalize as F4
from . import batch09

ORACLE = {
    "linpack-netlib-1979": True,    # the benchmark's own exact all-ones solution + residual
    "eispack-netlib-1976": True,    # closed-form spectrum 2-sqrt2, 2, 2+sqrt2
    "md5-rfc1321": True,            # the digests printed in RFC 1321 A.5
    "des-reference": True,          # 16-round Feistel round trip
    "tiny-aes-c": True,             # NIST SP 800-38A known-answer vectors
    "lapack-reference": False,      # acquired as the rival; not built this round
    "spdylay": False,               # acquired; not built this round
    "openssl-1.0.1f-heartbleed": False,   # archival source only, never executed
}
SOURCE_ONLY = {
    "lapack-reference": "SOURCE_ONLY this round: acquired as the WINNER of the LINPACK/EISPACK pair so the "
        "comparison exists, but the reference BLAS+LAPACK build (6776 files) was not run in this pass. The "
        "LINPACK-vs-LAPACK rate dataset is therefore NOT done -- named, not faked.",
    "spdylay": "SOURCE_ONLY this round: autotools build not attempted in this pass. Preserved + hashed so the "
        "SPDY framing/header-compression machinery can be read in its own world.",
    "openssl-1.0.1f-heartbleed": "SOURCE_ONLY BY INTENT: this body is preserved so a documented failure can be "
        "read in its original context (ssl/d1_both.c). It is deliberately never built or executed in the vault, "
        "and the vault carries no exploit for it. Archival/defensive only.",
}


def main():
    F4.ORACLE = ORACLE
    F4.SOURCE_ONLY = SOURCE_ONLY
    for sid in [r["specimen_id"] for r in batch09.S]:
        probs = F4.fill(sid)
        rec = R.load(sid)
        print("%-28s %-24s obs=%s %s" % (sid, rec["run_classification"],
              "".join("1" if v == "yes" else ("0" if v == "no" else "?") for v in rec["observability"].values()),
              "ok" if not probs else probs))


if __name__ == "__main__":
    main()
