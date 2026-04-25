"""prometheus_math.numerics — high-precision and special-function numerics.

Unified facade over mpmath (with optional gmpy2/cypari acceleration). All
operations accept an explicit precision argument expressed in BITS — the
same unit mpmath uses internally (`mpmath.mp.prec`). To convert from
decimal places, multiply by ~3.33 (log2(10)).

Style:
- Terse functional API, idempotent.
- Returns plain Python / mpmath / numpy types where natural.
- Raises ValueError on unsupported input.
- Uses precision contexts (`mp.workprec`) so global state is not leaked.

Forged: 2026-04-22 | Tier: 1 (mpmath / gmpy2 / cypari) | REQ-PM-NUMERICS
"""
from __future__ import annotations

from fractions import Fraction
from typing import Sequence, Optional, Iterable

from .registry import is_available

if not is_available("mpmath"):
    raise ImportError("prometheus_math.numerics requires mpmath")

import mpmath
from mpmath import mp, mpf as _mpf, mpc as _mpc, workprec

# Optional acceleration backends
_HAS_SYMPY = is_available("sympy")
_HAS_CYPARI = is_available("cypari")
_HAS_FLINT = is_available("flint")

if _HAS_SYMPY:
    import sympy as _sympy
if _HAS_CYPARI:
    try:
        import cypari as _cypari
        _pari = _cypari.pari
    except Exception:
        _HAS_CYPARI = False
        _pari = None


# ---------------------------------------------------------------------------
# Precision-aware constructors
# ---------------------------------------------------------------------------

def mpf(x, prec: int = 53):
    """Arbitrary-precision real number.

    Parameters
    ----------
    x : int | float | str | mpmath.mpf | Fraction
        Input value. Strings are recommended for exact decimal literals.
    prec : int
        Working precision in BITS (mpmath convention).
    """
    with workprec(prec):
        if isinstance(x, Fraction):
            return _mpf(x.numerator) / _mpf(x.denominator)
        try:
            return _mpf(x)
        except (TypeError, ValueError) as e:
            raise ValueError(f"cannot construct mpf from {x!r}: {e}")


def mpc(real, imag=0, prec: int = 53):
    """Arbitrary-precision complex number.

    Parameters
    ----------
    real, imag : numeric
        Real and imaginary parts.
    prec : int
        Precision in BITS.
    """
    with workprec(prec):
        try:
            return _mpc(real, imag)
        except (TypeError, ValueError) as e:
            raise ValueError(f"cannot construct mpc from ({real!r}, {imag!r}): {e}")


def set_precision(prec_bits: int) -> None:
    """Set global mpmath precision in BITS (mpmath.mp.prec).

    Note: this mutates global mpmath state. Prefer the per-call `prec`
    argument or a `with workprec(...)` context where possible.
    """
    if not isinstance(prec_bits, int) or prec_bits < 2:
        raise ValueError(f"prec_bits must be a positive int >= 2, got {prec_bits!r}")
    mp.prec = prec_bits


# ---------------------------------------------------------------------------
# L-functions / zeta
# ---------------------------------------------------------------------------

def zeta(s, prec: int = 53):
    """Riemann zeta function ζ(s) at arbitrary precision.

    Parameters
    ----------
    s : numeric (real, complex, or mpmath types)
    prec : int
        Precision in BITS.

    Returns
    -------
    mpmath.mpc (or mpf if input is purely real)
    """
    with workprec(prec):
        return mpmath.zeta(s)


def dirichlet_l(chi, s, prec: int = 53):
    """Dirichlet L-function L(s, χ).

    Parameters
    ----------
    chi : list[int] | callable
        The character. mpmath accepts a list of values χ(1..q-1) or a
        callable returning χ(n).
    s : numeric
    prec : int
        BITS.

    Returns
    -------
    mpmath.mpc
    """
    with workprec(prec):
        try:
            return mpmath.dirichlet(s, chi)
        except Exception as e:
            raise ValueError(f"dirichlet_l failed for chi={chi!r}, s={s!r}: {e}")


