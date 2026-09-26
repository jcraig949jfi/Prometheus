"""Archaeon reference adapter: archaeon.lineage.core World birth events + glin registry -> canonical causal graph (contract v0.1).

Native record (per birth, core.World._birth): executor_cell/oid/glin, executed_material (self|neighbour|mixed) + exec_counts, child_cell,
child_glin, template (executor|neighbour), template_glin, contributors (glins), copied_exec, copied_nbr, computed, host_glin, mechanism,
exact, novel_genome. Registry (World.gl): glin -> root, origin (random_inflow|control_inserted|originated), inserted, parents, hosts, ...

Granularity: SEGMENT. The native world tracks per-byte material ids, but a birth event records only per-source byte COUNTS, so the
adapter emits one material part per source (executor-copied, neighbour-copied, computed, other-new) with its share of the 32 bytes.
Claims at byte resolution are therefore not made (I12). The remainder part ("other-new": copy-noise mutation, input-derived, constant)
has no origin class in the event record, so it gets none (not UNKNOWN, not MUTATION): the adapter abstains.

Basis: TRACE for executor / executed material / contributors (the taint VM traced the data flow); NATIVE_RECORD for glin origin;
DERIVED for "an organism's material descends from its glin founder" (true by the glin rule: a birth continues a glin only when the
template supplied >= G/2 copied bytes).
"""
from __future__ import annotations

from typing import Iterable, Optional

from archaeon.causal_lens.schema import Graph, NONE, NI

G = 32
ORIGIN_MAP = {"random_inflow": "RANDOM_INFLOW", "control_inserted": "INSERTED_SEED", "seeded_test": "INSERTED_SEED", "originated": None}
MECH_TYPES = {"SELF_COPY": ["REPRODUCTION"], "HOST_EXECUTION": ["REPRODUCTION", "AMPLIFICATION", "HOSTING"],
              "NEIGHBOUR_COPY": ["REPRODUCTION", "AMPLIFICATION", "HOSTING"], "ORIGINATION": ["ORIGINATION"]}


def _hu(g: Graph, glin: int, reg: dict) -> str:
    h = "glin:%d" % glin
    if h in g.nodes: return h
    st = reg.get(glin, {})
    g.node(h, "HU", native_root=st.get("root"), native_origin=st.get("origin"))
    f = "found:%d" % glin
    o = ORIGIN_MAP.get(st.get("origin"))
    if st.get("root") in ("arrival", "inserted", "seeded_test") or o:
        g.node(f, "MATERIAL", **({"origin": o} if o else {})); g.edge(f, "member_of", h)
    return h


def _org_material(g: Graph, oid, glin: int, reg: dict, tag: str) -> str:
    """Material carried by one organism; descends from its glin founder (DERIVED)."""
    m = "mat:%s" % tag
    if m in g.nodes: return m
    h = _hu(g, glin, reg); g.node(m, "MATERIAL"); g.edge(m, "member_of", h)
    f = "found:%d" % glin
    if f in g.nodes and m != f: g.edge(m, "copies_from", f, basis="DERIVED", rule="glin continuity (template >= G/2 copied bytes)")
    return m


