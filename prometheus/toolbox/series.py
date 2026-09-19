"""Observation SERIES as durable receipt data (U3 ruling, operator 2026-09-19 s3).

A series is what an Observer records per tick, per episode: integer records of a fixed width. The
receipt carries, per observer kind, a SeriesRecord:

    status        PRESENT | EMPTY | DISABLED | BOUND_EXCEEDED       (written by the executor)
                  MISSING | MISSING_ARTIFACT | CORRUPT              (found by verify(), never written)
    encoding      "int_records_v1"   records are lists of ints; episodes are lists of records
    record_width  ints per record (0 when no record was produced)
    n_episodes, n_records, n_records_dropped
    bound         {"max_records": int|null, "max_inline_records": int}
    series_hash   sha256 over the canonical encoding of ALL kept records (identity; equal across BIT replay)
    replay_class  the world's class at execution (BIT: equal seeds -> equal series_hash)
    inline        the episodes themselves, when n_records <= max_inline_records
    artifact      {"path", "sha256", "bytes"} otherwise: a content-addressed file beside the receipt
                  whose hash is part of the receipt (receipt_id covers it)

Rules: a StateDevice may mirror a series during execution but is never the sole copy; a declared bound
drops records deterministically (the first max_records are kept, the rest counted) and says so in the
status; there is no undeclared truncation anywhere. recover() returns the episodes from inline data or
the artifact; verify() classifies without mutating the receipt.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Dict, List, Optional

ENCODING = "int_records_v1"
DEFAULT_MAX_INLINE = 512
ARTIFACT_DIR = "artifacts"
WRITTEN_STATUSES = ("PRESENT", "EMPTY", "DISABLED", "BOUND_EXCEEDED")


def canonical(episodes: List[List[List[int]]]) -> bytes:
    return json.dumps(episodes, separators=(",", ":")).encode()


def series_hash(episodes) -> str:
    return hashlib.sha256(canonical(episodes)).hexdigest()


def build(episodes: Optional[List[List[List[int]]]], *, enabled: bool, replay_class: str, max_records: Optional[int],
          max_inline: int, receipt_dir: pathlib.Path, columns: Optional[List[str]] = None) -> dict:
    """Build the SeriesRecord for one observer over one run. Writes the artifact file when needed. `columns`
    (C53) names every position of a record, from the observer, so a reader never guesses a layout."""
    if not enabled:
        return {"status": "DISABLED", "encoding": ENCODING, "record_width": 0, "n_episodes": 0, "n_records": 0, "n_records_dropped": 0,
                "bound": {"max_records": max_records, "max_inline_records": max_inline}, "series_hash": series_hash([]), "replay_class": replay_class,
                "columns": list(columns or [])}
    episodes = [[list(int(x) for x in rec) for rec in ep] for ep in (episodes or [])]
    total = sum(len(ep) for ep in episodes); dropped = 0
    if max_records is not None and total > max_records:
        kept = []; budget = max_records
        for ep in episodes:
            take = ep[:budget]; kept.append(take); budget -= len(take)
        dropped = total - max_records; episodes = kept; total = max_records
    width = max((len(rec) for ep in episodes for rec in ep), default=0)
    rec = {"status": "BOUND_EXCEEDED" if dropped else ("PRESENT" if total else "EMPTY"), "encoding": ENCODING, "record_width": width,
           "n_episodes": len(episodes), "n_records": total, "n_records_dropped": dropped,
           "bound": {"max_records": max_records, "max_inline_records": max_inline}, "series_hash": series_hash(episodes), "replay_class": replay_class,
           "columns": list(columns or [])}
    if columns and width and len(columns) != width:
        rec["status"] = "CORRUPT_LAYOUT"; rec["layout_defect"] = "observer declared %d columns but records have width %d" % (len(columns), width)
    if total <= max_inline:
        rec["inline"] = episodes
    else:
        blob = canonical(episodes); h = hashlib.sha256(blob).hexdigest()
        d = receipt_dir / ARTIFACT_DIR; d.mkdir(parents=True, exist_ok=True)
        p = d / ("series_%s.json" % h)
        if not p.exists():
            p.write_bytes(blob)
        rec["artifact"] = {"path": "%s/%s" % (ARTIFACT_DIR, p.name), "sha256": h, "bytes": len(blob)}
    return rec


def declared_series_observers(receipt: dict) -> List[str]:
    """Series keys as the executor wrote them: an observer kind, or kind#<index> for a repeated kind (C48)."""
    seen: Dict[str, int] = {}; keys = []
    for i, o in enumerate(receipt.get("components", {}).get("observers", [])):
        key = o["kind"] if o["kind"] not in seen else "%s#%d" % (o["kind"], i); seen[o["kind"]] = i
        if o.get("series"):
            keys.append(key)
    return keys


def verify(receipt: dict, base_dir) -> Dict[str, str]:
    """Classify every declared series without mutating anything."""
    base = pathlib.Path(base_dir); out: Dict[str, str] = {}
    have = receipt.get("series", {}) or {}
    for kind in declared_series_observers(receipt):
        s = have.get(kind)
        if s is None:
            out[kind] = "MISSING"; continue
        if s["status"] not in WRITTEN_STATUSES:
            out[kind] = "CORRUPT"; continue
        if s["status"] == "DISABLED":
            out[kind] = "DISABLED"; continue
        if "inline" in s:
            out[kind] = s["status"] if series_hash(s["inline"]) == s["series_hash"] and sum(len(e) for e in s["inline"]) == s["n_records"] else "CORRUPT"
        elif "artifact" in s:
            p = base / s["artifact"]["path"]
            if not p.exists():
                out[kind] = "MISSING_ARTIFACT"; continue
            blob = p.read_bytes()
            ok = hashlib.sha256(blob).hexdigest() == s["artifact"]["sha256"] == s["series_hash"] and len(blob) == s["artifact"]["bytes"]
            out[kind] = s["status"] if ok else "CORRUPT"
        else:
            out[kind] = "CORRUPT"
    return out


def recover(receipt: dict, base_dir) -> Dict[str, List[List[List[int]]]]:
    """The episodes per declared observer, from the receipt alone (+ its artifacts). Raises on CORRUPT/MISSING."""
    base = pathlib.Path(base_dir); out = {}
    status = verify(receipt, base)
    for kind, st in status.items():
        if st in ("MISSING", "MISSING_ARTIFACT", "CORRUPT"):
            raise ValueError("series %s is %s" % (kind, st))
        s = receipt["series"][kind]
        if st == "DISABLED":
            out[kind] = []
        elif "inline" in s:
            out[kind] = s["inline"]
        else:
            out[kind] = json.loads((base / s["artifact"]["path"]).read_bytes().decode())
    return out
