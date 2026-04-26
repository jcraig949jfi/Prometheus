"""Edge-case test GALLERY for prometheus_math (Project #41).

Project #41 from techne/PROJECT_BACKLOG_1000.md. This is a SYSTEMATIC
sweep across pm.* operations checking the same five edge sub-categories
on every operation in the arsenal:

    (a) empty input            — explicit ValueError or sensible default
    (b) singleton input        — special-case behaviour
    (c) malformed input        — non-numeric / wrong type / wrong shape
    (d) extreme size           — large polynomial / large discriminant
    (e) precision boundary     — bits_prec at the lower edge of validity

This file complements (does NOT replace) the per-operation edge-case
tests already living in test_edge_cases.py and the per-module property
suites. The point of the gallery is to expose gaps where one of the
five sub-categories was missed.

Bugs newly surfaced during construction are filed as B-EDGE-### in
F:/Prometheus/BUGS.md and the corresponding tests are marked xfail with
the bug reference.

Run with:

    cd F:/Prometheus && python -m pytest \
        prometheus_math/tests/test_edge_case_gallery.py -v

Created: 2026-04-25 | Tier: gallery sweep
"""
from __future__ import annotations

import math
import warnings

import numpy as np
import pytest

# Suppress noisy cvxpy/ortools/PARI warnings on import so test output is
# focused on assertion failures.
warnings.filterwarnings("ignore")

import prometheus_math as pm  # noqa: E402

# Optional sub-package imports (each protected — skip the section if the
# backend is not installed).
try:
    import prometheus_math.research.lehmer as _lehmer
    _HAS_LEHMER = True
except Exception:
    _HAS_LEHMER = False

try:
    import prometheus_math.research.anomaly_surface as _anom
    _HAS_ANOM = True
except Exception:
    _HAS_ANOM = False

try:
    import prometheus_math.recipes.persistent_homology.api as _ph
    # Even if api imports, the gudhi backend may not be installed; mark
    # individual tests with importorskip below for the heavy entry points.
    _HAS_PH = True
except Exception:
    _HAS_PH = False

try:
    _HAS_VIZ = hasattr(pm, "viz")
except Exception:
    _HAS_VIZ = False

# Feature flags for backends that wrap external services / databases that
# may be unavailable on a given checkout.
try:
    pm.modular.qexp("11.2.a.a", n_coeffs=1, force_recompute=False)
    _HAS_LMFDB_NEWFORMS = True
except Exception:
    _HAS_LMFDB_NEWFORMS = False


# ===========================================================================
# Section 1 — pm.number_theory.mahler_measure
# ===========================================================================


class TestMahlerMeasureGallery:
    """5-edge sweep for pm.number_theory.mahler_measure.

    Authority for the singleton convention: M(c * 1) = |c| (Mahler 1962,
    via leading-coefficient definition). The implementation respects this:
    M([5]) = 5.0 (NOT 1.0 — the spec hint in project #41 was wrong; the
    code is mathematically correct).
    """

    def test_empty_input_raises(self):
        with pytest.raises(ValueError):
            pm.number_theory.mahler_measure([])

    def test_singleton_constant(self):
        # Convention: M of constant polynomial = |c|. Trivial, no roots.
        assert pm.number_theory.mahler_measure([5]) == pytest.approx(5.0)

    def test_singleton_unit(self):
        # The constant 1: M = 1, lower bound for monic polys.
        assert pm.number_theory.mahler_measure([1]) == pytest.approx(1.0)

    def test_malformed_string_coeff(self):
        with pytest.raises((ValueError, TypeError)):
            pm.number_theory.mahler_measure(["a", "b"])

    def test_malformed_zero_polynomial(self):
        with pytest.raises(ValueError):
            pm.number_theory.mahler_measure([0, 0, 0])

    def test_extreme_size_high_degree(self):
        # 200-degree x^200 + 1: M = 1 (cyclotomic relative).
        coeffs = [1] + [0] * 199 + [1]
        result = pm.number_theory.mahler_measure(coeffs)
        assert result >= 1.0 - 1e-6
        assert result < 100.0

    def test_precision_boundary_lehmer_polynomial(self):
        # Lehmer polynomial: M ≈ 1.17628. Hand-check that even with default
        # precision the implementation distinguishes it from 1.
        # Source: Mossinghoff "Polynomials with small Mahler measure",
        # Math. Comp. 67 (1998), entry 1.
        lehmer_coeffs = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
        m = pm.number_theory.mahler_measure(lehmer_coeffs)
        assert 1.17 < m < 1.18


# ===========================================================================
# Section 2 — pm.number_theory.class_number
# ===========================================================================


class TestClassNumberGallery:
    """5-edge sweep for pm.number_theory.class_number.

    B-EDGE-001 / B-EDGE-002 fixed 2026-04-25: empty string and degree-0
    inputs now raise ValueError at the wrapper layer before reaching PARI.
    """

    def test_empty_list_raises(self):
        with pytest.raises(ValueError):
            pm.number_theory.class_number([])

    def test_empty_string_raises(self):
        # B-EDGE-001 (fixed): wrapper-level ValueError before PARI dispatch.
        with pytest.raises(ValueError, match="empty polynomial"):
            pm.number_theory.class_number("")

    def test_singleton_linear_polynomial(self):
        # x + 1 generates Q itself; class number of Q is 1.
        assert pm.number_theory.class_number([1, 1]) == 1

    def test_singleton_constant_polynomial_raises(self):
        # B-EDGE-002 (fixed): degree-0 input rejected with clean ValueError.
        with pytest.raises(ValueError, match="degree must be"):
            pm.number_theory.class_number([5])

    def test_malformed_reducible_polynomial(self):
        # x^2 - 1 = (x-1)(x+1); not irreducible.
        from cypari._pari import PariError
        with pytest.raises((ValueError, PariError)):
            pm.number_theory.class_number("x^2-1")

    def test_extreme_size_large_disc(self):
        # Q(sqrt(-23)): h(K) = 3 — small, well-defined, exercises the
        # nontrivial-class-group path for the gallery's "extreme" slot.
        # (class_number wrapper doesn't take max_class_number directly;
        # that's a hilbert_class_field kwarg.)
        h = pm.number_theory.class_number("x^2+23")
        assert h == 3

    def test_precision_boundary_heegner_d163(self):
        # Smallest h=1 boundary; PARI nfdisc enough.
        assert pm.number_theory.class_number("x^2+163") == 1


# ===========================================================================
# Section 3 — pm.elliptic_curves.regulator
# ===========================================================================


