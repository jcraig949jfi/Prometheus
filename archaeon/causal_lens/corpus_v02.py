"""Synthetic corpus v0.2: 15 fixtures that attack the v0.2 distinctions (ruling s10). Engine-independent (segment granularity).

Each fixture returns (graph, expected, prohibited):
  expected    facts the lens must report (checked by `facts`)
  prohibited  {name: (cheat graph, violation prefix)} -- inferences the contract must reject
"""
from __future__ import annotations

import copy
from typing import Callable, Dict, Tuple

from archaeon.causal_lens.schema_v02 import Graph, YES, NO, NI, NONE, NA, ILL, continuity, spontaneous

MAJ = {"kind": "MAJORITY", "threshold": 0.5, "tie": "ILL_POSED", "no_majority": "ILL_POSED"}


def F(v, basis="DECLARED", **kw):
    return dict(value=v, basis=basis, **kw)


def G(**meta):
    return Graph("synthetic", "segment", {"hu_rule": MAJ}, meta)


def body(g, b, ident=None, loc=None):
    g.node(b, "BODY")
    if ident: g.node(ident, "IDENTITY"); g.edge(ident, "assigned", b)
    if loc: g.node(loc, "LOCATION"); g.edge(b, "located_in", loc)
    return b


def mat(g, m, origin=None, hu=None, carrier=None, made_in=None):
    g.node(m, "MATERIAL", **({"origin": origin} if origin else {}))
    if hu: g.node(hu, "HU"); g.edge(m, "member_of", hu)
    if carrier: g.edge(carrier, "carries", m)
    if made_in: g.node(made_in, "LOCATION"); g.edge(m, "made_in", made_in)
    return m


def _rebuild(g):
    g._out.clear(); g._in.clear()
    for s, r, t, a in g.edges: g._out[(s, r)].append(t); g._in[(t, r)].append(s)
    return g


def _drop_edges(g, rel):
    g.edges = [e for e in g.edges if e[1] != rel]; return _rebuild(g)


def recomb(shares: Dict[str, float]):
    """child made of segments from donors with the given shares (rest = new material)."""
    g = G(); t = "t"; g.event(t, ["RECOMBINATION"]); body(g, "C", "idC"); out = {}
    for i, (d, s) in enumerate(shares.items()):
        body(g, "B" + d); mat(g, "m" + d, "RANDOM_INFLOW", "h" + d, "B" + d)
        p = mat(g, "c" + d, None, None, "C"); g.node(p, "MATERIAL", share=s); g.edge(p, "copies_from", "m" + d); g.edge(t, "produced", p); out["h" + d] = s
    c = continuity(out, MAJ)
    g.field(t, "factual_contributors", ["h" + d for d in shares], "TRACE", "segment", native_count=len(shares), shares=out)
    if c["hu_continuity"] == ILL:
        g.field(t, "hu_continuity", ILL, "DERIVED", ill_posed=c["ill_posed"]); g.field(t, "resulting_hu", ILL, "DERIVED", ill_posed=c["ill_posed"])
    else:
        h = c["hu_continuity"]; g.field(t, "hu_continuity", h, "DERIVED"); g.field(t, "resulting_hu", h, "DERIVED")
        g.nodes[t]["types"] = sorted(set(g.nodes[t]["types"]) | {"REPRODUCTION"})
        for p in g.out(t, "produced"): g.edge(p, "member_of", h)
    return g, c


def facts(g: Graph) -> dict:
    ev = {t: g.nodes[t]["fields"] for t in g.of_kind("TRANSFORMATION")}
    val = lambda t, k: ev[t].get(k, {}).get("value")
    return {"violations": g.check(), "hu_continuity": {t: val(t, "hu_continuity") for t in ev if "hu_continuity" in ev[t]},
            "resulting_hu": {t: val(t, "resulting_hu") for t in ev if "resulting_hu" in ev[t]},
            "host_body": {t: val(t, "host_body") for t in ev if "host_body" in ev[t]},
            "architecture_class": {t: val(t, "architecture_class") for t in ev if "architecture_class" in ev[t]},
            "establishments": g.establishments(), "spontaneous": {h: spontaneous(g, h) for h in g.of_kind("HU")},
            "cf": {c: g.nodes[c]["result"] for c in g.of_kind("CF_TEST")}}


