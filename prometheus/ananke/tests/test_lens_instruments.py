"""Known-answer tests for the two PTE instruments in lens.py: the
mirror-pair CARRIER SWAP and the TEMPORAL REACH profile. Hand plants only,
CPU. Every verdict is shown on a plant whose carrier is known by
construction, and every table includes wrong-carrier NEGATIVE controls."""
from __future__ import annotations

import pytest
import torch

from prometheus.ananke import assays, c1b, envs, lens, plants

torch.set_num_threads(2)
SEEDS = assays.world_seeds(0x7E57, 32)
HOLD = envs.EnvSpec(family="HOLD", gap=8, cue_len=2, trials=12)


def _mid(env):
    return c1b.ticks(env)["mid"]


@pytest.fixture(scope="module")
def echo():
    ph = plants.c1b_echo_physics()
    return lens.carrier_table(ph, plants.echo_hold(ph)[None], HOLD, SEEDS, _mid(HOLD),
                              names=["channel_all", "channel_content", "channel_count", "pay0",
                                     "pay1", "site_all", "w", "delay+1"])


@pytest.fixture(scope="module")
def latch():
    ph = plants.c1b_echo_physics().replace(prog_len=12, payload_width=1)
    g = plants.plant("hold_latch", ph)
    return lens.carrier_table(ph, g, HOLD, SEEDS, _mid(HOLD), names=["site_all", "S", "channel_all", "w"])


@pytest.fixture(scope="module")
def rule():
    ph = plants.c1b_rule_physics()
    return lens.carrier_table(ph, plants.rule_switch_hold(ph), HOLD, SEEDS, _mid(HOLD),
                              names=["r", "S", "channel_all"])


@pytest.fixture(scope="module")
def route():
    ph = plants.c1b_route_physics()
    env = envs.EnvSpec(family="RELAY", d=2, delta=8, cue_len=4, trials=12)
    ticks = [t0 + 5 for t0 in c1b.ticks(env)["t0"]]
    return lens.carrier_table(ph, plants.route_relay(ph)[None], env, SEEDS, ticks, names=["w", "S", "channel_all"])


def test_echo_bit_rides_in_channel_content(echo):
    assert echo["normal"][0] >= 0.95
    for n in ("channel_all", "channel_content", "pay0"):
        assert echo[n]["verdict"] == "FLIP", (n, echo[n])


def test_echo_negative_controls(echo):
    for n in ("channel_count", "pay1", "site_all", "w"):       # markers / sites / routing carry nothing
        assert echo[n]["verdict"] == "NO-EFFECT", (n, echo[n])


def test_echo_is_timing_sensitive_but_timing_cannot_flip(echo):
    assert echo["delay+1"]["kind"] == "perturb"
    assert echo["delay+1"]["verdict"] == "CHANCE", echo["delay+1"]


def test_latch_bit_in_site_state(latch):
    assert latch["S"]["verdict"] == "FLIP" and latch["site_all"]["verdict"] == "FLIP"
    assert latch["channel_all"]["verdict"] == "NO-EFFECT"


def test_rule_bit_in_rule_pointer(rule):
    assert rule["r"]["verdict"] == "FLIP", rule["r"]
    assert rule["S"]["verdict"] == "NO-EFFECT" and rule["channel_all"]["verdict"] == "NO-EFFECT"


def test_route_bit_in_routing_weights(route):
    assert route["w"]["verdict"] == "FLIP", route["w"]
    assert route["channel_all"]["verdict"] == "NO-EFFECT"


def test_verdict_rule_can_return_each_outcome():
    import numpy as np
    n = np.full(16, 0.9)
    assert lens.swap_verdict(n, np.full(16, 0.1)) == "FLIP"
    assert lens.swap_verdict(n, np.full(16, 0.9)) == "NO-EFFECT"
    assert lens.swap_verdict(n, np.full(16, 0.5)) == "CHANCE"


# ------------------------------------------------------------ temporal reach
@pytest.fixture(scope="module")
def da_profile():
    ph = plants.c1b_da_physics()
    env = envs.EnvSpec(family="RELAY", d=1, delta=4, cue_len=2, trials=12, iti=50)
    return lens.cue_arrival_profile(ph, plants.plant("relay_flood", ph), env, trial=5, M=32)


def test_reach_known_answer_delay_equals_delta(da_profile):
    lo = da_profile["cue_onset_lag"]
    c1_window = range(lo, 0)            # [t0, readout): C1's packet_ablation
    corrected = range(lo, 1)            # [t0, readout]
    assert lens.reach(da_profile, c1_window) == 0.0
    assert lens.reach(da_profile, corrected) == 1.0


def test_reach_is_undefined_without_arrivals():
    ph = plants.c1b_echo_physics().replace(prog_len=12, payload_width=1)
    prof = lens.cue_arrival_profile(ph, plants.plant("hold_latch", ph), HOLD, M=16)
    assert lens.reach(prof, range(-20, 1)) is None          # a latch sends nothing: reach undefined, not 0
