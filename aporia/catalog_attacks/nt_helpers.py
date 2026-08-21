"""nt_helpers — the campaign's twice-burned number-theoretic primitives, in ONE place.

Built P69 as the P68 residue's named prerequisite: the singular-series factor-2
landmine struck twice across independent rewrites (P51 template, P68 fresh code),
and the li_k uniform-in-t quadrature bias struck twice (P52 origin, ELEN-P51
finding it still in the P51 template). Twice-observed instrument-bug classes go
to a shared tested module; every future attack lane imports from here.

Every function carries its landmine note in-code. test_nt_helpers.py pins each
against the campaign's reviewer-verified values and committed artifacts — the
constants are COMPUTED and cross-checked against attack_*_results.json, never
remembered (feedback: Euler-product constants computed not remembered).
"""
from __future__ import annotations

import math

import numpy as np


# ---------------------------------------------------------------- primes

def sieve_primes(n: int) -> np.ndarray:
    """All primes <= n as int64 array (numpy boolean sieve)."""
    if n < 2:
        return np.array([], dtype=np.int64)
    s = np.ones(n + 1, dtype=bool)
    s[:2] = False
    for p in range(2, int(n ** 0.5) + 1):
        if s[p]:
            s[p * p:: p] = False
    return np.flatnonzero(s).astype(np.int64)


# ------------------------------------------------- singular series (the landmine)

def singular_series_ratio(k: int) -> float:
    """prod over odd primes q | k of (q-1)/(q-2)  — the Hardy-Littlewood
    singular-series ratio S(2k)/S(2) for prime pairs (p, p+2k), and the
    odd-part factor in the Goldbach r(n) prediction.

    LANDMINE (twice-burned, P51 template + P68 fresh code): the factor 2 MUST be
    stripped before the odd-prime loop. Trial division starting at q=3 without
    stripping 2s leaves an even cofactor m; the m>1 tail-prime branch then either
    misses the odd factor entirely or applies (m-1)/(m-2) to an even m.
    Symptom signature: k=6 -> 1.0 instead of 2.0; z-scores explode to O(500).
    """
    prod = 1.0
    m = int(k)
    while m % 2 == 0:          # the strip — do not remove
        m //= 2
    q = 3
    while q * q <= m:
        if m % q == 0:
            prod *= (q - 1) / (q - 2)
            while m % q == 0:
                m //= q
        q += 2
    if m > 1:                  # m is now an odd prime > sqrt(original odd part)
        prod *= (m - 1) / (m - 2)
    return prod


# --------------------------------------------- li_k quadrature (the other landmine)

def li_k(x: float, k: int, steps: int = 200_000) -> float:
    """int_2^x dt / (ln t)^k  via the u-substitution t = e^u:
    int_{ln 2}^{ln x} e^u / u^k du, composite Simpson uniform in u.

    LANDMINE (twice-burned, P52 origin + ELEN-P51 finding it live in the P51
    template): a uniform-in-t grid concentrates nodes where the integrand is
    flat and starves the near-2 region where 1/ln^k t is large; the bias ran
    +0.005% at k=2 up to +0.541% in the worst campaign case, and in the P51
    template it CANCELLED against a second error to fake a flat 0.995.
    Uniform-in-u is the fix; convergence under step-doubling is the test.
    """
    if x <= 2.0:
        return 0.0
    if steps % 2:
        steps += 1
    u = np.linspace(math.log(2.0), math.log(x), steps + 1)
    f = np.exp(u) / u ** k
    h = (u[-1] - u[0]) / steps
    return float(h / 3.0 * (f[0] + f[-1] + 4.0 * f[1:-1:2].sum() + 2.0 * f[2:-1:2].sum()))


# ---------------------------------------------------------------- unfolding

def unfold_u1(gamma1: float, q: float) -> float:
    """First-zero unfolding for degree-1 L-functions: u1 = gamma1 * ln(q) / (2*pi).
    Convention as committed in attack_0348_powered.py (the 0348 test of record).
    Mean-spacing normalization FIRST on any gap comparison (feedback_scale_vs_shape).
    """
    return gamma1 * math.log(q) / (2.0 * math.pi)


# ------------------------------------------------------- Euler-product constants

def twin_prime_constant(limit: int = 10_000_000) -> float:
    """C2 = prod_{p>2} (1 - 1/(p-1)^2), truncated at `limit`.
    Computed in log-space (np.log1p) exactly as the campaign's committed
    instruments did. Tail beyond 1e7 is < 1e-8 in relative terms.
    """
    pp = sieve_primes(limit)[1:].astype(np.float64)   # drop p=2
    return float(np.exp(np.sum(np.log1p(-1.0 / (pp - 1.0) ** 2))))


def artin_constant(limit: int = 10_000_000) -> float:
    """A = prod_p (1 - 1/(p(p-1))), truncated at `limit` (attack_0067 convention)."""
    pp = sieve_primes(limit).astype(np.float64)
    return float(np.exp(np.sum(np.log1p(-1.0 / (pp * (pp - 1.0))))))


# ------------------------------------------------- class groups (batch-4 additions)

def reduced_forms(D: int) -> list[tuple[int, int, int]]:
    """All reduced positive-definite binary quadratic forms (a,b,c) of
    discriminant D < 0 (b^2 - 4ac = D): |b| <= a <= c, with b >= 0 when
    |b| == a or a == c. PRIMITIVE forms only (gcd(a,b,c)=1) — the form class
    number counts primitive classes; without the gcd filter h(-12) would count
    the imprimitive (2,2,2) and read 2 instead of 1. Added P76 for MATH-0482
    tranche B — class-group orders are COMPUTED, never remembered.
    """
    if D >= 0 or D % 4 not in (0, 1):
        raise ValueError(f"D must be negative and 0 or 1 mod 4, got {D}")
    forms = []
    a = 1
    while 4 * a * a <= -D * 4 // 3 + 4:            # a <= sqrt(|D|/3) guard, integer-safe
        if a * a * 3 > -D:
            break
        for b in range(-a, a + 1):
            if (b * b - D) % (4 * a):
                continue
            c = (b * b - D) // (4 * a)
            if c < a:
                continue
            if (abs(b) == a or a == c) and b < 0:  # canonical representative only
                continue
            if math.gcd(math.gcd(a, abs(b)), c) != 1:   # primitive classes only
                continue
            forms.append((a, b, c))
        a += 1
    return forms


def class_number(D: int) -> int:
    """h(D) = number of reduced forms of discriminant D < 0."""
    return len(reduced_forms(D))
