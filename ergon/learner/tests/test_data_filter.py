"""Tests for ergon.pipeline_d.data_filter — W3.7.

Per pivot/ergon_learner_v0.5_design_2026-05-05.md §5 W3.7 success
condition:

    "Filter applied to W3.2 + W3.1 outputs; per-class drop counts logged;
     INDETERMINATE retained with metadata flag; unfiltered control corpus
     preserved alongside filtered for W4.1 comparison"

Closed-loop bias caveat: the morphology classifier is itself trained on
substrate verdicts. These tests verify mechanics of the filter; the
W4.1 filtered-vs-unfiltered comparison is the substrate-grade defense
against the closed loop, not these unit tests.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from ergon.pipeline_d.data_filter import (
    CLASS_BATTERY_BLIND_SPOT,
    CLASS_INDETERMINATE,
    CLASS_PRODUCTIVE,
    CLASS_TEMPLATE_OVERFITTING,
    CLASS_THIN_DATA_ARTIFACT,
    DEFAULT_CLASSIFIER_PATH,
    DEFAULT_DROP_CLASSES,
    Classifier,
    DroppedRecord,
    classify_record,
    extract_features,
    filter_corpus,
    load_morphology_classifier,
)


# ---------------------------------------------------------------------------
# Synthetic record fixtures — one designed to land in each of the 4 classes
# ---------------------------------------------------------------------------

# `has_diag_neg` is the only feature in the shipped JSON whose dominant
# verdict is `overfitting` (per Charon's report) -> template_overfitting.
RECORD_TEMPLATE_OVERFITTING = {
    "name": "[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(-1,-1,-1)]",
    "source": "regime_change",  # adds a thin_data feature too, but overfitting wins on tie-break
    "claim_id": "synth_overfit_1",
}

# Pure thin_data feature set: n_steps_5 + flagged + regime_change + delta_pct_high.
# All Charon-classified as `thin_data` (one cell <10).
RECORD_THIN_DATA = {
    "name": "[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1)]",
    "source": "regime_change",
    "flagged": True,
    "delta_pct": 0.7,
    "claim_id": "synth_thindata_1",
}

# `best_model` is the only `indeterminate`-classified feature in the JSON.
# Triggering ONLY it lands the record in battery_blind_spot.
RECORD_BATTERY_BLIND_SPOT = {
    "best_model": "poly_log_d5",
    "claim_id": "synth_blindspot_1",
}

# No classifier features fire (Lehmer-style poly record with disjoint feature
# space). Should land in INDETERMINATE -> retained.
RECORD_INDETERMINATE = {
    "poly_coefficients": [1, 0, 0, -1, 1, 0, 0, -1, 0, 0, 1, -1, 0, 0, 1],
    "mahler_measure_dps30": 1.176280818,
    "class_post_fold": "lehmer_composite",
    "claim_id": "lehmer_17_entry_4",
}

# Productive class is unreachable from the shipped classifier (no feature
# in the JSON has a `productive` verdict per Charon's honesty notes).
# We construct a record whose *only* fired feature is one we manually
# label productive in the classifier rules to verify the productive
# code path is reachable end-to-end.
RECORD_PRODUCTIVE_PROBE = {
    "name": "[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1)]",
    "claim_id": "synth_productive_1",
}


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

def test_classifier_loads_from_default_path():
    repo_root = Path(__file__).resolve().parents[3]
    path = repo_root / DEFAULT_CLASSIFIER_PATH
    clf = load_morphology_classifier(path)
    assert isinstance(clf, Classifier)
    assert len(clf.rules) > 0
    assert "has_diag_neg" in clf.rules  # canonical feature from Charon's JSON
    # Charon reports overfitting majority for has_diag_neg.
    assert clf.rules["has_diag_neg"].spec_class == CLASS_TEMPLATE_OVERFITTING
    # n_steps_5 is thin_data per Charon.
    assert clf.rules["n_steps_5"].spec_class == CLASS_THIN_DATA_ARTIFACT
    # best_model is the indeterminate feature -> battery_blind_spot.
    assert clf.rules["best_model"].spec_class == CLASS_BATTERY_BLIND_SPOT


@pytest.fixture(scope="module")
def classifier() -> Classifier:
    repo_root = Path(__file__).resolve().parents[3]
    return load_morphology_classifier(repo_root / DEFAULT_CLASSIFIER_PATH)


# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------

def test_extract_features_a149_walk():
    feats = extract_features(RECORD_TEMPLATE_OVERFITTING)
    assert feats.get("has_diag_neg") is True
    assert feats.get("n_steps_5") is True
    assert feats.get("regime_change") is True
    # No (1,1,1) step in the set -> has_diag_pos must be absent.
    assert "has_diag_pos" not in feats


def test_extract_features_lehmer_returns_empty():
    """The 17-entry boundary layer's feature space is disjoint from the
    classifier's. Generalization caveat: filter is a no-op on Lehmer."""
    feats = extract_features(RECORD_INDETERMINATE)
    assert feats == {}


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def test_classify_template_overfitting(classifier):
    assert classify_record(RECORD_TEMPLATE_OVERFITTING, classifier) == CLASS_TEMPLATE_OVERFITTING


def test_classify_thin_data_artifact(classifier):
    # All triggered features are thin_data verdicts -> majority thin_data.
    assert classify_record(RECORD_THIN_DATA, classifier) == CLASS_THIN_DATA_ARTIFACT


