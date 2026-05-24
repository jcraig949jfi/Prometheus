"""PolyhymniaTensor — the one-tensor abstraction.

A sparse, content-addressable, N-dimensional structure on disk. Cells are
JSONL records; coordinate axes are JSONL registries; lineage edges are
JSONL records. The class wraps read / write / slice / project / sample.

Design intent (see CHARTER.md "What 'one tensor' actually means here"):
  - There's one tensor. Everything tensor-shaped jams into it.
  - Sparse: only populated cells exist on disk.
  - Content-addressable: cell_id = sha256(canonical content) so dup-detect is free.
  - Append-only: cells.jsonl is never rewritten in place. Corrections =
    append a cell with the same coord signature; integrator merges (latest
    content wins, tag axes union).
  - Open-vocabulary axes: scours can register new axis values as discovered.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator, Optional

# Canonical axis names. Adding a new coordinate axis requires adding it
# here AND creating tensor/axes/<name>.jsonl. Existing cells get `null`
# for the new axis (no migration needed; schema is open).
COORD_AXES = (
    "time",                  # int year or None
    "discipline",            # string from axes/discipline.jsonl
    "object_kind",           # string from axes/object_kind.jsonl
    "structural_rank",       # int or None
    "abstraction_level",     # string from axes/abstraction_level.jsonl
    "substrate_yield_type",  # 'A'|'B'|'C'|'D'|'E' or None
)
TAG_AXES = (
    "researchers",        # list[str]
    "lineage_ancestors",  # list[str]  (cell_ids of ancestors)
    "free_tags",          # list[str]
    "citations",          # list[str]  (arXiv IDs, DOIs, URLs)
)


@dataclass
class CandidateCell:
    """A scour's output: a cell without cell_id / first_seen_at yet.
    The integrator computes those."""
    coords: dict
    content: dict
    source: dict
    tags: dict = field(default_factory=lambda: {a: [] for a in TAG_AXES})

    def to_dict(self) -> dict:
        # Ensure all coord axes are present (None if unset)
        coords = {a: self.coords.get(a) for a in COORD_AXES}
        tags = {a: list(self.tags.get(a) or []) for a in TAG_AXES}
        return {"coords": coords, "tags": tags,
                "content": dict(self.content),
                "source": dict(self.source)}


@dataclass
class LineageEdge:
    """An edge in the lineage graph: from_cell_id led to to_cell_id."""
    from_cell_id: str
    to_cell_id: str
    relation: str = "informs"   # e.g., 'cites', 'specializes', 'extends', 'refutes'
    note: str = ""
    scour: str = ""

    def to_dict(self) -> dict:
        return {
            "from": self.from_cell_id, "to": self.to_cell_id,
            "relation": self.relation, "note": self.note,
            "scour": self.scour,
            "added_at": datetime.now(timezone.utc).isoformat(),
        }


def _canonicalize_for_hash(coords: dict, content: dict) -> str:
    """Produce a stable canonical string for hashing. We hash on:
       - sorted coordinate tuple (deterministic axis order)
       - title (the most stable content identifier)
       - lowercased + whitespace-normalized body (deterministic content)
    Tags are NOT in the hash — same cell rediscovered with new tags
    should merge, not duplicate."""
    coord_str = "|".join(f"{k}={coords.get(k)!r}" for k in COORD_AXES)
    title = (content.get("title") or "").strip().lower()
    body = " ".join((content.get("body") or "").lower().split())
    return f"{coord_str}\n{title}\n{body[:500]}"


def compute_cell_id(coords: dict, content: dict) -> str:
    """16-char sha256 of canonical content. Same input → same cell_id."""
    canon = _canonicalize_for_hash(coords, content)
    return hashlib.sha256(canon.encode("utf-8", errors="replace")).hexdigest()[:16]


class PolyhymniaTensor:
    """On-disk tensor wrapper. Thread-safety: NOT thread-safe — the daemon's
    single-instance lock provides serialization. If multiple processes ever
    need to write, switch to a file-lock around the JSONL append."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.axes_dir = self.root / "axes"
        self.cells_path = self.root / "cells.jsonl"
        self.lineage_path = self.root / "lineage.jsonl"
        # Ensure dirs exist
        self.axes_dir.mkdir(parents=True, exist_ok=True)
        self.cells_path.parent.mkdir(parents=True, exist_ok=True)

    # ---- axis registries ----------------------------------------------------

    def axis_values(self, axis: str) -> list[dict]:
        """Read the registered values for a coordinate axis. Returns list of
        {value, label, added_at, ...} dicts. Empty list if axis file absent."""
        p = self.axes_dir / f"{axis}.jsonl"
        if not p.exists():
            return []
        out = []
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return out

    def register_axis_value(self, axis: str, value: str, label: str = "") -> bool:
        """Add a new value to a coordinate axis registry (idempotent)."""
        existing = {v["value"] for v in self.axis_values(axis)}
        if value in existing:
            return False
        p = self.axes_dir / f"{axis}.jsonl"
        p.parent.mkdir(parents=True, exist_ok=True)
        rec = {"value": value, "label": label or value,
               "added_at": datetime.now(timezone.utc).date().isoformat()}
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return True

    # ---- cell I/O -----------------------------------------------------------

    def iter_cells(self) -> Iterator[dict]:
        if not self.cells_path.exists():
            return
        with self.cells_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue

    def total_cells(self) -> int:
        if not self.cells_path.exists():
            return 0
        with self.cells_path.open(encoding="utf-8") as f:
            return sum(1 for _ in f)

    def load_index(self) -> dict[str, dict]:
        """Build an in-memory {cell_id: cell} index. O(N); use sparingly.
        For Phase 0 this is fine since cell counts are modest. A SQLite
        mirror is the future fast-slice path."""
        return {c["cell_id"]: c for c in self.iter_cells()}

    def integrate(self, candidates: list[CandidateCell]) -> dict:
        """Merge candidate cells into the tensor. Returns delta summary:
           {'new': int, 'merged': int, 'axis_values_added': dict}.

        Merge semantics:
          - Compute cell_id from canonical coords+content.
          - If cell_id is new: append, set first_seen_at + last_seen_at.
          - If cell_id exists: union tag axes, update content (latest wins),
            update last_seen_at, append a new record (the latest read of a
            cell is always the last record in the JSONL).
        """
        if not candidates:
            return {"new": 0, "merged": 0, "axis_values_added": {}}

        # Load current state (cells + axis registries)
        index = self.load_index()
        axis_values: dict[str, set] = {a: {v["value"] for v in self.axis_values(a)}
                                       for a in COORD_AXES}
        now = datetime.now(timezone.utc).isoformat()
        axis_values_added: dict[str, list] = {a: [] for a in COORD_AXES}
        new_count, merged_count = 0, 0

        with self.cells_path.open("a", encoding="utf-8") as f:
            for cand in candidates:
                d = cand.to_dict()
                cell_id = compute_cell_id(d["coords"], d["content"])
                # Auto-register new axis values
                for a in COORD_AXES:
                    v = d["coords"].get(a)
                    if v is not None and v not in axis_values[a]:
                        self.register_axis_value(a, str(v))
                        axis_values[a].add(v)
                        axis_values_added[a].append(v)
                if cell_id in index:
                    # Merge: union tags, update content
                    existing = index[cell_id]
                    merged_tags = {
                        a: sorted(set(existing.get("tags", {}).get(a, []))
                                  | set(d["tags"].get(a, [])))
                        for a in TAG_AXES
                    }
                    record = {
                        "cell_id": cell_id,
                        "coords": d["coords"],
                        "tags": merged_tags,
                        "content": d["content"],   # latest content
                        "source": d["source"],
                        "first_seen_at": existing.get("first_seen_at", now),
                        "last_seen_at": now,
                    }
                    merged_count += 1
                else:
                    record = {
                        "cell_id": cell_id,
                        **d,
                        "first_seen_at": now,
                        "last_seen_at": now,
                    }
                    new_count += 1
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                index[cell_id] = record

        return {
            "new": new_count,
            "merged": merged_count,
            "axis_values_added": {a: v for a, v in axis_values_added.items() if v},
        }

    def append_lineage(self, edges: list[LineageEdge]) -> int:
        if not edges:
            return 0
        # Dedup against existing edges
        existing: set[tuple] = set()
        if self.lineage_path.exists():
            with self.lineage_path.open(encoding="utf-8") as f:
                for line in f:
                    try:
                        e = json.loads(line)
                        existing.add((e["from"], e["to"], e.get("relation", "informs")))
                    except Exception:
                        continue
        appended = 0
        with self.lineage_path.open("a", encoding="utf-8") as f:
            for edge in edges:
                key = (edge.from_cell_id, edge.to_cell_id, edge.relation)
                if key in existing:
                    continue
                existing.add(key)
                f.write(json.dumps(edge.to_dict(), ensure_ascii=False) + "\n")
                appended += 1
        return appended

    # ---- slicing / projection / sampling ------------------------------------

    def slice(self, **constraints) -> Iterator[dict]:
        """Yield cells whose coordinates match all given constraints.
        Constraints can be exact values or callables (predicates) or lists
        (membership). Tag axes also supported (membership only)."""
        def _match(cell, axis, constraint) -> bool:
            if axis in COORD_AXES:
                val = cell["coords"].get(axis)
                if callable(constraint):
                    return constraint(val)
                if isinstance(constraint, (list, tuple, set)):
                    return val in constraint
                return val == constraint
            elif axis in TAG_AXES:
                tag_vals = set(cell.get("tags", {}).get(axis, []))
                if isinstance(constraint, (list, tuple, set)):
                    return bool(tag_vals & set(constraint))
                return constraint in tag_vals
            return True

        # Index lookup (last record per cell_id wins, matching merge semantics)
        latest: dict[str, dict] = {}
        for c in self.iter_cells():
            latest[c["cell_id"]] = c
        for c in latest.values():
            if all(_match(c, a, v) for a, v in constraints.items()):
                yield c

    def project(self, axis: str, **constraints) -> dict[Any, int]:
        """Count cells matching constraints, grouped by axis. Returns
        {axis_value: count} dict."""
        counts: dict[Any, int] = {}
        for c in self.slice(**constraints):
            if axis in COORD_AXES:
                v = c["coords"].get(axis)
                counts[v] = counts.get(v, 0) + 1
            elif axis in TAG_AXES:
                for v in c.get("tags", {}).get(axis, []):
                    counts[v] = counts.get(v, 0) + 1
        return counts

    def sample(self, n: int = 5, **constraints) -> list[dict]:
        """Return up to n cells matching constraints. Random-ish (insertion
        order; not cryptographically random)."""
        out = []
        for c in self.slice(**constraints):
            out.append(c)
            if len(out) >= n:
                break
        return out

    # ---- stats --------------------------------------------------------------

    def stats(self) -> dict:
        """Snapshot of tensor size + per-axis cardinality + sparsity."""
        latest: dict[str, dict] = {}
        for c in self.iter_cells():
            latest[c["cell_id"]] = c
        cells = list(latest.values())
        n = len(cells)
        per_axis_card = {}
        for a in COORD_AXES:
            vals = set(c["coords"].get(a) for c in cells)
            vals.discard(None)
            per_axis_card[a] = len(vals)
        for a in TAG_AXES:
            vals: set = set()
            for c in cells:
                vals.update(c.get("tags", {}).get(a, []))
            per_axis_card[a] = len(vals)
        # Lineage edge count
        lineage_n = 0
        if self.lineage_path.exists():
            with self.lineage_path.open(encoding="utf-8") as f:
                lineage_n = sum(1 for _ in f)
        # Sparsity: populated / (product of registered axis sizes)
        registered_sizes = {a: len(self.axis_values(a)) for a in COORD_AXES}
        dense_capacity = 1
        for v in registered_sizes.values():
            dense_capacity *= max(1, v)
        return {
            "total_cells": n,
            "total_lineage_edges": lineage_n,
            "coord_axis_cardinality": {a: per_axis_card[a] for a in COORD_AXES},
            "tag_axis_cardinality": {a: per_axis_card[a] for a in TAG_AXES},
            "registered_coord_sizes": registered_sizes,
            "dense_capacity_if_fully_populated": dense_capacity,
            "sparsity_fraction_populated": (n / dense_capacity) if dense_capacity else 0,
        }
