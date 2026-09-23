"""P-I04 [T-X20 x T-X17 x T-X21, deformation X]: RECOMBINATION UNDER CONTEXT PRESSURE - the evolver with
the grammar's splice operator at rate .3 vs mutation only, from a mixed population of geometry
representatives, in worlds B and C; every NEW response surface archived with genome, generation and
reward before selection can remove it; NEW surfaces with competence followed at once (cue causality
and state corruption). Computational scope: integer programs on a bounded VM.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
from collections import Counter

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import manifold as MF          # noqa: E402
import ctxworlds as CW         # noqa: E402
import ctxevo as CE            # noqa: E402
import evolver as EV           # noqa: E402
A, L = CM.A, CM.L
sys.path.insert(0, str(HERE.parent / "P-I02"))
from run_PI02 import cue_causality, eval_reg   # noqa: E402

PID, TID = "P-I04", "T-X20"
SHAPES, WORLDS, SEEDS, G, EVERY = (0, 4, 5, 1, 3), ("B", "C"), (1, 2), 100, 5
ARCHIVE = {"new": [], "shapes": [], "donors": None}


def mixed_init():
    reps = [dict(r) for c in SHAPES for r in MF.representatives(c, 8)]
    return [{"m": A.canonical(reps[i % len(reps)]["manifest"]), "anc": i % len(reps), "anc_parent": None, "anc_stratum": None, "anc_walker": None} for i in range(EV.N)], [MF.rows()[r["organism_id"]]["vector"] for r in reps]


def hook(world, seed, arm):
    def f(g, pop, evs):
        if g % EVERY:
            return
        fit = np.array([e["reward_per_ask"] for e in evs])
        idx = np.argsort(-fit)[:8]
        shapes = Counter()
        for i in idx:
            v = MF.curve(pop[int(i)]["m"])[0]
            if not all(x == x for x in v):
                shapes["silent"] += 1
                continue
            k, d = MF.nearest(v)
            dd = min(MF.dist(v, dv) for dv in ARCHIVE["donors"])
            if d > 0.3 and dd > 0.3:
                shapes["NEW"] += 1
                ARCHIVE["new"].append({"world": world, "seed": seed, "arm": arm, "gen": g, "train_reward": float(fit[int(i)]), "vector": v, "m": pop[int(i)]["m"], "d_known": d, "d_donor": dd})
            else:
                shapes[MF.SHAPE[k]] += 1
        ARCHIVE["shapes"].append({"world": world, "seed": seed, "arm": arm, "gen": g, "shapes": dict(shapes)})
    return f


def job(j):
    init, donors = mixed_init()
    ARCHIVE["new"], ARCHIVE["shapes"], ARCHIVE["donors"] = [], [], donors
    r = CE.run_world(j["world"], j["seed"], G=G, init=init, label="nestor.pi04|" + j["arm"], mate_rate=(0.3 if j["arm"] == "splice" else 0.0), on_generation=hook(j["world"], j["seed"], j["arm"]))
    sets = CE.held_sets(j["world"], j["seed"])
    followed = []
    for n in ARCHIVE["new"]:
        n["held"] = CE.held_reward(n["m"], sets)
        if n["held"] >= CE.THRESH[j["world"]]:
            cc = cue_causality(n["m"], j["world"], sets)
            rec = [eval_reg(n["m"], sets[0], clear_at={(0, 3 * 4)})["reward"], eval_reg(n["m"], sets[0])["reward"]] if j["world"] == "C" else None
            followed.append({"gen": n["gen"], "held": n["held"], "cue_causality": cc, "reward_cleared_vs_base": rec, "vector": n["vector"], "m": n["m"]})
    top_shapes = Counter()
    for t in r["tops"][:8]:
        v = MF.curve(t["m"])[0]
        top_shapes["silent" if not all(x == x for x in v) else ("NEW" if MF.nearest(v)[1] > 0.3 else MF.SHAPE[MF.nearest(v)[0]])] += 1
    return {"world": j["world"], "seed": j["seed"], "arm": j["arm"], "top4_held": float(np.mean([t["held"] for t in r["tops"][:4]])), "best_held": r["tops"][0]["held"], "crossed": CE.crossed(r), "top_shapes": dict(top_shapes),
            "n_new": len(ARCHIVE["new"]), "new": [{k: v for k, v in n.items()} for n in ARCHIVE["new"]], "followed": followed, "shape_log": ARCHIVE["shapes"], "tops": r["tops"][:4]}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "co_parents": ["T-X17", "T-X21"], "deformation": "X", "scope": CM.SCOPE, "claim_type": "recombination-under-selection",
                         "init": "8 representatives of each of start-anchored, periodic, ask-time, schedule, immune (40), cycled to 96", "arms": {"splice": "grammar 'splice' with a tournament mate at rate .3", "mutation": "mutation only"}, "worlds": WORLDS, "seeds": SEEDS, "G": G,
                         "archive": "every %d generations the top-8 curves; NEW = > .3 from every P-F02 centroid and from every donor vector; genome, generation, train reward kept; NEW with held-out reward >= threshold followed (cue causality; state corruption in C)" % EVERY,
                         "readouts": "held-out reward, crossing, top shapes, NEW counts per arm; followed surfaces", "material_rule": "any followed NEW surface, or the splice arm crosses where mutation does not (or vice versa)", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    jobs = [{"world": w, "seed": s, "arm": arm} for w in WORLDS for s in SEEDS for arm in ("splice", "mutation")]
    with A.pool(8) as ex:
        runs = list(ex.map(job, jobs))
    table = {"%s|%s|s%d" % (r["world"], r["arm"], r["seed"]): {"top4_held": r["top4_held"], "best": r["best_held"], "crossed": r["crossed"], "top_shapes": r["top_shapes"], "n_new": r["n_new"], "n_followed": len(r["followed"])} for r in runs}
    diff = any(any(r["crossed"] for r in runs if r["world"] == w and r["arm"] == "splice") != any(r["crossed"] for r in runs if r["world"] == w and r["arm"] == "mutation") for w in WORLDS)
    followed = [f for r in runs for f in r["followed"]]
    material = bool(followed or diff)
    out = {"perturbation_id": PID, "parent": TID, "table": table, "n_new_total": sum(r["n_new"] for r in runs), "n_followed": len(followed), "followed": [{k: v for k, v in f.items() if k != "m"} for f in followed], "arms_differ_in_crossing": diff, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "archive.json").write_text(json.dumps([{k: v for k, v in r.items() if k not in ("tops",)} for r in runs], ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "recombination under pressure: %s; NEW surfaces %d (followed %d); arms differ in crossing %s" % ({k: (round(v["top4_held"], 3), v["crossed"], v["top_shapes"], v["n_new"]) for k, v in table.items()}, out["n_new_total"], len(followed), diff), material, detail={"table": table})
    for tid in ("T-X17", "T-X21"):
        L.append_evidence(tid, PID, "cross: splice vs mutation crossing %s; NEW %d" % ({k: v["crossed"] for k, v in table.items()}, out["n_new_total"]), material)
    print("DONE material=%s (%.0f s) %s new %d followed %d" % (material, time.time() - t0, {k: (round(v["top4_held"], 2), v["crossed"]) for k, v in table.items()}, out["n_new_total"], len(followed)))


if __name__ == "__main__":
    main()