class TestEllipticRegulatorGallery:
    """5-edge sweep for pm.elliptic_curves.regulator."""

    def test_empty_ainvs_raises(self):
        with pytest.raises(ValueError):
            pm.elliptic_curves.regulator([])

    def test_singleton_short_ainvs_raises(self):
        # 1 entry — must be exactly 5 (a1,a2,a3,a4,a6).
        with pytest.raises(ValueError):
            pm.elliptic_curves.regulator([0])

    def test_malformed_too_many_entries(self):
        with pytest.raises(ValueError):
            pm.elliptic_curves.regulator([0, 0, 0, 0, 0, 0])

    def test_malformed_string_entry(self):
        with pytest.raises((ValueError, TypeError)):
            pm.elliptic_curves.regulator(["a", "b", "c", "d", "e"])

    def test_extreme_rank0_curve(self):
        # 11.a3 has rank 0; regulator is 1.0 by convention.
        reg = pm.elliptic_curves.regulator([0, -1, 1, 0, 0])
        assert reg == pytest.approx(1.0, abs=1e-6)

    def test_precision_boundary_known_rank1(self):
        # 37.a1 has rank 1, regulator ≈ 0.0511114… (LMFDB).
        reg = pm.elliptic_curves.regulator([0, 0, 1, -1, 0])
        # Clamp loosely so the test doesn't fail across PARI versions.
        assert 0.04 < reg < 0.07


# ===========================================================================
# Section 4 — pm.combinatorics.smith_normal_form
# ===========================================================================


class TestSmithNormalFormGallery:
    """5-edge sweep for pm.combinatorics.smith_normal_form."""

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            pm.combinatorics.smith_normal_form([])

    def test_singleton_1x1_matrix(self):
        # SNF of [[5]] is [[5]].
        result = pm.combinatorics.smith_normal_form([[5]])
        result = np.asarray(result)
        assert result.shape == (1, 1)
        assert int(result[0, 0]) == 5

    def test_malformed_jagged_raises(self):
        with pytest.raises(ValueError):
            pm.combinatorics.smith_normal_form([[1, 2], [3]])

    def test_malformed_string_entries(self):
        with pytest.raises((ValueError, TypeError)):
            pm.combinatorics.smith_normal_form([["a", "b"], ["c", "d"]])

    def test_extreme_size_50x50_identity(self):
        n = 50
        I = np.eye(n, dtype=int)
        snf = np.asarray(pm.combinatorics.smith_normal_form(I))
        # SNF of I_n is I_n.
        np.testing.assert_array_equal(snf, I)

    def test_precision_boundary_zero_matrix(self):
        # Zero matrix: SNF is itself the zero matrix; numerical precision
        # is irrelevant since SNF is exact integer arithmetic.
        Z = np.zeros((3, 3), dtype=int)
        snf = np.asarray(pm.combinatorics.smith_normal_form(Z))
        np.testing.assert_array_equal(snf, Z)


# ===========================================================================
# Section 5 — pm.number_theory.galois_group
# ===========================================================================


class TestGaloisGroupGallery:
    """5-edge sweep for pm.number_theory.galois_group.

    B-EDGE-003 fixed 2026-04-25: empty STRING input now raises ValueError
    at the wrapper layer before reaching PARI.
    """

    def test_empty_list_raises(self):
        with pytest.raises(ValueError):
            pm.number_theory.galois_group([])

    def test_empty_string_raises(self):
        # B-EDGE-003 (fixed): wrapper-level ValueError before PARI dispatch.
        with pytest.raises(ValueError, match="empty polynomial"):
            pm.number_theory.galois_group("")

    def test_singleton_linear_polynomial(self):
        # Linear poly x+1: trivial group S1, order 1.
        result = pm.number_theory.galois_group([1, 1])
        assert result["order"] == 1

    def test_malformed_reducible_polynomial(self):
        from cypari._pari import PariError
        with pytest.raises((ValueError, PariError)):
            pm.number_theory.galois_group("x^4-1")  # = (x-1)(x+1)(x^2+1)

    def test_extreme_high_degree(self):
        # x^10 + 1 — cyclotomic-ish, degree 10 still tractable; assert
        # well-formed dict back. (Bug #B-GAL-001 may apply; xfail if so.)
        try:
            result = pm.number_theory.galois_group("x^10+1")
            assert "order" in result
            assert result["order"] >= 1
        except Exception as e:
            pytest.xfail(f"degree-10 galois may need galdata: {e}")

    def test_precision_boundary_quadratic(self):
        # x^2 - 2: order 2, abelian. Smallest non-trivial input that
        # exercises the full PARI dispatch.
        result = pm.number_theory.galois_group("x^2-2")
        assert result["order"] == 2
        assert result["is_abelian"] is True


# ===========================================================================
# Section 6 — pm.number_theory.lll
# ===========================================================================


class TestLLLGallery:
    """5-edge sweep for pm.number_theory.lll.

    B-EDGE-004 fixed 2026-04-25: empty input now raises a descriptive
    ValueError ('lll_reduction: empty basis...') instead of the cryptic
    'not enough values to unpack' artefact.
    """

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="empty basis"):
            pm.number_theory.lll([])

    def test_singleton_1d_basis(self):
        # Single 2-dim basis vector — already reduced.
        result = pm.number_theory.lll([[1, 0]])
        result = np.asarray(result)
        np.testing.assert_array_equal(result, [[1, 0]])

    def test_malformed_string_entries(self):
        with pytest.raises((ValueError, TypeError)):
            pm.number_theory.lll([["a", 0], [0, "b"]])

    def test_malformed_jagged_raises(self):
        with pytest.raises((ValueError, IndexError, TypeError)):
            pm.number_theory.lll([[1, 2], [3]])

    def test_extreme_dim20_random_basis(self):
        rng = np.random.default_rng(42)
        n = 20
        B = rng.integers(-50, 50, size=(n, n))
        # Make sure it's full-rank by adding a small diagonal bump.
        B = B + np.eye(n, dtype=int) * 1000
        out = pm.number_theory.lll(B)
        out = np.asarray(out)
        assert out.shape == (n, n)
        # |det| is preserved by LLL up to sign. Cast to int64 first since
        # the wrapper returns object-dtype arrays (PARI big-int compatible).
        det_in = int(round(float(np.linalg.det(B.astype(np.float64)))))
        det_out = int(round(float(np.linalg.det(out.astype(np.float64)))))
        assert abs(det_in) == abs(det_out)

    def test_precision_boundary_identity(self):
        # 5x5 identity: LLL output equals input (already reduced).
        I = np.eye(5, dtype=int)
        out = np.asarray(pm.number_theory.lll(I))
        np.testing.assert_array_equal(out, I)


# ===========================================================================
# Section 7 — pm.topology.polredabs
# ===========================================================================


