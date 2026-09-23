"""P-C16 (serendipity, compound by design): trap-to-NOP decode AND length-balanced proposal weights
in one neutral walk.

Parent T-ARCH4/M1. Three arms on canonicalised viable parents, 2 walkers each, depth 16: MODULO
(frozen weights), R2 (trap-to-NOP, frozen weights), R2+BALANCED (trap-to-NOP; operator weights
rescaled so insertion+duplication mass equals deletion+splice mass, other operators untouched and
the vector renormalised). Measures length delta, acceptance, exaptation, structural diversity at
depth 16. Asks whether 'neutrality + length' (C4-08) is one phenomenon or two.
Computational scope: integer programs on a bounded VM.
"""
from __future__ import annotations

import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
A, L = CM.A, CM.L

PID, TID = "P-C16", "T-ARCH4/M1"
DEPTH, WALKERS = 16, 2
ARMS = ("modulo", "r2", "r2_balanced")


def balanced_weights():
    names, w = list(A.GR.NAMES), list(A.GR.WEIGHTS)
    grow = sum(w[names.index(x)] for x in ("insertion", "duplication"))
    shrink = sum(w[names.index(x)] for x in ("deletion", "splice"))
    target = 0.5 * (grow + shrink)
    for x in ("insertion", "duplication"):
        w[names.index(x)] *= target / grow
    for x in ("deletion", "splice"):
        w[names.index(x)] *= target / shrink
    s = sum(w)
    return names, [v / s for v in w]


def proposal_for(arm):
    names, wts = balanced_weights()
    cum = np.cumsum(wts)

    def proposal(cur, rng):
        if arm == "r2_balanced":
            u = (rng.next_u32() % 1_000_000) / 1_000_000.0
            name = names[int(np.searchsorted(cum, u))]
            child, rec = A.GR.mutate(cur, rng, mate=None, name=name)
        else:
            child, rec = A.GR.mutate(cur, rng, mate=None, name=None)
        if arm != "modulo":
            child, n = A.trap(child, "nop")
            rec = dict(rec)
            rec["trapped_words"] = n
        return child, rec
    return proposal


def job(j):
    p, arm = j["parent"], j["arm"]
    env = p["env"]
    eps = {k: A.episodes(k) for k in A.ENVS}
    pm = A.canonical(p["manifest"])
    pev = A.eval_all(pm, eps)
    others = [o for o in A.OTHER_ENVS if o != env]
    out = []
    for w in range(1, WALKERS + 1):
        wk = A.C5.walk(pm, p["organism_id"], w, eps[env], DEPTH, 32, proposal=proposal_for(arm))
        final = wk["archived"].get(wk["depth"])
        fev = A.eval_all(final, eps)
        ex = [o for o in others if fev[o]["reward_per_ask"] >= pev[o]["reward_per_ask"] + A.C1.BAND and fev[o]["reward_per_ask"] >= A.C1.FLOOR]
        props = sum(s["proposals"] for s in wk["steps"])
        out.append({"walker": w, "depth": wk["depth"], "acceptance": (wk["depth"] / props) if props else None,
                    "len_delta": CM.n_instr(final) - CM.n_instr(pm), "exaptive": bool(ex), "manifest": final})
    return {"parent_id": p["organism_id"], "arm": arm, "walkers": out}


def main():
    t0 = time.time()
    names, wts = balanced_weights()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "scope": CM.SCOPE, "claim_type": "serendipity-compound-descriptive",
                         "delta": "arms modulo / r2 / r2_balanced (trap-to-NOP + length-balanced operator weights)", "balanced_weights": dict(zip(names, [round(x, 4) for x in wts])),
                         "held_fixed": "walk rules, parents' behaviour, seeds, environments", "attacks": "whether neutrality and length growth are one phenomenon (C4-08)",
                         "nonredundant": "compound by design in a protected slot", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    jobs = [{"parent": p, "arm": a} for p in parents for a in ARMS]
    with A.pool(8) as ex:
        res = list(ex.map(job, jobs))
    summ, per = {}, {}
    for a in ARMS:
        ws = [w for r in res if r["arm"] == a for w in r["walkers"]]
        summ[a] = {"n": len(ws), "connected_16": float(np.mean([w["depth"] == DEPTH for w in ws])),
                   "acceptance_mean": float(np.nanmean([w["acceptance"] if w["acceptance"] is not None else np.nan for w in ws])),
                   "len_delta_mean": float(np.mean([w["len_delta"] for w in ws])), "exaptation_rate": float(np.mean([w["exaptive"] for w in ws])),
                   "structural_diversity_16": CM.struct_div([w["manifest"] for w in ws][:120])}
        for r in res:
            if r["arm"] == a:
                per.setdefault(r["parent_id"], {})[a] = float(np.mean([w["len_delta"] for w in r["walkers"]]))
    contrasts = {"len_r2_minus_modulo": CM.paired_signflip([v["r2"] - v["modulo"] for v in per.values()]),
                 "len_r2bal_minus_r2": CM.paired_signflip([v["r2_balanced"] - v["r2"] for v in per.values()])}
    material = any(c and (c["above_p95"] or c["below_p05"]) for c in contrasts.values())
    out = {"perturbation_id": PID, "parent": TID, "summary": summ, "contrasts": contrasts, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "compound walk: len delta modulo %.2f / r2 %.2f / r2+balanced %.2f; exaptation %.3f / %.3f / %.3f"
                      % (summ["modulo"]["len_delta_mean"], summ["r2"]["len_delta_mean"], summ["r2_balanced"]["len_delta_mean"],
                         summ["modulo"]["exaptation_rate"], summ["r2"]["exaptation_rate"], summ["r2_balanced"]["exaptation_rate"]), material, detail={"summary": summ, "contrasts": contrasts})
    print("DONE material=%s (%.0f s) %s" % (material, time.time() - t0, {a: {k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()} for a, s in summ.items()}))


if __name__ == "__main__":
    main()