# ------------------------------------------------------------------------------------------------ the fifteen
def v01_symmetric_recombination():
    g, c = recomb({"A": 0.5, "B": 0.5})
    ch = copy.deepcopy(g); ch.field("t", "resulting_hu", "hA", "DERIVED"); ch.field("t", "hu_continuity", ILL, "DERIVED", ill_posed=c["ill_posed"])
    ch2 = copy.deepcopy(g); ch2.field("t", "hu_continuity", ILL, "DERIVED")
    return g, {"hu_continuity": {"t": ILL}, "resulting_hu": {"t": ILL}}, {"singular_continuity_despite_ill_posed": (ch, "J7"),
                                                                        "ill_posed_without_justification": (ch2, "J6")}


def v02_majority_recombination_60_40():
    g, c = recomb({"A": 0.6, "B": 0.4})
    ch = copy.deepcopy(g); ch.field("t", "factual_contributors", ["hA"], "TRACE", "segment", native_count=2)
    return g, {"hu_continuity": {"t": "hA"}, "resulting_hu": {"t": "hA"}}, {"minority_donor_dropped": (ch, "J5")}


def v03_rearranged_self_copy():
    """positional similarity 0.2 but 90% of bytes copied (out of position) from own material; ARCH = cyclic-rotation equivalence."""
    g = G(); body(g, "W", "idW"); mat(g, "mW", "RANDOM_INFLOW", "hW", "W")
    g.arch("archW", "equivalence", "cyclic_rotation_of_source", "the copy loop starts at an offset; rotation preserves the program up to entry point")
    g.edge("mW", "member_of_arch", "archW")
    g.node("x", "EXECUTION"); g.edge("x", "performed_by", "W"); g.edge("x", "write_governed_by", "mW", share=1.0)
    g.event("t", ["REPRODUCTION"], executor_body=F("W", "TRACE"), factual_contributors=F(["hW"], "TRACE", granularity="segment", shares={"hW": 0.9}),
            hu_continuity=F("hW", "DERIVED"), resulting_hu=F("hW", "DERIVED"), architecture_class=F("archW", "DERIVED"))
    g.edge("t", "via", "x"); body(g, "C"); p = mat(g, "cW", None, "hW", "C"); g.edge(p, "copies_from", "mW"); g.edge(p, "member_of_arch", "archW"); g.edge("t", "produced", p)
    g.node("t", "TRANSFORMATION", native_positional_fidelity=0.2)
    ch = copy.deepcopy(g); ch.arch("archS", "behavioral", "sequence_similarity>=0.9", "looks alike"); ch.field("t", "architecture_class", "archS", "DERIVED")
    ch2 = copy.deepcopy(g); ch2.field("t", "hu_continuity", "archW", "DERIVED")
    return g, {"hu_continuity": {"t": "hW"}, "architecture_class": {"t": "archW"}}, {"arch_from_similarity": (ch, "A1"), "arch_as_hu": (ch2, "J17")}