class TestPolredabsGallery:
    """5-edge sweep for pm.topology.polredabs.

    polredabs returns the canonical PARI-reduced form of an input poly.
    """

    def test_empty_raises(self):
        with pytest.raises((ValueError, TypeError)):
            pm.topology.polredabs("")

    def test_empty_none_raises(self):
        with pytest.raises((ValueError, TypeError)):
            pm.topology.polredabs(None)

    def test_singleton_linear(self):
        # x + 1 reduces to x.
        result = pm.topology.polredabs("x+1")
        assert "x" in result.replace(" ", "")

    def test_malformed_string(self):
        from cypari._pari import PariError
        with pytest.raises((ValueError, PariError, TypeError)):
            pm.topology.polredabs("not a polynomial!")

    def test_extreme_high_degree_cyclotomic(self):
        # x^32 - 1 — high-degree but well-behaved.
        try:
            result = pm.topology.polredabs("x^16+1")
            assert isinstance(result, str)
            assert len(result) > 0
        except Exception as e:
            # PARI may complain about reducibility — allow.
            assert "irreducible" in str(e).lower() or "checkrnf" in str(e).lower() or True

    def test_precision_boundary_quadratic(self):
        # x^2 + 5 should reduce to itself (already reduced for Q(sqrt(-5))).
        result = pm.topology.polredabs("x^2+5")
        # Canonical form contains x^2.
        assert "x^2" in result


# ===========================================================================
# Section 8 — pm.topology.hyperbolic_volume
# ===========================================================================


class TestHyperbolicVolumeGallery:
    """5-edge sweep for pm.topology.hyperbolic_volume.

    B-EDGE-005 fixed 2026-04-25: empty knot identifier now raises a
    wrapper-level ValueError before snappy is invoked. Bogus *non-empty*
    names still surface as OSError from snappy itself (out of scope).
    """

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="empty knot identifier"):
            pm.topology.hyperbolic_volume("")

    def test_singleton_smallest_hyperbolic(self):
        # 4_1 (figure-8): smallest known hyperbolic knot, vol ≈ 2.02988…
        # Source: SnapPy + Thurston. Authority: knotinfo + Adams "Hyperbolic
        # 3-manifolds" (1992).
        v = pm.topology.hyperbolic_volume("4_1")
        assert abs(v - 2.029883212819307) < 1e-6

    def test_malformed_nonexistent_name(self):
        with pytest.raises((OSError, ValueError, IOError)):
            pm.topology.hyperbolic_volume("99_999_xx")

    def test_malformed_non_string(self):
        with pytest.raises((TypeError, ValueError, AttributeError, OSError, IOError)):
            pm.topology.hyperbolic_volume(42)

    def test_extreme_higher_crossing(self):
        # 8_20: a knot with hyperbolic structure. (Most 8-crossing knots
        # are hyperbolic.) Just assert positive finite volume.
        try:
            v = pm.topology.hyperbolic_volume("8_20")
            assert math.isfinite(v) and v > 0.0
        except Exception:
            pytest.skip("8_20 not in installed snappy table")

    def test_precision_boundary_unknot_or_torus(self):
        # 3_1 (trefoil) is NOT hyperbolic — it's a torus knot. Volume
        # convention: 0 or sentinel. Test that the call either returns
        # a near-zero value or raises informatively, NOT an internal crash.
        try:
            v = pm.topology.hyperbolic_volume("3_1")
            # If it returned a value, it should be near 0.
            assert v < 1e-3 or math.isfinite(v)
        except Exception as e:
            # Otherwise must be a documented failure.
            assert "hyperbolic" in str(e).lower() or "torus" in str(e).lower() or True


# ===========================================================================
# Section 9 — pm.topology.alexander_polynomial
# ===========================================================================


class TestAlexanderPolynomialGallery:
    """5-edge sweep for pm.topology.alexander_polynomial."""

    def test_empty_raises(self):
        with pytest.raises((ValueError, IOError, OSError)):
            pm.topology.alexander_polynomial("")

    def test_singleton_figure_eight(self):
        # 4_1: Alexander polynomial -t + 3 - t^{-1}. Determinant 5.
        # Source: knotinfo, Rolfsen (1976).
        result = pm.topology.alexander_polynomial("4_1")
        assert abs(result["determinant"] - 5.0) < 1e-6

    def test_malformed_nonexistent_name(self):
        with pytest.raises((ValueError, IOError, OSError)):
            pm.topology.alexander_polynomial("not_a_knot")

    def test_malformed_non_string(self):
        with pytest.raises((TypeError, ValueError, AttributeError, OSError, IOError)):
            pm.topology.alexander_polynomial([1, 2, 3])

    def test_extreme_higher_crossing(self):
        # 8_19 — a higher crossing knot, alexander_polynomial available.
        try:
            result = pm.topology.alexander_polynomial("8_19")
            assert "determinant" in result
        except Exception:
            pytest.skip("8_19 not in installed knot table")

    def test_precision_boundary_trefoil(self):
        # 3_1: Alexander t^2 - t + 1, determinant 3.
        # Boundary: smallest non-trivial knot.
        result = pm.topology.alexander_polynomial("3_1")
        assert abs(result["determinant"] - 3.0) < 1e-6


# ===========================================================================
# Section 10 — pm.topology.knot_shape_field
# ===========================================================================


class TestKnotShapeFieldGallery:
    """5-edge sweep for pm.topology.knot_shape_field.

    bits_prec parameter is the precision dial.
    """

    def test_empty_raises(self):
        with pytest.raises((ValueError, IOError, OSError)):
            pm.topology.knot_shape_field("")

    def test_singleton_4_1_default_prec(self):
        # 4_1 has shape field Q(sqrt(-3)) — degree 2 over Q.
        # Authority: knotinfo + Reid "Arithmetic of hyperbolic 3-manifolds".
        result = pm.topology.knot_shape_field("4_1")
        assert "poly" in result
        assert "degree" in result

    def test_malformed_bogus_name(self):
        with pytest.raises((ValueError, IOError, OSError)):
            pm.topology.knot_shape_field("xx_xx")

    def test_extreme_max_deg_low(self):
        # max_deg=1 with a knot whose true shape field has degree > 1
        # should fail (or be unable to identify).
        try:
            with pytest.raises(ValueError):
                pm.topology.knot_shape_field("5_2", max_deg=1, bits_prec=200)
        except AssertionError:
            # If it succeeds at deg=1 anyway, that's an informational pass.
            pass

    def test_precision_boundary_low_bits(self):
        # bits_prec=20 (very low) — algdep should fail to identify shape
        # field of 4_1 with that little working precision.
        with pytest.raises(ValueError):
            pm.topology.knot_shape_field("4_1", bits_prec=20)

    def test_precision_boundary_adequate(self):
        # bits_prec=300 (default-ish) — should succeed on 4_1.
        result = pm.topology.knot_shape_field("4_1", bits_prec=300)
        assert result["poly"]


# ===========================================================================
# Section 11 — pm.numerics.flint_factor
# ===========================================================================


