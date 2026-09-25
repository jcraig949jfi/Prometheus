"""P-C03: C4-05's neutral walk under Nestor's trap-to-NOP decode layer (R2) vs modulo.

Parent T-ARCH4/R1. Delta: parents canonicalised (opcode word := word mod 25, behaviour-identical);
walk proposals = the frozen grammar's edit, then under R2 every out-of-table opcode word the edit
produced decodes as NOP (counted as an insulation event); under modulo the same edit is evaluated
as the VM would decode it. Same walk rules (band 1/16 of the ORIGINAL parent, 32 proposals, depth
16), same seeds, 2 walkers per viable parent. Related to but not identical with Campaign 5's
representation B (which regenerates parents under a narrow encoding): here the parents keep their
exact behaviour and only NEW out-of-table words are trapped. Descriptive with paired sign-flip
bands. Computational scope: integer programs on a bounded VM.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
A, L = CM.A, CM.L

PID, TID = "P-C03", "T-ARCH4/R1"
DEPTH, WALKERS = 16, 2


def make_proposal(mode):
    def proposal(cur, rng):
        child, rec = A.GR.mutate(cur, rng, mate=None, name=None)
        child2, n = A.trap(child, mode)
        rec = dict(rec)
        rec["trapped_words"] = n
        return child2, rec
    return proposal


def walk_job(job):
    p, mode = job["parent"], job["mode"]
    env = p["env"]
    eps = {k: A.episodes(k) for k in A.ENVS}
    pm = A.canonical(p["manifest"])
    pev = A.eval_all(pm, eps)
    others = [o for o in A.OTHER_ENVS if o != env]
    out = []
    for w in range(1, WALKERS + 1):
        wk = A.C5.walk(pm, p["organism_id"], w, eps[env], DEPTH, 32, proposal=make_proposal(mode))
        final = wk["archived"].get(wk["depth"])
        fev = A.eval_all(final, eps)
        ex = [o for o in others if fev[o]["reward_per_ask"] >= pev[o]["reward_per_ask"] + A.C1.BAND and fev[o]["reward_per_ask"] >= A.C1.FLOOR]
        props = sum(s["proposals"] for s in wk["steps"])
        out.append({"walker": w, "depth": wk["depth"], "stalled": wk["stalled"], "proposals": props,
                    "acceptance": (wk["depth"] / props) if props else None,
                    "trapped_in_accepted": sum(int(s.get("args", {}) is not None and 0) for s in wk["steps"]),
                    "trapped_words_total": sum(int(s.get("trapped_words", 0) or 0) for s in wk["steps"]),
                    "len_delta": CM.n_instr(final) - CM.n_instr(pm), "exaptive_on": ex,
                    "reward_final": fev[env]["reward_per_ask"], "manifest": final})
    return {"parent_id": p["organism_id"], "stratum": p["stratum"], "env": env, "mode": mode, "walkers": out}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "scope": CM.SCOPE, "claim_type": "one-axis-walk-descriptive",
                         "delta": "walk proposals decoded under R2 (trap-to-NOP for new out-of-table opcode words) vs modulo, on canonicalised parents",
                         "held_fixed": "walk rules (band 1/16 of the original parent, 32 proposals, depth 16), seeds, environments, parents' behaviour",
                         "attacks": "'the neutral network is large, connected and cheap' as a property of modulo decode (C4-05); the insulated neighbourhood",
                         "nonredundant": "C5 measured representation B's census (C5-05) and the OLD deep walk (C5-01); no walk under an insulating decode was run",
                         "measures": "connected depth, acceptance, insulation events per accepted step, length delta, structural diversity at depth 16, held-out exaptation at depth 16; paired sign-flip bands (modulo vs R2) per parent",
                         "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    jobs = [{"parent": p, "mode": m} for p in parents for m in ("modulo", "nop")]
    with A.pool(8) as ex:
        res = list(ex.map(walk_job, jobs))
    by = {}
    for r in res:
        by.setdefault(r["parent_id"], {})[r["mode"]] = r
    per_mode = {m: {"depth": [], "acceptance": [], "len_delta": [], "exapt": [], "trapped": []} for m in ("modulo", "nop")}
    mani = {m: [] for m in per_mode}
    diffs = {"acceptance": [], "len_delta": [], "exapt": []}
    for pid, d in by.items():
        for m in per_mode:
            for w in d[m]["walkers"]:
                per_mode[m]["depth"].append(w["depth"])
                per_mode[m]["acceptance"].append(w["acceptance"] if w["acceptance"] is not None else np.nan)
                per_mode[m]["len_delta"].append(w["len_delta"])
                per_mode[m]["exapt"].append(1.0 if w["exaptive_on"] else 0.0)
                per_mode[m]["trapped"].append(w["trapped_words_total"])
                mani[m].append(w["manifest"])
        for key in diffs:
            a = np.nanmean([(w["acceptance"] if key == "acceptance" else w["len_delta"] if key == "len_delta" else (1.0 if w["exaptive_on"] else 0.0)) for w in d["nop"]["walkers"]])
            b = np.nanmean([(w["acceptance"] if key == "acceptance" else w["len_delta"] if key == "len_delta" else (1.0 if w["exaptive_on"] else 0.0)) for w in d["modulo"]["walkers"]])
            diffs[key].append(a - b)
    summary = {m: {"n_walkers": len(v["depth"]), "connected_16": float(np.mean([x == DEPTH for x in v["depth"]])),
                   "acceptance_mean": float(np.nanmean(v["acceptance"])), "len_delta_mean": float(np.mean(v["len_delta"])),
                   "exaptation_rate": float(np.mean(v["exapt"])), "trapped_words_per_walker": float(np.mean(v["trapped"])),
                   "structural_diversity_16": CM.struct_div(mani[m][:120])} for m, v in per_mode.items()}
    contrasts = {k: CM.paired_signflip(v) for k, v in diffs.items()}
    material = any(c and (c["above_p95"] or c["below_p05"]) for c in contrasts.values())
    res_out = {"perturbation_id": PID, "parent": TID, "summary": summary, "paired_contrasts_nop_minus_modulo": contrasts,
               "material": material, "n_parents": len(parents), "elapsed_s": round(time.time() - t0, 1),
               "per_parent": {pid: {m: [{k: v for k, v in w.items() if k != "manifest"} for w in d[m]["walkers"]] for m in d} for pid, d in by.items()}}
    L.result(HERE, res_out, ph)
    L.append_evidence(TID, PID, "walk under trap-to-NOP vs modulo: acceptance %.3f vs %.3f, len delta %.2f vs %.2f, exaptation %.3f vs %.3f, insulation events/walker %.1f"
                      % (summary["nop"]["acceptance_mean"], summary["modulo"]["acceptance_mean"], summary["nop"]["len_delta_mean"], summary["modulo"]["len_delta_mean"],
                         summary["nop"]["exaptation_rate"], summary["modulo"]["exaptation_rate"], summary["nop"]["trapped_words_per_walker"]),
                      material, detail={"contrasts": contrasts, "summary": summary})
    print("DONE material=%s %s (%.0f s)" % (material, {m: {k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()} for m, s in summary.items()}, time.time() - t0))


if __name__ == "__main__":
    main()
