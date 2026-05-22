"""Tests for theseus.orchestration.signature_index."""
from __future__ import annotations

from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.orchestration.signature_index import (
    SignatureIndex,
    compute_signature,
    _verdict_class,
    _coarsen_relation,
)


def _mk(
    claim_payload: dict,
    generator_id: str = "a1",
    verdict: str = Verdict.REJECTED.value,
    claim_kind: str = ClaimKind.INVARIANT_EQUALITY.value,
    batch_id: str = "test-batch",
) -> TheseusRecord:
    rid = TheseusRecord.compute_record_id(
        canonical_claim_text=str(claim_payload), generator_id=generator_id,
    )
    return TheseusRecord(
        record_id=rid, generator_id=generator_id, batch_id=batch_id,
        emitted_at="2026-05-22T00:00:00Z", claim_kind=claim_kind,
        claim_payload=claim_payload,
        canonical_claim_text=str(claim_payload), verdict=verdict,
    )


def test_verdict_class_collapses_verdicts():
    assert _verdict_class(Verdict.REJECTED.value) == "KILL"
    assert _verdict_class(Verdict.PROMOTED.value) == "CONFIRM"
    assert _verdict_class(Verdict.SHADOW_CATALOG.value) == "CONFIRM"
    assert _verdict_class(Verdict.INCONCLUSIVE.value) == "INCONCLUSIVE"


def test_signature_a1_paired_invariants_same_shape_across_objects():
    """Two A1 records about different (knot, ec) pairs but SAME
    (invariant_a, invariant_b, relation) must produce the same signature."""
    r1 = _mk({
        "catalog_a": "knot", "object_a": "3_1",
        "invariant_a": "crossing_number", "value_a": 3,
        "catalog_b": "ec", "object_b": "11.a1",
        "invariant_b": "rank", "value_b": 0,
        "relation": "equal", "holds": False,
    })
    r2 = _mk({
        "catalog_a": "knot", "object_a": "4_1",
        "invariant_a": "crossing_number", "value_a": 4,
        "catalog_b": "ec", "object_b": "37.a1",
        "invariant_b": "rank", "value_b": 1,
        "relation": "equal", "holds": False,
    })
    assert compute_signature(r1) == compute_signature(r2)


def test_signature_distinguishes_relation():
    r1 = _mk({
        "catalog_a": "knot", "invariant_a": "crossing_number",
        "catalog_b": "ec", "invariant_b": "rank",
        "relation": "equal",
    })
    r2 = _mk({
        "catalog_a": "knot", "invariant_a": "crossing_number",
        "catalog_b": "ec", "invariant_b": "rank",
        "relation": "divides",
    })
    assert compute_signature(r1) != compute_signature(r2)


def test_signature_distinguishes_verdict_class():
    r1 = _mk({
        "catalog_a": "knot", "invariant_a": "x",
        "catalog_b": "ec", "invariant_b": "y", "relation": "equal",
    }, verdict=Verdict.REJECTED.value)
    r2 = _mk({
        "catalog_a": "knot", "invariant_a": "x",
        "catalog_b": "ec", "invariant_b": "y", "relation": "equal",
    }, verdict=Verdict.SHADOW_CATALOG.value)
    assert compute_signature(r1) != compute_signature(r2)


def test_coarsen_abs_diff_le_K_tight_mid_wide():
    """K-buckets: ≤3 → tight, ≤10 → mid, >10 → wide."""
    assert _coarsen_relation("abs_diff_le_1") == "abs_diff_le_tight"
    assert _coarsen_relation("abs_diff_le_3") == "abs_diff_le_tight"
    assert _coarsen_relation("abs_diff_le_5") == "abs_diff_le_mid"
    assert _coarsen_relation("abs_diff_le_10") == "abs_diff_le_mid"
    assert _coarsen_relation("abs_diff_le_30") == "abs_diff_le_wide"
    assert _coarsen_relation("abs_diff_le_100") == "abs_diff_le_wide"


def test_coarsen_passes_through_other_relations():
    assert _coarsen_relation("equal") == "equal"
    assert _coarsen_relation("divides") == "divides"
    assert _coarsen_relation("equal_mod_2") == "equal_mod_2"


def test_signature_abs_diff_le_K_collapses_to_bucket():
    """Different K values in same bucket should produce same signature."""
    r1 = _mk({
        "catalog_a": "knot", "invariant_a": "x",
        "catalog_b": "ec", "invariant_b": "y",
        "relation": "abs_diff_le_35",
    })
    r2 = _mk({
        "catalog_a": "knot", "invariant_a": "x",
        "catalog_b": "ec", "invariant_b": "y",
        "relation": "abs_diff_le_47",  # different K, same wide bucket
    })
    assert compute_signature(r1) == compute_signature(r2)