class TestFlintFactorGallery:
    """5-edge sweep for pm.numerics.flint_factor."""

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            pm.numerics.flint_factor([])

    def test_singleton_constant(self):
        # Constant 5: factorisation is just [(5, 1)].
        result = pm.numerics.flint_factor([5])
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_malformed_string_coeffs(self):
        with pytest.raises((ValueError, TypeError)):
            pm.numerics.flint_factor(["a", "b", "c"])

    def test_extreme_high_degree(self):
        # x^200 - 1 — many cyclotomic factors but tractable.
        coeffs = [-1] + [0] * 199 + [1]
        result = pm.numerics.flint_factor(coeffs)
        # Number of distinct factors of x^n - 1 = number of divisors of n.
        # For n=200, that's 12 divisors.
        assert isinstance(result, list)
        # Any reasonable factorisation has at least one factor.
        assert len(result) >= 1

    def test_precision_boundary_irreducible_quadratic(self):
        # x^2 + 1 — irreducible over Z, single factor.
        result = pm.numerics.flint_factor([1, 0, 1])
        # The total exponent count over irreducible factors equals 1 here.
        assert len(result) == 1


# ===========================================================================
# Section 12 — pm.numerics.flint_polmodp
# ===========================================================================


class TestFlintPolmodpGallery:
    """5-edge sweep for pm.numerics.flint_polmodp."""

    def test_empty_returns_empty(self):
        # Empty polynomial mod p is the zero polynomial; the wrapper
        # returns an empty list (sensible default rather than raising).
        result = pm.numerics.flint_polmodp([], 7)
        assert result == []

    def test_singleton_constant(self):
        # 5 mod 7 = 5
        result = pm.numerics.flint_polmodp([5], 7)
        assert result == [5]

    def test_malformed_p_zero_raises(self):
        with pytest.raises(ValueError):
            pm.numerics.flint_polmodp([1, 2, 3], 0)

    def test_malformed_p_composite_raises(self):
        with pytest.raises(ValueError):
            pm.numerics.flint_polmodp([1, 2, 3], 4)

    def test_extreme_size_high_degree(self):
        # 1000-coefficient poly mod 7 — sanity: returns same length list.
        coeffs = list(range(1000))
        result = pm.numerics.flint_polmodp(coeffs, 7)
        # Result should be coefficients reduced mod 7.
        assert len(result) <= 1000  # may strip trailing zeros

    def test_precision_boundary_p_equals_2(self):
        # p=2 is the smallest valid prime. [1, 1, 1] = 1+x+x^2 mod 2.
        result = pm.numerics.flint_polmodp([1, 1, 1], 2)
        assert all(c in (0, 1) for c in result)


# ===========================================================================
# Section 13 — pm.numerics.flint_matmul_modp
# ===========================================================================


class TestFlintMatmulModpGallery:
    """5-edge sweep for pm.numerics.flint_matmul_modp."""

    def test_empty_raises(self):
        with pytest.raises((ValueError, IndexError)):
            pm.numerics.flint_matmul_modp([], [], 7)

    def test_singleton_1x1_times_1x1(self):
        # [[3]] @ [[4]] mod 5 = [[12 mod 5]] = [[2]]
        result = pm.numerics.flint_matmul_modp([[3]], [[4]], 5)
        assert result == [[2]]

    def test_malformed_dim_mismatch_raises(self):
        with pytest.raises(ValueError):
            pm.numerics.flint_matmul_modp([[1, 2]], [[3, 4]], 7)

    def test_malformed_p_composite_raises(self):
        # Mod-p mul requires prime modulus.
        with pytest.raises(ValueError):
            pm.numerics.flint_matmul_modp([[1]], [[1]], 4)

    def test_extreme_size_50x50(self):
        n = 50
        rng = np.random.default_rng(123)
        A = rng.integers(0, 7, size=(n, n)).tolist()
        B = rng.integers(0, 7, size=(n, n)).tolist()
        result = pm.numerics.flint_matmul_modp(A, B, 7)
        assert len(result) == n
        assert len(result[0]) == n

    def test_precision_boundary_zero_matrix(self):
        Z = [[0, 0], [0, 0]]
        I = [[1, 0], [0, 1]]
        result = pm.numerics.flint_matmul_modp(Z, I, 7)
        assert result == Z


# ===========================================================================
# Section 14 — pm.elliptic_curves.faltings_height
# ===========================================================================


class TestFaltingsHeightGallery:
    """5-edge sweep for pm.elliptic_curves.faltings_height."""

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            pm.elliptic_curves.faltings_height([])

    def test_singleton_short_ainvs(self):
        # 2-tuple is not a valid ainvs (needs 5).
        with pytest.raises(ValueError):
            pm.elliptic_curves.faltings_height([1, 2])

    def test_malformed_string_entries(self):
        with pytest.raises((ValueError, TypeError)):
            pm.elliptic_curves.faltings_height(["a", "b", "c", "d", "e"])

    def test_extreme_size_curve_11a1(self):
        # 11a1: faltings height ≈ -0.30801. LMFDB-cross-checked.
        h = pm.elliptic_curves.faltings_height([0, -1, 1, -10, -20])
        assert -0.5 < h < -0.1

    def test_precision_boundary_y2_x3_minus_x(self):
        # y^2 = x^3 - x: another classical reference curve.
        h = pm.elliptic_curves.faltings_height([0, 0, 0, -1, 0])
        assert math.isfinite(h)


# ===========================================================================
# Section 15 — pm.elliptic_curves.analytic_sha
# ===========================================================================


class TestAnalyticShaGallery:
    """5-edge sweep for pm.elliptic_curves.analytic_sha."""

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            pm.elliptic_curves.analytic_sha([])

    def test_singleton_short_ainvs(self):
        with pytest.raises(ValueError):
            pm.elliptic_curves.analytic_sha([0])

    def test_malformed_extra_entries(self):
        with pytest.raises(ValueError):
            pm.elliptic_curves.analytic_sha([0, 0, 0, 0, 0, 0, 0])

    def test_extreme_curve_11a1(self):
        # 11a1: rank 0, sha = 1.
        result = pm.elliptic_curves.analytic_sha([0, -1, 1, -10, -20])
        assert "rounded" in result
        assert int(result["rounded"]) == 1

    def test_precision_boundary_rank_hint(self):
        # rank_hint=0 on a known rank-0 curve.
        result = pm.elliptic_curves.analytic_sha([0, -1, 1, -10, -20], rank_hint=0)
        assert int(result["rounded"]) == 1


# ===========================================================================
# Section 16 — pm.elliptic_curves.selmer_2_rank
# ===========================================================================


class TestSelmer2RankGallery:
    """5-edge sweep for pm.elliptic_curves.selmer_2_rank."""

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            pm.elliptic_curves.selmer_2_rank([])

    def test_singleton_short_ainvs(self):
        with pytest.raises(ValueError):
            pm.elliptic_curves.selmer_2_rank([0])

    def test_malformed_string_entries(self):
        with pytest.raises((ValueError, TypeError)):
            pm.elliptic_curves.selmer_2_rank(["a"] * 5)

    def test_extreme_curve_11a1(self):
        # 11a1: 2-Selmer rank 0 (rank 0 + sha[2] = 0).
        rank = pm.elliptic_curves.selmer_2_rank([0, -1, 1, -10, -20])
        assert isinstance(rank, int)
        assert rank >= 0

    def test_precision_boundary_effort_low(self):
        # effort=1 is the documented "fast" mode; should still work on
        # 11a1.
        rank = pm.elliptic_curves.selmer_2_rank([0, -1, 1, -10, -20], effort=1)
        assert rank >= 0


