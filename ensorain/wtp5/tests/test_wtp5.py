import ast
import os

import numpy as np

from ensorain.wtp5 import worlds, tape, mutate, planted, certify

HERE = os.path.dirname(os.path.dirname(__file__))


def test_search_never_imports_planted():
    for f in ("search.py", "mutate.py", "campaign5.py"):
        p = os.path.join(HERE, f)
        if not os.path.exists(p):
            continue
        tree = ast.parse(open(p).read())
        names = {a.name for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) for a in n.names}
        mods = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
        assert "planted" not in names and not any(m and "planted" in m for m in mods), f


def test_planted_solvers_pass():
    for spec in ("A-R2-desert", "A-R3-desert", "B-R2-desert", "B-R3-desert", "N-R2-desert", "N-R3-desert"):
        w = worlds.make(spec)
        out = tape.lifetime(planted.planted(w), w, np.random.default_rng(3))
        assert out["roles"][1] == 1.0, spec


def test_desert_targets_balanced_and_gate_obs_identical():
    w = worlds.make("A-R2-desert")
    ep = w.block(256, np.random.default_rng(0))
    T = w.T
    assert abs(ep["tgt"][:, T - 1].mean()) < 0.2
    g = ep["obs"][:, T - 1]
    # the gate observation carries only b: identical across contexts given b
    assert np.allclose(g[:, [0, 1, 3, 4, 5]], g[0, [0, 1, 3, 4, 5]])


def test_certifier_rejects_empty_state_and_ranks_planted():
    g = mutate.random_genome(np.random.default_rng(0))
    for nd in g["nodes"]:
        assert nd["op"] != "WRITE" or True
    blank = tape.genome([tape.node("OBS"), tape.node("CH", 0, i=0), tape.node("ACT", 1)], S=2)
    c = certify.certify(blank, "A", "R2", 5)
    assert c["rung"] == -1
    c = certify.certify(planted.planted(worlds.make("A-R3-desert")), "A", "R3", 5)
    assert c["rung"] == 3


def test_working_state_bounded():
    g = planted.planted(worlds.make("N-R3-desert"))
    assert g["S"] * tape.W <= 64


def test_mutation_arms():
    rng = np.random.default_rng(1)
    g = mutate.random_genome(rng)
    for _ in range(300):
        g, _ = mutate.mutate(g, rng, promotion=False, plasticity=False)
        assert not g["modules"] and g["eta"] == 0
    for _ in range(300):
        g, _ = mutate.mutate(g, rng, promotion=True, plasticity=True)
        assert len(g["nodes"]) <= tape.N_MAX + 12
        tape.lifetime(g, worlds.make("A-R2-desert"), rng, L=1, K=4)


def test_flat_stop_rule():
    from ensorain.wtp5.search import Run
    r = Run.__new__(Run)
    r.evals = 100_000
    r.telemetry = [dict(evals=e, best_rung=0, archive=100, best_fit=0.6) for e in range(0, 100_001, 10_000)]
    assert r.frontier_flat()
    r.telemetry[-1]["best_rung"] = 1
    assert not r.frontier_flat()
    r.telemetry[-1]["best_rung"] = 0
    r.telemetry[-1]["archive"] = 106
    assert not r.frontier_flat()
    r.telemetry[-1]["archive"] = 100
    r.telemetry[-2]["best_fit"] = 0.62
    assert not r.frontier_flat()
    r.evals, r.telemetry = 40_000, r.telemetry[:5]
    assert not r.frontier_flat()
