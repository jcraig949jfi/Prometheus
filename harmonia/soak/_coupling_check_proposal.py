"""Proposed coupling check: derive the cid list from CONJ instead of hardcoding it.

test_registry_decides_the_five_cids asserts every cid is registered, but against a
HARDCODED five-entry dict. Adding a sixth conjecture to rp0.CONJ therefore turns
nothing red (mutation-verified, HARMA-P34). Deriving the loop from CONJ closes it.

This is the existing assertion with the source of the list changed. Proposal only;
Aporia's file is untouched.
"""
import os
import sys

sys.path.insert(0, os.path.abspath("harmonia/experiments"))
import reasoning_phase0 as rp0          # noqa: E402
from verifier_lens import decide_conjecture  # noqa: E402


def test_every_generated_cid_has_a_registry_entry():
    """The generator and the registry must agree. Derived from CONJ, not hardcoded."""
    missing = [cid for cid, *_ in rp0.CONJ if decide_conjecture(cid) is None]
    assert not missing, (
        f"cids emitted by gen_R6 with no z3 registry entry: {missing}. "
        "Every such probe degrades to an unscoreable abstention.")


if __name__ == "__main__":
    test_every_generated_cid_has_a_registry_entry()
    print(f"coupling check: OK — all {len(rp0.CONJ)} generated cids are registered")
