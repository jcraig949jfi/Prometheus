"""Known-answer tests for swap_v2 (CPU). Run: python -m pytest roles/Ananke/pte/c3/test_swap_v2.py -q -p no:cacheprovider"""
import os
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest  # noqa: E402

import swap_v2 as S  # noqa: E402
C = S.C
from prometheus.ananke import assays, envs, plants  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402


@pytest.fixture(scope="module")
def hold():
    ph = Physics()
    env = envs.EnvSpec(family="HOLD", gap=8, trials=12)
    g = plants.plant("hold_latch", ph)
    seeds = assays.world_seeds(C.H_int(0x5A2, 1), 64)
    return ph, env, g, seeds


def test_site_state_flips(hold):
    ph, env, g, seeds = hold
    r = S.carrier_swap(ph, g, env, seeds, [("S", None)], trials=[3, 6, 9], offset=env.cue_len + 2)
    assert r["verdict"] == "FLIP" and sum(r["applied_pairs"]) > 0


def test_unused_component_is_empty_not_no_effect(hold):
    ph, env, g, seeds = hold
    r = S.carrier_swap(ph, g, env, seeds, [("Kp", None)], trials=[3, 6, 9], offset=env.cue_len + 2)
    assert r["verdict"] == "EMPTY_SWAP"                     # M1: identical between twins -> never NO_EFFECT


def test_offset_past_readout_rejected(hold):
    ph, env, g, seeds = hold
    with pytest.raises(AssertionError):
        S.carrier_swap(ph, g, env, seeds, [("S", None)], trials=[3], offset=env.cue_len + env.gap)


def test_incompetent_specimen_gets_no_verdict(hold):
    ph, env, _, seeds = hold
    import numpy as np
    g = np.zeros((ph.rules, ph.prog_len, 5), dtype=np.int64)
    g[0, 0] = (1, 0, 4, 0, 0)            # a trivial program; whatever it does, it is not competent at HOLD
    r = S.carrier_swap(ph, g, env, seeds, [("S", None)], trials=[3, 6, 9], offset=env.cue_len + 2)
    assert r["verdict"] in ("INCOMPETENT", "EMPTY_SWAP")


def test_sub_component_swap(hold):
    ph, env, g, seeds = hold
    r0 = S.carrier_swap(ph, g, env, seeds, [("S", 0)], trials=[3, 6, 9], offset=env.cue_len + 2)
    assert r0["verdict"] == "FLIP"       # hold_latch keeps the bit in S0
