"""Tests for ergon.learner.operators — five mutation operator classes."""
from __future__ import annotations

import random
from typing import Counter

import pytest

from ergon.learner.genome import Genome, NodeRef, validate_dag_invariants
from ergon.learner.operators.anti_prior import (
    AntiPriorOperator,
    DEFAULT_CORPUS_FREQUENCIES,
    KL_DIVERGENCE_THRESHOLD,
    compute_genome_atom_frequencies,
    kl_divergence,
)
from ergon.learner.operators.base import (
    fresh_genome,
    make_mvp_atom_pool,
    sample_arg,
)
from ergon.learner.operators.structural import StructuralOperator
from ergon.learner.operators.structured_null import StructuredNullOperator
from ergon.learner.operators.symbolic import SymbolicOperator
from ergon.learner.operators.uniform import UniformOperator


@pytest.fixture
def atom_pool():
    return make_mvp_atom_pool()


@pytest.fixture
def rng():
    return random.Random(42)


def make_simple_parent(atom_pool, rng) -> Genome:
    """Helper: a small valid genome to use as mutation parent."""
    return fresh_genome(atom_pool, rng, "structural", n_atoms=3)


# ===========================================================================
# Authority — operator class lineage tags match v8 specification
# ===========================================================================


def test_structural_operator_class_tag():
    assert StructuralOperator.operator_class == "structural"


def test_symbolic_operator_class_tag():
    assert SymbolicOperator.operator_class == "symbolic"


def test_uniform_operator_class_tag():
    assert UniformOperator.operator_class == "uniform"


def test_structured_null_operator_class_tag():
    assert StructuredNullOperator.operator_class == "structured_null"


def test_anti_prior_operator_class_tag():
    assert AntiPriorOperator.operator_class == "anti_prior"


def test_atom_pool_size():
    """MVP atom pool has 12 atoms across categories."""
    pool = make_mvp_atom_pool()
    assert len(pool) == 12


# ===========================================================================
# Property — every operator produces a valid genome with correct lineage tag
# ===========================================================================


def test_structural_produces_valid_genome(atom_pool, rng):
    parent = make_simple_parent(atom_pool, rng)
    op = StructuralOperator()
    child = op.mutate(parent, rng, atom_pool)
    validate_dag_invariants(child)
    assert child.mutation_operator_class == "structural"


def test_symbolic_produces_valid_genome(atom_pool, rng):
    parent = make_simple_parent(atom_pool, rng)
    op = SymbolicOperator()
    child = op.mutate(parent, rng, atom_pool)
    validate_dag_invariants(child)
    assert child.mutation_operator_class == "symbolic"


def test_uniform_produces_valid_genome(atom_pool, rng):
    op = UniformOperator()
    child = op.mutate(None, rng, atom_pool)  # uniform ignores parent
    validate_dag_invariants(child)
    assert child.mutation_operator_class == "uniform"


def test_structured_null_produces_valid_genome(atom_pool, rng):
    op = StructuredNullOperator()
    child = op.mutate(None, rng, atom_pool)
    validate_dag_invariants(child)
    assert child.mutation_operator_class == "structured_null"


def test_anti_prior_produces_valid_genome(atom_pool, rng):
    op = AntiPriorOperator()
    child = op.mutate(None, rng, atom_pool)
    validate_dag_invariants(child)
    assert child.mutation_operator_class == "anti_prior"


def test_structural_child_has_parent_hash(atom_pool, rng):
    """Mutation operators set parent_hash for lineage tracking."""
    parent = make_simple_parent(atom_pool, rng)
    op = StructuralOperator()
    child = op.mutate(parent, rng, atom_pool)
    assert child.parent_hash == parent.content_hash()


def test_symbolic_child_has_parent_hash(atom_pool, rng):
    parent = make_simple_parent(atom_pool, rng)
    op = SymbolicOperator()
    child = op.mutate(parent, rng, atom_pool)
    assert child.parent_hash == parent.content_hash()


def test_symbolic_preserves_dag_topology(atom_pool, rng):
    """Symbolic preserves callable_refs (no atom changes), only mutates literals."""
    parent = make_simple_parent(atom_pool, rng)
    op = SymbolicOperator(mutation_rate_per_arg=1.0)  # mutate every arg
    child = op.mutate(parent, rng, atom_pool)
    # Same number of nodes and same callable_refs in the same order
    assert len(child.nodes) == len(parent.nodes)
    for parent_node, child_node in zip(parent.nodes, child.nodes):
        assert parent_node.callable_ref == child_node.callable_ref


def test_uniform_ignores_parent(atom_pool, rng):
    """Uniform's output is independent of parent — produces fresh randomness."""
    parent = make_simple_parent(atom_pool, rng)
    op = UniformOperator()
    # Call uniform twice with different parents; should produce same output structure
    rng_a = random.Random(123)
    rng_b = random.Random(123)
    child_a = op.mutate(parent, rng_a, atom_pool)
    child_b = op.mutate(None, rng_b, atom_pool)
    assert child_a.content_hash() == child_b.content_hash()


# ===========================================================================
# Property — anti_prior KL divergence semantics
# ===========================================================================


def test_kl_divergence_zero_for_identical_distributions():
    p = {"a": 0.5, "b": 0.5}
    assert kl_divergence(p, p) == pytest.approx(0.0, abs=1e-9)


