"""Exact identity of the RUNNING engine build (DFX-3).

`engine_source_hash` is computed at import over the ACTUAL loaded source files of
the `sfe` package (sorted by name, LF-normalized so a checkout's line-ending
convention does not change the identity). It therefore comes from the build the
process is executing -- not from operator attestation -- and any source edit
changes it. `source_commit` is best-effort git metadata (None when the tree is
not a git checkout); the source hash is the authoritative identity.

The identity is exposed on GET /v2/version and stamped into every
EXPERIMENT_COMMITTED event, so each experiment binds to the exact instrument
release that committed it.
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

_PKG = Path(__file__).resolve().parent


def _source_hash() -> str:
    h = hashlib.sha256()
    for p in sorted(_PKG.glob("*.py"), key=lambda p: p.name):
        data = p.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        h.update(p.name.encode("utf-8"))
        h.update(b"\x00")
        h.update(data)
        h.update(b"\x00")
    return "sha256:" + h.hexdigest()


def _git_commit():
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(_PKG),
                           capture_output=True, text=True, timeout=3)
        out = r.stdout.strip()
        return out if r.returncode == 0 and out else None
    except Exception:                                  # noqa: BLE001
        return None


ENGINE_SOURCE_HASH = _source_hash()
SOURCE_COMMIT = _git_commit()


def identity() -> dict:
    return {"engine_source_hash": ENGINE_SOURCE_HASH,
            "source_commit": SOURCE_COMMIT}