def test_signature_canonical_order():
    """(A, B) and (B, A) catalog/invariant order should produce same signature."""
    r1 = _mk({
        "catalog_a": "knot", "invariant_a": "x",
        "catalog_b": "ec", "invariant_b": "y", "relation": "equal",
    })
    r2 = _mk({
        "catalog_a": "ec", "invariant_a": "y",
        "catalog_b": "knot", "invariant_b": "x", "relation": "equal",
    })
    assert compute_signature(r1) == compute_signature(r2)


def test_signature_b_family_operator():
    r = _mk(
        {"operator": "neg", "input_value": 5},
        generator_id="b3",
        claim_kind=ClaimKind.COMPOSITION_TEST.value,
    )
    sig = compute_signature(r)
    assert "b3" in sig
    assert "neg" in sig


def test_signature_literature_e_family():
    r = _mk(
        {"arxiv_id": "2401.00001", "title": "Foo", "claim_text": "..."},
        generator_id="e2",
        claim_kind=ClaimKind.LITERATURE_MINED.value,
    )
    sig = compute_signature(r)
    assert sig.startswith("e2:lit:")


def test_signature_g1_twist():
    r = _mk(
        {
            "twist_class_j": "1728/1",
            "ec_a": "11.a1", "ec_b": "33.a1",
            "invariant": "rank", "holds": True,
        },
        generator_id="g1",
        claim_kind=ClaimKind.SYMMETRY_TRANSFORM.value,
    )
    sig = compute_signature(r)
    assert "g1:twist:rank" in sig


def test_signature_g3_hasse_prime_buckets():
    r1 = _mk(
        {"ec_label": "11.a1", "prime": 5, "a_p": 1},
        generator_id="g3",
        claim_kind=ClaimKind.SYMMETRY_TRANSFORM.value,
    )
    r2 = _mk(
        {"ec_label": "11.a1", "prime": 7, "a_p": -2},
        generator_id="g3",
        claim_kind=ClaimKind.SYMMETRY_TRANSFORM.value,
    )
    # Both small primes → same bucket
    assert compute_signature(r1) == compute_signature(r2)
    r3 = _mk(
        {"ec_label": "11.a1", "prime": 503, "a_p": 5},
        generator_id="g3",
        claim_kind=ClaimKind.SYMMETRY_TRANSFORM.value,
    )
    # Mid bucket different from small
    assert compute_signature(r1) != compute_signature(r3)


def test_signature_fallback_for_unrecognized_shape():
    r = _mk({"random_field": "foo"}, generator_id="d5", claim_kind="weird")
    sig = compute_signature(r)
    assert sig.startswith("d5:weird:")


def test_index_record_returns_true_on_first_seen(tmp_path):
    idx = SignatureIndex(path=tmp_path / "idx.sqlite")
    r = _mk({
        "catalog_a": "knot", "invariant_a": "x",
        "catalog_b": "ec", "invariant_b": "y", "relation": "equal",
    })
    assert idx.record(r) is True


def test_index_record_returns_false_on_repeat(tmp_path):
    idx = SignatureIndex(path=tmp_path / "idx.sqlite")
    r1 = _mk({
        "catalog_a": "knot", "invariant_a": "x",
        "catalog_b": "ec", "invariant_b": "y", "relation": "equal",
        "object_a": "3_1", "object_b": "11.a1",
    })
    r2 = _mk({
        "catalog_a": "knot", "invariant_a": "x",
        "catalog_b": "ec", "invariant_b": "y", "relation": "equal",
        "object_a": "4_1", "object_b": "37.a1",  # different objects, same shape
    })
    assert idx.record(r1) is True
    assert idx.record(r2) is False  # same signature


def test_index_count_signatures_per_gen(tmp_path):
    idx = SignatureIndex(path=tmp_path / "idx.sqlite")
    for rel in ("equal", "divides", "abs_diff_le_3"):
        r = _mk({
            "catalog_a": "knot", "invariant_a": "x",
            "catalog_b": "ec", "invariant_b": "y",
            "relation": rel,
        }, generator_id="a1")
        idx.record(r)
    idx.flush()
    r_b = _mk(
        {"operator": "neg", "input_value": 1},
        generator_id="b3",
        claim_kind=ClaimKind.COMPOSITION_TEST.value,
    )
    idx.record(r_b)
    idx.flush()
    assert idx.count_signatures("a1") == 3
    assert idx.count_signatures("b3") == 1
    assert idx.count_signatures() == 4


def test_index_summary_by_gen(tmp_path):
    idx = SignatureIndex(path=tmp_path / "idx.sqlite")
    # 2 unique shapes for a1, total seen 5
    for i in range(3):
        idx.record(_mk({
            "catalog_a": "knot", "invariant_a": "x",
            "catalog_b": "ec", "invariant_b": "y", "relation": "equal",
        }, generator_id="a1"))
    for i in range(2):
        idx.record(_mk({
            "catalog_a": "knot", "invariant_a": "x",
            "catalog_b": "ec", "invariant_b": "y", "relation": "divides",
        }, generator_id="a1"))
    idx.flush()
    summary = idx.summary_by_gen()
    assert "a1" in summary
    assert summary["a1"]["n_unique_signatures"] == 2
    assert summary["a1"]["total_seen"] == 5


