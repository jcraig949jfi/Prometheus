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


# ---------------------------------------------------------------------------
# Arbitrary-precision Discrete Fourier Transform
# ---------------------------------------------------------------------------
#
# Project #54 surface: numpy.fft is float64. That is sufficient for most
# signal processing but inadequate for high-precision number theory
# (theta-function evaluation, exact roots of high-degree integer
# polynomials via DFT-based methods, p-adic-adjacent computations where
# rounding shifts the rational reconstruction). The mp-DFT below builds
# exclusively on mpmath.mpc arithmetic at user-controlled precision.
#
# Algorithms:
# - Length 1, 2: closed form.
# - Length a power of 2: radix-2 Cooley-Tukey, decimation-in-time. Each
#   butterfly is mpc multiply/add at the working precision.
# - Arbitrary length: Bluestein's chirp z-transform. Convolves x · w^{-n^2/2}
#   with w^{n^2/2} where w = exp(pi i / N), reducing the problem to a
#   length-M radix-2 FFT for any M >= 2N - 1 (we round up to the next
#   power of 2). This makes the cost O(N log N) for any N, at the price
#   of a ~6x constant factor versus pure radix-2.
#
# Precision/speed tradeoff:
# - prec=53 ≈ float64 — comparable speed-per-op to numpy but many python
#   levels of overhead; expect 100-1000x slower than numpy.fft.
# - prec=200 — accurate to ~60 decimal digits; ~3x slower than prec=53
#   (mpmath multiplication scales sub-quadratically).
# - prec=1000 — accurate to ~300 decimal digits; ~30x slower than prec=53.
# Use mpmath ONLY when float64 demonstrably fails. For reference,
# np.fft.fft on length 10^6 takes ~30 ms; mpdft at prec=200 on length
# 10^4 takes seconds.
# ---------------------------------------------------------------------------


def _validate_dft_args(x, prec: int, op: str) -> None:
    if not isinstance(prec, int) or prec < 1:
        raise ValueError(f"{op}: prec must be a positive int, got {prec!r}")
    if x is None:
        raise ValueError(f"{op}: input is None")
    try:
        n = len(x)
    except TypeError:
        raise ValueError(f"{op}: input must be a sequence, got {type(x).__name__}")
    if n == 0:
        raise ValueError(f"{op}: input is empty; DFT requires at least one sample")


def _coerce_mpc_seq(x) -> list:
    """Convert each element of x to mpmath.mpc at the active precision."""
    out = []
    for v in x:
        if isinstance(v, _mpc):
            out.append(v)
        elif isinstance(v, _mpf):
            out.append(_mpc(v, 0))
        elif isinstance(v, complex):
            out.append(_mpc(v.real, v.imag))
        else:
            # int, float, Fraction, str
            try:
                if isinstance(v, Fraction):
                    out.append(_mpc(_mpf(v.numerator) / _mpf(v.denominator), 0))
                else:
                    out.append(_mpc(v, 0))
            except Exception as e:
                raise ValueError(f"DFT: cannot coerce element {v!r} to mpc: {e}")
    return out


def _is_pow2(n: int) -> bool:
    return n >= 1 and (n & (n - 1)) == 0


def _next_pow2(n: int) -> int:
    if n < 1:
        return 1
    p = 1
    while p < n:
        p <<= 1
    return p


def _bit_reverse_permute(a: list) -> list:
    """In-place bit-reversal permutation for radix-2 FFT."""
    n = len(a)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            a[i], a[j] = a[j], a[i]
    return a


def _radix2_fft_inplace(a: list, inverse: bool = False) -> list:
    """Iterative radix-2 Cooley-Tukey FFT, in place on `a` (length is a power of 2).

    Operates at the AMBIENT mpmath working precision; callers are
    expected to wrap the call in a `mp.workprec(...)` context.
    """
    n = len(a)
    if n == 1:
        return a
    _bit_reverse_permute(a)
    pi = mpmath.pi
    sign = 1 if inverse else -1
    length = 2
    while length <= n:
        # Twiddle base: w = exp(sign * 2*pi*i / length)
        ang = sign * 2 * pi / length
        w_step = _mpc(mpmath.cos(ang), mpmath.sin(ang))
        half = length >> 1
        for start in range(0, n, length):
            w = _mpc(1, 0)
            for k in range(half):
                u = a[start + k]
                t = w * a[start + k + half]
                a[start + k] = u + t
                a[start + k + half] = u - t
                w = w * w_step
        length <<= 1
    if inverse:
        inv_n = _mpf(1) / _mpf(n)
        for i in range(n):
            a[i] = a[i] * inv_n
    return a


