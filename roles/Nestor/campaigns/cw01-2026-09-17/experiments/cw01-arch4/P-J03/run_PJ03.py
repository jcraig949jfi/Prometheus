"""P-J03 [T-X17, deformation G; requires P-J01]: SCAFFOLD STRIPPING. No P-J01 world crossed, so the scaffolded
lineage is WITNESS-SEEDED (FLAGGED): the P-J01 A' seed-1 final population with 8 individuals replaced by
P-J02's verified XOR-1 witness (ancestor tag 999). Ladder, 2 seeds:
  stage 0  A'  (xor 1)   40 generations   scaffolded S0 | plateau P0 (same population, no witness)
  stage 1      xor 3     60 generations   S1 <- S0 | P1 <- P0
  stage 2      xor 15    60 generations   S2 <- S1 | P2 <- P1 | FRESH F2 (init walkers, 60 generations)
  removal      xor 0     60 generations   R <- S2 (regime 1 expects v: identity suffices); retest on the
                                          xor-15 held-out sets every 10 generations (persistence / decay)
  reuse        xor 5     60 generations   R' <- R | plateau P2 | fresh (a different conditional transform)
Per stage: top-4 held-out, crossing, generation of first crossing (best-by-training individual's held-out
reward per generation), share of the witness ancestry. Computational scope: integer programs on a bounded VM."""
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
import ctxevo as CE            # noqa: E402
import evolver as EV           # noqa: E402
sys.path.insert(0, str(HERE.parent / "P-J02"))
from run_PJ02 import insert    # noqa: E402
A, L = CM.A, CM.L
PID, TID = "P-J03", "T-X17"
WIT_ANC, N_WIT = 999, 8
STAGES = [("stage0_xor1", 1, 40), ("stage1_xor3", 3, 60), ("stage2_xor15", 15, 60)]
STORE = {"held": [], "wshare": []}


def make_hook(sets):
    def hook(g, pop, evs):
        i = int(np.argmax([e["reward_per_ask"] for e in evs]))
        STORE["held"].append(round(CE.held_reward(pop[i]["m"], sets), 3))
        STORE["wshare"].append(sum(1 for x in pop if x["anc"] == WIT_ANC) / len(pop))
    return hook


def stage(init, seed, xor, G, label, retest_sets=None):
    STORE["held"], STORE["wshare"] = [], []
    sets = CE.held_sets("A", seed, xor=xor)
    retest = {"held": []}
    if retest_sets is not None:
        def hook(g, pop, evs):
            i = int(np.argmax([e["reward_per_ask"] for e in evs]))
            STORE["held"].append(round(CE.held_reward(pop[i]["m"], sets), 3))
            STORE["wshare"].append(sum(1 for x in pop if x["anc"] == WIT_ANC) / len(pop))
            if g % 10 == 0 or g == G - 1:
                top = sorted(range(len(pop)), key=lambda k: -evs[k]["reward_per_ask"])[:4]
                retest["held"].append((g, round(float(np.mean([CE.held_reward(pop[k]["m"], retest_sets) for k in top])), 3)))
    else:
        hook = make_hook(sets)
    r = CE.run_world("A", seed, G=G, init=init, label=label, xor=xor, on_generation=hook)
    thr = CE.THRESH["A"]
    g_cross = next((g for g, h in enumerate(STORE["held"]) if h >= thr), None)
    return {"xor": xor, "G": G, "top4_held": float(np.mean([t["held"] for t in r["tops"][:4]])), "best_held": r["tops"][0]["held"], "crossed": CE.crossed(r), "g_cross": g_cross,
            "held_by_gen": STORE["held"][::5], "witness_share_by_gen": [round(x, 3) for x in STORE["wshare"][::5]], "final_witness_share": STORE["wshare"][-1], "retest_xor15_top4": retest["held"],
            "final_pop": r["final_pop"], "tops": r["tops"][:4]}


def base_population(seed):
    with gzip.open(HERE.parent / "P-J01" / ("genealogy_A_s%d.json.gz" % seed), "rt", encoding="utf-8") as fh:
        gens = json.load(fh)
    return [{"m": x["m"], "anc": x["anc"]} for x in gens[-1]]


def witness_genome():
    wit = json.load(open(HERE.parent / "P-J02" / "witnesses.json", encoding="utf-8"))
    w = next(x for x in wit if x["xor1"] is not None)
    tops = json.load(open(HERE.parent / "P-I01" / "tops.json", encoding="utf-8"))
    m = next(r for r in tops if r["world"] == "A" and r["control"] is None and r["seed"] == w["seed"])["tops"][w["rank"]]["m"]
    return insert(m, w["xor1"]["pos"], w["xor1"]["seq"]), w


