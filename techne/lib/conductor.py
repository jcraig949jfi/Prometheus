"""TOOL_CONDUCTOR — Conductor + local reduction data of an elliptic curve over Q.

The conductor N is the universal stratifier for EC arithmetic: it parameterises
LMFDB labels, separates reduction types, and anchors every BSD test. This
tool also exposes the Tamagawa product and per-prime Kodaira symbols from the
same `ellglobalred` call — no wasted work.

Wraps PARI's `ellglobalred`.

Interface:
    conductor(ainvs) -> int
    global_reduction(ainvs) -> dict
        {conductor, tamagawa_product, bad_primes,
         local: [{p, f_p, kodaira, c_p, reduction}, ...]}
    bad_primes(ainvs) -> list[int]

Kodaira code (PARI convention, negative for I*_n / II*/III*/IV*):
     1  ->  good (does not appear here; bad primes only)
     2  ->  II     3 -> III     4 -> IV
     5  ->  I_1    6 -> I_2    5+n -> I_n
    -1  ->  I*_0  -5 -> I*_1  -5-n -> I*_n
    -2  ->  II*   -3 -> III*  -4  -> IV*

Local layout (PARI's ellglobalred per-prime entry):
     slot 0 : f_p   (exponent of p in the conductor)
     slot 1 : Kodaira code
     slot 2 : local transformation flag (0 if curve already minimal at p)
     slot 3 : c_p   (Tamagawa number at p)

Forged: 2026-04-21 | Tier: 1 (Python/cypari) | REQ-019
Tested against: LMFDB conductors (11a1->11, 37a1->37, 389a1->389, 15a1->15).
"""
from __future__ import annotations

import cypari

_pari = cypari.pari


_KODAIRA_NAMED = {
    2: "II", 3: "III", 4: "IV",
    -1: "I*_0", -2: "II*", -3: "III*", -4: "IV*",
}


def _ellinit(ainvs):
    if not isinstance(ainvs, (list, tuple)) or len(ainvs) != 5:
        raise ValueError(
            f"ainvs must be a length-5 list [a1,a2,a3,a4,a6], got {ainvs!r}")
    coeffs = "[" + ",".join(str(int(a)) for a in ainvs) + "]"
    return _pari(f"ellinit({coeffs})")


def _decode_kodaira(code: int) -> str:
    c = int(code)
    if c in _KODAIRA_NAMED:
        return _KODAIRA_NAMED[c]
    if c >= 5:
        return f"I_{c - 4}"
    if c <= -5:
        return f"I*_{-c - 4}"
    return f"KOD({c})"


def conductor(ainvs) -> int:
    """Global conductor N of the elliptic curve."""
    E = _ellinit(ainvs)
    r = E.ellglobalred()
    return int(r[0])


def bad_primes(ainvs) -> list[int]:
    """Primes of bad reduction, sorted ascending."""
    E = _ellinit(ainvs)
    r = E.ellglobalred()
    fac = r[3]  # factorization matrix: col 0 = primes
    return [int(fac[i, 0]) for i in range(int(fac.matsize()[0]))]


def global_reduction(ainvs) -> dict:
    """Full global reduction data in one structured dict.

    Returns
    -------
    dict
        conductor (int), tamagawa_product (int),
        bad_primes (list[int]),
        local (list of dicts): {p, f_p, kodaira_code, kodaira, c_p, reduction}
    """
    E = _ellinit(ainvs)
    r = E.ellglobalred()
    N = int(r[0])
    tam_prod = int(r[2])
    fac = r[3]
    n_bad = int(fac.matsize()[0])
    primes = [int(fac[i, 0]) for i in range(n_bad)]
    local_data = r[4]
    locals_ = []
    for i, p in enumerate(primes):
        entry = local_data[i]
        f_p = int(entry[0])
        kod = int(entry[1])
        local_flag = int(entry[2])
        c_p = int(entry[3])
        locals_.append({
            "p": p,
            "f_p": f_p,
            "kodaira_code": kod,
            "kodaira": _decode_kodaira(kod),
            "c_p": c_p,
            "local_flag": local_flag,
        })
    return {
        "conductor": N,
        "tamagawa_product": tam_prod,
        "bad_primes": primes,
        "local": locals_,
    }


if __name__ == "__main__":
    cases = [
        ("11a1",   [0, -1, 1, -10, -20],  11),
        ("37a1",   [0,  0, 1,  -1,   0],  37),
        ("389a1",  [0,  1, 1,  -2,   0], 389),
        ("15a1",   [1,  1, 1,   0,   0],  15),
        ("5077a1", [0,  0, 1,  -7,   6], 5077),
    ]
    print("conductor smoke test")
    print("-" * 54)
    for name, ainv, expected in cases:
        N = conductor(ainv)
        ok = N == expected
        print(f"  {name:8s}  N={N:6d}  expected={expected:6d}  {'OK' if ok else 'FAIL'}")

    # Tamagawa consistency check: product of c_p must equal tam_product
    print("\nTamagawa product consistency:")
    for name, ainv in [("15a1", [1,1,1,0,0]), ("14a1", [1,0,1,4,-6]),
                       ("11a1", [0,-1,1,-10,-20]), ("27a1", [0,0,1,0,-7])]:
        g = global_reduction(ainv)
        prod_c = 1
        for loc in g['local']:
            prod_c *= loc['c_p']
        ok = prod_c == g['tamagawa_product']
        locs = ", ".join(f"p={l['p']}({l['kodaira']},c={l['c_p']})" for l in g['local'])
        print(f"  {name:6s}  tam={g['tamagawa_product']}  prod(c_p)={prod_c}  "
              f"{'OK' if ok else 'FAIL'}  [{locs}]")
