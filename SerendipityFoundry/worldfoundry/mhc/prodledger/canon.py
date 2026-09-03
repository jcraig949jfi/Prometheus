"""Canonical serialization and candidate identity.

Identity is where counterfeits start: two syntactically distinct encodings of
one candidate must collapse to one id, and two genuinely different candidates
must never collide by encoding tricks. Rules:

  * strict schema whitelist -- unknown keys are REFUSED, not ignored;
  * NFC unicode normalization on every string (composed/decomposed forms of
    the same text are the same text);
  * explicit-default values are elided (omitted-default == explicit-default);
  * duplicate keys in the raw JSON are REFUSED (parsers that keep the last
    key silently would otherwise let two texts share one parse);
  * sorted keys, compact separators, ASCII-escaped output;
  * integers only for numerics (floats REFUSED -- no float has a canonical
    text form we are willing to bet money on).
"""
from __future__ import annotations

import hashlib
import json
import unicodedata


class CanonError(Exception):
    pass


CANDIDATE_SCHEMA = {
    # field           (type, required, default)
    "schema_version": (str, True, None),
    "namespace":      (str, True, None),          # SCIENTIFIC | CALIBRATION
    "family_id":      (str, True, None),
    "subject":        (str, True, None),          # content address of hypothesis subject
    "delta_star":     (str, True, None),          # content address of candidate perturbation
    "ref_rule":       (str, True, None),          # validated template instance hash (R)
    "context_rule":   (str, True, None),          # validated template instance hash (W)
    "role_rule":      (str, True, None),          # validated template instance hash (Pi)
    "tie_rule":       (str, True, None),          # validated template instance hash (tau)
    "detector":       (str, True, None),          # sealed inference-artifact hash (V)
    "betting_rule":   (str, True, None),          # committed predictable rule hash (beta)
    "K":              (int, True, None),
    "block_budget":   (int, True, None),
    "m_refs":         (int, False, 3),
    "selection_blocks": (list, False, []),        # block ids used to SELECT the candidate
}


def _reject_dup_keys(pairs):
    seen = set()
    for k, _ in pairs:
        if k in seen:
            raise CanonError(f"duplicate key in raw JSON: {k!r}")
        seen.add(k)
    return dict(pairs)


def parse_strict(raw: str) -> dict:
    try:
        return json.loads(raw, object_pairs_hook=_reject_dup_keys)
    except CanonError:
        raise
    except Exception as e:
        raise CanonError(f"unparseable: {e}")


def canonical_candidate(d: dict) -> dict:
    """Validate against the whitelist and return the canonical form."""
    if not isinstance(d, dict):
        raise CanonError("candidate must be an object")
    for k in d:
        if k not in CANDIDATE_SCHEMA:
            raise CanonError(f"unknown field REFUSED: {k!r}")
    out = {}
    for k, (typ, required, default) in CANDIDATE_SCHEMA.items():
        if k in d:
            v = d[k]
        elif required:
            raise CanonError(f"missing required field: {k}")
        else:
            v = default
        if typ is int:
            if isinstance(v, bool) or not isinstance(v, int):
                raise CanonError(f"{k}: integer required (floats refused)")
        elif typ is str:
            if not isinstance(v, str):
                raise CanonError(f"{k}: string required")
            v = unicodedata.normalize("NFC", v)
        elif typ is list:
            if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
                raise CanonError(f"{k}: list of strings required")
            v = sorted(unicodedata.normalize("NFC", x) for x in v)
        if not required and v == default:
            continue                       # elide explicit defaults
        out[k] = v
    return out


def canon_bytes(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("ascii")


def candidate_id(d: dict) -> str:
    return "cand-" + hashlib.sha256(canon_bytes(canonical_candidate(d))).hexdigest()[:24]


def event_hash(prev_hash: str, event: dict) -> str:
    return hashlib.sha256(prev_hash.encode("ascii") + canon_bytes(event)).hexdigest()