def v04_body_renamed_after_overwrite():
    g = G(); body(g, "V", "id7"); body(g, "D", "id3"); mat(g, "mD", "RANDOM_INIT", "hD", "D"); mat(g, "mV", "RANDOM_INIT", "hV", "V")
    g.node("id9", "IDENTITY")
    g.event("t", ["REPRODUCTION", "AMPLIFICATION", "HOSTING", "IDENTITY_CHANGE"], executor_body=F("D", "TRACE"), host_body=F("V", "TRACE"),
            factual_contributors=F(["hD"], "TRACE", granularity="segment"), hu_continuity=F("hD", "DERIVED"), resulting_hu=F("hD", "DERIVED"))
    g.edge("t", "consumes", "V"); g.edge("t", "produced", "V"); g.edge("t", "produced", "id9"); g.edge("id9", "assigned", "V", **{"from": "t"})
    g.edges[[i for i, e in enumerate(g.edges) if e[:3] == ["id7", "assigned", "V"]][0]][3]["until"] = "t"
    p = mat(g, "mV2", None, "hD", "V"); g.edge(p, "copies_from", "mD"); g.edge("t", "produced", p); g.edge("t", "hosted_by", "V")
    ch = copy.deepcopy(g); ch.field("t", "host_body", "id9", "NATIVE_RECORD")
    ch2 = copy.deepcopy(g); ch2.node("V2", "BODY"); ch2.edge("t", "produced", "V2")
    return g, {"host_body": {"t": "V"}}, {"identity_as_host": (ch, "J14"), "rename_creates_new_body": (ch2, "J15")}


def _exec_case(own_share, own_governs):
    g = G(); body(g, "W", "idW"); body(g, "P", "idP"); mat(g, "mW", "RANDOM_INFLOW", "hW", "W"); mat(g, "mP", "RANDOM_INFLOW", "hP", "P")
    g.node("x", "EXECUTION"); g.edge("x", "performed_by", "W")
    g.edge("x", "execution_share", "mW", share=own_share); g.edge("x", "execution_share", "mP", share=1 - own_share)
    g.edge("x", "write_governed_by", "mW" if own_governs else "mP", share=1.0)
    g.event("t", ["REPRODUCTION"], executor_body=F("W", "TRACE"),
            write_governing=F(["mW" if own_governs else "mP"], "TRACE", source="pc of the writing instructions"),
            execution_share=F({"mW": own_share, "mP": 1 - own_share}, "TRACE", source="step counts by region"),
            factual_contributors=F(["hW"], "TRACE", granularity="segment"), hu_continuity=F("hW", "DERIVED"), resulting_hu=F("hW", "DERIVED"))
    g.edge("t", "via", "x"); body(g, "C"); p = mat(g, "c", None, "hW", "C"); g.edge(p, "copies_from", "mW"); g.edge("t", "produced", p)
    g.prop("t", "autonomy_write", YES if own_governs else NO, "TRACE"); g.prop("t", "autonomy_exec", YES if own_share > 0.5 else NO, "TRACE")
    ch = copy.deepcopy(g); ch.field("t", "write_governing", ["mW" if own_share > 0.5 else "mP"], "DERIVED", source="execution_share majority")
    ch2 = copy.deepcopy(g); ch2.prop("t", "autonomous", YES, "DERIVED")
    return g, {}, {"write_governance_from_execution_share": (ch, "J8"), "bare_autonomy": (ch2, "J9")}


def v05_foreign_execution_own_writes(): return _exec_case(0.10, True)
def v06_local_execution_foreign_writes(): return _exec_case(0.90, False)


def v07_made_in_A_descended_from_B():
    g = G(); body(g, "B", loc="nicheB"); mat(g, "mB", "RANDOM_INIT", "hB", "B", made_in="nicheB"); body(g, "C", loc="nicheA")
    g.event("t", ["REPRODUCTION"], factual_contributors=F(["hB"], "TRACE", granularity="segment"), hu_continuity=F("hB", "DERIVED"), resulting_hu=F("hB", "DERIVED"))
    p = mat(g, "c", None, "hB", "C", made_in="nicheA"); g.edge(p, "copies_from", "mB"); g.edge("t", "produced", p)
    ch = copy.deepcopy(g); mat(ch, "mA", "RANDOM_INIT", "hA", None, made_in="nicheA"); ch.edge("c", "copies_from", "mA", basis="location")
    return g, {"resulting_hu": {"t": "hB"}}, {"niche_as_ancestry": (ch, "J16")}