def test_classify_battery_blind_spot(classifier):
    # Only best_model fires -> indeterminate per Charon -> battery_blind_spot per spec.
    assert classify_record(RECORD_BATTERY_BLIND_SPOT, classifier) == CLASS_BATTERY_BLIND_SPOT


def test_classify_indeterminate_for_disjoint_feature_space(classifier):
    """Lehmer record: zero classifier features fire -> INDETERMINATE."""
    assert classify_record(RECORD_INDETERMINATE, classifier) == CLASS_INDETERMINATE


def test_classify_productive_path_is_reachable():
    """Verify the productive_morphology code path is wired end-to-end,
    even though the shipped JSON has no productive features. We synthesize
    a classifier where one feature is productive and confirm the record
    routes there."""
    from ergon.pipeline_d.data_filter import FeatureRule

    rules = {
        "n_steps_5": FeatureRule(
            feature="n_steps_5",
            spec_class=CLASS_PRODUCTIVE,
            n_total=97,
            rationale="synthetic test override",
        ),
    }
    synthetic_clf = Classifier(rules=rules, feature_extractors=("n_steps_5",), meta={})
    assert classify_record(RECORD_PRODUCTIVE_PROBE, synthetic_clf) == CLASS_PRODUCTIVE


# ---------------------------------------------------------------------------
# Filter — shape + INDETERMINATE retention + round-trip
# ---------------------------------------------------------------------------

def test_filter_returns_three_part_tuple(classifier):
    corpus = [RECORD_TEMPLATE_OVERFITTING, RECORD_INDETERMINATE]
    result = filter_corpus(corpus, classifier)
    assert isinstance(result, tuple)
    assert len(result) == 3
    filtered, dropped, counts = result
    assert isinstance(filtered, list)
    assert isinstance(dropped, list)
    assert isinstance(counts, dict)


def test_filter_drops_battery_blind_spot_and_template_overfitting(classifier):
    corpus = [
        RECORD_TEMPLATE_OVERFITTING,
        RECORD_THIN_DATA,
        RECORD_BATTERY_BLIND_SPOT,
        RECORD_INDETERMINATE,
    ]
    filtered, dropped, counts = filter_corpus(corpus, classifier)

    dropped_classes = {d.flagged_class for d in dropped}
    assert dropped_classes == set(DEFAULT_DROP_CLASSES)
    assert counts.get(CLASS_TEMPLATE_OVERFITTING) == 1
    assert counts.get(CLASS_BATTERY_BLIND_SPOT) == 1
    # thin_data + indeterminate retained
    assert len(filtered) == 2


def test_filter_retains_indeterminate_with_metadata_flag(classifier):
    """Per spec: INDETERMINATE records are RETAINED with a metadata flag."""
    filtered, dropped, _ = filter_corpus([RECORD_INDETERMINATE], classifier)
    assert len(filtered) == 1
    assert len(dropped) == 0
    assert filtered[0].get("morphology_class") == CLASS_INDETERMINATE
    # Original payload preserved.
    assert filtered[0]["claim_id"] == "lehmer_17_entry_4"
    assert filtered[0]["mahler_measure_dps30"] == pytest.approx(1.176280818)


def test_filter_round_trip_no_records_lost(classifier):
    """filtered ∪ dropped = original (modulo metadata-flag tagging)."""
    corpus = [
        RECORD_TEMPLATE_OVERFITTING,
        RECORD_THIN_DATA,
        RECORD_BATTERY_BLIND_SPOT,
        RECORD_INDETERMINATE,
    ]
    filtered, dropped, _ = filter_corpus(corpus, classifier)
    assert len(filtered) + len(dropped) == len(corpus)

    # Identity by claim_id (filtered records gain a morphology_class tag, so
    # we compare on stable identifier, not full dict equality).
    seen_ids = {r["claim_id"] for r in filtered} | {d.record["claim_id"] for d in dropped}
    original_ids = {r["claim_id"] for r in corpus}
    assert seen_ids == original_ids


def test_filter_does_not_mutate_input(classifier):
    """Defensive: input records must not be mutated. The closed-loop
    discipline depends on us keeping the original corpus pristine for
    the W4.1 unfiltered control run."""
    original = dict(RECORD_INDETERMINATE)
    filter_corpus([RECORD_INDETERMINATE], classifier)
    assert RECORD_INDETERMINATE == original
    assert "morphology_class" not in RECORD_INDETERMINATE


def test_filter_custom_drop_classes(classifier):
    """drop_classes is configurable — caller may opt to drop thin_data too,
    or drop nothing (effectively a classification-only pass)."""
    corpus = [RECORD_TEMPLATE_OVERFITTING, RECORD_THIN_DATA, RECORD_INDETERMINATE]
    filtered, dropped, counts = filter_corpus(corpus, classifier, drop_classes=())
    assert len(dropped) == 0
    assert len(filtered) == 3
    assert counts == {}


def test_filter_lehmer_no_op_documented(classifier):
    """Generalization caveat regression test: for a Lehmer-style corpus
    (no classifier features fire), the filter is a no-op. This is the
    'filter_was_no_op' event the W6.1 dossier needs to flag."""
    lehmer_like_corpus = [
        {"poly_coefficients": [1, 0, 0, -1, 1], "claim_id": f"lehmer_{i}"}
        for i in range(17)
    ]
    filtered, dropped, counts = filter_corpus(lehmer_like_corpus, classifier)
    assert len(filtered) == 17
    assert len(dropped) == 0
    assert counts == {}
    # All retained as INDETERMINATE.
    assert all(r["morphology_class"] == CLASS_INDETERMINATE for r in filtered)
