"""Known-answer fixtures for attribution v0.

TH014_LEAK       six histories that end in the SAME 32 child bytes (harness copy, world migration, recombination operator inserting
                 most of it, host write, neighbour write, genuine self-construction). Required answer: six different production classes.
                 Future reproduction instruments must pass this (see ATTRIBUTION_V0.md s5).
ADVERSARIAL      the directive's reproduction cases plus three of ours (harness copy, IBS without IBD, one producer / two donors). Each
                 carries the INTENDED verdict and why; classify.DEFINITIONS are scored against them.
STRUCTURE        representational stress cases from directive item 2 (two material parents, one producer two donors, host execution with
                 neighbour material, harness copy, recombination, no singular producer, IBS without IBD, IBD with changed state).
These are SYNTHETIC. Historical instances are in regression.py.
"""
from __future__ import annotations

from archaeon.attribution import schema as S
from archaeon.attribution.schema import seg

G = 32
CHILD = bytes.fromhex("22592835581410fdf68ad092291919141850517b75b24d827228a45916f9863e")   # any fixed 32 bytes; the same child throughout


def perf(kind, pid, role="performer"):
    return {"kind": kind, "id": pid, "role": role}


MACH = [3, 4, 5, 6, 12]          # the knockout-essential loci of the block-13 founder (TH-013), reused as a plausible machinery set


def cap(capability, result, conditions=None, method="executed", ruler="isolated_vm_copy_v0", machinery=None):
    """machinery = the child's own loci whose knockout removes this capability (empty for host-assisted: the machinery is not local)."""
    c = {"capability": capability, "result": result, "conditions": conditions or {"neighbour": "zero"}, "method": method, "ruler": ruler}
    if result and capability not in ("none_demonstrated",): c["machinery_loci"] = list(MACH if machinery is None else machinery)
    return c


def mat(*segs, n=G):
    return {"unit": "byte", "n_units": n, "resolution": "per_locus", "segments": list(segs)}


def knockouts(loci, subject=None):
    """knockout dependence entries backing a machinery claim (A17). In fixtures these are AUTHORED, not executed (Review 1 R1-3);
    real adapters must produce them by execution (th015_archaeon.machinery)."""
    out = []
    for p in loci:
        d = {"target": "machinery", "locus": p, "intervention": "knockout: locus %d set to 0x00" % p, "outcome": "the copy capability",
             "result": "ceases", "contrast": "unmodified child", "n": 1}
        if subject: d["subject"] = subject
        out.append(d)
    return out


def base(eid, subject, performers, process, material, **kw):
    """donor capability moves from native['donor_capabilities'] (a free field, Review 1 CX-3c) into executed capability claims
    ABOUT the donor; machinery claims get knockout dependence entries."""
    nat = dict(kw.pop("native", None) or {}); dcaps = nat.pop("donor_capabilities", {})
    caps = list(kw.pop("capability", None) or []); dep = list(kw.pop("dependence", None) or [])
    ents = {s_["entity"] for s_ in material["segments"] if s_.get("source_kind") == "entity"}
    for ent, ok in dcaps.items():
        if ent in ents:
            caps.append({"capability": "exact_self_copy", "result": bool(ok), "subject": ent, "conditions": {"neighbour": "zero"},
                         "method": "executed", "ruler": "isolated_vm_copy_v0"})
    for c in caps:
        if c.get("machinery_loci") and "subject" not in c: dep += knockouts(c["machinery_loci"])
    kw["native"] = nat; kw["capability"] = caps; kw["dependence"] = dep
    kw.setdefault("contrast", {"baseline": "shares of the child's %d byte loci" % G, "kind": "reference_entity"})
    kw.setdefault("state", {"resemblance": [{"reference": "P", "ibs": 1.0, "units": "byte"}]})
    return S.record(eid, "synthetic", subject, carrier={"performers": performers, "exec_where": S.NI, "exec_what": S.NI},
                    production={"process": process, "evidence": "fixture"}, material=material, **kw)


