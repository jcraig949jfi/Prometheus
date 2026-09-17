"""Controls for the keyed-memory expressiveness witness (point release Stage 0, 2026-09-17).

positive  the 12-instruction keyed program answers every ASK on both probes
negative  the one-value (last-PUT) program -- the shelf strategy of C3-SFE-02 -- scores exactly
          half on the two-key probe and 1/16 on the all-keys probe: the probe separates the two
          memory classes rather than rewarding "any output"
cheat     an echo program (output whatever is on the value channel) scores 0 under the honest
          probe and 6/6 under a probe that LEAKS the expected value on the value channel during
          ASK ticks -- so a full score is evidence of memory, not of a leaky channel
identity  same manifest, same inputs -> byte-identical outputs and ops (the meter minus timings)
"""
from __future__ import annotations

import json
import os

from proteus.eval import keyed_memory_witness as W
from proteus.foundry.identity import RUNTIME_HASH
from proteus.foundry.prng import SplitMix64
from proteus.foundry.vm import Meter, Player

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_positive_keyed_program_answers_every_ask():
    w = W.witness()
    assert w["verdict"] == "ISA_EXPRESSES_KEYED_MEMORY"
    k = w["rows"]["keyed"]
    assert (k["two_key"]["correct"], k["two_key"]["asks"]) == (6, 6)
    assert (k["all_keys"]["correct"], k["all_keys"]["asks"]) == (16, 16)
    assert k["genome_instructions"] == 12
    assert k["two_key"]["statuses"] == ["halt"]          # never runs out of tick budget


def test_negative_one_value_program_sits_on_the_half_credit_shelf():
    w = W.witness()
    o = w["rows"]["one_value"]
    assert (o["two_key"]["correct"], o["two_key"]["asks"]) == (3, 6)
    assert (o["all_keys"]["correct"], o["all_keys"]["asks"]) == (1, 16)
    assert w["controls"]["negative_one_value_scores_below_keyed"] is True
    assert w["controls"]["inert_outputs_nothing"] is True


def _echo_genome():
    g = []
    g += W._instr(W.LDC, 1, 1)      # r1 = 1
    g += W._instr(W.IN, 5, 1)       # r5 = value channel (0 when empty)
    g += W._instr(W.OUT, 5, 0)      # output it
    g += W._instr(W.HALT)
    return g


def _run(manifest, ticks, leak):
    p = Player(manifest)
    st = p.fresh_state()
    rng = SplitMix64(0)
    correct = total = 0
    for t in ticks:
        if t[0] == "PUT":
            inputs = [[t[1]], [t[2]]]
        else:
            inputs = [[t[1]], [t[2]] if leak else []]
        o, _ = p.run_tick(st, inputs, 1, rng, meter=Meter())
        got = o[0][0] if o and o[0] else None
        if t[0] == "ASK":
            total += 1
            correct += got == t[2]
        st["ticks"] += 1
    return correct, total


def test_cheat_echo_scores_zero_unless_the_probe_leaks():
    m = W.manifest_for(_echo_genome())
    assert _run(m, W.two_key_episode(), leak=False) == (0, 6)
    assert _run(m, W.two_key_episode(), leak=True) == (6, 6)


def test_identity_replay_is_exact():
    m = W.manifest_for(W.keyed_memory_genome(48))
    a = W.run_episode(m, W.two_key_episode())
    b = W.run_episode(m, W.two_key_episode())
    assert a == b
    assert a["ops"] == 81


def test_committed_witness_matches_the_runtime():
    path = os.path.join(ROOT, "proteus", "eval", "KEYED_MEMORY_WITNESS.json")
    if not os.path.exists(path):
        return
    committed = json.load(open(path, encoding="utf-8"))
    assert committed["runtime_hash"] == RUNTIME_HASH
    live = W.witness()
    assert live["rows"] == committed["rows"]
    assert live["verdict"] == committed["verdict"]
