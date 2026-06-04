"""Rosetta join weaver — the only thing that makes the fabric ONE tapestry.

Crawlers weave only within their own landscape; without a join, the fabric is
N disconnected webs and no cross-domain organization can emerge. The weaver
crawls the FABRIC ITSELF: it builds a concept-token index across landscapes
(from node ids, and from OEIS `name` text), then emits cross-landscape
`shares_concept` edges where a distinctive token surfaces in >=2 landscapes.

Epistemic rules still hold: provenance (crawler="rosetta"), operator-typed
(shares_concept), and null_p by token rarity — a token in many nodes is generic
(high null); a rare token shared across landscapes is the surprising link
(low null). A name-match is a HYPOTHESIS; the traversal + null is what tests it.
"""
from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, timezone

from agents.arachne.fabric import Fabric, Edge

_CAMEL = re.compile(r"[A-Z]?[a-z]{2,}|[A-Z]{2,}")
_STOP = {
    "the", "and", "for", "with", "num", "def", "val", "list", "set", "map",
    "type", "data", "test", "mk", "aux", "lemma", "theorem", "number", "numbers",
    "sequence", "sequences", "function", "functions", "values", "form", "case",
    "main", "self", "args", "kwargs", "true", "false", "none", "int", "str",
    "sum", "add", "mul", "sub", "get", "from", "into", "via", "use", "new",
}


def _tokens(text: str) -> set:
    out = set()
    for w in _CAMEL.findall(text or ""):
        w = w.lower()
        if len(w) >= 4 and w not in _STOP and not w.isdigit():
            out.add(w)
    return out


class JoinWeaver:
    name = "rosetta"

    def __init__(self, oeis_adapter=None):
        self._oeis = oeis_adapter
        # token -> {landscape -> set(node_ids)}
        self._index: dict[str, dict] = defaultdict(lambda: defaultdict(set))
        self._seen_nodes: set[str] = set()
        self._oeis_name_cache: dict[str, str] = {}
        self.total_edges = 0

    def _label_tokens(self, node: str) -> set:
        ls, _, rest = node.partition(":")
        if ls == "oeis":
            name = self._oeis_name_cache.get(node)
            return _tokens(name) if name else set()
        # mathlib / algolib / lmfdb: tokens live in the id itself
        return _tokens(rest.replace("/", ".").replace(".", " "))

    def _fetch_oeis_names(self, oeis_nodes: list) -> None:
        if not oeis_nodes or self._oeis is None or getattr(self._oeis, "_conn", None) is None:
            return
        aids = [n.split(":", 1)[1] for n in oeis_nodes]
        try:
            cur = self._oeis._conn.cursor()
            cur.execute("SELECT oeis_id, name FROM analysis.oeis WHERE oeis_id = ANY(%s);", (aids,))
            for aid, nm in cur.fetchall():
                self._oeis_name_cache[f"oeis:{aid}"] = nm or ""
            cur.close()
        except Exception:
            pass

    def _ingest(self, fabric: Fabric) -> None:
        new = [n for n in fabric.nodes() if n not in self._seen_nodes]
        if not new:
            return
        self._fetch_oeis_names([n for n in new if n.startswith("oeis:")])
        for node in new:
            self._seen_nodes.add(node)
            ls = node.split(":", 1)[0]
            for tok in self._label_tokens(node):
                self._index[tok][ls].add(node)

    def weave(self, fabric: Fabric, rng, max_edges: int = 40) -> dict:
        """One join pass. Returns fabric.add() delta."""
        self._ingest(fabric)
        now = datetime.now(timezone.utc).isoformat()
        edges = []
        # tokens that bridge >=2 landscapes are the cross-domain candidates
        bridging = [(tok, lsmap) for tok, lsmap in self._index.items() if len(lsmap) >= 2]
        rng.shuffle(bridging)
        for tok, lsmap in bridging:
            n_nodes = sum(len(s) for s in lsmap.values())
            null_p = min(0.95, 0.10 + 0.04 * n_nodes)   # rarer token => lower null
            ls_list = list(lsmap.keys())
            # link a small representative set across each landscape pair
            for i in range(len(ls_list)):
                for j in range(i + 1, len(ls_list)):
                    a_nodes = list(lsmap[ls_list[i]])[:3]
                    b_nodes = list(lsmap[ls_list[j]])[:3]
                    for a in a_nodes:
                        for b in b_nodes:
                            edges.append(Edge(src=a, dst=b, op="shares_concept",
                                              landscape="rosetta", crawler="rosetta",
                                              born_at=now, null_p=float(null_p)))
            if len(edges) >= max_edges:
                break
        delta = fabric.add(edges)
        self.total_edges += delta["new_edges"]
        return delta

    def snapshot(self) -> dict:
        bridging = sum(1 for lsmap in self._index.values() if len(lsmap) >= 2)
        return {"id": "rosetta", "landscape": "rosetta", "alive": True,
                "total_edges": self.total_edges, "concepts_indexed": len(self._index),
                "bridging_concepts": bridging}
