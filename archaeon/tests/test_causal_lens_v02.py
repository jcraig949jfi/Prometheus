"""Contract v0.2 conformance: 15 attack fixtures conform; every prohibited inference is rejected by the invariant it violates."""
from __future__ import annotations

import json

import pytest

from archaeon.causal_lens import corpus_v02 as C
from archaeon.causal_lens.schema_v02 import Graph, continuity, ILL, NI, NONE


@pytest.mark.parametrize("name", sorted(C.FIXTURES))
def test_fixture_conforms(name):
    g, exp, _ = C.FIXTURES[name]()
    assert C.conform(g, exp) == []


@pytest.mark.parametrize("name,cheat", [(n, c) for n in sorted(C.FIXTURES) for c in C.FIXTURES[n]()[2]])
def test_prohibited_inference_rejected(name, cheat):
    g, want = C.FIXTURES[name]()[2][cheat]
    v = g.check()
    assert any(x.startswith(want) for x in v), (cheat, v)


def test_continuity_rule_semantics():
    M = C.MAJ
    assert continuity({"a": 0.5, "b": 0.5}, M)["hu_continuity"] == ILL                 # symmetric
    assert continuity({"a": 0.6, "b": 0.4}, M)["hu_continuity"] == "a"                 # declared majority
    assert continuity({"a": 0.34, "b": 0.33, "c": 0.33}, M)["hu_continuity"] == ILL    # many-to-many, no majority
    assert continuity({"a": NI, "b": 0.4}, M)["hu_continuity"] == NI                   # incomplete evidence that could matter: never ILL_POSED
    assert continuity({"a": NI, "b": 0.6}, M)["hu_continuity"] == "b"                  # v0.2.1: a strict known majority is decided
    assert continuity({"a": NI, "b": 0.5}, M)["hu_continuity"] == NI                   # 0.5 known + 0.5 unknown could be a tie
    assert continuity({"a": 0.3, "b": 0.3}, dict(M, no_majority="ORIGINATE"))["hu_continuity"] == NONE
    assert continuity({}, M)["hu_continuity"] == NONE


def test_json_roundtrip():
    for name, f in C.FIXTURES.items():
        g, _, _ = f()
        h = Graph.from_json(json.loads(json.dumps(g.to_json())))
        assert C.facts(h) == C.facts(g), name


def test_upgrader_on_every_v01_fixture_is_valid_and_lossless():
    from archaeon.causal_lens import corpus as C1
    from archaeon.causal_lens.upgrade_v01 import upgrade
    for name, f in C1.FIXTURES.items():
        g1, exp, cheats = f()
        g2, rep = upgrade(g1)
        assert g2.check() == [], (name, g2.check())
        assert g2.establishments().keys() == set(g1.establishments()), name
        for t in g1.of_kind("TRANSFORMATION"):
            assert g2.nodes[t]["v01"] == g1.nodes[t]["fields"]                      # the v0.1 claim is preserved verbatim
            assert g2.contributors_hu(t) == g1.contributors_hu(t), (name, t)         # heredity edges survive unchanged
        for c, (cg, want) in cheats.items():                                          # every v0.1 cheat is still rejected once upgraded
            assert upgrade(cg)[0].check(), (name, c)
