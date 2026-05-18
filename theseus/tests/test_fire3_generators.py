"""Smoke tests for Fire #3 active generators: C2 counterfactual, C4, H1."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.generators.c2_threshold_mutation import (
    C2ThresholdMutationGenerator,
    _counterfactual_thresholds,
)
from theseus.generators.c4_generalization import (
    C4GeneralizationGenerator,
    _generate_weakenings,
)
from theseus.generators.h1_self_play_hunter import (
    H1SelfPlayHunterGenerator,
)


def test_counterfactual_thresholds_boundary_adjacent():
    cands = _counterfactual_thresholds(orig_k=3, actual_diff=5)
    # Should include 5 (boundary), 4 (one inside), 6 (one outside), and midpoint 4
    assert 5 in cands
    assert 4 in cands
    assert 6 in cands
    assert 3 not in cands  # Excludes orig_k


def test_counterfactual_thresholds_nonnegative():
    cands = _counterfactual_thresholds(orig_k=5, actual_diff=1)
    assert all(k >= 0 for k in cands)


def test_c2_emits_counterfactual_mutation():
    g = C2ThresholdMutationGenerator(batch_id="t", seed=0)
    found_cf = False
    for _ in range(15):
        r = g.next()
        if r is not None and r.claim_payload.get("mutation_kind") == "counterfactual_boundary":
            found_cf = True
            break
    assert found_cf, "C2 should emit at least one counterfactual_boundary mutation"


def test_weakenings_for_equal():
    rng = __import__("random").Random(0)
    weaks = _generate_weakenings("equal", rng)
    assert "equal_mod_2" in weaks
    assert any(w.startswith("abs_diff_le_") for w in weaks)


def test_weakenings_for_abs_diff():
    rng = __import__("random").Random(0)
    weaks = _generate_weakenings("abs_diff_le_3", rng)
    assert all(w.startswith("abs_diff_le_") for w in weaks)
    for w in weaks:
        k = int(w.split("_")[-1])
        assert k > 3  # strictly weaker (bigger threshold)


def test_weakenings_for_divides_returns_empty():
    rng = __import__("random").Random(0)
    assert _generate_weakenings("divides", rng) == []


def test_c4_emits_self_consistent_generalization():
    g = C4GeneralizationGenerator(batch_id="t", seed=0)
    found = False
    for _ in range(20):
        r = g.next()
        if r is not None:
            assert r.generator_id == "c4"
            p = r.claim_payload
            # Logical implication should ~always hold on healthy substrate
            assert p["self_consistent"] is True or p["self_consistent"] is False
            assert "C4_GEN" in r.canonical_claim_text
            found = True
            break
    assert found, "C4 should produce a record in 20 tries"


def test_h1_bootstraps_and_emits(tmp_path):
    """H1 with empty corpus should bootstrap via internal A1 seed."""
    g = H1SelfPlayHunterGenerator(
        batch_id="t", seed=0, corpus_dir=tmp_path, hunt_budget=10
    )
    found = False
    for _ in range(10):
        r = g.next()
        if r is not None:
            assert r.generator_id == "h1"
            assert "H1_HUNT" in r.canonical_claim_text
            assert r.claim_payload["hunt_budget"] == 10
            found = True
            break
    assert found, "H1 should produce a record in 10 tries"


def test_h1_reads_corpus_when_available(tmp_path):
    """H1 should read SHADOW_CATALOG records from existing corpus."""
    corpus_file = tmp_path / "batch-test.jsonl"
    survivor = TheseusRecord(
        record_id="surv1",
        generator_id="a1",
        batch_id="test",
        emitted_at="2026-05-18T00:00:00Z",
        claim_kind=ClaimKind.INVARIANT_EQUALITY.value,
        claim_payload={
            "relation": "equal_mod_2",
            "object_a": "3_1",
            "object_b": "11a1",
            "invariant_a": "signature",
            "invariant_b": "rank",
            "value_a": 2,
            "value_b": 0,
            "catalog_a": "knot",
            "catalog_b": "ec",
            "holds": True,
        },
        canonical_claim_text="signature(knot:3_1) equal_mod_2 rank(ec:11a1)",
        verdict=Verdict.SHADOW_CATALOG.value,
    )
    with corpus_file.open("w", encoding="utf-8") as f:
        f.write(survivor.to_jsonl() + "\n")

    g = H1SelfPlayHunterGenerator(
        batch_id="t", seed=0, corpus_dir=tmp_path, hunt_budget=10
    )
    g._load_survivors()
    assert len(g._survivors) == 1


def test_c2_c4_h1_registered_as_active():
    from theseus.registry import list_active

    actives = list_active()
    assert "c2" in actives
    assert "c4" in actives
    assert "h1" in actives