# ------------------------------------------------------------------ TH-014: same bytes, different history
TH014_LEAK = {
    "HARNESS_COPY": base("th014.harness", "C", [perf("harness", "harness")], "harness_copy", mat(seg(0, 32, entity="P", src_lo=0, via="harness_log"))),
    "MIGRATION_COPY": base("th014.migration", "C", [perf("migration", "migrate")], "migration_copy",
                           mat(seg(0, 32, entity="P", src_lo=0, via="harness_log"))),
    "OPERATOR_RECOMBINATION": base("th014.recomb", "C", [perf("recombination_operator", "xover")], "recombination_operator",
                                   mat(seg(0, 28, entity="P", src_lo=0, via="operator_log"), seg(28, 32, entity="Q", src_lo=28, via="operator_log"))),
    "HOST_WRITTEN": base("th014.host", "C", [perf("host_organism", "H")], "executed_write", mat(seg(0, 32, entity="P", src_lo=0, via="taint"))),
    "NEIGHBOUR_WRITTEN": base("th014.nbr", "C", [perf("neighbour_organism", "N")], "executed_write",
                              mat(seg(0, 32, entity="P", src_lo=0, via="taint"))),
    "SELF_CONSTRUCTED": base("th014.self", "C", [perf("organism_code", "P")], "executed_write", mat(seg(0, 32, entity="P", src_lo=0, via="taint"))),
}
TH014_CHILD_BYTES = {k: CHILD for k in TH014_LEAK}                     # identical by construction: the point of the fixture


def th014_leaky_variants():
    """the historical mistake, per channel: an infrastructure copy credited to the organism. The validator must reject each one."""
    out = {}
    for k in ("HARNESS_COPY", "MIGRATION_COPY", "OPERATOR_RECOMBINATION"):
        r = S.record(**{kk: vv for kk, vv in TH014_LEAK[k].items() if kk not in ("schema",)})
        r["aggregation"] = [{"label": "SELF_COPY", "rule": "native_flag", "convention": False}]
        out[k + "+SELF_LABEL"] = r
        r2 = S.record(**{kk: vv for kk, vv in TH014_LEAK[k].items() if kk not in ("schema",)})
        r2["carrier"] = {"performers": [perf("organism_code", "P")], "exec_where": S.NI, "exec_what": S.NI}
        out[k + "+ORGANISM_CARRIER"] = r2
        # Review 1 CX-2a/2b: the realistic leak -- process AND carrier both mis-logged as the organism's executed write, while the
        # material provenance still comes from the infrastructure log. A16 must catch it.
        r3 = S.record(**{kk: vv for kk, vv in TH014_LEAK[k].items() if kk not in ("schema",)})
        r3["carrier"] = {"performers": [perf("organism_code", "P")], "exec_where": S.NI, "exec_what": S.NI}
        r3["production"] = {"process": "executed_write", "evidence": "engine log (mis-logged)"}
        r3["aggregation"] = [{"label": "SELF_COPY", "rule": "native_flag", "convention": False}]
        out[k + "+MISLOGGED_CHANNEL"] = r3
    return out


# ------------------------------------------------------------------ adversarial reproduction cases (directive item 3 + ours)
def _adv(eid, performers, process, material, caps, intended, why, resemblance=None, dependence=None, native=None, origin="directive"):
    """origin: 'directive' (the operator's item-3 list), 'archaeon' (added by the author), 'artemis', 'review1' (added from Review 1's
    counter-examples). The verdicts are AUTHORED; Review 1 showed that which definition 'wins' depends on which cases are included."""
    r = base(eid, "C", performers, process, material, capability=caps, dependence=dependence or [],
             state={"resemblance": resemblance if resemblance is not None else [{"reference": "P", "ibs": 1.0, "units": "byte"}]},
             native=dict({"donor_capabilities": {"P": True, "N": True, "A": True, "B": True}}, **(native or {})))
    return {"record": r, "intended": intended, "why": why, "origin": origin}


VARIANT_OK = {"target": "material", "intervention": "variant: flip a non-machinery byte in the donor before copying",
              "outcome": "child carries the variant AND still copies", "result": "persists", "contrast": "unmodified donor", "n": 32}
VARIANT_DEAD = dict(VARIANT_OK, result="ceases", outcome="child carries the variant AND still copies (every variant loses copying)")

