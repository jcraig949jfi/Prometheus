"""Tests for prometheus_math.learner_corpus — P5 NearMissCorpus interface stub.

Coverage:
  * Schema shape and per-domain feature lookup
  * Stub emission from legacy-ledger-shaped records
  * Disk layout (pre / post / provenance separation)
  * Loader anti-leakage discipline (post-view requires explicit opt-in)
  * Leakage event logging
  * Splits round-trip
  * emit_from_substrate raises NotImplementedError (Tier 2 gate)
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from prometheus_math.learner_corpus import (
    LEAKAGE_LOG_FILENAME,
    POST_VIEW_DIRNAME,
    PRE_VIEW_DIRNAME,
    PROVENANCE_VIEW_DIRNAME,
    SCHEMA_VERSION,
    CorpusEmission,
    LearnerCorpusLoader,
    ObjectFeatures,
    PostFalsificationLeakageError,
    PostFalsificationView,
    PreFalsificationView,
    ProvenanceView,
    RAW_INVARIANTS_PER_DOMAIN,
    RankLossTriple,
    SplitName,
    Splits,
    TripletLossTriple,
    emit_from_substrate,
    get_raw_invariant_keys,
    stub_emit_from_legacy_ledger,
    write_emission_to_disk,
)


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


def _legacy_records_lehmer(n: int = 3):
    """Synthesise n legacy-ledger-shaped records for the Lehmer domain."""
    out = []
    for i in range(n):
        out.append(
            {
                "poly_coefficients": [1, 0, -1, 0, 1, 0, -1, 0, 1, 0, -1, 0, 1, 0, 1],  # deg14 stub
                "mahler_measure_dps30": 1.176 + i * 0.001,
                "mahler_measure_dps60": 1.176 + i * 0.001,
                "mahler_measure_dps100": 1.176 + i * 0.001,
                "n_irreducible_factors": 1,
                "kill_vector": {
                    "components": [
                        {"falsifier_name": "out_of_band", "triggered": False, "margin": 0.001}
                    ]
                },
                "operator_class": f"DiscoveryEnv@degree=14/seed={i}",
                "timestamp": 1714500000.0 + i,
                "label_source": "lehmer_brute_force_path_b",
                "label_strength": "candidate",
            }
        )
    return out


# ---------------------------------------------------------------------------
# Schema shape
# ---------------------------------------------------------------------------


def test_per_domain_raw_invariant_registry_has_lehmer_full_list():
    keys = get_raw_invariant_keys("lehmer")
    # Q-E2 from Ergon: pinned 13-key Lehmer feature list
    assert "poly_coefficients" in keys
    assert "mahler_measure_dps30" in keys
    assert "mahler_measure_dps60" in keys
    assert "mahler_measure_dps100" in keys
    assert "cyclotomic_factor_indices" in keys
    assert "non_cyclotomic_factor_present" in keys
    assert "reflection_pair_partner_hash" in keys


def test_per_domain_raw_invariant_registry_unknown_domain_returns_sentinel():
    keys = get_raw_invariant_keys("nonexistent_domain")
    assert keys == ("__unregistered__",)


def test_obstruction_shape_deferred_to_charon():
    keys = get_raw_invariant_keys("obstruction_shape")
    assert keys == ("__deferred_to_charon__",)


def test_schema_version_is_stub():
    assert SCHEMA_VERSION == "v2.3-stub"


# ---------------------------------------------------------------------------
# Stub emission
# ---------------------------------------------------------------------------


def test_stub_emit_returns_corpus_emission_with_correct_view_counts():
    records = _legacy_records_lehmer(n=5)
    emission = stub_emit_from_legacy_ledger(
        records,
        region_key="lehmer:deg14:pm5:palindromic",
        label_version="discovery_pipeline:v1.5",
        domain="lehmer",
    )

    assert isinstance(emission, CorpusEmission)
    assert len(emission.pre_views) == 5
    assert len(emission.post_views) == 5
    assert len(emission.provenance_views) == 5
    assert emission.region_key == "lehmer:deg14:pm5:palindromic"
    assert emission.schema_version == "v2.3-stub"


def test_stub_emit_pre_views_carry_lehmer_raw_invariants():
    records = _legacy_records_lehmer(n=2)
    emission = stub_emit_from_legacy_ledger(
        records,
        region_key="lehmer:deg14:pm5:palindromic",
        label_version="v1.5",
        domain="lehmer",
    )

    pre = emission.pre_views[0]
    assert pre.object.domain == "lehmer"
    assert pre.object.coordinate_chart_id == "provisional:lehmer"
    assert "poly_coefficients" in pre.object.raw_invariants
    assert "mahler_measure_dps30" in pre.object.raw_invariants
    assert "mahler_measure_dps100" in pre.object.raw_invariants


def test_stub_emit_object_id_is_content_addressed():
    records = _legacy_records_lehmer(n=2)
    emission_a = stub_emit_from_legacy_ledger(
        records, region_key="r", label_version="v1.5", domain="lehmer"
    )
    emission_b = stub_emit_from_legacy_ledger(
        records, region_key="r", label_version="v1.5", domain="lehmer"
    )
    # Same content → same object_ids (content-addressed)
    assert emission_a.object_ids == emission_b.object_ids


def test_stub_emit_post_views_match_pre_view_object_ids():
    records = _legacy_records_lehmer(n=3)
    emission = stub_emit_from_legacy_ledger(
        records, region_key="r", label_version="v1.5", domain="lehmer"
    )
    pre_ids = {v.object_id for v in emission.pre_views}
    post_ids = {v.object_id for v in emission.post_views}
    prov_ids = {v.object_id for v in emission.provenance_views}
    assert pre_ids == post_ids == prov_ids


def test_stub_emit_post_views_carry_kill_vector_when_present():
    records = _legacy_records_lehmer(n=1)
    emission = stub_emit_from_legacy_ledger(
        records, region_key="r", label_version="v1.5", domain="lehmer"
    )
    post = emission.post_views[0]
    assert post.kill_vector is not None
    assert post.triangulation_path == "untriangulated:stub"  # DEFERRED until P6
    assert post.method_spec is None  # DEFERRED until P3
    assert post.evidence_field is None  # DEFERRED until P1


def test_stub_emit_default_split_is_all_train():
    records = _legacy_records_lehmer(n=4)
    emission = stub_emit_from_legacy_ledger(
        records, region_key="r", label_version="v1.5", domain="lehmer"
    )
    assert len(emission.splits.train) == 4
    assert len(emission.splits.validation_same_region) == 0
    assert len(emission.splits.synthetic_null) == 0


def test_stub_emit_no_triples_generated():
    """Stub does not generate triples — that requires P5 proper +
    boundary-layer clustering. Documented as a stub limitation."""
    records = _legacy_records_lehmer(n=3)
    emission = stub_emit_from_legacy_ledger(
        records, region_key="r", label_version="v1.5", domain="lehmer"
    )
    assert emission.rank_triples == ()
    assert emission.triplet_triples == ()


# ---------------------------------------------------------------------------
# Disk layout
# ---------------------------------------------------------------------------


def test_write_emission_creates_three_view_subdirs(tmp_path: Path):
    records = _legacy_records_lehmer(n=2)
    emission = stub_emit_from_legacy_ledger(
        records, region_key="r", label_version="v1.5", domain="lehmer",
        output_root=tmp_path,
    )

    root = tmp_path / emission.emission_id
    assert (root / PRE_VIEW_DIRNAME).is_dir()
    assert (root / POST_VIEW_DIRNAME).is_dir()
    assert (root / PROVENANCE_VIEW_DIRNAME).is_dir()
    assert (root / "metadata.json").exists()
    assert (root / "splits.json").exists()


def test_write_emission_one_json_per_object_per_view(tmp_path: Path):
    records = _legacy_records_lehmer(n=3)
    emission = stub_emit_from_legacy_ledger(
        records, region_key="r", label_version="v1.5", domain="lehmer",
        output_root=tmp_path,
    )

    root = tmp_path / emission.emission_id
    assert len(list((root / PRE_VIEW_DIRNAME).glob("*.json"))) == 3
    assert len(list((root / POST_VIEW_DIRNAME).glob("*.json"))) == 3
    assert len(list((root / PROVENANCE_VIEW_DIRNAME).glob("*.json"))) == 3


# ---------------------------------------------------------------------------
# Loader — anti-leakage discipline (load-bearing)
# ---------------------------------------------------------------------------


@pytest.fixture
def emission_on_disk(tmp_path: Path) -> Path:
    records = _legacy_records_lehmer(n=4)
    emission = stub_emit_from_legacy_ledger(
        records, region_key="r", label_version="v1.5", domain="lehmer",
        output_root=tmp_path,
    )
    return tmp_path / emission.emission_id


def test_loader_default_load_returns_pre_views_only(emission_on_disk: Path):
    loader = LearnerCorpusLoader(emission_on_disk)
    views = list(loader.load())
    assert len(views) == 4
    assert all(isinstance(v, PreFalsificationView) for v in views)
    # Pre-views carry NO kill outcomes. Anti-leakage by structure.
    for v in views:
        assert v.object.domain == "lehmer"
        assert "poly_coefficients" in v.object.raw_invariants


def test_loader_post_view_blocked_without_explicit_flag(emission_on_disk: Path):
    """Default attempt to load post-view raises PostFalsificationLeakageError.
    This is the load-bearing anti-leakage gate."""
    loader = LearnerCorpusLoader(emission_on_disk)
    with pytest.raises(PostFalsificationLeakageError):
        # NOTE: keyword-only arg; cannot pass positionally
        list(loader.load_post_view(
            allow_post_falsification=False,
            caller_id="test",
            purpose="audit",
        ))


def test_loader_post_view_blocked_when_flag_omitted(emission_on_disk: Path):
    """Flag is keyword-only; omitting it raises TypeError before load."""
    loader = LearnerCorpusLoader(emission_on_disk)
    with pytest.raises(TypeError):
        list(loader.load_post_view(caller_id="test", purpose="audit"))


def test_loader_post_view_loads_with_explicit_flag(emission_on_disk: Path):
    loader = LearnerCorpusLoader(emission_on_disk)
    views = list(
        loader.load_post_view(
            allow_post_falsification=True,
            caller_id="ergon.tire_kick.W4",
            purpose="explanation",
        )
    )
    assert len(views) == 4
    assert all(isinstance(v, PostFalsificationView) for v in views)


def test_loader_post_view_load_logs_leakage_event(emission_on_disk: Path):
    """Every post-view load is logged for substrate-level leakage audit."""
    loader = LearnerCorpusLoader(emission_on_disk)
    list(
        loader.load_post_view(
            allow_post_falsification=True,
            caller_id="ergon.tire_kick.W4",
            purpose="explanation",
        )
    )

    log_path = emission_on_disk / LEAKAGE_LOG_FILENAME
    assert log_path.exists()
    events = loader.post_view_load_events()
    assert len(events) == 1
    assert events[0]["caller_id"] == "ergon.tire_kick.W4"
    assert events[0]["purpose"] == "explanation"


def test_loader_multiple_post_view_loads_append_to_log(emission_on_disk: Path):
    loader = LearnerCorpusLoader(emission_on_disk)
    for purpose in ("audit", "calibration", "explanation"):
        list(
            loader.load_post_view(
                allow_post_falsification=True,
                caller_id=f"caller_{purpose}",
                purpose=purpose,
            )
        )
    events = loader.post_view_load_events()
    assert len(events) == 3
    assert {e["purpose"] for e in events} == {"audit", "calibration", "explanation"}


# ---------------------------------------------------------------------------
# Provenance and splits
# ---------------------------------------------------------------------------


def test_loader_load_provenance_returns_provenance_views(emission_on_disk: Path):
    loader = LearnerCorpusLoader(emission_on_disk)
    provs = list(loader.load_provenance())
    assert len(provs) == 4
    assert all(isinstance(p, ProvenanceView) for p in provs)
    assert all(p.label_source == "lehmer_brute_force_path_b" for p in provs)


def test_loader_load_splits_round_trips(emission_on_disk: Path):
    loader = LearnerCorpusLoader(emission_on_disk)
    splits = loader.load_splits()
    assert isinstance(splits, Splits)
    assert len(splits.train) == 4
    assert splits.get(SplitName.TRAIN) == splits.train


def test_loader_load_rank_and_triplet_triples_empty_for_stub(emission_on_disk: Path):
    loader = LearnerCorpusLoader(emission_on_disk)
    assert loader.load_rank_triples() == []
    assert loader.load_triplet_triples() == []


# ---------------------------------------------------------------------------
# emit_from_substrate is intentionally NotImplemented until Day 13
# ---------------------------------------------------------------------------


def test_emit_from_substrate_raises_on_empty_records():
    """As of Day-13 ship, emit_from_substrate is real (no longer
    NotImplementedError). It DOES still reject empty input — calling
    with no records is a programming error, not a use case."""
    with pytest.raises(ValueError, match="typed_records cannot be empty"):
        emit_from_substrate([], region_key="r", label_version="v", domain="lehmer")


# ---------------------------------------------------------------------------
# emit_from_substrate (real, post-Day-13) — full-emission tests
# ---------------------------------------------------------------------------


def _typed_records_lehmer_promoted_and_rejected(n_promoted: int = 4, n_rejected: int = 3, n_candidates: int = 5):
    """Synthesise typed records with a mix of label_strengths so triple
    generation has positives + negatives + near-misses to draw from."""
    base_ts = 1714500000.0
    records = []
    region = "lehmer:deg14:pm5:palindromic"
    for i in range(n_promoted):
        records.append({
            "poly_coefficients": [1, 0, -1, 0, 1, 0, -1, 0, 1, 0, -1, 0, 1, 0, 1 + i],
            "mahler_measure": 1.176 + i * 1e-4,
            "kill_vector": {"components": [{"falsifier_name": "out_of_band", "triggered": False, "margin": 0.001}]},
            "evidence_field": {"distance_to_target": {"value": 0.001, "unit": "absolute"}},
            "method_spec": {"engine": "mpmath", "strategy": "factor_first", "independence_class": "mpmath_polynomial_factorization"},
            "triangulation_path": "path_a_high_precision_mpmath_dps60",
            "exclusion_certificate_ref": "ec_lehmer_deg14_pm5",
            "operator_class": f"DiscoveryEnv@degree=14/seed={i}",
            "timestamp": base_ts + i,
            "label_source": "lehmer_brute_force_path_b",
            "label_strength": "promoted",
            "region_key": region,
        })
    for i in range(n_rejected):
        records.append({
            "poly_coefficients": [1, 0, -1, 0, 1, 0, -1, 0, 1, 0, -1, 0, 1, 0, -1 - i],
            "mahler_measure": 2.0 + i * 0.1,
            "kill_vector": {"components": [{"falsifier_name": "out_of_band", "triggered": True}]},
            "method_spec": {"engine": "mpmath", "strategy": "direct", "independence_class": "mpmath_polynomial_factorization"},
            "triangulation_path": "untriangulated",
            "operator_class": f"random@seed={i}",
            "timestamp": base_ts + 100 + i,
            "label_source": "stub:legacy_ledger",
            "label_strength": "rejected",
            "region_key": region,
        })
    for i in range(n_candidates):
        records.append({
            "poly_coefficients": [1, 0, -1, 0, 1, 0, -1, 0, 1, 0, -1, 0, 1, 1 + i, 1],
            "mahler_measure": 1.18 + i * 1e-3,
            "kill_vector": {"components": [{"falsifier_name": "out_of_band", "triggered": False, "margin": 0.005}]},
            "method_spec": {"engine": "sympy", "strategy": "symbolic", "independence_class": "sympy_symbolic_factorization"},
            "triangulation_path": "untriangulated",
            "operator_class": f"DiscoveryEnv@degree=14/seed={i+10}",
            "timestamp": base_ts + 50 + i,
            "label_source": "lehmer_brute_force_path_b",
            "label_strength": "candidate",
            "region_key": region,
        })
    return records


def test_emit_from_substrate_schema_version_is_v23_not_stub():
    records = _typed_records_lehmer_promoted_and_rejected(n_promoted=2, n_rejected=2, n_candidates=2)
    em = emit_from_substrate(
        records, region_key="lehmer:deg14:pm5:palindromic",
        label_version="discovery_pipeline:v2.3", domain="lehmer",
    )
    assert em.schema_version == "v2.3"
    assert "stub" not in em.schema_version


def test_emit_from_substrate_post_view_carries_method_spec_and_triangulation():
    """Post-view must carry the upstream P3/P6/P4 references."""
    records = _typed_records_lehmer_promoted_and_rejected(n_promoted=1, n_rejected=1, n_candidates=1)
    em = emit_from_substrate(
        records, region_key="lehmer:deg14:pm5:palindromic",
        label_version="v2.3", domain="lehmer",
    )
    promoted_post = next(p for p in em.post_views if p.method_spec and p.method_spec.get("strategy") == "factor_first")
    assert promoted_post.method_spec["engine"] == "mpmath"
    assert promoted_post.triangulation_path == "path_a_high_precision_mpmath_dps60"
    assert promoted_post.exclusion_certificate_ref == "ec_lehmer_deg14_pm5"


def test_emit_from_substrate_generates_synthetic_null_pack():
    records = _typed_records_lehmer_promoted_and_rejected(n_promoted=2, n_rejected=2, n_candidates=2)
    em = emit_from_substrate(
        records, region_key="lehmer:deg14:pm5:palindromic",
        label_version="v2.3", domain="lehmer",
        n_synthetic_null_per_record=2,
    )
    # 6 real + 12 synthetic null
    assert len(em.pre_views) == 6 + 12
    assert len(em.splits.synthetic_null) == 12
    # Synthetic-null provenance must carry the family flag
    null_ids = set(em.splits.synthetic_null)
    null_provs = [p for p in em.provenance_views if p.object_id in null_ids]
    assert all(p.synthetic_null_family == "label_shuffle_v1" for p in null_provs)


def test_emit_from_substrate_synthetic_null_inherits_object_features():
    """Synthetic-null records share the source object's features (the
    shuffle is on LABEL only, not on features). This is the discipline
    that lets the Learner detect 'is the model learning labels or
    features' via held-out comparison."""
    records = _typed_records_lehmer_promoted_and_rejected(n_promoted=1, n_rejected=1, n_candidates=1)
    em = emit_from_substrate(
        records, region_key="lehmer:deg14:pm5:palindromic",
        label_version="v2.3", domain="lehmer",
        n_synthetic_null_per_record=1,
    )
    null_ids = set(em.splits.synthetic_null)
    null_pre_views = [v for v in em.pre_views if v.object_id in null_ids]
    real_pre_views = [v for v in em.pre_views if v.object_id not in null_ids]
    # Each null view's object features should match SOME real view's features
    for null_v in null_pre_views:
        assert any(
            null_v.object.canonical_form == real_v.object.canonical_form
            for real_v in real_pre_views
        )


