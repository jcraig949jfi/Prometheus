"""R36 -- FOSSIL_WORLD_MANIFEST canonicalization (Amendment 3, 2026-09-16; built 2026-09-18 on Nyx #358 ASK 1).

FOSSIL_WORLD identity must be host-independent:
    canonical encoding = UTF-8, LF, canonical JSON, keys sorted, arrays with DEFINED ordering,
    exactly one terminal LF; versions are strings; no timestamps, hostnames, temporary paths or
    image ids in the semantic manifest.  FOSSIL_WORLD_ID = SHA256(canonical_manifest_bytes).
    Runtime witnesses (image digests, container ids, interpreter paths) are attached SEPARATELY.

Package entries sort by (normalized package name, architecture, version string); toolchains by
(tool class, canonical name, version string); environment variables by name and carry only the
semantic value the world requires.

This module does not replace packet.fossil_world_id() (R21, measurement over dockerfile sha +
package manifest sha + probes, ids 'fw-...'); it adds the R36 form with ids 'fw2-...'.  A world may
carry both until every packet has migrated.  Fixtures: techne/tests/test_world_manifest.py.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Iterable

SCHEMA = "techne.fossil.world_manifest/1"
EPHEMERAL_KEYS = {"host", "hostname", "timestamp", "written_utc", "image_id", "image_digest", "container_id",
                  "executable", "path", "tmp", "tmpdir", "pid", "session"}


def normalize_name(name: str) -> str:
    """PEP 503 style: lowercase, runs of -_. collapse to '-'."""
    return re.sub(r"[-_.]+", "-", name.strip()).lower()


def _pkg(p: dict) -> dict:
    return {"name": normalize_name(str(p["name"])), "arch": str(p.get("arch", "noarch")), "version": str(p["version"])}


def _tool(t: dict) -> dict:
    return {"class": str(t["class"]), "name": str(t["name"]), "version": str(t["version"])}


def canonical_dict(world: dict) -> dict:
    """The semantic manifest as a plain dict, ephemeral keys refused, arrays sorted as R36 says."""
    for k in world:
        if k in EPHEMERAL_KEYS:
            raise ValueError("ephemeral key %r does not belong in a semantic world manifest (attach it as a RUNTIME_WITNESS)" % k)
    if "name" not in world or "class" not in world:
        raise ValueError("world needs 'name' and 'class'")
    out = {
        "schema": SCHEMA,
        "name": str(world["name"]),
        "class": str(world["class"]),
        "architecture": str(world.get("architecture", "")),
        "interpreter": {k: str(v) for k, v in sorted((world.get("interpreter") or {}).items())},
        "packages": sorted((_pkg(p) for p in world.get("packages", [])), key=lambda p: (p["name"], p["arch"], p["version"])),
        "toolchains": sorted((_tool(t) for t in world.get("toolchains", [])), key=lambda t: (t["class"], t["name"], t["version"])),
        "env": sorted(({"name": str(e["name"]), "value": str(e.get("value", ""))} for e in world.get("env", [])), key=lambda e: e["name"]),
        "base": {k: str(v) for k, v in sorted((world.get("base") or {}).items())},
    }
    return out


def canonical_bytes(world: dict) -> bytes:
    d = canonical_dict(world)
    s = json.dumps(d, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False)
    return (s + "\n").encode("utf-8")


def world_id(world: dict) -> str:
    return "fw2-" + hashlib.sha256(canonical_bytes(world)).hexdigest()


def parse_manifest_text(text: str) -> dict:
    """A manifest read back from disk, whatever its line endings: CRLF and LF parse to the same dict."""
    return json.loads(text.replace("\r\n", "\n"))


def native_python_world(name: str, packages: Iterable[tuple[str, str]], python_version: str,
                        implementation: str = "CPython", architecture: str = "x86_64") -> dict:
    """A world = an interpreter + a frozen package set. No path, no host."""
    return {"name": name, "class": "native_python", "architecture": architecture,
            "interpreter": {"implementation": implementation, "version": python_version},
            "packages": [{"name": n, "version": v, "arch": "noarch"} for n, v in packages],
            "toolchains": [], "env": [], "base": {}}


def this_interpreter_world(name: str) -> dict:
    """The running interpreter as a world (semantic part only; the witness is separate)."""
    import platform
    from importlib import metadata
    seen = {}
    for d in metadata.distributions():
        n = d.metadata["Name"] if d.metadata else None
        if not n:
            continue
        seen[normalize_name(n)] = str(d.version)
    return native_python_world(name, sorted(seen.items()), platform.python_version(),
                               platform.python_implementation(), platform.machine().lower() or "x86_64")


def runtime_witness_for_this_interpreter() -> dict:
    """What R36 keeps OUT of the manifest and attaches beside it."""
    import platform
    import sys
    import hashlib as _h
    from importlib import metadata
    lines = sorted({"%s==%s" % (normalize_name(d.metadata["Name"]), d.version) for d in metadata.distributions() if d.metadata and d.metadata["Name"]})
    return {"kind": "native_python_interpreter", "executable_basename": sys.executable.replace("\\", "/").split("/")[-1],
            "platform": platform.platform(), "pip_freeze_sha256": _h.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest(),
            "n_distributions": len(lines)}