def v08_transplant_made_in_A_now_in_C():
    g = G(); body(g, "D", loc="worldA"); mat(g, "mD", "RANDOM_INFLOW", "hD", "D", made_in="worldA")
    body(g, "T", loc="worldC"); g.node("operator", "BODY")
    g.event("tx", ["TRANSFER"], executor_body=F(NONE), factual_contributors=F(["hD"], "TRACE", granularity="segment"), hu_continuity=F("hD", "DERIVED"), resulting_hu=F("hD", "DERIVED"))
    p = mat(g, "mT", "TRANSPLANT", "hD", "T"); g.edge(p, "copies_from", "mD"); g.edge("tx", "produced", p)
    g.edge("operator", "transports", p, **{"from": "worldA", "to": "worldC"})
    ch = copy.deepcopy(g); _drop_edges(ch, "copies_from")
    return g, {"spontaneous": {"hD": NO}, "made_in_mD": ["worldA"]}, {"transplant_severed": (ch, "J5")}


def _npe_like(factual_share, suff, nec, name):
    g = G(); body(g, "V", "idV"); body(g, "D", "idD"); mat(g, "mD", "RANDOM_INIT", "hD", "D"); mat(g, "mV", "RANDOM_INIT", "hV", "V")
    cont = continuity({"hD": factual_share, "hV": round(1 - factual_share, 3)}, MAJ)
    fields = dict(executor_body=F("D", "TRACE"), host_body=F("V", "TRACE"),
                  factual_contributors=F(["hD", "hV"], "TRACE", granularity="segment", shares={"hD": factual_share, "hV": round(1 - factual_share, 3)}))
    g.event("t", ["REPRODUCTION", "HOSTING"], **fields)
    if cont["hu_continuity"] == ILL: g.field("t", "hu_continuity", ILL, "DERIVED", ill_posed=cont["ill_posed"])
    else: g.field("t", "hu_continuity", cont["hu_continuity"], "DERIVED")
    g.edge("t", "hosted_by", "V")
    p1 = mat(g, "c1", None, None, "V"); g.edge(p1, "copies_from", "mD"); p2 = mat(g, "c2", None, None, "V"); g.edge(p2, "copies_from", "mV")
    g.edge("t", "produced", p1); g.edge("t", "produced", p2)
    g.cf_test("cfS", "mD", "SUFFICIENCY", {"name": "randomize_victim", "draws": 3}, {"predicate": "rebuilt victim fidelity>=0.9"}, suff, on="t")
    g.cf_test("cfN", "mD", "NECESSITY", {"name": "block_donor_writes"}, {"predicate": "victim fidelity to donor>=0.9 fails"}, nec, on="t")
    ch = copy.deepcopy(g); ch.cf_test("cfX", "mD", "SUFFICIENCY", None, {"predicate": "x"}, YES, on="t")
    ch2 = copy.deepcopy(g); ch2.field("t", "factual_contributors", ["hD"], "REPLAY", "segment", source="counterfactual rebuild of a random victim")
    ch3 = copy.deepcopy(g); ch3.prop("t", "sufficient", YES, "REPLAY")
    return g, {"cf": {"cfS": suff, "cfN": nec}}, {"cf_without_intervention": (ch, "J11"), "factual_from_counterfactual": (ch2, "J10"),
                                                 "bare_sufficient": (ch3, "J9/J11")}


def v09_factual_contributor_fails_sufficiency(): return _npe_like(0.8, NO, YES, "v09")
def v10_low_contribution_counterfactually_sufficient(): return _npe_like(0.2, YES, NO, "v10")


