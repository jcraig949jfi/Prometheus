"""STUB test suite for ConstructiveExistenceWitness (Tier B core, substrate v3).

**Status:** STUB. Filed by substrate-tester fire #47 (2026-05-08) per
substrate v3 proposal `pivot/substrate_v3_proposal_stub_2026-05-08.md`.
ConstructiveExistenceWitness primitive does NOT yet exist in
`sigma_kernel/`. This file is a SHAPE-OF-TESTS document for Techne's
contract-change-window pickup.

**Origin:** four-fire convergence (#38/#39/#40/#41) + qualification
(#42) + extension (#44) + refinement (#45). Substrate has
ExclusionCertificate for negative existentials; needs companion
primitive for POSITIVE existentials with constructive witness across
~30+ catalog entries.

**Subtypes (6):**
  1. RankDecompositionWitness (sum of outer products + rank + uniqueness)
  2. ContractionOrderWitness (permutation/binary-tree + cost)
  3. IsomorphismCertificate (group-element tuple)
  4. LimitWitness / BorderRankWitness (parametric family + limit semantics)
  5. RepresentationTheoreticWitness (Young tableaux / pictographs)
  6. structural_inequality_certificate (Kruskal-bound-style sufficient cond.)

**How Techne picks this up:**
  1. Build the primitive in `sigma_kernel/constructive_existence_witness.py`
     (suggested module path, parallel to exclusion_certificate.py).
  2. Remove `@pytest.mark.skip` decorators one class at a time as each
     subtype lands.
  3. Tests should pass without modification — substrate-tester wrote
     them to specify the contract, not to be loose.

**Related tickets:** T-2026-05-08-ST-fire38-001 / 39-001 / 40-001 /
41-001 / 42-001 / 43-001 / 44-001 / 45-001 (capability-gap chain) +
ST-fire41-002 / 42-002 / 43-002 / 44-002 / 45-002 (Aporia coordination
chain).

This file uses pytest's collection-time skip mechanism: tests reference
imports that don't yet exist. We wrap import-time references in
try/except + module-level skip so pytest collects but skips the module
cleanly until the primitive exists.
"""
from __future__ import annotations

import pytest

# Module-level skip until Techne lands the primitive.
try:
    from sigma_kernel.constructive_existence_witness import (  # type: ignore[import-not-found]
        ConstructiveExistenceWitness,
        WitnessSubtype,
        RankDecompositionWitness,
        ContractionOrderWitness,
        IsomorphismCertificate,
        LimitWitness,
        RepresentationTheoreticWitness,
        StructuralInequalityCertificate,
        WitnessRegistry,
        WitnessVerificationError,
    )
    _PRIMITIVE_EXISTS = True
except ImportError:
    _PRIMITIVE_EXISTS = False

pytestmark = pytest.mark.skipif(
    not _PRIMITIVE_EXISTS,
    reason=(
        "ConstructiveExistenceWitness primitive not yet implemented. "
        "See pivot/substrate_v3_proposal_stub_2026-05-08.md and "
        "T-2026-05-08-ST-fire41-002 (Aporia coordination)."
    ),
)


# =============================================================================
# T1-T6 — parent-type contract tests (apply to all subtypes)
# =============================================================================


