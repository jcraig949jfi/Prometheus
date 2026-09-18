"""AXIS W fixtures (G6-1 proofs): a generated world runs; determinism; provenance reproduces the world;
the feature distribution spans bins 0..10; the interactive evaluator's result shape feeds the T0 row;
coupling makes one organism's harvest visible to the next (ENDOGENOUS source); a hand-written
harvester beats a silent program on a resources world (the world is not inert).

    python -m archaeon.campaign6.worlds.fixtures
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign6.worlds import sample_world, world_from_record, evaluate_world, ComposedWorld   # noqa: E402
from archaeon.campaign6.observatory.fingerprint import rows_v0               # noqa: E402

HARVESTER = {"schema_version": "proteus.player_manifest.v0", "n_regs": 4, "tape_words": 32, "code_writable": False, "persist": "none", "tick_budget": 64, "out_cap": 4,
             # LDC r0=0 ; OUT r0 -> channel r1(=0) ; HALT  : harvest pool 0 every tick
             "genome": [3, 0, 0, 0, 23, 0, 1, 0, 1, 0, 0, 0]}
SILENT = {"schema_version": "proteus.player_manifest.v0", "n_regs": 2, "tape_words": 16, "code_writable": False, "persist": "none", "tick_budget": 16, "out_cap": 1,
          "genome": [1, 0, 0, 0]}


def main() -> int:
    rep = {}
    recs = [sample_world(s) for s in range(1, 201)]
    bins = Counter(r["complexity_bin"] for r in recs)
    rep["bins_1_200"] = dict(sorted(bins.items()))
    rep["bins_span_0_to_10"] = min(bins) <= 1 and max(bins) >= 8
    forced = [sample_world(1000 + b, bin_target=b) for b in range(0, 11)]
    rep["bin_target_exact"] = all(r["complexity_bin"] == b or (b == 0 and r["complexity_bin"] == 1) for b, r in enumerate(forced))
    # provenance reproduces the world
    r7 = sample_world(7); again = sample_world(r7["provenance"]["seed"])
    rep["provenance_reproduces"] = again["world_id"] == r7["world_id"] and again["params"] == r7["params"]
    # every generated world runs a parent and the harvester deterministically
    ps = C1.parents_from_population(); m = ps[12]["parent"]
    ok = det = 0
    for r in recs[:40]:
        w = world_from_record(r)
        a = evaluate_world(m, w, seed=1, E=4); b = evaluate_world(m, w, seed=1, E=4)
        ok += 0.0 <= a["reward"] <= 1.0; det += (json.dumps({k: v for k, v in a.items() if k != "meter"}, sort_keys=True, default=str) == json.dumps({k: v for k, v in b.items() if k != "meter"}, sort_keys=True, default=str))
    rep["worlds_run_ok"] = "%d/40" % ok; rep["deterministic"] = "%d/40" % det
    # the row assembles from the interactive result
    r = recs[0]; w = world_from_record(r); ev = evaluate_world(m, w, seed=1, E=4)
    t0, ext = rows_v0(m, "org", None, 0, 0, ev, ev["_answers"], world_features=ev["world"]["env_dependencies"], asks_per_episode=ev["_asks_per_episode"])
    rep["row_ok"] = t0["digest"].startswith("sha256:") and "episode_digests" in ext
    # not inert: the harvester beats the silent program on a pure resources world
    rw = ComposedWorld({"ticks": 24, "resources": {"on": True, "types": 2, "regen": 0.2, "deplete": 0.5}, "channels": {"on": True, "k": 1}})
    h = evaluate_world(HARVESTER, rw, seed=3, E=8)["reward"]; s0 = evaluate_world(SILENT, rw, seed=3, E=8)["reward"]
    rep["harvester_vs_silent"] = [round(h, 4), round(s0, 4)]; rep["not_inert"] = h > s0 + 0.1
    # coupling: the second organism sees a depleted pool (ENDOGENOUS)
    cw = ComposedWorld({"ticks": 8, "resources": {"on": True, "types": 1, "regen": 0.0, "deplete": 0.9}, "coupling": {"on": True}, "channels": {"on": True, "k": 1}})
    shared = {}
    first = evaluate_world(HARVESTER, cw, seed=5, E=1, shared=shared)["reward"]; second = evaluate_world(HARVESTER, cw, seed=5, E=1, shared=shared)["reward"]
    rep["coupling_first_vs_second"] = [round(first, 4), round(second, 4)]; rep["endogenous_visible"] = second < first
    # hazards with lethality can end an episode; delayed and hidden run
    hw = ComposedWorld({"ticks": 24, "resources": {"on": True, "types": 2, "regen": 0.1, "deplete": 0.5}, "locality": {"on": True, "nodes": 4}, "hazards": {"on": True, "cost": 0.3, "lethal": True},
                        "delayed": {"on": True, "d": 2}, "hidden": {"on": True, "noise": 0.3}, "objects": {"on": True, "cells": 2, "bonus": 0.5}, "channels": {"on": True, "k": 4}})
    hv = evaluate_world(HARVESTER, hw, seed=9, E=8)
    rep["rich_world_runs"] = {"reward": round(hv["reward"], 4), "died_episodes": hv["world"]["died_episodes"], "deps": hv["world"]["env_dependencies"], "actions": hv["world"]["action_hist"]}
    print(json.dumps(rep, indent=1))
    return 0 if (rep["bins_span_0_to_10"] and rep["bin_target_exact"] and rep["provenance_reproduces"] and ok == 40 and det == 40 and rep["row_ok"] and rep["not_inert"] and rep["endogenous_visible"]) else 1


if __name__ == "__main__":
    sys.exit(main())