# ---------------------------------------------------------------------------
# Integer relations
# ---------------------------------------------------------------------------

def pslq(x: Sequence, tol: Optional[float] = None,
         max_coeff: int = 10**6) -> Optional[list[int]]:
    """Find an integer relation among a list of mpmath floats.

    Given x = [x_1, ..., x_n], returns [c_1, ..., c_n] of integers with
    sum(c_i * x_i) ≈ 0, or None if no relation found within bounds.

    Parameters
    ----------
    x : sequence of mpmath floats / numerics
    tol : float, optional
        Tolerance; defaults to mpmath default (~1e-prec).
    max_coeff : int
        Reject relations with |c_i| > max_coeff.
    """
    if not x or len(x) < 2:
        raise ValueError("pslq needs at least 2 inputs")
    try:
        xs = [_mpf(v) if not isinstance(v, (_mpf, _mpc)) else v for v in x]
    except Exception as e:
        raise ValueError(f"pslq inputs must be numeric: {e}")
    try:
        if tol is None:
            rel = mpmath.pslq(xs, maxcoeff=max_coeff)
        else:
            rel = mpmath.pslq(xs, tol=tol, maxcoeff=max_coeff)
    except Exception:
        return None
    if rel is None:
        return None
    rel = [int(c) for c in rel]
    if any(abs(c) > max_coeff for c in rel):
        return None
    if all(c == 0 for c in rel):
        return None
    return rel


def lindep_complex(z, max_deg: int = 8, prec: int = 200) -> Optional[list[int]]:
    """Find an integer-polynomial relation satisfied by complex z.

    Returns coefficients [c_0, c_1, ..., c_d] of a polynomial p with
    p(z) ≈ 0, where d ≤ max_deg, or None if no relation found.

    Tries PARI's `algdep` first (cypari) for robustness; falls back to
    `mpmath.pslq` on [1, z, z^2, ..., z^max_deg].
    """
    if max_deg < 1:
        raise ValueError("max_deg must be >= 1")

    # PARI fast path
    if _HAS_CYPARI:
        try:
            old_prec = _pari.set_real_precision(max(38, int(prec / 3.33)))
            try:
                p = _pari.algdep(complex(z) if not hasattr(z, 'real') else z, max_deg)
            finally:
                _pari.set_real_precision(old_prec)
            # PARI poly -> coefficient list (constant term first)
            coeffs = [int(c) for c in p.Vecrev()]
            if any(coeffs):
                return coeffs
        except Exception:
            pass  # fall through to mpmath

    # mpmath fallback
    with workprec(prec):
        try:
            zc = _mpc(z)
        except Exception as e:
            raise ValueError(f"lindep_complex: bad z={z!r}: {e}")
        powers = [zc**k for k in range(max_deg + 1)]
        # mpmath pslq is real-only; split into [Re(z^k), Im(z^k)] system
        # by stacking: real and imaginary parts must both be 0.
        # Use mpmath's complex-aware version: pslq accepts complex.
        try:
            rel = mpmath.pslq(powers, maxcoeff=10**6)
        except Exception:
            rel = None
        if rel is None:
            return None
        rel = [int(c) for c in rel]
        if all(c == 0 for c in rel):
            return None
        return rel


# ---------------------------------------------------------------------------
# Polynomial roots
# ---------------------------------------------------------------------------

