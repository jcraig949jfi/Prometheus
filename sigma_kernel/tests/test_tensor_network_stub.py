"""STUB test suite for Tier A++ meta-primitive (substrate v3):
TensorNetwork.

**Status:** STUB. Filed by substrate-tester fire #59 (2026-05-09) per
Aporia ratification (`pivot/restart_decisions_2026-05-09.md`, commit
370b28c6). Tier A++ TensorNetwork meta-primitive does NOT yet exist
in `sigma_kernel/`. This file is a SHAPE-OF-TESTS document for
Techne's Phase-2 contract-change-window pickup.

**Why "Tier A++":** Aporia's framing — TensorNetwork extends the
existing `CoordinateChart` primitive with index-contraction structure.
The "++" denotes both the extension (it builds on Tier A) and the
fact that it absorbs / unifies several substrate-tester-surfaced
finer-grained primitives:
  - TensorObject (n-dim tensor with entry-level identity, fire #38)
  - TensorNetworkGraph (LabeledHypergraph, fire #39)
  - GroupAction (group-element tuples acting on tensors, fire #40)
  - SchemeObject (algebraic-geometric vanishing locus, fire #41)

**What this primitive carries (per Aporia's bundling):**
- Network topology (vertices = tensors with shapes; edges = shared
  index labels; possibly hypergraph for multi-tensor index sharing)
- Tensor entries at each vertex (TensorObject role)
- Group-action structure when the network has GL_n symmetry
  (GroupAction role)
- Algebraic constraints / defining ideals (SchemeObject role) for the
  vanishing locus of the network's contraction value
- Index-contraction operation: contract one or more shared edges,
  returning a smaller network or a scalar

**Catalog coverage per Aporia:** P30 attack paradigm; catalog #49-51
(tensor-train rank, Tucker compression, Hackbusch hierarchical),
#75-78 (area law conditions, PEPS contraction, tensor network
expressibility, holographic), #82-84 (geometry of TN manifolds, sign
problems, optimal contraction order).

**How Techne picks this up:**
  1. Build primitive in `sigma_kernel/tensor_network.py` (suggested
     module path).
  2. Remove module-level `skipif` when import succeeds.
  3. Tests should pass without modification.

**Cross-tier interactions:**
- Tier A (CoordinateChart) — TensorNetwork EXTENDS this; legacy
  CoordinateChart usages should remain valid (substrate v2.3 §6.2 P0)
- Tier B (ConstructiveExistenceWitness) — ContractionOrderWitness
  subtype (fire #39) verifies optimal contraction-order claims
- Tier C (MomentPolytope) — TensorNetwork → σ_r projection (fire #58
  TestTierATierCComposition)
- Tier D (GenericityAlmostEverywhereCert) — random tensor networks
  with measure-zero exception loci

**Sister files:**
  - test_constructive_existence_witness_stub.py (fire #47, Tier B)
  - test_distribution_object_stub.py (fire #48, Tier D)
  - test_moment_polytope_stub.py (fire #58, Tier C)

**Source ticket:** T-2026-05-09-ST-fire59-001 (Techne; Tier A++ meta-
primitive test-suite stub).
"""
from __future__ import annotations

import pytest

# Module-level skip until Techne lands the Tier A++ meta-primitive.
try:
    from sigma_kernel.tensor_network import (  # type: ignore[import-not-found]
        TensorNetwork,
        NetworkVertex,
        NetworkEdge,
        ContractionPlan,
        ContractionOrder,
        IndexLabel,
        TensorEntry,
        ContractionResult,
        TensorNetworkRegistry,
        ContractionError,
    )
    _PRIMITIVE_EXISTS = True
except ImportError:
    _PRIMITIVE_EXISTS = False

pytestmark = pytest.mark.skipif(
    not _PRIMITIVE_EXISTS,
    reason=(
        "Tier A++ TensorNetwork meta-primitive not yet implemented. "
        "See pivot/restart_decisions_2026-05-09.md (decision 2 — meta-"
        "primitive 1 of 5: extends CoordinateChart) and source fires "
        "#38/#39/#40/#41 (component primitives bundled here)."
    ),
)


# =============================================================================
# Construction / topology contract
# =============================================================================


