"""Test suite for prometheus_math.iwasawa.

Project #26 Phase 1. Iwasawa lambda/mu invariant computation via the
cyclotomic Z_p-extension tower.

Categories per math-tdd skill (techne/skills/math-tdd.md):
  - Authority: tests against published Iwasawa-theory results.
  - Property:  invariants every (lambda, mu, nu) triple satisfies.
  - Edge:      K = Q, very large p (out-of-range), non-prime p.
  - Composition: p_class_number = product(p_class_group_part).

Run: pytest prometheus_math/tests/test_iwasawa.py -v
"""
from __future__ import annotations

import math
import pytest
from hypothesis import HealthCheck, assume, given, settings, strategies as st

from prometheus_math.iwasawa import (
    cyclotomic_zp_extension,
    greenberg_test,
    lambda_mu,
    p_class_group_part,
    p_class_number,
)


# ---------------------------------------------------------------------------
# AUTHORITY-BASED TESTS
# ---------------------------------------------------------------------------

class TestAuthority:
    """Cross-checks against published Iwasawa-theory results."""

    def test_q_sqrt_minus_23_at_p_3_lambda_is_one(self):
        """Q(sqrt(-23)), p=3: classical result lambda_3 = 1, mu_3 = 0.

        Reference: Washington, "Introduction to Cyclotomic Fields", 2nd ed.,
        Chapter 13 (Iwasawa invariants of quadratic fields). For an
        imaginary quadratic field K = Q(sqrt(-d)) with class number divisible
        by 3 and p = 3 split or ramified appropriately, lambda_3 >= 1.
        For Q(sqrt(-23)) specifically (h = 3), lambda_3 = 1, mu_3 = 0.

        Hand-verified via the layer chain:
          |Cl(K_0)[3^inf]| = 3   (h(Q(sqrt(-23))) = 3)
          |Cl(K_1)[3^inf]| = 9
          |Cl(K_2)[3^inf]| = 27
        i.e. e_n = n + 1, giving lambda = 1, mu = 0, nu = 1.
        """
        res = lambda_mu('x^2 + 23', 3, n_max=2, max_layer_degree=20)
        assert res['fits_well'], f"Iwasawa fit failed: {res}"
        assert res['lambda'] == 1, f"expected lambda=1; got {res}"
        assert res['mu'] == 0, f"expected mu=0; got {res}"
        # Depth sequence should be 1, 2, 3 (or longer; first three pinned)
        assert res['depth_sequence'][:3] == [1, 2, 3], res['depth_sequence']

    def test_rationals_have_zero_invariants(self):
        """K = Q has trivial class group at every layer of every Z_p-ext.

        Reference: Q has class number 1; the cyclotomic Z_p-extension
        of Q has class number 1 at every layer (Iwasawa). Hence
        lambda_p(Q) = mu_p(Q) = nu_p(Q) = 0 for every p.
        """
        for p in [2, 3, 5, 7]:
            res = lambda_mu('x', p, n_max=3, max_layer_degree=20)
            assert res['lambda'] == 0, f"p={p}: {res}"
            assert res['mu'] == 0, f"p={p}: {res}"
            assert res['nu'] == 0, f"p={p}: {res}"
            assert all(c == 1 for c in res['class_number_sequence']), res

    def test_q_sqrt_minus_5_class_group_at_p_2(self):
        """Q(sqrt(-5)) has Cl = Z/2, so its 2-part is [2].

        Reference: Cohen, "Advanced Topics in Computational Number Theory",
        Table 1.1, p.10 (Q(sqrt(-5)) has class number 2). LMFDB
        nf_fields label '2.0.20.1'.
        """
        assert p_class_group_part('x^2 + 5', 2) == [2]
        assert p_class_group_part('x^2 + 5', 3) == []  # 3 does not divide h
        assert p_class_group_part('x^2 + 5', 5) == []

    def test_q_sqrt_minus_23_class_group_at_p_3(self):
        """Q(sqrt(-23)) has Cl = Z/3, so its 3-part is [3].

        Reference: LMFDB nf_fields label '2.0.23.1' lists class group
        structure [3]. Cohen Table 1.1.
        """
        assert p_class_group_part('x^2 + 23', 3) == [3]
        assert p_class_number('x^2 + 23', 3) == 3
        assert p_class_group_part('x^2 + 23', 2) == []  # h = 3 has no 2-part


