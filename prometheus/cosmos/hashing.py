"""Content identity and chained receipts.

Hash recipe borrowed (concept, not import) from prometheus/toolbox/receipt.py `_h`:
sha256 over canonical JSON (sort_keys, compact separators). Cosmos keeps full
64-hex digests; short forms are for display only.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def canon(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=_default)


def _default(o: Any):
    try:
        import numpy as np
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
    except ImportError:  # pragma: no cover
        pass
    if isinstance(o, (set, frozenset)):
        return sorted(o)
    raise TypeError("not canonicalisable: %r" % type(o))


def h(obj: Any) -> str:
    return hashlib.sha256(canon(obj).encode("utf-8")).hexdigest()


def file_sha(path: Path) -> str:
    """sha256 over LF-normalised bytes (equals the git blob content hash input)."""
    data = Path(path).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def code_identity() -> Dict[str, Any]:
    """Runtime identity: git HEAD, dirty flag, and a hash over the cosmos package sources."""
    root = Path(__file__).resolve().parent
    srcs = sorted(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)
    pkg = hashlib.sha256()
    for p in srcs:
        pkg.update(p.relative_to(root).as_posix().encode())
        pkg.update(file_sha(p).encode())
    out = {"cosmos_src_sha": pkg.hexdigest(), "n_src": len(srcs)}
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, timeout=20)
        dirty = subprocess.run(["git", "status", "--porcelain", "--", str(root)], cwd=root, capture_output=True,
                               text=True, timeout=20)
        out["git_head"] = head.stdout.strip() or None
        out["cosmos_dirty"] = bool(dirty.stdout.strip())
    except Exception as e:  # pragma: no cover - git absent
        out["git_head"] = None
        out["git_error"] = repr(e)
    return out


class ReceiptChain:
    """Append-only JSONL; each record carries prev and its own content id.

    A record's id = h(record without 'id'). Tampering with any record breaks
    verify() at that record and every later link.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._last = None
        if self.path.exists():
            recs = self.read()
            if recs:
                self._last = recs[-1]["id"]

    def append(self, kind: str, body: Dict[str, Any]) -> str:
        rec = {"kind": kind, "prev": self._last, "t": round(time.time(), 3), "body": body}
        rec["id"] = h(rec)
        with open(self.path, "a", encoding="utf-8", newline="\n") as f:
            f.write(canon(rec) + "\n")
            f.flush()
            os.fsync(f.fileno())
        self._last = rec["id"]
        return rec["id"]

    def read(self) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        with open(self.path, encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def verify(self) -> Optional[int]:
        """Return None if the chain verifies, else the index of the first bad record."""
        prev = None
        for i, rec in enumerate(self.read()):
            body = {k: v for k, v in rec.items() if k != "id"}
            if rec.get("prev") != prev or h(body) != rec.get("id"):
                return i
            prev = rec["id"]
        return None


def cosmos_home() -> Path:
    """Operational state lives outside git (M2 D: is an SMR disk; default is the user profile on C:)."""
    p = Path(os.environ.get("COSMOS_HOME") or (Path.home() / "cosmos_runs"))
    p.mkdir(parents=True, exist_ok=True)
    return p


def derive_seed(*parts: Iterable[Any]) -> int:
    """Seeds derive from named parts through sha256, so families never share streams by accident."""
    return int(h(list(parts))[:15], 16)