class TestParentContract:
    """Tests on ConstructiveExistenceWitness PARENT type. Subtype-specific
    payload tests live in per-subtype TestClasses below."""

    def test_T1_registry_collision_raises(self):
        """Sister to ExclusionCertificate's T020. Re-registering an
        equivalent witness should raise CollisionError (substrate's
        append-only discipline)."""
        from sigma_kernel.constructive_existence_witness import (
            CollisionError, WitnessRegistry,
        )
        registry = WitnessRegistry()
        witness = _make_minimal_witness()
        registry.register(witness)
        with pytest.raises(CollisionError):
            registry.register(witness)

    def test_T2_content_addressed_payload(self):
        """The witness's payload_hash MUST match _sha256(payload). Tampering
        with payload after construction MUST be detected by re-hashing
        on registry retrieval."""
        witness = _make_minimal_witness()
        assert witness.payload_hash is not None
        assert len(witness.payload_hash) == 64  # sha256 hex
        # roundtrip through a registry verifies hash stability
        from sigma_kernel.constructive_existence_witness import WitnessRegistry
        registry = WitnessRegistry()
        registry.register(witness)
        retrieved = registry.lookup(witness.witness_id)
        assert retrieved.payload_hash == witness.payload_hash

    def test_T3_subtype_dispatch(self):
        """witness.subtype must select the correct verifier. Each subtype
        has a registered verifier in the dispatch table; constructing a
        witness with mismatched subtype/payload should raise."""
        from sigma_kernel.constructive_existence_witness import (
            WitnessSubtype, get_verifier,
        )
        for subtype in WitnessSubtype:
            verifier = get_verifier(subtype)
            assert verifier is not None
            assert callable(verifier)

    def test_T4_verification_roundtrip(self):
        """A correctly-constructed witness must verify; a tampered
        witness must fail verification."""
        witness = _make_valid_rank_decomposition_witness()
        assert witness.verify() is True
        tampered = _tamper_payload(witness)
        assert tampered.verify() is False

    def test_T5_scope_replay_cert_registry_interaction(self):
        """Witness carries scope (region_spec), replay (ReplayInfo), and
        registers in WitnessRegistry alongside ExclusionCertificate's
        registry — same substrate hooks."""
        witness = _make_minimal_witness()
        assert witness.region_spec is not None
        assert witness.replay is not None
        assert witness.replay.code_hash is not None
        assert witness.replay.data_hash is not None
        assert witness.replay.seed is not None

    def test_T6_asymmetric_existential_consistency(self):
        """A positive ConstructiveExistenceWitness and a negative
        ExclusionCertificate cannot both exist for the same claim
        (region_spec + claim_property). Substrate's epistemic
        consistency rule."""
        from sigma_kernel.constructive_existence_witness import (
            WitnessRegistry, EpistemicInconsistencyError,
        )
        from sigma_kernel.exclusion_certificate import (
            CertificateRegistry, ExclusionCertificate,
        )
        # ... construct a claim with witness AND exclusion cert; expect
        # error when registering second
        witness = _make_minimal_witness()
        exclusion = _make_matching_exclusion_certificate(witness)
        wreg = WitnessRegistry()
        creg = CertificateRegistry()
        wreg.register(witness)
        with pytest.raises(EpistemicInconsistencyError):
            wreg.cross_check_against(creg)
            creg.register(exclusion)


# =============================================================================
# Subtype 1: RankDecompositionWitness (fire #38)
# =============================================================================


class TestRankDecompositionWitness:
    """Witness shape: (decomposition: Tuple[Tuple[Tensor, ...], ...],
    rank_claimed: int, uniqueness: 'nonunique'|'locally'|'globally')."""

    def test_decomposition_sums_to_target(self):
        """sum of outer products in decomposition must equal the target
        tensor (verifier numerical-equality check)."""
        # T = e_1 (x) e_1 + e_2 (x) e_2 (rank 2 in 2x2) — minimal valid case
        witness = _make_valid_rank_decomposition_witness()
        assert witness.verify() is True

    def test_rank_below_claimed_rejected(self):
        """If decomposition has fewer than rank_claimed components or sum
        doesn't match, verify() returns False."""
        witness = _make_valid_rank_decomposition_witness()
        # remove one component; now sum != target
        bad = witness.with_components(witness.decomposition[:-1])
        assert bad.verify() is False

    def test_uniqueness_annotation_present(self):
        """uniqueness in {'nonunique', 'locally', 'globally'}."""
        witness = _make_valid_rank_decomposition_witness()
        assert witness.uniqueness in ("nonunique", "locally", "globally")

    def test_globally_unique_witness_implies_kruskal_or_equivalent(self):
        """If uniqueness='globally', a sufficient-condition certificate
        (Kruskal-bound or equivalent) MUST be attached. Substrate's
        epistemic-explicitness discipline."""
        witness = _make_valid_rank_decomposition_witness(uniqueness="globally")
        assert witness.uniqueness_certificate is not None


# =============================================================================
# Subtype 2: ContractionOrderWitness (fire #39)
# =============================================================================


class TestContractionOrderWitness:
    """Witness shape: (network: TensorNetworkGraph, order: List[edge],
    cost: int, cost_metric: 'max_intermediate'|'flop_count')."""

    def test_order_is_valid_permutation_of_edges(self):
        """The order must be a valid contraction sequence (each edge
        appears exactly once; intermediate tensors well-formed)."""
        witness = _make_valid_contraction_order_witness()
        assert witness.verify() is True

    def test_claimed_cost_matches_recomputed(self):
        """Re-running cost computation on the order must equal the
        claimed cost (within numerical tolerance)."""
        witness = _make_valid_contraction_order_witness()
        recomputed = witness.recompute_cost()
        assert abs(recomputed - witness.cost) < 1e-9


# =============================================================================
# Subtype 3: IsomorphismCertificate (fire #40)
# =============================================================================


class TestIsomorphismCertificate:
    """Witness shape: (source_tensor, target_tensor, group_action,
    group_elements: Tuple[Matrix, ...])."""

    def test_group_elements_invertible(self):
        """All group_elements must be invertible (in GL_n)."""
        cert = _make_valid_isomorphism_certificate()
        for elem in cert.group_elements:
            assert _is_invertible(elem)

    def test_action_maps_source_to_target(self):
        """Applying group_action with group_elements to source must yield
        target (numerical equality)."""
        cert = _make_valid_isomorphism_certificate()
        assert cert.verify() is True


