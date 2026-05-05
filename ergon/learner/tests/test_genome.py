"""Tests for ergon.learner.genome — DAG genomes over arsenal atoms."""
from __future__ import annotations

import pytest

from ergon.learner.genome import (
    Genome,
    GenomeValidationError,
    MAX_DEPTH,
    MAX_WIDTH,
    NodeRef,
    validate_dag_invariants,
)


# ---------------------------------------------------------------------------
# Helpers — canonical small genomes for testing
# ---------------------------------------------------------------------------


def make_simple_chain_genome() -> Genome:
    """A 3-node chain: node0 -> node1 -> node2."""
    return Genome(
        nodes=(
            NodeRef(
                callable_ref="prometheus_math.numerics_special_dilogarithm:dilogarithm",
                arg_bindings=(("literal", 0.5),),
            ),
            NodeRef(
                callable_ref="prometheus_math.numerics_special_dilogarithm:polylogarithm",
                arg_bindings=(("literal", 2), ("ref", 0)),
            ),
            NodeRef(
                callable_ref="prometheus_math.number_theory:hecke_eigenvalue",
                arg_bindings=(("ref", 1),),
            ),
        ),
        target_predicate="test predicate",
        mutation_operator_class="structural",
    )


def make_branching_dag_genome() -> Genome:
    """A 4-node DAG: nodes 0, 1 are sources; node 2 references both; node 3 references node 2."""
    return Genome(
        nodes=(
            NodeRef(
                callable_ref="atom_0",
                arg_bindings=(("literal", 1),),
            ),
            NodeRef(
                callable_ref="atom_1",
                arg_bindings=(("literal", 2),),
            ),
            NodeRef(
                callable_ref="atom_2_combiner",
                arg_bindings=(("ref", 0), ("ref", 1)),
            ),
            NodeRef(
                callable_ref="atom_3_root",
                arg_bindings=(("ref", 2),),
            ),
        ),
        target_predicate="test predicate",
        mutation_operator_class="symbolic",
    )


# ---------------------------------------------------------------------------
# Authority — content-hash determinism (the load-bearing genome property)
# ---------------------------------------------------------------------------


def test_content_hash_deterministic():
    """Same genome content produces same hash."""
    g1 = make_simple_chain_genome()
    g2 = make_simple_chain_genome()
    assert g1.content_hash() == g2.content_hash()


def test_content_hash_excludes_parent():
    """parent_hash is excluded from content_hash — two genomes with different
    parents but same content are the same individual."""
    g1 = make_simple_chain_genome()
    g2 = Genome(
        nodes=g1.nodes,
        target_predicate=g1.target_predicate,
        mutation_operator_class=g1.mutation_operator_class,
        parent_hash="some_other_parent_hash",
    )
    assert g1.content_hash() == g2.content_hash()


def test_content_hash_excludes_metadata():
    """metadata is mutable runtime data; excluded from content_hash."""
    g1 = make_simple_chain_genome()
    g2 = Genome(
        nodes=g1.nodes,
        target_predicate=g1.target_predicate,
        mutation_operator_class=g1.mutation_operator_class,
        metadata={"runtime_note": "this changes during search"},
    )
    assert g1.content_hash() == g2.content_hash()


def test_content_hash_includes_operator_class():
    """Same DAG produced by different operator classes are tagged differently."""
    g1 = make_simple_chain_genome()  # operator_class = "structural"
    g2 = Genome(
        nodes=g1.nodes,
        target_predicate=g1.target_predicate,
        mutation_operator_class="uniform",
    )
    # Lineage tagging means same DAG via different operator -> different individual
    assert g1.content_hash() != g2.content_hash()


def test_content_hash_includes_target_predicate():
    """Different target predicates = different individuals (even if DAG identical)."""
    g1 = make_simple_chain_genome()
    g2 = Genome(
        nodes=g1.nodes,
        target_predicate="different predicate",
        mutation_operator_class=g1.mutation_operator_class,
    )
    assert g1.content_hash() != g2.content_hash()


# ---------------------------------------------------------------------------
# Property — depth / width / n_atoms
# ---------------------------------------------------------------------------


def test_chain_depth():
    """3-node chain has depth 2 (node0 -> node1 -> node2)."""
    g = make_simple_chain_genome()
    assert g.depth() == 2


def test_chain_width():
    """3-node chain has width 1 (one node per depth level)."""
    g = make_simple_chain_genome()
    assert g.width() == 1


def test_branching_dag_depth():
    """4-node DAG: nodes 0,1 at depth 0; node 2 at depth 1; node 3 at depth 2 -> depth 2."""
    g = make_branching_dag_genome()
    assert g.depth() == 2


