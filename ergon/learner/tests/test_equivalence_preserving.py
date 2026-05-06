"""Tests for ergon.learner.operators.equivalence_preserving — W2.7 spike.

Per pivot/ergon_learner_v0.5_design_2026-05-05.md §3.4 W2.7:

    "Operator generates 100 child genomes from 10 EC parents without
     crash; mutations preserve EC isomorphism class invariants per
     arsenal `equivalence_class` tag"

The arsenal-level invariant for elliptic curves is the *isogeny class*
(LMFDB ec_curvedata `lmfdb_iso` field; arsenal equivalence_class
`variety_fingerprint`). j-invariant changes across non-trivial isogenies
— the test verifies isogeny-class preservation, which is the actual
LMFDB-level invariant the canonicalizer enforces.
"""
from __future__ import annotations

import random

import pytest

from ergon.learner.genome import Genome, NodeRef, validate_dag_invariants
from ergon.learner.operators.base import (
    fresh_genome,
    make_mvp_atom_pool,
    sample_arg,
)
from ergon.learner.operators.equivalence_preserving import (
    EquivalencePreservingOperator,
    _FALLBACK_ISOGENY_CLASSES,
    _is_ec_label_literal,
    _isogeny_class_of,
    _siblings_in_class,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def atom_pool():
    return make_mvp_atom_pool()


@pytest.fixture
def rng():
    return random.Random(20260505)


def make_ec_parent(label: str, atom_pool: dict) -> Genome:
    """Build a parent genome whose root is an isogeny_class call on `label`."""
    return Genome(
        nodes=(
            NodeRef(
                callable_ref="prometheus_math.elliptic_curves:isogeny_class",
                arg_bindings=(("literal", label),),
            ),
        ),
        target_predicate="EC isogeny class lookup",
        mutation_operator_class="structural",  # parent's lineage
    )


# Ten EC parents, drawn from the canonical small-conductor classes the
# fallback table covers (and that LMFDB / Cremona both mirror). Mix of
# multi-curve classes (11.a*, 14.a*, 15.a*, 17.a*, 19.a*, 26.a*, 26.b*,
# 33.a*, 37.b*, 38.a*) — singletons (37.a1, 389.a1, 5077.a1) deliberately
# excluded so we exercise the sibling-pick path, not the fresh fallback.
_TEN_EC_PARENT_LABELS = [
    "11.a1", "11.a2", "14.a1", "15.a1", "17.a1",
    "19.a1", "26.a1", "26.b1", "33.a2", "37.b1",
]


# ---------------------------------------------------------------------------
# Authority — operator class lineage tag
# ---------------------------------------------------------------------------


def test_operator_class_tag():
    assert EquivalencePreservingOperator.operator_class == "equivalence_preserving"


def test_instance_tag():
    """v0.5 ships exactly one instance: isogeny-on-EC."""
    assert EquivalencePreservingOperator.instance == "isogeny_on_ec"


# ---------------------------------------------------------------------------
# Property — helper functions behave as documented
# ---------------------------------------------------------------------------


def test_isogeny_class_of_lmfdb_label():
    assert _isogeny_class_of("11.a1") == "11.a"
    assert _isogeny_class_of("389.a1") == "389.a"
    assert _isogeny_class_of("5077.a1") == "5077.a"


def test_isogeny_class_of_cremona_label():
    assert _isogeny_class_of("11a1") == "11.a"
    assert _isogeny_class_of("37b3") == "37.b"


def test_isogeny_class_of_invalid_label():
    assert _isogeny_class_of("not-a-label") is None
    assert _isogeny_class_of("") is None


def test_is_ec_label_literal_recognizes_both_styles():
    assert _is_ec_label_literal("11.a1")
    assert _is_ec_label_literal("11a1")
    assert not _is_ec_label_literal("foo")
    assert not _is_ec_label_literal(42)
    assert not _is_ec_label_literal(None)


def test_siblings_in_class_returns_class_members():
    siblings = _siblings_in_class("11.a1")
    assert "11.a1" in siblings
    assert "11.a2" in siblings
    assert "11.a3" in siblings


def test_siblings_in_class_singleton():
    siblings = _siblings_in_class("389.a1")
    # Singleton class — siblings tuple is just the curve itself.
    assert siblings == ("389.a1",)


def test_fallback_table_covers_canonical_labels():
    """Every label in `sample_arg('ec_label')` must have a fallback entry."""
    for _ in range(20):
        rng = random.Random(_)
        label = sample_arg("ec_label", rng)
        cls = _isogeny_class_of(label)
        assert cls is not None, f"Could not parse class from {label}"
        assert cls in _FALLBACK_ISOGENY_CLASSES, \
            f"Sampler emits {label} but fallback table missing class {cls}"


# ---------------------------------------------------------------------------
# Property — mutate() produces a valid genome with correct lineage
# ---------------------------------------------------------------------------


def test_mutate_produces_valid_genome(atom_pool, rng):
    parent = make_ec_parent("11.a1", atom_pool)
    op = EquivalencePreservingOperator()
    child = op.mutate(parent, rng, atom_pool)
    validate_dag_invariants(child)
    assert child.mutation_operator_class == "equivalence_preserving"


def test_mutate_sets_parent_hash(atom_pool, rng):
    parent = make_ec_parent("14.a1", atom_pool)
    op = EquivalencePreservingOperator()
    child = op.mutate(parent, rng, atom_pool)
    assert child.parent_hash == parent.content_hash()


def test_mutate_records_equivalence_move_metadata(atom_pool, rng):
    parent = make_ec_parent("11.a1", atom_pool)
    op = EquivalencePreservingOperator()
    child = op.mutate(parent, rng, atom_pool)
    move = child.metadata.get("equivalence_move")
    assert move is not None
    assert move["instance"] == "isogeny_on_ec"
    assert move["from_label"] == "11.a1"
    assert move["to_label"] in ("11.a2", "11.a3")
    assert move["isogeny_class"] == "11.a"


# ---------------------------------------------------------------------------
# Edge — empty / single-node parent / no-EC parent
# ---------------------------------------------------------------------------


def test_mutate_empty_parent_returns_fresh(atom_pool, rng):
    op = EquivalencePreservingOperator()
    child = op.mutate(None, rng, atom_pool)
    assert len(child.nodes) >= 1
    assert child.mutation_operator_class == "equivalence_preserving"


def test_mutate_no_ec_label_parent_falls_back_to_fresh(atom_pool, rng):
    """Parent without any EC-label literal -> fall back to fresh, still tagged."""
    parent = Genome(
        nodes=(
            NodeRef(
                callable_ref="prometheus_math.number_theory:euler_phi",
                arg_bindings=(("literal", 42),),
            ),
        ),
        target_predicate="no EC here",
        mutation_operator_class="structural",
    )
    op = EquivalencePreservingOperator()
    child = op.mutate(parent, rng, atom_pool)
    assert child.mutation_operator_class == "equivalence_preserving"
    validate_dag_invariants(child)


def test_mutate_singleton_class_falls_back_to_fresh(atom_pool, rng):
    """Singleton isogeny class (e.g. 389.a1) has no non-self siblings ->
    fall back to fresh rather than emit a no-op."""
    parent = make_ec_parent("389.a1", atom_pool)
    op = EquivalencePreservingOperator(allow_self_swap=False)
    child = op.mutate(parent, rng, atom_pool)
    # Falls back to fresh — child differs from parent in content.
    assert child.mutation_operator_class == "equivalence_preserving"
    assert child.content_hash() != parent.content_hash()


# ---------------------------------------------------------------------------
# W2.7 acceptance criterion — 100 children from 10 parents
# ---------------------------------------------------------------------------


def test_w27_acceptance_100_children_10_parents(atom_pool):
    """W2.7 acceptance: 100 child genomes from 10 EC parents.

    - No crashes during mutation.
    - Every child carries `mutation_operator_class="equivalence_preserving"`.
    - Every successful sibling-swap preserves the isogeny class
      (LMFDB-level arsenal `variety_fingerprint` invariant).
    """
    op = EquivalencePreservingOperator()
    rng = random.Random(20260505)

    parents = [make_ec_parent(lbl, atom_pool) for lbl in _TEN_EC_PARENT_LABELS]
    assert len(parents) == 10

    n_children = 100
    children: list[Genome] = []
    for i in range(n_children):
        parent = parents[i % 10]
        child = op.mutate(parent, rng, atom_pool)
        children.append(child)

    # No crashes -> reaching here is sufficient.
    assert len(children) == n_children

    # Every child has the lineage tag.
    for c in children:
        assert c.mutation_operator_class == "equivalence_preserving", (
            f"Child missing lineage tag: {c}"
        )

    # Isogeny-class preservation: for every child whose mutation went
    # through the sibling-swap path (recorded in metadata), the from/to
    # labels share an isogeny class.
    n_isogeny_swaps = 0
    n_invariant_preserved = 0
    for c in children:
        move = c.metadata.get("equivalence_move")
        if move is None:
            continue
        n_isogeny_swaps += 1
        from_cls = _isogeny_class_of(move["from_label"])
        to_cls = _isogeny_class_of(move["to_label"])
        assert from_cls == to_cls, (
            f"Isogeny class not preserved: {move['from_label']} ({from_cls}) "
            f"-> {move['to_label']} ({to_cls})"
        )
        assert from_cls == move["isogeny_class"]
        n_invariant_preserved += 1

    # All 10 parents are non-singleton classes — every child should have
    # gone through the sibling-swap path.
    assert n_isogeny_swaps == n_children, (
        f"Expected all {n_children} children to be sibling-swaps; got "
        f"{n_isogeny_swaps}"
    )
    assert n_invariant_preserved == n_isogeny_swaps


def test_w27_children_differ_from_parent(atom_pool):
    """Sibling-swap should produce a distinct child (not a content-hash
    no-op) for every non-singleton parent."""
    op = EquivalencePreservingOperator()
    rng = random.Random(0)
    for label in _TEN_EC_PARENT_LABELS:
        parent = make_ec_parent(label, atom_pool)
        for _ in range(5):
            child = op.mutate(parent, rng, atom_pool)
            assert child.content_hash() != parent.content_hash(), (
                f"Child hash collides with parent for {label}; "
                f"child label={child.metadata.get('equivalence_move')}"
            )
