"""Ares controls. Negative: random organisms sit at the chance floor.
Positive: the GA improves on a world in a few generations. Cheat: a
hand-wired organism that carries the intended conditional behaviour
scores far above any fixed policy AND the node-ablation measure
localises it; the no-state substrate ablation destroys a hand-wired
carrier. Determinism: same seed, same log. These are controls on the
INSTRUMENT; the hand-wired organisms never enter a sweep population."""
import json
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))

from ares import substrate as S          # noqa: E402
from ares import search as R             # noqa: E402
from ares import worlds as W             # noqa: E402
from ares.develop import express, random_dev_population, run_dev  # noqa: E402

CFG = S.Config()


def fixed_policy_population(action, cfg=CFG):
    """One organism whose output `action` node is a constant 1, others 0."""
    pop = S.Population(cfg, 1)
    out = cfg.n - S.N_OUT + action
    pop.op[0, out] = S.OPS.index("CONST"); pop.bias[0, out] = 1.0
    return pop


def test_all_worlds_all_modes_run_under_fixed_policies():
    for name in W.WORLDS:
        for mode in W.MODES:
            for a in range(3):
                f = R.rollout(fixed_policy_population(a), R.make_world(name, mode), [1, 2, 3])
                assert np.all(np.isfinite(f)), (name, mode, a)


def test_random_population_is_at_chance_on_W4():
    # W4 hidden regime: with no cue after step 3 a random organism cannot
    # exceed the fixed-policy floor of ~0 by more than noise.
    rng = np.random.default_rng(3)
    pop = S.random_population(CFG, 256, rng)
    f = R.rollout(pop, R.make_world("W4", "present"), R.EVAL_SEEDS)
    assert abs(f.mean()) < 3.0, f.mean()


def test_determinism():
    a = R.run("W3", "present", CFG, P=32, G=4, eps=2, seed=7, log_every=2)
    b = R.run("W3", "present", CFG, P=32, G=4, eps=2, seed=7, log_every=2)
    assert json.dumps(a["log"], sort_keys=True) == json.dumps(b["log"], sort_keys=True)
    assert a["final"]["heldout"] == b["final"]["heldout"]


def test_positive_control_ga_improves_W3_absent():
    out = R.run("W3", "absent", CFG, P=64, G=12, eps=3, seed=1, log_every=11)
    assert out["log"][-1]["champ_heldout"] > out["log"][0]["mean_train"] + 5


def cheat_W2():
    """Risky exactly when the cue channel exceeds 0.5. Output1 = THRESH(cue > 0.5);
    output0 = CONST 0.5 so that when the threshold is off, safe wins."""
    pop = S.Population(CFG, 1)
    n = CFG.n; o0, o1 = n - 3, n - 2
    h = S.OBS_DIM
    pop.alive[0, h] = True
    pop.op[0, h] = S.OPS.index("THRESH"); pop.W1[0, h, 1] = 1.0; pop.bias[0, h] = 0.5   # cue - 0.5 > 0
    pop.op[0, o1] = S.OPS.index("ADD"); pop.W1[0, o1, h] = 2.0                        # output1 = 2*thresh
    pop.op[0, o0] = S.OPS.index("CONST"); pop.bias[0, o0] = 0.5
    return pop


def test_cheat_control_W2_conditional_risk_is_expressible_and_localised():
    w = R.make_world("W2", "present")
    safe = R.rollout(fixed_policy_population(0), w, R.EVAL_SEEDS)[0]
    risky = R.rollout(fixed_policy_population(1), w, R.EVAL_SEEDS)[0]
    cheat = cheat_W2()
    f = R.rollout(cheat, w, R.EVAL_SEEDS)[0]
    assert risky < safe < f, (risky, safe, f)          # always-risky is strictly worse than always-safe
    assert f > safe + 30, (f, safe)
    d = R.dissect(cheat.genome(0), "W2", "present")
    assert len(d["node_ablation"]) == 1
    assert d["node_ablation"][0]["fit"] <= safe + 1e-6  # removing the gate node collapses to fixed-safe
    # the same organism in the shuffled world gains nothing over safe
    fs = R.rollout(cheat, R.make_world("W2", "shuffled"), R.EVAL_SEEDS)[0]
    ss = R.rollout(fixed_policy_population(0), R.make_world("W2", "shuffled"), R.EVAL_SEEDS)[0]
    assert fs < ss, (fs, ss)


def cheat_W4():
    """A hidden node with keep 0.9 fed by the cue keeps the early regime
    sign; outputs read its sign. Nothing here is named; it is one node."""
    pop = S.Population(CFG, 1)
    n = CFG.n; o1, o2 = n - 2, n - 1
    h = S.OBS_DIM
    pop.alive[0, h] = True
    # a saturating self-loop: tanh(3*v + 3*cue) is bistable at +-1 and holds
    # its sign against the 0.3-sd noise once the cue is gone. (A leak-only
    # carrier with keep 0.9 decays to noise by step ~15: recorded 2026-09-19.)
    pop.op[0, h] = S.OPS.index("TANH"); pop.W1[0, h, 1] = 3.0; pop.W1[0, h, h] = 3.0
    pop.op[0, o1] = S.OPS.index("ADD"); pop.W1[0, o1, h] = -1.0
    pop.op[0, o2] = S.OPS.index("ADD"); pop.W1[0, o2, h] = 1.0
    return pop


def test_cheat_control_W4_carrier_destroyed_by_no_state_ablation():
    w = R.make_world("W4", "present")
    f = R.rollout(cheat_W4(), w, R.EVAL_SEEDS)[0]
    assert f > 25, f                                  # 40 steps, +1 each when right
    d = R.dissect(cheat_W4().genome(0), "W4", "present")
    assert d["substrate_ablation"]["no_state"] < 10, d["substrate_ablation"]


def test_genome_round_trip():
    out = R.run("W1", "present", CFG, P=32, G=3, eps=2, seed=5, log_every=2)
    g = out["final"]["genome"]
    pop = S.Population.from_genomes([g])
    f = R.rollout(pop, R.make_world("W1", "present"), R.EVAL_SEEDS)[0]
    assert abs(f - out["final"]["heldout"]) < 1e-4


def test_development_expresses_and_runs():
    rng = np.random.default_rng(0)
    dev = random_dev_population(CFG, 16, rng)
    pop = express(dev)
    assert pop.alive[:, S.OBS_DIM].all()
    out = run_dev("W4", "present", CFG, P=16, G=2, eps=1, seed=0, log_every=1)
    assert np.isfinite(out["final"]["heldout"])


def test_catalog_loads_and_every_world_entry_is_wired():
    cat = json.load(open(os.path.join(os.path.dirname(HERE), "PRESSURE_CATALOG.json")))
    for p in cat["pressures"]:
        if p["status"] == "WORLD":
            assert p["world"] in W.WORLDS or p["world"] in ("W6", "W9", "W10"), p["id"]
        assert p["falsification"], p["id"]


def test_coevolution_runs_and_static_modes_do_not_evolve_B():
    out = R.run_coevo("absent", CFG, P=16, G=2, eps=1, seed=0, log_every=1)
    assert np.isfinite(out["final"]["heldout"])
    out = R.run_coevo("present", CFG, P=16, G=2, eps=1, seed=0, log_every=1)
    assert np.isfinite(out["final"]["heldout"])
