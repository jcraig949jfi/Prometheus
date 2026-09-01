"""Identity and hashing for Gen-2. Self-contained (no dependency on the pinned
foundry release), so the Gen-2 runtime is a clean separate artifact.

IDs are opaque, prefixed, sortable-by-time-of-issue only loosely (a random
suffix guarantees uniqueness under concurrency without a central counter).
Content hashing is canonical (sorted keys, UTF-8, no whitespace) so the same
logical object always hashes identically -- the basis of the event chain and of
content-addressed artifacts.
"""

from __future__ import annotations

import hashlib
import json
import secrets
from typing import Any

# id prefixes make an id self-describing and make cross-kind confusion a visible
# error rather than a silent one.
PREFIX = {
    "foundry": "fdy", "client": "cli", "session": "ses", "world": "wld",
    "event": "evt", "work": "wrk", "worker": "wkr", "hypothesis": "hyp",
    "prediction": "prd", "experiment": "exp", "observation": "obs",
    "failure": "fai", "artifact": "art", "checkpoint": "ckp", "edge": "edg",
    "measurement": "mea", "import": "imp", "erratum": "err",
}


def new_id(kind: str) -> str:
    p = PREFIX.get(kind)
    if p is None:
        raise ValueError(f"unknown id kind {kind!r}")
    return f"{p}_{secrets.token_hex(12)}"


def kind_of(id_str: str) -> str:
    head = id_str.split("_", 1)[0]
    for k, p in PREFIX.items():
        if p == head:
            return k
    return "unknown"


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def content_hash(obj: Any) -> str:
    """A content address for a JSON-serializable object."""
    return "sha256:" + sha256_hex(canonical_bytes(obj))


def blob_hash(data: bytes) -> str:
    return "sha256:" + sha256_hex(data)