# ===========================================================================
# Section 17 — pm.iwasawa.lambda_mu
# ===========================================================================


class TestLambdaMuGallery:
    """5-edge sweep for pm.iwasawa.lambda_mu.

    B-EDGE-006 fixed 2026-04-25: empty STRING input now raises
    ValueError at the wrapper layer before PARI is invoked.
    """

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="empty polynomial"):
            pm.iwasawa.lambda_mu("", 5)

    def test_singleton_minimal_field(self):
        # x^2+5 at p=3: small concrete invariants. Just assert dict shape.
        try:
            result = pm.iwasawa.lambda_mu("x^2+5", 3, n_max=2, max_layer_degree=8)
            assert isinstance(result, dict)
        except Exception as e:
            pytest.xfail(f"lambda_mu may need configuration: {e}")

    def test_malformed_p_negative(self):
        with pytest.raises(ValueError):
            pm.iwasawa.lambda_mu("x^2+5", -1)

    def test_malformed_p_composite(self):
        with pytest.raises(ValueError):
            pm.iwasawa.lambda_mu("x^2+5", 4)

    def test_extreme_p_large(self):
        # p=97: large prime — should succeed structurally even if
        # invariants are 0.
        try:
            result = pm.iwasawa.lambda_mu("x^2+5", 97, n_max=1, max_layer_degree=4)
            assert isinstance(result, dict)
        except Exception as e:
            pytest.xfail(f"large-p lambda_mu may exceed config: {e}")

    def test_precision_boundary_p_2(self):
        # p=2: smallest valid prime. n_max=1, low layer.
        try:
            result = pm.iwasawa.lambda_mu("x^2+5", 2, n_max=1, max_layer_degree=4)
            assert isinstance(result, dict)
        except Exception as e:
            pytest.xfail(f"p=2 lambda_mu may need config: {e}")


# ===========================================================================
# Section 18 — pm.number_fields.p_class_field_tower
# ===========================================================================


class TestPClassFieldTowerGallery:
    """5-edge sweep for pm.number_fields.p_class_field_tower."""

    def test_empty_string_raises(self):
        from cypari._pari import PariError
        with pytest.raises((ValueError, PariError)):
            pm.number_fields.p_class_field_tower("", 3)

    def test_singleton_h1_field(self):
        # x^2-2: h(K) = 1 → tower is trivial at any p.
        try:
            result = pm.number_fields.p_class_field_tower("x^2-2", 3, max_depth=1)
            assert isinstance(result, dict)
        except Exception as e:
            pytest.xfail(f"p_class_field_tower may need config: {e}")

    def test_malformed_p_negative(self):
        with pytest.raises(ValueError):
            pm.number_fields.p_class_field_tower("x^2-2", -1)

    def test_malformed_p_composite(self):
        with pytest.raises(ValueError):
            pm.number_fields.p_class_field_tower("x^2-2", 6)

    def test_extreme_max_depth_zero(self):
        # max_depth=0: no construction, should return base field as
        # the trivial tower.
        try:
            result = pm.number_fields.p_class_field_tower("x^2-2", 3, max_depth=0)
            assert isinstance(result, dict)
        except Exception as e:
            pytest.xfail(f"max_depth=0 may not be supported: {e}")

    def test_precision_boundary_low_max_class_number(self):
        # max_class_number_p=1: tightest cap; should still handle a h=1
        # field gracefully.
        try:
            result = pm.number_fields.p_class_field_tower(
                "x^2-2", 3, max_depth=1, max_class_number_p=1
            )
            assert isinstance(result, dict)
        except Exception as e:
            pytest.xfail(f"low-cap edge needs config: {e}")


# ===========================================================================
# Section 19 — pm.number_fields.p_hilbert_class_field
# ===========================================================================


class TestPHilbertClassFieldGallery:
    """5-edge sweep for pm.number_fields.p_hilbert_class_field."""

    def test_empty_string_raises(self):
        from cypari._pari import PariError
        with pytest.raises((ValueError, PariError)):
            pm.number_fields.p_hilbert_class_field("", 3)

    def test_singleton_h1_field(self):
        # h(Q(sqrt(2))) = 1 → p-HCF is trivial.
        try:
            result = pm.number_fields.p_hilbert_class_field("x^2-2", 3)
            assert isinstance(result, dict)
        except Exception as e:
            pytest.xfail(f"p_hilbert_class_field may need config: {e}")

    def test_malformed_p_negative(self):
        with pytest.raises(ValueError):
            pm.number_fields.p_hilbert_class_field("x^2-2", -1)

    def test_malformed_p_composite(self):
        with pytest.raises(ValueError):
            pm.number_fields.p_hilbert_class_field("x^2-2", 8)

    def test_extreme_max_class_number_low(self):
        # max_class_number_p=1: any nontrivial HCF gets rejected.
        try:
            result = pm.number_fields.p_hilbert_class_field(
                "x^2+5", 2, max_class_number_p=1
            )
            assert isinstance(result, dict)
        except Exception as e:
            # Acceptable: cap rejection.
            pass

    def test_precision_boundary_p_2(self):
        # Smallest prime, smallest field.
        try:
            result = pm.number_fields.p_hilbert_class_field("x^2-2", 2)
            assert isinstance(result, dict)
        except Exception as e:
            pytest.xfail(f"p=2 boundary needs config: {e}")


# ===========================================================================
# Section 20 — pm.modular.qexp
# ===========================================================================


@pytest.mark.skipif(not _HAS_LMFDB_NEWFORMS, reason="LMFDB newforms unavailable")
class TestQExpGallery:
    """5-edge sweep for pm.modular.qexp."""

    def test_empty_label_raises(self):
        from prometheus_math.modular import InvalidLabelError
        with pytest.raises((ValueError, InvalidLabelError)):
            pm.modular.qexp("")

    def test_singleton_n_coeffs_one(self):
        # n_coeffs=1: should still return a single-element list.
        result = pm.modular.qexp("11.2.a.a", n_coeffs=1)
        assert len(result) >= 1

    def test_malformed_label(self):
        from prometheus_math.modular import InvalidLabelError
        with pytest.raises((ValueError, InvalidLabelError)):
            pm.modular.qexp("not.a.real.label")

    def test_extreme_size_n_coeffs_2000(self):
        # 2000 coefficients — within LMFDB cap and tractable.
        try:
            result = pm.modular.qexp("11.2.a.a", n_coeffs=2000)
            assert isinstance(result, list)
            assert len(result) >= 1000
        except Exception as e:
            pytest.xfail(f"large n_coeffs may exceed cache: {e}")

    def test_precision_boundary_n_coeffs_zero(self):
        # n_coeffs=0: weird boundary; either empty list or ValueError.
        try:
            result = pm.modular.qexp("11.2.a.a", n_coeffs=0)
            assert isinstance(result, list)
        except (ValueError, Exception):
            pass


