"""Tests for prometheus_math.numerics arbitrary-precision DFT.

Project #54 — pm.numerics.dft via mpmath.

Test categories follow techne/skills/math-tdd.md:
  Authority — output matches authoritative reference values.
  Property  — invariants hold across many inputs (Hypothesis).
  Edge      — empty / singleton / malformed / pathological scale.
  Composition — DFT composes correctly with other operations.
"""
from __future__ import annotations

import math

import mpmath
import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

from prometheus_math import numerics as N


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _to_complex(x):
    """Convert mpmath types to native Python complex."""
    if isinstance(x, mpmath.mpc):
        return complex(float(x.real), float(x.imag))
    if isinstance(x, mpmath.mpf):
        return complex(float(x), 0.0)
    return complex(x)


def _close(a, b, tol=1e-10):
    return abs(_to_complex(a) - _to_complex(b)) < tol


def _all_close(A, B, tol=1e-10):
    return len(A) == len(B) and all(_close(a, b, tol) for a, b in zip(A, B))


# ---------------------------------------------------------------------------
# AUTHORITY tests
# ---------------------------------------------------------------------------


def test_authority_dft_unit_pulse():
    """DFT of [1, 0, 0, 0] = [1, 1, 1, 1].

    Reference: standard DFT identity. The DFT of a unit pulse delta_0 is
    the constant function 1 (Oppenheim & Schafer, "Discrete-Time Signal
    Processing", 3rd ed., Eq. 8.55).
    """
    X = N.mpdft([1, 0, 0, 0], prec=80)
    assert _all_close(X, [1, 1, 1, 1], tol=1e-20)


def test_authority_dft_constant_input():
    """DFT of [1, 1, 1, 1] = [4, 0, 0, 0].

    Reference: DFT of a constant is N*delta_0. Standard textbook identity
    (Oppenheim & Schafer, Eq. 8.55, dual of the unit-pulse example).
    """
    X = N.mpdft([1, 1, 1, 1], prec=80)
    assert _close(X[0], 4, tol=1e-20)
    for k in range(1, 4):
        assert abs(_to_complex(X[k])) < 1e-20


def test_authority_dft_real_cosine_spectrum():
    """DFT of cos(2*pi*k/N) for N=8 has peaks at k=1 and k=N-1=7.

    Reference: Euler decomposition cos(theta) = (e^{i theta} + e^{-i theta})/2
    placed on the DFT grid yields N/2 at the two symmetric bins.
    Cross-checked against numpy.fft.fft for the same input.
    """
    N_pts = 8
    with mpmath.workprec(80):
        x = [mpmath.cos(2 * mpmath.pi * k / N_pts) for k in range(N_pts)]
    X = N.mpdft(x, prec=80)
    # Peaks at k=1 and k=7 of magnitude N/2 = 4
    assert abs(abs(_to_complex(X[1])) - 4.0) < 1e-12
    assert abs(abs(_to_complex(X[7])) - 4.0) < 1e-12
    # All other bins close to zero
    for k in (0, 2, 3, 4, 5, 6):
        assert abs(_to_complex(X[k])) < 1e-12


def test_authority_dft_round_trip_real():
    """DFT followed by IDFT recovers the input exactly (within tolerance).

    Reference: Parseval/Plancherel — IDFT is the exact inverse of DFT
    by construction. (Oppenheim & Schafer, Eq. 8.56.)
    """
    x = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    X = N.mpdft(x, prec=100)
    x_back = N.mpidft(X, prec=100)
    for a, b in zip(x, x_back):
        assert abs(_to_complex(a) - _to_complex(b)) < 1e-25


def test_authority_dft_agrees_with_numpy_at_high_prec():
    """At prec=200, mpdft of length-8 real input agrees with numpy.fft.fft.

    Reference: numpy.fft.fft (float64 IEEE-754) — the high-precision
    answer must agree to within float64 precision of numpy's result.
    """
    x = [0.5, 1.5, -2.0, 3.25, 0.0, -1.75, 2.5, -0.5]
    X_mp = N.mpdft(x, prec=200)
    X_np = np.fft.fft(x)
    for k in range(8):
        diff = abs(_to_complex(X_mp[k]) - X_np[k])
        # numpy float64 carries ~1e-14 relative error; high-prec must agree.
        assert diff < 1e-12, f"bin {k}: mpdft={X_mp[k]}, numpy={X_np[k]}, diff={diff}"


# ---------------------------------------------------------------------------
# PROPERTY tests
# ---------------------------------------------------------------------------


@given(st.lists(st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False),
                min_size=1, max_size=12))
@settings(max_examples=30, deadline=None)
def test_property_length_preserved(x):
    """DFT output length equals input length, for any N >= 1."""
    X = N.mpdft(x, prec=53)
    assert len(X) == len(x)


@given(st.lists(st.floats(min_value=-5, max_value=5, allow_nan=False, allow_infinity=False),
                min_size=1, max_size=8),
       st.lists(st.floats(min_value=-5, max_value=5, allow_nan=False, allow_infinity=False),
                min_size=1, max_size=8),
       st.floats(min_value=-3, max_value=3, allow_nan=False, allow_infinity=False),
       st.floats(min_value=-3, max_value=3, allow_nan=False, allow_infinity=False))