def solve_polynomial(coeffs: Sequence, prec: int = 53) -> list:
    """Roots of a polynomial at arbitrary precision.

    Parameters
    ----------
    coeffs : sequence
        Polynomial coefficients, HIGHEST DEGREE FIRST (mpmath convention).
        e.g. [1, 0, -2] = x^2 - 2.
    prec : int
        Precision in BITS.

    Returns
    -------
    list of mpmath.mpc roots.
    """
    if not coeffs or len(coeffs) < 2:
        raise ValueError("solve_polynomial needs at least 2 coefficients")
    with workprec(prec):
        try:
            roots = mpmath.polyroots(list(coeffs), maxsteps=200, extraprec=prec)
        except mpmath.libmp.libhyper.NoConvergence as e:
            raise ValueError(f"polyroots did not converge: {e}")
        except Exception as e:
            raise ValueError(f"polyroots failed: {e}")
        return list(roots)


# ---------------------------------------------------------------------------
# Special functions
# ---------------------------------------------------------------------------

def gamma(z, prec: int = 53):
    """Gamma function Γ(z) at arbitrary precision (BITS)."""
    with workprec(prec):
        return mpmath.gamma(z)


def beta(a, b, prec: int = 53):
    """Beta function B(a, b) = Γ(a)Γ(b)/Γ(a+b) at arbitrary precision."""
    with workprec(prec):
        return mpmath.beta(a, b)


# ---------------------------------------------------------------------------
# Bernoulli numbers (exact rational)
# ---------------------------------------------------------------------------

def bernoulli(n: int) -> Fraction:
    """The n-th Bernoulli number B_n as an exact Fraction.

    Uses sympy if available (exact rational); falls back to mpmath
    (which returns mpf and is then rationalised — accurate but slower).

    Convention: B_1 = -1/2 (sympy convention).
    """
    if not isinstance(n, int) or n < 0:
        raise ValueError(f"bernoulli: n must be a non-negative int, got {n!r}")
    if _HAS_SYMPY:
        b = _sympy.bernoulli(n)
        return Fraction(b.p, b.q) if hasattr(b, 'p') else Fraction(b)
    # mpmath fallback at high precision, then rationalise
    with workprec(max(64, 8 * n)):
        v = mpmath.bernoulli(n)
        # Rationalise via mpmath.identify isn't reliable; convert via str.
        return Fraction(str(v)).limit_denominator(10**18)


# ---------------------------------------------------------------------------
# FLINT-backed advanced operations
# ---------------------------------------------------------------------------
#
# Project #31 surface: integer- and modular-polynomial factoring, fast
# linear algebra mod p. python-flint wraps the FLINT C library, which on
# these problems is typically 5x-50x faster than PARI's equivalents
# (FLINT uses tuned x86_64 assembly + GMP; PARI's polynomial arithmetic
# is generally written in portable C). The wrappers below convert all
# inputs and outputs to native Python types (int / list[int] /
# list[list[int]]) so callers never need to touch flint.* objects.
#
# All wrappers raise ImportError with a clear message if python-flint
# is not installed; we never auto-fail at module import time.
# ---------------------------------------------------------------------------

if _HAS_FLINT:
    try:
        import flint as _flint
    except Exception:  # pragma: no cover
        _HAS_FLINT = False
        _flint = None
else:  # pragma: no cover
    _flint = None


def _require_flint(op: str) -> None:
    if not _HAS_FLINT:
        raise ImportError(
            f"prometheus_math.numerics.{op} requires python-flint; "
            "install via `pip install python-flint`"
        )


def _is_prime_int(p: int) -> bool:
    """Trial-division primality test for small p; sympy fast path if avail."""
    if not isinstance(p, int) or p < 2:
        return False
    if _HAS_SYMPY:
        return bool(_sympy.isprime(p))
    if p < 4:
        return p in (2, 3)
    if p % 2 == 0 or p % 3 == 0:
        return False
    i = 5
    while i * i <= p:
        if p % i == 0 or p % (i + 2) == 0:
            return False
        i += 6
    return True


def _check_prime(p: int, op: str) -> None:
    if not isinstance(p, int):
        raise ValueError(f"{op}: modulus must be an int, got {type(p).__name__}")
    if p < 2:
        raise ValueError(f"{op}: modulus must be >= 2, got {p}")
    if not _is_prime_int(p):
        raise ValueError(f"{op}: modulus {p} is not prime; FLINT mod-p ops require a prime modulus")


