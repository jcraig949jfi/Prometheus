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


def host_block() -> dict:
    return {"platform": platform.platform(), "python": sys.version.split()[0], "machine": platform.node()}


def build_block() -> dict:
    """Content hashes of the kernel's own modules, so a receipt names the kernel that produced it."""
    import pathlib
    root = pathlib.Path(__file__).resolve().parent
    files = sorted(p for p in root.rglob("*.py") if "tests" not in p.parts and "examples" not in p.parts)
    h = hashlib.sha256()
    for p in files:
        h.update(p.relative_to(root).as_posix().encode()); h.update(p.read_bytes().replace(b"\r\n", b"\n"))
    return {"kernel_hash": h.hexdigest()[:16], "n_files": len(files)}


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
    """Append-only JSONL, one flush per record (base-role rule: never a shell redirect; the program writes)."""

    def __init__(self, path):
        import pathlib
        self.path = pathlib.Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._f = open(self.path, "a", encoding="utf-8", newline="\n")
        self.n = 0

    def write(self, r: dict) -> dict:
        r = finalize(r)
        self._f.write(json.dumps(r, sort_keys=True, separators=(",", ":"), default=str) + "\n"); self._f.flush()
        self.n += 1
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
                out.append(validate(rec))
            except ReceiptError as exc:
                raise ReceiptError("line %d: %s" % (n, exc))
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
            seen.add(rid); ids.append(rid); valid += 1
    return {"path": str(path), "lines": lines, "valid": valid, "defects": defects, "receipt_ids": ids}
