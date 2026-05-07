"""E002 acceptance-gate tests for the synthetic env (W3.1).

Thin gate-level wrapper of the 3 locked acceptance criteria documented in
`ergon/diagnostic_c/SYNTHETIC_ENV_ACCEPTANCE.md`. Deeper unit tests + edge
cases live in `test_synthetic_env.py`; this file's job is to be the single
file a maintainer can run to confirm the env still meets all 3 criteria
under default config — exactly the gate Aporia's W2.5 sign-off depends on.
"""
from __future__ import annotations

import pytest

from ergon.diagnostic_c.synthetic_env import (
    generate_synthetic_corpus,
    validate_acceptance_criteria,
)


@pytest.fixture(scope="module")
def default_corpus():
    """Default-config corpus: n_train=1000, n_heldout=200, snr_db=10, seed=42."""
    train, _ = generate_synthetic_corpus(
        n_train=1000, n_heldout=200, snr_db=10.0, seed=42,
    )
    return train


@pytest.fixture(scope="module")
def default_result(default_corpus):
    return validate_acceptance_criteria(default_corpus)


def test_criterion_1_lsq_baseline_above_85(default_result):
    """Criterion 1: LSQ-baseline recoverability >85% on held-out clean data."""
    assert default_result["criterion_1_pass"], (
        f"LSQ baseline {default_result['lsq_baseline_accuracy']:.3f} did not exceed 0.85 floor"
    )


def test_criterion_2_snr_in_documented_range(default_result):
    """Criterion 2: SNR in 5-20 dB (not modal-collapse boundary, not trivial)."""
    assert default_result["criterion_2_pass"], (
        f"SNR {default_result['snr_db']:.2f} dB outside [5, 20]"
    )


def test_criterion_3_feature_space_similarity_documented(default_result):
    """Criterion 3: feature-space similarity claim is documented (qualitative)."""
    claim = default_result["feature_space_similarity"]
    assert isinstance(claim, str) and len(claim) > 50, "feature-space claim missing"
    assert default_result["criterion_3_pass"]


def test_all_three_criteria_pass_under_default_config(default_result):
    """Single-call gate check: all 3 must pass under the default config."""
    assert default_result["all_pass"], (
        f"Synthetic env fails acceptance gate: {default_result}"
    )


def test_lsq_below_85_fails_criterion_1():
    """Negative-direction sanity: at SNR=-10 dB the LSQ baseline drops below 0.85."""
    corpus, _ = generate_synthetic_corpus(
        n_train=500, n_heldout=200, snr_db=-10.0, seed=42,
    )
    result = validate_acceptance_criteria(corpus)
    assert not result["criterion_1_pass"]
    assert not result["all_pass"]


def test_snr_too_clean_fails_criterion_2():
    """Negative-direction sanity: at SNR=40 dB the gate flags 'too clean'."""
    corpus, _ = generate_synthetic_corpus(
        n_train=500, n_heldout=200, snr_db=40.0, seed=42,
    )
    result = validate_acceptance_criteria(corpus)
    assert not result["criterion_2_pass"]
    assert not result["all_pass"]


def test_acceptance_doc_exists():
    """The sibling MD doc must exist so Aporia/maintainers don't need to read code."""
    from pathlib import Path

    doc = Path("ergon/diagnostic_c/SYNTHETIC_ENV_ACCEPTANCE.md")
    assert doc.exists(), f"Acceptance doc missing: {doc}"
    text = doc.read_text(encoding="utf-8")
    # Quick load-bearing-content check
    for required in ("Criterion 1", "Criterion 2", "Criterion 3", "validate_acceptance_criteria", "Aporia"):
        # case-insensitive heading or content match
        assert required.lower() in text.lower(), f"Missing required content: {required!r}"
