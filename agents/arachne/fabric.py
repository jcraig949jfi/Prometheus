"""The shared fabric — the one tapestry all crawlers weave.

Append-only JSONL edge store with provenance, operator-type, and a null score
on every edge (the three epistemic rules). Dedup by (src, dst, op).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Optional


def _edge_key(src: str, dst: str, op: str) -> str:
    return hashlib.sha1(f"{src}\x1f{dst}\x1f{op}".encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class Edge:
    src: str            # namespaced node id, e.g. "mathlib:Nat.add_comm"
    dst: str
    op: str             # the VERB: uses / shares_invariant / calls / transforms ...
    landscape: str      # which landscape produced it
    crawler: str        # which crawler produced it (provenance)
    born_at: str        # ISO timestamp
    null_p: float       # ~P(a random crawler makes this edge); high => cheap/generic

    @property
    def key(self) -> str:
        return _edge_key(self.src, self.dst, self.op)


class Fabric:
    """In-process view + append-only persistence of the tapestry."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.edges_path = self.root / "edges.jsonl"
        self._keys: set[str] = set()
        self._nodes: set[str] = set()
        self._edge_count = 0
        self._load()

    def _load(self) -> None:
        if not self.edges_path.exists():
            return
        for line in self.edges_path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            k = _edge_key(e["src"], e["dst"], e["op"])
            self._keys.add(k)
            self._nodes.add(e["src"])
            self._nodes.add(e["dst"])
            self._edge_count += 1

    def has(self, src: str, dst: str, op: str) -> bool:
        return _edge_key(src, dst, op) in self._keys

    def add(self, edges: Iterable[Edge]) -> dict:
        """Append novel edges. Returns {new_edges, new_nodes, dup_edges}."""
        new_e = new_n = dup = 0
        buf = []
        for e in edges:
            if e.key in self._keys:
                dup += 1
                continue
            self._keys.add(e.key)
            buf.append(json.dumps(asdict(e), ensure_ascii=False))
            new_e += 1
            for node in (e.src, e.dst):
                if node not in self._nodes:
                    self._nodes.add(node)
                    new_n += 1
        if buf:
            with self.edges_path.open("a", encoding="utf-8") as f:
                f.write("\n".join(buf) + "\n")
            self._edge_count += new_e
        return {"new_edges": new_e, "new_nodes": new_n, "dup_edges": dup}

    def node_degree_seen(self, node: str) -> bool:
        return node in self._nodes

    def stats(self) -> dict:
        return {"edges": self._edge_count, "nodes": len(self._nodes)}