def test_emit_from_substrate_generates_triples_anti_trivial_separability():
    """Triples must be drawn from same region (anti-trivial-separability per Gemini).
    With promoted + rejected + candidates all in same region, we should get triples."""
    records = _typed_records_lehmer_promoted_and_rejected(n_promoted=3, n_rejected=3, n_candidates=3)
    em = emit_from_substrate(
        records, region_key="lehmer:deg14:pm5:palindromic",
        label_version="v2.3", domain="lehmer",
        n_synthetic_null_per_record=0,
    )
    assert len(em.triplet_triples) > 0
    # Triples reference object_ids; all must exist in pre_views
    pre_ids = {v.object_id for v in em.pre_views}
    for t in em.triplet_triples:
        assert t.anchor_id in pre_ids
        assert t.positive_id in pre_ids
        assert t.hard_negative_id in pre_ids


def test_emit_from_substrate_no_triples_when_region_too_small():
    """If there are fewer than 3 records in a region, no triples generated.
    Anti-trivial-separability discipline."""
    records = _typed_records_lehmer_promoted_and_rejected(n_promoted=1, n_rejected=1, n_candidates=0)
    em = emit_from_substrate(
        records, region_key="lehmer:deg14:pm5:palindromic",
        label_version="v2.3", domain="lehmer",
        n_synthetic_null_per_record=0,
    )
    assert len(em.triplet_triples) == 0


