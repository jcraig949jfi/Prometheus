"""Historical regression suite (directive item 7). Each case is a documented Prometheus attribution error, recorded as the EVENT SHAPE
the record established, with its source. `expect` is what attribution v0 must say. `old_labels` is the historical mistaken
reading, written as an aggregation label; the validator must REJECT the record once that label is added. If v0 accepts an old
label, it reproduces the old mistake and fails.

These are shape reconstructions from the cited records, not re-extractions of every historical event. The cross-engine assay
(assay.py) runs adapters over real preserved events.

Engine attributions are corrected where the directive's wording differs from the record:
- the recombination SPLICE credited to the donor is NPE's (Z80A-D05), not BEE's;
- BEE's recombination is the EXTERNAL crossover operator (a true mixed-parent channel);
- the "transplant" hazard is the Z80xAtlas seeded transplants (Archaeon's z80atlas campaign). NPE implants are a harness channel of
  the same class.
"""
from __future__ import annotations

from archaeon.attribution import schema as S
from archaeon.attribution.schema import seg
from archaeon.attribution.fixtures import base, perf, cap, mat


def L(label, value=None, rule="historical_ruler", convention=False):
    d = {"label": label, "rule": rule, "convention": convention}
    if value is not None: d["value"] = value
    return d


def _c(rec, expect, old_labels, source, engine):
    rec["engine"] = engine; rec["source"] = source
    return {"record": rec, "expect": expect, "old_labels": old_labels, "source": source}