@settings(max_examples=20, deadline=None)
def test_property_linearity(x, y, a, b):
    """DFT(a*x + b*y) = a*DFT(x) + b*DFT(y).

    Linearity is the foundational property of the discrete Fourier
    transform — a linear operator over C^N.
    """
    n = min(len(x), len(y))
    if n < 1:
        return
    x = x[:n]
    y = y[:n]
    z = [a * xi + b * yi for xi, yi in zip(x, y)]
    Xz = N.mpdft(z, prec=80)
    Xx = N.mpdft(x, prec=80)
    Xy = N.mpdft(y, prec=80)
    for k in range(n):
        lhs = _to_complex(Xz[k])
        rhs = a * _to_complex(Xx[k]) + b * _to_complex(Xy[k])
        assert abs(lhs - rhs) < 1e-10


@given(st.lists(st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False),
                min_size=1, max_size=10))
@settings(max_examples=20, deadline=None)
def test_property_parseval(x):
    """Parseval's theorem: sum |x_n|^2 = (1/N) * sum |X_k|^2.

    Energy is preserved between time and frequency domains
    (Oppenheim & Schafer, Eq. 8.61).
    """
    n = len(x)
    X = N.mpdft(x, prec=80)
    e_time = sum(xi ** 2 for xi in x)
    e_freq = sum(abs(_to_complex(Xk)) ** 2 for Xk in X) / n
    assert abs(e_time - e_freq) < 1e-9 * max(1.0, e_time)


@given(st.lists(st.floats(min_value=-5, max_value=5, allow_nan=False, allow_infinity=False),
                min_size=1, max_size=10),
       st.integers(min_value=53, max_value=200))
