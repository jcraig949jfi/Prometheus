"""P-J07 [T-X21; anti-gravity; requires P-J02]: INVASION OF A SINGLE WITNESS. The identity-plateau population
of A' (P-J01 A' seed-1 final population, 95 individuals) plus ONE verified XOR-1 witness (P-J02's minimal
witness on the P-I01 genome; tagged ancestor 999) evolves in A' for 40 generations under (i) the P-J01
regime (tournament 3, 16 asks per generation), (ii) 64 asks per generation (less fitness noise), (iii)
tournament 2, 4 seeds each. Every birth is a mutated copy (the grammar never copies faithfully), so the
witness lineage survives only if its descendants keep the function: tracked = lineage frequency per
generation, its mean fitness, fixation / loss, generations to fixation, and the final held-out reward.
If a beneficial one-edit mutant is lost by noise, drift or mutational load, P-J01's failure includes a
SEARCH FAILURE of the selection dynamics, not only of encoding distance. Computational scope: integer
programs on a bounded VM."""
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
sys.path.insert(0, str(HERE.parent / "P-J02"))
from run_PJ02 import insert    # noqa: E402
A, L = CM.A, CM.L
PID, TID, XOR, G = "P-J07", "T-X21", 1, 40
WIT_ANC = 999
STORE = {"freq": [], "wfit": [], "pfit": []}


def hook(g, pop, evs):
    w = [e["reward_per_ask"] for x, e in zip(pop, evs) if x["anc"] == WIT_ANC]
    p = [e["reward_per_ask"] for x, e in zip(pop, evs) if x["anc"] != WIT_ANC]
    STORE["freq"].append(len(w) / len(pop))
    STORE["wfit"].append(float(np.mean(w)) if w else None)
    STORE["pfit"].append(float(np.mean(p)) if p else None)


def plateau_population(seed=1):
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
    STORE["freq"], STORE["wfit"], STORE["pfit"] = [], [], []
    pop = plateau_population()[:95]
    wm, _ = witness_genome()
    init = pop + [{"m": wm, "anc": WIT_ANC}]
    kw = {"n": j["asks"]} if j["asks"] != 16 else {}
    r = CE.run_world("A", 100 + j["seed"], G=G, init=init, label="nestor.pj07|%s" % j["arm"], xor=XOR, on_generation=hook, k_t=j["kt"], **kw)
    freq = STORE["freq"]
    g_fix = next((g for g, f in enumerate(freq) if f >= 1.0), None)
    g_loss = next((g for g, f in enumerate(freq) if f == 0.0), None)
    final_w = sum(1 for x in r["final_pop"] if x["anc"] == WIT_ANC) / len(r["final_pop"])
    return {"arm": j["arm"], "seed": j["seed"], "asks": j["asks"], "kt": j["kt"], "freq": [round(f, 3) for f in freq], "witness_fit": [round(f, 3) if f is not None else None for f in STORE["wfit"]],
            "plateau_fit": [round(f, 3) if f is not None else None for f in STORE["pfit"]], "g_fixation": g_fix, "g_loss": g_loss, "final_witness_share": final_w, "top4_held": float(np.mean([t["held"] for t in r["tops"][:4]])),
            "pop_held": r["pop_held_mean"], "crossed": CE.crossed(r), "max_freq": max(freq), "outcome": ("FIXED" if g_fix is not None and freq[-1] >= 0.9 else "LOST" if freq[-1] == 0.0 else "SEGREGATING")}


def main():
    t0 = time.time()
    wm, w = witness_genome()
    sets = CE.held_sets("A", 1, xor=XOR)
    w_held = CE.held_reward(wm, sets)
    arms = [("pj01_regime", 16, 3), ("asks64", 64, 3), ("tournament2", 16, 2)]
    jobs = [{"arm": a, "asks": n, "kt": k, "seed": s} for a, n, k in arms for s in (1, 2, 3, 4)]
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "requires": ["P-J02"], "scope": CM.SCOPE, "claim_type": "anti-gravity", "background": "P-J01 A' seed-1 final population (95) + 1 witness (anc 999)",
                         "witness": {"source": "P-J02 minimal xor1 witness on P-I01 genome (seed %d, rank %d)" % (w["seed"], w["rank"]), "n_instr": w["xor1"]["n_instr"], "held": w_held}, "G": G, "arms": arms, "seeds": [1, 2, 3, 4],
                         "readouts": "witness-lineage frequency per generation, mean fitness of the lineage vs plateau, fixation (freq 1.0) / loss, final held-out",
                         "reading": "LOST under selection despite fitness 1.0 vs .5 = search failure of the dynamics (mutational load / noise); FIXED = the dynamics are not the obstruction, the encoding distance is",
                         "material_rule": "always material", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    with A.pool(12) as ex:
        rows = list(ex.map(job, jobs))
    summary = {}
    for a, _, _ in arms:
        rs = [r for r in rows if r["arm"] == a]
        summary[a] = {"outcomes": [r["outcome"] for r in rs], "g_fixation": [r["g_fixation"] for r in rs], "g_loss": [r["g_loss"] for r in rs], "max_freq": [r["max_freq"] for r in rs], "final_share": [round(r["final_witness_share"], 3) for r in rs],
                      "top4_held": [round(r["top4_held"], 3) for r in rs], "crossed": [r["crossed"] for r in rs], "freq_curve_s1": rs[0]["freq"][::4], "witness_fit_s1": rs[0]["witness_fit"][::4]}
    out = {"perturbation_id": PID, "parent": TID, "witness_held": w_held, "summary": summary, "rows": rows, "material": True, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "invasion of a single XOR-1 witness (held %.3f) into the A' plateau population: %s" % (w_held, {a: {k: v for k, v in d.items() if k in ("outcomes", "g_fixation", "g_loss", "max_freq", "top4_held", "crossed")} for a, d in summary.items()}), True, detail=summary)
    L.append_evidence("T-R01", PID, "cross: selection dynamics given a beneficial mutant: %s" % {a: d["outcomes"] for a, d in summary.items()}, True)
    print("DONE (%.0f s)" % (time.time() - t0), json.dumps(summary, default=CM.js)[:1500])


if __name__ == "__main__":
    main()
