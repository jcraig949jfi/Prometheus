"""PORTABILITY-01 Target A: the canonical graph built from Archaeon's native records must preserve the ENVGATE distinctions."""
from __future__ import annotations

from archaeon.causal_lens import fossils_archaeon as F
from archaeon.causal_lens.schema import spontaneous, NONE


def _events(g):
    return [t for t in g.of_kind("TRANSFORMATION") if "ESTABLISHMENT" not in g.nodes[t]["types"]]


def test_a1_autonomous_copier_is_its_own_ancestor_and_unhosted():
    w, _ = F.a1_autonomous(); g = F.graph_of(w, "A1")
    assert g.check() == []
    (t,) = _events(g); f = g.nodes[t]["fields"]
    assert g.nodes[t]["types"] == ["REPRODUCTION"] and f["host"]["value"] == NONE
    assert g.contributors_hu(t) == {f["resulting_hu"]["value"]} and spontaneous(g, f["resulting_hu"]["value"]) == "YES"


def test_a2_inserted_ancestry_survives_hosting_by_a_random_executor():
    w, nat = F.a2_inserted(); g = F.graph_of(w, "A2")
    assert g.check() == []
    (t,) = _events(g); f = g.nodes[t]["fields"]
    res = f["resulting_hu"]["value"]
    assert res == "glin:%d" % nat["resident_glin"] and spontaneous(g, res) == "NO"          # I1
    ex_hu = "glin:%d" % w.glin[0]
    assert ex_hu not in g.contributors_hu(t) and f["host"]["value"] != NONE                 # I2/I3
    assert {"AMPLIFICATION", "HOSTING"} <= set(g.nodes[t]["types"])                        # I9: not an origination


def test_a3_block15_many_host_labels_one_heritable_unit():
    w, nat = F.a3_block15_panel(); g = F.graph_of(w, "A3")
    assert g.check() == []
    ts = _events(g); resident = "glin:%d" % nat["resident_glin"]
    assert len(ts) == nat["hosting_births"] >= 10
    assert all(g.contributors_hu(t) == {resident} for t in ts)                              # one genetic architecture
    labels = {e[2] for e in g.edges if e[1] == "labelled_parent"}
    assert len(labels) == len(ts)                                                           # ...under n native parent labels
    hosts = {g.nodes[t]["fields"]["host"]["value"] for t in ts}
    assert len(hosts) == len(ts) and not any(g.hu_of(m) == resident for h in hosts for m in g.out(h, "owns"))
