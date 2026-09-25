"""PROTEUS-46 verdict file -- the committed numbers recompute under the preregistered rule; a reduced-K
rerun reproduces the committed classes for its seeds; the file carries the three-way semantics."""
from __future__ import annotations

import json

from proteus.foundry.identity import hash_obj
from proteus.foundry.prng import SplitMix64, seed_from
from proteus.round2 import falsifier_46 as F


def test_committed_verdict_recomputes_from_committed_numbers():
    doc = json.load(open(F.OUT_JSON, encoding="utf-8"))
    v, rule = F.verdict(doc["neighbourhood"])
    assert v == doc["verdict"] and rule == doc["rule_evaluation"]
    assert doc["falsifier_status"] == {"CLIFF_DOES_NOT_SURVIVE": "PASSED", "CLIFF_SURVIVES": "FALSIFIER_FAILED", "INDETERMINATE": "INDETERMINATE"}[v]
    assert doc["neighbourhood_exhausted"] is False and len(doc["reopen_conditions"]) == 4
    assert doc["departures"] == []


def test_first_children_reproduce_for_every_operator():
    doc = json.load(open(F.OUT_JSON, encoding="utf-8"))
    for sub in ("v0", "graph"):
        S = F.SUBSTRATES[sub]
        parent = S["parents"]["one_value"]
        p_two, _p_all, p_out = F.score(sub, parent)
        assert p_two == doc["neighbourhood"][sub]["one_value"]["parent_two_key"] == 3
        for op in S["operators"]:
            # the committed per-operator counts are a superset of what these 20 seeds produce
            counts = {}
            for i in range(20):
                child = S["mutate"](parent, SplitMix64(seed_from("p46", sub, "one_value", op, i)), op)
                if hash_obj(child) == hash_obj(parent):
                    continue
                two, _a, out = F.score(sub, child)
                cls = F.classify(p_two, two, out == p_out)
                counts[cls] = counts.get(cls, 0) + 1
            committed = doc["neighbourhood"][sub]["one_value"]["per_operator_counts"][op]
            for cls, n in counts.items():
                assert committed.get(cls, 0) >= n, (sub, op, cls)


def test_classifier_semantics():
    assert F.classify(3, 4, False) == "USEFUL" and F.classify(3, 3, True) == "NEUTRAL"
    assert F.classify(3, 3, False) == "NEUTRAL_DIFF" and F.classify(3, 0, False) == "DESTROYED"
    assert F.classify(3, 2, False) == "GRADED_DOWN"
