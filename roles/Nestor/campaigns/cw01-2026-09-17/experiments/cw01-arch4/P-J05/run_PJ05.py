"""P-J05 [T-X21; requires P-J01]: FIRST-CROSSING GENEALOGY from the stored per-generation populations of the
P-J01 plain runs (pid / op / fitness per individual). If a run crossed, the lineage around the crossing
generation is reconstructed and the route named; otherwise the route is NOT_APPLICABLE and the same
machinery describes the lineage of the final best: operators along the lineage, generations at which the
genome changed, held-out reward along the lineage every 10 generations, the coalescence (MRCA) generation
of the final population, and the best-held-by-generation curve. Computational scope: integer programs on
a bounded VM."""
from __future__ import annotations

import gzip
import json
import pathlib
import sys
import time
from collections import Counter

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import ctxevo as CE            # noqa: E402
A, L = CM.A, CM.L
PID, TID, XOR = "P-J05", "T-X21", 1
PJ01 = HERE.parent / "P-J01"


def lineage(gens, g_end, i_end):
    """Indices (g, i) of the ancestors of individual i_end at generation g_end, oldest first."""
    chain, g, i = [], g_end, i_end
    while g >= 0:
        chain.append((g, i))
        pid = gens[g][i].get("pid")
        if pid is None or g == 0:
            break
        g, i = g - 1, pid
    return chain[::-1]


def mrca_gen(gens, g_end):
    """Latest generation at which every individual of generation g_end shares a single ancestor."""
    idx = list(range(len(gens[g_end])))
    for g in range(g_end, 0, -1):
        idx = [gens[g][i].get("pid") for i in idx]
        if len(set(idx)) == 1:
            return g - 1
    return None


