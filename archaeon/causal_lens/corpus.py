"""Synthetic conformance corpus (PORTABILITY-01 s5): twelve engine-independent fixtures with their expected causal relations.

Each fixture returns (graph, expected, cheats):
  graph     the honest canonical account (must pass Graph.check() with zero violations)
  expected  answers the lens must give (queries in `answer`)
  cheats    {name: (mutated graph, violation-id prefix it must trigger)} -- a checker that accepts a cheat is not an instrument
Material is modelled at SEGMENT granularity (a "segment" is any engine's smallest tracked heritable part) so nothing here assumes bytes.
"""
from __future__ import annotations

import copy
from typing import Callable, Dict, Tuple

from archaeon.causal_lens.schema import Graph, YES, NO, NI, NONE, NA, spontaneous


def _mat(g, mid, origin=None, hu=None, owner=None):
    g.node(mid, "MATERIAL", **({"origin": origin} if origin else {}))
    if hu: g.node(hu, "HU"); g.edge(mid, "member_of", hu)
    if owner: g.node(owner, "ENTITY"); g.edge(owner, "owns", mid)
    return mid


def _exec(g, xid, executor, governed):
    g.node(xid, "EXECUTION"); g.edge(xid, "performed_by", executor)
    for m in governed: g.edge(xid, "governed_by", m)
    return xid


def _F(v, basis="DECLARED", **kw):
    return dict(value=v, basis=basis, **kw)


def answer(g: Graph) -> dict:
    """The engine-neutral answers compared against `expected`."""
    out = {"violations": g.check(), "establishments": sorted(g.establishments()), "hus": sorted(g.of_kind("HU"))}
    out["spontaneous"] = {h: spontaneous(g, h) for h in g.of_kind("HU")}
    out["contributors"] = {t: sorted(g.contributors_hu(t)) for t in g.of_kind("TRANSFORMATION")}
    out["executor"] = {t: g.nodes[t]["fields"].get("executor", {}).get("value") for t in g.of_kind("TRANSFORMATION")}
    out["host"] = {t: g.nodes[t]["fields"].get("host", {}).get("value") for t in g.of_kind("TRANSFORMATION")}
    return out


# ------------------------------------------------------------------------------------------------ fixtures
def f01_autonomous_copier():
    g = Graph("synthetic", "segment")
    _mat(g, "mA", "RANDOM_INFLOW", "hA", "A"); _exec(g, "x1", "A", ["mA"])
    g.event("t1", ["REPRODUCTION"], executor=_F("A"), executed_material=_F(["mA"]), child_contributors=_F(["hA"]), host=_F(NONE), resulting_hu=_F("hA"))
    g.edge("t1", "via", "x1"); _mat(g, "mC", None, "hA", "C"); g.edge("t1", "produced", "mC"); g.edge("mC", "copies_from", "mA")
    exp = {"contributors": {"t1": ["hA"]}, "spontaneous": {"hA": YES}, "executor": {"t1": "A"}, "host": {"t1": NONE}}
    ch = copy.deepcopy(g); ch.field("t1", "child_contributors", ["A"], "DECLARED")
    return g, exp, {"executor_named_as_contributor": (ch, "I2/I3")}


def f02_inserted_copier():
    g, _, _ = f01_autonomous_copier(); g.nodes["mA"]["origin"] = "INSERTED_SEED"
    exp = {"spontaneous": {"hA": NO}, "contributors": {"t1": ["hA"]}}
    ch = copy.deepcopy(g); ch.prop("hA", "spontaneous", YES, "NATIVE_RECORD", "label renamed to 'spontaneous'")
    return g, exp, {"inserted_relabelled_spontaneous": (ch, "I1")}


def f03_transplanted_copier():
    g = Graph("synthetic", "segment", {"worlds": ["donor", "recipient"]})
    _mat(g, "mD", "RANDOM_INFLOW", "hD", "D")                                   # donor-world material, random origin there
    g.event("tx", ["TRANSFER"], executor=_F(NONE), host=_F(NONE), child_contributors=_F(["hD"]), resulting_hu=_F("hD"))
    _mat(g, "mT", "TRANSPLANT", "hD", "T"); g.edge("tx", "produced", "mT"); g.edge("mT", "copies_from", "mD")
    g.node("operator", "ENTITY"); g.edge("operator", "transports", "mT")
    exp = {"spontaneous": {"hD": NO}, "contributors": {"tx": ["hD"]}, "origins_hD": ["RANDOM_INFLOW", "TRANSPLANT"]}
    ch = copy.deepcopy(g); ch.edges = [e for e in ch.edges if e[1] != "copies_from"]; ch._out.clear(); ch._in.clear()
    for s, r, t, a in ch.edges: ch._out[(s, r)].append(t); ch._in[(t, r)].append(s)
    return g, exp, {"transplant_severed_from_donor": (ch, "I7")}