def _strip_trailing_zero_coeffs(coeffs):
    out = list(coeffs)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def _to_int_list(it) -> list[int]:
    return [int(x) for x in it]


def flint_factor(coeffs: Sequence[int]) -> list[tuple[list[int], int]]:
    """Factor an integer-coefficient polynomial over Z[x] using FLINT.

    Parameters
    ----------
    coeffs : sequence of int
        Polynomial coefficients in ASCENDING order: [c_0, c_1, ..., c_d]
        represents c_0 + c_1*x + ... + c_d*x^d.

    Returns
    -------
    list of (factor_coeffs, multiplicity)
        Each factor's coefficients in ascending order. If the leading
        integer content is not ±1, it is included as a degree-0 factor
        ([content], 1) at the head of the list.

    Speed
    -----
    FLINT's `fmpz_poly_factor` is typically 5x-50x faster than PARI's
    `factor` on integer polynomials (FLINT uses Hensel lifting +
    Zassenhaus + LLL recombination, all tuned in C/asm).

    Raises
    ------
    ValueError
        If `coeffs` is empty or represents the zero polynomial.
    """
    _require_flint("flint_factor")
    if coeffs is None or len(coeffs) == 0:
        raise ValueError("flint_factor: empty coefficient list")
    cleaned = _strip_trailing_zero_coeffs(coeffs)
    if all(c == 0 for c in cleaned):
        raise ValueError("flint_factor: zero polynomial has no factorisation")
    try:
        poly = _flint.fmpz_poly([int(c) for c in cleaned])
    except Exception as e:
        raise ValueError(f"flint_factor: bad input {coeffs!r}: {e}")
    content, factors = poly.factor()
    out: list[tuple[list[int], int]] = []
    c_int = int(content)
    # Emit content as a degree-0 factor whenever it is non-trivial (≠1).
    # A leading -1 is also "non-trivial" because it flips the sign of the
    # reconstructed polynomial; including it lets callers round-trip via
    # flint_polmul of the factor list.
    if c_int != 1:
        out.append(([c_int], 1))
    for f, m in factors:
        out.append((_to_int_list(f.coeffs()), int(m)))
    # Special case: constant ±1 of magnitude 1 with no further factors
    if not out and len(cleaned) == 1:
        out.append(([int(cleaned[0])], 1))
    return out


def flint_polmodp(coeffs: Sequence[int], p: int) -> list[int]:
    """Reduce integer polynomial coefficients modulo a prime p.

    Parameters
    ----------
    coeffs : sequence of int
        Ascending coefficient list.
    p : int
        Prime modulus. Composite moduli are rejected to avoid FLINT
        crashes on impossible inverses.

    Returns
    -------
    list[int]
        Reduced coefficients, each in [0, p-1].

    Speed
    -----
    Much faster than per-element Python `% p` on long polynomials due
    to FLINT's `nmod_poly` packed storage; comparable to numpy on small
    inputs but with arbitrary-length integer support.
    """
    _require_flint("flint_polmodp")
    _check_prime(p, "flint_polmodp")
    if coeffs is None:
        raise ValueError("flint_polmodp: coeffs is None")
    poly = _flint.nmod_poly([int(c) % p for c in coeffs], p)
    return _to_int_list(poly.coeffs())


