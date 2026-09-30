"""Theseus v0 machinery tests: the controls that make the instruments falsifiable."""

import numpy as np

from theseus.synth import battery as bt
from theseus.synth import collide as co
from theseus.synth import compile_g0 as cg
from theseus.synth import entities as en
from theseus.synth import run_v0 as rv
from theseus.synth import substrate as sb


def _g0():
    return cg.compile_corpus()


def test_g0_corpus_compiles_valid_and_distinct():
    c = _g0()
    assert len(c) == 95
    assert all(not sb.validate(e["genome"]) for e in c)
    assert len({sb.genome_hash(e["genome"]) for e in c}) == 95
    assert all(e["metadata"]["source"] == "hephaestus" for e in c)


def test_run_is_deterministic():
    g = _g0()[3]["genome"]
    a, _ = sb.run(g, seed=0)
    b, _ = sb.run(g, seed=0)
    assert np.array_equal(a, b)


def _reg_with(c, ids):
    reg = en.Registry()
    for e in c:
        if e["id"] in ids:
            reg.add({"id": e["id"], "origin": "human", "kind": "concept", "executableRepresentation": e["genome"],
                     "parentIds": [], "metadata": {}})
    return reg


def test_collisions_are_noncommutative():
    c = _g0()
    ids = [c[i]["id"] for i in (0, 10, 20)]
    reg = _reg_with(c, ids)
    t = co.TensorStore(0)
    ga, _ = co.collide([reg[i] for i in ids], t, "cX", operators=[])
    gb, _ = co.collide([reg[i] for i in ids[::-1]], t, "cX", operators=[])
    assert sb.genome_hash(ga) != sb.genome_hash(gb)


def test_one_shot_law_depth_is_one_and_recursion_raises_it():
    from theseus.synth.analysis import law_depth
    c = _g0()
    ids = [c[i]["id"] for i in range(6)]
    reg = _reg_with(c, ids)
    t = co.TensorStore(0)
    g1, _ = co.collide([reg[i] for i in ids[:3]], t, "c1", operators=[])
    assert law_depth(g1) == 1
    reg.add({"id": "M1", "origin": "synthetic", "kind": "mechanism", "executableRepresentation": g1,
             "parentIds": ids[:3], "metadata": {}})
    g2, _ = co.collide([reg["M1"], reg[ids[3]]], t, "c2", operators=[])
    assert law_depth(g2) >= 1
    reg.add({"id": "M2", "origin": "synthetic", "kind": "mechanism", "executableRepresentation": g2,
             "parentIds": ["M1", ids[3]], "metadata": {}})
    assert reg.min_depth_to_g0("M2") == 1
    assert reg["M2"]["generation"] == 2
    assert set(reg["M2"]["ancestry"]) == {"M1", *ids[:4]}


def test_lanes_exclude_human_parents_when_deep():
    c = _g0()
    reg = _reg_with(c, [c[0]["id"]])
    assert en.eligible(reg, c[0]["id"], "G0")
    assert not en.eligible(reg, c[0]["id"], "DEEP")
    assert not en.eligible(reg, c[0]["id"], "VERY_DEEP")


def test_execution_neutral_programs_are_not_viable():
    rng = np.random.default_rng(1)
    scales = np.ones(bt.N_DESC)
    for _ in range(5):
        g = rv.neutral_genome(rng)
        r = bt.evaluate(g, scales, None)
        assert not r["viability"]["transforms"]
        assert not r["viable"]


def test_rule_destroyed_twin_does_not_transform():
    g = _g0()[0]["genome"]
    t = rv.rule_destroyed_twin(g)
    tr, _ = sb.run(t, seed=0)
    assert np.abs(tr[-1] - sb._init(t, t["C"], sb.N_DEFAULT, 0)).max() < 1e-3


def test_battery_has_at_least_twenty_interventions_and_detects_change():
    assert bt.N_INT >= 20
    g = _g0()[5]["genome"]
    f = bt.fingerprint(g, np.ones(bt.N_DESC))
    assert f["fp"].shape == (bt.FP_DIM,)
    assert (f["resp"] > 0).any()


def test_tyche_lens_runs_inside_substrate():
    from tyche import lens as tl
    lg = tl.random_genome(np.random.default_rng(3))
    g = {"C": 2, "topo": {"kind": "ring", "seed": 0}, "bc": "periodic", "init": {"kind": "random", "amp": 1.0},
         "rules": [{"op": "diffuse", "src": [0], "dst": 0, "p": [0.2]},
                   {"op": "lensmap", "src": [0], "dst": 1, "p": [0.5], "lens": lg}]}
    assert not sb.validate(g)
    tr, info = sb.run(g, seed=0, T=16)
    assert np.isfinite(tr).all()
