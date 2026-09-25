"""Environment guarantees, plant controls and assay guards."""
from __future__ import annotations

import numpy as np
import pytest
import torch

from prometheus.ananke import assays, envs, plants
from prometheus.ananke.engine import Controls
from prometheus.ananke.physics import Physics

DEV = "cuda" if torch.cuda.is_available() else "cpu"
PH = Physics(topology="torus", n_sites=100, radius=1, dest_mode="all", prog_len=12)


def fam_env(f):
    return envs.EnvSpec(family=f, d=3, delta=8, gap=6, trials=16, block=4)


@pytest.mark.parametrize("fam", envs.FAMILIES)
def test_mirror_pairs_make_constants_exactly_chance(fam):
    ep = envs.build(PH, fam_env(fam), assays.world_seeds(1, 16))
    y = ep.y
    assert (y[0::2] == -y[1::2]).all()
    for c in (-1, 0, 1):
        tr = np.full((ep.ro_tick.max() + 1, 16, 1), c)
        acc = envs.score(ep, tr)
        assert np.allclose(acc.reshape(8, 2).mean(1), 0.5)


@pytest.mark.parametrize("fam", envs.FAMILIES)
def test_no_sequential_exploit(fam):
    """Lag-1 target autocorrelation ~ 0 at scale (the 2026-09-24 defect)."""
    ep = envs.build(PH, fam_env(fam), assays.world_seeds(2, 800))
    y = ep.y[0::2].astype(float)
    if fam == "FLIP":   # within-block: y_k*y_{k-1} = x_k*x_{k-1}, iid
        pass
    r = (y[:, 1:] * y[:, :-1]).mean()
    assert abs(r) < 0.03, r


def test_xor_single_input_carries_no_information():
    ep = envs.build(PH, fam_env("XOR"), assays.world_seeds(3, 400))
    sv = ep.schedule.sense_val.numpy()
    x1 = np.sign(sv[ep.ro_tick[0] - 8, :, 0]).T     # cue onset of each trial
    corr = (x1 * ep.y).mean()
    assert abs(corr) < 0.03


def test_relay_plant_positive_and_zero_comm_negative():
    seeds = assays.world_seeds(4, 16)
    g = plants.plant("relay_flood", PH)[None]
    env = fam_env("RELAY")
    assert assays.evaluate(PH, g, env, seeds, device=DEV).mean()[0] == 1.0
    z = assays.evaluate(PH, g, env, seeds, ctrl=Controls(zero_comm=True), device=DEV)
    assert z.mean()[0] == 0.5


def test_null_plant_is_chance_and_insensitive():
    seeds = assays.world_seeds(5, 16)
    r = assays.evaluate(PH, plants.plant("null", PH)[None], fam_env("RELAY"), seeds, device=DEV)
    assert r.mean()[0] == 0.5 and r.sens_any[0] == 0 and r.sens_act[0] == 0


def test_contrast_detects_real_dependence():
    seeds = assays.world_seeds(6, 16)
    r = assays.evaluate(PH, plants.plant("hold_latch", PH)[None], fam_env("HOLD"), seeds, device=DEV)
    assert r.mean()[0] == 1.0 and r.sens_act[0] == 1.0


def test_noop_guard_marks_inapplicable_controls():
    seeds = assays.world_seeds(7, 8)
    out = assays.run_controls(PH, plants.plant("relay_flood", PH), fam_env("RELAY"), seeds, device=DEV)
    assert out["frozen_routing"]["status"] == "NOT_APPLICABLE"   # plastic_route=0
    assert out["zero_comm"]["status"] == "RAN" and out["zero_comm"]["acc"] == 0.5
    assert out["irrelevant_channel"]["status"] == "RAN"


def test_twin_assay_null_and_positive():
    seeds = assays.world_seeds(8, 4)
    G = np.stack([plants.plant("relay_flood", PH), plants.plant("null", PH)])
    tw = assays.twin_assay(PH, G, fam_env("RELAY"), seeds, device=DEV)
    assert tw["readout_flipped"][0] == 1.0 and tw["reach"][0] >= 3
    assert tw["reach"][1] == 0 and tw["persist"][1] == 0
