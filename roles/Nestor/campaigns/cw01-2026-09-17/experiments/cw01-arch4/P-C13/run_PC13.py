"""P-C13 (anti-gravity): the SWAMP under three decode rules.

Parent T-ARCH4/R1. The fully degenerate gen0_random parents (answered_share 0 on W0; reported apart
in C4-05 as 'a swamp by construction') are censused (12 grammar operators x 8 draws, C4-01 rules)
and walked (depth 16, 2 walkers) under modulo, trap-to-NOP and trap-to-HALT decode of new
out-of-table opcode words (parents canonicalised). Does any rule give the swamp a gradient: any
child that answers at all, any D7/D6, any walker leaving degeneracy? Descriptive.
Computational scope: integer programs on a bounded VM.
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
A, L = CM.A, CM.L

PID, TID = "P-C13", "T-ARCH4/R1"
MODES = ("modulo", "nop", "halt")
DRAWS, DEPTH, WALKERS = 8, 16, 2


def proposal_for(mode):
    def proposal(cur, rng):
        child, rec = A.GR.mutate(cur, rng, mate=None, name=None)
        child2, n = A.trap(child, mode)
        rec = dict(rec)
        rec["trapped_words"] = n
        return child2, rec
    return proposal


def job(j):
    p, mode = j["parent"], j["mode"]
    env = p["env"]
    eps = {k: A.episodes(k) for k in A.ENVS}
    pm = A.canonical(p["manifest"])
    pev = A.eval_all(pm, eps)
    rows = []
    for op in A.C1.OPERATORS:
        for d in range(1, DRAWS + 1):
            rng = A.SplitMix64(A.seed_from("c4.01.edit", A.CAMPAIGN_SEED, p["organism_id"], op, d))
            try:
                child, rec = A.GR.mutate(pm, rng, mate=None, name=op)
            except A.ManifestError:
                rows.append({"op": op, "draw": d, "D": "D0", "answers": 0.0})
                continue
            if "noop" in (rec.get("args") or {}):
                continue
            child, n = A.trap(child, mode)
            cev = A.eval_all(child, eps)
            disp = A.C1.displacement(cev[env]["_answers"], pev[env]["_answers"])
            cl = A.classify(cev, pev, disp, False, env)
            rows.append({"op": op, "draw": d, "D": cl["label"], "answers": cev[env]["answered_share"],
                         "max_reward_any_env": max(v["reward_per_ask"] for v in cev.values()), "trapped": n})
    walks = []
    for w in range(1, WALKERS + 1):
        wk = A.C5.walk(pm, p["organism_id"], w, eps[env], DEPTH, 32, proposal=proposal_for(mode))
        final = wk["archived"].get(wk["depth"])
        fev = A.eval_all(final, eps)
        walks.append({"walker": w, "depth": wk["depth"], "answers_final": fev[env]["answered_share"],
                      "max_reward_any_env": max(v["reward_per_ask"] for v in fev.values()),
                      "len_delta": CM.n_instr(final) - CM.n_instr(pm)})
    return {"parent_id": p["organism_id"], "mode": mode, "rows": rows, "walks": walks}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "scope": CM.SCOPE, "claim_type": "exploratory-descriptive",
                         "delta": "the degenerate gen0_random parents censused and walked under modulo / trap-to-NOP / trap-to-HALT decode",
                         "held_fixed": "parents' behaviour (canonicalised), operators, draws, walk rules, environments, classification",
                         "attacks": "'a swamp by construction' (C4-05) as a property of the decode rule",
                         "nonredundant": "the degenerate stratum was set aside in C4 and C5, never perturbed",
                         "measures": "share of children that answer at all; any D7/D6; max reward on any environment; walkers leaving degeneracy",
                         "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    swamp = [p for p in CM.viable_parents() if p["degenerate"]]
    jobs = [{"parent": p, "mode": m} for p in swamp for m in MODES]
    with A.pool(8) as ex:
        res = list(ex.map(job, jobs))
    summ = {}
    for m in MODES:
        rs = [r for x in res if x["mode"] == m for r in x["rows"]]
        ws = [w for x in res if x["mode"] == m for w in x["walks"]]
        c = Counter(r["D"] for r in rs)
        summ[m] = {"n_children": len(rs), "answering_share": float(np.mean([r.get("answers", 0) > 0 for r in rs])) if rs else None,
                   "D7": c["D7"], "D6": c["D6"], "D5": c["D5"], "D2": c["D2"], "classes": dict(c),
                   "max_reward_any_env_children": max([r.get("max_reward_any_env", 0.0) for r in rs] + [0.0]),
                   "walkers_answering_at_end": float(np.mean([w["answers_final"] > 0 for w in ws])) if ws else None,
                   "walker_max_reward_any_env": max([w["max_reward_any_env"] for w in ws] + [0.0]),
                   "walker_len_delta_mean": float(np.mean([w["len_delta"] for w in ws])) if ws else None}
    material = any((s["D7"] + s["D6"]) > 0 or (s["max_reward_any_env_children"] >= A.C1.FLOOR) or (s["walker_max_reward_any_env"] >= A.C1.FLOOR) for s in summ.values())
    out = {"perturbation_id": PID, "parent": TID, "n_swamp_parents": len(swamp), "summary": summ, "material": material,
           "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "swamp under decode rules: %s" % {m: {k: s[k] for k in ("answering_share", "D7", "D6", "max_reward_any_env_children", "walker_max_reward_any_env")} for m, s in summ.items()},
                      material, detail=summ)
    print("DONE material=%s (%.0f s) %s" % (material, time.time() - t0, json.dumps({m: {k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items() if k != "classes"} for m, s in summ.items()})))


if __name__ == "__main__":
    main()
