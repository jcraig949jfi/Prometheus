"""Diversity scoring.

v0.1: token-set Jaccard distance from recent emissions. Cheap, no
embeddings needed.

Tier-1 replacement: sentence-transformer embedding cosine distance.
"""
from __future__ import annotations

import re
from typing import List

from theseus.emit.record_schema import TheseusRecord


_TOKEN_RE = re.compile(r"\w+")


def _tokens(text: str) -> set:
    return set(_TOKEN_RE.findall(text.lower()))


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    return 1.0 - (len(a & b) / max(len(a | b), 1))


def diversity_score(
    record: TheseusRecord, recent: List[TheseusRecord], window: int = 50
) -> float:
    """Return mean Jaccard distance of `record` from the last `window`
    emissions. Higher = more novel relative to recent corpus.

    Empty recent → score 1.0 (maximally novel by default).
    """
    if not recent:
        return 1.0
    sample = recent[-window:]
    my_tokens = _tokens(record.canonical_claim_text)
    dists = [
        _jaccard(my_tokens, _tokens(r.canonical_claim_text)) for r in sample
    ]
    return sum(dists) / len(dists)
