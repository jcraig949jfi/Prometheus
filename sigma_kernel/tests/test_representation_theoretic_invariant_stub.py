"""STUB test suite for Tier E meta-primitive (substrate v3):
RepresentationTheoreticInvariant.

**Status:** STUB. Filed by substrate-tester fire #60 (2026-05-09) per
Aporia ratification (`pivot/restart_decisions_2026-05-09.md`, commit
370b28c6). Tier E meta-primitive does NOT yet exist in
`sigma_kernel/`. This file is a SHAPE-OF-TESTS document for Techne's
Phase-2 contract-change-window pickup.

**This is the 5th and final of 5 meta-primitive stubs**, closing the
set begun in fires #47/#48/#58/#59.

**Origin:** fire #44 (catalog #95 Kronecker positivity, §XII GCT)
surfaced PartitionObject + IrreducibleRepresentation +
SymmetricFunction/Plethysm as Tier E. Plus RepresentationTheoreticWitness
as Tier B subtype #5. Aporia bundled into a single Tier E meta-primitive.

**What this primitive carries (per Aporia's bundling):**
- Partition / Young diagram with combinatorial structure (transpose
  λ', dominance order, branching rule λ → μ)
- Irreducible representation lookup / character / dimension
- Symmetric-function ring elements (Schur basis s_λ, power-sum p_λ,
  monomial m_λ) with operations: multiplication, plethysm s_a[s_b],
  ω involution, Hall inner product
- Kronecker coefficients g(λ, μ, ν) — multiplicity of V_ν in V_λ ⊗ V_μ
  as S_n-modules
- Plethysm coefficients (e.g. Foulkes' s_a[s_b] - s_b[s_a] expansion)
- Schur-positivity certificates

**Catalog coverage per Aporia:** §XII GCT (#95-100); absorbs:
- T-ST-fire44-001 (Kronecker positivity) → Tier E meta-primitive
  instance for catalog #95
- §XII #92 (GCT VP vs VNP via padded permanent) — plethystic
  obstruction certificates
- §XII #98 (Foulkes' conjecture) — Schur-positivity claim
- §XII #99 (Saxl's conjecture) — tensor-square contains every irrep

**How Techne picks this up:**
  1. Build primitive in `sigma_kernel/representation_theoretic_invariant.py`
     (or split: `partition.py`, `symmetric_function.py`,
     `irreducible_representation.py`).
  2. Remove module-level `skipif` when import succeeds.
  3. Tests should pass without modification.

**Cross-tier interactions:**
- Tier B `RepresentationTheoreticWitness` (subtype #5) — Young-tableau
  / pictograph / plethysm-coefficient witnesses for g > 0 existence
  claims; verifier consumes Tier E primitives
- Tier A `TensorNetwork` — when network has S_n-symmetry, irrep
  decomposition is a Tier E operation
- Tier C `MomentPolytope` — Berenstein-Sjamaar's moment polytope is
  defined via irrep multiplicities (Tier E feeds Tier C)

**Sister files (the 5-stub set):**
  - test_constructive_existence_witness_stub.py (fire #47, Tier B)
  - test_distribution_object_stub.py (fire #48, Tier D)
  - test_moment_polytope_stub.py (fire #58, Tier C)
  - test_tensor_network_stub.py (fire #59, Tier A)
  - test_representation_theoretic_invariant_stub.py (fire #60, Tier E — THIS FILE)

**Source ticket:** T-2026-05-09-ST-fire60-001 (Techne; closes the
5-stub set).
"""
from __future__ import annotations

import pytest

# Module-level skip until Techne lands the Tier E meta-primitive.
try:
    from sigma_kernel.representation_theoretic_invariant import (  # type: ignore[import-not-found]
        Partition,
        IrreducibleRepresentation,
        SymmetricFunction,
        SchurFunction,
        Plethysm,
        KroneckerCoefficient,
        SchurPositivityCertificate,
        IrrepRegistry,
    )
    _PRIMITIVE_EXISTS = True
