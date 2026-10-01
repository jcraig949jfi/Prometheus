"""Controls for the alien-lawful generator and verifier: each check is shown
able to fire (positive / cheat controls), and the frozen dataset satisfies
its own ground-truth claims."""

import json
import os

import numpy as np
import pytest

from hecate.alien import generate as G
from hecate.alien import verify as V
from hecate.alien.systems import step

DATA = os.path.join(os.path.dirname(os.path.dirname(__file__)), "alien", "data")


def test_analogue_check_rejects_known_template_fed_as_alien():
    rng = np.random.RandomState(0)
    known = G.known_pool(rng)
    diff = next(k for k in known if k["kind"] == "diffusion")
    graph_known = [k for k in known if k["family"] == "graph"]
    ok, why = G.analogue_ok(diff, graph_known, V.table(diff))
    assert not ok and "agrees" in why


def test_analogue_check_rejects_affine_map():
    cat = {"family": "map", "kind": "cat"}
    ok, why = G.analogue_ok(cat, [], V.table(cat))
    assert not ok and why == "affine"


def test_property_checks_fire_both_ways():
    diff = {"family": "graph", "kind": "diffusion", "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]]}
    assert G.check_prop(diff, {"type": "conserved_linear", "w": [1] * 6, "mod": 1000})
    bfs = dict(diff, kind="bfs")
    assert not G.check_prop(bfs, {"type": "conserved_linear", "w": [1] * 6, "mod": 1000})
    assert G.check_prop({"family": "map", "kind": "cat"}, {"type": "bijective"})
    assert not G.check_prop({"family": "tab", "kind": "median3"}, {"type": "bijective"})


@pytest.fixture(scope="module")
def key():
    with open(os.path.join(DATA, "answer_key.json"), encoding="utf-8") as fh:
        return json.load(fh)


def test_counts(key):
    from collections import Counter
    c = Counter(v["class"] for v in key.values())
    assert c == {"KNOWN_LAWFUL": 20, "ALIEN_LAWFUL": 40, "MATCHED_NOISE": 40}
    assert set(Counter(v["family"] for v in key.values()).values()) == {20}


def test_every_alien_property_verifies_and_every_null_destroys_it(key):
    for sid, e in key.items():
        if e["class"] == "ALIEN_LAWFUL":
            assert e["verification_tests"] and all(t["result"] for t in e["verification_tests"]), sid
            null = key[e["matched_to"]]
            tbl = V.table(null["params"])
            prim = [pr for pr in e["planted"] if pr.get("primary", True)]
            assert not any(G.check_prop(null["params"], pr, tbl) for pr in prim), sid


def test_answers_match_simulator(key):
    for sid, e in list(key.items())[::7]:
        a = e["answers"]
        for s, nxt in zip(a["q2_states"], a["t2"]):
            assert list(step(e["params"], tuple(s))) == nxt, sid


def test_public_file_leaks_no_class_information():
    with open(os.path.join(DATA, "public.json"), encoding="utf-8") as fh:
        txt = fh.read().lower()
    for word in ("alien", "known", "noise", "scramble", "destroy", "seductive", "lawful",
                 "planted", "generator", "diffusion", "odometer", "linmix", "null"):
        assert word not in txt, word


def test_claim_scorer_each_status_fires():
    from hecate.alien.score import score_claims
    diff = {"family": "graph", "kind": "diffusion", "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]]}
    obj = {"t4": {"claims": [
        {"kind": "conserved", "expr": "sum(s)"},                 # TRUE for diffusion
        {"kind": "conserved", "expr": "s[0]"},                   # FALSE
        {"kind": "conserved", "expr": "len(s)"},                 # TRIVIAL (constant)
        {"kind": "conserved", "expr": "s.__class__"},            # UNTESTABLE (sandbox rejects)
        {"kind": "other", "prose": "looks smooth"}]}}             # UNTESTABLE
    planted = [{"type": "conserved_linear", "w": [1] * 6, "mod": 1000}]
    res, cap = score_claims(diff, obj, planted, {})
    assert [r["status"] for r in res] == ["TRUE", "FALSE", "TRIVIAL", "UNTESTABLE", "UNTESTABLE"]
    assert list(cap.values()) == [True]


def test_code_scorer_rewards_true_rule_and_not_identity():
    from hecate.alien.score import score_code
    from hecate.alien.systems import step
    p = {"family": "map", "kind": "rot90"}
    ev = [[i, (3 * i) % 31] for i in range(40)]
    ans = {"eval_states": ev, "eval_next": [list(step(p, tuple(s))) for s in ev], "t3_spec": [], "t3": []}
    good = score_code(p, "def step(s):\n    return [(-s[1]) % 31, s[0]]\n", ans, {})
    bad = score_code(p, "def step(s):\n    return list(s)\n", ans, {})
    assert good["eval_exact"] == 1.0 and bad["eval_exact"] < 0.1
