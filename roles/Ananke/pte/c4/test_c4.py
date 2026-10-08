"""PTE-C4 known-answer tests (CPU). Run: python -m pytest roles/Ananke/pte/c4/test_c4.py -q -p no:cacheprovider"""
import dataclasses
import json
import os
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
import pytest  # noqa: E402

import c4_common as K  # noqa: E402
C = K.C; R = K.R
from prometheus.ananke import assays, envs  # noqa: E402


@pytest.fixture(scope="module")
def cell():
    P = json.load(open(os.path.join(HERE, "..", "c2c", "PLAN_C2C.json")))
    c = [x for x in P["cells"] if x["cell_id"].startswith("FLIP-0000")][0]
    ph = R.rep_physics(C.Physics.from_dict(c["physics"]).validate(), "R4")
    env = dataclasses.replace(envs.EnvSpec(**c["env"]), family="GATE")
    return ph, env


def test_gate_env_semantics(cell):
    ph, env = cell
    seeds = assays.world_seeds(C.H_int(0x7E57, 2), 64)
    ep = envs.build(ph, env, seeds)
    sv = ep.schedule.sense_val.numpy(); Pd = env.period()
    for b in range(0, 64, 2):
        assert (ep.y[b] == -ep.y[b + 1]).all()                                   # mirror twins: target negated
        assert int(ep.schedule.read_idx[b, 0]) == int(ep.schedule.sense_idx[b, 1])  # context sensed at the actuator
        x = np.sign(sv[np.arange(env.trials) * Pd, b, 0])
        ctx = np.sign(sv[np.arange(0, env.trials, env.block) * Pd, b, 1])
        assert (ep.y[b] == np.repeat(ctx, env.block) * x).all()                 # y = context * cue
        nz = np.flatnonzero(sv[:, b, 1])
        assert set(nz // Pd) <= set(range(0, env.trials, env.block))             # context only at block onsets
    assert ep.scored.all()
    lag1 = np.mean([np.corrcoef(ep.y[b, :-1], ep.y[b, 1:])[0, 1] for b in range(0, 64, 2)])
    assert abs(lag1) < 0.15                                                      # no sequential exploit


def test_gate_plant_competent_and_controls_fail(cell):
    ph, env = cell
    seeds = assays.world_seeds(C.H_int(0x7E57, 3), 128)
    pt, ep = C.eval_programs(ph, env, seeds, [K.gate_plant(ph), C.null(ph), K.relay_plant(ph)], device="cpu")
    assert C.competence("RELAY-mh", pt[0], ep)["status"] == "TRUE"
    assert C.competence("RELAY-mh", pt[1], ep)["status"] == "FALSE"
    assert C.competence("RELAY-mh", pt[2], ep)["status"] != "TRUE"                 # cue relay without context fails


def test_live_lines_finds_plant_body(cell):
    ph, env = cell
    seeds = assays.world_seeds(C.H_int(0x7E57, 4), 16)
    live, _ = K.live_lines(ph, env, K.gate_plant(ph), seeds, "RELAY-mh")
    assert set(live) <= set(range(15)) and len(live) >= 8                       # only plant lines can be live


def test_rename_state_identity_swap_and_shift_untouched(cell):
    ph, env = cell
    g = K.gate_plant(ph)[0]
    assert np.array_equal(K.rename_state(g, ph, [0, 1, 2]), g)
    sw = K.rename_state(g, ph, [1, 0, 2])                    # swap S0 <-> S1
    assert np.array_equal(K.rename_state(sw, ph, [1, 0, 2]), g)  # involution
    D, NW, NR = ph.state_dim, ph.n_write(), ph.n_read()
    for a, b in zip(g, sw):
        op = int(a[0]) % 16
        if op in (6, 10):
            assert a[3] == b[3]                               # shift field untouched
        if int(a[1]) % NW == 0:
            assert int(b[1]) % NW == 1                         # dst S0 -> S1


def test_renamed_module_keeps_function_with_readout_renamed_back(cell):
    """A RELAY plant renamed S0<->S1 no longer drives the readout (S0); renaming back restores it exactly."""
    ph, env = cell
    import dataclasses as dc
    renv = dc.replace(env, family="RELAY", d=1, trials=12)
    seeds = assays.world_seeds(C.H_int(0x7E57, 5), 64)
    g = K.relay_plant(ph)
    r = np.stack([K.rename_state(g[0], ph, [1, 0, 2])])
    back = np.stack([K.rename_state(r[0], ph, [1, 0, 2])])
    pt, ep = C.eval_programs(ph, renv, seeds, [g, r, back], device="cpu")
    assert np.array_equal(pt[0], pt[2])
    assert C.competence("RELAY-mh", pt[0], ep)["status"] == "TRUE" and C.competence("RELAY-mh", pt[1], ep)["status"] != "TRUE"