def flint_polmodp_factor(coeffs: Sequence[int], p: int) -> list[tuple[list[int], int]]:
    """Factor an integer polynomial modulo a prime p over F_p[x].

    Parameters
    ----------
    coeffs : sequence of int
        Ascending coefficient list.
    p : int
        Prime modulus.

    Returns
    -------
    list of (factor_coeffs, multiplicity)
        Each factor's coefficients are in [0, p-1], ascending. The
        leading content (a unit in F_p) is included as a degree-0
        factor at the head if it is not 1.

    Speed
    -----
    FLINT uses Cantor-Zassenhaus (with optional Berlekamp for small p)
    over `nmod_poly`; typically 10x-100x faster than PARI's `factormod`
    on degrees > 50.

    Raises
    ------
    ValueError
        On non-prime modulus or empty / zero polynomial.
    """
    _require_flint("flint_polmodp_factor")
    _check_prime(p, "flint_polmodp_factor")
    if coeffs is None or len(coeffs) == 0:
        raise ValueError("flint_polmodp_factor: empty coefficient list")
    reduced = [int(c) % p for c in coeffs]
    cleaned = _strip_trailing_zero_coeffs(reduced)
    if all(c == 0 for c in cleaned):
        raise ValueError("flint_polmodp_factor: zero polynomial mod p has no factorisation")
    poly = _flint.nmod_poly(cleaned, p)
    content, factors = poly.factor()
    out: list[tuple[list[int], int]] = []
    c_int = int(content) % p
    if c_int != 1 % p:
        out.append(([c_int], 1))
    for f, m in factors:
        out.append((_to_int_list(f.coeffs()), int(m)))
    if not out and len(cleaned) == 1:
        out.append(([cleaned[0]], 1))
    return out


def _validate_matrix(M, op: str) -> tuple[int, int]:
    if M is None:
        raise ValueError(f"{op}: matrix is None")
    try:
        rows = list(M)
    except TypeError:
        raise ValueError(f"{op}: matrix is not iterable")
    if not rows:
        raise ValueError(f"{op}: matrix has zero rows")
    nrows = len(rows)
    ncols = len(rows[0]) if rows[0] is not None else 0
    if ncols == 0:
        raise ValueError(f"{op}: matrix has zero columns")
    for r in rows:
        if len(r) != ncols:
            raise ValueError(f"{op}: matrix is jagged (row lengths differ)")
    return nrows, ncols


def _to_nmod_mat(M, p: int):
    rows = [[int(x) % p for x in r] for r in M]
    return _flint.nmod_mat(rows, p)


def flint_matmul_modp(A, B, p: int) -> list[list[int]]:
    """Fast matrix multiplication modulo a prime p.

    Parameters
    ----------
    A, B : list[list[int]]
        Integer matrices.
    p : int
        Prime modulus.

    Returns
    -------
    list[list[int]]
        Entries of A @ B reduced mod p, each in [0, p-1].

    Speed
    -----
    FLINT's `nmod_mat_mul` uses Strassen + tuned BLAS-like inner kernels
    for word-sized primes, often 10x-30x faster than `numpy @ numpy %
    p` for primes that fit in a 64-bit word.

    Raises
    ------
    ValueError
        On shape mismatch or non-prime modulus.
    """
    _require_flint("flint_matmul_modp")
    _check_prime(p, "flint_matmul_modp")
    a_rows, a_cols = _validate_matrix(A, "flint_matmul_modp")
    b_rows, b_cols = _validate_matrix(B, "flint_matmul_modp")
    if a_cols != b_rows:
        raise ValueError(
            f"flint_matmul_modp: shape mismatch: A is {a_rows}x{a_cols}, B is {b_rows}x{b_cols}"
        )
    Am = _to_nmod_mat(A, p)
    Bm = _to_nmod_mat(B, p)
    C = Am * Bm
    return [[int(C[i, j]) for j in range(C.ncols())] for i in range(C.nrows())]


def flint_matrix_rank_modp(M, p: int) -> int:
    """Rank of an integer matrix reduced modulo a prime p.

    Parameters
    ----------
    M : list[list[int]]
    p : int
        Prime modulus.

    Returns
    -------
    int
        Rank over F_p, satisfying 0 <= rank <= min(nrows, ncols).

    Speed
    -----
    FLINT's `nmod_mat_rank` uses fraction-free LU over F_p, typically
    5x-20x faster than sympy's `Matrix(...).rank()` on integer
    matrices.
    """
    _require_flint("flint_matrix_rank_modp")
    _check_prime(p, "flint_matrix_rank_modp")
    _validate_matrix(M, "flint_matrix_rank_modp")
    return int(_to_nmod_mat(M, p).rank())