class TestTensorNetworkConstruction:
    """Basic construction + topology invariants."""

    def test_empty_network(self):
        """An empty TensorNetwork is constructible (zero vertices, zero
        edges) and round-trips through registration."""
        tn = TensorNetwork.empty()
        assert len(tn.vertices) == 0
        assert len(tn.edges) == 0

    def test_single_vertex_network(self):
        """A 1-vertex network (a single tensor T) carries T's entries +
        its index labels as half-edges."""
        tn = TensorNetwork.from_single_tensor(
            tensor_id="A",
            shape=(3, 3),
            index_labels=("i", "j"),
        )
        assert len(tn.vertices) == 1
        assert tn.vertices["A"].shape == (3, 3)

    def test_two_vertex_network_with_shared_edge(self):
        """A 2-vertex network where A and B share index 'k' has one
        contractible edge."""
        tn = TensorNetwork.from_specs([
            {"id": "A", "shape": (3, 5), "labels": ("i", "k")},
            {"id": "B", "shape": (5, 3), "labels": ("k", "j")},
        ])
        assert len(tn.vertices) == 2
        assert len(tn.edges) == 1
        assert tn.edges[0].shared_label == "k"

    def test_topology_invariants_dimension_consistency(self):
        """An edge between two vertices with mismatched dimensions on
        the shared index must raise at construction."""
        with pytest.raises((ValueError, ContractionError)):
            TensorNetwork.from_specs([
                {"id": "A", "shape": (3, 5), "labels": ("i", "k")},
                {"id": "B", "shape": (7, 3), "labels": ("k", "j")},  # k=7, A says k=5
            ])

    def test_content_addressed_network_id(self):
        """Two structurally identical networks have equal IDs."""
        spec = [
            {"id": "A", "shape": (3, 5), "labels": ("i", "k")},
            {"id": "B", "shape": (5, 3), "labels": ("k", "j")},
        ]
        tn1 = TensorNetwork.from_specs(spec)
        tn2 = TensorNetwork.from_specs(spec)
        assert tn1.network_id == tn2.network_id


# =============================================================================
# Contraction operation contract
# =============================================================================


class TestContractionOperation:
    """The core operation: contract one or more edges."""

    def test_full_contraction_returns_scalar(self):
        """Contracting every edge of a fully-connected network with no
        free indices yields a scalar."""
        tn = _make_scalar_yielding_network()
        result = tn.contract_all()
        assert isinstance(result, ContractionResult)
        assert result.is_scalar is True

    def test_partial_contraction_returns_smaller_network(self):
        """Contracting one edge of a 3-vertex network yields a
        2-vertex network (or 1 + smaller, depending on topology)."""
        tn = _make_3_vertex_chain()
        partial = tn.contract_edge(tn.edges[0].edge_id)
        assert isinstance(partial, TensorNetwork)
        assert len(partial.vertices) < len(tn.vertices)

    def test_associativity_under_order_swap(self):
        """For a 3-vertex network A-B-C with two edges (A-B) + (B-C),
        contracting (A,B) first then C must equal contracting (B,C)
        first then A (modulo numerical tolerance). This is what makes
        ContractionOrder optimization meaningful."""
        tn = _make_3_vertex_chain()
        order_1 = ContractionOrder.from_sequence([
            tn.edges[0].edge_id, tn.edges[1].edge_id,
        ])
        order_2 = ContractionOrder.from_sequence([
            tn.edges[1].edge_id, tn.edges[0].edge_id,
        ])
        r1 = tn.contract_via(order_1)
        r2 = tn.contract_via(order_2)
        assert r1.equals_within(r2, tol=1e-9)


# =============================================================================
# CoordinateChart extension contract (Tier A++)
# =============================================================================


