"""Tests for ergon.diagnostic_c.synthetic_env (W3.1).

Acceptance-criteria coverage per Aporia 2026-05-05 sign-off:
1. LSQ-baseline recoverability >85% on held-out clean data.
2. SNR in documented range (5-20 dB; not at modal-collapse boundary, not trivial).
3. Feature space qualitatively similar to 17-entry boundary-layer fixture.
"""
from __future__ import annotations

import numpy as np
import pytest

from ergon.diagnostic_c.synthetic_env import (
    COEFF_RANGE,
    DEGREE,
    N_FEATURES,
    N_FREE_COEFFS,
    SyntheticCorpus,
    SyntheticRecord,
    generate_synthetic_corpus,
    validate_acceptance_criteria,
)


def test_corpus_generation_basic():
    train, heldout = generate_synthetic_corpus(n_train=1000, n_heldout=200, seed=42)
    assert isinstance(train, SyntheticCorpus)
    assert len(train.train) == 1000
    assert len(train.heldout) == 200
    assert len(heldout.heldout) == 200


def test_record_shape():
    train, _ = generate_synthetic_corpus(n_train=200, n_heldout=50, seed=1)
    r = train.train[0]
    assert isinstance(r, SyntheticRecord)
    assert len(r.poly_coefficients) == DEGREE + 1
    for c in r.poly_coefficients:
        assert COEFF_RANGE[0] <= c <= COEFF_RANGE[1]
    for i in range(DEGREE + 1):
        assert r.poly_coefficients[i] == r.poly_coefficients[DEGREE - i]
    assert r.label in (0, 1)
    assert r.poly_coefficients[0] != 0
    assert r.poly_coefficients[DEGREE] != 0


def test_record_to_dict():
    train, _ = generate_synthetic_corpus(n_train=100, n_heldout=20, seed=7)
    d = train.train[0].to_dict()
    assert "poly_coefficients" in d
    assert "height" in d
    assert "nnz_free" in d
    assert "mahler_proxy" in d
    assert "label" in d
    assert "label_continuous" in d


def test_determinism_seed():
    a, _ = generate_synthetic_corpus(n_train=100, n_heldout=20, seed=123)
    b, _ = generate_synthetic_corpus(n_train=100, n_heldout=20, seed=123)
    for ra, rb in zip(a.train, b.train):
        assert ra.poly_coefficients == rb.poly_coefficients
        assert ra.label == rb.label


def test_seed_changes_corpus():
    a, _ = generate_synthetic_corpus(n_train=200, n_heldout=50, seed=1)
    b, _ = generate_synthetic_corpus(n_train=200, n_heldout=50, seed=2)
    same = sum(1 for ra, rb in zip(a.train, b.train) if ra.poly_coefficients == rb.poly_coefficients)
    assert same < len(a.train) // 2


def test_label_balance():
    train, _ = generate_synthetic_corpus(n_train=1000, n_heldout=200, seed=42)
    labels = np.array([r.label for r in train.train])
    frac = labels.mean()
    assert 0.4 < frac < 0.6


def test_acceptance_criterion_1_lsq_above_85():
    train, _ = generate_synthetic_corpus(n_train=1000, n_heldout=200, snr_db=10.0, seed=42)
    result = validate_acceptance_criteria(train)
    assert result["lsq_baseline_accuracy"] > 0.85, (
        f"LSQ baseline {result['lsq_baseline_accuracy']:.3f} <= 0.85"
    )
    assert result["criterion_1_pass"]


def test_acceptance_criterion_2_snr_in_range():
    train, _ = generate_synthetic_corpus(n_train=1000, n_heldout=200, snr_db=10.0, seed=42)
    result = validate_acceptance_criteria(train)
    assert 5.0 <= result["snr_db"] <= 20.0, f"SNR {result['snr_db']:.2f} dB outside [5, 20]"
    assert abs(result["snr_db"] - 10.0) < 2.0
    assert result["criterion_2_pass"]


def test_acceptance_criterion_3_feature_space_claim():
    train, _ = generate_synthetic_corpus(n_train=200, n_heldout=50, seed=42)
    result = validate_acceptance_criteria(train)
    claim = result["feature_space_similarity"]
    assert isinstance(claim, str) and len(claim) > 50
    for keyword in ("polynomial", "palindromic", "Mahler", "boundary-layer"):
        assert keyword.lower() in claim.lower(), f"Missing keyword: {keyword}"
    assert result["criterion_3_pass"]


def test_all_three_criteria_pass_default():
    train, _ = generate_synthetic_corpus(n_train=1000, n_heldout=200, seed=42)
    result = validate_acceptance_criteria(train)
    assert result["all_pass"], f"Acceptance criteria failed: {result}"


def test_validate_returns_numbers_not_strings():
    train, _ = generate_synthetic_corpus(n_train=500, n_heldout=100, seed=99)
    result = validate_acceptance_criteria(train)
    assert isinstance(result["lsq_baseline_accuracy"], float)
    assert isinstance(result["snr_db"], float)
    assert 0.0 <= result["lsq_baseline_accuracy"] <= 1.0


def test_extreme_snr_high_makes_lsq_near_perfect():
    train, _ = generate_synthetic_corpus(n_train=500, n_heldout=200, snr_db=40.0, seed=42)
    result = validate_acceptance_criteria(train)
    assert result["lsq_baseline_accuracy"] > 0.95
    assert not result["criterion_2_pass"], "SNR=40 should be flagged as too clean"


def test_extreme_snr_low_makes_lsq_near_chance():
    train, _ = generate_synthetic_corpus(n_train=500, n_heldout=200, snr_db=-10.0, seed=42)
    result = validate_acceptance_criteria(train)
    assert result["lsq_baseline_accuracy"] < 0.75
    assert not result["criterion_2_pass"]
    assert not result["all_pass"]


def test_small_n_train_edge_case():
    train, _ = generate_synthetic_corpus(n_train=20, n_heldout=10, seed=42)
    assert len(train.train) == 20
    assert len(train.heldout) == 10


def test_n_train_too_small_raises():
    with pytest.raises(ValueError):
        generate_synthetic_corpus(n_train=5, n_heldout=10, seed=42)


def test_n_heldout_too_small_raises():
    with pytest.raises(ValueError):
        generate_synthetic_corpus(n_train=100, n_heldout=5, seed=42)


def test_feature_count_matches_constant():
    assert N_FEATURES == N_FREE_COEFFS + 3


def test_modal_collapse_boundary_avoidance():
    train_clean, _ = generate_synthetic_corpus(n_train=500, n_heldout=100, snr_db=40.0, seed=0)
    res_clean = validate_acceptance_criteria(train_clean)
    train_default, _ = generate_synthetic_corpus(n_train=500, n_heldout=100, snr_db=10.0, seed=0)
    res_default = validate_acceptance_criteria(train_default)
    assert res_default["snr_db"] < res_clean["snr_db"] - 5.0
