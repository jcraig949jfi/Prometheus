"""audit.guards: each guard is silent on a clean protocol and FIRES on the corruption it targets
(guard_that_cannot_fire), and G12 carries W2-O's control exemption: silent on the zero_comm World of a recorded
SIGNAL cell, still firing on a genuinely dead normal arm. Corruptions are small inline monkeypatches (W2-C's
operator catalogue stays with its experiment tooling)."""
from __future__ import annotations

import numpy as np
import pytest

from prometheus.ananke import assays, envs, plants, search
from prometheus.ananke import engine as E
from prometheus.ananke.audit import guards as G
from prometheus.ananke.audit.tests import _data as D
from prometheus.ananke.engine import Controls
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int

SEEDS = assays.world_seeds(4242, 16)
PH_SMALL = Physics(topology="torus", n_sites=64, radius=1, dest_mode="all", prog_len=12, state_dim=4,
                   payload_width=2, channels=2).validate()
ENV = envs.EnvSpec(family="RELAY", d=2, delta=8, trials=4)
GENOME = plants.plant("relay_flood", PH_SMALL)


def protocol():
    """normal + zero_comm on the same seeds (the held block's shape), single genome."""
    assays.evaluate(PH_SMALL, GENOME[None], ENV, SEEDS, device="cpu")
    assays.evaluate(PH_SMALL, GENOME[None], ENV, SEEDS, ctrl=Controls(zero_comm=True), device="cpu")


def alarms(corruption=()):
    with G.patched(list(corruption)):
        with G.guarded() as g:
            protocol()
            g.champion = GENOME
            return set(g.check())


def drop_mirror():
    b0 = envs.build

    def build(ph, env, seeds):
        ep = b0(ph, env, seeds)
        ep.schedule.sense_val[:, 1::2] = ep.schedule.sense_val[:, 0::2]
        ep.y[1::2] = ep.y[0::2]
        return ep
    return [(envs, "build", build)]


def invert_scorer():
    sc = envs.score
    return [(envs, "score", lambda ep, trace: sc(ep, -np.asarray(trace)))]


def control_ignored():
    init = E.World.__init__

    def __init__(self, ph, genomes, world_seeds, device="cuda", ctrl=None, schedule=None, census=False):
        init(self, ph, genomes, world_seeds, device=device, ctrl=None, schedule=schedule, census=census)
    return [(E.World, "__init__", __init__)]


def test_clean_run_raises_only_the_advisory():
    assert alarms() == {"G0_DEGENERATE_CONTROL"}    # zero_comm is forced at .5 for a relay: baseline-visible


@pytest.mark.parametrize("corruption,guards", [
    (drop_mirror, {"G4_MIRROR_INVARIANT"}),
    (invert_scorer, {"G10_SCORER_SELFTEST"}),
    (control_ignored, {"G5_CONDITION_PROVENANCE", "G6_CONTROL_DISTINGUISHABLE"}),
])
def test_guard_fires_on_its_corruption(corruption, guards):
    assert guards <= alarms(corruption())


def test_held_disjoint_fires_only_when_selection_and_held_share_worlds():
    with G.guarded() as g:
        assays.evaluate(PH_SMALL, GENOME[None].repeat(2, 0), ENV, SEEDS, device="cpu")    # selection
        assays.evaluate(PH_SMALL, GENOME[None], ENV, SEEDS, device="cpu")                 # 'held'
        assert "G8_HELD_DISJOINT" in g.check()
    with G.guarded() as g:
        assays.evaluate(PH_SMALL, GENOME[None].repeat(2, 0), ENV, assays.world_seeds(1, 8), device="cpu")
        assays.evaluate(PH_SMALL, GENOME[None], ENV, SEEDS, device="cpu")
        assert "G8_HELD_DISJOINT" not in g.check()


def test_patched_restores_on_exception():
    before = envs.build
    with pytest.raises(RuntimeError):
        with G.patched([(envs, "build", None)]):
            raise RuntimeError
    assert envs.build is before


def _held(cid, arms=("normal", "zero_comm")):
    r = D.by_id()[cid]
    ph = Physics.from_dict(r["physics"]).validate()
    env = envs.EnvSpec(**r["env"])
    sp = search.SearchSpec(**r["search"])
    champ = np.asarray(r["result"]["champion"])
    hs = assays.world_seeds(H_int(r["search_seed"], search.HELD_NS), sp.M_held)
    with G.guarded() as g:
        g.champion = champ
        if "normal" in arms:
            rh = assays.evaluate(ph, champ[None], env, hs, device="cpu", graph=False)
            # known answer: the recorded held accuracy reproduces exactly (otherwise the test is meaningless)
            assert abs(assays.pair_ci(rh.pair_acc()[0])[0] - r["result"]["held"]["acc"]) < 1e-12
        if "zero_comm" in arms:
            assays.evaluate(ph, champ[None], env, hs, ctrl=Controls(zero_comm=True), device="cpu", graph=False)
        return set(g.check()), r


@D.need(D.ROWS)
def test_g12_silent_on_zero_comm_arm_of_recorded_signal_cell():
    """W2-O: on the W2-C draft G12 fired here (false 'broken experiment' alarm raised by the zero_comm World)."""
    a, r = _held("1d88af703d4dab91")              # RELAY smallworld, recorded SIGNAL, held .681
    assert r["labels"]["SIGNAL"] is True
    assert "G12_STATE_LIVE" not in a, a


@D.need(D.ROWS)
def test_g12_still_fires_on_a_dead_normal_arm():
    a, _ = _held("89bd6fdb1b66ce96", arms=("normal",))   # recorded NULL; emissions stop, E -> 0
    assert "G12_STATE_LIVE" in a, a
