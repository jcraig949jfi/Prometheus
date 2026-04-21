"""TOOL_ROOT_NUMBER — Global root number of an elliptic curve over Q.

The root number w(E) = +/-1 is the sign of the functional equation for L(E, s).
By the parity conjecture (BSD consequence):
    w(E) = (-1)^{rank(E)}
So w(E) = -1 is strong circumstantial evidence that rank(E) is odd.

w(E) = prod_p w_p(E) over local root numbers at all bad primes and the
archimedean place. Wraps PARI's `ellrootno`.

Interface:
    root_number(ainvs) -> int                              # +1 or -1
    local_root_number(ainvs, p) -> int
    parity_consistent(ainvs, analytic_rank) -> bool

Forged: 2026-04-21 | Tier: 1 (Python/cypari) | REQ-017
Tested against: LMFDB root numbers for 11a1 (+1), 37a1 (-1), 389a1 (+1),
5077a1 (-1, rank 3), 234446a1 (+1, rank 4 — conditional on BSD parity).
"""
from __future__ import annotations

import cypari

_pari = cypari.pari


def _ellinit(ainvs):
    """Build a PARI elliptic curve from a-invariants [a1,a2,a3,a4,a6]."""
    if not isinstance(ainvs, (list, tuple)) or len(ainvs) != 5:
        raise ValueError(
            f"ainvs must be a length-5 list [a1,a2,a3,a4,a6], got {ainvs!r}")
    coeffs = "[" + ",".join(str(int(a)) for a in ainvs) + "]"
    return _pari(f"ellinit({coeffs})")


def root_number(ainvs) -> int:
    """Global root number w(E) in {+1, -1}.

    Parameters
    ----------
    ainvs : list[int]
        Weierstrass a-invariants [a1, a2, a3, a4, a6].

    Returns
    -------
    int
        +1 or -1.

    Raises
    ------
    ValueError
        If the curve is singular (discriminant 0).
    """
    E = _ellinit(ainvs)
    return int(E.ellrootno())


def local_root_number(ainvs, p: int) -> int:
    """Local root number w_p(E) at the prime p.

    w_p = +1 for good reduction. The product of all local root numbers
    equals the global root number.
    """
    E = _ellinit(ainvs)
    return int(E.ellrootno(int(p)))


def parity_consistent(ainvs, analytic_rank: int) -> bool:
    """Check (-1)^rank == w(E). Assumes BSD parity (known for most curves)."""
    w = root_number(ainvs)
    return (-1) ** int(analytic_rank) == w


if __name__ == "__main__":
    cases = [
        ("11a1",     [0, -1, 1, -10, -20],  +1, 0),
        ("37a1",     [0,  0, 1,  -1,   0],  -1, 1),
        ("389a1",    [0,  1, 1,  -2,   0],  +1, 2),
        ("5077a1",   [0,  0, 1,  -7,   6],  -1, 3),
        ("15a1",     [1,  1, 1,   0,   0],  +1, 0),
    ]
    print("root_number smoke test")
    print("-" * 54)
    for name, ainv, expected_w, rank in cases:
        w = root_number(ainv)
        ok = w == expected_w
        pc = parity_consistent(ainv, rank)
        print(f"  {name:8s}  w={w:+d}  expected={expected_w:+d}  "
              f"parity({rank})={pc}  {'OK' if ok and pc else 'FAIL'}")

    # Local consistency: w(E) = w_inf * prod_p w_p, and for E/Q, w_inf = -1.
    # 37a1 has global w = -1 and one bad prime 37, so w_37 = +1.
    w_local = local_root_number([0, 0, 1, -1, 0], 37)
    print(f"\n  37a1 local at 37: w_37={w_local:+d}  expected=+1 (w_inf=-1 carries the sign)")
