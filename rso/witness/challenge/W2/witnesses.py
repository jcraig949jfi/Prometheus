"""Behavioural witness for the W2 semantic edit (edits.json). Takes the module under test `m` (original in the
baseline child, edited in the mutant child) and returns a small JSON-able value; the mutation runner records
repr(value) for both so NOT_EQUIVALENT is witnessed, not assumed. DATA FILE: frozen at the set commit.

No registered subject, arm-on-registered-seed, accuracy or retention number: synthetic traces with known decisions,
seeds >= 5,000,000.
"""
import shutil
import tempfile

from rso.witness.challenge.W2 import cases_w2 as W


def e1(m):
    """m = rso.witness.evaluate. X clean and Y REFUSED (custody) present the same node ids. DA's class, and whether
    EVIDENCE_DUPLICATE / EVIDENCE_REFUSED is the reason, in BOTH argument orders. R1 as registered: UNQUALIFIED with
    EVIDENCE_DUPLICATE in both orders (no argument-order resolution)."""
    root = tempfile.mkdtemp(prefix="w2-witness-")
    try:
        b = W.build_e1(root)
        out = {}
        for label, order in (("XY", [b["X"], b["Y"]]), ("YX", [b["Y"], b["X"]])):
            res = m.evaluate(order, b["store"], W.FIRST_CHECK, W.SUBJECTS, "S4", seed_lists=W.seed_lists())
            s = res["subjects"]["S4"]
            why = s.get("why") or []
            out[label] = {"class": s.get("class"), "duplicate": any("EVIDENCE_DUPLICATE" in w for w in why),
                          "refused": any("EVIDENCE_REFUSED" in w for w in why)}
        return out
    finally:
        shutil.rmtree(root, ignore_errors=True)