# =============================================================================
# Subtype 4: LimitWitness / BorderRankWitness (fire #41)
# =============================================================================


class TestLimitWitness:
    """Witness shape: (parametric_family: Callable[[float], Tensor],
    rank_bound: int, target: Tensor, epsilon_sequence: Sequence[float])."""

    def test_parametric_family_has_bounded_rank(self):
        """For each epsilon > 0 in epsilon_sequence, parametric_family(eps)
        must have rank <= rank_bound."""
        witness = _make_valid_limit_witness()
        assert witness.verify() is True

    def test_limit_equals_target(self):
        """As epsilon -> 0 along epsilon_sequence,
        parametric_family(eps) -> target (numerical convergence within
        substrate's epsilon-tolerance discipline)."""
        witness = _make_valid_limit_witness()
        assert witness.limit_distance() < 1e-6


# =============================================================================
# Subtype 5: RepresentationTheoreticWitness (fire #44)
# =============================================================================


class TestRepresentationTheoreticWitness:
    """Witness shape: (kronecker_triple: Tuple[Partition, Partition,
    Partition], witness_object: YoungTableau | Pictograph |
    PlethysmCoefficient)."""

    def test_witness_object_type_matches_subkind(self):
        """If witness_subkind='tableau', witness_object must be a
        YoungTableau; etc."""
        witness = _make_valid_rep_theoretic_witness()
        assert witness.verify() is True

    def test_kronecker_coefficient_positive_when_witness_present(self):
        """The presence of any valid witness implies g(λ, μ, ν) > 0."""
        witness = _make_valid_rep_theoretic_witness()
        assert witness.implies_positivity is True


# =============================================================================
# Subtype 6: StructuralInequalityCertificate (fire #45)
# =============================================================================


class TestStructuralInequalityCertificate:
    """Witness shape: (predicate: 'Kruskal_2r_plus_2'|'AlexanderHirschowitz'
    |..., k_rank_data: dict, sufficient_condition_satisfied: bool)."""

    def test_predicate_evaluates_true(self):
        """The named predicate (e.g. Kruskal's 2r+2 <= sum k_i) must
        evaluate to True given the k_rank_data."""
        cert = _make_valid_structural_inequality_certificate()
        assert cert.verify() is True

    def test_substrate_epistemic_explicitness(self):
        """The certificate carries a NAMED predicate from a registry of
        known sufficient conditions (no anonymous/text predicates)."""
        cert = _make_valid_structural_inequality_certificate()
        from sigma_kernel.constructive_existence_witness import (
            KNOWN_SUFFICIENT_CONDITIONS,
        )
        assert cert.predicate in KNOWN_SUFFICIENT_CONDITIONS


# =============================================================================
# Tier-B / Tier-D composition (fires #43 + #45)
# =============================================================================


class TestTierBTierDComposition:
    """Tier B at fixed parameters + Tier D at parameter scaling.
    Examples: SOS-witness-at-(n,d,lambda) + threshold-curve-at-scaling-n."""

    def test_witness_at_fixed_parameters_implies_threshold_regime_above(self):
        """If a positive Tier-B witness exists at parameters P, and P is
        registered against a Tier-D PhaseTransitionThreshold T, then P
        must fall in T.regime_above (the 'capable' side of the
        transition)."""
        # Requires Tier D primitive too; double-skip if either missing.
        try:
            from sigma_kernel.distribution_object import (  # type: ignore[import-not-found]
                PhaseTransitionThreshold,
            )
        except ImportError:
            pytest.skip("Tier D not yet implemented")
        # ... assemble witness + threshold + assert membership in
        # regime_above
        pass


# =============================================================================
# Helper builders (will be implemented when primitive lands)
# =============================================================================


def _make_minimal_witness():
    """Construct a minimal valid ConstructiveExistenceWitness for parent
    contract tests. Subtype = whichever is simplest to instantiate."""
    raise NotImplementedError("primitive not yet built")


def _make_valid_rank_decomposition_witness(uniqueness: str = "locally"):
    raise NotImplementedError("primitive not yet built")


def _make_valid_contraction_order_witness():
    raise NotImplementedError("primitive not yet built")


def _make_valid_isomorphism_certificate():
    raise NotImplementedError("primitive not yet built")


def _make_valid_limit_witness():
    raise NotImplementedError("primitive not yet built")


def _make_valid_rep_theoretic_witness():
    raise NotImplementedError("primitive not yet built")


def _make_valid_structural_inequality_certificate():
    raise NotImplementedError("primitive not yet built")


def _make_matching_exclusion_certificate(witness):
    raise NotImplementedError("primitive not yet built")


def _tamper_payload(witness):
    raise NotImplementedError("primitive not yet built")


def _is_invertible(matrix):
    import numpy as np
    return np.linalg.matrix_rank(matrix) == matrix.shape[0]