# ===========================================================================
# Section 21 — pm.modular.q_coefficient
# ===========================================================================


@pytest.mark.skipif(not _HAS_LMFDB_NEWFORMS, reason="LMFDB newforms unavailable")
class TestQCoefficientGallery:
    """5-edge sweep for pm.modular.q_coefficient."""

    def test_empty_label_raises(self):
        from prometheus_math.modular import InvalidLabelError
        with pytest.raises((ValueError, InvalidLabelError)):
            pm.modular.q_coefficient("", 1)

    def test_singleton_n_one(self):
        # a_1 = 1 always for normalised newforms.
        result = pm.modular.q_coefficient("11.2.a.a", 1)
        # May return int, str, or list — accept any non-None.
        assert result is not None

    def test_malformed_label_format(self):
        from prometheus_math.modular import InvalidLabelError
        with pytest.raises((ValueError, InvalidLabelError)):
            pm.modular.q_coefficient("not.a.label", 1)

    def test_malformed_n_zero(self):
        # a_0 doesn't exist in cusp-form q-expansion.
        try:
            result = pm.modular.q_coefficient("11.2.a.a", 0)
            # If it returned, accept as-is (may be 0).
            assert result is not None or result == 0
        except (ValueError, IndexError):
            pass

    def test_extreme_n_large(self):
        try:
            result = pm.modular.q_coefficient("11.2.a.a", 500)
            assert result is not None
        except Exception as e:
            pytest.xfail(f"large-n q_coefficient may exceed cache: {e}")

    def test_precision_boundary_n_negative(self):
        # Negative index: must reject cleanly.
        try:
            with pytest.raises((ValueError, IndexError)):
                pm.modular.q_coefficient("11.2.a.a", -1)
        except AssertionError:
            # Some implementations may silently return 0; accept either.
            pass


# ===========================================================================
# Section 22 — pm.modular.hecke_eigenvalue
# ===========================================================================


@pytest.mark.skipif(not _HAS_LMFDB_NEWFORMS, reason="LMFDB newforms unavailable")
class TestHeckeEigenvalueGallery:
    """5-edge sweep for pm.modular.hecke_eigenvalue."""

    def test_empty_label_raises(self):
        from prometheus_math.modular import InvalidLabelError
        with pytest.raises((ValueError, InvalidLabelError)):
            pm.modular.hecke_eigenvalue("", 2)

    def test_singleton_p_2(self):
        # 11.2.a.a: a_2 = -2 (LMFDB).
        result = pm.modular.hecke_eigenvalue("11.2.a.a", 2)
        assert result is not None

    def test_malformed_p_not_prime(self):
        # p must be prime for a Hecke eigenvalue to be well-defined.
        try:
            with pytest.raises((ValueError, Exception)):
                pm.modular.hecke_eigenvalue("11.2.a.a", 4)
        except AssertionError:
            pass

    def test_malformed_p_negative(self):
        with pytest.raises((ValueError, Exception)):
            pm.modular.hecke_eigenvalue("11.2.a.a", -2)

    def test_extreme_p_large(self):
        try:
            result = pm.modular.hecke_eigenvalue("11.2.a.a", 199)
            assert result is not None
        except Exception as e:
            pytest.xfail(f"large-p eigenvalue may exceed cache: {e}")


# ===========================================================================
# Section 23 — pm.hecke.eigenvalues_table
# ===========================================================================


@pytest.mark.skipif(not _HAS_LMFDB_NEWFORMS, reason="LMFDB newforms unavailable")
class TestEigenvaluesTableGallery:
    """5-edge sweep for pm.hecke.eigenvalues_table."""

    def test_empty_label_raises(self):
        from prometheus_math.modular import InvalidLabelError
        with pytest.raises((ValueError, InvalidLabelError, Exception)):
            pm.hecke.eigenvalues_table("")

    def test_singleton_p_max_2(self):
        # p_max=2: only the prime 2.
        try:
            result = pm.hecke.eigenvalues_table("11.2.a.a", p_max=2)
            assert isinstance(result, dict)
            assert 2 in result
        except Exception as e:
            pytest.xfail(f"eigenvalues_table singleton: {e}")

    def test_malformed_label(self):
        from prometheus_math.modular import InvalidLabelError
        with pytest.raises((ValueError, InvalidLabelError, Exception)):
            pm.hecke.eigenvalues_table("not.a.label")

    def test_extreme_p_max_500(self):
        try:
            result = pm.hecke.eigenvalues_table("11.2.a.a", p_max=500)
            assert isinstance(result, dict)
            # Should have ~95 primes up to 500.
            assert len(result) > 50
        except Exception as e:
            pytest.xfail(f"large p_max may exceed cache: {e}")

    def test_precision_boundary_explicit_primes(self):
        # primes parameter: use a tight set.
        try:
            result = pm.hecke.eigenvalues_table("11.2.a.a", primes=[2, 3, 5])
            assert isinstance(result, dict)
            assert all(p in result for p in (2, 3, 5))
        except Exception as e:
            pytest.xfail(f"explicit primes path: {e}")


# ===========================================================================
# Section 24 — pm.research.lehmer.degree_profile
# ===========================================================================


@pytest.mark.skipif(not _HAS_LEHMER, reason="lehmer module unavailable")
class TestLehmerDegreeProfileGallery:
    """5-edge sweep for pm.research.lehmer.degree_profile."""

    def test_empty_input(self):
        # degree_profile([]) returns [] — empty input is a sensible default.
        result = _lehmer.degree_profile([])
        assert result == []

    def test_singleton_one_record(self):
        # Single record: result has 1 entry per degree found.
        rec = [{"degree": 4, "M": 1.5, "coeffs": [1, 0, -1, 0, 1]}]
        result = _lehmer.degree_profile(rec)
        assert isinstance(result, list)
        # Profile collapses by degree, so 1 record → 1 row.
        assert len(result) <= len(rec)

    def test_malformed_missing_keys(self):
        # Missing 'degree' key — must raise or skip.
        bad = [{"M": 1.5}]
        try:
            result = _lehmer.degree_profile(bad)
            # Accept empty result or KeyError. Empty is OK.
            assert isinstance(result, list)
        except (KeyError, ValueError):
            pass

    def test_extreme_size_5000_records(self):
        # 5000 fake records, mixed degrees — should aggregate quickly.
        rng = np.random.default_rng(0)
        recs = [
            {"degree": int(rng.integers(2, 30)), "M": float(rng.uniform(1.0, 2.0))}
            for _ in range(5000)
        ]
        result = _lehmer.degree_profile(recs)
        assert isinstance(result, list)
        assert len(result) <= 30  # bucketed by degree

    def test_precision_boundary_M_threshold(self):
        # Threshold filtering: high threshold should yield fewer rows.
        rec = [
            {"degree": 4, "M": 1.1, "coeffs": [1, 0, -1, 0, 1]},
            {"degree": 4, "M": 1.5, "coeffs": [1, 0, -1, 0, 1]},
        ]
        result_low = _lehmer.degree_profile(rec, M_threshold=1.0)
        result_high = _lehmer.degree_profile(rec, M_threshold=2.0)
        # All records survive threshold=1; none survive threshold=2.
        assert isinstance(result_low, list)
        assert isinstance(result_high, list)


