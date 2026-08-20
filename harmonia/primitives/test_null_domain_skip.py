"""Pinned regression for the HARMA-P14 defect (fixed P40): null_marginal_pairing
must honour the domain-skip contract that evaluate_lattice and the other nulls
follow — a spec with domain-restricted operators (operators that raise
spec.transform_errors on out-of-domain values) must not crash the null battery.

Pinned exactly (P38 doctrine: pin the contract, not a disjunction):
  * domain-restricted spec -> null runs, returns degenerate=True, reports
    n_dropped per side, perm_rates non-empty
  * fully-out-of-domain side -> the nothing-to-permute path, perm_rates == []
  * unrestricted spec -> behaviour unchanged (degenerate, no drops)

Run: python -m pytest harmonia/primitives/test_null_domain_skip.py -q
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from harmonia.primitives.lattice_void_miner import LatticeSpec, null_marginal_pairing  # noqa: E402

ALWAYS = lambda a, b, r: True  # noqa: E731
CELL = {"inv_a": "x", "inv_b": "y", "f": "keep", "g": "keep", "rel": "always"}


def keep_only(k):
    def op(v):
        if v > k:
            raise ValueError("outside this invariant's domain")
        return v
    return op


def spec_with(k):
    return LatticeSpec(
        side_a_name="A", side_b_name="B",
        side_a={"x": list(range(1, 101))}, side_b={"y": list(range(1, 101))},
        operators={"keep": keep_only(k)},
        relations=("always",),
        eval_relation=ALWAYS,
    )


def test_domain_restricted_spec_does_not_crash():
    r = null_marginal_pairing(spec_with(5), CELL)
    assert r["degenerate"] is True, r
    assert r["n_dropped"] == [95, 95], r
    assert len(r["perm_rates"]) == 5 and all(x == 1.0 for x in r["perm_rates"]), r


def test_fully_out_of_domain_side_yields_nothing_to_permute():
    r = null_marginal_pairing(spec_with(0), CELL)
    assert r["degenerate"] is True, r
    assert r["perm_rates"] == [], r
    assert r["n_dropped"] == [100, 100], r


def test_unrestricted_spec_unchanged():
    r = null_marginal_pairing(spec_with(100), CELL)
    assert r["degenerate"] is True, r
    assert r["n_dropped"] == [0, 0], r
    assert len(r["perm_rates"]) == 5, r


if __name__ == "__main__":
    test_domain_restricted_spec_does_not_crash()
    test_fully_out_of_domain_side_yields_nothing_to_permute()
    test_unrestricted_spec_unchanged()
    print("3/3 pinned regressions pass")