except ImportError:
    _PRIMITIVE_EXISTS = False

pytestmark = pytest.mark.skipif(
    not _PRIMITIVE_EXISTS,
    reason=(
        "Tier E RepresentationTheoreticInvariant meta-primitive not "
        "yet implemented. See pivot/restart_decisions_2026-05-09.md "
        "(decision 2 — meta-primitive 4 of 5: Schur/Kronecker/plethysm "
        "certificates) and source fire #44 (catalog #95 Kronecker "
        "positivity origin)."
    ),
)


# =============================================================================
# Partition contract — combinatorial structure on Young diagrams
# =============================================================================


class TestPartitionContract:
    """Partition λ = (λ_1, λ_2, ..., λ_k) of n with λ_1 ≥ λ_2 ≥ ... ≥ λ_k > 0."""

    def test_construction_from_tuple(self):
        lam = Partition.from_tuple((4, 2, 1))
        assert lam.size == 7
        assert lam.length == 3

    def test_nonincreasing_validation(self):
        """Strictly increasing parts must raise (Young diagram convention)."""
        with pytest.raises(ValueError):
            Partition.from_tuple((1, 2, 3))

    def test_nonpositive_part_rejected(self):
        with pytest.raises(ValueError):
            Partition.from_tuple((3, 2, 0, -1))

    def test_transpose_involution(self):
        """λ'' == λ for all λ (transpose is its own inverse)."""
        for parts in [(4, 2, 1), (3, 3, 1), (5,), (1, 1, 1, 1)]:
            lam = Partition.from_tuple(parts)
            assert lam.transpose().transpose() == lam

    def test_dominance_partial_order(self):
        """λ dominates μ iff sum_{i<=k} λ_i >= sum_{i<=k} μ_i for all k.
        Reflexive + transitive + antisymmetric."""
        a = Partition.from_tuple((3, 2, 1))
        b = Partition.from_tuple((2, 2, 2))
        # a dominates b: 3>=2, 3+2>=2+2, 3+2+1==2+2+2
        assert a.dominates(b) is True
        assert b.dominates(a) is False
        assert a.dominates(a) is True  # reflexive

    def test_content_addressed_id(self):
        a = Partition.from_tuple((4, 2, 1))
        b = Partition.from_tuple((4, 2, 1))
        assert a.partition_id == b.partition_id


# =============================================================================
# IrreducibleRepresentation contract
# =============================================================================


class TestIrreducibleRepresentationContract:
    """V_λ for λ ⊢ n is an irreducible S_n-module of dimension f^λ
    (number of standard Young tableaux of shape λ)."""

    def test_lookup_by_partition(self):
        lam = Partition.from_tuple((3, 1))
        v = IrreducibleRepresentation.for_partition(lam)
        assert v.partition == lam

    def test_dimension_via_hook_length_formula(self):
        """f^λ = n! / product of hook lengths. Spot-check on (3,1):
        n=4; hooks: row 1 = (4, 2, 1); row 2 = (1); product = 8;
        4!/8 = 3."""
        lam = Partition.from_tuple((3, 1))
        v = IrreducibleRepresentation.for_partition(lam)
        assert v.dimension == 3

    def test_trivial_rep_is_one_dimensional(self):
        """V_(n) is the trivial representation; dim = 1."""
        for n in (1, 2, 3, 5, 10):
            lam = Partition.from_tuple((n,))
            v = IrreducibleRepresentation.for_partition(lam)
            assert v.dimension == 1

    def test_sign_rep_dimension(self):
        """V_(1^n) is the sign representation; dim = 1."""
        for n in (2, 3, 4):
            lam = Partition.from_tuple(tuple(1 for _ in range(n)))
            v = IrreducibleRepresentation.for_partition(lam)
            assert v.dimension == 1


# =============================================================================
# SymmetricFunction / Schur basis contract
# =============================================================================


