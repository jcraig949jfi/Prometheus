"""World quotient: W_i ~ W_j iff equal verdict vectors over a frozen probe battery.

Aphrodite's denotational idea (roles/Aphrodite/engine/semantics.py: identity = value vector
over a frozen probe battery) lifted from programs to worlds. The battery reads the
certificate's native summaries only:
  PAYS          SELECTIVE_PAYS.v1 verdict
  BEATS_LAST    fit(SEL) - fit(LAST) >= 0.10   (memory worth its price vs forgetting)
  BEATS_LOG     fit(SEL) - fit(LOG)  >= 0.10   (selectivity worth it vs hoarding)
  RETAINS       SEL accuracy >= 0.9            (the carrier actually holds the cue)
Reported: classes / nodes (compression), and per edge kind the fraction of edges whose
endpoints fall in different classes (boundary edges). Mostly-singleton classes would mean
the battery measures substrate identity, not phenomena.
"""
from __future__ import annotations

import json
from collections import Counter
from typing import Any, Dict

BATTERY = ("PAYS", "BEATS_LAST", "BEATS_LOG", "RETAINS")


def verdict_vector(fitness: Dict[str, float], acc_sel: float, pays: bool) -> tuple:
    return (int(pays), int(fitness["SEL"] - fitness["LAST"] >= 0.10), int(fitness["SEL"] - fitness["LOG"] >= 0.10),
            int(acc_sel >= 0.9))


def quotient(rows, edges=()) -> Dict[str, Any]:
    cls = {}
    for r in rows:
        cls[r["world_id"]] = verdict_vector(r["fitness"], r["acc"]["SEL"], bool(r["y"]))
    counts = Counter(cls.values())
    by_family = {}
    for r in rows:
        by_family.setdefault(r["family"], Counter())[cls[r["world_id"]]] += 1
    bnd: Dict[str, list] = {}
    for src, dst, kind in edges:
        if src in cls and dst in cls:
            bnd.setdefault(kind, []).append(cls[src] != cls[dst])
    return {"battery": BATTERY, "n_nodes": len(cls), "n_classes": len(counts),
            "compression": round(len(counts) / max(1, len(cls)), 4),
            "classes": {"".join(map(str, k)): v for k, v in counts.most_common()},
            "classes_by_family": {f: {"".join(map(str, k)): v for k, v in c.most_common()} for f, c in by_family.items()},
            "boundary_edge_fraction": {k: round(sum(v) / len(v), 4) for k, v in bnd.items()},
            "boundary_edges_n": {k: len(v) for k, v in bnd.items()}}
