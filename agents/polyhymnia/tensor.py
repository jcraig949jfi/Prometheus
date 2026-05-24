"""PolyhymniaTensor — Polyhymnia's library + the Omnitensor abstraction.

The Omnitensor is one sparse, content-addressable, N-dimensional structure
on disk that everything tensor-shaped gets jammed into. This file is the
Python wrapper. Storage is append-only JSONL — one record per tessera (the
mosaic-tile unit), one record per lineage edge.

Naming note: per ChatGPT cross-frontier 2026-05-24 + James greenlight,
the *artifact* is the **Omnitensor**; the *agent* that writes/reads it is
**Polyhymnia**; each populated coordinate is a **tessera** (Latin/Greek
for the small tile in a mosaic — exactly what a single cell of the
Omnitensor is). Renamed from "cell" 2026-05-24.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator, Optional

# ---------------------------------------------------------------------------
# Axes (the Omnitensor's dimensions)
# ---------------------------------------------------------------------------
# Coordinate axes: each tessera has ONE value per axis (or None).
# Adding a new coord axis = append here + create tensor/axes/<name>.jsonl.
# Existing tesserae get None for the new axis; no migration required.
COORD_AXES = (
    "time",                  # int year or None
    "discipline",            # string from axes/discipline.jsonl
    "object_kind",           # string from axes/object_kind.jsonl
    "structural_rank",       # int or None (0 scalar, 1 vector, 2 matrix, 3+ tensor)
    "abstraction_level",     # string from axes/abstraction_level.jsonl
    "substrate_yield_type",  # 'A'|'B'|'C'|'D'|'E' or None
    "epistemic_status",      # MYTHIC|MENTIONED|EXTRACTED|SUPPORTED|RUNNABLE|REPRODUCED|FALSIFIED
    "data_modality",         # text|image|audio|video|scalar|tensor|graph|formula|code|dataset|null
    "code_language",         # python|c|cpp|julia|matlab|lean|fortran|rust|js|null
)

# Tag axes: many-to-many. The lineage_ancestors tag is the knowledge-graph spine.
TAG_AXES = (
    "researchers",        # list[str] — named contributors
    "lineage_ancestors",  # list[str] — tessera_ids of ancestors (knowledge graph)
    "free_tags",          # list[str] — arbitrary keywords
    "citations",          # list[str] — arXiv IDs, DOIs, URLs
    "game_affordance",    # list[str] — which games this tessera enables
)


# ---------------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------------

@dataclass
class CandidateTessera:
    """A scour's output: a tessera without tessera_id / first_seen_at yet.
    The integrator computes those."""
    coords: dict
    content: dict
    source: dict
    tags: dict = field(default_factory=lambda: {a: [] for a in TAG_AXES})
    confidence: Optional[float] = None  # 0.0-1.0; top-level numeric, not a coord

    def to_dict(self) -> dict:
        coords = {a: self.coords.get(a) for a in COORD_AXES}
        tags = {a: list(self.tags.get(a) or []) for a in TAG_AXES}
        return {
            "coords": coords, "tags": tags,
            "content": dict(self.content),
            "source": dict(self.source),
            "confidence": self.confidence,
        }


@dataclass
class LineageEdge:
    """Edge in the knowledge graph. The relation vocabulary is documented
    in tensor/relations.jsonl. Open vocabulary — new relations auto-register."""
    from_tessera_id: str
    to_tessera_id: str
    relation: str = "informs"
    note: str = ""
    scour: str = ""

    def to_dict(self) -> dict:
        return {
            "from": self.from_tessera_id, "to": self.to_tessera_id,
            "relation": self.relation, "note": self.note,
            "scour": self.scour,
            "added_at": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def _canonicalize_for_hash(coords: dict, content: dict) -> str:
    coord_str = "|".join(f"{k}={coords.get(k)!r}" for k in COORD_AXES)
    title = (content.get("title") or "").strip().lower()
    body = " ".join((content.get("body") or "").lower().split())
    return f"{coord_str}\n{title}\n{body[:500]}"


def compute_tessera_id(coords: dict, content: dict) -> str:
    """16-char sha256 of canonical content. Same input → same tessera_id."""
    canon = _canonicalize_for_hash(coords, content)
    return hashlib.sha256(canon.encode("utf-8", errors="replace")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# The Omnitensor
# ---------------------------------------------------------------------------

class PolyhymniaTensor:
    """On-disk Omnitensor wrapper. Thread-safety: NOT thread-safe — the daemon's
    single-instance lock provides serialization."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.axes_dir = self.root / "axes"
        self.tesserae_path = self.root / "tesserae.jsonl"
        self.lineage_path = self.root / "lineage.jsonl"
        self.axes_dir.mkdir(parents=True, exist_ok=True)
        self.tesserae_path.parent.mkdir(parents=True, exist_ok=True)

    # ---- axis registries ----------------------------------------------------

    def axis_values(self, axis: str) -> list[dict]:
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

    # ---- tessera I/O --------------------------------------------------------

    def iter_tesserae(self) -> Iterator[dict]:
        if not self.tesserae_path.exists():
            return
        with self.tesserae_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue

    def total_tesserae(self) -> int:
        if not self.tesserae_path.exists():
            return 0
        with self.tesserae_path.open(encoding="utf-8") as f:
            return sum(1 for _ in f)

    def load_index(self) -> dict[str, dict]:
        """In-memory {tessera_id: tessera} index. O(N); use sparingly."""
        return {t["tessera_id"]: t for t in self.iter_tesserae()}

    def integrate(self, candidates: list[CandidateTessera]) -> dict:
        """Merge candidate tesserae into the Omnitensor. Returns delta summary.

        Merge semantics:
          - tessera_id from canonical coords+content.
          - New id: append; set first_seen_at + last_seen_at.
          - Existing id: union tag axes, latest content wins, update last_seen_at.
        """
        if not candidates:
            return {"new": 0, "merged": 0, "axis_values_added": {}}

        index = self.load_index()
        axis_values: dict[str, set] = {a: {v["value"] for v in self.axis_values(a)}
                                       for a in COORD_AXES}
        now = datetime.now(timezone.utc).isoformat()
        axis_values_added: dict[str, list] = {a: [] for a in COORD_AXES}
        new_count, merged_count = 0, 0

        with self.tesserae_path.open("a", encoding="utf-8") as f:
            for cand in candidates:
                d = cand.to_dict()
                tessera_id = compute_tessera_id(d["coords"], d["content"])
                # Auto-register new axis values (open-vocabulary)
                for a in COORD_AXES:
                    v = d["coords"].get(a)
                    if v is not None and v not in axis_values[a]:
                        self.register_axis_value(a, str(v))
                        axis_values[a].add(v)
                        axis_values_added[a].append(v)
                if tessera_id in index:
                    existing = index[tessera_id]
                    merged_tags = {
                        a: sorted(set(existing.get("tags", {}).get(a, []))
                                  | set(d["tags"].get(a, [])))
                        for a in TAG_AXES
                    }
                    record = {
                        "tessera_id": tessera_id,
                        "coords": d["coords"],
                        "tags": merged_tags,
                        "content": d["content"],
                        "source": d["source"],
                        "confidence": d.get("confidence"),
                        "first_seen_at": existing.get("first_seen_at", now),
                        "last_seen_at": now,
                    }
                    merged_count += 1
                else:
                    record = {
                        "tessera_id": tessera_id,
                        **d,
                        "first_seen_at": now,
                        "last_seen_at": now,
                    }
                    new_count += 1
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                index[tessera_id] = record

        return {
            "new": new_count,
            "merged": merged_count,
            "axis_values_added": {a: v for a, v in axis_values_added.items() if v},
        }

    def append_lineage(self, edges: list[LineageEdge]) -> int:
        if not edges:
            return 0
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
                key = (edge.from_tessera_id, edge.to_tessera_id, edge.relation)
                if key in existing:
                    continue
                existing.add(key)
                f.write(json.dumps(edge.to_dict(), ensure_ascii=False) + "\n")
                appended += 1
        return appended

    # ---- slicing / projection / sampling ------------------------------------

    def slice(self, **constraints) -> Iterator[dict]:
        def _match(t, axis, constraint) -> bool:
            if axis in COORD_AXES:
                val = t["coords"].get(axis)
                if callable(constraint):
                    return constraint(val)
                if isinstance(constraint, (list, tuple, set)):
                    return val in constraint
                return val == constraint
            elif axis in TAG_AXES:
                tag_vals = set(t.get("tags", {}).get(axis, []))
                if isinstance(constraint, (list, tuple, set)):
                    return bool(tag_vals & set(constraint))
                return constraint in tag_vals
            return True

        latest: dict[str, dict] = {}
        for t in self.iter_tesserae():
            latest[t["tessera_id"]] = t
        for t in latest.values():
            if all(_match(t, a, v) for a, v in constraints.items()):
                yield t

    def project(self, axis: str, **constraints) -> dict[Any, int]:
        counts: dict[Any, int] = {}
        for t in self.slice(**constraints):
            if axis in COORD_AXES:
                v = t["coords"].get(axis)
                counts[v] = counts.get(v, 0) + 1
            elif axis in TAG_AXES:
                for v in t.get("tags", {}).get(axis, []):
                    counts[v] = counts.get(v, 0) + 1
        return counts

    def sample(self, n: int = 5, **constraints) -> list[dict]:
        out = []
        for t in self.slice(**constraints):
            out.append(t)
            if len(out) >= n:
                break
        return out

    # ---- stats --------------------------------------------------------------

    def stats(self) -> dict:
        latest: dict[str, dict] = {}
        for t in self.iter_tesserae():
            latest[t["tessera_id"]] = t
        tesserae = list(latest.values())
        n = len(tesserae)
        per_axis_card = {}
        for a in COORD_AXES:
            vals = set(t["coords"].get(a) for t in tesserae)
            vals.discard(None)
            per_axis_card[a] = len(vals)
        for a in TAG_AXES:
            vals: set = set()
            for t in tesserae:
                vals.update(t.get("tags", {}).get(a, []))
            per_axis_card[a] = len(vals)
        lineage_n = 0
        if self.lineage_path.exists():
            with self.lineage_path.open(encoding="utf-8") as f:
                lineage_n = sum(1 for _ in f)
        registered_sizes = {a: len(self.axis_values(a)) for a in COORD_AXES}
        dense_capacity = 1
        for v in registered_sizes.values():
            dense_capacity *= max(1, v)
        return {
            "total_tesserae": n,
            "total_lineage_edges": lineage_n,
            "coord_axis_cardinality": {a: per_axis_card[a] for a in COORD_AXES},
            "tag_axis_cardinality": {a: per_axis_card[a] for a in TAG_AXES},
            "registered_coord_sizes": registered_sizes,
            "dense_capacity_if_fully_populated": dense_capacity,
            "sparsity_fraction_populated": (n / dense_capacity) if dense_capacity else 0,
        }
