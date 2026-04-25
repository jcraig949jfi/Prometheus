"""Test suite for prometheus_math.number_fields p-class-field-tower operations.

Project #29 Phase 1. p-Hilbert class field iteration ("p-class-field tower"),
extending TOOL_HILBERT_CLASS_FIELD with restriction to the p-Sylow of Cl(K).

Categories per math-tdd skill (techne/skills/math-tdd.md):
  - Authority: published h_p / p-HCF results (Cohen, Washington).
  - Property:  invariants p-HCF must satisfy (degree | h_p, monotone, ...).
  - Edge:      K=Q, h_K=1, max_depth=0, invalid p, after-termination idempotence.
  - Composition: degree(p-HCF) = product(p_class_group_part); H_K factors through H_p(K).

Run: pytest prometheus_math/tests/test_p_class_field_tower.py -v
"""
from __future__ import annotations

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from prometheus_math.number_fields import (
    p_hilbert_class_field,
    p_class_field_tower,
    tower_terminates_p,
    p_tower_signature,
    hilbert_class_field,
)
from prometheus_math.iwasawa import p_class_group_part, p_class_number


# ---------------------------------------------------------------------------
# AUTHORITY-BASED TESTS
# ---------------------------------------------------------------------------

class TestAuthority:
    """Cross-checks against published p-class-field results."""

    def test_q_sqrt_minus_23_at_p_3_hcf_is_cubic(self):
        """Q(sqrt(-23)) at p=3: 3-HCF is a cyclic degree-3 extension of K.

        Reference: Cohen, "A Course in Computational Algebraic Number
        Theory", Table 4.4 (small imaginary quadratic class numbers).
        h(Q(sqrt(-23))) = 3, class group Z/3, so 3-Sylow is full Cl(K)
        and the 3-Hilbert class field equals the full Hilbert class field
        of degree 6 over Q.

        Hand-verified: Cohen Theorem 6.3.4 — for K imaginary quadratic
        with cyclic class group of prime order p, H_p(K) = H(K).
        """
        result = p_hilbert_class_field('x^2+23', 3)
        assert result['degree_rel'] == 3, result
        assert result['degree_abs'] == 6, result
        assert result['class_number_p_K'] == 3, result
        assert not result['is_trivial']

    def test_q_sqrt_minus_5_at_p_2_hcf_is_quadratic(self):
        """Q(sqrt(-5)) at p=2: 2-HCF is a cyclic degree-2 extension of K.

        Reference: Cohen, "A Course in Computational Algebraic Number
        Theory", Table 1.1 (p.10). h(Q(sqrt(-5))) = 2, class group Z/2,
        so 2-Sylow is full and the 2-Hilbert class field equals the
        Hilbert class field. The polredabs canonical form is x^4+3x^2+1
        (Q(sqrt(-5), i), the genus field).

        Cross-check: LMFDB nf_fields label '2.0.20.1' (class_number=2).
        """
        result = p_hilbert_class_field('x^2+5', 2)
        assert result['degree_rel'] == 2
        assert result['degree_abs'] == 4
        assert result['class_number_p_K'] == 2
        assert result['abs_poly'] == 'x^4 + 3*x^2 + 1'

    def test_q_i_at_p_2_is_trivial(self):
        """Q(i) = Q(sqrt(-1)) at p=2: tower trivial since h(Q(i))=1.

        Reference: Cohen Table 1.1 (Q(i) class number 1, "Heegner
        list" of imaginary quadratic UFDs). Trivial tower at every p.
        LMFDB nf_fields label '2.0.4.1' (class_number=1).
        """
        result = p_hilbert_class_field('x^2+1', 2)
        assert result['is_trivial']
        assert result['degree_rel'] == 1
        assert result['class_number_p_K'] == 1

        tower = p_class_field_tower('x^2+1', 2, max_depth=3)
        assert tower['terminated']
        assert tower['terminated_depth'] == 0

    def test_heegner_disc_minus_163_trivial_at_any_p(self):
        """Q(sqrt(-163)) at any p: tower trivial since h=1 (largest Heegner).

        Reference: Heegner-Stark theorem — discriminants
        D in {-3,-4,-7,-8,-11,-19,-43,-67,-163} are exactly the imaginary
        quadratic UFDs. Cohen Theorem 5.4.1.
        """
        for prime in (2, 3, 5, 7):
            result = p_hilbert_class_field('x^2+163', prime)
            assert result['is_trivial'], f"p={prime}: {result}"
            tower = p_class_field_tower('x^2+163', prime, max_depth=2)
            assert tower['terminated'], f"p={prime}: {tower}"
            assert tower['terminated_depth'] == 0

    def test_q_sqrt_minus_23_p_3_tower_terminates_at_depth_one(self):
        """Q(sqrt(-23)) at p=3: full 3-tower terminates at depth 1.

        Reference: Washington, "Introduction to Cyclotomic Fields",
        2nd ed., §10.3 (class field tower of imaginary quadratic
        fields with small h_p). The 3-HCF of Q(sqrt(-23)) is the
        sextic field Q[x]/(x^6-3x^5+5x^4-5x^3+5x^2-3x+1), which has
        class number 1 (hence tower terminates at depth 1).

        Hand-verified by computing bnfinit on the depth-1 field:
        cyc = [] (trivial class group).
        """
        tower = p_class_field_tower('x^2+23', 3, max_depth=3)
        assert tower['terminated'], tower
        assert tower['terminated_depth'] == 1, tower
        # Degree progression: K = degree 2, depth 1 = degree 6
        assert tower['degree_progression'][:2] == [2, 6], tower