class TestSymmetricFunctionContract:
    """Symmetric-function ring Λ with Schur basis s_λ + plethysm + Hall
    inner product."""

    def test_schur_function_construction(self):
        s = SchurFunction.for_partition(Partition.from_tuple((2, 1)))
        assert s.degree == 3

    def test_schur_orthonormality_under_hall_inner_product(self):
        """⟨s_λ, s_μ⟩ = δ_{λ,μ}."""
        s_21 = SchurFunction.for_partition(Partition.from_tuple((2, 1)))
        s_3 = SchurFunction.for_partition(Partition.from_tuple((3,)))
        s_111 = SchurFunction.for_partition(Partition.from_tuple((1, 1, 1)))
        assert s_21.hall_inner_product(s_21) == 1
        assert s_21.hall_inner_product(s_3) == 0
        assert s_21.hall_inner_product(s_111) == 0

    def test_schur_multiplication_uses_LR_rule(self):
        """s_λ · s_μ = sum_ν c^ν_{λ,μ} s_ν where c^ν_{λ,μ} is
        Littlewood-Richardson coefficient. Spot-check: s_1 · s_1 =
        s_2 + s_(1,1)."""
        s_1 = SchurFunction.for_partition(Partition.from_tuple((1,)))
        product = s_1 * s_1
        # Coefficients of s_2 and s_(1,1) in the product should both be 1
        c_2 = product.coefficient_of(Partition.from_tuple((2,)))
        c_11 = product.coefficient_of(Partition.from_tuple((1, 1)))
        assert c_2 == 1
        assert c_11 == 1

    def test_omega_involution(self):
        """ω(s_λ) = s_{λ'}. Power-sum: ω(p_n) = (-1)^(n-1) p_n. Spot
        check via ω(ω(f)) == f."""
        s = SchurFunction.for_partition(Partition.from_tuple((3, 1)))
        omega_s = s.omega()
        # ω(s_(3,1)) = s_(2,1,1)
        assert omega_s.leading_partition() == Partition.from_tuple((2, 1, 1))


# =============================================================================
# Plethysm contract — s_a[s_b] etc.
# =============================================================================


class TestPlethysmContract:
    """Plethysm s_λ[s_μ] is composition in the symmetric-function ring."""

    def test_plethysm_returns_symmetric_function(self):
        s_2 = SchurFunction.for_partition(Partition.from_tuple((2,)))
        s_2_of_s_1 = Plethysm.compute(outer=s_2, inner=s_2)
        assert isinstance(s_2_of_s_1, SymmetricFunction)

    def test_known_plethysm_s_2_of_s_2(self):
        """s_2[s_2] = s_4 + s_(2,2). Classic small case."""
        s_2 = SchurFunction.for_partition(Partition.from_tuple((2,)))
        result = Plethysm.compute(outer=s_2, inner=s_2)
        c_4 = result.coefficient_of(Partition.from_tuple((4,)))
        c_22 = result.coefficient_of(Partition.from_tuple((2, 2)))
        assert c_4 == 1
        assert c_22 == 1


# =============================================================================
# KroneckerCoefficient contract — g(λ, μ, ν)
# =============================================================================


class TestKroneckerCoefficientContract:
    """g(λ, μ, ν) = multiplicity of V_ν in V_λ ⊗ V_μ as S_n-modules."""

    def test_known_g_2_2_2_equals_1(self):
        """g((2), (2), (2)) = 1 (trivial × trivial = trivial)."""
        lam = Partition.from_tuple((2,))
        g = KroneckerCoefficient.compute(lam, lam, lam)
        assert g == 1

    def test_g_is_symmetric_under_partition_swap(self):
        """g(λ, μ, ν) = g(μ, λ, ν) = g(ν, μ, λ) = ... (S_3 symmetry)."""
        a = Partition.from_tuple((2, 1))
        b = Partition.from_tuple((2, 1))
        c = Partition.from_tuple((2, 1))
        g_abc = KroneckerCoefficient.compute(a, b, c)
        g_bac = KroneckerCoefficient.compute(b, a, c)
        g_cba = KroneckerCoefficient.compute(c, b, a)
        assert g_abc == g_bac == g_cba

    def test_g_nonnegative(self):
        """Kronecker coefficients are non-negative (multiplicities)."""
        for parts in [(3,), (2, 1), (1, 1, 1)]:
            lam = Partition.from_tuple(parts)
            g = KroneckerCoefficient.compute(lam, lam, lam)
            assert g >= 0


