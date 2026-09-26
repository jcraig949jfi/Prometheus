"""PORTABILITY-01 s5: the synthetic conformance corpus. Honest fixtures conform; every cheat is caught by the invariant it violates."""
from __future__ import annotations

import copy
import json

import pytest

from archaeon.causal_lens import corpus as C
from archaeon.causal_lens.schema import Graph


@pytest.mark.parametrize("name", sorted(C.FIXTURES))
def test_fixture_conforms(name):
    g, exp, _ = C.FIXTURES[name]()
    assert C.conform(g, exp) == []


@pytest.mark.parametrize("name,cheat", [(n, c) for n in sorted(C.FIXTURES) for c in C.FIXTURES[n]()[2]])
def test_cheat_is_caught(name, cheat):
    g, want = C.FIXTURES[name]()[2][cheat]
    v = g.check()
    assert any(x.startswith(want) for x in v), (cheat, v)


def test_i11_parent_labels_never_change_heredity():
    g, exp, _ = C.f09_takeover_many_labels_one_architecture()
    a = C.answer(g)
    h = copy.deepcopy(g); h.edges = [e for e in h.edges if e[1] != "labelled_parent"]
    h._out.clear(); h._in.clear()
    for s, r, t, at in h.edges: h._out[(s, r)].append(t); h._in[(t, r)].append(s)
    b = C.answer(h)
    assert a["contributors"] == b["contributors"] and a["establishments"] == b["establishments"] == ["hR"]


def test_json_roundtrip_preserves_answers():
    for name, f in C.FIXTURES.items():
        g, exp, _ = f()
        h = Graph.from_json(json.loads(json.dumps(g.to_json())))
        assert C.answer(h) == C.answer(g), name
