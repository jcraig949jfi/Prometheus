"""H5 alpha producer side and producer cost receipts (design v0.1 §5 H5, C4)."""
from __future__ import annotations

import pytest

from archaeon.producer import h5_decoders as H
from archaeon.producer import costs as C


# ---------------------------------------------------------------- H5 decoders
def test_all_three_decoders_are_total_with_exactly_16_per_rule():
    for dec in (H.direct, H.make_balanced(7), H.make_scrambled(H.direct, 3),
                H.make_scrambled(H.make_balanced(7), 11)):
        facts = H.check_exact(dec)
        assert facts["rules_reached"] == 256 and facts["multiplicity"] == 16


def test_direct_is_the_low_eight_bits_and_balanced_differs_from_it():
    assert H.direct(0b1111_0000_1010) == 0b0000_1010
    bal = H.make_balanced(7)
    assert H.decoder_table(bal) != H.decoder_table(H.direct)
    # scrambling the RULE labels preserves the partition of genomes into
    # preimage classes exactly (it relabels classes, never regroups them)
    scr = H.make_scrambled(H.direct, 3)
    for r in (0, 90, 204, 255):
        pre = H.preimage(H.direct, r)
        assert H.preimage(scr, H.rule_permutation(3)[r]) == pre


def test_a_broken_decoder_is_refused_by_the_exact_check():
    with pytest.raises(ValueError, match="multiplicities"):
        H.check_exact(lambda g: (g & 0xFF) if g < 4000 else 0)
    with pytest.raises(ValueError, match="missing"):
        H.check_exact(lambda g: g & 0x7F)


def test_matched_start_and_single_bit_flip_are_seeded_and_replay():
    dec = H.make_balanced(1)
    g1 = H.sample_genotype_for_rule(dec, 90, seed=5)
    g2 = H.sample_genotype_for_rule(dec, 90, seed=5)
    assert g1 == g2 and dec(g1) == 90
    c1, b1 = H.flip_one_bit(g1, seed=9)
    c2, b2 = H.flip_one_bit(g1, seed=9)
    assert (c1, b1) == (c2, b2) and bin(c1 ^ g1).count("1") == 1
    prov = H.draw_provenance(dec, g1, c1, b1, 9)
    assert prov["rule"] == dec(c1) and prov["parent_rule"] == 90 and "genome" not in {"rule"}


def test_accessible_variation_is_measured_on_independent_parents():
    parents = H.independent_parents(seed=2, n=200)
    d = H.accessible_variation(H.direct, parents)
    b = H.accessible_variation(H.make_balanced(7), parents)
    # direct: flipping one of the 4 high bits never changes the rule, so at
    # most 8 distinct neighbour phenotypes; a balanced permutation can reach
    # up to 12. This is the ACCESS difference H5 is about, with the catalogue
    # and multiplicities identical (test above).
    assert d["mean_distinct_neighbour_phenotypes"] <= 8.0
    assert b["mean_distinct_neighbour_phenotypes"] > d["mean_distinct_neighbour_phenotypes"]
    assert d["parents"] == b["parents"] == 200 and d["se"] is not None


