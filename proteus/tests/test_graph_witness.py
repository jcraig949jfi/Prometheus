"""Keyed-memory witness on the graph substrate (PROTEUS-46, first half) -- controls mirror the v0 witness."""
from __future__ import annotations

import json
import os

from proteus.graph import witness as W
from proteus.graph.identity import RUNTIME_HASH


def test_positive_negative_cheat_identity():
    w = W.witness()
    assert w["verdict"] == "GRAPH_ISA_EXPRESSES_KEYED_MEMORY"
    assert w["rows"]["keyed"]["two_key"]["correct"] == 6 and w["rows"]["keyed"]["all_keys"]["correct"] == 16
    assert w["controls"]["one_value_exact"] == [3, 6]                 # the shelf strategy scores exactly half
    assert w["controls"]["inert_outputs_nothing"] is True
    assert w["controls"]["echo_honest"] == [0, 6] and w["controls"]["echo_leaky"] == [6, 6]
    a = W.run_episode(W.keyed_memory_manifest(), W.two_key_episode())
    assert a == W.run_episode(W.keyed_memory_manifest(), W.two_key_episode())
    assert a["dormant_nodes"] == 1                                     # the NOP spacer is dormant and free


def test_committed_witness_matches_runtime():
    if not os.path.exists(W.OUT_PATH):
        return
    committed = json.load(open(W.OUT_PATH, encoding="utf-8"))
    assert committed["runtime_hash"] == RUNTIME_HASH
    assert committed["rows"] == W.witness()["rows"]
