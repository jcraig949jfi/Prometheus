"""Operational join — cross-landscape edges grounded in COMPUTATION, not names.

The lexical join failed the null (homonyms). This join earns its edges: it runs a
sympy function to produce an actual integer sequence, then asks OEIS which
sequence that IS. A match is a verified, specific, low-null bridge:

    algolib:totient  --computes-->  oeis:A000010

The verb is "computes" (feedback_verbs_over_nouns). The algolib node id is the
sympy name, so it coincides with the node the algolib crawler already weaves
`calls` edges around — the computes edge stitches the code-graph to the
sequence-graph at a real shared vertex.
"""
from __future__ import annotations

from datetime import datetime, timezone

from agents.arachne.fabric import Fabric, Edge


def _seq_funcs():
    """name -> (callable(n)->int, start_n). Names match the algolib crawler's
    node ids (sympy attribute names) so nodes coincide."""
    import sympy
    specs = {
        "totient": ("totient", 1), "divisor_count": ("divisor_count", 1),
        "divisor_sigma": ("divisor_sigma", 1), "mobius": ("mobius", 1),
        "prime": ("prime", 1), "primepi": ("primepi", 1),
        "factorial": ("factorial", 0), "fibonacci": ("fibonacci", 0),
        "lucas": ("lucas", 0), "catalan": ("catalan", 0), "bell": ("bell", 0),
        "tribonacci": ("tribonacci", 0), "harmonic": (None, None),  # rational, skip
    }
    out = {}
    for name, (attr, start) in specs.items():
        if attr is None:
            continue
        fn = getattr(sympy, attr, None)
        if callable(fn):
            out[name] = (fn, start)
    return out


class OperationalJoiner:
    name = "operational"

    def __init__(self, oeis_adapter=None, terms=16):
        self._conn = getattr(oeis_adapter, "_conn", None)
        self._terms = terms
        self._done: set[str] = set()
        self._funcs = {}
        self.total_edges = 0
        self.matched = 0
        if self._conn is not None:
            try:
                self._funcs = _seq_funcs()
            except Exception:
                self._funcs = {}

    def available(self) -> bool:
        return self._conn is not None and bool(self._funcs)

    def _compute(self, fn, start) -> list:
        out = []
        for n in range(start, start + self._terms):
            try:
                v = int(fn(n))
            except Exception:
                break
            out.append(v)
        return out

    def _match_oeis(self, L: list) -> list:
        """Return OEIS A-numbers whose first terms equal the computed sequence
        (trying offset 0 and 1 to absorb OEIS offset conventions)."""
        hits = []
        cur = self._conn.cursor()
        for cand in (L, L[1:]):
            if len(cand) < 8:
                continue
            try:
                # ORDER BY oeis_id => prefer canonical low A-numbers over later
                # coincidental matches that share the same long prefix.
                cur.execute(
                    "SELECT oeis_id FROM analysis.oeis WHERE first_terms[1:%s] = %s::bigint[] "
                    "AND oeis_id IS NOT NULL ORDER BY oeis_id ASC LIMIT 8;", (len(cand), cand))
                hits += [r[0] for r in cur.fetchall()]
            except Exception:
                pass
        cur.close()
        return list(dict.fromkeys(hits))

    def weave(self, fabric: Fabric, rng, batch: int = 4) -> dict:
        """Process up to `batch` not-yet-tried functions; emit verified edges."""
        if not self.available():
            return {"new_edges": 0}
        todo = [n for n in self._funcs if n not in self._done]
        rng.shuffle(todo)
        now = datetime.now(timezone.utc).isoformat()
        edges = []
        for name in todo[:batch]:
            self._done.add(name)
            fn, start = self._funcs[name]
            L = self._compute(fn, start)
            if len(L) < 6:
                continue
            hits = self._match_oeis(L)
            # specificity: a sequence that pins ONE OEIS entry is a strong bridge;
            # one matching many shares a generic prefix => higher null.
            null_p = min(0.6, 0.05 * max(1, len(hits)))
            for aid in hits:
                self.matched += 1
                edges.append(Edge(src=f"algolib:{name}", dst=f"oeis:{aid}",
                                  op="computes", landscape="operational",
                                  crawler="operational", born_at=now, null_p=float(null_p)))
        delta = fabric.add(edges)
        self.total_edges += delta["new_edges"]
        return delta

    def exhausted(self) -> bool:
        return len(self._done) >= len(self._funcs)

    def snapshot(self) -> dict:
        return {"id": "operational", "landscape": "operational", "alive": True,
                "total_edges": self.total_edges, "funcs_tried": len(self._done),
                "funcs_total": len(self._funcs), "matched": self.matched}
