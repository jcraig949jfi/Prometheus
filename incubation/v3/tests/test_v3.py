"""Tests for the Lens Genesis substrate. Fast, deterministic."""
from __future__ import annotations

import ast
import os
import random
import sys

V3 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for sub in ("worlds", "representations", "learner", "controls"):
    sys.path.insert(0, os.path.join(V3, sub))

from families_v3 import BLOCK1, BLOCK2, make_domains          # noqa: E402
from lens import enumerate_lenses, enumeration_sha, lens_serial, \
    run_with_lens, run_program                                 # noqa: E402
from classify_v3 import classify                               # noqa: E402
import lens_learner as L                                       # noqa: E402

R2OP = ("STAGE", (("A", "S"), ("Z", "P")), ("IF", "FSIZE", "LE", "FSIZE"), "MEET")
TRUE = (tuple(sorted(BLOCK1)), tuple(sorted(BLOCK2)))


def test_domains_inverses_and_replay():
    rng = random.Random(1)
    for wid, d in make_domains().items():
        kw = {"n_blocks": 3} if wid == "vE" else {}
        if wid == "vD":
            kw["decoy_uses"] = 1
        task, omni = d.gen_task(rng, 4, **kw)
        assert d.run_word(omni["witness"], omni["s"]) == omni["t"]
        assert d.decode(task["start"]) == omni["s"]
        for pid in d.pids:
            nx = d.apply(pid, omni["s"])
            assert dict(d.pred(nx))[pid] == omni["s"], (wid, pid)


def test_enumeration_frozen():
    vA = make_domains()["vA"]
    lenses = enumerate_lenses(vA.pids)
    assert len(lenses) == 11050
    assert enumeration_sha(lenses) == "be25ed731e597b5e"


def test_true_lens_solves_and_word_verifies():
    vA = make_domains()["vA"]
    rng = random.Random(2)
    task, omni = vA.gen_task(rng, 7)
    r = run_with_lens(vA, task, TRUE, R2OP, 400_000)
    assert r["solved"] and r["ops"] < 5_000
    s = omni["s"]
    for pid in r["word"]:
        s = vA.apply(pid, s)
    assert s == omni["t"]


def test_overlapping_supports_rejected():
    vA = make_domains()["vA"]
    rng = random.Random(3)
    task, _ = vA.gen_task(rng, 3)
    bad = (tuple(sorted(BLOCK1)), tuple(sorted(("u02",))))     # decoy spans blocks
    r = run_with_lens(vA, task, bad, R2OP, 50_000)
    assert not r["solved"] and r["why"] == "support_overlap"


def test_classifier_rules():
    assert classify({"kind": "macro", "word": ["u00"]}) == "MACRO"
    assert classify(R2OP) == "OPERATOR"
    assert classify((tuple(sorted(BLOCK1)),)) == "ACTION_RESTRICTION"
    assert classify(TRUE) == "REPRESENTATIONAL"
    assert classify(TRUE, sub_halts=["meet", "noop"]) == "ACTION_RESTRICTION"
    assert classify(TRUE, sub_halts=["meet", "meet"]) == "REPRESENTATIONAL"


def test_trigger_thresholds():
    ok = [{"budget_exhausted": False}] * 10
    bad = [{"budget_exhausted": True}] * 4 + [{"budget_exhausted": False}] * 6
    assert not L.trigger_fired(ok)[0]
    assert L.trigger_fired(bad)[0]
    assert not L.trigger_fired(bad[:6])[0]


def test_extension_order_pins_exclusions():
    vE = make_domains()["vE"]
    prior_alphabet = set(BLOCK1 + BLOCK2) | {"u02", "u05"}
    order = L.extension_order(TRUE, prior_alphabet, vE.pids)
    for g in order:
        used = {p for grp in g for p in grp}
        assert "u02" not in used and "u05" not in used
        assert set(BLOCK1) <= used and set(BLOCK2) <= used


def test_routed_fallback_and_lens_paths():
    doms = make_domains()
    rng = random.Random(4)
    tA, _ = doms["vA"].gen_task(rng, 7)
    tD, _ = doms["vD"].gen_task(rng, 4, decoy_uses=1)
    cap = 4_000
    rA = L.run_routed(doms["vA"], tA, TRUE, cap, R2OP, 400_000)
    rD = L.run_routed(doms["vD"], tD, TRUE, cap, R2OP, 400_000)
    assert rA["solved"] and rA["routed_to"] == "lens"
    assert rD["solved"] and rD["routed_to"] == "fallback"


def test_learner_import_boundary():
    forbidden = {"BLOCK1", "BLOCK2", "BLOCK3", "TRUE_LENS", "DECOYS", "DECOY3"}
    for mod in ("learner/lens_learner.py", "representations/lens.py",
                "representations/classify_v3.py"):
        tree = ast.parse(open(os.path.join(V3, mod)).read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert not {n.name.split(".")[0]
                            for n in node.names} & {"families_v3"}, mod
            elif isinstance(node, ast.ImportFrom):
                assert (node.module or "").split(".")[0] != "families_v3", mod
            elif isinstance(node, ast.Name):
                assert node.id not in forbidden, (mod, node.id)
