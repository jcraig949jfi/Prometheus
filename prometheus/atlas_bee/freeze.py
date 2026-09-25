"""Freeze an adaptation: canonical JSON + sha256 (directive Phase 4).

A frozen prereg is written BEFORE the adaptation is run; a repair is a NEW descendant freeze, never an edit of the
original. Line endings and key order are canonicalised so the hash is recomputable by any reader on any platform
(a freeze record nobody can recompute is decorative). The hash covers the prereg payload ONLY, so a reader checks
sha256_of(record["prereg"]) == record["freeze"]["sha256"].
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

ALGO = "sha256-canonical-json-v1"


def canonical_bytes(obj: Any) -> bytes:
    """UTF-8 bytes of obj as canonical JSON: sorted keys, compact separators, ASCII-escaped, no NaN/Infinity. The
    representation is byte-stable across platforms (no CRLF, no locale), which is what makes the sha256 a reader
    can recompute."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")


def sha256_of(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def freeze(prereg: dict) -> dict:
    """Wrap a prereg in an immutable freeze record. The wrapper carries the algorithm, the digest and the byte
    count; the digest is over the prereg alone so it is independent of the wrapper's own fields."""
    if not isinstance(prereg, dict):
        raise TypeError("freeze() takes a prereg dict")
    b = canonical_bytes(prereg)
    return {"prereg": prereg, "freeze": {"algo": ALGO, "sha256": hashlib.sha256(b).hexdigest(), "canonical_bytes": len(b)}}


def verify(record: dict) -> bool:
    """True iff the record's stored digest matches a fresh canonical digest of its prereg (and the algo is known)."""
    fr = record.get("freeze") or {}
    if fr.get("algo") != ALGO:
        return False
    return sha256_of(record["prereg"]) == fr.get("sha256")