@settings(max_examples=15, deadline=None)
def test_property_round_trip_under_precision(x, prec):
    """mpdft → mpidft is identity within precision-controlled tolerance.

    Hypothesis sweeps precision in [53, 200] bits. The round-trip
    error should fall below 2^{-prec/2} for any prec.
    """
    X = N.mpdft(x, prec=prec)
    x_back = N.mpidft(X, prec=prec)
    tol = 2 ** (-prec // 2 + 5)
    for a, b in zip(x, x_back):
        assert abs(_to_complex(a) - _to_complex(b)) < max(tol, 1e-14)


@given(st.lists(st.floats(min_value=-10, max_value=10, allow_nan=False, allow_infinity=False),
                min_size=1, max_size=12))
@settings(max_examples=20, deadline=None)
def test_property_dc_equals_sum(x):
    """X[0] = sum_n x[n] (DC component is the sum). Always."""
    X = N.mpdft(x, prec=80)
    s = sum(x)
    assert abs(_to_complex(X[0]) - s) < 1e-10 * max(1.0, abs(s))


# ---------------------------------------------------------------------------
# EDGE-CASE tests
# ---------------------------------------------------------------------------


def test_edge_empty_input_raises():
    """Empty input raises ValueError."""
    with pytest.raises(ValueError):
        N.mpdft([], prec=53)


def test_edge_singleton_input_returns_input():
    """Singleton input returns [x[0]] unchanged.

    DFT of a length-1 sequence is itself by definition.
    """
    X = N.mpdft([42.0], prec=53)
    assert len(X) == 1
    assert _close(X[0], 42.0, tol=1e-12)


def test_edge_invalid_precision_raises():
    """prec < 1 raises ValueError."""
    with pytest.raises(ValueError):
        N.mpdft([1, 2, 3, 4], prec=0)
    with pytest.raises(ValueError):
        N.mpdft([1, 2, 3, 4], prec=-5)


def test_edge_length_2_simple_case():
    """Length-2 input: DFT is [x0+x1, x0-x1] (Hadamard pair)."""
    X = N.mpdft([3.0, 5.0], prec=80)
    assert _close(X[0], 8.0, tol=1e-15)  # 3 + 5
    assert _close(X[1], -2.0, tol=1e-15)  # 3 - 5


def test_edge_large_non_power_of_two_length():
    """Length-1000 (not power of 2) completes via Bluestein's algorithm.

    Verifies algorithmic correctness for arbitrary lengths, not just
    radix-2. Spot-check a few bins against numpy.fft.fft.
    """
    rng = np.random.default_rng(42)
    x = rng.standard_normal(1000).tolist()
    X = N.mpdft(x, prec=80)
    assert len(X) == 1000
    X_np = np.fft.fft(x)
    # Spot-check selected bins
    for k in (0, 1, 7, 250, 500, 999):
        diff = abs(_to_complex(X[k]) - X_np[k])
        # numpy float64 has accumulated ~1e-10 absolute error at N=1000
        assert diff < 1e-8, f"bin {k}: mpdft - numpy = {diff}"


def test_edge_numerical_precision_boundary():
    """At very low prec=20 bits, DFT is still consistent (not garbage)."""
    x = [1.0, 2.0, 3.0, 4.0]
    X = N.mpdft(x, prec=20)
    # DC should still equal the sum modulo low-precision error.
    assert abs(_to_complex(X[0]) - 10.0) < 1e-3


def test_edge_complex_input_supported():
    """DFT accepts complex input (mpc type)."""
    x = [1 + 1j, 2 - 1j, 3, 4 + 2j]
    X = N.mpdft(x, prec=80)
    assert len(X) == 4
    # DC = sum
    s = sum(x)
    assert abs(_to_complex(X[0]) - s) < 1e-12


# ---------------------------------------------------------------------------
# COMPOSITION tests
# ---------------------------------------------------------------------------


def test_composition_mpdft_mpidft_round_trip_real():
    """mpdft then mpidft on real input == input (within tol).

    Composition: forward+inverse is the identity. This catches
    normalization-factor bugs (off-by-N errors).
    """
    x = [1.7, -2.3, 0.5, 4.1, -0.8, 3.0, 2.5, -1.1]
    X = N.mpdft(x, prec=120)
    y = N.mpidft(X, prec=120)
    for a, b in zip(x, y):
        assert abs(_to_complex(a) - _to_complex(b)) < 1e-30


def test_composition_polynomial_multiply_vs_numpy_convolve():
    """mpdft_polynomial_multiply matches numpy.convolve.

    Composition: DFT-based polynomial multiplication composes the DFT
    with pointwise product and IDFT — must agree with the direct
    convolution algorithm.
    """
    p = [1, 2, 3]       # 1 + 2x + 3x^2
    q = [4, 5, 6, 7]    # 4 + 5x + 6x^2 + 7x^3
    expected = np.convolve(p, q).tolist()  # [4, 13, 28, 34, 32, 21]
    result = N.mpdft_polynomial_multiply(p, q, prec=80)
    assert len(result) == len(expected)
    for a, b in zip(result, expected):
        assert abs(float(a) - float(b)) < 1e-10


def test_composition_circulant_inverse_identity():
    """Circulant-via-DFT inverse times the original circulant matrix == I.

    Composition: circulant matrices are diagonalized by the DFT; inverting
    via DFT and multiplying back must give the identity.
    """
    c = [4.0, 1.0, 2.0, 3.0]  # generator of a 4x4 circulant matrix
    n = len(c)
    # Build the circulant matrix C explicitly.
    C = np.array([[c[(i - j) % n] for j in range(n)] for i in range(n)])
    inv = N.mpdft_circulant_inverse(c, prec=120)
    # Convert mp inverse generator back to numpy matrix.
    inv_row = [_to_complex(z) for z in inv]
    C_inv = np.array([[inv_row[(i - j) % n] for j in range(n)] for i in range(n)])
    product = C @ C_inv
    I = np.eye(n)
    err = np.max(np.abs(product - I))
    assert err < 1e-10, f"max |C C^-1 - I| = {err}"


def test_mpfft_power_of_two_only():
    """mpfft requires power-of-2 length; raises ValueError otherwise."""
    # Power-of-2 length is accepted and matches mpdft.
    x = [1.0, 2.0, 3.0, 4.0]
    Xfft = N.mpfft(x, prec=80)
    Xdft = N.mpdft(x, prec=80)
    for a, b in zip(Xfft, Xdft):
        assert abs(_to_complex(a) - _to_complex(b)) < 1e-25
    # Non-power-of-2 length raises.
    with pytest.raises(ValueError):
        N.mpfft([1.0, 2.0, 3.0], prec=53)
    with pytest.raises(ValueError):
        N.mpfft([], prec=53)


def test_mpdft_real_matches_mpdft():
    """mpdft_real on real input returns the same spectrum as mpdft."""
    x = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    X_real = N.mpdft_real(x, prec=80)
    X_full = N.mpdft(x, prec=80)
    for a, b in zip(X_real, X_full):
        assert abs(_to_complex(a) - _to_complex(b)) < 1e-15


def test_mpdft_real_rejects_imaginary_input():
    """mpdft_real raises on inputs with non-zero imaginary part."""
    with pytest.raises(ValueError):
        N.mpdft_real([1.0, 2.0, 3.0 + 1.0j, 4.0], prec=53)


def test_composition_2d_dft_separability():
    """2D DFT equals row-then-column DFT (separability).

    Composition: 2D DFT is the composition of two 1D DFTs along
    different axes. Cross-checks 2D against repeated 1D DFTs.
    """
    matrix = [[1.0, 2.0, 3.0, 4.0],
              [5.0, 6.0, 7.0, 8.0],
              [9.0, 0.0, 1.0, 2.0],
              [3.0, 4.0, 5.0, 6.0]]
    F2 = N.mpdft_2d(matrix, prec=80)
    # Row-then-column reference
    rows = [N.mpdft(r, prec=80) for r in matrix]
    cols = []
    for j in range(4):
        col = [rows[i][j] for i in range(4)]
        cols.append(N.mpdft(col, prec=80))
    # Reassemble
    expected = [[cols[j][i] for j in range(4)] for i in range(4)]
    for i in range(4):
        for j in range(4):
            assert abs(_to_complex(F2[i][j]) - _to_complex(expected[i][j])) < 1e-10