def test_equivalence_classes_collapse_the_count():
    parents = H.independent_parents(seed=3, n=50)
    ident = {r: r for r in range(256)}
    coarse = {r: r // 2 for r in range(256)}          # a stand-in for Herakles's 224 classes
    a = H.accessible_variation(H.direct, parents, ident)
    b = H.accessible_variation(H.direct, parents, coarse)
    assert b["mean_distinct_neighbour_phenotypes"] <= a["mean_distinct_neighbour_phenotypes"]
    assert b["collapsed_to_equivalence_classes"]


# ---------------------------------------------------------------- cost receipts
def test_resource_vector_rules():
    C.Resource("cpu_seconds", 1.5, "s", "process_time", "measured")
    with pytest.raises(ValueError, match="unavailable is not zero"):
        C.Resource("gpu_seconds", 0.0, "s", "-", "unavailable")
    with pytest.raises(ValueError, match="needs a quantity"):
        C.Resource("cpu_seconds", None, "s", "-", "measured")
    with pytest.raises(ValueError, match="measured in"):
        C.Resource("cpu_seconds", 1.0, "ms", "-", "measured")
    with pytest.raises(ValueError, match="stage"):
        C.CostEvent(stage="vibes", attempt_id="a", resources=[])


def test_meter_and_rollup_reference_children_and_never_sum_peak_memory():
    with C.Meter() as m:
        sum(range(10000))
    rs = m.resources([C.Resource("peak_memory_bytes", 1000, "bytes", "rss", "measured"),
                      C.Resource("items", 3, "count", "count", "measured")])
    e1 = C.CostEvent("retrieval", "att-1", rs)
    e2 = C.CostEvent("generation", "att-1", m.resources([C.Resource("peak_memory_bytes", 5000, "bytes", "rss", "measured")]))
    r = C.rollup("analysis", "att-1", [e1, e2])
    assert set(r.children) == {e1.cost_event_id, e2.cost_event_id}
    by = {x.resource: x for x in r.resources}
    assert "peak_memory_bytes" not in by                         # never summed
    assert by["gpu_seconds"].enforcement_class == "unavailable"  # stays unavailable
    assert by["items"].quantity == 3
    assert e1.cost_event_id != e2.cost_event_id


def test_counterfactual_attribution_charges_the_physical_cost_once():
    phys = C.CostEvent("generation", "src-build",
                       [C.Resource("cpu_seconds", 40.0, "s", "process_time", "measured"),
                        C.Resource("gpu_seconds", None, "s", "-", "unavailable")])
    arms = {arm: C.attribute_counterfactual(phys, arm, uses, reuse_horizon=4)
            for arm, uses in (("S00", False), ("S10", True), ("S01", False), ("S11", True))}
    assert arms["S00"]["attributed"]["cpu_seconds"] == 0.0
    assert arms["S10"]["attributed"]["cpu_seconds"] == 10.0
    assert arms["S11"]["attributed"]["gpu_seconds"] is None
    assert all(a["physical_cost_event_id"] == phys.cost_event_id for a in arms.values())
    with pytest.raises(ValueError):
        C.attribute_counterfactual(phys, "x", True, reuse_horizon=0)


def test_reconcile_names_the_missing_engine_side():
    p = [C.CostEvent("retrieval", "att-1", []), C.CostEvent("generation", "att-2", [])]
    r = C.reconcile(p, [{"attempt_id": "att-1"}, {"attempt_id": "att-9"}])
    assert r == {"matched": ["att-1"], "producer_only": ["att-2"], "executor_only": ["att-9"],
                 "engine_side": "absent (Daedalus C4-3)"}


def test_engine_projection_uses_only_the_engine_vocabulary_and_never_sends_enforcement_class():
    """Daedalus TRACKA-VECTOR-1: as emitted, the vector was refused three
    times (extra key, unknown method, unknown scope). The projection must be
    acceptable by construction."""
    with C.Meter() as m:
        pass
    ev = C.CostEvent("generation", "att-x", m.resources(
        [C.Resource("peak_memory_bytes", 1000, "bytes", "rss", "measured"),
         C.Resource("items", 3, "count", "count", "measured")]))
    entries = C.to_engine_entries(ev)
    assert entries and all("enforcement_class" not in e for e in entries)
    assert all(e["method"] in C.ENGINE_METHODS and e["scope"] in C.ENGINE_SCOPES for e in entries)
    by = {e["resource"]: e for e in entries}
    assert by["cpu_seconds"]["method"] == "clock" and by["peak_memory_bytes"]["method"] == "sampler"
    assert by["items"]["method"] == "counter" and by["gpu_seconds"]["method"] == "declared"
    assert by["gpu_seconds"]["quantity"] is None                       # unavailable is not zero
    assert by["cpu_seconds"]["refs"]["producer_method"].startswith("time.process_time")
    assert by["cpu_seconds"]["refs"]["producer_enforcement_class"] == "measured"
    roll = C.rollup("analysis", "att-x", [ev])
    assert all(e["method"] in ("derived", "declared") for e in C.to_engine_entries(roll))
    with pytest.raises(ValueError):
        C.to_engine_entries(ev, scope="producer")
    assert C.from_engine_response([{"resource": "cpu_seconds", "enforcement_class": "measured"}]) == {"cpu_seconds": "measured"}


def test_published_class_map_loads_and_collapses_the_exact_reference():
    from archaeon.producer import h5_reference as R
    cm = R.load_class_map()
    assert cm["n_classes"] == 224 and "8 steps" in cm["scope"] and "7-ring" in cm["scope"]
    eq = cm["equivalence"]
    assert eq[240] == eq[15] == eq[180] == eq[210] and eq[170] == eq[85] and eq[204] not in (eq[240], eq[170])
    direct = R.exact_reference(H.direct)
    collapsed = R.exact_reference(H.direct, equivalence=eq)
    assert collapsed["mean_reach"] <= direct["mean_reach"]
