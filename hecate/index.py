"""Global discovery index (charter GLOBAL DISCOVERY INDEX), derived from the
program records; never hand-edited.

Node types: concept, triplicate, historical_artifact, hypothesis
(interpretation | mechanism), lens, experiment, engine, anomaly,
rejected_explanation, surviving_principle.
Edge types (charter list, plus has_concept / targets / historical_source,
which the charter's list implies but does not name):
derived_from, contradicts, supports, transfers_to, shares_structure_with,
falsified_by, implemented_as, observed_under, human_flagged,
cross_collided_with, has_concept, historical_source.

    python -m hecate.index      # writes hecate/index/{nodes,edges}.jsonl + SUMMARY.json
"""

from __future__ import annotations

import collections
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROG_GLOB = os.path.join(ROOT, "hecate", "programs", "*", "program.json")
OUT = os.path.join(ROOT, "hecate", "index")


def _q(tid, local):
    return f"{tid}/{local}"


def build(paths=None):
    nodes, edges = {}, []

    def node(nid, ntype, **attrs):
        nodes.setdefault(nid, {"id": nid, "type": ntype, **attrs})

    def edge(src, dst, etype, **attrs):
        edges.append({"src": src, "dst": dst, "type": etype, **attrs})

    for path in sorted(paths or glob.glob(PROG_GLOB)):
        with open(path, encoding="utf-8") as fh:
            p = json.load(fh)
        tid = p["id"]
        node(tid, "triplicate", key=p.get("key"), verdict=p.get("currentVerdict"),
             source=(p.get("provenance") or {}).get("source"))
        for c in p.get("concepts") or []:
            cid = "concept:" + c["name"]
            node(cid, "concept", field=c.get("field"), mechanism=c.get("mechanism"))
            edge(tid, cid, "has_concept")
        prov = p.get("provenance") or {}
        if prov.get("sourceArtifact"):
            hid = "hist:" + prov["sourceArtifact"]
            node(hid, "historical_artifact", historicalId=prov.get("historicalId"),
                 source=prov.get("source"))
            edge(tid, hid, "historical_source")
        for parent in prov.get("derived_from") or []:
            edge(tid, parent, "derived_from")

        for h in p.get("hypotheses") or []:
            hid = _q(tid, h["id"])
            node(hid, "hypothesis", kind=h.get("kind"), form=h.get("form"),
                 layer=h.get("layer"), passId=h.get("passId"),
                 statement=(h.get("statement") or "")[:240])
            edge(hid, tid, "derived_from", note="belongs to triplicate")
            for d in h.get("derived_from") or []:
                edge(hid, _q(tid, d), "derived_from")
            for rel in ("supports", "contradicts", "shares_structure_with",
                        "transfers_to", "falsified_by", "cross_collided_with"):
                for d in h.get(rel) or []:
                    edge(hid, d if "/" in d else _q(tid, d), rel)
        for lens in p.get("lenses") or []:
            lid = _q(tid, lens["id"])
            node(lid, "lens", name=lens.get("name"), passId=lens.get("passId"))
            for m in lens.get("targets") or []:
                edge(_q(tid, m), lid, "observed_under")
        for w in p.get("experiments") or []:
            wid = _q(tid, w["id"])
            node(wid, "experiment", substrate=w.get("substrate"),
                 passId=w.get("passId"), outcome=w.get("outcome"))
            for m in w.get("mechanism_ids") or []:
                edge(_q(tid, m), wid, "implemented_as")
            for l in w.get("lens_ids") or []:
                edge(wid, _q(tid, l), "observed_under")
            for i, s in enumerate(w.get("rejected_explanations") or []):
                rid = f"{wid}/rejected/{i}"
                node(rid, "rejected_explanation", text=str(s)[:240])
                edge(wid, rid, "falsified_by", note="explanation ruled out by this world")
            for a in w.get("anomalies") or []:
                aid = f"{wid}/anomaly/{a.get('id')}"
                node(aid, "anomaly", text=(a.get("text") or "")[:240])
                edge(aid, wid, "observed_under")
                if a.get("human_flagged"):
                    edge(aid, wid, "human_flagged")
        for e in p.get("candidateEngines") or []:
            eid = _q(tid, e.get("id") or e.get("name"))
            node(eid, "engine", name=e.get("name"))
            edge(eid, tid, "derived_from")

    counts = {
        "nodes": dict(collections.Counter(n["type"] for n in nodes.values())),
        "edges": dict(collections.Counter(e["type"] for e in edges)),
        "mechanism_forms_across_triplicates": _form_recurrence(nodes),
    }
    return list(nodes.values()), edges, counts


def _form_recurrence(nodes):
    """How many distinct triplicates produced a mechanism of each form. A
    coarse, label-level recurrence count only: two mechanisms of the same
    form are NOT the same mechanism. Structural recurrence needs the gravity
    detector's family names (HECATE-13) and is not computed here."""
    by_form = collections.defaultdict(set)
    for n in nodes.values():
        if n["type"] == "hypothesis" and n.get("kind") == "mechanism":
            by_form[n.get("form")].add(n["id"].split("/")[0])
    return {str(k): len(v) for k, v in sorted(by_form.items(), key=lambda t: -len(t[1]))}


def write():
    nodes, edges, counts = build()
    os.makedirs(OUT, exist_ok=True)
    for name, rows in (("nodes", nodes), ("edges", edges)):
        with open(os.path.join(OUT, f"{name}.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
            for r in sorted(rows, key=lambda r: json.dumps(r, sort_keys=True)):
                fh.write(json.dumps(r, sort_keys=True, ensure_ascii=True) + "\n")
    with open(os.path.join(OUT, "SUMMARY.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(counts, indent=2, sort_keys=True) + "\n")
    return counts


if __name__ == "__main__":
    print(json.dumps(write(), indent=2, sort_keys=True))
