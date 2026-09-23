"""Cycle-2 controls. The carrier instrumentation must (a) separate a
hand-wired RECURRENT carrier from a hand-wired KEEP carrier, (b) move an
OUTPUT self-loop under transplant (the cycle-1 blind spot), (c) bind the
exclusion constraints, (d) show the hostile worlds actually damage an
activation carrier. Hand-wired organisms never enter a sweep population.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))

from ares import carriers as C          # noqa: E402
from ares import search as R            # noqa: E402
from ares import substrate as S         # noqa: E402

CFG = S.Config()
W4_SEEDS = None


def seeds():
    global W4_SEEDS
    if W4_SEEDS is None:
        W4_SEEDS = R.balanced_seeds_for(R.make_world("W4", "present"))
    return W4_SEEDS


def recur_carrier():
    """A saturating self-loop holds the cue's sign for the whole life."""
    pop = S.Population(CFG, 1)
    n = CFG.n; h = S.OBS_DIM
    pop.alive[0, h] = True
    pop.op[0, h] = S.OPS.index("TANH")
    pop.W1[0, h, 1] = 3.0
    pop.W1[0, h, h] = 3.0                      # the carrier edge
    pop.op[0, n - 2] = S.OPS.index("ADD"); pop.W1[0, n - 2, h] = -1.0
    pop.op[0, n - 1] = S.OPS.index("ADD"); pop.W1[0, n - 1, h] = 1.0
    return pop


def keep_carrier():
    """A near-unity leak coefficient holds the sign with NO edge cycle:
    the DESIGNATED carrier, hand-wired so it actually works."""
    pop = S.Population(CFG, 1)
    n = CFG.n; h = S.OBS_DIM
    pop.alive[0, h] = True
    pop.op[0, h] = S.OPS.index("ADD")
    pop.W1[0, h, 1] = 1.0
    pop.keep[0, h] = 0.98                      # the carrier coefficient
    pop.op[0, n - 2] = S.OPS.index("ADD"); pop.W1[0, n - 2, h] = -1.0
    pop.op[0, n - 1] = S.OPS.index("ADD"); pop.W1[0, n - 1, h] = 1.0
    return pop


def test_both_hand_wired_carriers_work_and_are_distinguished():
    s = seeds()
    fr = float(R.rollout(recur_carrier(), R.make_world("W4", "present"), s)[0])
    fk = float(R.rollout(keep_carrier(), R.make_world("W4", "present"), s)[0])
    # bar is "unambiguously above the world's floor (0.0) and above any
    # fixed policy", not a tuned number: both carriers clear half the cap.
    assert fr > 20, fr
    assert fk > 20, fk            # the designated carrier is NOT unusable
    ar = C.carrier_ablation(recur_carrier().genome(0), "W4", "present", s)
    ak = C.carrier_ablation(keep_carrier().genome(0), "W4", "present", s)
    assert ar["carrier_class"] == "RECUR", (ar["carrier_class"], ar["collapses"])
    assert ak["carrier_class"] == "KEEP", (ak["carrier_class"], ak["collapses"])
    assert ar["collapses"]["recurrent"] and not ar["collapses"]["keep"]
    assert ak["collapses"]["keep"] and not ak["collapses"]["recurrent"]
    assert ar["inventory"]["self_loops"] == 1 and ak["inventory"]["self_loops"] == 0
    assert ak["inventory"]["keep_nodes"] == 1


def test_edge_ablation_finds_the_single_carrier_edge():
    a = C.carrier_ablation(recur_carrier().genome(0), "W4", "present", seeds())
    lb = a["load_bearing_edges"]
    assert len(lb) == 1, lb
    assert lb[0]["self_loop"] and lb[0]["src"] == S.OBS_DIM


def output_selfloop_carrier():
    """The cycle-1 blind spot: the loop lives on an OUTPUT node, which
    hidden-node ablation can never remove."""
    pop = S.Population(CFG, 1)
    n = CFG.n
    o = n - 1
    pop.op[0, o] = S.OPS.index("TANH")
    pop.W1[0, o, 1] = 3.0
    pop.W1[0, o, o] = 3.0
    pop.op[0, n - 2] = S.OPS.index("CONST"); pop.bias[0, n - 2] = 0.0
    return pop


def test_output_selfloop_is_invisible_to_node_ablation_but_visible_here():
    g = output_selfloop_carrier().genome(0)
    d = R.dissect(g, "W4", "present", seeds=seeds())
    assert d["node_ablation"] == [], d["node_ablation"]      # no hidden nodes at all
    a = C.carrier_ablation(g, "W4", "present", seeds())
    assert a["inventory"]["self_loops_on_output"] == 1
    assert a["collapses"]["recurrent"], a


def test_transplant_moves_an_output_selfloop():
    g = output_selfloop_carrier().genome(0)
    inv = C.inventory(g)
    nodes = inv["scc_nodes"][0]
    assert nodes == [CFG.n - 1]
    rng = np.random.default_rng(0)
    hosts = S.random_population(CFG, 4, rng)
    m = C.splice_carrier(hosts, 0, g, nodes, rng)
    assert m is not None
    assert hosts.W1[0, CFG.n - 1, CFG.n - 1] != 0            # the loop actually moved


def test_forbid_recurrence_binds_under_mutation():
    cfg = S.Config(forbid_recurrence=True)
    rng = np.random.default_rng(1)
    pop = S.random_population(cfg, 24, rng)
    for _ in range(40):
        for p in range(pop.P):
            S.mutate_one(pop, p, rng)
    assert int(S.n_recurrent_edges(pop).sum()) == 0
    for p in range(pop.P):
        assert not S.has_cycle_one(pop, p)


def test_forbid_self_loops_binds_under_mutation():
    cfg = S.Config(forbid_self_loops=True)
    rng = np.random.default_rng(2)
    pop = S.random_population(cfg, 24, rng)
    for _ in range(40):
        for p in range(pop.P):
            S.mutate_one(pop, p, rng)
    d = np.arange(cfg.n)
    assert int(((pop.W1[:, d, d] != 0) | (pop.W2[:, d, d] != 0)).sum()) == 0


def test_hostile_worlds_damage_an_activation_carrier():
    s4 = seeds()
    base = float(R.rollout(recur_carrier(), R.make_world("W4", "present"), s4)[0])
    for w in ("W14", "W15"):
        sw = R.balanced_seeds_for(R.make_world(w, "present"))
        f = float(R.rollout(recur_carrier(), R.make_world(w, "present"), sw)[0])
        # >= 10% relative damage. Measured 2026-09-23: W14 (activation
        # noise) costs a SATURATING self-loop only ~18% -- saturation is
        # intrinsically noise-robust, so W14 is a weak attack on this
        # carrier and W15 (reset) is the strong one. Recorded in DESIGN_C2.
        assert f < 0.9 * base, (w, f, base)


def test_interrupt_world_actually_resets_state():
    w = R.make_world("W15", "present")
    w.reset(np.random.default_rng(seeds()[0]), 1)
    assert len(w.reset_steps) == 4 and all(5 <= t < w.T - 5 for t in w.reset_steps)


def test_opportunity_is_measurable_and_keep_is_reachable():
    o = C.opportunity(S.Config(), n_trials=600, seed=3)
    assert o["eligible"]["keep"] > 100 and o["eligible"]["recurrent"] > 100
    assert 0.0 <= o["p_create"]["keep"] <= 1.0
    assert o["p_create"]["keep"] > 0, o          # keep IS mutationally reachable
