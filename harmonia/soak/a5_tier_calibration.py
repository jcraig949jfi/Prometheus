"""Calibration of the new A5 anchor tier, and a staleness test of SOAK-03 (soak P23).

Two things, both external.

1. SOAK-03 STALENESS. At P1 I measured the anchor registry and retired rotation (a)
   as exhausted. Twenty passes then cited that verdict while Aporia revised the
   registry four times underneath it. Re-measuring: the NUMBERS moved a lot
   (A3+A4 23 -> 36, all 72 now attested where 15 were not, a new A5 grade, a new
   repair_log field) while the CONCLUSION survived -- still no locally replicable
   anchor. AA-015 is the one new computational match and is not runnable: its
   'computation' is the 2^O(n) constructivity condition of the natural-proofs
   barrier, and its own basis records the primary source as UNREACHED.

2. A5 CALIBRATION. A5 appeared during this soak and asserts full-text PDF
   extraction -- a stronger claim than A4 -- and had never been independently
   exercised. AA-007 is the only A5 entry with mathematical content.

   WHAT THIS CHECKS: internal coherence and correct interpretation.
   WHAT IT CANNOT CHECK: that the quote is verbatim. Fidelity needs the PDF
   re-fetched and diffed; a mis-transcribed exponent that stayed self-consistent
   would pass everything below.

Read-only.
"""
from fractions import Fraction as F

# Theorem 1.2 as extracted into AA-007:
#   d^{1/2-1/p}  <~_{r,p}  C_{r,p}(d)  <~_{r,p}  d^{1/2-1/max(p,2r)} log d
# Attestation remark: "upper matches lower (up to log) iff p >= 2r".


def exponents(r: int, p: int):
    return F(1, 2) - F(1, p), F(1, 2) - F(1, max(p, 2 * r))


def check_iff(r_hi=9, p_hi=40):
    """Does 'matches iff p >= 2r' hold across the grid?"""
    checked, bad = 0, []
    for r in range(2, r_hi):
        for p in range(2, p_hi):
            lo, hi = exponents(r, p)
            checked += 1
            if (lo == hi) != (p >= 2 * r):
                bad.append((r, p, lo, hi))
    return checked, bad


def headline_supported():
    """At p=2r the exponent must be strictly positive, i.e. C grows polynomially
    in d and therefore cannot be a polylog quantity like sqrt(log d)."""
    out = []
    for r in (2, 3, 4, 5):
        lo, hi = exponents(r, 2 * r)
        out.append((r, lo, lo > 0))
    return out


if __name__ == "__main__":
    checked, bad = check_iff()
    print(f"'matches iff p>=2r': checked {checked} (r,p) pairs, disagreements {len(bad)}")
    print("\nopen-regime gaps (p < 2r):")
    for r, p in ((2, 2), (2, 3), (3, 2), (3, 5), (4, 7)):
        lo, hi = exponents(r, p)
        print(f"  r={r} p={p}: lower {lo}  upper {hi}  gap {hi - lo}")
    print("\nheadline (tensor constant is NOT sqrt(log d)):")
    for r, lo, ok in headline_supported():
        print(f"  r={r}, p=2r: matched exponent {lo}  polynomial-in-d: {ok}")
    print("\nLIMIT: internal coherence only. Verbatim fidelity is UNCHECKED and")
    print("       requires re-fetching arXiv:2411.10633 and diffing the text.")
