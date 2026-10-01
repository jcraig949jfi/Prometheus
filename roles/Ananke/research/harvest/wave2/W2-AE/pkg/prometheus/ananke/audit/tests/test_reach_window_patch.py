"""W2-B's reach_certificate patch (promoted into audit.trace): a hook in an EARLIER trial whose difference died
before this trial's cue no longer makes the trial ABSORBED; a value-only change is not a decision change.
(W2-B tests/test_reachcert_patch.py: FAIL on the H-INST draft, PASS on the patched module promoted here.)"""
from __future__ import annotations

import torch

from prometheus.ananke import assays, c1b, envs, plants
from prometheus.ananke.audit import trace as P

SEEDS = assays.world_seeds(0x7E57, 16)
M = len(SEEDS)
HOLD = envs.EnvSpec(family="HOLD", gap=8, cue_len=2, trials=12)
TK = c1b.ticks(HOLD)
K = 5


def latch():
    ph = plants.c1b_echo_physics().replace(prog_len=12, payload_width=1)
    return ph, plants.plant("hold_latch", ph)


def test_hook_in_earlier_trial_does_not_make_trial_absorbed():
    ph, g = latch()
    ep = envs.build(ph, HOLD, SEEDS)
    a = torch.as_tensor(ep.schedule.read_idx[:, 0])

    def zero(w):
        w.S[torch.arange(M), a, 0] = 0
    r = P.reach_certificate(ph, g, HOLD, SEEDS, {TK["mid"][0]: zero}, K)
    assert r["applied"] == 1.0
    assert r["verdict"] == "NOT_REACHED", r["verdict"]
    # MUST-STAY: the same hook inside trial K's window is still a touch (and an output change)
    r2 = P.reach_certificate(ph, g, HOLD, SEEDS, {TK["mid"][K]: zero}, K)
    assert r2["verdict"] == "REACHED_OUTPUT"


def test_value_only_change_is_not_a_decision_change():
    ph, g = latch()
    ep = envs.build(ph, HOLD, SEEDS)
    a = int(ep.schedule.read_idx[0, 0])

    def nudge(w):
        w.S[0, a, 0] += 1
    r = P.reach_certificate(ph, g, HOLD, SEEDS, {TK["ro"][K] - 1: nudge}, K)
    assert r["verdict"] == "REACHED_OUTPUT" and abs(r["output"] - 1 / M) < 1e-9
    assert r.get("decision") == 0.0
    assert r["per_world"][0] == "REACHED_VALUE_ONLY" and r["per_world"][1] == "UNAPPLIED"