CASES = {
    "npe_recombination_splice_credited_to_donor": _c(
        base("reg.npe.splice", "child", [perf("recombination_operator", "splice")], "recombination_operator",
             mat(seg(0, 58, entity="donor", src_lo=0, via="operator_log"), seg(58, 64, entity="recipient", src_lo=58, via="operator_log"), n=64),
             capability=[cap("exact_self_copy", False, method="replayed")]),
        {"class": "OPERATOR_RECOMBINATION", "reproduction": False},
        [L("self_reproduction"), L("SELF_COPY"), L("spontaneous_replicator")],
        "Z80A-D05: 94% of fake replicators were splice products credited to the donor (D_Z80_SYNTHESIS s2)", "NPE"),
    "bee_migration_copy": _c(
        base("reg.bee.migration", "child", [perf("migration", "POLLINATION")], "migration_copy",
             mat(seg(0, 64, entity="src_org", src_lo=0, via="harness_log"), n=64)),
        {"class": "MIGRATION_COPY", "reproduction": False},
        [L("self_reproduction"), L("SELF_COPY")],
        "BEE migration COPY under POLLINATION/RESERVOIR (0 -> 148/150 extinction when fixed; D_Z80_SYNTHESIS s2)", "BEE"),
    "z80atlas_seeded_transplant": _c(
        base("reg.z80a.transplant", "child", [perf("transplant", "seeder")], "transplant_insertion",
             mat(seg(0, 64, entity="seeded_specimen", src_lo=0, via="harness_log"), n=64)),
        {"class": "TRANSPLANT_INSERTION", "reproduction": False},
        [L("spontaneous_replicator"), L("SELF_COPY")],
        "Z80xAtlas 'spontaneous' flags were seeded transplants (project memory 2026-09-23; D_Z80_SYNTHESIS s2)", "Z80xAtlas"),
    "npe_p11_failing_overwrite": _c(
        base("reg.npe.p11fail", "victim_slot", [perf("organism_code", "donor"), perf("neighbour_organism", "partner", role="co_performer")],
             "executed_write", mat(seg(0, 40, entity="donor", src_lo=0), seg(40, 64, "new_computed"), n=64),
             dependence=[{"target": "carrier", "intervention": "P-11 C2: re-implant donor against a random victim", "outcome": "overwrite recurs",
                          "result": "ceases", "contrast": "actual victim", "n": 1}]),
        {"class": "SELF_CONSTRUCTED_WITH_HELP", "capability": None},
        [L("causal_reproduction"), L("reproduction")],
        "NPE predecessor-admitted births: only 6/34 are P-11 causal (W1; DEEP_BLOCK REPORT s4 item 5)", "NPE"),
    "low_entropy_painter": _c(
        base("reg.painter", "child", [perf("organism_code", "painter")], "executed_write", mat(seg(0, 64, "new_constant"), n=64),
             state={"resemblance": [{"reference": "painter", "ibs": 0.9, "units": "byte"}]},
             capability=[cap("exact_self_copy", False)]),
        {"class": "ORGANISM_WRITTEN_NEW_MATERIAL", "reproduction": False},
        [L("descends_from", "painter"), L("SELF_COPY"), L("reproduction")],
        "block-copy-free low-entropy writers passing fidelity-by-resemblance (BEE first_replication on junk; FF-4/FF-27)", "BEE"),
    "pte_ga_self_cross": _c(
        base("reg.pte.selfcross", "child", [perf("recombination_operator", "search.py crossover")], "recombination_operator",
             mat(seg(0, 32, entity="A", src_lo=0, via="operator_log"), seg(32, 64, entity="A", src_lo=32, via="operator_log"), n=64)),
        {"class": "OPERATOR_RECOMBINATION", "donors": 1, "reproduction": False},
        [L("recombinant"), L("mixed_parent")],
        "E-002: the 1/16 tie is a self-cross of a PTE genetic-algorithm crossover (a == b; A_E002_REVIEW.md:13; "
        "E-002/T-008_T-011_RESULTS.md:32-36). Corrected after Review 1 (R1-4), which found it had been encoded as an Archaeon "
        "organism's executed write", "PTE"),
    "bee_external_crossover_true_mixed": _c(
        base("reg.bee.xover", "child", [perf("recombination_operator", "EXTERNAL")], "recombination_operator",
             mat(seg(0, 30, entity="A", src_lo=0, via="operator_log"), seg(30, 64, entity="B", src_lo=30, via="operator_log"), n=64)),
        {"class": "OPERATOR_RECOMBINATION", "donors": 2, "reproduction": False},
        [L("parent_id", "A", rule="SINGULAR_MATERIAL_PARENT", convention=True), L("SELF_COPY")],
        "BEE EXTERNAL crossover: a true two-donor channel carried by the operator (W2_BEE_LENS)", "BEE"),
    "archaeon_organism_recombination": _c(
        base("reg.arch.recomb", "child", [perf("host_organism", "H")], "executed_write",
             mat(seg(0, 18, entity="H", src_lo=0), seg(18, 32, entity="N", src_lo=18)), capability=[cap("exact_self_copy", True)],
             native={"donor_capabilities": {"H": True, "N": True}}),
        {"class": "ORGANISM_RECOMBINATION_SELF_INCLUDED", "donors": 2, "reproduction": True},
        [L("parent_id", "H", rule="SINGULAR_MATERIAL_PARENT", convention=True)],
        "Archaeon +RECOMBINATION births (nE >= 4 and nN >= 4; lineage core); the parent chain names the executor only", "Archaeon"),
    "archaeon_parent_chain_is_executor": _c(
        base("reg.arch.hostexec", "child", [perf("host_organism", "H")], "executed_write", mat(seg(0, 32, entity="N", src_lo=0)),
             state={"resemblance": [{"reference": "N", "ibs": 1.0, "units": "byte"}]},
             capability=[cap("host_assisted_copy", True, {"neighbour": "host:H-class"})],
             native={"donor_capabilities": {"N": True}}),
        {"class": "HOST_WRITTEN", "reproduction": True},
        [L("parent_id", "H", rule="SINGULAR_MATERIAL_PARENT", convention=True), L("SELF_COPY"), L("descends_from", "H")],
        "Archaeon parent chain = executor label (ENVGATE line; FALSE_FRIENDS); 72% of block-15 hosting births are by material", "Archaeon"),
    "resemblance_lineage_without_descent": _c(
        base("reg.bee.glineage", "child", [perf("organism_code", "X")], "executed_write", mat(seg(0, 64, entity="X", src_lo=0), n=64),
             state={"resemblance": [{"reference": "L_founder", "ibs": 0.95, "units": "byte"}, {"reference": "X", "ibs": 1.0, "units": "byte"}]},
             capability=[cap("exact_self_copy", True)], native={"donor_capabilities": {"X": True}}),
        {"class": "SELF_CONSTRUCTED", "reproduction": True},
        [L("lineage_member", "L_founder"), L("descends_from", "L_founder")],
        "BEE glineage assigned by resemblance; material by resemblance (W2; FF-4/FF-27): IBS read as IBD", "BEE"),
}
