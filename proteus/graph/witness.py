"""Expressiveness witness on the GRAPH substrate (PROTEUS-46, first half): the same keyed two-value
memory the v0 witness built (proteus/eval/keyed_memory_witness.py), now as connectivity.

Same neutral probe, same controls: two input channels (key; value-or-empty), one output channel,
keys 0..15. Correct behaviour: on an ASK for key k, output the last value PUT under k. The
one-value control (store to a fixed slot) must score exactly half on the two-key probe -- the
shelf strategy -- and the echo cheat must score 0 unless the probe leaks. Not a world; W2_K2 not
read. What it establishes: the graph ISA expresses the same class at a comparable cost, so the
two substrates can be compared on SEARCH geometry (PROTEUS-46 second half) with expressiveness
held equal.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from proteus.foundry.prng import SplitMix64  # noqa: E402
from proteus.graph.identity import RUNTIME_HASH, hash_obj  # noqa: E402
from proteus.graph.vm import (CONST, HALT, ID, IN, INQ, LD, NOP, OUT, ROUTE, SCHEMA, ST, GraphMeter,  # noqa: E402
                              GraphPlayer, canonicalize)

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "KEYED_MEMORY_WITNESS_GRAPH.json")
MAX_KEY = 15


def _node(kind, *params, persist=False):
    return {"kind": kind, "params": list(params), "persist": persist}


def _manifest(nodes, data_edges, control_edges, entry=0, state_words=16):
    return canonicalize({"schema_version": SCHEMA, "nodes": nodes, "data_edges": data_edges,
                         "control_edges": control_edges, "entry": entry, "state_words": state_words,
                         "tick_budget": 16, "out_cap": 1, "call_depth_max": 0, "persist_state": True})


def keyed_memory_manifest() -> dict:
    nodes = [_node(CONST, 1),   # 0  channel 1
             _node(INQ),        # 1  unread on ch1 (value present?)
             _node(CONST, 0),   # 2  channel 0 / output channel
             _node(IN),         # 3  key from ch0
             _node(NOP),        # 4  (spacer; dormant)
             _node(ROUTE),      # 5  value present -> port 0 (PUT) else port 1 (ASK)
             _node(IN),         # 6  value from ch1
             _node(ST),         # 7  state[key] = value
             _node(HALT),       # 8
             _node(LD),         # 9  state[key]
             _node(OUT),        # 10 out ch0 <- value
             _node(HALT)]       # 11
    data = [[0, 1, 0], [2, 3, 0], [1, 5, 0], [0, 6, 0], [3, 7, 0], [6, 7, 1], [3, 9, 0], [9, 10, 0], [2, 10, 1]]
    control = [[0, 0, 1], [1, 0, 2], [2, 0, 3], [3, 0, 5], [5, 0, 6], [6, 0, 7], [7, 0, 8], [5, 1, 9], [9, 0, 10], [10, 0, 11]]
    return _manifest(nodes, data, control)


def one_value_manifest() -> dict:
    """Store every value to slot 0 and answer every ASK from slot 0 (the shelf strategy)."""
    nodes = [_node(CONST, 1), _node(INQ), _node(CONST, 0), _node(IN), _node(NOP), _node(ROUTE),
             _node(IN), _node(ST), _node(HALT), _node(LD), _node(OUT), _node(HALT)]
    data = [[0, 1, 0], [2, 3, 0], [1, 5, 0], [0, 6, 0], [2, 7, 0], [6, 7, 1], [2, 9, 0], [9, 10, 0], [2, 10, 1]]
    control = [[0, 0, 1], [1, 0, 2], [2, 0, 3], [3, 0, 5], [5, 0, 6], [6, 0, 7], [7, 0, 8], [5, 1, 9], [9, 0, 10], [10, 0, 11]]
    return _manifest(nodes, data, control)


def echo_manifest() -> dict:
    """Output whatever is on the value channel (the cheat): 0 under the honest probe."""
    nodes = [_node(CONST, 1), _node(IN), _node(CONST, 0), _node(OUT), _node(HALT)]
    data = [[0, 1, 0], [1, 3, 0], [2, 3, 1]]
    control = [[0, 0, 1], [1, 0, 2], [2, 0, 3], [3, 0, 4]]
    return _manifest(nodes, data, control)


def inert_manifest() -> dict:
    return _manifest([_node(NOP) for _ in range(12)], [], [[i, 0, i + 1] for i in range(11)])


def run_episode(manifest, ticks, leak=False, seed=0):
    p = GraphPlayer(manifest)
    st = p.fresh_state()
    rng = SplitMix64(seed)
    meter = GraphMeter(p.n)
    outs, correct, total = [], 0, 0
    for t in ticks:
        if t[0] == "PUT":
            inputs = [[t[1]], [t[2]]]
        else:
            inputs = [[t[1]], [t[2]] if leak else []]
        o, _status = p.run_tick(st, inputs, 1, rng, meter=meter)
        got = o[0][0] if o and o[0] else None
        outs.append(got)
        if t[0] == "ASK":
            total += 1
            correct += 1 if got == t[2] else 0
        st["ticks"] += 1
    md = meter.as_dict()
    return {"outputs": outs, "asks": total, "correct": correct, "ops": md["ops"],
            "ops_by_category": md["ops_by_category"], "nodes_executed": md["nodes_executed"],
            "dormant_nodes": len(p.dormant), "statuses": md["statuses"]}


def two_key_episode():
    return [("PUT", 3, 1001), ("PUT", 9, 2002), ("ASK", 3, 1001), ("ASK", 9, 2002), ("PUT", 3, 3003),
            ("ASK", 3, 3003), ("ASK", 9, 2002), ("ASK", 9, 2002), ("ASK", 3, 3003)]


def all_keys_episode():
    return [("PUT", k, 5000 + 7 * k) for k in range(MAX_KEY + 1)] + \
           [("ASK", k, 5000 + 7 * k) for k in reversed(range(MAX_KEY + 1))]


def witness() -> dict:
    rows = {}
    for name, m in (("keyed", keyed_memory_manifest()), ("one_value", one_value_manifest()),
                    ("inert", inert_manifest()), ("echo", echo_manifest())):
        rows[name] = {"organism_id": hash_obj(m), "n_nodes": len(m["nodes"]),
                      "two_key": run_episode(m, two_key_episode()), "all_keys": run_episode(m, all_keys_episode())}
    rows["echo"]["two_key_leaky_probe"] = run_episode(echo_manifest(), two_key_episode(), leak=True)
    k, o, e = rows["keyed"], rows["one_value"], rows["echo"]
    verdict = ("GRAPH_ISA_EXPRESSES_KEYED_MEMORY"
               if k["two_key"]["correct"] == 6 and k["all_keys"]["correct"] == 16 else "WITNESS_FAILED")
    return {
        "schema_version": "proteus.keyed_memory_witness_graph.v1",
        "runtime_hash": RUNTIME_HASH,
        "verdict": verdict,
        "controls": {"one_value_exact": [o["two_key"]["correct"], 6], "inert_outputs_nothing":
                     all(v is None for v in rows["inert"]["two_key"]["outputs"]),
                     "echo_honest": [e["two_key"]["correct"], 6], "echo_leaky": [e["two_key_leaky_probe"]["correct"], 6]},
        "cost_vs_v0": {"graph_keyed_ops_two_key": k["two_key"]["ops"], "v0_keyed_ops_two_key": 81,
                       "graph_nodes": k["n_nodes"], "v0_instructions": 12},
        "rows": rows,
    }


def main() -> int:
    from proteus.workspace import assert_not_canonical
    assert_not_canonical("run graph witness")
    w = witness()
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(w, f, indent=1, sort_keys=True)
        f.write("\n")
    print(OUT_PATH)
    print("verdict:", w["verdict"], "| controls:", json.dumps(w["controls"]), "| cost:", json.dumps(w["cost_vs_v0"]))
    return 0 if w["verdict"].endswith("KEYED_MEMORY") else 1


if __name__ == "__main__":
    sys.exit(main())