# ---------------------------------------------------------------------------
# PROPERTY-BASED TESTS
# ---------------------------------------------------------------------------

class TestProperties:
    """Invariants that p_hilbert_class_field / tower must satisfy."""

    @pytest.mark.parametrize("d,p,expected_h_p", [
        (-5, 2, 2),    # cyc = [2]
        (-23, 3, 3),   # cyc = [3]
        (-1, 2, 1),    # cyc = []
        (-7, 2, 1),    # cyc = []
        (-163, 3, 1),  # cyc = []
    ])
    def test_degree_equals_h_p(self, d, p, expected_h_p):
        """For abelian p-Sylow, degree(p_HCF) over K equals h_p(K).

        Property: |Gal(H_p(K)/K)| = |Cl(K)[p^infty]| by class field theory.
        """
        result = p_hilbert_class_field(f'x^2+{-d}' if d < 0 else f'x^2-{d}', p)
        assert result['degree_rel'] == expected_h_p
        assert result['class_number_p_K'] == expected_h_p

    @pytest.mark.parametrize("d,p", [(-5, 2), (-23, 3), (-1, 2), (-163, 5)])
    def test_tower_degrees_are_monotone_nondecreasing(self, d, p):
        """Tower's cumulative degree progression is monotone non-decreasing.

        Property: each layer is an extension (possibly trivial) of the prior,
        so [K_n : Q] divides [K_{n+1} : Q].
        """
        tower = p_class_field_tower(f'x^2+{-d}', p, max_depth=2)
        degs = tower['degree_progression']
        for i in range(1, len(degs)):
            assert degs[i] >= degs[i - 1], f"non-monotone: {degs}"
            assert degs[i] % degs[i - 1] == 0, \
                f"deg[{i}]={degs[i]} not divisible by deg[{i-1}]={degs[i-1]}"

    def test_termination_idempotent(self):
        """If tower terminates at depth d, depths >= d return the same poly.

        Property: once h_p = 1 we hit a fixed point of p_hilbert_class_field.
        """
        tower = p_class_field_tower('x^2+23', 3, max_depth=4)
        assert tower['terminated']
        d = tower['terminated_depth']
        polys = tower['tower']
        # Polys at indices d, d+1 (and beyond if computed) must be identical.
        for i in range(d, len(polys) - 1):
            assert polys[i] == polys[i + 1], \
                f"tower diverges after termination at depth {d}: {polys}"

    @pytest.mark.parametrize("p", [2, 3, 5, 7, 11])
    def test_h_p_eq_one_implies_trivial_extension(self, p):
        """If Cl(K)[p^infty] is trivial, p_HCF(K) = K (degree 1 over K).

        Property: trivial p-class group ⇒ trivial p-HCF.
        Test: Q(i) has h=1, so trivial at every p.
        """
        result = p_hilbert_class_field('x^2+1', p)
        assert result['is_trivial']
        assert result['degree_rel'] == 1

    @given(d=st.sampled_from([1, 5, 23, 47, 163]),
           p=st.sampled_from([2, 3, 5]))
    @settings(max_examples=10, deadline=None,
              suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_signature_first_entry_equals_base_degree(self, d, p):
        """Property: tower signature's first entry is always [K_0 : Q] = 2.

        For any imaginary quadratic K = Q(sqrt(-d)), depth-0 of the tower
        is K itself with degree 2. p_tower_signature returns the
        cumulative degree progression including layer 0.
        """
        sig = p_tower_signature(f'x^2+{d}', p, max_depth=1)
        assert isinstance(sig, tuple)
        assert len(sig) >= 1
        assert sig[0] == 2  # base field degree


# ---------------------------------------------------------------------------
# EDGE-CASE TESTS
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Documented edge cases.

    Edges covered:
    - K = Q (degree 1): trivial tower
    - h_K = 1: trivial tower at any p
    - max_depth = 0: returns just K, no iteration
    - invalid p (non-prime, p < 2): ValueError
    - p larger than h_K: trivial p-part, immediate termination
    - empty/malformed polynomial: ValueError
    """

    def test_K_eq_Q_is_trivial(self):
        """K = Q has trivial class group at any p."""
        result = p_hilbert_class_field('x', 3)
        assert result['is_trivial']
        assert result['degree_rel'] == 1

        tower = p_class_field_tower('x', 5, max_depth=3)
        assert tower['terminated']
        assert tower['terminated_depth'] == 0
        assert tower['degree_progression'] == [1]

    def test_max_depth_zero_returns_K_alone(self):
        """max_depth=0 returns the base field with no iteration attempted."""
        tower = p_class_field_tower('x^2+23', 3, max_depth=0)
        assert tower['max_depth_reached'] == 0
        assert len(tower['tower']) == 1
        # h_3 of K = 3 != 1, so not terminated, but capped immediately
        assert tower['terminated_depth'] is None or tower['terminated_depth'] == 0

    def test_invalid_prime_raises(self):
        """Non-prime or p < 2 raises ValueError."""
        with pytest.raises(ValueError):
            p_hilbert_class_field('x^2+5', 1)
        with pytest.raises(ValueError):
            p_hilbert_class_field('x^2+5', 4)
        with pytest.raises(ValueError):
            p_hilbert_class_field('x^2+5', -3)
        with pytest.raises(ValueError):
            p_class_field_tower('x^2+5', 4)

    def test_empty_polynomial_raises(self):
        """Empty polynomial coeff list raises ValueError."""
        with pytest.raises(ValueError):
            p_hilbert_class_field([], 3)
        with pytest.raises(ValueError):
            p_class_field_tower([], 3)

    def test_p_not_dividing_h_is_trivial(self):
        """p coprime to h_K ⇒ p-Sylow is trivial ⇒ p-HCF = K."""
        # Q(sqrt(-5)) has h=2; p=3 should give trivial p-HCF
        result = p_hilbert_class_field('x^2+5', 3)
        assert result['is_trivial']
        # Q(sqrt(-23)) has h=3; p=2 should give trivial p-HCF
        result = p_hilbert_class_field('x^2+23', 2)
        assert result['is_trivial']

    def test_tower_terminates_p_convenience(self):
        """tower_terminates_p returns boolean correctly for known cases."""
        assert tower_terminates_p('x^2+1', 2, max_depth=2)        # h=1 trivial
        assert tower_terminates_p('x^2+5', 2, max_depth=2)        # depth 1
        assert tower_terminates_p('x^2+23', 3, max_depth=2)       # depth 1
        assert tower_terminates_p('x^2+163', 5, max_depth=2)      # h=1 trivial


# ---------------------------------------------------------------------------
# COMPOSITION TESTS
# ---------------------------------------------------------------------------

class TestComposition:
    """Multi-tool consistency checks."""

    @pytest.mark.parametrize("polynomial,p", [
        ('x^2+5', 2),
        ('x^2+23', 3),
        ('x^2+47', 5),  # h=5
    ])
    def test_p_hcf_degree_matches_p_class_group_part_product(self, polynomial, p):
        """[H_p(K) : K] = product(p_class_group_part(K, p)).

        Composition: cross-check against project #26's
        prometheus_math.iwasawa.p_class_group_part. Both must agree on
        the size of Cl(K)[p^infty].
        """
        hcf = p_hilbert_class_field(polynomial, p)
        parts = p_class_group_part(polynomial, p)
        expected_h_p = 1
        for c in parts:
            expected_h_p *= c
        assert hcf['degree_rel'] == expected_h_p, \
            f"p-HCF degree {hcf['degree_rel']} != prod parts {expected_h_p} for {polynomial}, p={p}"
        assert hcf['class_number_p_K'] == p_class_number(polynomial, p)

    def test_full_hcf_factors_through_p_hcf_for_each_p(self):
        """The full Hilbert class field factors through H_p(K) for each p|h.

        Composition: for K with h_K = prod_p p^{a_p}, we have
            [H(K) : K] = h_K = prod_p [H_p(K) : K] = prod_p p^{a_p}.
        Cross-checks hilbert_class_field against p_hilbert_class_field.

        Test field: Q(sqrt(-89)) has h=12, cyc=[12]. So
        [H : K] = 12 = [H_2 : K] * [H_3 : K] = 4 * 3.
        """
        full = hilbert_class_field('x^2+89')
        h2 = p_hilbert_class_field('x^2+89', 2)
        h3 = p_hilbert_class_field('x^2+89', 3)
        assert full['degree_rel'] == 12
        assert h2['degree_rel'] == 4
        assert h3['degree_rel'] == 3
        assert h2['degree_rel'] * h3['degree_rel'] == full['degree_rel']

    def test_p_tower_signature_matches_progression(self):
        """p_tower_signature is the degree_progression as a tuple.

        Composition: signature is a derived view of the tower dict.
        """
        tower = p_class_field_tower('x^2+23', 3, max_depth=2)
        sig = p_tower_signature('x^2+23', 3, max_depth=2)
        assert sig == tuple(tower['degree_progression'])