def f04_random_origin_copier():
    g = Graph("synthetic", "segment")
    g.node("inflow", "ENV")
    g.event("t0", ["ORIGINATION"], executor=_F(NONE), host=_F(NONE), resulting_hu=_F("hR"), material_origin=_F(["RANDOM_INFLOW"]))
    _mat(g, "mR", "RANDOM_INFLOW", None, "R"); g.node("hR", "HU"); g.edge("mR", "member_of", "hR"); g.edge("t0", "produced", "mR"); g.edge("t0", "produced", "hR")
    g.edge("inflow", "transports", "mR")
    _exec(g, "x1", "R", ["mR"]); g.event("t1", ["REPRODUCTION"], executor=_F("R"), host=_F(NONE), child_contributors=_F(["hR"]), resulting_hu=_F("hR"))
    g.edge("t1", "via", "x1"); _mat(g, "mC", None, "hR", "C"); g.edge("t1", "produced", "mC"); g.edge("mC", "copies_from", "mR")
    g.event("tE", ["ESTABLISHMENT"], resulting_hu=_F("hR"))
    exp = {"spontaneous": {"hR": YES}, "establishments": ["hR"], "contributors": {"t1": ["hR"]}}
    ch = copy.deepcopy(g); ch.nodes["t1"]["types"] = ["ORIGINATION"]
    return g, exp, {"reproduction_called_origination": (ch, "I9")}


def f05_host_executes_foreign_copier():
    """ENVGATE-01 block-15 shape: an inert host executes the resident's copier code and emits the resident's genome."""
    g = Graph("synthetic", "segment")
    _mat(g, "mH", "RANDOM_INFLOW", "hH", "H"); _mat(g, "mR", "RANDOM_INFLOW", "hR", "R")
    _exec(g, "x1", "H", ["mH", "mR"])                                             # executor H; executed material: its own AND the resident's
    g.event("t1", ["REPRODUCTION", "AMPLIFICATION", "HOSTING"], executor=_F("H"), executed_material=_F(["mH", "mR"]), host=_F("H"),
            child_contributors=_F(["hR"]), resulting_hu=_F("hR"))
    g.edge("t1", "via", "x1"); g.edge("H", "hosts", "t1")
    _mat(g, "mC", None, "hR", "C"); g.edge("t1", "produced", "mC"); g.edge("mC", "copies_from", "mR")
    exp = {"contributors": {"t1": ["hR"]}, "executor": {"t1": "H"}, "host": {"t1": "H"}}
    ch = copy.deepcopy(g); ch.field("t1", "child_contributors", ["hH"], "DERIVED", source="executor lineage")
    return g, exp, {"executor_lineage_as_contributor": (ch, "I2/I3")}


def f06_mutation_novel_element():
    g = Graph("synthetic", "segment")
    _mat(g, "mP1", "RANDOM_INFLOW", "hA", "A"); _mat(g, "mP2", "RANDOM_INFLOW", "hA"); g.edge("A", "owns", "mP2")
    _exec(g, "x1", "A", ["mP1", "mP2"])
    g.event("t1", ["REPRODUCTION", "MUTATION"], executor=_F("A"), host=_F(NONE), child_contributors=_F(["hA"]), resulting_hu=_F("hA"))
    g.edge("t1", "via", "x1")
    _mat(g, "mC1", None, "hA", "C"); g.edge("mC1", "copies_from", "mP1")
    _mat(g, "mN", "MUTATION", "hA"); g.edge("C", "owns", "mN"); g.edge("mN", "mutates_from", "mP2")
    g.edge("t1", "produced", "mC1"); g.edge("t1", "produced", "mN")
    exp = {"origins_mN": ["MUTATION"], "origins_mC1": ["RANDOM_INFLOW"], "contributors": {"t1": ["hA"]}}
    ch = copy.deepcopy(g); ch.edges = [e for e in ch.edges if e[1] != "mutates_from"]; ch._out.clear(); ch._in.clear()
    for s, r, t, a in ch.edges: ch._out[(s, r)].append(t); ch._in[(t, r)].append(s)
    return g, exp, {"mutation_without_provenance": (ch, "I5")}


