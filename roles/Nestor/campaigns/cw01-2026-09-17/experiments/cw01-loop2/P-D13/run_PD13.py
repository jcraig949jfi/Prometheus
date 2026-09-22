"""P-D13 (serendipity): e07's blind deletion inside e06's ecology.

Parent T-E06 (x T-E07). Between generations every body loses a random fraction f = 0.1 of its
units, blind to content: TAPE loses random instructions (never below 1); TREE has random internal
nodes contracted to their left child (never below a leaf). A sham arm consumes the same draws and
changes nothing. Arms: STATIC / DAMAGE / SHAM; mixed_assortative seeded .5, recombination 0.5,
80 generations, 4 attempt ids. Measures: coexistence, final TREE frequency, growth advantage,
mean structural units per label.
"""
from __future__ import annotations

import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "loop"))
import looprun as L            # noqa: E402
import seeds as S              # noqa: E402

W6 = L.import_world("cw01-e06", "world_e06")
PID, TID, F = "P-D13", "T-E06", 0.1


def growth(run, a, b):
    """world_e06.growth_advantage's formula without its latent crash (CW01-D074)."""
    import math
    h = run["history"]
    res = 1.0 / max(2.0, sum(h[0].get("n_" + lab, 0) for lab in run["labels"]))

    def odds(rec):
        x = min(max(rec.get("freq_" + a, 0.0), res), 1 - res)
        y = min(max(rec.get("freq_" + b, 0.0), res), 1 - res)
        return x / y
    return float((math.log(odds(h[-1])) - math.log(odds(h[0]))) / max(1, len(h) - 1))
MODE = {"arm": "STATIC"}
_orig_gen = W6.generation


def contract_tree(node, r, target=None, counter=None):
    """Contract the counter-th internal node to its left child (blind to content)."""
    if node[0] == "in":
        return node
    if counter[0] == target:
        counter[0] += 1
        return node[1]
    counter[0] += 1
    return (node[0], contract_tree(node[1], r, target, counter), contract_tree(node[2], r, target, counter))


def damage_pop(pop, r, apply):
    out = []
    for g in pop:
        h = dict(g)
        if g["substrate"] == "TAPE":
            prog = list(g["body"])
            k = int(round(F * len(prog)))
            picks = r.choice(len(prog), size=min(k, max(0, len(prog) - 1)), replace=False) if len(prog) > 1 else []
            if apply and len(picks):
                h["body"] = [ins for i, ins in enumerate(prog) if i not in set(int(x) for x in picks)]
        else:
            n_int = W6.tree_nodes(g["body"]) - (W6.tree_nodes(g["body"]) + 1) // 2      # internal nodes of a full binary tree
            k = int(round(F * max(n_int, 0)))
            picks = r.choice(max(n_int, 1), size=min(k, max(n_int, 0)), replace=False) if n_int > 0 else []
            if apply:
                body = g["body"]
                for t in sorted((int(x) for x in picks), reverse=True):
                    body = contract_tree(body, r, t, [0])
                h["body"] = body
        out.append(h)
    return out


def generation_w(pop, cfg, items, cross_ok, r, elite_frac):
    if MODE["arm"] != "STATIC":
        pop = damage_pop(pop, r, apply=(MODE["arm"] == "DAMAGE"))
    return _orig_gen(pop, cfg, items, cross_ok, r, elite_frac)


W6.generation = generation_w


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "claim_type": "serendipity-descriptive",
                         "delta": "blind fraction-%.1f deletion of body units between generations (TAPE: instructions; TREE: internal-node contraction), sham draw-matched; arms STATIC/DAMAGE/SHAM" % F,
                         "unchanged": "e06 world, sharing, prices, tournament 3, recombination 0.5, seeded .5, 80 generations", "attacks": "representation ecology under representation-blind damage",
                         "measures": "coexistence, final TREE frequency, growth advantage, structural units per label", "continuation": ["f dose", "damage one substrate only", "damage timing"]})
    rows = []
    for aid in ["cw01-loop2-PD13-%d" % i for i in range(4)]:
        for arm in ("STATIC", "DAMAGE", "SHAM"):
            MODE["arm"] = arm
            cfg = L.load_cfg("cw01-e06", aid)
            targets = [t for t in W6.attempt_target(cfg, S.seed) if t.get("graph") is not None]
            run = W6.evolve(cfg, "mixed_assortative", 80, 96, S.seed, "%s|%s" % (aid, arm), freq_first=0.5, target=targets)
            h = run["history"][-1]
            rec = {"aid": aid, "arm": arm, "coexist": W6.coexisting(run), "final_TREE": W6.final_frequency(run, "TREE"),
                   "growth_TREE_vs_TAPE": growth(run, "TREE", "TAPE"), "units_TREE": h.get("structural_units_TREE"), "units_TAPE": h.get("structural_units_TAPE"),
                   "score_TREE": h.get("score_TREE"), "score_TAPE": h.get("score_TAPE")}
            rows.append(rec)
            print("   %s %-6s coexist %s TREE %.3f growth %+.4f units T/P %s/%s" % (aid[-1], arm, rec["coexist"], rec["final_TREE"], rec["growth_TREE_vs_TAPE"], rec["units_TREE"], rec["units_TAPE"]), flush=True)
    summ = {a: {"coexist": sum(1 for r in rows if r["arm"] == a and r["coexist"]), "final_TREE_mean": float(np.mean([r["final_TREE"] for r in rows if r["arm"] == a])),
                "growth_mean": float(np.mean([r["growth_TREE_vs_TAPE"] for r in rows if r["arm"] == a]))} for a in ("STATIC", "DAMAGE", "SHAM")}
    sham_ok = all(abs(a["final_TREE"] - b["final_TREE"]) < 1e-9 for a, b in zip([r for r in rows if r["arm"] == "STATIC"], [r for r in rows if r["arm"] == "SHAM"]))
    material = bool(abs(summ["DAMAGE"]["growth_mean"] - summ["STATIC"]["growth_mean"]) > 0.01 or summ["DAMAGE"]["coexist"] != summ["STATIC"]["coexist"])
    out = {"perturbation_id": PID, "parent": TID, "summary": summ, "sham_identical_to_static": sham_ok, "rows": rows, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "blind damage in the ecology: %s; sham identical to static %s" % ({k: (v["coexist"], round(v["final_TREE_mean"], 3), round(v["growth_mean"], 4)) for k, v in summ.items()}, sham_ok), material, detail=summ)
    print("DONE material=%s sham_ok=%s %s (%.0f s)" % (material, sham_ok, summ, time.time() - t0))


if __name__ == "__main__":
    main()
