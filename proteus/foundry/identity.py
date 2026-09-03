"""Content-addressed identities. Everything the fossil record points at is a sha256 of canonical bytes."""
from __future__ import annotations

import hashlib
import json
import os

FOUNDRY_DIR = os.path.dirname(os.path.abspath(__file__))

RUNTIME_SOURCE_FILES = ("affordances.py", "vm.py")


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_hex(data) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def hash_obj(obj) -> str:
    return sha256_hex(canonical_json(obj))


def _read_lf(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read().replace(b"\r\n", b"\n")


def runtime_identity() -> dict:
    """sha256 over the LF-normalised runtime sources plus the affordance hash.

    Line endings are normalised so a CRLF checkout on Windows yields the same identity as the
    committed LF blob; the identity is of the program, not of the platform's checkout.
    """
    from . import affordances
    h = hashlib.sha256()
    per_file = {}
    for name in RUNTIME_SOURCE_FILES:
        b = _read_lf(os.path.join(FOUNDRY_DIR, name))
        d = hashlib.sha256(b).hexdigest()
        per_file[name] = d
        h.update(name.encode() + b"\x00" + d.encode() + b"\x00")
    h.update(b"affordance:" + affordances.AFFORDANCE_HASH.encode())
    return {
        "runtime_version": "proteus.runtime.v0",
        "runtime_hash": h.hexdigest(),
        "affordance_hash": affordances.AFFORDANCE_HASH,
        "source_files": per_file,
    }


RUNTIME = runtime_identity()
RUNTIME_HASH = RUNTIME["runtime_hash"]