def test_emit_from_substrate_canonical_splits_assign_records():
    records = _typed_records_lehmer_promoted_and_rejected(n_promoted=10, n_rejected=10, n_candidates=10)
    em = emit_from_substrate(
        records, region_key="lehmer:deg14:pm5:palindromic",
        label_version="v2.3", domain="lehmer",
        n_synthetic_null_per_record=0,
    )
    # All 30 records should appear in some split (no record orphaned)
    in_splits = (
        set(em.splits.train) | set(em.splits.validation_same_region)
        | set(em.splits.validation_heldout_region) | set(em.splits.validation_heldout_method)
        | set(em.splits.validation_later_time)
    )
    real_ids = {v.object_id for v in em.pre_views}
    assert real_ids == in_splits


def test_emit_from_substrate_val_later_time_is_top_10_percent():
    """Temporal split: latest ~10% of records by timestamp go to val_later_time."""
    records = _typed_records_lehmer_promoted_and_rejected(n_promoted=10, n_rejected=10, n_candidates=10)
    em = emit_from_substrate(
        records, region_key="lehmer:deg14:pm5:palindromic",
        label_version="v2.3", domain="lehmer",
        n_synthetic_null_per_record=0,
    )
    # 30 real records; later_time ~= top 10% = 3 records
    assert 1 <= len(em.splits.validation_later_time) <= 5


