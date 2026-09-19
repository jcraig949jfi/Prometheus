"""Receipt -- core.receipt.v1 (WORLDS_KERNEL_DESIGN v0.2 s4, s14, s15, s22). The laboratory record.

One receipt per executed RUN (one arm x one sweep point x one seed x one episode set). It says what
happened, what was measured, by which observer version, under which configuration, on which
implementations, at what raw cost, with which replay class. It contains no interpretation.

Two ledgers are kept DISJOINT (NPE rule, kept): `engineering` (throughput, wall, bytes) and
`science` (measures, objective, control outcomes). A key in both is a validation failure.
Receipts are written outside any hot-state device (s23): JSONL, flushed per record.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from typing import Any, Dict, List

SCHEMA = "prometheus.toolbox.receipt.v1"
STATUSES = ("COMPLETED", "FAILED", "BLOCKED_MISSING_CAPABILITY", "TARGET_UNSUPPORTED", "CONTROL_NOT_MET", "INTEGRITY_HALT")
REQUIRED = ("schema", "receipt_id", "experiment_id", "experiment_digest", "arm", "sweep_point", "seed", "status",
            "components", "capabilities", "replay_class", "trace_hashes", "events_total", "engineering", "science",
            "accounting", "host", "build", "started_utc", "finished_utc")


class ReceiptError(ValueError):
    pass


def _h(obj, n=16) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()[:n]


_HOST_CACHE: Dict[str, Any] = {}


def host_block() -> dict:
    """Computed once per process (C107: platform.platform() runs a WMI query on Windows, 2.3 ms per receipt --
    17% of a search generation in the soak's profile; the host does not change under a running process)."""
    if not _HOST_CACHE:
        _HOST_CACHE.update({"platform": platform.platform(), "python": sys.version.split()[0], "machine": platform.node()})
    return dict(_HOST_CACHE)


_BUILD_CACHE: Dict[str, Any] = {}


def build_block(refresh: bool = False) -> dict:
    """Content hashes of the kernel's own modules, so a receipt names the kernel that produced it. Computed once
    per process (C56: recomputed 433 times it was a third of EXP-002's wall time); refresh=True recomputes."""
    if _BUILD_CACHE and not refresh:
        return dict(_BUILD_CACHE)
    import pathlib
    root = pathlib.Path(__file__).resolve().parent
    files = sorted(p for p in root.rglob("*.py") if "tests" not in p.parts and "examples" not in p.parts and "playtests" not in p.parts)
    h = hashlib.sha256()
    for p in files:
        h.update(p.relative_to(root).as_posix().encode()); h.update(p.read_bytes().replace(b"\r\n", b"\n"))
    _BUILD_CACHE.update({"kernel_hash": h.hexdigest()[:16], "n_files": len(files)})
    return dict(_BUILD_CACHE)


def validate(r: dict) -> dict:
    if r.get("schema") != SCHEMA:
        raise ReceiptError("schema")
    missing = [k for k in REQUIRED if k not in r]
    if missing:
        raise ReceiptError("missing %s" % missing)
    if r["status"] not in STATUSES:
        raise ReceiptError("status %r" % r["status"])
    if r["replay_class"] not in ("BIT", "SEMANTIC", "PARTIAL", "NONDETERMINISTIC", "NOT_RUN"):
        raise ReceiptError("replay_class")
    if not isinstance(r["engineering"], dict) or not isinstance(r["science"], dict):
        raise ReceiptError("ledgers must be dicts")
    overlap = set(r["engineering"]) & set(r["science"])
    if overlap:
        raise ReceiptError("metric in both ledgers: %s" % sorted(overlap))
    for slot in ("world", "substrate"):
        if slot not in r["components"]:
            raise ReceiptError("components.%s" % slot)
    if r["receipt_id"] != receipt_id(r):
        raise ReceiptError("receipt_id does not match content")
    return r


def receipt_id(r: dict) -> str:
    body = {k: v for k, v in r.items() if k != "receipt_id"}
    return _h(body, 24)


def finalize(r: dict) -> dict:
    r = dict(r); r["schema"] = SCHEMA
    r.setdefault("host", host_block()); r.setdefault("build", build_block())
    r["receipt_id"] = receipt_id(r)
    return validate(r)


class ReceiptWriter:
    """Append-only JSONL, one flush per record (base-role rule: never a shell redirect; the program writes).
    Receipts CHAIN (C44): each carries prev_receipt_id = the previous receipt's id in this file (None for the
    first), so a deleted middle line is detectable; a writer opened on an existing file continues the chain
    from its last VALID receipt."""

    def __init__(self, path):
        import pathlib
        self.path = pathlib.Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.prev = None
        if self.path.exists() and self.path.stat().st_size > 0:
            last = None
            with open(self.path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        last = validate(json.loads(line))["receipt_id"]
                    except (ValueError, ReceiptError):
                        pass
            self.prev = last
        self._f = open(self.path, "a", encoding="utf-8", newline="\n")
        self.n = 0

    def write(self, r: dict) -> dict:
        r = dict(r); r["prev_receipt_id"] = self.prev
        r = finalize(r)
        self._f.write(json.dumps(r, sort_keys=True, separators=(",", ":"), default=str) + "\n"); self._f.flush()
        self.n += 1; self.prev = r["receipt_id"]
        return r

    def close(self) -> None:
        self._f.close()


def read_all(path) -> List[dict]:
    """STRICT read: every line must be a valid receipt; any defect raises ReceiptError naming the line (C10)."""
    out = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                raise ReceiptError("line %d: TRUNCATED_OR_MALFORMED_JSON" % n)
            try:
                rec = validate(rec)
            except ReceiptError as exc:
                raise ReceiptError("line %d: %s" % (n, exc))
            if "prev_receipt_id" in rec and rec["prev_receipt_id"] != (out[-1]["receipt_id"] if out else None):
                raise ReceiptError("line %d: CHAIN_BREAK (prev_receipt_id does not name the previous receipt)" % n)
            out.append(rec)
    return out


def scan(path) -> dict:
    """FORENSIC read: never raises; counts valid receipts and names every defect by line
    (truncation / malformed JSON, receipt_id mismatch = edited after writing, schema defects, duplicates)."""
    valid = 0; defects = []; ids = []; seen = set(); lines = 0
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            lines += 1
            try:
                rec = json.loads(line)
            except ValueError:
                defects.append({"line": n, "defect": "TRUNCATED_OR_MALFORMED_JSON"}); continue
            try:
                validate(rec)
            except ReceiptError as exc:
                msg = str(exc)
                defects.append({"line": n, "defect": ("RECEIPT_ID_MISMATCH" if "receipt_id" in msg else "SCHEMA:" + msg)}); continue
            rid = rec["receipt_id"]
            if rid in seen:
                defects.append({"line": n, "defect": "DUPLICATE_RECEIPT_ID", "receipt_id": rid}); continue   # a copy is not a second run
            if "prev_receipt_id" in rec and rec["prev_receipt_id"] != (ids[-1] if ids else None):
                defects.append({"line": n, "defect": "CHAIN_BREAK", "expected_prev": ids[-1] if ids else None, "found_prev": rec["prev_receipt_id"]})
            seen.add(rid); ids.append(rid); valid += 1
    return {"path": str(path), "lines": lines, "valid": valid, "defects": defects, "receipt_ids": ids}
