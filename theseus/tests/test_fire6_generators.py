"""Smoke tests for Fire #6 active generators: D3 MCTS triangulation, B2 commutativity, C5 specialization."""
from __future__ import annotations

import pytest

from theseus.emit.record_schema import Verdict
from theseus.generators.d3_triangulation_seeds import (
    D3TriangulationSeedsGenerator,
)
from theseus.generators.b2_composition_test import (
    B2CompositionTestGenerator,
)
from theseus.generators.c5_specialization import (
    C5SpecializationGenerator,
    _generate_strengthenings,
)


def test_d3_bootstraps_from_a4(tmp_path):
    g = D3TriangulationSeedsGenerator(
        batch_id="t", seed=0, corpus_dir=tmp_path, n_branches=3
    )
    found = False
    for _ in range(15):
        r = g.next()
        if r is not None:
            assert r.generator_id == "d3"
            p = r.claim_payload
            assert "child_r2_values" in p
            assert "agreement_fraction" in p
            assert "triangulated_verdict" in p
            assert "D3_TRIANG" in r.canonical_claim_text
            found = True
            break
    assert found, "D3 should produce a record in 15 tries"


def test_d3_triangulated_verdict_in_valid_set(tmp_path):
    g = D3TriangulationSeedsGenerator(
        batch_id="t", seed=0, corpus_dir=tmp_path, n_branches=3
    )
    valid_verdicts = {
        Verdict.SHADOW_CATALOG.value,
        Verdict.REJECTED.value,
        Verdict.INCONCLUSIVE.value,
    }
    for _ in range(10):
        r = g.next()
        if r is not None:
            assert r.verdict in valid_verdicts


def test_b2_identity_commutes_with_all():
    """The identity operator should commute with every other operator."""
    g = B2CompositionTestGenerator(batch_id="t", seed=0)
    found_id_pair = False
    for _ in range(100):
        r = g.next()
        if r is None:
            continue
        p = r.claim_payload
        if p["operator_f"] == "identity" or p["operator_g"] == "identity":
            found_id_pair = True
            assert p["commutes"] is True
            break
    assert found_id_pair, "Should find at least one identity-involving pair in 100 tries"


def test_b2_finds_noncommuting_pair():
    """neg and mod_3 don't commute: neg(2)=−2 mod 3 = 1, but mod_3(2)=2 neg = −2."""
    g = B2CompositionTestGenerator(batch_id="t", seed=0)
    found_noncomm = False
    for _ in range(100):
        r = g.next()
        if r is None:
            continue
        if not r.claim_payload["commutes"]:
            found_noncomm = True
            break
    assert found_noncomm


def test_c5_strengthening_for_abs_diff():
    import random as rmod
    rng = rmod.Random(0)
    strongs = _generate_strengthenings("abs_diff_le_5", rng)
    for s in strongs:
        k = int(s.split("_")[-1])
        assert k < 5


def test_c5_no_strengthening_for_equal():
    import random as rmod
    assert _generate_strengthenings("equal", rmod.Random(0)) == []


def test_c5_emits_specialization():
    g = C5SpecializationGenerator(batch_id="t", seed=0)
    found = False
    for _ in range(20):
        r = g.next()
        if r is not None:
            assert r.generator_id == "c5"
            assert "C5_SPEC" in r.canonical_claim_text
            assert "strong_holds" in r.claim_payload
            found = True
            break
    assert found, "C5 should produce a record in 20 tries"


def test_d3_b2_c5_registered_as_active():
    from theseus.registry import list_active

    actives = list_active()
    assert "d3" in actives
    assert "b2" in actives
    assert "c5" in actives