def test_emit_from_substrate_holdout_method_split_works():
    """When holdout_method_independence_class is set, records using that
    method's IC are routed to val_heldout_method."""
    records = _typed_records_lehmer_promoted_and_rejected(n_promoted=5, n_rejected=5, n_candidates=5)
    em = emit_from_substrate(
        records, region_key="lehmer:deg14:pm5:palindromic",
        label_version="v2.3", domain="lehmer",
        n_synthetic_null_per_record=0,
        holdout_method_independence_class="sympy_symbolic_factorization",  # candidates use this
    )
    assert len(em.splits.validation_heldout_method) > 0


def test_emit_from_substrate_deterministic_under_split_seed():
    """Same seed + same records → same emission (modulo timestamps)."""
    records = _typed_records_lehmer_promoted_and_rejected(n_promoted=3, n_rejected=3, n_candidates=3)
    em1 = emit_from_substrate(
        records, region_key="lehmer:deg14:pm5:palindromic",
        label_version="v2.3", domain="lehmer",
        split_seed=42, n_synthetic_null_per_record=0,
    )
    em2 = emit_from_substrate(
        records, region_key="lehmer:deg14:pm5:palindromic",
        label_version="v2.3", domain="lehmer",
        split_seed=42, n_synthetic_null_per_record=0,
    )
    assert em1.splits.train == em2.splits.train
    assert em1.splits.validation_same_region == em2.splits.validation_same_region