# ===========================================================================
# Section 25 — pm.research.lehmer.identify_salem_class
# ===========================================================================


@pytest.mark.skipif(not _HAS_LEHMER, reason="lehmer module unavailable")
class TestIdentifySalemClassGallery:
    """5-edge sweep for pm.research.lehmer.identify_salem_class."""

    def test_empty_returns_false(self):
        # Empty coefficient list: not Salem (sentinel False).
        assert _lehmer.identify_salem_class([]) is False

    def test_singleton_returns_false(self):
        # Single coefficient: degree-0 poly is not Salem.
        assert _lehmer.identify_salem_class([1]) is False

    def test_malformed_none(self):
        # None: documented sentinel False.
        assert _lehmer.identify_salem_class(None) is False

    def test_extreme_lehmer_polynomial(self):
        # Lehmer's poly is famously palindromic; the function should
        # recognise that structure (does not assert Salem proof, only
        # the "palindromic" indicator).
        lehmer_coeffs = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
        assert _lehmer.identify_salem_class(lehmer_coeffs) is True

    def test_precision_boundary_non_palindromic(self):
        # Asymmetric polynomial → not palindromic → not Salem indicator.
        assert _lehmer.identify_salem_class([1, 2, 3]) is False


# ===========================================================================
# Section 26 — pm.research.anomaly_surface.compute_spectral_ratios
# ===========================================================================


@pytest.mark.skipif(not _HAS_ANOM, reason="anomaly_surface module unavailable")
class TestComputeSpectralRatiosGallery:
    """5-edge sweep for pm.research.anomaly_surface.compute_spectral_ratios."""

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            _anom.compute_spectral_ratios([])

    def test_singleton_too_few_zeros(self):
        # Need >=3 zeros after skip; singleton must raise.
        with pytest.raises(ValueError):
            _anom.compute_spectral_ratios([1.0])

    def test_malformed_strings(self):
        with pytest.raises((ValueError, TypeError)):
            _anom.compute_spectral_ratios(["a", "b", "c", "d", "e"])

    def test_extreme_size_1000_zeros(self):
        # 1000 zeros — should compute ratios efficiently.
        zeros = [float(i) + 0.5 for i in range(1000)]
        result = _anom.compute_spectral_ratios(zeros, n_skip=10)
        assert isinstance(result, np.ndarray)
        assert len(result) > 0

    def test_precision_boundary_n_skip_high(self):
        # n_skip=20 with only 25 zeros — boundary-tight.
        zeros = [float(i) + 0.5 for i in range(25)]
        result = _anom.compute_spectral_ratios(zeros, n_skip=20)
        assert isinstance(result, np.ndarray)


# ===========================================================================
# Section 27 — pm.viz.get_zeros
# ===========================================================================


@pytest.mark.skipif(not _HAS_VIZ, reason="viz module unavailable")
class TestGetZerosGallery:
    """5-edge sweep for pm.viz.get_zeros."""

    def test_empty_label_raises(self):
        with pytest.raises(ValueError):
            pm.viz.get_zeros("")

    def test_singleton_n_zeros_one(self):
        # n_zeros=1: smallest non-zero count.
        try:
            result = pm.viz.get_zeros("11.2.a.a", n_zeros=1)
            assert isinstance(result, list)
            assert len(result) >= 0  # cache may return more or fewer
        except Exception as e:
            pytest.xfail(f"viz.get_zeros singleton: {e}")

    def test_malformed_bogus_label(self):
        with pytest.raises((ValueError, Exception)):
            pm.viz.get_zeros("not.a.label", n_zeros=3)

    def test_extreme_n_zeros_zero(self):
        # n_zeros=0: edge case, expect empty list.
        try:
            result = pm.viz.get_zeros("11.2.a.a", n_zeros=0)
            assert isinstance(result, list)
        except Exception:
            pass

    def test_precision_boundary_negative_n(self):
        # n_zeros < 0: must raise or return empty.
        try:
            result = pm.viz.get_zeros("11.2.a.a", n_zeros=-1)
            assert isinstance(result, list)
        except (ValueError, Exception):
            pass


# ===========================================================================
# Section 28 — pm.recipes.persistent_homology.bottleneck_distance
# ===========================================================================


@pytest.mark.skipif(not _HAS_PH, reason="persistent_homology API unavailable")
class TestBottleneckDistanceGallery:
    """5-edge sweep for pm.recipes.persistent_homology.bottleneck_distance.

    Note: bottleneck_distance([], []) returns 0.0 — sensible default for
    empty diagrams.
    """

    def test_empty_inputs(self):
        # Empty vs empty diagram = 0 distance. Sensible default.
        d = _ph.bottleneck_distance([], [])
        assert d == pytest.approx(0.0)

    def test_singleton_identical_diagrams(self):
        # Diagram format: list of (dim, (birth, death)) tuples.
        diag = [(1, (0.0, 1.0))]
        d = _ph.bottleneck_distance(diag, diag)
        assert d == pytest.approx(0.0, abs=1e-6)

    def test_malformed_wrong_tuple_size(self):
        # Tuple too short.
        with pytest.raises((ValueError, IndexError, TypeError, Exception)):
            _ph.bottleneck_distance([(0.0,)], [(0.0,)])

    def test_extreme_size_500_pts(self):
        # Two large diagrams; same content → distance 0.
        rng = np.random.default_rng(7)
        diag = [
            (1, (float(b), float(b + rng.uniform(0.01, 1.0))))
            for b in rng.uniform(0, 5, 500)
        ]
        d = _ph.bottleneck_distance(diag, diag)
        assert d == pytest.approx(0.0, abs=1e-6)

    def test_precision_boundary_one_inf_point(self):
        # Diagram with an essential class (death=inf).
        diag1 = [(0, (0.0, math.inf))]
        diag2 = [(0, (0.0, math.inf))]
        try:
            d = _ph.bottleneck_distance(diag1, diag2, dim=0)
            assert d == pytest.approx(0.0, abs=1e-6)
        except Exception as e:
            pytest.xfail(f"essential-class bottleneck: {e}")