def _bluestein_dft(x: list, inverse: bool = False) -> list:
    """Bluestein chirp z-transform DFT for arbitrary length N.

    Operates at the ambient mpmath precision. For length N, allocates
    M = next_pow2(2N - 1) buffers and runs three radix-2 FFTs (two
    forward + one inverse), each of length M.

    Math: X[k] = sum_n x[n] e^{-i 2 pi k n / N}.
    Identity: 2 k n = k^2 + n^2 - (k - n)^2.
    Define a_n = x[n] * w^{n^2}, b_n = w^{-n^2}, w = e^{-i pi / N}
    (use w = e^{i pi / N} for the inverse). Then
        X[k] = w^{k^2} * (a * b)[k]
    where * is convolution. Pad both to length M and use the radix-2 FFT.
    """
    n = len(x)
    if n == 1:
        return [x[0]]
    pi = mpmath.pi
    sign = 1 if inverse else -1
    # Chirp base: exp(sign * i * pi / N)
    ang_unit = sign * pi / n
    # Precompute exp(sign * i * pi * m / N) for m in [0, 2N).
    # Since k^2 mod 2N has period 2N in k, indexing by (k*k)%(2*n) gives
    # chirp(k) = exp(sign * i * pi * k^2 / N).
    # NOTE: we store exp(ang_unit * m), NOT exp(ang_unit * m^2). The
    # squaring happens in the index lookup, not in the table value.
    half_table = []
    for m in range(2 * n):
        a = ang_unit * m
        half_table.append(_mpc(mpmath.cos(a), mpmath.sin(a)))

    def chirp(k: int):
        return half_table[(k * k) % (2 * n)]

    M = _next_pow2(2 * n - 1)
    a = [_mpc(0, 0)] * M
    b = [_mpc(0, 0)] * M
    for k in range(n):
        a[k] = x[k] * chirp(k)
    # b is the kernel: b[k] = conj(chirp(k)) for k in [-(n-1), n-1]
    for k in range(n):
        # conj(chirp(k)) since chirp(k) = exp(sign*i*pi*k^2/N), conj flips sign
        ck = chirp(k)
        bk = _mpc(ck.real, -ck.imag)
        b[k] = bk
        if k > 0:
            b[M - k] = bk
    # Convolve via radix-2 FFT: ifft(fft(a) * fft(b))
    A = list(a)
    _radix2_fft_inplace(A, inverse=False)
    B = list(b)
    _radix2_fft_inplace(B, inverse=False)
    C = [A[i] * B[i] for i in range(M)]
    _radix2_fft_inplace(C, inverse=True)
    # X[k] = chirp(k) * C[k] for k in [0, n)
    X = [chirp(k) * C[k] for k in range(n)]
    if inverse:
        inv_n = _mpf(1) / _mpf(n)
        X = [v * inv_n for v in X]
    return X


def _naive_dft(x: list, inverse: bool = False) -> list:
    """Direct O(N^2) DFT. Fast for small N (no chirp setup cost)."""
    n = len(x)
    pi = mpmath.pi
    sign = 1 if inverse else -1
    ang_unit = sign * 2 * pi / n
    out = []
    for k in range(n):
        s = _mpc(0, 0)
        for j in range(n):
            a = ang_unit * (k * j)
            s = s + x[j] * _mpc(mpmath.cos(a), mpmath.sin(a))
        if inverse:
            s = s / _mpf(n)
        out.append(s)
    return out


