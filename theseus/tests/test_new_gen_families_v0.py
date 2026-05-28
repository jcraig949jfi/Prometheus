"""Stage 1 TDD tests for the 5 new monoculture-breaking gen families.

Plan: pivot/techne_5gen_plan_2026-05-27.md

Each gen gets 5 tests in this order (failing → passing as
implementation lands):
  1. Class imports without error
  2. Instantiates with a batch_id
  3. .next() emits at least one TheseusRecord on at least one of the
     first 100 calls (not None forever)
  4. Emitted record has the EXPECTED NEW claim_kind (not in the
     5 high-frequency old shapes from Fire #121 triage)
  5. Emitted record's role classification is DISCOVERY

These tests are written BEFORE implementation. Running this module
now should fail with ImportError on the five new generators —
that's the red. As each gen is implemented, its 5 tests turn
green. Coverage goal: 25/25 green at end of Stage 6.
"""
from __future__ import annotations

import pytest

from theseus.emit.record_schema import TheseusRecord
from theseus.generators.base import GeneratorRole


# The 5 high-frequency old shapes per Fire #121 triage. New gens must
# emit something OUTSIDE this set to be considered shape-novel.
OLD_HIGH_FREQ_KINDS = {
    "invariant_equality",
    "kill_neighborhood",
    "symmetry_transform",
    "operator_rotation",
    "composition_test",
}


def _exercise_next(gen, max_calls=100):
    """Drive next() up to max_calls; return first record or None."""
    for _ in range(max_calls):
        r = gen.next()
        if r is not None:
            return r
    return None


# =============================================================================
# k1 — typed bridge
# =============================================================================

def test_k1_imports():
    from theseus.generators.k1_typed_bridge import K1TypedBridgeGenerator
    assert K1TypedBridgeGenerator is not None


def test_k1_instantiates():
    from theseus.generators.k1_typed_bridge import K1TypedBridgeGenerator
    g = K1TypedBridgeGenerator(batch_id="test-k1")
    assert g.generator_id == "k1"


def test_k1_emits_record():
    from theseus.generators.k1_typed_bridge import K1TypedBridgeGenerator
    g = K1TypedBridgeGenerator(batch_id="test-k1")
    rec = _exercise_next(g)
    assert isinstance(rec, TheseusRecord)


def test_k1_claim_shape_is_typed_bridge():
    from theseus.generators.k1_typed_bridge import K1TypedBridgeGenerator
    g = K1TypedBridgeGenerator(batch_id="test-k1")
    rec = _exercise_next(g)
    assert rec is not None
    assert rec.claim_kind == "typed_bridge"
    assert rec.claim_kind not in OLD_HIGH_FREQ_KINDS


def test_k1_role_is_discovery():
    from theseus.generators.k1_typed_bridge import K1TypedBridgeGenerator
    assert K1TypedBridgeGenerator.role == GeneratorRole.DISCOVERY


# =============================================================================
# l1 — obstruction (negative-existential)
# =============================================================================

def test_l1_imports():
    from theseus.generators.l1_obstruction import L1ObstructionGenerator
    assert L1ObstructionGenerator is not None


def test_l1_instantiates():
    from theseus.generators.l1_obstruction import L1ObstructionGenerator
    g = L1ObstructionGenerator(batch_id="test-l1")
    assert g.generator_id == "l1"


def test_l1_emits_record():
    from theseus.generators.l1_obstruction import L1ObstructionGenerator
    g = L1ObstructionGenerator(batch_id="test-l1")
    rec = _exercise_next(g)
    assert isinstance(rec, TheseusRecord)


def test_l1_claim_shape_is_obstruction():
    from theseus.generators.l1_obstruction import L1ObstructionGenerator
    g = L1ObstructionGenerator(batch_id="test-l1")
    rec = _exercise_next(g)
    assert rec is not None
    assert rec.claim_kind == "obstruction"
    assert rec.claim_kind not in OLD_HIGH_FREQ_KINDS


def test_l1_role_is_discovery():
    from theseus.generators.l1_obstruction import L1ObstructionGenerator
    assert L1ObstructionGenerator.role == GeneratorRole.DISCOVERY


# =============================================================================
# m1 — minimal counterexample
# =============================================================================

def test_m1_imports():
    from theseus.generators.m1_minimal_counterexample import (
        M1MinimalCounterexampleGenerator,
    )
    assert M1MinimalCounterexampleGenerator is not None


def test_m1_instantiates():
    from theseus.generators.m1_minimal_counterexample import (
        M1MinimalCounterexampleGenerator,
    )
    g = M1MinimalCounterexampleGenerator(batch_id="test-m1")
    assert g.generator_id == "m1"


def test_m1_emits_record():
    from theseus.generators.m1_minimal_counterexample import (
        M1MinimalCounterexampleGenerator,
    )
    g = M1MinimalCounterexampleGenerator(batch_id="test-m1")
    rec = _exercise_next(g)
    assert isinstance(rec, TheseusRecord)