def job(j):
    with gzip.open(PJ01 / ("genealogy_%s_s%d.json.gz" % (j["world"], j["seed"])), "rt", encoding="utf-8") as fh:
        gens = json.load(fh)
    sets = CE.held_sets(j["world"], j["seed"], xor=XOR)
    thr = CE.THRESH[j["world"]]
    G = len(gens)
    best_held = []
    g_cross = None
    for g, pop in enumerate(gens):
        i = int(np.argmax([x["fit"] for x in pop]))
        h = CE.held_reward(pop[i]["m"], sets)
        best_held.append(round(h, 3))
        if g_cross is None and h >= thr:
            g_cross = g
    g_focus = g_cross if g_cross is not None else G - 1
    i_focus = int(np.argmax([x["fit"] for x in gens[g_focus]]))
    chain = lineage(gens, g_focus, i_focus)
    ops = [gens[g][i].get("op") for g, i in chain]
    changed = [g for (g, i), o in zip(chain, ops) if o not in (None, "copy")]
    held_along = {g: round(CE.held_reward(gens[g][i]["m"], sets), 3) for g, i in chain if g % 10 == 0 or g == g_focus}
    fit_along = [round(gens[g][i]["fit"], 3) for g, i in chain]
    window = None
    route = "NOT_APPLICABLE(no crossing)"
    if g_cross is not None:
        lo, hi = max(0, g_cross - 10), min(G - 1, g_cross + 5)
        window = []
        for g, i in chain:
            if lo <= g <= hi:
                window.append({"g": g, "op": gens[g][i].get("op"), "fit": round(gens[g][i]["fit"], 3), "held": round(CE.held_reward(gens[g][i]["m"], sets), 3), "n_instr": len(gens[g][i]["m"]["genome"]) // 4})
        # after the crossing: descendants in the +5 window are the same chain (single lineage); route from the chain
        pre = [w for w in window if w["g"] < g_cross]
        step = [w for w in window if w["g"] == g_cross][0]
        if step["op"] == "copy":
            route = "OTHER(crossing generation is a copy: held-out reward crossed on unchanged genome; a sampling crossing)"
        elif pre and pre[-1]["held"] < thr and (pre[-1]["held"] > best_held[max(0, g_cross - 11)] + 0.05):
            route = "NEUTRAL_OR_PARTIAL_PRECURSOR_THEN_BENEFICIAL"
        elif pre and pre[-1]["held"] < best_held[max(0, g_cross - 11)] - 0.05:
            route = "DELETERIOUS_INTERMEDIATE_RESCUED"
        else:
            route = "ONE_BENEFICIAL_MUTATION"
    return {"world": j["world"] + "'", "seed": j["seed"], "G": G, "g_cross": g_cross, "route": route, "best_held_by_gen": best_held[::5], "final_best_held": best_held[-1],
            "lineage_len": len(chain), "ops_along_lineage": dict(Counter(ops)), "generations_changed": len(changed), "last_change_gen": changed[-1] if changed else None,
            "held_along_lineage": held_along, "fit_along_lineage_every10": fit_along[::10], "mrca_gen_of_final": mrca_gen(gens, G - 1), "crossing_window": window,
            "n_instr_along": [len(gens[g][i]["m"]["genome"]) // 4 for g, i in chain][::20], "chain_tail_genomes": [gens[g][i]["m"] for g, i in chain[-3:]]}


def main():
    t0 = time.time()
    jobs = [{"world": w, "seed": s} for w in "ABC" for s in (1, 2, 3)]
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "requires": ["P-J01"], "scope": CM.SCOPE, "claim_type": "genealogy", "source": "P-J01 genealogy_*.json.gz (every generation, pid / op / fit)",
                         "crossing": "first generation whose best-by-training individual scores >= threshold on the 4 held-out sets", "window": "10 generations before, 5 after",
                         "routes": ["ONE_BENEFICIAL_MUTATION", "NEUTRAL_OR_PARTIAL_PRECURSOR_THEN_BENEFICIAL", "RECOMBINATION (n/a: mutation-only births)", "DELETERIOUS_INTERMEDIATE_RESCUED", "OTHER", "NOT_APPLICABLE(no crossing)"],
                         "no_crossing_readouts": "lineage of the final best: operators, generations changed, held-out along the lineage, MRCA generation of the final population",
                         "material_rule": "material if any run crossed; otherwise descriptive", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    with A.pool(9) as ex:
        rows = list(ex.map(job, jobs))
    material = any(r["g_cross"] is not None for r in rows)
    summary = {"routes": {"%s|s%d" % (r["world"], r["seed"]): r["route"] for r in rows}, "g_cross": {"%s|s%d" % (r["world"], r["seed"]): r["g_cross"] for r in rows},
               "generations_changed_of_120": [r["generations_changed"] for r in rows], "last_change_gen": [r["last_change_gen"] for r in rows], "mrca_gen_of_final": [r["mrca_gen_of_final"] for r in rows],
               "ops_along_lineage_pooled": dict(sum((Counter(r["ops_along_lineage"]) for r in rows), Counter())), "final_best_held": [r["final_best_held"] for r in rows],
               "held_along_lineage_example": rows[0]["held_along_lineage"]}
    out = {"perturbation_id": PID, "parent": TID, "summary": summary, "rows": [{k: v for k, v in r.items() if k != "chain_tail_genomes"} for r in rows], "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "lineage_tails.json").write_text(json.dumps([{"world": r["world"], "seed": r["seed"], "tail": r["chain_tail_genomes"]} for r in rows], ensure_ascii=True), encoding="utf-8")
    L.append_evidence(TID, PID, "genealogy of the P-J01 runs: crossing generations %s; routes %s; generations at which the final best's lineage changed (of 120) %s, last change %s; MRCA of the final population %s; operators along lineages %s" % (
        summary["g_cross"], sorted(set(summary["routes"].values())), summary["generations_changed_of_120"], summary["last_change_gen"], summary["mrca_gen_of_final"], summary["ops_along_lineage_pooled"]), material, detail=summary)
    print("DONE (%.0f s)" % (time.time() - t0), json.dumps(summary, default=CM.js)[:1500])


if __name__ == "__main__":
    main()