def test_index_saturation_score(tmp_path):
    idx = SignatureIndex(path=tmp_path / "idx.sqlite")
    # Single shape repeated many times → high saturation
    for i in range(10):
        idx.record(_mk({
            "catalog_a": "knot", "invariant_a": "x",
            "catalog_b": "ec", "invariant_b": "y", "relation": "equal",
        }, generator_id="a1"))
    idx.flush()
    score = idx.saturation_score("a1")
    # 1 unique / 10 total = 0.1 unique → 0.9 saturated
    assert score is not None
    assert abs(score - 0.9) < 1e-9


def test_count_unique_signatures_for_roles_excludes_non_discovery(tmp_path):
    """Pass set of non-discovery generator_ids; their signatures don't count."""
    idx = SignatureIndex(path=tmp_path / "idx.sqlite")
    # 3 shapes from a1 (DISCOVERY)
    for rel in ("equal", "divides", "equal_mod_2"):
        idx.record(_mk({
            "catalog_a": "knot", "invariant_a": "x",
            "catalog_b": "ec", "invariant_b": "y", "relation": rel,
        }, generator_id="a1"))
    # 2 shapes from c4 (TAUTOLOGY_CONTROL — exclude)
    for rel in ("equal", "divides"):
        idx.record(_mk({
            "catalog_a": "knot", "invariant_a": "x",
            "catalog_b": "ec", "invariant_b": "y", "relation": rel,
        }, generator_id="c4"))
    idx.flush()
    # Total includes both
    assert idx.count_signatures() == 5
    # Excluding c4 from non-discovery gids drops it
    assert idx.count_unique_signatures_for_roles({"c4"}) == 3
    # Empty exclusion = total
    assert idx.count_unique_signatures_for_roles(set()) == 5


def test_index_top_signatures_sorted_by_count(tmp_path):
    idx = SignatureIndex(path=tmp_path / "idx.sqlite")
    # Shape A: 5 records
    for i in range(5):
        idx.record(_mk({
            "catalog_a": "knot", "invariant_a": "x",
            "catalog_b": "ec", "invariant_b": "y", "relation": "equal",
        }, generator_id="a1"))
    # Shape B: 2 records
    for i in range(2):
        idx.record(_mk({
            "catalog_a": "knot", "invariant_a": "z",
            "catalog_b": "ec", "invariant_b": "w", "relation": "divides",
        }, generator_id="a1"))
    idx.flush()
    top = idx.top_signatures(n=2)
    assert len(top) == 2
    assert top[0]["seen_count"] == 5
    assert top[1]["seen_count"] == 2


def test_last_flush_novel_by_gen_attributes_novelty(tmp_path):
    """Fire #59: per-gen novel-signature breakdown drives novelty-aware
    bandit yield_score."""
    idx = SignatureIndex(path=tmp_path / "idx.sqlite")
    # a1 emits 2 novel shapes
    idx.record(_mk({
        "catalog_a": "knot", "invariant_a": "x",
        "catalog_b": "ec", "invariant_b": "y", "relation": "equal",
    }, generator_id="a1"))
    idx.record(_mk({
        "catalog_a": "knot", "invariant_a": "z",
        "catalog_b": "ec", "invariant_b": "w", "relation": "divides",
    }, generator_id="a1"))
    # c5 emits 1 novel shape
    idx.record(_mk({
        "catalog_a": "knot", "invariant_a": "p",
        "catalog_b": "mf", "invariant_b": "q", "relation": "equal",
    }, generator_id="c5"))
    idx.flush()
    per_gen = idx.last_flush_novel_by_gen()
    assert per_gen.get("a1") == 2
    assert per_gen.get("c5") == 1


def test_last_flush_novel_by_gen_resets_on_each_flush(tmp_path):
    """Per-gen novelty breakdown is reset on each flush; second flush
    of repeats yields 0 novel for the gen."""
    idx = SignatureIndex(path=tmp_path / "idx.sqlite")
    idx.record(_mk({
        "catalog_a": "knot", "invariant_a": "x",
        "catalog_b": "ec", "invariant_b": "y", "relation": "equal",
    }, generator_id="a1"))
    idx.flush()
    assert idx.last_flush_novel_by_gen() == {"a1": 1}
    # Same shape again: 0 novel
    idx.record(_mk({
        "catalog_a": "knot", "invariant_a": "x",
        "catalog_b": "ec", "invariant_b": "y", "relation": "equal",
    }, generator_id="a1"))
    idx.flush()
    assert idx.last_flush_novel_by_gen() == {}


def test_last_flush_novel_by_gen_empty_before_any_flush(tmp_path):
    """Fresh index returns empty dict from last_flush_novel_by_gen."""
    idx = SignatureIndex(path=tmp_path / "idx.sqlite")
    assert idx.last_flush_novel_by_gen() == {}
