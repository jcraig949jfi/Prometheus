"""PROTEUS-46 (second half): the falsifier of the graph profile, run exactly as preregistered in
proteus/round2/PROTEUS-46_PREREGISTRATION.md (committed first, main eb58691fc). Nothing in the rule
below was written after seeing a number; anything that had to be is recorded in the output under
`departures`.

Output: proteus/round2/PROTEUS-46_FALSIFIER.json (the verdict file Archaeon's frontier loop reads:
`verdict`, `falsifier_status`, `neighbourhood_exhausted`, `reopen_conditions`, every number with its
floor) and PROTEUS-46_FALSIFIER.md (the same, as a table).
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from proteus.eval import keyed_memory_witness as W0  # noqa: E402
from proteus.foundry import grammar as G0  # noqa: E402
from proteus.foundry.identity import hash_obj  # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from  # noqa: E402
from proteus.graph import grammar as G1  # noqa: E402
from proteus.graph import witness as W1  # noqa: E402
from proteus.graph.identity import RUNTIME_HASH as GRAPH_RUNTIME  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH as V0_RUNTIME  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "PROTEUS-46_FALSIFIER.json")
OUT_MD = os.path.join(HERE, "PROTEUS-46_FALSIFIER.md")
K = 400
WALKS, WALK_STEPS = 200, 3
GREEDY_PATHS, GREEDY_WIDTH = 100, 50
REOPEN = ["a materially different graph topology of the same function", "a different mutation operator set or mass profile",
          "a developmental regime (growth/dormancy rules) not present in graph_grammar.v1", "a representation change beyond graph_organism.v1"]

SUBSTRATES = {
    "v0": {"runtime": V0_RUNTIME, "grammar": G0.GRAMMAR_HASH, "operators": list(G0.NAMES), "weights": list(G0.WEIGHTS),
           "parents": {"one_value": W0.manifest_for(W0.one_value_genome()), "keyed": W0.manifest_for(W0.keyed_memory_genome(48))},
           "mutate": lambda m, rng, name: G0.mutate(m, rng, None, name)[0],
           "run": lambda m, ticks: W0.run_episode(m, ticks)},
    "graph": {"runtime": GRAPH_RUNTIME, "grammar": G1.GRAMMAR_HASH, "operators": list(G1.NAMES), "weights": list(G1.WEIGHTS),
              "parents": {"one_value": W1.one_value_manifest(), "keyed": W1.keyed_memory_manifest()},
              "mutate": lambda m, rng, name: G1.mutate(m, rng, None, name)[0],
              "run": lambda m, ticks: W1.run_episode(m, ticks)},
}


def score(sub: str, m: dict) -> tuple:
    a = SUBSTRATES[sub]["run"](m, W0.two_key_episode())
    b = SUBSTRATES[sub]["run"](m, W0.all_keys_episode())
    return a["correct"], b["correct"], (tuple(a["outputs"]), tuple(b["outputs"]))


def classify(parent_two: int, two: int, same_outputs: bool) -> str:
    if two > parent_two:
        return "USEFUL"
    if two == parent_two:
        return "NEUTRAL" if same_outputs else "NEUTRAL_DIFF"
    if two == 0:
        return "DESTROYED"
    return "GRADED_DOWN"


def neighbourhood(sub: str, parent_name: str) -> dict:
    S = SUBSTRATES[sub]
    parent = S["parents"][parent_name]
    p_two, p_all, p_out = score(sub, parent)
    ph = hash_obj(parent)
    per_op, batches = {}, {"A": {}, "B": {}}
    identity = 0
    for op in S["operators"]:
        counts = {}
        for i in range(K):
            rng = SplitMix64(seed_from("p46", sub, parent_name, op, i))
            child = S["mutate"](parent, rng, op)
            if hash_obj(child) == ph:
                identity += 1
                continue
            two, _all, out = score(sub, child)
            cls = classify(p_two, two, out == p_out)
            counts[cls] = counts.get(cls, 0) + 1
            bat = "A" if i < K // 2 else "B"
            batches[bat][cls] = batches[bat].get(cls, 0) + 1
        per_op[op] = counts
    total = {}
    for c in per_op.values():
        for k, v in c.items():
            total[k] = total.get(k, 0) + v
    n = sum(total.values())

    def shares(counts):
        m = sum(counts.values()) or 1
        return {k: counts.get(k, 0) / m for k in ("USEFUL", "GRADED_DOWN", "DESTROYED", "NEUTRAL", "NEUTRAL_DIFF")}

    return {"parent_two_key": p_two, "parent_all_keys": p_all, "children": n, "identity_children_excluded": identity,
            "counts": total, "shares": shares(total), "batch_shares": {b: shares(c) for b, c in batches.items()},
            "per_operator_counts": per_op,
            "per_operator_shares": {op: shares(c) for op, c in per_op.items()}}


def walks(sub: str) -> dict:
    S = SUBSTRATES[sub]
    parent = S["parents"]["one_value"]
    reached_random = 0
    for w in range(WALKS):
        rng = SplitMix64(seed_from("p46.walk", sub, w))
        m = parent
        for _ in range(WALK_STEPS):
            op = rng.weighted(S["operators"], S["weights"])
            m = S["mutate"](m, rng, op)
        if score(sub, m)[0] == 6:
            reached_random += 1
    reached_greedy, best_seen = 0, 0
    for g in range(GREEDY_PATHS):
        rng = SplitMix64(seed_from("p46.greedy", sub, g))
        m = parent
        cur = score(sub, m)[0]
        for _ in range(WALK_STEPS):
            best, best_key = m, (cur, 0)
            for _c in range(GREEDY_WIDTH):
                op = rng.weighted(S["operators"], S["weights"])
                child = S["mutate"](m, rng, op)
                two, _all, _out = score(sub, child)
                ops = S["run"](child, W0.two_key_episode())["ops"]
                key = (two, -ops)
                if key > best_key:
                    best, best_key = child, key
            m, cur = best, best_key[0]
        best_seen = max(best_seen, cur)
        if cur == 6:
            reached_greedy += 1
    return {"random_3step_walks": WALKS, "random_reached_6": reached_random,
            "greedy_3step_paths": GREEDY_PATHS, "greedy_width": GREEDY_WIDTH, "greedy_reached_6": reached_greedy,
            "greedy_best_two_key_seen": best_seen}


def verdict(nb: dict) -> tuple:
    v0, gr = nb["v0"]["one_value"], nb["graph"]["one_value"]
    u0, ug = v0["shares"]["USEFUL"], gr["shares"]["USEFUL"]
    g0, gg = v0["shares"]["GRADED_DOWN"], gr["shares"]["GRADED_DOWN"]
    floor_u = max(abs(v0["batch_shares"]["A"]["USEFUL"] - v0["batch_shares"]["B"]["USEFUL"]),
                  abs(gr["batch_shares"]["A"]["USEFUL"] - gr["batch_shares"]["B"]["USEFUL"]))
    floor_g = max(abs(v0["batch_shares"]["A"]["GRADED_DOWN"] - v0["batch_shares"]["B"]["GRADED_DOWN"]),
                  abs(gr["batch_shares"]["A"]["GRADED_DOWN"] - gr["batch_shares"]["B"]["GRADED_DOWN"]))
    useful_cond = (ug >= 5 * u0) if u0 > 0 else (gr["counts"].get("USEFUL", 0) >= 5)
    graded_cond = gg >= 2 * g0
    exceed = (ug - u0) > floor_u and (gg - g0) > floor_g
    if useful_cond and graded_cond and exceed:
        v = "CLIFF_DOES_NOT_SURVIVE"
    elif ug <= u0 + floor_u and gg <= g0 + floor_g:
        v = "CLIFF_SURVIVES"
    else:
        v = "INDETERMINATE"
    return v, {"useful_v0": u0, "useful_graph": ug, "graded_v0": g0, "graded_graph": gg,
               "floor_useful": floor_u, "floor_graded": floor_g,
               "useful_condition": useful_cond, "graded_condition": graded_cond, "both_exceed_floor": exceed}


def render(doc: dict) -> str:
    L = ["# PROTEUS-46 falsifier -- result (preregistered in PROTEUS-46_PREREGISTRATION.md, main eb58691fc)", "",
         "verdict %s | falsifier_status %s | neighbourhood_exhausted %s" % (doc["verdict"], doc["falsifier_status"], doc["neighbourhood_exhausted"]), ""]
    r = doc["rule_evaluation"]
    L.append("    primary (one_value parent, two_key probe)     v0.4      graph     floor")
    L.append("    USEFUL share                              %8.4f  %8.4f  %8.4f" % (r["useful_v0"], r["useful_graph"], r["floor_useful"]))
    L.append("    GRADED_DOWN share                         %8.4f  %8.4f  %8.4f" % (r["graded_v0"], r["graded_graph"], r["floor_graded"]))
    L.append("    useful_condition %s  graded_condition %s  both_exceed_floor %s" % (r["useful_condition"], r["graded_condition"], r["both_exceed_floor"]))
    L.append("")
    for parent in ("one_value", "keyed"):
        L.append("## parent %s" % parent)
        L.append("    %-8s %8s %8s %8s %8s %8s %8s %6s" % ("sub", "children", "USEFUL", "GRADED", "DESTR", "NEUTRAL", "NEU_DIFF", "ident"))
        for sub in ("v0", "graph"):
            n = doc["neighbourhood"][sub][parent]
            s = n["shares"]
            L.append("    %-8s %8d %8.4f %8.4f %8.4f %8.4f %8.4f %6d" % (sub, n["children"], s["USEFUL"], s["GRADED_DOWN"], s["DESTROYED"], s["NEUTRAL"], s["NEUTRAL_DIFF"], n["identity_children_excluded"]))
        L.append("")
        for sub in ("v0", "graph"):
            L.append("    per operator, %s / %s" % (sub, parent))
            for op, s in doc["neighbourhood"][sub][parent]["per_operator_shares"].items():
                L.append("      %-22s USEFUL %.4f GRADED %.4f DESTR %.4f NEUTRAL %.4f NEU_DIFF %.4f" % (op, s["USEFUL"], s["GRADED_DOWN"], s["DESTROYED"], s["NEUTRAL"], s["NEUTRAL_DIFF"]))
            L.append("")
    L.append("## walks (secondary; never move the verdict)")
    for sub in ("v0", "graph"):
        w = doc["walks"][sub]
        L.append("    %-6s random 3-step reached 6/6: %d/%d | greedy 3-step (width %d) reached 6/6: %d/%d | best two_key seen %d" % (
            sub, w["random_reached_6"], w["random_3step_walks"], w["greedy_width"], w["greedy_reached_6"], w["greedy_3step_paths"], w["greedy_best_two_key_seen"]))
    L.append("")
    L.append("## departures from the preregistration")
    for d in doc["departures"] or ["none"]:
        L.append("- " + d)
    L.append("")
    L.append("## reopen conditions (operator ruling 2026-09-18)")
    for c in doc["reopen_conditions"]:
        L.append("- " + c)
    return "\n".join(L) + "\n"


def main() -> int:
    from proteus.workspace import assert_not_canonical
    assert_not_canonical("run falsifier_46")
    nb = {sub: {p: neighbourhood(sub, p) for p in ("one_value", "keyed")} for sub in ("v0", "graph")}
    wk = {sub: walks(sub) for sub in ("v0", "graph")}
    v, rule = verdict(nb)
    status = {"CLIFF_DOES_NOT_SURVIVE": "PASSED", "CLIFF_SURVIVES": "FALSIFIER_FAILED", "INDETERMINATE": "INDETERMINATE"}[v]
    doc = {
        "schema_version": "proteus.p46_falsifier.v1",
        "preregistration": "proteus/round2/PROTEUS-46_PREREGISTRATION.md @ main eb58691fc",
        "verdict": v, "falsifier_status": status,
        "neighbourhood_exhausted": False,
        "neighbourhood_exhausted_note": "one hand-written parent pair on one neutral probe cannot exhaust a transformation neighbourhood; retirement under condition A is NOT supported by this file",
        "reopen_conditions": REOPEN,
        "substrates": {s: {"runtime_hash": SUBSTRATES[s]["runtime"], "grammar_hash": SUBSTRATES[s]["grammar"], "operators": SUBSTRATES[s]["operators"]} for s in SUBSTRATES},
        "parameters": {"K_per_operator": K, "walks": WALKS, "walk_steps": WALK_STEPS, "greedy_paths": GREEDY_PATHS, "greedy_width": GREEDY_WIDTH},
        "rule_evaluation": rule, "neighbourhood": nb, "walks": wk,
        "departures": [],
        "limits": ["hand-written parents, not evolved organisms", "neutral probe, not W2_K2", "one graph wiring of the function"],
    }
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
        f.write("\n")
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(doc))
    print(render(doc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