def v11_host_scaffold_no_material():
    g = G(); body(g, "W", "idW"); body(g, "H", "idH"); mat(g, "mW", "RANDOM_INFLOW", "hW", "W"); mat(g, "mH", "RANDOM_INFLOW", "hH", "H")
    g.event("t", ["REPRODUCTION", "HOSTING"], executor_body=F("W", "TRACE"), host_body=F("H", "TRACE"),
            factual_contributors=F(["hW"], "TRACE", granularity="segment"), hu_continuity=F("hW", "DERIVED"), resulting_hu=F("hW", "DERIVED"))
    g.edge("t", "hosted_by", "H"); p = mat(g, "c", None, "hW", "H"); g.edge(p, "copies_from", "mW"); g.edge("t", "produced", p)
    g.cf_test("cfN", "H", "NECESSITY", {"name": "substitute_host_state", "with": "empty body"}, {"predicate": "birth occurs"}, YES, on="t")
    ch = copy.deepcopy(g); ch.field("t", "factual_contributors", ["hW", "hH"], "DERIVED", granularity="segment")
    return g, {"cf": {"cfN": YES}}, {"required_host_as_contributor": (ch, "J2/J3")}


def v12_no_singular_lineage_stable_architecture():
    g = G(); g.arch("archR", "behavioral", "identical output trace on the declared probe set", "the probe set exercises every reachable rule")
    for d in "ABC":
        body(g, "B" + d); mat(g, "m" + d, "RANDOM_INIT", "h" + d, "B" + d); g.edge("m" + d, "member_of_arch", "archR")
    shares = {"hA": 0.34, "hB": 0.33, "hC": 0.33}; c = continuity(shares, MAJ)
    g.event("t", ["RECOMBINATION"], factual_contributors=F(["hA", "hB", "hC"], "TRACE", granularity="segment", native_count=3, shares=shares),
            hu_continuity=F(ILL, "DERIVED", ill_posed=c["ill_posed"]), resulting_hu=F(ILL, "DERIVED", ill_posed=c["ill_posed"]), architecture_class=F("archR", "REPLAY"))
    body(g, "C")
    for d in "ABC":
        p = mat(g, "c" + d, None, None, "C"); g.edge(p, "copies_from", "m" + d); g.edge(p, "member_of_arch", "archR"); g.edge("t", "produced", p)
    g.event("tE", ["ESTABLISHMENT"], persisting_object=F("archR", "DERIVED"))
    ch = copy.deepcopy(g); ch.event("tE2", ["ESTABLISHMENT"])
    ch2 = copy.deepcopy(g); ch2.field("t", "resulting_hu", "archR", "DERIVED")
    return g, {"hu_continuity": {"t": ILL}, "architecture_class": {"t": "archR"}, "establishments": {"archR": "ARCH"}}, \
        {"establishment_without_object": (ch, "J13"), "arch_as_resulting_hu": (ch2, "J17")}


def v13_insufficient_evidence_not_ill_posed():
    g = G(); c = continuity({"hA": NI, "hB": 0.4}, MAJ)
    body(g, "BA"); body(g, "BB"); mat(g, "mA", "RANDOM_INIT", "hA", "BA"); mat(g, "mB", "RANDOM_INIT", "hB", "BB")
    g.event("t", ["UNCLASSIFIED"], hu_continuity=F(c["hu_continuity"], "DERIVED"), resulting_hu=F(NI, "DERIVED"))
    ch = copy.deepcopy(g); ch.field("t", "hu_continuity", ILL, "DERIVED", ill_posed={"rule": MAJ, "evidence": {"hA": NI, "hB": 0.4}, "why": "unknown"})
    ch2 = copy.deepcopy(g); ch2.field("t", "executor_body", ILL, "DERIVED", ill_posed={"rule": "x", "evidence": {"a": 1}})
    return g, {"hu_continuity": {"t": NI}}, {"ill_posed_as_soft_unknown": (ch, "J6"), "ill_posed_in_non_identity_field": (ch2, "J6")}


