"""P-A10 (anti-gravity): neutral label fixation time vs population structure in e06's world.

Parent T-X01 (<- e02, e06). Delta: e06's control A (two labels on ONE substrate, no
representational difference) run under four population structures: tournament size 3 (as
e06 ran), tournament size 2, tournament size 1 (pure drift: a random parent), and a 4-deme
island model (24 per deme, generation() per deme, one random migrant swapped between
consecutive demes per generation). 4 seeds each, 80 generations. Ruler: the generation at
which one label reaches frequency 0 or 1 (fixation), or 80+ if both persist, against the
neutral expectation ~N = 96. Unchanged: world, substrate, mutation, sharing, prices.
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
PID, TID, AID = "P-A10", "T-X01", "cw01-loop1-PA10"
N_ORG, GENS, N_SEED = 96, 80, 4
STRUCTURES = ("tournament3", "tournament2", "tournament1", "islands4")


def control_a_arm(cfg):
    for name, a in cfg["arms"].items():
        if name.startswith("_"):
            continue
        subs = a.get("substrates", [])
        if len(subs) == 2 and subs[0] == subs[1]:
            return name
    raise RuntimeError("no control-A arm (two labels on one substrate) in e06 WORLD.json")


def run(cfg, arm, structure, seed_tag):
    labels = W6._labels(cfg, arm)
    r = np.random.Generator(np.random.PCG64(S.seed(AID, "evo|%s|%s" % (structure, seed_tag), 0)))
    pop = W6.initial_population(cfg, arm, r, N_ORG, 0.5)
    target = W6.attempt_target(cfg, S.seed)
    fix_gen, traj = None, []
    for gen in range(GENS):
        srng = np.random.Generator(np.random.PCG64(S.seed(AID, "stream|%s|%s|%d" % (structure, seed_tag, gen), 0)))
        items = W6.make_items(cfg, srng, target)
        if structure == "islands4":
            demes = [pop[i::4] for i in range(4)]
            new = []
            for d in demes:
                kids, _, _, _ = W6.generation(d, cfg, items, False, r, cfg["ecology"]["elite_fraction"])
                new.append(kids)
            for i in range(4):                                   # one migrant swapped between consecutive demes
                j = (i + 1) % 4
                a, b = int(r.integers(0, len(new[i]))), int(r.integers(0, len(new[j])))
                new[i][a], new[j][b] = new[j][b], new[i][a]
            pop = [g for d in new for g in d]
        else:
            pop, _, _, _ = W6.generation(pop, cfg, items, False, r, cfg["ecology"]["elite_fraction"])
        f = sum(1 for g in pop if g["label"] == labels[0]) / float(len(pop))
        traj.append(f)
        if fix_gen is None and (f == 0.0 or f == 1.0):
            fix_gen = gen
    return {"structure": structure, "seed": seed_tag, "fixation_gen": fix_gen, "final_freq": traj[-1],
            "coexist_at_end": bool(0.0 < traj[-1] < 1.0), "traj_every10": [round(x, 3) for x in traj[::10]]}


def main():
    t0 = time.time()
    cfg = L.load_cfg("cw01-e06", AID)
    arm = control_a_arm(cfg)
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "claim_type": "exploratory-descriptive",
                         "delta": "population structure: %s on e06 control A (%s)" % (STRUCTURES, arm), "seeds": N_SEED, "generations": GENS,
                         "unchanged": "world, substrate, mutation, sharing, prices, no recombination across labels differences (labels are neutral)",
                         "attacks": "the 26-vs-96 generation hitchhiking floor",
                         "statistic": "fixation generation per structure (80+ if both labels persist); neutral expectation ~ N = 96",
                         "decision": "descriptive; a structure whose median fixation time is >= 2x tournament3's is material"})
    rows = []
    for structure in STRUCTURES:
        base = cfg
        if structure == "tournament2":
            base = L.load_cfg("cw01-e06", AID); base["ecology"]["tournament_size"] = 2
        elif structure == "tournament1":
            base = L.load_cfg("cw01-e06", AID); base["ecology"]["tournament_size"] = 1
        for s in range(N_SEED):
            t1 = time.time()
            rec = run(base, arm, structure, "s%d" % s)
            rec["wall_s"] = round(time.time() - t1, 1)
            rows.append(rec)
            print("   %-12s s%d  fixation %s  final %.3f  coexist %s  (%.0f s)" % (structure, s, rec["fixation_gen"], rec["final_freq"], rec["coexist_at_end"], rec["wall_s"]), flush=True)
    summary = {}
    for structure in STRUCTURES:
        v = [r["fixation_gen"] if r["fixation_gen"] is not None else GENS for r in rows if r["structure"] == structure]
        summary[structure] = {"median_fixation": float(np.median(v)), "n_coexist": sum(1 for r in rows if r["structure"] == structure and r["coexist_at_end"])}
    base_med = summary["tournament3"]["median_fixation"]
    material = any(summary[s]["median_fixation"] >= 2 * base_med for s in STRUCTURES if s != "tournament3")
    res = {"perturbation_id": PID, "parent": TID, "arm": arm, "rows": rows, "summary": summary, "material": material,
           "neutral_expectation_generations": N_ORG, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, res, ph)
    L.append_evidence(TID, PID, "fixation vs structure: %s (neutral ~%d)" % ({k: v["median_fixation"] for k, v in summary.items()}, N_ORG), material, detail=summary,
                      state="ACTIVE", state_reason="the floor is now a measured function of structure; next: apply the slowest structure inside an ecology run")
    print("DONE material=%s %s (%.0f s)" % (material, summary, time.time() - t0))


if __name__ == "__main__":
    main()