def test_m1_claim_shape_is_minimal_counterexample():
    from theseus.generators.m1_minimal_counterexample import (
        M1MinimalCounterexampleGenerator,
    )
    g = M1MinimalCounterexampleGenerator(batch_id="test-m1")
    rec = _exercise_next(g)
    assert rec is not None
    assert rec.claim_kind == "minimal_counterexample"
    assert rec.claim_kind not in OLD_HIGH_FREQ_KINDS


def test_m1_role_is_discovery():
    from theseus.generators.m1_minimal_counterexample import (
        M1MinimalCounterexampleGenerator,
    )
    assert M1MinimalCounterexampleGenerator.role == GeneratorRole.DISCOVERY


# =============================================================================
# n1 — active disagreement
# =============================================================================

def test_n1_imports():
    from theseus.generators.n1_active_disagreement import (
        N1ActiveDisagreementGenerator,
    )
    assert N1ActiveDisagreementGenerator is not None


def test_n1_instantiates():
    from theseus.generators.n1_active_disagreement import (
        N1ActiveDisagreementGenerator,
    )
    g = N1ActiveDisagreementGenerator(batch_id="test-n1")
    assert g.generator_id == "n1"


def test_n1_emits_record():
    from theseus.generators.n1_active_disagreement import (
        N1ActiveDisagreementGenerator,
    )
    g = N1ActiveDisagreementGenerator(batch_id="test-n1")
    rec = _exercise_next(g)
    assert isinstance(rec, TheseusRecord)


def test_n1_claim_shape_is_verifier_disagreement():
    from theseus.generators.n1_active_disagreement import (
        N1ActiveDisagreementGenerator,
    )
    g = N1ActiveDisagreementGenerator(batch_id="test-n1")
    rec = _exercise_next(g)
    assert rec is not None
    assert rec.claim_kind == "verifier_disagreement"
    assert rec.claim_kind not in OLD_HIGH_FREQ_KINDS


def test_n1_role_is_discovery():
    from theseus.generators.n1_active_disagreement import (
        N1ActiveDisagreementGenerator,
    )
    assert N1ActiveDisagreementGenerator.role == GeneratorRole.DISCOVERY


# =============================================================================
# o1 — conjecture neighborhood
# =============================================================================

def test_o1_imports():
    from theseus.generators.o1_conjecture_neighborhood import (
        O1ConjectureNeighborhoodGenerator,
    )
    assert O1ConjectureNeighborhoodGenerator is not None


def test_o1_instantiates():
    from theseus.generators.o1_conjecture_neighborhood import (
        O1ConjectureNeighborhoodGenerator,
    )
    g = O1ConjectureNeighborhoodGenerator(batch_id="test-o1")
    assert g.generator_id == "o1"


def test_o1_emits_record():
    from theseus.generators.o1_conjecture_neighborhood import (
        O1ConjectureNeighborhoodGenerator,
    )
    g = O1ConjectureNeighborhoodGenerator(batch_id="test-o1")
    rec = _exercise_next(g)
    assert isinstance(rec, TheseusRecord)


def test_o1_claim_shape_is_conjecture_neighborhood():
    from theseus.generators.o1_conjecture_neighborhood import (
        O1ConjectureNeighborhoodGenerator,
    )
    g = O1ConjectureNeighborhoodGenerator(batch_id="test-o1")
    rec = _exercise_next(g)
    assert rec is not None
    assert rec.claim_kind == "conjecture_neighborhood"
    assert rec.claim_kind not in OLD_HIGH_FREQ_KINDS


def test_o1_role_is_discovery():
    from theseus.generators.o1_conjecture_neighborhood import (
        O1ConjectureNeighborhoodGenerator,
    )
    assert O1ConjectureNeighborhoodGenerator.role == GeneratorRole.DISCOVERY


# =============================================================================
# Cross-cutting: all 5 emit DISTINCT claim_kinds
# =============================================================================

def test_all_five_emit_distinct_kinds():
    """No two new gens collapse onto the same claim_kind."""
    from theseus.generators.k1_typed_bridge import K1TypedBridgeGenerator
    from theseus.generators.l1_obstruction import L1ObstructionGenerator
    from theseus.generators.m1_minimal_counterexample import (
        M1MinimalCounterexampleGenerator,
    )
    from theseus.generators.n1_active_disagreement import (
        N1ActiveDisagreementGenerator,
    )
    from theseus.generators.o1_conjecture_neighborhood import (
        O1ConjectureNeighborhoodGenerator,
    )
    kinds = set()
    for cls in (
        K1TypedBridgeGenerator,
        L1ObstructionGenerator,
        M1MinimalCounterexampleGenerator,
        N1ActiveDisagreementGenerator,
        O1ConjectureNeighborhoodGenerator,
    ):
        rec = _exercise_next(cls(batch_id=f"test-{cls.generator_id}"))
        assert rec is not None, f"{cls.generator_id} emitted None for 100 calls"
        kinds.add(rec.claim_kind)
    assert len(kinds) == 5, f"Expected 5 distinct kinds, got {len(kinds)}: {kinds}"