def v14_meaningless_concept_ill_posed():
    """a many-to-many transformation: two bodies' materials are pooled and re-split into three children in equal shares."""
    g = G(); shares = {"hA": 0.5, "hB": 0.5}; c = continuity(shares, MAJ)
    for d in "AB": body(g, "B" + d); mat(g, "m" + d, "RANDOM_INIT", "h" + d, "B" + d)
    for k in range(3):
        t = "t%d" % k; g.event(t, ["RECOMBINATION"], factual_contributors=F(["hA", "hB"], "TRACE", granularity="segment", native_count=2, shares=shares),
                                 hu_continuity=F(ILL, "DERIVED", ill_posed=c["ill_posed"]), resulting_hu=F(ILL, "DERIVED", ill_posed=c["ill_posed"]),
                                 architecture_class=F(NA, "DECLARED"))
        body(g, "K%d" % k)
        for d in "AB":
            p = mat(g, "k%d%s" % (k, d), None, None, "K%d" % k); g.edge(p, "copies_from", "m" + d); g.edge(t, "produced", p)
    ch = copy.deepcopy(g); ch.prop("t0", "is_offspring_of_A", ILL, "DERIVED")
    return g, {"hu_continuity": {"t0": ILL, "t1": ILL, "t2": ILL}}, {"ill_posed_as_boolean": (ch, "J6")}


def v15_parent_body_identity_diverge():
    """native parent label = identity P; the child's BODY is the old body of identity Q; material comes from R."""
    g = G(); body(g, "BP", "P"); body(g, "BQ", "Q"); body(g, "BR", "R"); mat(g, "mR", "RANDOM_INIT", "hR", "BR")
    g.node("N", "IDENTITY"); g.edge("N", "labelled_parent", "P")
    g.event("t", ["REPRODUCTION", "HOSTING", "IDENTITY_CHANGE"], executor_body=F("BP", "TRACE"), host_body=F("BQ", "TRACE"),
            factual_contributors=F(["hR"], "TRACE", granularity="segment"), hu_continuity=F("hR", "DERIVED"), resulting_hu=F("hR", "DERIVED"))
    g.edge("t", "consumes", "BQ"); g.edge("t", "produced", "BQ"); g.edge("t", "produced", "N"); g.edge("N", "assigned", "BQ"); g.edge("t", "hosted_by", "BQ")
    p = mat(g, "c", None, "hR", "BQ"); g.edge(p, "copies_from", "mR"); g.edge("t", "produced", p)
    ch = copy.deepcopy(g); ch.field("t", "factual_contributors", ["P"], "NATIVE_RECORD", "body", source="parent_id")
    return g, {"resulting_hu": {"t": "hR"}, "host_body": {"t": "BQ"}}, {"native_parent_as_contributor": (ch, "J2/J3")}


FIXTURES: Dict[str, Callable[[], Tuple[Graph, dict, dict]]] = {f.__name__: f for f in (
    v01_symmetric_recombination, v02_majority_recombination_60_40, v03_rearranged_self_copy, v04_body_renamed_after_overwrite,
    v05_foreign_execution_own_writes, v06_local_execution_foreign_writes, v07_made_in_A_descended_from_B, v08_transplant_made_in_A_now_in_C,
    v09_factual_contributor_fails_sufficiency, v10_low_contribution_counterfactually_sufficient, v11_host_scaffold_no_material,
    v12_no_singular_lineage_stable_architecture, v13_insufficient_evidence_not_ill_posed, v14_meaningless_concept_ill_posed,
    v15_parent_body_identity_diverge)}


def conform(g: Graph, expected: dict) -> list:
    a = facts(g); bad = []
    if a["violations"]: bad.append(("violations", a["violations"]))
    for k, want in expected.items():
        if k.startswith("made_in_"):
            got = g.made_in(k[len("made_in_"):])
            if got != want: bad.append((k, got, want))
            continue
        got = a[k]
        if isinstance(want, dict):
            for kk, w in want.items():
                if got.get(kk) != w: bad.append((k, kk, got.get(kk), w))
        elif got != want: bad.append((k, got, want))
    return bad