ADVERSARIAL = {
    "self_painting_homopolymer": _adv(
        "adv.selfpaint", [perf("organism_code", "P")], "executed_write",
        {"unit": "byte", "n_units": G, "resolution": "per_locus",
         "segments": [dict(seg(i, i + 1, entity="P", via="taint"), src_loci=[1, 2]) for i in range(G)]},
        [cap("exact_self_copy", True, machinery=[0, 1])], {"reproduction": True, "hereditary": False},
        "Artemis FR-011's NPE BYTEWISE case: a 0x36 homopolymer paints memory with its own operand byte; every child locus is IBD "
        "from ONE parent locus. It reproduces (the capability and its machinery descend), but transmits about one byte and no "
        "heritable variant survives. P-11 cannot tell it from copying; source_diversity (1/32 vs 1.0) can",
        dependence=[VARIANT_DEAD], origin="artemis"),
    "homopolymer_painter": _adv(
        "adv.painter", [perf("organism_code", "P")], "executed_write", mat(seg(0, 32, "new_constant", via="taint")),
        [cap("none_demonstrated", True), cap("exact_self_copy", False)], {"reproduction": False, "hereditary": False},
        "writes a constant fill; the child resembles every other painted cell but carries none of P's material and cannot paint",
        resemblance=[{"reference": "Q_painted", "ibs": 1.0, "units": "byte"}]),
    "exact_copier_no_heritable_variation": _adv(
        "adv.exact_noher", [perf("organism_code", "P")], "executed_write", mat(seg(0, 32, entity="P", src_lo=0)),
        [cap("exact_self_copy", True)], {"reproduction": True, "hereditary": False},
        "replication with capacity transmission, but no variant survives in a capable child: not Darwinian reproduction",
        dependence=[VARIANT_DEAD]),
    "cargo_without_capacity": _adv(
        "adv.cargo", [perf("organism_code", "P")], "executed_write", mat(seg(0, 20, entity="P", src_lo=12), seg(20, 32, "new_computed")),
        [cap("exact_self_copy", False), cap("approximate_self_copy", False)], {"reproduction": False, "hereditary": False},
        "P's cargo lands in the child but the machinery does not: material transmission without capacity",
        resemblance=[{"reference": "P", "ibs": 0.3, "units": "byte"}]),
    "machinery_without_founder_bytes": _adv(
        "adv.nofounder", [perf("organism_code", "P49")], "executed_write", mat(seg(0, 32, entity="P49", src_lo=0)),
        [cap("exact_self_copy", True)], {"reproduction": True, "hereditary": True},
        "generation 50 of a lineage whose founder bytes are all gone; each event still transmits material and capacity from the "
        "immediate donor. Founder-material rulers call this non-reproduction.",
        resemblance=[{"reference": "P49", "ibs": 1.0, "units": "byte"}, {"reference": "F0_founder", "ibs": 0.25, "units": "byte"}],
        dependence=[VARIANT_OK], native={"founder_share": 0.0, "donor_capabilities": {"P49": True}}),
    "scaffolded_copier": _adv(
        "adv.scaffold", [perf("organism_code", "P")], "executed_write", mat(seg(0, 32, entity="P", src_lo=0)),
        [cap("exact_self_copy", False), cap("scaffold_dependent_copy", True, {"neighbour": "zero", "scaffold": "input byte 128 present"})],
        {"reproduction": True, "hereditary": True, "qualifier": "SCAFFOLDED"},
        "copies only when the environment supplies input 128; reproduction, qualified by the scaffold", dependence=[VARIANT_OK]),
    "host_executed_copier": _adv(
        "adv.host", [perf("host_organism", "H")], "executed_write", mat(seg(0, 32, entity="N", src_lo=0)),
        [cap("exact_self_copy", False), cap("host_assisted_copy", True, {"neighbour": "host:H-class"})],
        {"reproduction": True, "hereditary": True, "qualifier": "HOST_ASSISTED"},
        "Tierra parasite: H's code copies N's material; N reproduces through H, not by itself. N HAS local machinery (its template "
        "/ jump loci: knocking them out removes host-assisted copying) -- corrected after Review 1, which showed machinery=[] is "
        "wrong about Tierra",
        resemblance=[{"reference": "N", "ibs": 1.0, "units": "byte"}], dependence=[VARIANT_OK]),
    "recombined_offspring": _adv(
        "adv.recomb", [perf("organism_code", "A")], "executed_write", mat(seg(0, 16, entity="A", src_lo=0), seg(16, 32, entity="B", src_lo=16)),
        [cap("exact_self_copy", True)], {"reproduction": True, "hereditary": True},
        "two material parents, both capable; the child copies. No singular parent exists",
        resemblance=[{"reference": "A", "ibs": 0.6, "units": "byte"}, {"reference": "B", "ibs": 0.55, "units": "byte"}], dependence=[VARIANT_OK]),
    "changed_encoding_conserved_function": _adv(
        "adv.recode", [perf("organism_code", "P")], "executed_write",
        mat(seg(0, 19, entity="P", src_lo=0), seg(19, 32, "new_mutation")), [cap("exact_self_copy", True)],
        {"reproduction": True, "hereditary": True},
        "13 of 32 bytes changed at neutral sites; function conserved. Byte-identity rulers call this non-reproduction",
        resemblance=[{"reference": "P", "ibs": 0.59, "units": "byte"}], dependence=[VARIANT_OK]),
    "trace_material_constructed_copier": _adv(
        "adv.trace", [perf("organism_code", "P")], "executed_write", mat(seg(0, 1, entity="P", src_lo=0), seg(1, 32, "new_computed")),
        [cap("exact_self_copy", True)], {"reproduction": False, "hereditary": False},
        "P computes a working copier that shares one byte of P's material; the machinery is newly built, not inherited. Any rule "
        "'material flow > 0 plus a capable child' calls this P's reproduction",
        resemblance=[{"reference": "P", "ibs": 0.1, "units": "byte"}]),
    "machinery_synonymous_mutation": _adv(
        "adv.synmach", [perf("organism_code", "P")], "executed_write",
        mat(seg(0, 4, entity="P", src_lo=0), seg(4, 5, "new_mutation"), seg(5, 32, entity="P", src_lo=5)), [cap("exact_self_copy", True)],
        {"reproduction": True, "hereditary": True},
        "one of the five machinery loci mutated to a synonymous byte; function conserved. A rule demanding every machinery byte "
        "descend calls this non-reproduction", resemblance=[{"reference": "P", "ibs": 0.97, "units": "byte"}], dependence=[VARIANT_OK]),
    "harness_copy": _adv(
        "adv.harness", [perf("harness", "harness")], "harness_copy", mat(seg(0, 32, entity="P", src_lo=0, via="harness_log")),
        [cap("exact_self_copy", True)], {"reproduction": False, "hereditary": False},
        "the harness copied P; the child can copy, but this EVENT is not P reproducing"),
    "ibs_without_ibd": _adv(
        "adv.ibs", [perf("organism_code", "Z")], "executed_write", mat(seg(0, 32, "new_input", via="taint")),
        [cap("exact_self_copy", True)], {"reproduction": False, "hereditary": False},
        "an unrelated writer produces bytes identical to P from its inputs; the child copies, but nothing descends from P",
        native={"donor_capabilities": {}}),
}


