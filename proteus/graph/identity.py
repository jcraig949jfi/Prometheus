"""Identity of the graph runtime (proteus.runtime.graph.v1): sha256 over the LF-normalised sources
plus the node-kind table hash. Mirrors proteus/foundry/identity.py; independent of it, so the v0
runtime hash (73f110e2...) is untouched by anything in this package.
"""
from __future__ import annotations

import hashlib
import os

from proteus.foundry.identity import canonical_json, hash_obj, sha256_hex  # noqa: F401  (shared helpers)

GRAPH_DIR = os.path.dirname(os.path.abspath(__file__))
RUNTIME_SOURCE_FILES = ("affordances.py", "vm.py", "grammar.py")
RUNTIME_VERSION = "proteus.runtime.graph.v1"


def _read_lf(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read().replace(b"\r\n", b"\n")


def runtime_identity() -> dict:
    from . import affordances
    h = hashlib.sha256()
    per_file = {}
    for name in RUNTIME_SOURCE_FILES:
        b = _read_lf(os.path.join(GRAPH_DIR, name))
        d = hashlib.sha256(b).hexdigest()
        per_file[name] = d
        h.update(name.encode() + b"\x00" + d.encode() + b"\x00")
    h.update(b"affordance:" + affordances.AFFORDANCE_HASH.encode())
    return {
        "runtime_version": RUNTIME_VERSION,
        "runtime_hash": h.hexdigest(),
        "affordance_hash": affordances.AFFORDANCE_HASH,
        "source_files": per_file,
    }


RUNTIME = runtime_identity()
RUNTIME_HASH = RUNTIME["runtime_hash"]
