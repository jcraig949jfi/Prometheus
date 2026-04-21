"""TOOL_CF_EXPANSION — Continued fraction expansion and analysis.

Computes the continued fraction expansion of a rational number and
analyzes its properties. Key for the Zaremba conjecture test: does
every integer q have some a coprime to q such that all CF digits of a/q
are bounded by some absolute constant (conjectured: 5)?

Interface:
    cf_expand(p, q) -> list[int]
    cf_max_digit(p, q) -> int
    zaremba_test(q, bound=5) -> dict
    cf_from_float(x, max_terms=50) -> list[int]

Forged: 2026-04-21 | Tier: 1 (pure Python) | REQ-014
Tested against: known CF expansions (e.g. 355/113 = [3;7,16])
"""


def cf_expand(p: int, q: int) -> list:
    """Compute the continued fraction expansion of p/q.

    Parameters
    ----------
    p, q : int
        Numerator and denominator. q must be > 0.

    Returns
    -------
    list of int — the CF coefficients [a_0; a_1, a_2, ...].
    Finite for rationals.
    """
    if q <= 0:
        raise ValueError(f"Denominator must be positive, got {q}")
    result = []
    while q != 0:
        a, r = divmod(p, q)
        result.append(a)
        p, q = q, r
    return result


def cf_max_digit(p: int, q: int) -> int:
    """Return the largest CF digit in the expansion of p/q."""
    return max(cf_expand(p, q))


def zaremba_test(q: int, bound: int = 5) -> dict:
    """Test the Zaremba conjecture for a given denominator q.

    Zaremba's conjecture: for every q >= 1, there exists a with
    gcd(a, q) = 1 such that all partial quotients of a/q are <= bound.

    Parameters
    ----------
    q : int — the denominator to test
    bound : int — the CF digit bound (default 5, the conjectured constant)

    Returns
    -------
    dict with:
        q : int
        bound : int
        satisfies : bool — True if a witness a was found
        witness : int or None — the smallest a with all CF digits <= bound
        n_tested : int — how many a values were tested
        min_max_digit : int — smallest max-CF-digit across all coprime a
        best_a : int — the a achieving min_max_digit
    """
    from math import gcd

    best_max = float('inf')
    best_a = None
    witness = None
    tested = 0

    for a in range(1, q):
        if gcd(a, q) != 1:
            continue
        tested += 1
        cf = cf_expand(a, q)
        mx = max(cf) if cf else 0
        if mx < best_max:
            best_max = mx
            best_a = a
        if mx <= bound and witness is None:
            witness = a

    return {
        "q": q,
        "bound": bound,
        "satisfies": witness is not None,
        "witness": witness,
        "n_tested": tested,
        "min_max_digit": best_max if best_max < float('inf') else None,
        "best_a": best_a,
    }


def cf_from_float(x: float, max_terms: int = 50, tol: float = 1e-12) -> list:
    """Compute CF expansion of a float (truncated to max_terms).

    Useful for real algebraic numbers or transcendentals. The expansion
    may not be exact due to floating point.
    """
    result = []
    for _ in range(max_terms):
        a = int(x) if x >= 0 else int(x) - (1 if x != int(x) else 0)
        result.append(a)
        frac = x - a
        if abs(frac) < tol:
            break
        x = 1.0 / frac
    return result


def sturm_bound(weight: int, level: int, prime_factors: list = None) -> int:
    """Compute the Sturm bound for modular forms.

    The Sturm bound is: floor(k/12 * N * prod(1 + 1/p for p | N))
    where k = weight, N = level. Two modular forms of weight k and level N
    that agree on the first sturm_bound coefficients are identical.

    Parameters
    ----------
    weight : int — the weight k
    level : int — the level N
    prime_factors : list of int, optional — prime factors of N. If None,
        computed automatically.

    Returns
    -------
    int — the Sturm bound.
    """
    if prime_factors is None:
        prime_factors = _prime_factors(level)

    index = 1
    for p in set(prime_factors):
        index *= (1 + 1 / p)

    return int(weight * level * index / 12)


def _prime_factors(n: int) -> list:
    """Return list of prime factors of n (with multiplicity)."""
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


if __name__ == "__main__":
    # Smoke tests
    print("355/113 =", cf_expand(355, 113))  # Should be [3, 7, 16]
    print("Max digit:", cf_max_digit(355, 113))  # Should be 16

    # Zaremba test for small q
    for q in [5, 7, 10, 13, 50]:
        r = zaremba_test(q)
        status = f"witness a={r['witness']}" if r['satisfies'] else f"FAILS (min max digit = {r['min_max_digit']})"
        print(f"Zaremba(q={q}, bound=5): {status}")

    # Sturm bound
    print(f"\nSturm bound (k=2, N=11): {sturm_bound(2, 11)}")
    print(f"Sturm bound (k=12, N=1): {sturm_bound(12, 1)}")

    # CF of pi
    import math
    print(f"\nCF(pi) = {cf_from_float(math.pi, max_terms=10)}")
