"""TOOL_CF_EXPANSION — Continued fraction expansion and analysis.

Computes the continued fraction expansion of a rational number and
analyzes its properties. Key for the Zaremba conjecture test: does
every integer q have some a coprime to q such that all CF digits of a/q
are bounded by some absolute constant (conjectured: 5)?

Tier-2 (project #52): batch and numba JIT paths for arrays of rationals.
Charon's scans need cf-expansions of millions of rationals; the JIT
path amortizes Python overhead. Arbitrary-precision Python ints (which
numba cannot represent) automatically fall back to a Python loop — so
correctness never depends on sniffing the input.

Interface (Tier-1):
    cf_expand(p, q) -> list[int]
    cf_max_digit(p, q) -> int
    zaremba_test(q, bound=5) -> dict
    cf_from_float(x, max_terms=50) -> list[int]

Interface (Tier-2, project #52):
    cf_expand_batch(rationals, max_terms=200) -> list[list[int]]
    cf_expand_jit(p, q, max_terms=200) -> np.ndarray  (int64 padded)
    cf_expand_array(rationals_array, max_terms=200, fallback='python')
        -> np.ndarray  shape (n, max_terms)
    cf_truncate_to_partial(p, q, n_terms) -> list[int]

Forged: 2026-04-21 | Tier: 1+2 | REQ-014
Tested against: known CF expansions (e.g. 355/113 = [3;7,16]).
"""
from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Optional numba — graceful degradation if unavailable.
# ---------------------------------------------------------------------------
try:
    import numba
    from numba import njit
    HAS_NUMBA = True
except ImportError:  # pragma: no cover — covered manually if numba removed
    HAS_NUMBA = False
    numba = None

    def njit(*args, **kwargs):
        """No-op decorator when numba is missing."""
        if len(args) == 1 and callable(args[0]):
            return args[0]

        def _wrap(fn):
            return fn

        return _wrap


# Largest int that fits safely in numba's int64 (numpy int64 max).
_INT64_MAX = np.iinfo(np.int64).max
_INT64_MIN = np.iinfo(np.int64).min


# ---------------------------------------------------------------------------
# Tier-1 scalar (pre-existing API — preserved verbatim except q-sign norm).
# ---------------------------------------------------------------------------

def cf_expand(p: int, q: int) -> list:
    """Compute the continued fraction expansion of p/q.

    Parameters
    ----------
    p, q : int
        Numerator and denominator. q must be != 0.

    Returns
    -------
    list of int — the CF coefficients [a_0; a_1, a_2, ...]. Finite for
    rationals. For p == 0 returns [0].
    """
    if q == 0:
        raise ValueError(f"Denominator must be non-zero, got q={q}")
    # Normalize sign so q > 0; CF is unique under q > 0.
    if q < 0:
        p, q = -p, -q
    if p == 0:
        return [0]
    result = []
    while q != 0:
        a, r = divmod(p, q)
        result.append(int(a))
        p, q = q, r
    return result


def cf_max_digit(p: int, q: int) -> int:
    """Return the largest CF digit in the expansion of p/q."""
    return max(cf_expand(p, q))