def test_kl_divergence_positive_for_different_distributions():
    p = {"a": 1.0, "b": 0.0}
    q = {"a": 0.5, "b": 0.5}
    kl = kl_divergence(p, q)
    assert kl > 0.0


def test_anti_prior_prefers_low_corpus_frequency_atoms(atom_pool):
    """anti_prior should sample low-corpus-frequency atoms more often than high."""
    op = AntiPriorOperator()
    rng = random.Random(0)
    atom_counter = Counter()
    for _ in range(50):
        g = op.mutate(None, rng, atom_pool)
        for node in g.nodes:
            atom_counter[node.callable_ref] += 1

    # The high-frequency dilogarithm should be sampled LESS than the
    # low-frequency Hecke eigenvalue
    dilogarithm_count = atom_counter.get(
        "prometheus_math.numerics_special_dilogarithm:dilogarithm", 0
    )
    hecke_count = atom_counter.get(
        "prometheus_math.number_theory:hecke_eigenvalue", 0
    )
    # In DEFAULT_CORPUS_FREQUENCIES: dilogarithm=0.18, hecke=0.02 (9× higher freq)
    # Anti-prior weights are 1/freq, so hecke gets ~9× more weight than dilogarithm
    # Over 50 genomes (~150 atoms), expect hecke > dilogarithm
    assert hecke_count > dilogarithm_count


def test_anti_prior_metadata_includes_kl_divergence(atom_pool, rng):
    """Every anti_prior genome carries kl_divergence_from_corpus in metadata."""
    op = AntiPriorOperator()
    child = op.mutate(None, rng, atom_pool)
    assert "kl_divergence_from_corpus" in child.metadata


def test_anti_prior_divergence_check(atom_pool, rng):
    """divergence_check returns the operator's diagnostic on an external genome."""
    op = AntiPriorOperator()
    g = op.mutate(None, rng, atom_pool)
    result = op.divergence_check(g)
    assert "kl_divergence" in result
    assert "passes_threshold" in result
    assert result["threshold"] == KL_DIVERGENCE_THRESHOLD


# ===========================================================================
# Edge — empty parent / single-node parent / max-atoms parent
# ===========================================================================


def test_structural_empty_parent_returns_fresh(atom_pool, rng):
    """Structural with None parent falls back to fresh_genome."""
    op = StructuralOperator()
    child = op.mutate(None, rng, atom_pool)
    assert len(child.nodes) >= 1
    assert child.mutation_operator_class == "structural"


def test_symbolic_empty_parent_returns_fresh(atom_pool, rng):
    op = SymbolicOperator()
    child = op.mutate(None, rng, atom_pool)
    assert len(child.nodes) >= 1
    assert child.mutation_operator_class == "symbolic"


def test_structural_single_node_parent_can_mutate(atom_pool, rng):
    """Single-node parent: structural shouldn't try to remove the only node."""
    parent = fresh_genome(atom_pool, rng, "structural", n_atoms=1)
    op = StructuralOperator()
    child = op.mutate(parent, rng, atom_pool)
    # Child must still be valid (might have ≥1 node from add or swap)
    assert len(child.nodes) >= 1


def test_uniform_respects_n_atoms_distribution(atom_pool):
    """Uniform respects its configured n_atoms range."""
    op = UniformOperator(n_atoms_distribution=(2, 4))
    rng = random.Random(0)
    sizes = []
    for _ in range(20):
        g = op.mutate(None, rng, atom_pool)
        sizes.append(len(g.nodes))
    assert min(sizes) >= 2
    assert max(sizes) <= 4


# ===========================================================================
# Composition — multi-operator scenarios + integration with archive
# ===========================================================================


def test_chain_of_mutations_preserves_invariants(atom_pool, rng):
    """A chain of structural -> symbolic -> structural mutations preserves DAG invariants."""
    g = fresh_genome(atom_pool, rng, "structural")
    structural = StructuralOperator()
    symbolic = SymbolicOperator()
    for _ in range(5):
        g = structural.mutate(g, rng, atom_pool)
        validate_dag_invariants(g)
        g = symbolic.mutate(g, rng, atom_pool)
        validate_dag_invariants(g)


def test_all_five_operators_produce_distinct_lineage_tags(atom_pool, rng):
    """Ensure each operator class is correctly tagged so archive can attribute."""
    ops = [
        StructuralOperator(),
        SymbolicOperator(),
        UniformOperator(),
        StructuredNullOperator(),
        AntiPriorOperator(),
    ]
    parent = fresh_genome(atom_pool, rng, "structural")
    classes = set()
    for op in ops:
        child = op.mutate(parent, rng, atom_pool)
        classes.add(child.mutation_operator_class)
    assert classes == {
        "structural", "symbolic", "uniform", "structured_null", "anti_prior",
    }


def test_sample_arg_returns_correct_types():
    """sample_arg returns values matching the sampler-name's type."""
    rng = random.Random(0)
    assert isinstance(sample_arg("integer_small", rng), int)
    assert isinstance(sample_arg("real_unit_interval", rng), float)
    assert isinstance(sample_arg("complex_unit_disk", rng), tuple)
    assert isinstance(sample_arg("modular_form_label", rng), str)
    assert isinstance(sample_arg("ec_label", rng), str)