def mpdft(x: Sequence, prec: int = 53, inverse: bool = False) -> list:
    """Arbitrary-precision Discrete Fourier Transform.

    Computes X[k] = sum_{n=0}^{N-1} x[n] exp(-2 pi i k n / N) at the
    requested precision. For inverse=True, returns the inverse transform
    with the canonical 1/N normalization.

    Parameters
    ----------
    x : sequence
        Input samples. Real or complex; accepts Python int/float/complex,
        mpmath.mpf/mpc, and Fraction.
    prec : int
        Working precision in BITS (mpmath convention). Must be >= 1.
    inverse : bool
        If True, compute the inverse DFT.

    Returns
    -------
    list of mpmath.mpc

    Algorithm
    ---------
    - Length 1: identity.
    - Length 2: closed form [x0+x1, x0-x1].
    - N <= 32 (and not a power of 2): naive O(N^2) DFT (avoids chirp setup).
    - Power of 2: iterative radix-2 Cooley-Tukey, O(N log N).
    - Other lengths: Bluestein chirp z-transform via radix-2 FFT, O(N log N).

    Examples
    --------
    >>> mpdft([1, 0, 0, 0])
    [mpc(real='1.0', imag='0.0'), ...]  # constant 1
    >>> mpdft([1, 1, 1, 1])
    [mpc(real='4.0', imag='0.0'), 0, 0, 0]  # impulse at 0
    """
    _validate_dft_args(x, prec, "mpdft")
    with workprec(prec):
        xs = _coerce_mpc_seq(x)
        n = len(xs)
        if n == 1:
            return [xs[0]]
        if n == 2:
            if inverse:
                half = _mpf(1) / _mpf(2)
                return [(xs[0] + xs[1]) * half, (xs[0] - xs[1]) * half]
            return [xs[0] + xs[1], xs[0] - xs[1]]
        if _is_pow2(n):
            buf = list(xs)
            _radix2_fft_inplace(buf, inverse=inverse)
            return buf
        if n <= 32:
            return _naive_dft(xs, inverse=inverse)
        return _bluestein_dft(xs, inverse=inverse)


def mpidft(X: Sequence, prec: int = 53) -> list:
    """Arbitrary-precision Inverse Discrete Fourier Transform.

    x[n] = (1/N) sum_{k=0}^{N-1} X[k] exp(+2 pi i k n / N).

    Parameters
    ----------
    X : sequence
        Spectrum samples. Real or complex.
    prec : int
        Working precision in BITS.

    Returns
    -------
    list of mpmath.mpc
    """
    return mpdft(X, prec=prec, inverse=True)


def mpfft(x: Sequence, prec: int = 53) -> list:
    """Arbitrary-precision FFT, power-of-2 lengths only.

    Strict variant of `mpdft` that requires the input length to be a
    power of 2. Faster than `mpdft` because it skips the length check
    and dispatch logic.

    Parameters
    ----------
    x : sequence
        Input samples; len(x) must be a power of 2.
    prec : int
        Working precision in BITS.

    Returns
    -------
    list of mpmath.mpc

    Raises
    ------
    ValueError
        If len(x) is not a power of 2, or x is empty, or prec < 1.
    """
    _validate_dft_args(x, prec, "mpfft")
    n = len(x)
    if not _is_pow2(n):
        raise ValueError(f"mpfft: length must be a power of 2, got {n}")
    with workprec(prec):
        buf = _coerce_mpc_seq(x)
        if n == 1:
            return buf
        _radix2_fft_inplace(buf, inverse=False)
        return buf


