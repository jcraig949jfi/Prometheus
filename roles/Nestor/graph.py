"""EXPERIMENT_GRAPH.jsonl: the resumable research graph (charter section 2).

Append-only. A node's later state is a new line with the same experiment_id; the LAST
line for an id wins. Nothing is ever rewritten in place, so the graph's own history is
auditable.

    python graph.py show            # current state of every node
    python graph.py open            # nodes whose status is not CLOSED / RETIRED
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

GRAPH = pathlib.Path(__file__).resolve().parent / "EXPERIMENT_GRAPH.jsonl"
FIELDS = ("experiment_id", "parent_ids", "question", "lane", "mutation_class", "reason",
          "protocol_hash", "budget", "status", "outcome", "classification", "weak_signal",
          "child_ids", "retirement_reason", "evidence")
LANES = ("EXPLORE", "CONFIRM", "FORENSIC", "INFRA")
CLASSES = (None, "SIGNAL", "WEAK_SIGNAL", "CLEAN_NULL", "INVALID", "INFRASTRUCTURE",
           "INSTRUMENT", "DEFECT_FOUND")
STATUSES = ("PLANNED", "ACTIVE", "RUNNING", "ADJUDICATING", "CLOSED", "RETIRED", "WITHHELD")


def state():
    cur = {}
    if GRAPH.exists():
        for line in GRAPH.read_text(encoding="utf-8").splitlines():
            if line.strip():
                n = json.loads(line)
                cur[n["experiment_id"]] = {**cur.get(n["experiment_id"], {}), **n}
    return cur


def put(**node):
    """Append a node (or a state update: only the changed fields are needed)."""
    assert "experiment_id" in node
    unknown = set(node) - set(FIELDS) - {"ts"}
    assert not unknown, unknown
    if "lane" in node:
        assert node["lane"] in LANES, node["lane"]
    if "classification" in node:
        assert node["classification"] in CLASSES, node["classification"]
    if "status" in node:
        assert node["status"] in STATUSES, node["status"]
    node = dict(node, ts=time.strftime("%Y-%m-%dT%H:%M:%S"))
    with GRAPH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(node, sort_keys=True) + "\n")
    return node


if __name__ == "__main__":
    s = state()
    which = sys.argv[1] if len(sys.argv) > 1 else "show"
    for k, n in s.items():
        if which == "open" and n.get("status") in ("CLOSED", "RETIRED", "WITHHELD"):
            continue
        print("%-28s %-9s %-8s %-14s %s" % (k, n.get("status"), n.get("lane"),
                                            n.get("classification"), (n.get("question") or "")[:70]))