def test_emit_from_substrate_different_seeds_yield_different_splits():
    records = _typed_records_lehmer_promoted_and_rejected(n_promoted=10, n_rejected=10, n_candidates=10)
    em1 = emit_from_substrate(
        records, region_key="lehmer:deg14:pm5:palindromic",
        label_version="v2.3", domain="lehmer",
        split_seed=0, n_synthetic_null_per_record=0,
    )
    em2 = emit_from_substrate(
        records, region_key="lehmer:deg14:pm5:palindromic",
        label_version="v2.3", domain="lehmer",
        split_seed=99, n_synthetic_null_per_record=0,
    )
    # Splits must differ across seeds (very high probability with 30 records)
    assert em1.splits.train != em2.splits.train


def test_emit_from_substrate_writes_to_disk(tmp_path: Path):
    records = _typed_records_lehmer_promoted_and_rejected(n_promoted=2, n_rejected=2, n_candidates=2)
    em = emit_from_substrate(
        records, region_key="lehmer:deg14:pm5:palindromic",
        label_version="v2.3", domain="lehmer",
        output_root=tmp_path, n_synthetic_null_per_record=1,
    )
    root = tmp_path / em.emission_id
    assert (root / PRE_VIEW_DIRNAME).is_dir()
    assert (root / POST_VIEW_DIRNAME).is_dir()
    assert (root / PROVENANCE_VIEW_DIRNAME).is_dir()
    # Loader can round-trip the disk emission. n_synthetic_null_per_record=1
    # means ONE null PER RECORD → 6 real records produce 6 nulls = 12 total.
    loader = LearnerCorpusLoader(root)
    pre_views = list(loader.load())
    assert len(pre_views) == 6 + 6  # 6 real + 6 synthetic null
    splits = loader.load_splits()
    assert len(splits.synthetic_null) == 6