def f07_recombination_two_donors():
    g = Graph("synthetic", "segment")
    _mat(g, "mA", "RANDOM_INFLOW", "hA", "A"); _mat(g, "mB", "RANDOM_INFLOW", "hB", "B")
    _exec(g, "x1", "A", ["mA"])
    g.event("t1", ["ORIGINATION", "RECOMBINATION"], executor=_F("A"), host=_F(NONE), child_contributors=_F(["hA", "hB"], native_count=2),
            resulting_hu=_F("hX"))
    g.edge("t1", "via", "x1")
    g.node("hX", "HU"); g.edge("t1", "produced", "hX")
    _mat(g, "mX1", None, "hX", "X"); g.edge("mX1", "copies_from", "mA"); _mat(g, "mX2", None, "hX"); g.edge("mX2", "copies_from", "mB")
    g.edge("mX1", "recombines_with", "mX2"); g.edge("t1", "produced", "mX1"); g.edge("t1", "produced", "mX2")
    exp = {"contributors": {"t1": ["hA", "hB"]}, "spontaneous": {"hX": YES, "hA": YES, "hB": YES}}
    ch = copy.deepcopy(g); ch.field("t1", "child_contributors", ["hA"], "NATIVE_RECORD", source="single parent field"); ch.nodes["t1"]["fields"]["child_contributors"]["native_count"] = 2
    return g, exp, {"recombination_truncated_to_one_parent": (ch, "I6")}


def f08_ecological_assistance():
    g = Graph("synthetic", "segment")
    _mat(g, "mA", "RANDOM_INFLOW", "hA", "A"); _mat(g, "mF", "RANDOM_INFLOW", "hF", "F")
    _exec(g, "x1", "A", ["mA"])
    g.event("t1", ["REPRODUCTION", "HOSTING"], executor=_F("A"), host=_F("F"), child_contributors=_F(["hA"]), resulting_hu=_F("hA"))
    g.edge("t1", "via", "x1"); g.edge("F", "hosts", "t1")                          # F supplied location / resources only
    _mat(g, "mC", None, "hA", "C"); g.edge("t1", "produced", "mC"); g.edge("mC", "copies_from", "mA")
    exp = {"contributors": {"t1": ["hA"]}, "host": {"t1": "F"}}
    ch = copy.deepcopy(g); ch.field("t1", "child_contributors", ["hA", "hF"], "DERIVED", source="host lineage")
    return g, exp, {"host_as_contributor": (ch, "I2/I3")}


def f09_takeover_many_labels_one_architecture(n_hosts: int = 20):
    """ENVGATE-01 block-15 at population scale: n native lineage labels, ONE heritable unit."""
    g = Graph("synthetic", "segment")
    g.event("tO", ["ORIGINATION"], executor=_F(NONE), resulting_hu=_F("hR")); _mat(g, "mR", "RANDOM_INFLOW", None, "R")
    g.node("hR", "HU"); g.edge("mR", "member_of", "hR"); g.edge("tO", "produced", "mR"); g.edge("tO", "produced", "hR")
    for k in range(n_hosts):
        h = "H%d" % k; _mat(g, "mH%d" % k, "RANDOM_INFLOW", "hH%d" % k, h)
        g.event("tH%d" % k, ["ORIGINATION"], executor=_F(NONE), resulting_hu=_F("hH%d" % k)); g.edge("tH%d" % k, "produced", "hH%d" % k)
        _exec(g, "x%d" % k, h, ["mH%d" % k, "mR"])
        t = "t%d" % k
        g.event(t, ["REPRODUCTION", "AMPLIFICATION", "HOSTING"], executor=_F(h), host=_F(h), child_contributors=_F(["hR"]), resulting_hu=_F("hR"))
        g.edge(t, "via", "x%d" % k); g.edge(h, "hosts", t)
        _mat(g, "mC%d" % k, None, "hR", "C%d" % k); g.edge(t, "produced", "mC%d" % k); g.edge("mC%d" % k, "copies_from", "mR")
        g.edge("C%d" % k, "labelled_parent", h)                                      # native parent pointer = the HOST (a distinct label per host)
    g.event("tE", ["ESTABLISHMENT"], resulting_hu=_F("hR"))
    exp = {"establishments": ["hR"], "native_labels": n_hosts}
    ch = copy.deepcopy(g)
    for k in range(n_hosts):                                                          # count each host label as its own lineage
        ch.node("L%d" % k, "HU"); ch.edge("t%d" % k, "produced", "L%d" % k); ch.event("tE%d" % k, ["ESTABLISHMENT"], resulting_hu=_F("L%d" % k))
    return g, exp, {"host_labels_as_lineages": (ch, "I9")}