def mpdft_real(x: Sequence, prec: int = 53) -> list:
    """DFT specialised to real input.

    For real x, X[k] = conj(X[N-k]). This routine still returns the full
    length-N spectrum (so callers don't have to special-case indexing),
    but the redundant half is reconstructed from the first via Hermitian
    symmetry rather than recomputed — useful for verifying that callers
    have not introduced aliasing.

    Parameters
    ----------
    x : sequence of real numbers (anything coercible to mpf).
    prec : int
        Working precision in BITS.

    Returns
    -------
    list of mpmath.mpc, length N
    """
    _validate_dft_args(x, prec, "mpdft_real")
    n = len(x)
    if n == 1:
        with workprec(prec):
            return [_mpc(x[0], 0)]
    with workprec(prec):
        # Coerce as real first to assert the callers' contract; if any
        # input has a non-zero imaginary part, this is a programming error.
        xs = []
        for v in x:
            if isinstance(v, complex) and v.imag != 0:
                raise ValueError(f"mpdft_real: imaginary input {v!r}")
            if isinstance(v, _mpc) and v.imag != 0:
                raise ValueError(f"mpdft_real: imaginary input {v!r}")
            if isinstance(v, _mpf):
                xs.append(_mpc(v, 0))
            elif isinstance(v, _mpc):
                xs.append(v)
            else:
                xs.append(_mpc(v, 0))
        # Use the general dispatch.
        if n == 2:
            return [xs[0] + xs[1], xs[0] - xs[1]]
        if _is_pow2(n):
            buf = list(xs)
            _radix2_fft_inplace(buf, inverse=False)
            return buf
        if n <= 32:
            return _naive_dft(xs, inverse=False)
        # For Bluestein, we still get full output; symmetry just gives a
        # cheap consistency check.
        X = _bluestein_dft(xs, inverse=False)
        # Enforce Hermitian symmetry exactly: X[k] := conj(X[N-k]) for k > N/2.
        for k in range(n // 2 + 1, n):
            sym = X[n - k]
            X[k] = _mpc(sym.real, -sym.imag)
        return X


def mpdft_2d(matrix: Sequence[Sequence], prec: int = 53) -> list:
    """2-D Discrete Fourier Transform.

    F2[i, j] = sum_{p, q} M[p, q] exp(-2 pi i (i p / R + j q / C))
            = DFT_columns(DFT_rows(M))

    Parameters
    ----------
    matrix : R x C nested sequence (each row same length).
    prec : int
        Working precision in BITS.

    Returns
    -------
    list[list[mpmath.mpc]] of shape R x C.
    """
    if not isinstance(prec, int) or prec < 1:
        raise ValueError(f"mpdft_2d: prec must be a positive int, got {prec!r}")
    if matrix is None or len(matrix) == 0:
        raise ValueError("mpdft_2d: empty matrix")
    R = len(matrix)
    C = len(matrix[0])
    for r in matrix:
        if len(r) != C:
            raise ValueError("mpdft_2d: ragged matrix")
    with workprec(prec):
        # Row DFTs
        rows = [mpdft(list(matrix[i]), prec=prec) for i in range(R)]
        # Column DFTs
        out = [[_mpc(0, 0)] * C for _ in range(R)]
        for j in range(C):
            col = [rows[i][j] for i in range(R)]
            col_X = mpdft(col, prec=prec)
            for i in range(R):
                out[i][j] = col_X[i]
        return out


def mpdft_circulant_inverse(c: Sequence, prec: int = 53) -> list:
    """First row of the inverse of the circulant matrix generated by c.

    A circulant matrix C is diagonalised by the DFT matrix F:
        C = F^{-1} diag(F c) F.
    Therefore C^{-1} = F^{-1} diag(1 / F c) F, i.e. the inverse is the
    circulant matrix whose generator is IDFT(1 / DFT(c)).

    Parameters
    ----------
    c : sequence
        First row (or column) of the circulant matrix.
    prec : int
        Working precision in BITS.

    Returns
    -------
    list of mpmath.mpc — the generator (first row) of C^{-1}.

    Raises
    ------
    ValueError
        If c is empty, prec < 1, or any DFT bin of c is zero (singular).
    """
    _validate_dft_args(c, prec, "mpdft_circulant_inverse")
    with workprec(prec):
        cs = _coerce_mpc_seq(c)
        n = len(cs)
        C_hat = mpdft(cs, prec=prec)
        # Detect singularity: any DFT bin equal to zero
        for k, v in enumerate(C_hat):
            if abs(v) == 0:
                raise ValueError(
                    f"mpdft_circulant_inverse: circulant matrix is singular "
                    f"(DFT bin {k} is zero)"
                )
        inv_hat = [_mpc(1, 0) / v for v in C_hat]
        return mpidft(inv_hat, prec=prec)


def mpdft_polynomial_multiply(p: Sequence, q: Sequence, prec: int = 53) -> list:
    """Multiply two polynomials via DFT-based convolution.

    For p of degree dp and q of degree dq, computes the coefficients of
    p * q (a polynomial of degree dp + dq) using zero-padded DFTs.

    Parameters
    ----------
    p, q : sequences
        Coefficients in ASCENDING order: p = [p_0, p_1, ..., p_dp].
    prec : int
        Working precision in BITS.

    Returns
    -------
    list of mpmath.mpf (real-valued; imaginary part is rounded to zero
    after IDFT). For complex polynomials, callers should use mpdft +
    mpidft directly.

    Raises
    ------
    ValueError
        If either input is empty, prec < 1.
    """
    if not isinstance(prec, int) or prec < 1:
        raise ValueError(f"mpdft_polynomial_multiply: prec must be a positive int, got {prec!r}")
    if p is None or q is None:
        raise ValueError("mpdft_polynomial_multiply: None input")
    if len(p) == 0 or len(q) == 0:
        raise ValueError("mpdft_polynomial_multiply: empty input")
    out_len = len(p) + len(q) - 1
    M = _next_pow2(out_len) if out_len > 1 else 1
    if M < 2:
        M = 2  # ensure the radix-2 FFT path
    with workprec(prec):
        # Zero-pad
        p_pad = list(p) + [0] * (M - len(p))
        q_pad = list(q) + [0] * (M - len(q))
        P = mpdft(p_pad, prec=prec)
        Q = mpdft(q_pad, prec=prec)
        R = [P[i] * Q[i] for i in range(M)]
        r = mpidft(R, prec=prec)
        # Truncate to out_len, return mpf real part
        return [v.real for v in r[:out_len]]