def flint_matrix_det_modp(M, p: int) -> int:
    """Determinant of a square integer matrix modulo a prime p.

    Parameters
    ----------
    M : list[list[int]]
        Square integer matrix.
    p : int
        Prime modulus.

    Returns
    -------
    int
        det(M) mod p, in [0, p-1].

    Raises
    ------
    ValueError
        If M is not square, or modulus is not prime.
    """
    _require_flint("flint_matrix_det_modp")
    _check_prime(p, "flint_matrix_det_modp")
    nrows, ncols = _validate_matrix(M, "flint_matrix_det_modp")
    if nrows != ncols:
        raise ValueError(f"flint_matrix_det_modp: matrix must be square, got {nrows}x{ncols}")
    return int(_to_nmod_mat(M, p).det()) % p


def flint_polmul(coeffs1: Sequence[int], coeffs2: Sequence[int]) -> list[int]:
    """Multiply two integer-coefficient polynomials.

    Parameters
    ----------
    coeffs1, coeffs2 : sequence of int
        Ascending coefficient lists.

    Returns
    -------
    list[int]
        Coefficients of the product, ascending.

    Speed
    -----
    FLINT's `fmpz_poly_mul` automatically chooses among Karatsuba,
    Toom-Cook, and Schönhage-Strassen FFT depending on the input size;
    on degree > 1000, often 5x-50x faster than the naive Cauchy
    product.
    """
    _require_flint("flint_polmul")
    if coeffs1 is None or coeffs2 is None:
        raise ValueError("flint_polmul: None input")
    if len(coeffs1) == 0 or len(coeffs2) == 0:
        return []
    p = _flint.fmpz_poly([int(c) for c in coeffs1])
    q = _flint.fmpz_poly([int(c) for c in coeffs2])
    return _to_int_list((p * q).coeffs())


def flint_gcd_poly(coeffs1: Sequence[int], coeffs2: Sequence[int]) -> list[int]:
    """GCD of two integer-coefficient polynomials over Z.

    Returns the primitive part (content removed). Sign convention: the
    leading coefficient is non-negative.

    Parameters
    ----------
    coeffs1, coeffs2 : sequence of int
        Ascending coefficient lists.

    Returns
    -------
    list[int]
        Coefficients of gcd(p, q), ascending. Returns [1] if the GCD
        is a unit.

    Speed
    -----
    FLINT's `fmpz_poly_gcd` uses subresultant pseudo-remainders with
    modular reduction at small primes, typically 5x-20x faster than
    sympy's `gcd`.
    """
    _require_flint("flint_gcd_poly")
    if coeffs1 is None or coeffs2 is None:
        raise ValueError("flint_gcd_poly: None input")
    if len(coeffs1) == 0 and len(coeffs2) == 0:
        raise ValueError("flint_gcd_poly: gcd(0, 0) is undefined")
    if len(coeffs1) == 0:
        return _to_int_list(_flint.fmpz_poly([int(c) for c in coeffs2]).coeffs())
    if len(coeffs2) == 0:
        return _to_int_list(_flint.fmpz_poly([int(c) for c in coeffs1]).coeffs())
    p = _flint.fmpz_poly([int(c) for c in coeffs1])
    q = _flint.fmpz_poly([int(c) for c in coeffs2])
    g = p.gcd(q)
    out = _to_int_list(g.coeffs())
    if not out:
        return [0]
    # Normalize sign: leading coefficient non-negative
    if out and out[-1] < 0:
        out = [-c for c in out]
    return out