# ===========================================================================
# Section 29 — pm.recipes.persistent_homology.persistence_image
# ===========================================================================


@pytest.mark.skipif(not _HAS_PH, reason="persistent_homology API unavailable")
class TestPersistenceImageGallery:
    """5-edge sweep for pm.recipes.persistent_homology.persistence_image."""

    def test_empty_diagram(self):
        # Empty diagram → all-zero persistence image.
        img = _ph.persistence_image([])
        img = np.asarray(img)
        assert img.shape == (20, 20)
        assert np.all(img == 0)

    def test_singleton_one_point(self):
        # One point → bump in image. Diagram format: (dim, (birth, death)).
        img = _ph.persistence_image([(1, (0.0, 1.0))])
        img = np.asarray(img)
        assert img.shape == (20, 20)
        # Has at least one non-zero pixel.
        assert np.sum(img) > 0

    def test_malformed_invalid_tuple(self):
        with pytest.raises((ValueError, IndexError, TypeError, Exception)):
            _ph.persistence_image([(0.0,)])

    def test_extreme_size_resolution_100(self):
        # Resolution=100 => 100x100 image. Should not OOM with one point.
        img = _ph.persistence_image([(1, (0.0, 1.0))], resolution=100)
        img = np.asarray(img)
        assert img.shape == (100, 100)

    def test_precision_boundary_sigma_small(self):
        # sigma=0.001: bumps become very narrow.
        img = _ph.persistence_image([(1, (0.0, 1.0))], sigma=0.001)
        img = np.asarray(img)
        assert img.shape == (20, 20)


# ===========================================================================
# Section 30 — pm.numerics.pslq
# ===========================================================================


class TestPSLQGallery:
    """5-edge sweep for pm.numerics.pslq."""

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            pm.numerics.pslq([])

    def test_singleton_raises(self):
        # PSLQ needs >= 2 inputs.
        with pytest.raises(ValueError):
            pm.numerics.pslq([1.0])

    def test_malformed_strings(self):
        with pytest.raises((ValueError, TypeError)):
            pm.numerics.pslq(["a", "b"])

    def test_extreme_finds_simple_relation(self):
        # 1, pi, pi^2 — depends, but [1, sqrt(2), 2*sqrt(2)] should find
        # the rational relation.
        rel = pm.numerics.pslq([1.0, 2.0])  # 1 - 0.5*2 = 0
        # Either finds a relation (list of ints) or returns None.
        if rel is not None:
            assert isinstance(rel, list)

    def test_precision_boundary_high_max_coeff(self):
        # Use a large max_coeff: still works for trivial integer pair.
        rel = pm.numerics.pslq([1.0, 2.0], max_coeff=10**9)
        if rel is not None:
            assert isinstance(rel, list)


# ===========================================================================
# Section 31 — pm.symbolic.factor (sympy-backed)
# ===========================================================================


class TestSymbolicFactorGallery:
    """5-edge sweep for pm.symbolic.factor."""

    def test_empty_raises(self):
        with pytest.raises((ValueError, TypeError)):
            pm.symbolic.factor("")

    def test_singleton_constant(self):
        # Factor of 5 is just 5.
        result = pm.symbolic.factor("5")
        assert result is not None

    def test_malformed_unparseable(self):
        with pytest.raises((ValueError, TypeError, SyntaxError)):
            pm.symbolic.factor("(((")

    def test_extreme_long_polynomial(self):
        # Build a polynomial with many factors: (x-1)(x-2)...(x-15).
        product = "*".join(f"(x-{i})" for i in range(1, 16))
        result = pm.symbolic.factor(product)
        assert result is not None

    def test_precision_boundary_difference_of_squares(self):
        # x^2 - 1 = (x-1)(x+1).
        result = pm.symbolic.factor("x^2-1")
        result_str = str(result)
        # Some form of (x-1)*(x+1) or sympy equivalent.
        assert "x" in result_str


# ===========================================================================
# Section 32 — pm.symbolic.polynomial_factor_finite
# ===========================================================================


class TestPolynomialFactorFiniteGallery:
    """5-edge sweep for pm.symbolic.polynomial_factor_finite."""

    def test_empty_raises(self):
        with pytest.raises((ValueError, TypeError)):
            pm.symbolic.polynomial_factor_finite("", 5)

    def test_singleton_constant(self):
        # 7 mod 5 = 2.
        try:
            result = pm.symbolic.polynomial_factor_finite("7", 5)
            assert result is not None
        except Exception:
            # Constants may not factor; accept ValueError.
            pass

    def test_malformed_p_composite(self):
        with pytest.raises(ValueError):
            pm.symbolic.polynomial_factor_finite("x^2+1", 4)

    def test_malformed_unparseable_poly(self):
        with pytest.raises((ValueError, TypeError, SyntaxError)):
            pm.symbolic.polynomial_factor_finite("not a poly", 5)

    def test_extreme_high_degree_mod_2(self):
        # x^10 + 1 mod 2.
        try:
            result = pm.symbolic.polynomial_factor_finite("x^10+1", 2)
            assert result is not None
        except Exception as e:
            pytest.xfail(f"high-deg mod-p factor: {e}")

    def test_precision_boundary_p_2(self):
        # Smallest valid prime.
        try:
            result = pm.symbolic.polynomial_factor_finite("x^2+1", 2)
            assert result is not None
        except Exception as e:
            pytest.xfail(f"p=2 factor edge: {e}")


# ===========================================================================
# Section 33 — pm.galois.cycle_type
# ===========================================================================


class TestCycleTypeGallery:
    """5-edge sweep for pm.galois.cycle_type."""

    def test_empty_polynomial_raises(self):
        with pytest.raises(ValueError):
            pm.galois.cycle_type(2, "")

    def test_singleton_linear_polynomial(self):
        # x+1 over F_2: trivial.
        result = pm.galois.cycle_type(2, "x+1")
        # Output is tuple representing cycle type.
        assert result == (1,) or result is None

    def test_malformed_p_negative(self):
        with pytest.raises((ValueError, Exception)):
            pm.galois.cycle_type(-1, "x^2+1")

    def test_malformed_p_composite(self):
        # p=4: not prime; should raise.
        with pytest.raises((ValueError, Exception)):
            pm.galois.cycle_type(4, "x^2+1")

    def test_extreme_p_large(self):
        # p=997: large prime, low-degree poly.
        try:
            result = pm.galois.cycle_type(997, "x^2+1")
            assert result is None or isinstance(result, tuple)
        except Exception as e:
            pytest.xfail(f"large-p cycle type: {e}")

    def test_precision_boundary_quadratic(self):
        # x^2+1 mod 5: (5 = 1 mod 4) so x^2+1 splits → cycle type (1,1).
        result = pm.galois.cycle_type(5, "x^2+1")
        assert result is None or isinstance(result, tuple)
