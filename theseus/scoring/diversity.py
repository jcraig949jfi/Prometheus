"""Diversity scoring.

v0.2: sentence-transformer embedding cosine distance (all-MiniLM-L6-v2,
384-dim, MIT-licensed). Falls back to Jaccard token-set distance if
sentence-transformers isn't available.

Per-record embeddings are cached by record_id (content-addressed) so
re-scoring against a moving window doesn't re-encode.

For batches > LARGE_BATCH_THRESHOLD the daemon may switch to Jaccard
to keep throughput up; that decision is made at the daemon level via
the `diversity_mode` config knob (Tier-1).
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional

from theseus.emit.record_schema import TheseusRecord


_TOKEN_RE = re.compile(r"\w+")

# Lazy-loaded sentence-transformers state. DEFAULT IS JACCARD MODE.
# Empirical Fire #3 result: sentence-transformer encode-per-record drops
# throughput 15x (85K → 5.5K records/30s). Embedding mode is opt-in via
# enable_embedding_diversity() — useful for periodic deep-diversity
# checks or smaller batches; throughput-mode batches stay on Jaccard.
_EMBEDDING_MODEL = None
_EMBEDDING_AVAILABLE: Optional[bool] = False  # default OFF
_EMBEDDING_CACHE: Dict[str, "object"] = {}  # record_id -> np.ndarray


def _try_load_embedding_model():
    """Try to load sentence-transformers model once; cache result."""
    global _EMBEDDING_MODEL, _EMBEDDING_AVAILABLE
    if _EMBEDDING_AVAILABLE is False:
        return None
    if _EMBEDDING_AVAILABLE is True and _EMBEDDING_MODEL is not None:
        return _EMBEDDING_MODEL
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
        _EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        _EMBEDDING_AVAILABLE = True
    except Exception:
        _EMBEDDING_AVAILABLE = False
        _EMBEDDING_MODEL = None
    return _EMBEDDING_MODEL


def enable_embedding_diversity() -> None:
    """Opt in to embedding-based diversity scoring.

    Slow (~15x slowdown vs Jaccard). Use for periodic deep-diversity
    checks, not for throughput-mode batches.
    """
    global _EMBEDDING_AVAILABLE, _EMBEDDING_MODEL
    _EMBEDDING_AVAILABLE = None  # untried → try to load on next call
    _EMBEDDING_MODEL = None


def use_jaccard_only() -> None:
    """Force Jaccard mode (skip embedding model load).

    Useful in tests and for throughput-mode batches (the default).
    """
    global _EMBEDDING_AVAILABLE, _EMBEDDING_MODEL
    _EMBEDDING_AVAILABLE = False
    _EMBEDDING_MODEL = None


def _tokens(text: str) -> set:
    return set(_TOKEN_RE.findall(text.lower()))


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    return 1.0 - (len(a & b) / max(len(a | b), 1))


def _jaccard_diversity(
    record: TheseusRecord, recent: List[TheseusRecord]
) -> float:
    my_tokens = _tokens(record.canonical_claim_text)
    dists = [_jaccard(my_tokens, _tokens(r.canonical_claim_text)) for r in recent]
    return sum(dists) / len(dists)


def _get_embedding(record: TheseusRecord, model):
    cached = _EMBEDDING_CACHE.get(record.record_id)
    if cached is not None:
        return cached
    emb = model.encode(record.canonical_claim_text, show_progress_bar=False)
    _EMBEDDING_CACHE[record.record_id] = emb
    # Bound cache size; LRU isn't worth the overhead at this scale.
    if len(_EMBEDDING_CACHE) > 5000:
        # Drop ~half: keep most-recently-added.
        keys = list(_EMBEDDING_CACHE.keys())
        for k in keys[: len(keys) // 2]:
            del _EMBEDDING_CACHE[k]
    return emb


def _embedding_diversity(
    record: TheseusRecord, recent: List[TheseusRecord], model
) -> float:
    import numpy as np  # type: ignore

    my_emb = _get_embedding(record, model)
    my_norm = my_emb / max(float(np.linalg.norm(my_emb)), 1e-9)
    sims = []
    for r in recent:
        emb = _get_embedding(r, model)
        n = max(float(np.linalg.norm(emb)), 1e-9)
        sims.append(float(my_norm @ (emb / n)))
    if not sims:
        return 1.0
    return float(1.0 - sum(sims) / len(sims))


def diversity_score(
    record: TheseusRecord, recent: List[TheseusRecord], window: int = 50
) -> float:
    """Return diversity in [0, 1]: higher = more novel relative to recent.

    Uses sentence-transformer embeddings if available, else Jaccard.
    Empty recent → 1.0 by convention.
    """
    if not recent:
        return 1.0
    sample = recent[-window:]
    model = _try_load_embedding_model()
    if model is not None:
        try:
            return _embedding_diversity(record, sample, model)
        except Exception:
            pass  # any embedding failure → fall back to Jaccard
    return _jaccard_diversity(record, sample)