def job(j):
    seed, chain = j["seed"], j["chain"]
    out = {"seed": seed, "chain": chain, "stages": {}}
    s15 = CE.held_sets("A", seed, xor=15)
    if chain == "fresh":
        init, _ = EV.init_population()
        out["stages"]["stage2_xor15"] = stage(init, 300 + seed, 15, 60, "nestor.pj03|fresh")
        out["stages"]["reuse_xor5"] = stage(init, 320 + seed, 5, 60, "nestor.pj03|fresh5")
        pops = {"F2": out["stages"]["stage2_xor15"]["final_pop"]}
    else:
        pop = base_population(1)
        if chain == "scaffolded":
            wm, _ = witness_genome()
            pop = pop[:-N_WIT] + [{"m": json.loads(json.dumps(wm)), "anc": WIT_ANC} for _ in range(N_WIT)]
        pops = {}
        for k, (name, xor, G) in enumerate(STAGES):
            st = stage(pop, 200 + 10 * k + seed, xor, G, "nestor.pj03|%s|%s" % (chain, name))
            out["stages"][name] = st
            pop = st["final_pop"]
        pops["S2" if chain == "scaffolded" else "P2"] = pop
        if chain == "scaffolded":
            rem = stage(pop, 240 + seed, 0, 60, "nestor.pj03|removal", retest_sets=s15)
            out["stages"]["removal_xor0"] = rem
            pops["R"] = rem["final_pop"]
            out["stages"]["reuse_xor5"] = stage(rem["final_pop"], 250 + seed, 5, 60, "nestor.pj03|reuse")
        else:
            out["stages"]["reuse_xor5"] = stage(pop, 250 + seed, 5, 60, "nestor.pj03|plateau5")
    out["pops"] = pops
    return out


def main():
    t0 = time.time()
    wm, w = witness_genome()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "requires": ["P-J01"], "scope": CM.SCOPE, "claim_type": "gateway-test", "FLAG": "WITNESS-SEEDED scaffold (no natural crossing in P-J01)",
                         "scaffold": {"witness": "P-J02 minimal xor1 witness (seed %d rank %d, %d instructions)" % (w["seed"], w["rank"], w["xor1"]["n_instr"]), "n_seeded": N_WIT, "background": "P-J01 A' seed-1 final population"},
                         "ladder": STAGES, "removal": "xor 0 for 60 generations, retest on xor-15 held-out every 10", "reuse": "xor 5 for 60 generations: post-removal vs plateau-ladder vs fresh", "seeds": [1, 2],
                         "crossing": "best-by-training individual's held-out >= .90 (generation), top-4 held-out at the end",
                         "gateway_rule": "scaffolded lineage crosses xor 15 while plateau-matched and fresh lineages stay trapped -> promote the gateway phenomenon (with the witness-seeded flag)",
                         "material_rule": "material if any lineage crosses xor 3 or xor 15, or the scaffold decays / persists measurably", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    jobs = [{"seed": s, "chain": c} for s in (1, 2) for c in ("scaffolded", "plateau", "fresh")]
    with A.pool(6) as ex:
        rows = list(ex.map(job, jobs))
    table = {}
    for r in rows:
        for name, st in r["stages"].items():
            table["%s|s%d|%s" % (r["chain"], r["seed"], name)] = {"top4_held": round(st["top4_held"], 3), "crossed": st["crossed"], "g_cross": st["g_cross"], "witness_share": round(st["final_witness_share"], 3), "retest_xor15": st["retest_xor15_top4"]}
    crossed = {c: {name: [r["stages"][name]["crossed"] for r in rows if r["chain"] == c and name in r["stages"]] for name in ("stage0_xor1", "stage1_xor3", "stage2_xor15", "removal_xor0", "reuse_xor5")} for c in ("scaffolded", "plateau", "fresh")}
    gateway = all(crossed["scaffolded"]["stage2_xor15"]) and not any(crossed["plateau"]["stage2_xor15"]) and not any(crossed["fresh"]["stage2_xor15"])
    scaffold_held = [r["stages"]["stage0_xor1"]["crossed"] for r in rows if r["chain"] == "scaffolded"]
    material = any(any(v) for c in crossed.values() for k, v in c.items() if k in ("stage1_xor3", "stage2_xor15")) or any(scaffold_held)
    summary = {"FLAG": "witness-seeded scaffold", "table": table, "crossed": crossed, "scaffold_persisted_stage0": scaffold_held, "gateway_rule_met": bool(gateway),
               "witness_share_stage0_by_gen": [r["stages"]["stage0_xor1"]["witness_share_by_gen"] for r in rows if r["chain"] == "scaffolded"],
               "reuse_xor5": {c: [round(r["stages"]["reuse_xor5"]["top4_held"], 3) for r in rows if r["chain"] == c] for c in ("scaffolded", "plateau", "fresh")}}
    out = {"perturbation_id": PID, "parent": TID, "summary": summary, "rows": [{k: v for k, v in r.items() if k != "pops"} | {"stages": {n: {k: v for k, v in s.items() if k not in ("final_pop",)} for n, s in r["stages"].items()}} for r in rows],
           "material": bool(material), "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    with gzip.open(HERE / "populations.json.gz", "wt", encoding="utf-8") as fh:
        json.dump([{"seed": r["seed"], "chain": r["chain"], "pops": r["pops"]} for r in rows], fh)
    L.append_evidence(TID, PID, "scaffold stripping (WITNESS-SEEDED, flagged): stage crossings %s; scaffold persisted through stage 0 %s; gateway rule met %s; xor-15 retest after removal %s; reuse xor 5 %s" % (
        crossed, scaffold_held, gateway, [t["retest_xor15"] for k, t in table.items() if "removal" in k], summary["reuse_xor5"]), bool(material), detail=summary)
    L.append_evidence("T-X21", PID, "cross: ladder xor1 -> xor3 -> xor15 from a witness-seeded scaffold: %s" % {c: crossed[c]["stage2_xor15"] for c in crossed}, bool(material))
    print("DONE (%.0f s)" % (time.time() - t0), json.dumps({k: v for k, v in summary.items() if k != "table"}, default=CM.js)[:1500])
    print(json.dumps(table, default=CM.js)[:2500])


if __name__ == "__main__":
    main()
