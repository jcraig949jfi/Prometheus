"""P40's domain-skip pin plus ONE case: an operator raising OverflowError.

P31 found Pin B scores 3/4 — narrowing `spec.transform_errors` to ValueError
leaves it green, because every operator in the pin raises only ValueError. The
declared contract is (ValueError, OverflowError), so half of it is unexercised.

This adds a spec whose operator raises OverflowError and asserts the same
domain-skip behaviour. Proposal only; Aporia's file is untouched.
"""
import os
import sys

sys.path.insert(0, os.path.abspath("."))
from harmonia.primitives.lattice_void_miner import LatticeSpec, null_marginal_pairing  # noqa: E402

ALWAYS = lambda a, b, r: True  # noqa: E731
CELL = {"inv_a": "x", "inv_b": "y", "f": "keep", "g": "keep", "rel": "always"}


def overflow_above(k):
    """Raises OverflowError — the OTHER member of the default transform_errors."""
    def op(v):
        if v > k:
            raise OverflowError("value outside representable domain")
        return v
    return op


def spec_with(op):
    return LatticeSpec(
        side_a_name="A", side_b_name="B",
        side_a={"x": list(range(1, 101))}, side_b={"y": list(range(1, 101))},
        operators={"keep": op}, relations=("always",), eval_relation=ALWAYS,
    )


def test_overflow_error_is_domain_skipped():
    r = null_marginal_pairing(spec_with(overflow_above(50)), CELL)
    assert r["n_dropped"] == [50, 50], r["n_dropped"]
    assert r["perm_rates"], "expected the battery to run on the in-domain half"


if __name__ == "__main__":
    test_overflow_error_is_domain_skipped()
    print("patched pin B: OK")
