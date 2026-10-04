"""Apparatus identity. Every v2b experiment records APPARATUS_ID: a sha256 over the content hashes of every
module it can import, plus the instrument selection. Two runs with equal APPARATUS_ID ran the same apparatus.
CRLF/LF differences are normalised (line endings are not apparatus)."""
import hashlib
import json
from pathlib import Path

from paths import ENG, RB1, V2B

APPARATUS_VERSION = "v2b-2"   # keep equal to __init__.APPARATUS_VERSION

# The frozen engine modules the v2b layer imports (directly or transitively).
ENGINE_MODULES = [
    "engine.py", "basis_v4.py", "fair.py", "identity.py", "tier3d.py", "a17.py", "a18.py", "a18_c1.py",
    "tribunal_t4.py", "meta_tribunal.py", "accel/fasteval.py",
]
V2B_MODULES = ["__init__.py", "paths.py", "apparatus.py", "gates.py", "walk.py", "capability.py", "supply.py",
               "instruments.py", "tribunal_t4_v1a.py", "ruler_v21.py"]


def _h(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def manifest(tribunal="v1a", ruler="v2.1"):
    files = {}
    for m in ENGINE_MODULES:
        p = ENG / m
        if p.exists():
            files["engine/" + m] = _h(p)
    for m in V2B_MODULES:
        p = V2B / m
        if p.exists():
            files["engine/v2b/" + m] = _h(p)
    files["science/compounding/rb1/ruler_v2.py"] = _h(RB1 / "ruler_v2.py")
    body = {"instruments": {"tribunal": tribunal, "ruler": ruler}, "files": files}
    body["apparatus_version"] = APPARATUS_VERSION
    body["apparatus_id"] = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()[:16]
    return body


if __name__ == "__main__":
    print(json.dumps(manifest(), indent=1))
