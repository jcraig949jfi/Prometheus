"""Rename the drifted lineage-edge key "target" to the canonical "to" (record.py LINEAGE_EDGE_TARGET_KEY).

Nyx #572 (2026-09-25): 80 lineage relations in Techne records used "target" against 112 using "to";
the capsules of the 39 rollout fossils copy the same edges, so 158 edges in 80 files drifted. The
writer was techne/fossils/preserve_rollouts.py (2026-09-19); poet-original-2019 and
terralingua-data-abundant-exp-1 were written by hand the same week in the same shape.

What this does, and only this:
  - for every techne/fossils/specimens/*/record.json and CAPSULE.json, every edge in
    record.lineage_relations / capsule.lineage.relations whose far end is under "target" is
    rewritten with the key "to" IN THE SAME POSITION; every other byte of the edge is untouched.
  - a file is rewritten only if (a) at least one edge changed and (b) re-serialising the UNCHANGED
    document with the writer's own convention reproduces the file byte for byte (LF-normalised).
    If (b) fails the file is reported FORMAT_MISMATCH and left alone: this script must never be
    the thing that reformats a record.
  - a receipt (path, before/after sha256, edges renamed) is written to
    techne/fossils/LINEAGE_KEY_MIGRATION_2026-09-25.json unless --dry-run.
  - idempotent: a second run finds 0 edges and rewrites nothing.

Refuses: an edge carrying BOTH keys (ambiguous; a human decides), an edge whose "target" is not
a non-empty string. Nothing else about the record is validated here; record.validate() does that.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import time

from . import vault
from .record import LINEAGE_EDGE_TARGET_KEY

DRIFTED = "target"
RECEIPT = vault.REPO / "techne" / "fossils" / "LINEAGE_KEY_MIGRATION_2026-09-25.json"
CONVENTIONS = {"record.json": 2, "CAPSULE.json": 1}   # json.dumps indent used by record.save / capsule.main


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _edges(doc: dict, kind: str) -> list[dict]:
    if kind == "record.json":
        return doc.get("lineage_relations") or []
    return ((doc.get("lineage") or {}).get("relations")) or []


def rename_edge(e: dict) -> tuple[dict, bool]:
    """Return (edge, changed). Key order preserved: "to" lands where "target" was."""
    if DRIFTED not in e:
        return e, False
    if LINEAGE_EDGE_TARGET_KEY in e:
        raise ValueError("edge carries both %r and %r: %r" % (DRIFTED, LINEAGE_EDGE_TARGET_KEY, e))
    v = e[DRIFTED]
    if not isinstance(v, str) or not v.strip():
        raise ValueError("edge %r is not a non-empty string: %r" % (DRIFTED, e))
    out = {}
    for k, val in e.items():
        out[LINEAGE_EDGE_TARGET_KEY if k == DRIFTED else k] = val
    return out, True


def migrate_file(p: pathlib.Path, write: bool) -> dict:
    kind = p.name
    indent = CONVENTIONS[kind]
    raw = p.read_bytes()
    lf = raw.replace(b"\r\n", b"\n")
    doc = json.loads(lf.decode("utf-8"))
    try:
        shown = str(p.relative_to(vault.REPO))
    except ValueError:            # a fixture tree outside the repo (tests)
        shown = str(p)
    row = {"path": shown.replace("\\", "/"), "sha256_before": _sha(lf), "edges_renamed": 0,
           "status": "UNCHANGED", "sha256_after": _sha(lf)}
    edges = _edges(doc, kind)
    new_edges, n = [], 0
    for e in edges:
        ne, ch = rename_edge(e)
        new_edges.append(ne); n += ch
    if n == 0:
        return row
    row["edges_renamed"] = n
    # (b): the writer's convention must reproduce the ORIGINAL bytes, else refuse to touch the file.
    if (json.dumps(doc, indent=indent) + "\n").encode("utf-8") != lf:
        row["status"] = "FORMAT_MISMATCH"
        return row
    if kind == "record.json":
        doc["lineage_relations"] = new_edges
    else:
        doc["lineage"]["relations"] = new_edges
    out = (json.dumps(doc, indent=indent) + "\n").encode("utf-8")
    row["sha256_after"] = _sha(out)
    row["status"] = "RENAMED" if write else "WOULD_RENAME"
    if write:
        p.write_bytes(out)
    return row


def run(specimens_dir: pathlib.Path, write: bool) -> dict:
    rows = []
    for d in sorted(specimens_dir.iterdir()):
        if not d.is_dir():
            continue
        for name in CONVENTIONS:
            p = d / name
            if p.exists():
                rows.append(migrate_file(p, write))
    by = {}
    for r in rows:
        by[r["status"]] = by.get(r["status"], 0) + 1
    return {"schema": "techne.fossil.lineage_key_migration/1", "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "drifted_key": DRIFTED, "canonical_key": LINEAGE_EDGE_TARGET_KEY, "write": write,
            "files_scanned": len(rows), "edges_renamed": sum(r["edges_renamed"] for r in rows), "by_status": by,
            "files": [r for r in rows if r["status"] != "UNCHANGED"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--specimens", default=str(vault.REPO / "techne" / "fossils" / "specimens"))
    ap.add_argument("--receipt", default=str(RECEIPT))
    a = ap.parse_args(argv)
    rep = run(pathlib.Path(a.specimens), write=not a.dry_run)
    if not a.dry_run:
        pathlib.Path(a.receipt).write_text(json.dumps(rep, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("files_scanned %d  edges_renamed %d  by_status %s%s" % (rep["files_scanned"], rep["edges_renamed"], rep["by_status"],
                                                                 "" if a.dry_run else "  receipt " + a.receipt))
    return 1 if rep["by_status"].get("FORMAT_MISMATCH") else 0


if __name__ == "__main__":
    raise SystemExit(main())
