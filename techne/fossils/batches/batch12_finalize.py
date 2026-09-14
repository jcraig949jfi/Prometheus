"""Batch 12 finalize: observability + nyx_handoff for the pre-1970 bodies.
    python -m techne.fossils.batches.batch12_finalize

All four are SOURCE_ONLY BY WORLD EXTINCTION, not by neglect. Under the charter's P3 ladder each
is BODY_RECOVERED_WORLD_NAMED: the body is preserved and hashed, and the world it expects is named
precisely (machine, word size, number representation, character set, OS, compiler, storage), but no
emulated world has been constructed for it in this vault yet. Historical source without its world
is useful; it is NOT called runnable."""
from __future__ import annotations

from .. import record as R
from . import batch04_finalize as F4
from . import batch12

ORACLE = {s["specimen_id"]: False for s in batch12.S}
SOURCE_ONLY = {
    "spacewar-pdp1-1962":
        "SOURCE_ONLY (BODY_RECOVERED_WORLD_NAMED): the 25 Mar 1962 PDP-1 assembly is preserved and hashed. "
        "Running it needs a PDP-1 with a Type 30 CRT, an 18-bit one's-complement machine with no OS, plus a "
        "period assembler. simh carries a PDP-1 simulator, so a world is REACHABLE -- it was not built this "
        "round, and the fossil is not called runnable until it is.",
    "eliza-weizenbaum-mad-slip-1965":
        "SOURCE_ONLY (BODY_RECOVERED_WORLD_NAMED): the MAD-SLIP listing is preserved. Running it needs CTSS "
        "on an IBM 7094 plus a MAD compiler and the SLIP library -- a world that no longer exists in ordinary "
        "use. The vault holds eliza-anthay-1966, a modern faithful reconstruction OF THIS BODY, which IS "
        "runnable; the original and the reconstruction are deliberately kept as separate specimens.",
    "cosell-eliza-bbn-lisp-1969":
        "SOURCE_ONLY (BODY_RECOVERED_WORLD_NAMED): BBN-LISP on a PDP-10 under TENEX. A session transcript "
        "ships with the source and is preserved beside it as a behavioural record made in the original world.",
    "lisp-1-5-ibm7090-1962":
        "SOURCE_ONLY (BODY_RECOVERED_WORLD_NAMED): the 7090 assembly transcription is preserved along with the "
        "repository's own assembler tooling. Running it needs an IBM 7090/7094 world; simh carries an i7094 "
        "simulator, so this is REACHABLE and is the strongest candidate for the first historical execution.",
}


def main():
    F4.ORACLE = ORACLE
    F4.SOURCE_ONLY = SOURCE_ONLY
    for sid in [r["specimen_id"] for r in batch12.S]:
        probs = F4.fill(sid)
        rec = R.load(sid)
        print("%-36s %-14s obs=%s %s" % (sid, rec["run_classification"],
              "".join("1" if v == "yes" else ("0" if v == "no" else "?") for v in rec["observability"].values()),
              "ok" if not probs else probs))


if __name__ == "__main__":
    main()
