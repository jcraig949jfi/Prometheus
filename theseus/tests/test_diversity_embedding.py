"""Tests for sentence-transformer diversity scoring with Jaccard fallback."""
from __future__ import annotations

import pytest

from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.scoring import diversity as div_mod
from theseus.scoring.diversity import (
    diversity_score,
    use_jaccard_only,
    enable_embedding_diversity,
    _try_load_embedding_model,
)


def _make(text: str) -> TheseusRecord:
    return TheseusRecord(
        record_id=TheseusRecord.compute_record_id(text, "g"),
        generator_id="g",
        batch_id="b",
        emitted_at="2026-05-18T00:00:00Z",
        claim_kind=ClaimKind.INVARIANT_EQUALITY.value,
        claim_payload={},
        canonical_claim_text=text,
        verdict=Verdict.UNVERIFIED.value,
    )


@pytest.fixture(autouse=True)
def _reset_embedding_state():
    """Each test starts with embedding state untried."""
    div_mod._EMBEDDING_MODEL = None
    div_mod._EMBEDDING_AVAILABLE = None
    div_mod._EMBEDDING_CACHE.clear()
    yield
    div_mod._EMBEDDING_MODEL = None
    div_mod._EMBEDDING_AVAILABLE = None
    div_mod._EMBEDDING_CACHE.clear()


def test_diversity_with_jaccard_only_identical():
    use_jaccard_only()
    r = _make("alpha beta gamma")
    r2 = _make("alpha beta gamma")
    assert diversity_score(r, [r2]) == 0.0


def test_diversity_with_jaccard_only_disjoint():
    use_jaccard_only()
    r = _make("alpha beta")
    r2 = _make("delta epsilon")
    assert diversity_score(r, [r2]) == 1.0


def test_diversity_empty_recent_returns_one():
    use_jaccard_only()
    r = _make("anything")
    assert diversity_score(r, []) == 1.0


def test_embedding_model_loads_if_available():
    """Sanity: if sentence-transformers is installed, loading succeeds."""
    try:
        import sentence_transformers  # noqa: F401
    except ImportError:
        pytest.skip("sentence-transformers not installed")
    enable_embedding_diversity()
    model = _try_load_embedding_model()
    assert model is not None


def test_embedding_diversity_distinguishes_semantics():
    """Semantically distant texts should score higher than near-duplicates."""
    try:
        import sentence_transformers  # noqa: F401
    except ImportError:
        pytest.skip("sentence-transformers not installed")
    enable_embedding_diversity()
    a = _make("signature of the knot equals rank of the elliptic curve")
    b = _make("signature of the knot equals rank of the elliptic curve")
    c = _make("the cat sat on the mat and watched the rain fall outside")

    d_identical = diversity_score(a, [b])
    d_unrelated = diversity_score(a, [c])
    assert d_unrelated > d_identical
