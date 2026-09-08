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
    "claim": "clm", "group": "grp", "family": "fam", "grant": "gnt",
    "scope": "scp",
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


# ---------------------------------------------------------------------------
# Session affinity keys (v5)
#
# Format:  sfes_<engine-instance-hex>_<random>
#
# The engine instance id is carried IN THE KEY, in the clear, on purpose. It is
# what lets an engine answer "this key is not mine" from the key's own bytes,
# before any lookup -- so a key minted by a sibling engine is never confused
# with a random string or a missing row. It is not a secret (verify_anchor and
# the audit envelope already publish it); the entropy lives in the tail.
#
# Nothing here hardcodes a machine. An engine instance id is minted per
# database, so M1..M50, ephemeral VMs and containers all work unchanged.
# ---------------------------------------------------------------------------
SESSION_KEY_PREFIX = "sfes"
_ENGINE_PREFIX = "eng_"


def session_key_for(engine_instance_id: str) -> str:
    """Mint a session key bound to this engine instance."""
    if not engine_instance_id.startswith(_ENGINE_PREFIX):
        raise ValueError("engine_instance_id must start with 'eng_'")
    body = engine_instance_id[len(_ENGINE_PREFIX):]
    return f"{SESSION_KEY_PREFIX}_{body}_{secrets.token_urlsafe(24)}"


def engine_id_from_key(key: str) -> Any:
    """The engine instance id a key CLAIMS, or None if it is not a session key.

    Parsing only -- this asserts nothing about validity. A well-formed key from
    a foreign engine parses fine; that is the point."""
    if not isinstance(key, str):
        return None
    # token_urlsafe emits "-" and "_", so the tail may itself contain
    # underscores: split only the two structural separators.
    parts = key.split("_", 2)
    if len(parts) != 3 or parts[0] != SESSION_KEY_PREFIX:
        return None
    body, tail = parts[1], parts[2]
    if len(body) != 24 or any(c not in "0123456789abcdef" for c in body):
        return None
    if len(tail) < 16:
        return None
    return _ENGINE_PREFIX + body


def key_fingerprint(key: str) -> str:
    """A safe, stable handle for logs and metrics. NEVER log the key itself:
    it is bearer-like, and a log line is a credential leak."""
    return "sfp_" + sha256_hex(key.encode())[:16]
