"""P-D14 (serendipity, T-ARCH4/W1 x T-E08): Campaign 4's neutral archive under a HELD-OUT SELECTION rule.

For every viable parent, walkers 1-4 (depth 16, archived at 2/4/8/16) form the archive. Rule A
(train): choose the archived variant with the best reward on the PARENT environment. Rule B
(held-out): choose by reward on W2_K2d1. Exaptation (D6 rule) of the chosen variant is then measured
on the remaining held-out environments (OTHER_ENVS minus the parent environment), identical for both
rules. Paired sign-flip over parents of (B - A). Computational scope: integer programs on a bounded VM.
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

PID, TID = "P-D14", "T-ARCH4/W1"
HELD = A.with_knobs(A.WorldSpec("W2_K2", K=2, value_bits=4), name="W2_K2d1", delay=1)
BAND = A.C1.BAND


def job(j):
    p = j["parent"]
    env = p["env"]
    eps = {k: A.episodes(k) for k in A.ENVS}
    held = A.episodes_for(HELD, A.CAMPAIGN_SEED, "train", 1, A.C1.E)
    pm = A.canonical(p["manifest"])
    pev = A.eval_all(pm, eps)
    others = [o for o in A.OTHER_ENVS if o != env]
    cands = []
    for w in range(1, 5):
        wk = A.C5.walk(pm, p["organism_id"], w, eps[env], 16, 32)
        for dd, m in wk["archived"].items():
            if dd == 0:
                continue
            cands.append({"walker": w, "depth": dd, "m": m, "train": A.evaluate(m, eps[env], rng_seed=0, reward_mode="per_ask")["reward_per_ask"],
                          "held": A.evaluate(m, held, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]})
    if not cands:
        return {"pid": p["organism_id"], "n_cands": 0}
    a = max(cands, key=lambda c: (c["train"], -c["depth"]))
    b = max(cands, key=lambda c: (c["held"], -c["depth"]))

    def exapt(c):
        fev = A.eval_all(c["m"], eps)
        ex = [o for o in others if fev[o]["reward_per_ask"] >= pev[o]["reward_per_ask"] + BAND and fev[o]["reward_per_ask"] >= A.C1.FLOOR]
        return bool(ex), ex
    ea, exa = exapt(a)
    eb, exb = exapt(b)
    return {"pid": p["organism_id"], "set": p["stratum"], "n_cands": len(cands), "A": {"walker": a["walker"], "depth": a["depth"], "train": a["train"], "held": a["held"], "exaptive": ea, "on": exa},
            "B": {"walker": b["walker"], "depth": b["depth"], "train": b["train"], "held": b["held"], "exaptive": eb, "on": exb}, "same_choice": (a["walker"], a["depth"]) == (b["walker"], b["depth"]),
            "held_parent": A.evaluate(pm, held, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "scope": CM.SCOPE, "claim_type": "serendipity-descriptive",
                         "archive": "walkers 1-4 depth 16 archived at 2/4/8/16 (C4-05 seeds)", "rules": {"A": "best reward on the parent environment (ties: shallowest)", "B": "best reward on W2_K2d1 (ties: shallowest)"},
                         "measure": "exaptation (D6 rule) on OTHER_ENVS minus the parent environment, same set for both rules", "statistic": "paired sign-flip over parents of exaptive(B) - exaptive(A); Wilson bands of each rate",
                         "material_rule": "paired sign-flip outside its band", "continuation": ["selection on each held-out world in turn", "top-k instead of best"],
                         "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    with A.pool(8) as ex:
        rows = [r for r in ex.map(job, [{"parent": p} for p in parents]) if r.get("n_cands")]
    ra = sum(1 for r in rows if r["A"]["exaptive"])
    rb = sum(1 for r in rows if r["B"]["exaptive"])
    sf = CM.paired_signflip([int(r["B"]["exaptive"]) - int(r["A"]["exaptive"]) for r in rows])
    same = sum(1 for r in rows if r["same_choice"])
    by_set = {}
    for r in rows:
        s = by_set.setdefault(r["set"], {"n": 0, "A": 0, "B": 0})
        s["n"] += 1
        s["A"] += int(r["A"]["exaptive"])
        s["B"] += int(r["B"]["exaptive"])
    material = bool(sf and (sf["above_p95"] or sf["below_p05"]))
    out = {"perturbation_id": PID, "parent": TID, "n_parents": len(rows), "exaptive_A": ra, "exaptive_B": rb, "same_choice": same, "by_set": by_set, "paired_signflip_B_minus_A": sf,
           "held_gain_B_minus_A": float(np.mean([r["B"]["held"] - r["A"]["held"] for r in rows])), "train_loss_B_minus_A": float(np.mean([r["B"]["train"] - r["A"]["train"] for r in rows])),
           "rows": rows, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "held-out selection of the neutral archive: exaptive A %d/%d vs B %d/%d (same choice %d); B-A %s; by set %s" % (ra, len(rows), rb, len(rows), same, (round(sf["mean_diff"], 3), sf["above_p95"]) if sf else None, by_set), material, detail=by_set)
    L.append_evidence("T-E08", PID, "cross: the train-vs-held-out selection surface in C4's archive: A %d/%d, B %d/%d" % (ra, len(rows), rb, len(rows)), material)
    print("DONE material=%s A %d B %d / %d same %d (%.0f s)" % (material, ra, rb, len(rows), same, time.time() - t0))


if __name__ == "__main__":
    main()