def add_events(g: Graph, events: Iterable[dict], reg: dict, prefix: str = "ev", origination_parts: Optional[dict] = None) -> Graph:
    for k, ev in enumerate(events):
        t = "%s%d" % (prefix, k); x = "x:%s" % t
        ex_ent = "org:%s" % ev["executor_oid"]; g.node(ex_ent, "ENTITY", cell=ev["executor_cell"])
        ch_ent = "child:%s" % t; g.node(ch_ent, "ENTITY", cell=ev["child_cell"])
        g.edge(ch_ent, "labelled_parent", ex_ent, native="ENVGATE-01 parent chain: child lineage label = executor's")   # I11: kept, never read
        exec_mat = _org_material(g, ev["executor_oid"], ev["executor_glin"], reg, "oid%s" % ev["executor_oid"])
        g.edge(ex_ent, "owns", exec_mat)
        nbr_glin = None
        if ev["copied_nbr"] > 0 or ev["exec_counts"].get("nbr", 0) > 0:
            others = [c for c in ev["contributors"] if c != ev["executor_glin"]]
            nbr_glin = ev["template_glin"] if ev["template"] == "neighbour" and ev["template_glin"] is not None else (others[0] if len(others) == 1 else None)
        nbr_mat = None
        if nbr_glin is not None:
            nbr_mat = _org_material(g, None, nbr_glin, reg, "occupant@%s" % t); g.node("occ:%s" % t, "ENTITY", cell=ev["child_cell"]); g.edge("occ:%s" % t, "owns", nbr_mat)
        g.node(x, "EXECUTION"); g.edge(x, "performed_by", ex_ent)
        sc = ev["exec_counts"]; tot = max(1, sc.get("self", 0) + sc.get("nbr", 0) + sc.get("other", 0))
        gov = []
        if sc.get("self", 0): g.edge(x, "governed_by", exec_mat, share=round(sc["self"] / tot, 4)); gov.append(exec_mat)
        if sc.get("nbr", 0):
            if nbr_mat is not None: g.edge(x, "governed_by", nbr_mat, share=round(sc["nbr"] / tot, 4)); gov.append(nbr_mat)
            else: gov.append(NI)
        mech = ev["mechanism"].split("+")[0]; types = list(MECH_TYPES.get(mech, ["UNCLASSIFIED"]))
        if "+RECOMBINATION" in ev["mechanism"]: types.append("RECOMBINATION")
        child_hu = _hu(g, ev["child_glin"], reg)
        host = ("org:%s" % ev["executor_oid"]) if ev["host_glin"] is not None else NONE
        contrib = ["glin:%d" % c for c in ev["contributors"]]
        for c in ev["contributors"]: _hu(g, c, reg)
        g.event(t, types)
        g.field(t, "executor", ex_ent, "TRACE", "entity")
        g.field(t, "executed_material", gov if gov else NONE, "TRACE", "genome", source="taint VM opcode-fetch source counts")
        g.field(t, "child_contributors", contrib, "TRACE", "segment", source="taint VM per-byte labels", native_count=len(ev["contributors"]))
        g.field(t, "host", host, "TRACE", "entity")
        g.field(t, "resulting_hu", child_hu, "TRACE", "genome")
        g.field(t, "env_dependencies", NI, "DECLARED", source="per-birth input dependence not recorded; arm-level only")
        g.edge(t, "via", x)
        if host != NONE: g.edge(host, "hosts", t)
        g.edge(t, "consumes", ex_ent)
        if "ORIGINATION" in types: g.edge(t, "produced", child_hu)
        # child material parts
        parts = []
        if ev["copied_exec"]:
            p = "%s:partE" % t; g.node(p, "MATERIAL", share=ev["copied_exec"] / G); g.edge(p, "copies_from", exec_mat); parts.append(p)
        if ev["copied_nbr"]:
            p = "%s:partN" % t; g.node(p, "MATERIAL", share=ev["copied_nbr"] / G)
            if nbr_mat is not None: g.edge(p, "copies_from", nbr_mat)
            parts.append(p)
        if ev["computed"]:
            p = "%s:partX" % t; g.node(p, "MATERIAL", share=ev["computed"] / G, origin="COMPUTED")
            for c in ev["contributors"]:
                src = exec_mat if c == ev["executor_glin"] else nbr_mat
                if src is not None: g.edge(src, "contributes_material", p)
            parts.append(p)
        rest = G - ev["copied_exec"] - ev["copied_nbr"] - ev["computed"]
        if rest > 0:
            p = "%s:partNew" % t; g.node(p, "MATERIAL", share=rest / G, note="mutation / input / constant bytes (breakdown not in event)"); parts.append(p)
        for p in parts:
            g.edge(t, "produced", p); g.edge(p, "member_of", child_hu); g.edge(ch_ent, "owns", p)
    return g


def add_establishments(g: Graph, reg: dict, established: Iterable[int], prefix="est"):
    for gg in established:
        h = _hu(g, gg, reg); g.event("%s:%d" % (prefix, gg), ["ESTABLISHMENT"])
        g.field("%s:%d" % (prefix, gg), "resulting_hu", h, "NATIVE_RECORD", "genome", source="World.genetic_establishments")
    return g


def from_world(w, engine_tag="archaeon.lineage", events=None) -> Graph:
    g = Graph(engine_tag, "segment", {"world": w.name})
    reg = w.gl
    add_events(g, events if events is not None else w.events, reg)
    add_establishments(g, reg, w.genetic_establishments())
    return g