def zaremba_test(q: int, bound: int = 5) -> dict:
    """Test the Zaremba conjecture for a given denominator q.

    Zaremba's conjecture: for every q >= 1, there exists a with
    gcd(a, q) = 1 such that all partial quotients of a/q are <= bound.
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
    """Compute CF expansion of a float (truncated to max_terms)."""
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
    """Compute the Sturm bound for modular forms."""
    if prime_factors is None:
        prime_factors = _prime_factors(level)

    index = 1
    for p in set(prime_factors):
        index *= (1 + 1 / p)

    return int(weight * level * index / 12)


def _prime_factors(n: int) -> list:
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


# ---------------------------------------------------------------------------
# Tier-2: batch operations and numba JIT (project #52).
# ---------------------------------------------------------------------------

def cf_truncate_to_partial(p: int, q: int, n_terms: int) -> list:
    """Truncate the CF expansion of p/q to the first n_terms terms.

    This is equivalent to ``cf_expand(p, q)[:n_terms]`` but short-circuits
    once n_terms terms have been emitted, which matters for very long
    expansions (e.g. consecutive Fibonacci numbers).
    """
    if n_terms <= 0:
        return []
    if q == 0:
        raise ValueError(f"Denominator must be non-zero, got q={q}")
    if q < 0:
        p, q = -p, -q
    if p == 0:
        return [0][:n_terms]
    result = []
    while q != 0 and len(result) < n_terms:
        a, r = divmod(p, q)
        result.append(int(a))
        p, q = q, r
    return result


def cf_expand_batch(rationals, max_terms: int = 200) -> list:
    """Batch CF expansion (pure Python).

    Parameters
    ----------
    rationals : iterable of (p, q) pairs OR np.ndarray with shape (n, 2)
        The rationals to expand.
    max_terms : int
        Per-rational truncation cap (defends against rationals that
        somehow loop without terminating, e.g. corrupted input). For
        well-formed rationals the natural CF terminates well before
        max_terms.

    Returns
    -------
    list of list[int] — one CF list per input rational, in order.
    """
    out = []
    for pair in rationals:
        p = int(pair[0])
        q = int(pair[1])
        out.append(cf_truncate_to_partial(p, q, max_terms))
    return out


# ---------------------------------------------------------------------------
# Numba JIT path. Operates on int64 only.
# ---------------------------------------------------------------------------

@njit(cache=True)
def _cf_jit_kernel(p, q, out):  # pragma: no cover — numba-compiled
    """Fill `out` (int64 array) with the CF terms of p/q.

    Returns the number of terms written. Trailing entries are left at
    their initial value (caller must zero-initialize).
    """
    # Normalize sign of q (numba does not support tuple swap with mixed types
    # but here both are int64, so swap is fine).
    if q < 0:
        p = -p
        q = -q
    if p == 0:
        out[0] = 0
        return 1
    n = 0
    cap = out.shape[0]
    while q != 0 and n < cap:
        # Floor division and modulo, matching Python semantics for
        # negative p with positive q. numba's `//` and `%` on int64
        # follow Python semantics (floor toward -inf).
        a = p // q
        r = p - a * q
        out[n] = a
        n += 1
        p = q
        q = r
    return n


@njit(cache=True)
def _cf_jit_batch_kernel(rationals, out):  # pragma: no cover
    """Vectorized JIT: process every row of `rationals` into `out`.

    rationals : int64[:, 2]
    out       : int64[n, max_terms] (zero-initialized)

    Loops entirely inside numba — no Python-level per-row dispatch.
    """
    n = rationals.shape[0]
    cap = out.shape[1]
    for i in range(n):
        p = rationals[i, 0]
        q = rationals[i, 1]
        if q == 0:
            # Encode an error sentinel (impossible CF: -1 cannot appear
            # as a tail term). Caller post-checks.
            out[i, 0] = -1
            continue
        if q < 0:
            p = -p
            q = -q
        if p == 0:
            out[i, 0] = 0
            continue
        k = 0
        while q != 0 and k < cap:
            a = p // q
            r = p - a * q
            out[i, k] = a
            k += 1
            p = q
            q = r


def cf_expand_jit(p: int, q: int, max_terms: int = 200) -> np.ndarray:
    """JIT-compiled scalar CF expansion. Returns a padded int64 array.

    The first call triggers JIT compilation (slow); subsequent calls are
    fast. For (p, q) outside int64, raises OverflowError — callers
    should use ``cf_expand_array`` to dispatch automatically.

    Returns
    -------
    np.ndarray of dtype int64, shape (max_terms,). Trailing zeros are
    pad/terminator. Note that an a_0 == 0 is also possible (e.g. 1/2 ->
    [0, 2, 0, 0, ...]); use the count returned by ``cf_expand`` for
    unambiguous slicing in that case.
    """
    if not HAS_NUMBA:
        raise RuntimeError(
            "cf_expand_jit requires numba; not importable in this env"
        )
    if q == 0:
        raise ValueError(f"Denominator must be non-zero, got q={q}")
    if not (_INT64_MIN <= p <= _INT64_MAX and _INT64_MIN <= q <= _INT64_MAX):
        raise OverflowError(
            f"|p| or |q| exceeds int64; p={p}, q={q}. Use cf_expand_array."
        )
    out = np.zeros(max_terms, dtype=np.int64)
    _cf_jit_kernel(np.int64(p), np.int64(q), out)
    return out


def _is_int64_safe(p, q) -> bool:
    """Cheap check: do both p and q fit into a signed 64-bit int?"""
    try:
        ip = int(p)
        iq = int(q)
    except (TypeError, ValueError):
        return False
    return _INT64_MIN <= ip <= _INT64_MAX and _INT64_MIN <= iq <= _INT64_MAX


def cf_expand_array(
    rationals_array,
    max_terms: int = 200,
    fallback: str = 'python',
) -> np.ndarray:
    """Vectorized CF expansion over an array of rationals.

    Parameters
    ----------
    rationals_array : np.ndarray, shape (n, 2)
        Numerator/denominator pairs. dtype=int64 triggers the JIT path;
        dtype=object triggers the Python fallback (for arbitrary-
        precision integers exceeding int64).
    max_terms : int
        Output width; rows are zero-padded.
    fallback : str
        'python' (default): non-int64 inputs go through cf_expand_batch.
        'error': raise OverflowError on overflow.

    Returns
    -------
    np.ndarray of dtype int64, shape (n, max_terms). Trailing zeros are
    pad / terminators.
    """
    arr = np.asarray(rationals_array)
    if arr.ndim != 2 or arr.shape[1] != 2:
        raise ValueError(
            f"rationals_array must have shape (n, 2); got {arr.shape}"
        )
    n = arr.shape[0]
    out = np.zeros((n, max_terms), dtype=np.int64)

    # Path 1: dtype-int64 and numba available — single JIT call for all rows.
    if HAS_NUMBA and arr.dtype == np.int64:
        # Defensive zero-denominator check on the cheap before JIT.
        if not np.all(arr[:, 1] != 0):
            bad = int(np.where(arr[:, 1] == 0)[0][0])
            raise ValueError(
                f"row {bad}: denominator zero (p={int(arr[bad, 0])})"
            )
        _cf_jit_batch_kernel(arr, out)
        return out

    # Path 2: dtype-object or no numba — fall back to Python.
    if fallback == 'error':
        # Probe for any oversized entry and raise.
        for i in range(n):
            p = arr[i, 0]
            q = arr[i, 1]
            if not _is_int64_safe(p, q):
                raise OverflowError(
                    f"row {i}: input exceeds int64 (fallback='error')"
                )
    # Python loop, supports arbitrary precision.
    for i in range(n):
        p = int(arr[i, 0])
        q = int(arr[i, 1])
        if q == 0:
            raise ValueError(
                f"row {i}: denominator zero (p={p}, q={q})"
            )
        cf = cf_truncate_to_partial(p, q, max_terms)
        # Pack into the row. All cf entries fit in int64 *unless* the
        # rational itself overflows — for that pathological case, clip.
        for j, a in enumerate(cf):
            if a > _INT64_MAX or a < _INT64_MIN:
                # CF terms are typically small even when p, q are huge;
                # but defend against malformed input.
                out[i, j] = _INT64_MAX if a > 0 else _INT64_MIN
            else:
                out[i, j] = a
    return out


# ---------------------------------------------------------------------------
# Smoke tests / micro-benchmark.
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import time

    print("355/113 =", cf_expand(355, 113))  # Should be [3, 7, 16]
    print("Max digit:", cf_max_digit(355, 113))  # Should be 16

    # Zaremba test for small q
    for q in [5, 7, 10, 13, 50]:
        r = zaremba_test(q)
        status = (
            f"witness a={r['witness']}"
            if r['satisfies']
            else f"FAILS (min max digit = {r['min_max_digit']})"
        )
        print(f"Zaremba(q={q}, bound=5): {status}")

    print(f"\nSturm bound (k=2, N=11): {sturm_bound(2, 11)}")
    print(f"Sturm bound (k=12, N=1): {sturm_bound(12, 1)}")

    import math
    print(f"\nCF(pi) = {cf_from_float(math.pi, max_terms=10)}")

    # Tier-2 micro-benchmark.
    if HAS_NUMBA:
        rng = np.random.default_rng(0)
        N = 10_000
        ps = rng.integers(1, 10**9, size=N, dtype=np.int64)
        qs = rng.integers(1, 10**9, size=N, dtype=np.int64)
        rationals = np.stack([ps, qs], axis=1).astype(np.int64)
        # Warmup JIT.
        cf_expand_array(rationals[:8], max_terms=64)

        t0 = time.perf_counter()
        out_py = cf_expand_batch(list(map(tuple, rationals)), max_terms=64)
        t1 = time.perf_counter()
        out_jit = cf_expand_array(rationals, max_terms=64)
        t2 = time.perf_counter()
        py_dt, jit_dt = t1 - t0, t2 - t1
        print(
            f"\nN={N}: python={py_dt*1000:.1f} ms, "
            f"jit={jit_dt*1000:.1f} ms, speedup={py_dt/jit_dt:.2f}x"
        )