def test_emit_from_substrate_provisional_chart_id_for_unregistered_domain():
    """Domains without registered CoordinateChart fall back to provisional:<domain>."""
    records = _typed_records_lehmer_promoted_and_rejected(n_promoted=1, n_rejected=1, n_candidates=1)
    # Strip the per-record chart_id so the function uses its default
    for r in records:
        r.pop("coordinate_chart_id", None)
    em = emit_from_substrate(
        records, region_key="lehmer:deg14:pm5:palindromic",
        label_version="v2.3", domain="lehmer",
        # no coordinate_chart_id passed → provisional:lehmer
    )
    pre = em.pre_views[0]
    assert pre.object.coordinate_chart_id == "provisional:lehmer"


def test_emit_from_substrate_explicit_chart_id_overrides_provisional():
    records = _typed_records_lehmer_promoted_and_rejected(n_promoted=1, n_rejected=1, n_candidates=1)
    for r in records:
        r.pop("coordinate_chart_id", None)
    em = emit_from_substrate(
        records, region_key="lehmer:deg14:pm5:palindromic",
        label_version="v2.3", domain="lehmer",
        coordinate_chart_id="lehmer:deg14:pm5:palindromic",  # registered chart_id
    )
    pre = em.pre_views[0]
    assert pre.object.coordinate_chart_id == "lehmer:deg14:pm5:palindromic"