class TestCoordinateChartExtension:
    """TensorNetwork EXTENDS CoordinateChart per Aporia's "Tier A++"
    framing. Legacy CoordinateChart usage must remain valid;
    TensorNetwork adds index-contraction structure on top."""

    def test_tensor_network_is_a_coordinate_chart(self):
        """A TensorNetwork is-a CoordinateChart (subtype / interface)."""
        from sigma_kernel.coordinate_chart import CoordinateChart
        tn = _make_scalar_yielding_network()
        assert isinstance(tn, CoordinateChart) or hasattr(tn, "as_coordinate_chart")

    def test_chart_metadata_preserved(self):
        """When a TensorNetwork is registered, its CoordinateChart
        metadata (domain, region_key, coordinate_system) is exposed."""
        tn = _make_scalar_yielding_network()
        chart_view = tn.as_coordinate_chart() if hasattr(tn, "as_coordinate_chart") else tn
        assert chart_view.domain is not None
        assert chart_view.region_key is not None


# =============================================================================
# Group-action sub-component (was GroupAction in fire #40)
# =============================================================================


class TestGroupActionOnNetwork:
    """When a TensorNetwork has GL-symmetry (e.g. matrix-multiplication
    tensor M⟨n⟩), the group action is carried as substrate-grade data."""

    def test_action_preserves_contraction_value(self):
        """For a network with GL-symmetry, applying any group element
        to all vertices must leave the full-contraction value unchanged."""
        tn = _make_GL_symmetric_network()
        original_value = tn.contract_all().scalar_value
        permuted = tn.apply_group_action(_random_GL_element(tn))
        permuted_value = permuted.contract_all().scalar_value
        assert abs(complex(original_value) - complex(permuted_value)) < 1e-9


# =============================================================================
# Tier B / Tier A composition: ContractionOrderWitness verification
# =============================================================================


class TestTierATierBComposition:
    """ContractionOrderWitness (Tier B subtype #2 from fire #39)
    verifies optimal contraction-order claims AGAINST a TensorNetwork
    instance."""

    def test_witness_validates_against_network(self):
        """A ContractionOrderWitness carries (network_id, order, cost).
        Validation reproduces the cost on the network and matches."""
        try:
            from sigma_kernel.constructive_existence_witness import (  # type: ignore[import-not-found]
                ContractionOrderWitness,
            )
        except ImportError:
            pytest.skip("Tier B not yet implemented")
        tn = _make_3_vertex_chain()
        witness = ContractionOrderWitness.for_network(
            network=tn, order_sequence=tn.edges,
        )
        assert witness.verify_against(tn) is True


# =============================================================================
# Catalog coverage smoke (per Aporia: P30, catalog #49-51, #75-78, #82-84)
# =============================================================================


class TestCatalogCoverageSmoke:
    """Aporia's framing: TensorNetwork covers attack paradigm P30 +
    specific catalog entries. Smoke-test that the primitive shape can
    represent each."""

    def test_can_represent_TT_format_chain(self):
        """Tensor-train decomposition (#49) is a chain of order-3
        tensors. TensorNetwork must represent."""
        tt = TensorNetwork.tensor_train(
            site_shapes=[(1, 3, 5), (5, 3, 5), (5, 3, 1)],
        )
        assert len(tt.vertices) == 3

    def test_can_represent_PEPS_grid(self):
        """PEPS = 2D tensor network (#76). Smoke: 2x2 grid is constructible."""
        peps = TensorNetwork.peps_grid(rows=2, cols=2, bond_dim=3, physical_dim=2)
        assert len(peps.vertices) == 4

    def test_can_represent_matrix_multiplication_tensor(self):
        """M⟨3⟩ from catalog #4 (fire #38 origin). The matrix-mult tensor
        is a specific 3-vertex network with shared traces."""
        m3 = TensorNetwork.matrix_multiplication_tensor(n=3)
        assert m3.matrix_size == 3


# =============================================================================
# Helper builders (Techne wires when primitive lands)
# =============================================================================


def _make_scalar_yielding_network():
    """A small fully-contracted-to-scalar network for testing
    contract_all() etc."""
    raise NotImplementedError("primitive not yet built")


def _make_3_vertex_chain():
    """A-B-C linear chain: shape((3,5)) - shape((5,4)) - shape((4,3))."""
    raise NotImplementedError("primitive not yet built")


def _make_GL_symmetric_network():
    """A network with GL-symmetric structure (e.g. M⟨2⟩)."""
    raise NotImplementedError("primitive not yet built")


def _random_GL_element(tn):
    """A random invertible matrix appropriate for the network's
    group-action structure."""
    raise NotImplementedError("primitive not yet built")