def test_branching_dag_width():
    """4-node DAG: depth-0 has 2 nodes (the maximum width)."""
    g = make_branching_dag_genome()
    assert g.width() == 2


def test_n_atoms():
    """n_atoms is just the number of nodes."""
    g = make_simple_chain_genome()
    assert g.n_atoms() == 3
    g2 = make_branching_dag_genome()
    assert g2.n_atoms() == 4


def test_root_node():
    """Root node is the last (highest-indexed) node."""
    g = make_simple_chain_genome()
    assert g.root_node().callable_ref.endswith(":hecke_eigenvalue")


def test_edges_computed():
    """Edges are derived from arg_bindings."""
    g = make_simple_chain_genome()
    edges = g.edges()
    # Chain: (0,1), (1,2)
    assert (0, 1) in edges
    assert (1, 2) in edges
    assert len(edges) == 2


def test_branching_edges():
    """Branching DAG edges: (0,2), (1,2), (2,3)."""
    g = make_branching_dag_genome()
    edges = set(g.edges())
    assert edges == {(0, 2), (1, 2), (2, 3)}


# ---------------------------------------------------------------------------
# Edge — DAG invariant violation
# ---------------------------------------------------------------------------


def test_dag_invariant_forward_reference_rejected():
    """A node referencing a higher-indexed node would create a cycle."""
    bad_genome = Genome(
        nodes=(
            NodeRef(
                callable_ref="atom_0",
                arg_bindings=(("ref", 1),),  # forward ref!
            ),
            NodeRef(
                callable_ref="atom_1",
                arg_bindings=(("literal", 1),),
            ),
        ),
        target_predicate="test",
        mutation_operator_class="structural",
    )
    with pytest.raises(GenomeValidationError):
        validate_dag_invariants(bad_genome)


def test_dag_invariant_self_reference_rejected():
    """A node referencing itself would create a cycle."""
    bad_genome = Genome(
        nodes=(
            NodeRef(
                callable_ref="atom_0",
                arg_bindings=(("ref", 0),),  # self-ref!
            ),
        ),
        target_predicate="test",
        mutation_operator_class="structural",
    )
    with pytest.raises(GenomeValidationError):
        validate_dag_invariants(bad_genome)


def test_dag_invariant_negative_index_rejected():
    """Negative ref index is invalid."""
    bad_genome = Genome(
        nodes=(
            NodeRef(
                callable_ref="atom_0",
                arg_bindings=(("ref", -1),),
            ),
        ),
        target_predicate="test",
        mutation_operator_class="structural",
    )
    with pytest.raises(GenomeValidationError):
        validate_dag_invariants(bad_genome)


def test_valid_dag_passes_invariants():
    """Well-formed DAG validates cleanly."""
    g = make_branching_dag_genome()
    validate_dag_invariants(g)  # no raise


# ---------------------------------------------------------------------------
# Composition — serialization roundtrip
# ---------------------------------------------------------------------------


def test_to_dict_from_dict_roundtrip():
    """Genome roundtrips through to_dict / from_dict losslessly."""
    g1 = make_simple_chain_genome()
    d = g1.to_dict()
    g2 = Genome.from_dict(d)
    assert g1.content_hash() == g2.content_hash()
    assert g1 == g2


def test_to_dict_roundtrip_preserves_parent_hash():
    """parent_hash survives roundtrip (even though excluded from content hash)."""
    g1 = Genome(
        nodes=make_simple_chain_genome().nodes,
        target_predicate="test",
        mutation_operator_class="structural",
        parent_hash="parent_abc123",
    )
    d = g1.to_dict()
    g2 = Genome.from_dict(d)
    assert g2.parent_hash == "parent_abc123"


def test_to_dict_includes_content_hash():
    """to_dict embeds content_hash as a denormalization for downstream lookups."""
    g = make_simple_chain_genome()
    d = g.to_dict()
    assert d["content_hash"] == g.content_hash()


# ---------------------------------------------------------------------------
# Composition — empty genome edge cases
# ---------------------------------------------------------------------------


def test_empty_genome_has_zero_depth_width_atoms():
    """Empty genome edge case (used as initial state before first mutation)."""
    g = Genome(
        nodes=(),
        target_predicate="empty",
        mutation_operator_class="uniform",
    )
    assert g.n_atoms() == 0
    assert g.depth() == 0
    assert g.width() == 0
    assert g.root_node() is None
    assert g.edges() == ()


def test_constants_match_v8_targets():
    """v8 §6.1 specifies target depth <=8 and target width <=5."""
    assert MAX_DEPTH == 8
    assert MAX_WIDTH == 5
