"""P-J01 [T-X21, deformation W; runs FIRST in cycle 8]: the SUCCESSOR WORLDS A' / B' / C' - identical to
A / B / C except that regime 1 expects v XOR 1. Same evolution (N 96, tournament 3, 120 generations,
fresh episodes, 3 seeds), controls (destroyed-cue evolved; shuffled / no-cue / destroyed on B' tops),
thresholds (A .90, B .80, C .80). Every generation's population is stored with parent pointers and
operator records (gzip) for the genealogy; the crossing generation per run is found post hoc (the
best-by-training individual's held-out reward). Worlds are read SEPARATELY. Computational scope:
integer programs on a bounded VM.
"""
from __future__ import annotations

import gzip
import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import ctxworlds as CW         # noqa: E402
import ctxevo as CE            # noqa: E402
A, L = CM.A, CM.L

PID, TID, XOR = "P-J01", "T-X21", 1
SEEDS, G = (1, 2, 3), 120
STORE = {"gens": []}


def hook(g, pop, evs):
    STORE["gens"].append([{"m": x["m"], "pid": x.get("pid"), "op": x.get("op"), "anc": x["anc"], "fit": float(e["reward_per_ask"])} for x, e in zip(pop, evs)])


def job(j):
    STORE["gens"] = []
    r = CE.run_world(j["world"], j["seed"], G=G, control=j.get("control"), label="nestor.pj01", xor=XOR, on_generation=hook)
    sets = CE.held_sets(j["world"], j["seed"], j.get("control"), xor=XOR)
    # crossing generation: first g where the best-by-training individual scores >= threshold on held-out
    g_cross, best_held_by_gen = None, []
    for g, pop in enumerate(STORE["gens"]):
        i = int(np.argmax([x["fit"] for x in pop]))
        h = CE.held_reward(pop[i]["m"], sets)
        best_held_by_gen.append(round(h, 3))
        if g_cross is None and h >= CE.THRESH[j["world"]]:
            g_cross = g
    if j.get("control") is None:
        with gzip.open(HERE / ("genealogy_%s_s%d.json.gz" % (j["world"], j["seed"])), "wt", encoding="utf-8") as fh:
            json.dump(STORE["gens"], fh)
    r["g_cross"] = g_cross
    r["best_held_by_gen"] = best_held_by_gen
    return r


def main():
    t0 = time.time()
    ceil = {}
    for w in "ABC":
        acc = {k: [] for k in (("ignore_cue_best", "cue_follow", "oracle") + (("tracker",) if w == "C" else ()))}
        for i in range(200):
            c = CW.ceilings(CW.make(w, 7, i, xor=XOR), w)
            for k in acc:
                acc[k].append(c[k])
        ceil[w] = {k: {"mean": float(np.mean(v)), "p95": float(np.percentile(v, 95))} for k, v in acc.items()}
        ceil[w]["threshold"] = CE.THRESH[w]
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "deformation": "W", "scope": CM.SCOPE, "claim_type": "world-construction", "xor": XOR,
                         "worlds": {"A'": "observable regime word; regime 1 expects v XOR 1", "B'": "cue tick then PUT then bare ASK; v XOR 1", "C'": "lifetime of 16 trials, block 4, cue reliability .7; v XOR 1"},
                         "formal_ceilings_200_sets": ceil, "evolution": {"N": 96, "G": G, "tournament": 3, "births": "mutation only", "seeds": SEEDS, "episodes": "fresh every generation"},
                         "controls": {"evolved": ["B' destroyed (2 seeds)", "C' destroyed (2 seeds)"], "on_B_tops": ["shuffled", "nocue", "destroyed"]}, "genealogy": "every generation's population with pid / op / fitness (gzip, plain runs)",
                         "crossing": "per run: first generation whose best-by-training individual scores >= threshold on 4 held-out sets; a world is CROSSED if >= 2/3 seeds cross (top-4 held-out), PARTIAL if 1/3",
                         "separate_readings": {"A'": "immediate conditional computation off the identity plateau", "B'": "recruiting existing persistent state for a decision whose cue is gone", "C'": "exceeding cue-following via temporal evidence"},
                         "material_rule": "always material", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    jobs = [{"world": w, "seed": s} for w in "ABC" for s in SEEDS] + [{"world": w, "seed": s, "control": "destroyed"} for w in "BC" for s in (1, 2)]
    with A.pool(8) as ex:
        runs = list(ex.map(job, jobs))
    table = {}
    for r in runs:
        key = "%s'|%s|s%d" % (r["world"], r["control"] or "plain", r["seed"])
        table[key] = {"top4_held": float(np.mean([t["held"] for t in r["tops"][:4]])), "best_held": r["tops"][0]["held"], "pop_held": r["pop_held_mean"], "train_final": r["history"][-1], "g_cross": r["g_cross"],
                      "len": r["len_final"], "pw": r["pw_final"], "crossed": CE.crossed(r), "best_held_by_gen": r["best_held_by_gen"][::10]}
    ctl = {}
    for r in runs:
        if r["world"] == "B" and r["control"] is None:
            for c in ("shuffled", "nocue", "destroyed"):
                sets = CE.held_sets("B", r["seed"], control=c, xor=XOR)
                ctl["B'|s%d|%s" % (r["seed"], c)] = float(np.mean([CE.held_reward(t["m"], sets) for t in r["tops"][:4]]))
    crossing = {w: sum(1 for r in runs if r["world"] == w and r["control"] is None and CE.crossed(r)) for w in "ABC"}
    loophole = {w: any(CE.crossed(r, w) for r in runs if r["world"] == w and r["control"] == "destroyed") for w in "BC"}
    disposition = {w: ("LOOPHOLE" if loophole.get(w) else "CROSSED" if crossing[w] >= 2 else "PARTIAL" if crossing[w] == 1 else "NOT_CROSSED") for w in "ABC"}
    cue_follow_C = ceil["C"]["cue_follow"]["mean"]
    readings = {"A'": disposition["A"], "B'": disposition["B"], "C'": ("EXCEEDS_CUE_FOLLOW" if any(table[k]["top4_held"] >= cue_follow_C + 0.1 for k in table if k.startswith("C'|plain")) else "AT_OR_BELOW_CUE_FOLLOW") + " / " + disposition["C"]}
    out = {"perturbation_id": PID, "parent": TID, "xor": XOR, "ceilings": ceil, "thresholds": CE.THRESH, "table": table, "B_controls_on_tops": ctl, "crossing_seeds": crossing, "loophole": loophole, "disposition": disposition, "readings": readings,
           "material": True, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "tops.json").write_text(json.dumps([{k: v for k, v in r.items() if k != "history"} for r in runs], ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "successor worlds (xor 1): readings %s; top-4 held-out %s; crossing generations %s; B' controls %s" % (readings, {k: round(v["top4_held"], 3) for k, v in table.items()}, {k: v["g_cross"] for k, v in table.items()}, {k: round(v, 3) for k, v in ctl.items()}), True, detail={"readings": readings, "table": {k: {kk: vv for kk, vv in v.items() if kk != "best_held_by_gen"} for k, v in table.items()}})
    print("DONE %s (%.0f s) %s | g_cross %s" % (readings, time.time() - t0, {k: round(v["top4_held"], 3) for k, v in table.items()}, {k: v["g_cross"] for k, v in table.items()}))


if __name__ == "__main__":
    main()
