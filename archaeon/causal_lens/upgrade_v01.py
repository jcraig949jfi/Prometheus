"""Deterministic v0.1 -> v0.2 upgrader. It never invents information: whatever v0.1 could not express becomes NOT_IDENTIFIABLE, and
the original v0.1 value is kept verbatim under `v01` on the node.

Mapping (CONTRACT_v0.1_to_v0.2.md):
  ENTITY e          -> BODY e + IDENTITY "id:"+e assigned to it (v0.1 cannot tell a rename from a new body: prop body_identity_split = NI)
  owns              -> carries;  hosts (ENTITY->T) -> hosted_by (T->BODY);  labelled_parent (E->E) -> labelled_parent (id:E -> id:E)
  executor / host   -> executor_body / host_body (+ executor_identity = id:executor)
  executed_material -> write_governing = NI and execution_share = NI (the v0.1 role is ambiguous: B3), value kept under v01
  child_contributors-> factual_contributors (v0.1 contributors were realized-trace or native claims by construction)
  material_origin   -> ancestry_origin;  made_in absent (unknown, not asserted)
  resulting_hu      -> resulting_hu; hu_continuity = resulting_hu for REPRODUCTION/AMPLIFICATION, NONE for ORIGINATION, NI otherwise
  ESTABLISHMENT resulting_hu -> persisting_object (kind HU)
"""
from __future__ import annotations

from typing import Tuple

from archaeon.causal_lens import schema as S1
from archaeon.causal_lens import schema_v02 as S2

REL_MAP = {"performed_by": "performed_by", "governed_by": None, "produced": "produced", "copies_from": "copies_from",
           "contributes_material": "contributes_material", "mutates_from": "mutates_from", "recombines_with": "recombines_with",
           "transports": "transports", "enables": "enables", "member_of": "member_of", "via": "via", "consumes": "consumes"}


def upgrade(g1: S1.Graph, hu_rule=None) -> Tuple[S2.Graph, dict]:
    gran = g1.gran if g1.gran in S2.GRAN else "body"
    if g1.gran == "entity": gran = "body"
    g = S2.Graph(g1.engine, gran, {"hu_rule": hu_rule or {"kind": "MAJORITY", "threshold": 0.5, "no_majority": "ORIGINATE"},
                                   "upgraded_from": "v0.1"}, dict(g1.meta, upgraded_from="prometheus.causal_lineage.v0.1"))
    report = {"entities_split": 0, "executed_material_unassigned": 0, "fields_marked_ni": 0}
    for nid, a in g1.nodes.items():
        k = a["kind"]; attrs = {x: y for x, y in a.items() if x not in ("kind", "fields", "types", "props")}
        if k == "ENTITY":
            g.node(nid, "BODY", **attrs); g.node("id:" + nid, "IDENTITY"); g.edge("id:" + nid, "assigned", nid)
            g.prop(nid, "body_identity_split", S2.NI, "DERIVED", "v0.1 ENTITY conflated body and identity"); report["entities_split"] += 1
        elif k == "TRANSFORMATION":
            g.node(nid, "TRANSFORMATION", types=list(a["types"]), fields={}, v01=a.get("fields"))
        elif k in ("MATERIAL", "HU", "EXECUTION", "ENV"):
            g.node(nid, k, **attrs)
        for pname, p in a.get("props", {}).items():
            g.prop(nid, pname, p["value"], p["basis"], p.get("source", ""))           # kept verbatim: an invalid v0.1 value stays invalid
    for s, r, t, at in g1.edges:
        if r == "owns": g.edge(s, "carries", t, **at)
        elif r == "hosts": g.edge(t, "hosted_by", s, **at)
        elif r == "labelled_parent": g.edge("id:" + s, "labelled_parent", "id:" + t, **at)
        elif r == "governed_by": g.edge(s, "execution_share", t, **dict(at, v01_role="governed_by (ambiguous)"))
        elif REL_MAP.get(r): g.edge(s, REL_MAP[r], t, **at)
    for t in g1.of_kind("TRANSFORMATION"):
        f1 = g1.nodes[t]["fields"]; ty = set(g1.nodes[t]["types"])
        def put(name, fd, **extra):
            g.field(t, name, fd["value"], fd["basis"], fd.get("granularity"), fd.get("source", ""), **extra)
        if "executor" in f1: put("executor_body", f1["executor"])
        if "host" in f1: put("host_body", f1["host"])
        if "executed_material" in f1:
            g.field(t, "write_governing", S2.NI, "DERIVED", source="v0.1 executed_material role ambiguous (B3)")
            g.field(t, "execution_share", S2.NI, "DERIVED", source="v0.1 executed_material role ambiguous (B3)")
            report["executed_material_unassigned"] += 1; report["fields_marked_ni"] += 2
        if "child_contributors" in f1:
            fd = f1["child_contributors"]; extra = {"native_count": fd["native_count"]} if "native_count" in fd else {}
            v = fd["value"]
            if v == S1.NA: v = S2.NA
            put("factual_contributors", dict(fd, value=v), **extra)
        if "material_origin" in f1: put("ancestry_origin", f1["material_origin"])
        if "env_dependencies" in f1: put("env_dependencies", f1["env_dependencies"])
        rh = f1.get("resulting_hu")
        if "ESTABLISHMENT" in ty and rh:
            put("persisting_object", rh)
        elif rh:
            put("resulting_hu", rh)
            if {"REPRODUCTION", "AMPLIFICATION"} & ty and isinstance(rh["value"], str) and rh["value"] in g1.nodes: hc = rh["value"]
            elif "ORIGINATION" in ty: hc = S2.NONE
            else: hc = S2.NI; report["fields_marked_ni"] += 1
            g.field(t, "hu_continuity", hc, "DERIVED", source="upgrader from v0.1 event types")
    return g, report