def f10_multiple_independent_establishments(k: int = 3):
    g = Graph("synthetic", "segment")
    for i in range(k):
        g.event("t0_%d" % i, ["ORIGINATION"], executor=_F(NONE), resulting_hu=_F("h%d" % i))
        _mat(g, "m%d" % i, "RANDOM_INFLOW", None, "R%d" % i); g.node("h%d" % i, "HU"); g.edge("m%d" % i, "member_of", "h%d" % i)
        g.edge("t0_%d" % i, "produced", "m%d" % i); g.edge("t0_%d" % i, "produced", "h%d" % i)
        g.event("tE%d" % i, ["ESTABLISHMENT"], resulting_hu=_F("h%d" % i))
    exp = {"establishments": ["h%d" % i for i in range(k)], "spontaneous": {"h%d" % i: YES for i in range(k)}}
    ch = copy.deepcopy(g); ch.event("tE_dup", ["ESTABLISHMENT"], resulting_hu=_F("h0"))
    return g, exp, {"one_hu_established_twice": (ch, "I8")}


def f11_ancestry_unknowable():
    g = Graph("synthetic", "segment")
    _mat(g, "mP", "UNKNOWN", "hP", "P"); g.node("C", "ENTITY"); g.edge("C", "labelled_parent", "P")
    g.event("t1", ["UNCLASSIFIED"], executor=_F(NI, "NATIVE_RECORD"), child_contributors=_F(NI, "NATIVE_RECORD"), resulting_hu=_F(NI, "NATIVE_RECORD"))
    _mat(g, "mC", "UNKNOWN"); g.edge("C", "owns", "mC"); g.edge("t1", "produced", "mC")
    exp = {"spontaneous": {"hP": NI}, "contributors": {"t1": []}, "executor": {"t1": NI}}
    ch1 = copy.deepcopy(g); ch1.field("t1", "child_contributors", ["hP"], "NATIVE_RECORD", source="parent_id")
    ch2 = copy.deepcopy(g); ch2.prop("hP", "spontaneous", False, "DERIVED")
    return g, exp, {"parent_id_as_material_provenance": (ch1, "I10"), "unknown_coerced_to_false": (ch2, "I10")}


def f12_no_genome_concept():
    """Field dynamics / a global rule: state changes, no individual executor, no heritable unit."""
    g = Graph("synthetic", "population")
    g.node("rule", "ENV"); g.node("field_t0", "MATERIAL", origin="RANDOM_INIT"); g.node("field_t1", "MATERIAL", origin="COMPUTED")
    g.event("t1", ["UNCLASSIFIED"], executor=_F(NONE), executed_material=_F(NONE), host=_F(NONE), child_contributors=_F(NA),
            resulting_hu=_F(NA), env_dependencies=_F(["rule"]))
    g.edge("rule", "enables", "t1"); g.edge("t1", "consumes", "field_t0"); g.edge("t1", "produced", "field_t1")
    exp = {"hus": [], "establishments": []}
    ch = copy.deepcopy(g); ch.node("genome", "HU"); ch.edge("t1", "produced", "genome")
    return g, exp, {"manufactured_genome": (ch, "I9")}


FIXTURES: Dict[str, Callable[[], Tuple[Graph, dict, dict]]] = {f.__name__: f for f in (
    f01_autonomous_copier, f02_inserted_copier, f03_transplanted_copier, f04_random_origin_copier, f05_host_executes_foreign_copier,
    f06_mutation_novel_element, f07_recombination_two_donors, f08_ecological_assistance, f09_takeover_many_labels_one_architecture,
    f10_multiple_independent_establishments, f11_ancestry_unknowable, f12_no_genome_concept)}


def conform(g: Graph, expected: dict) -> list:
    """Mismatches between the lens's answers on g and the expected relations (empty = conformant)."""
    a = answer(g); bad = []
    if a["violations"]: bad.append(("violations", a["violations"]))
    for k, want in expected.items():
        if k in ("contributors", "spontaneous", "executor", "host"):
            for key, w in want.items():
                if a[k].get(key) != w: bad.append((k, key, a[k].get(key), w))
        elif k in ("establishments", "hus"):
            if a[k] != sorted(want): bad.append((k, a[k], sorted(want)))
        elif k.startswith("origins_"):
            node = k[len("origins_"):]; got = sorted(g.hu_origins(node) if g.nodes[node]["kind"] == "HU" else g.origins(node))
            if got != sorted(want): bad.append((k, got, sorted(want)))
        elif k == "native_labels":
            got = len({e[2] for e in g.edges if e[1] == "labelled_parent"})
            if got != want: bad.append((k, got, want))
    return bad