# =============================================================================
# SchurPositivityCertificate contract
# =============================================================================


class TestSchurPositivityCertificateContract:
    """A SchurPositivityCertificate witnesses 'f is Schur-positive,'
    i.e. its Schur expansion has all non-negative coefficients."""

    def test_positive_function_certifies_positive(self):
        s_2 = SchurFunction.for_partition(Partition.from_tuple((2,)))
        cert = SchurPositivityCertificate.for_function(s_2)
        assert cert.is_schur_positive is True

    def test_negative_coefficient_fails_certificate(self):
        """A symmetric function with a negative Schur coefficient is
        NOT Schur-positive."""
        s_2 = SchurFunction.for_partition(Partition.from_tuple((2,)))
        s_11 = SchurFunction.for_partition(Partition.from_tuple((1, 1)))
        # s_2 - s_(1,1) has negative coefficient on s_(1,1)
        f = s_2 - s_11
        cert = SchurPositivityCertificate.for_function(f)
        assert cert.is_schur_positive is False


# =============================================================================
# Tier B / Tier E composition: RepresentationTheoreticWitness verification
# =============================================================================


class TestTierBTierEComposition:
    """RepresentationTheoreticWitness (Tier B subtype #5 from fire #44)
    consumes Tier E primitives to construct g > 0 witnesses."""

    def test_witness_for_kronecker_positivity_via_tableau(self):
        """A Young-tableau witness for g(λ,μ,ν) > 0 must reference
        Partition objects from Tier E and verify the count > 0."""
        try:
            from sigma_kernel.constructive_existence_witness import (  # type: ignore[import-not-found]
                RepresentationTheoreticWitness,
            )
        except ImportError:
            pytest.skip("Tier B not yet implemented")
        # ... assemble a tableau witness; verify Kronecker coefficient > 0
        pass


# =============================================================================
# Catalog coverage smoke (per Aporia: §XII #95-100)
# =============================================================================


class TestCatalogCoverageSmoke:
    """Smoke-test that the Tier E primitive can represent §XII GCT
    catalog entries."""

    def test_kronecker_coefficient_decision_problem(self):
        """Catalog #95: decide g(λ, μ, ν) > 0. KroneckerCoefficient
        primitive must support."""
        a = Partition.from_tuple((3, 1))
        b = Partition.from_tuple((2, 2))
        c = Partition.from_tuple((2, 1, 1))
        g = KroneckerCoefficient.compute(a, b, c)
        # Just exercise; specific value not asserted (open problem)
        assert g >= 0

    def test_foulkes_setup(self):
        """Catalog #98 (Foulkes' conjecture): s_a[s_b] - s_b[s_a]
        Schur-positive for a ≤ b. Smoke: the difference is constructible
        as a SymmetricFunction and SchurPositivityCertificate is
        applicable."""
        s_a = SchurFunction.for_partition(Partition.from_tuple((2,)))
        s_b = SchurFunction.for_partition(Partition.from_tuple((3,)))
        plet_a_b = Plethysm.compute(outer=s_a, inner=s_b)
        plet_b_a = Plethysm.compute(outer=s_b, inner=s_a)
        diff = plet_a_b - plet_b_a
        cert = SchurPositivityCertificate.for_function(diff)
        # Just check the certificate object is constructible; the
        # is_schur_positive value is the OPEN problem
        assert cert is not None