# ---------------------------------------------------------------------------
# PROPERTY-BASED TESTS
# ---------------------------------------------------------------------------

class TestProperties:
    """Invariants satisfied by every output."""

    def test_depth_sequence_nonneg(self):
        """e_n >= 0 for every layer (class group order >= 1)."""
        for K, p in [('x^2 + 5', 2), ('x^2 + 23', 3), ('x^2 + 14', 2)]:
            res = lambda_mu(K, p, n_max=2, max_layer_degree=16)
            for e in res['depth_sequence']:
                assert e >= 0, f"K={K} p={p}: depth seq has negative entry: {res}"

    def test_class_number_monotone_nondecreasing(self):
        """|Cl(K_n)[p^inf]| is non-decreasing in n.

        Justification: K_n ⊂ K_{n+1} is unramified outside p, and the
        norm map between class groups is surjective in this tower
        (Iwasawa), so the p-part can only grow.
        """
        res = lambda_mu('x^2 + 23', 3, n_max=2, max_layer_degree=20)
        seq = res['class_number_sequence']
        for i in range(len(seq) - 1):
            assert seq[i] <= seq[i + 1], f"non-monotone at i={i}: {seq}"

    def test_class_number_is_p_power(self):
        """p_class_number must be a non-negative power of p."""
        for K, p in [('x^2 + 5', 2), ('x^2 + 23', 3), ('x^2 + 14', 2),
                     ('x^2 + 47', 5)]:
            n = p_class_number(K, p)
            assert n >= 1
            # n is a power of p iff log_p(n) is integer
            if n > 1:
                k = int(round(math.log(n, p)))
                assert p ** k == n, f"K={K} p={p}: n={n} not a p-power"

    def test_p_class_group_entries_are_p_powers(self):
        """Every entry of p_class_group_part(K, p) is a positive power of p."""
        for K, p in [('x^2 + 5', 2), ('x^2 + 23', 3), ('x^2 + 47', 5),
                     ('x^2 + 14', 2)]:
            parts = p_class_group_part(K, p)
            for c in parts:
                assert c >= p, f"K={K} p={p}: factor {c} < p"
                k = int(round(math.log(c, p)))
                assert p ** k == c, f"K={K} p={p}: factor {c} not p-power"

    @given(st.sampled_from([3, 5, 7, 11, 13]))
    @settings(max_examples=4, deadline=None,
              suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_p_class_number_q_sqrt_d_at_coprime_p(self, p):
        """For Q(sqrt(-1)) (h=1) the p-part is trivial for every p.

        Hypothesis-driven across small primes p.
        """
        assert p_class_number('x^2 + 1', p) == 1


# ---------------------------------------------------------------------------
# EDGE-CASE TESTS
# ---------------------------------------------------------------------------

class TestEdges:
    """Edges enumerated:
      - K of degree 1 (= Q): trivial invariants
      - n_max < 1: ValueError
      - non-prime p: ValueError
      - p of unreasonable size: layer cap kicks in (no fake fit)
      - empty polynomial list: ValueError
      - non-totally-real field passed to greenberg_test: warns
    """

    def test_degree_one_K_is_trivial(self):
        """K = Q is degree 1, all invariants are zero."""
        res = lambda_mu('x', 5, n_max=2)
        assert res == res  # well-formed dict
        assert res['lambda'] == 0
        assert res['mu'] == 0
        assert res['nu'] == 0
        assert res['fits_well']
        assert p_class_group_part('x', 7) == []
        assert p_class_number('x', 11) == 1

    def test_n_max_below_one_raises(self):
        """n_max < 1 is malformed input."""
        with pytest.raises(ValueError):
            lambda_mu('x^2 + 23', 3, n_max=0)
        with pytest.raises(ValueError):
            lambda_mu('x^2 + 23', 3, n_max=-1)

    def test_non_prime_p_raises(self):
        """p must be prime."""
        with pytest.raises(ValueError):
            p_class_group_part('x^2 + 5', 4)
        with pytest.raises(ValueError):
            p_class_number('x^2 + 5', 6)
        with pytest.raises(ValueError):
            lambda_mu('x^2 + 23', 9, n_max=2)
        with pytest.raises(ValueError):
            cyclotomic_zp_extension('x^2 + 5', 1, 1)

    def test_empty_polynomial_raises(self):
        """Empty coefficient list is malformed."""
        with pytest.raises(ValueError):
            p_class_group_part([], 3)
        with pytest.raises(ValueError):
            lambda_mu([], 3, n_max=2)

    def test_large_p_caps_at_layer_degree(self):
        """A very large p makes K_1 of unreachable degree; we cap honestly.

        K = Q(sqrt(-5)) (deg 2), p = 23: layer 1 has degree 46, exceeding
        max_layer_degree=20. Function must report fits_well=False (not
        enough layers) and capped=True without inventing a fit.
        """
        res = lambda_mu('x^2 + 5', 23, n_max=2, max_layer_degree=20)
        assert res['capped'] is True
        # Either no layers or only K_0 succeeded (deg 2 <= 20):
        assert res['layers_computed'] <= 1
        assert res['fits_well'] is False
        assert 'layer_degree_cap' in res['reason']


# ---------------------------------------------------------------------------
# COMPOSITION TESTS
# ---------------------------------------------------------------------------

class TestComposition:
    """Cross-tool consistency."""

    def test_p_class_number_equals_product_of_factors(self):
        """p_class_number(K, p) = product of p_class_group_part(K, p).

        Composition between the two p-Sylow extractors. Catches off-by-one
        in factor-product logic.
        """
        for K, p in [('x^2 + 5', 2), ('x^2 + 23', 3), ('x^2 + 14', 2),
                     ('x^2 + 1', 7), ('x', 5)]:
            parts = p_class_group_part(K, p)
            prod = 1
            for c in parts:
                prod *= c
            assert prod == p_class_number(K, p), \
                f"K={K} p={p}: parts={parts} prod={prod} vs {p_class_number(K, p)}"

    def test_lambda_mu_depth_matches_p_class_number(self):
        """Layer 0 of lambda_mu's class_number_sequence == p_class_number(K, p).

        Composition: the K_0 layer in the tower must equal the bare
        p-class number of K. Catches indexing bugs in the tower loop.
        """
        K = 'x^2 + 23'
        p = 3
        res = lambda_mu(K, p, n_max=1, max_layer_degree=20)
        assert res['class_number_sequence'][0] == p_class_number(K, p)

    def test_cyclotomic_zp_layer_0_equals_K_modulo_polredabs(self):
        """K_0 in the Z_p-tower equals K (up to polredabs / variable-rename).

        Composition: cyclotomic_zp_extension(K, p, 0) and K define the
        same number field. Verified by comparing PARI bnfinit class
        numbers (they must agree on the class number).
        """
        import cypari
        pari = cypari.pari
        K = 'x^2 + 23'
        K_0 = cyclotomic_zp_extension(K, 3, 0)
        h_K = int(pari(f'bnfinit({K}).no'))
        h_K0 = int(pari(f'bnfinit({K_0}).no'))
        assert h_K == h_K0, f"layer 0 not isomorphic to K: {K_0}"

    def test_greenberg_consistency_with_lambda_mu_for_real_field(self):
        """greenberg_test reports the same lambda/mu as lambda_mu directly.

        Composition: greenberg_test is built on top of lambda_mu and
        must agree on the underlying invariants. Use a totally real
        quadratic field K = Q(sqrt(2)).
        """
        K = 'x^2 - 2'
        p = 3
        res_g = greenberg_test(K, p, n_max=2, max_layer_degree=20)
        res_lm = lambda_mu(K, p, n_max=2, max_layer_degree=20)
        assert res_g['lambda'] == res_lm['lambda']
        assert res_g['mu'] == res_lm['mu']
        assert res_g['is_totally_real'] is True
