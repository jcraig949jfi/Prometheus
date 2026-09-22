"""One canonical digest representation on both sides of the client (campaign 2, group F).

The engine returns artifact ids and blob hashes as 'sha256:<hex>'; local hashing produced
bare hex; campaign 1 compared the two three times and got it wrong twice (L-009, rec 1).
Every comparison in campaign 2 goes through same(); every stored digest is canon().
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Optional

PREFIX = "sha256:"


def canon(d: Optional[str]) -> Optional[str]:
    """'sha256:<hex>' from either form; None stays None; anything else is returned lower-cased
    with the prefix (a caller comparing an id to a digest gets False, never a spurious True)."""
    if d is None:
        return None
    s = str(d).strip().lower()
    if s.startswith(PREFIX):
        s = s[len(PREFIX):]
    return PREFIX + s


def hexof(d: Optional[str]) -> Optional[str]:
    c = canon(d)
    return None if c is None else c[len(PREFIX):]


def same(a: Optional[str], b: Optional[str]) -> bool:
    return a is not None and b is not None and canon(a) == canon(b)


def of_bytes(b: bytes) -> str:
    return PREFIX + hashlib.sha256(b).hexdigest()


def of_obj(o: Any) -> str:
    return of_bytes(json.dumps(o, sort_keys=True, separators=(",", ":")).encode())


def canonical_bytes(o: Any) -> bytes:
    """The byte form every artifact is published in (sorted keys, no whitespace), so the
    digest a reader recomputes from the fetched bytes equals the one the publisher declared."""
    return json.dumps(o, sort_keys=True, separators=(",", ":")).encode()