for _k in ("trace_material_constructed_copier", "machinery_synonymous_mutation", "harness_copy", "ibs_without_ibd"):
    ADVERSARIAL[_k]["origin"] = "archaeon"

VARIANT_DESC = dict(VARIANT_OK, intervention="variant: flip a description byte in the donor before copying")
# Review 1 counter-examples, adopted as cases (their verdicts are the reviewer's, argued in REVIEW_1.md)
ADVERSARIAL["universal_copier_junk"] = _adv(
    "adv.junk", [perf("host_organism", "H")], "executed_write", mat(seg(0, 32, entity="J", src_lo=0)),
    [cap("host_assisted_copy", True, {"neighbour": "host:H-class"}, machinery=[])], {"reproduction": False, "hereditary": False},
    "Review 1 CX-3a: a host with a universal copier copies inert junk J (J cannot copy, no locus of J matters). Pure cargo moved "
    "under a host; not reproduction of J", resemblance=[{"reference": "J", "ibs": 1.0, "units": "byte"}],
    native={"donor_capabilities": {"J": False}}, origin="review1")
ADVERSARIAL["von_neumann_constructor_description"] = _adv(
    "adv.vn", [perf("organism_code", "P")], "executed_write", mat(seg(0, 16, "new_computed"), seg(16, 32, entity="P", src_lo=16)),
    [cap("exact_self_copy", True)], {"reproduction": True, "hereditary": True},
    "Review 1 CX-3b: von Neumann's architecture. The description [16,32) is copied from P; the constructor [0,16), where the copy "
    "machinery sits, is BUILT from the description. The canonical self-reproducing automaton; machinery transmits as information, "
    "not as material", resemblance=[{"reference": "P", "ibs": 1.0, "units": "byte"}], dependence=[VARIANT_DESC], origin="review1")


# ------------------------------------------------------------------ directive item 2: structures the record must hold
STRUCTURE = {
    "two_material_parents": ADVERSARIAL["recombined_offspring"]["record"],
    "one_producer_two_donors": base("st.1p2d", "C", [perf("host_organism", "H")], "executed_write",
                                    mat(seg(0, 20, entity="N1", src_lo=0), seg(20, 32, entity="N2", src_lo=20))),
    "host_execution_neighbour_material": ADVERSARIAL["host_executed_copier"]["record"],
    "harness_copy": TH014_LEAK["HARNESS_COPY"],
    "recombination": TH014_LEAK["OPERATOR_RECOMBINATION"],
    "no_singular_producer": base("st.coexec", "C", [perf("organism_code", "A"), perf("organism_code", "B")], "executed_write",
                                 mat(seg(0, 32, entity="A", src_lo=0))),
    "ibs_without_ibd": ADVERSARIAL["ibs_without_ibd"]["record"],
    "ibd_with_changed_state": ADVERSARIAL["changed_encoding_conserved_function"]["record"],
}
