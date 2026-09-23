"""P-C15 (serendipity): CW01's blind fraction-deletion damage family on Campaign 4's programs.

Parent T-ARCH4/D1 (x T-E07). Delta: for each viable parent and its walker-1 depth-16 descendant,
delete a uniform random fraction f in {.1, .2, .3} of INSTRUCTIONS (whole 4-word units chosen
uniformly without replacement, blind to content) - the representation-blind family of cw01-e07 -
vs CONTIGUOUS deletion of the same count k at a random aligned position (the grammar's deletion
semantics with k forced); 8 draws each; C4-01 classification, displacement, exaptation. Attacks
C4-04's 'deletion carries ~0 reference effect' and the operator-vs-fraction geometry difference.
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

PID, TID = "P-C15", "T-ARCH4/D1"
FRACS, DRAWS = (0.1, 0.2, 0.3), 8


def delete_instr(m, idx):
    c = json.loads(json.dumps(m))
    g = c["genome"]
    keep = [w for i, w in enumerate(g) if (i // A.IW) not in idx]
    if len(keep) < A.IW:
        keep = g[:A.IW]
    c["genome"] = keep
    return c


def job(p):
    env = p["env"]
    eps = {k: A.episodes(k) for k in A.ENVS}
    programs = [("parent", p["manifest"])]
    wk = A.C5.walk(p["manifest"], p["organism_id"], 1, eps[env], 16, 32)
    programs.append(("walker16", wk["archived"].get(wk["depth"])))
    rows = []
    for tag, pm in programs:
        pev = A.eval_all(pm, eps)
        n = CM.n_instr(pm)
        for f in FRACS:
            k = max(1, int(round(f * n)))
            if k >= n:
                continue
            for d in range(1, DRAWS + 1):
                rng = A.SplitMix64(A.seed_from("nestor.pc15", A.LOOP_SEED, p["organism_id"], tag, f, d))
                for mode in ("blind", "contiguous"):
                    if mode == "blind":
                        idx = set()
                        while len(idx) < k:
                            idx.add(int(rng.next_u32() % n))
                    else:
                        s = int(rng.next_u32() % (n - k + 1))
                        idx = set(range(s, s + k))
                    child = delete_instr(pm, idx)
                    cev = A.eval_all(child, eps)
                    disp = A.C1.displacement(cev[env]["_answers"], pev[env]["_answers"])
                    cl = A.classify(cev, pev, disp, False, env)
                    rows.append({"parent_id": p["organism_id"], "stratum": p["stratum"], "program": tag, "f": f, "k": k, "n": n, "mode": mode, "draw": d,
                                 "D": cl["label"], "displacement": disp, "reward": cev[env]["reward_per_ask"], "parent_reward": pev[env]["reward_per_ask"]})
    return rows


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "scope": CM.SCOPE, "claim_type": "serendipity-descriptive",
                         "delta": "blind fraction deletion of instructions (f .1/.2/.3) vs contiguous deletion at matched count, on parents and their walker-1 depth-16 descendants",
                         "held_fixed": "programs, environments, classification, decode (modulo)", "attacks": "operator geometry vs fraction geometry; C4-04's deletion ~0 reference effect",
                         "nonredundant": "a damage family from another trajectory (cw01-e07) never applied here", "draws": DRAWS,
                         "measures": "loss, neutral, coherent, displacement by f x mode x program; paired sign-flip (blind minus contiguous) per parent",
                         "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    with A.pool(8) as ex:
        rows = [r for rs in ex.map(job, parents) for r in rs]
    summ = {}
    for prog in ("parent", "walker16"):
        for f in FRACS:
            for mode in ("blind", "contiguous"):
                rs = [r for r in rows if r["program"] == prog and r["f"] == f and r["mode"] == mode]
                if not rs:
                    continue
                c = Counter(r["D"] for r in rs)
                n = len(rs)
                summ["%s|f%.1f|%s" % (prog, f, mode)] = {"n": n, "loss": (c["D2"] + c["D3"]) / n, "neutral": c["D5"] / n,
                                                        "coherent": (c["D4"] + c["D6"] + c["D7"]) / n, "D6": c["D6"], "D7": c["D7"],
                                                        "displacement_mean": float(np.mean([r["displacement"] for r in rs]))}
    contrasts = {}
    for f in FRACS:
        per = {}
        for r in rows:
            if r["program"] == "parent" and r["f"] == f:
                per.setdefault(r["parent_id"], {}).setdefault(r["mode"], []).append(1.0 if r["D"] in ("D2", "D3") else 0.0)
        diffs = [np.mean(v["blind"]) - np.mean(v["contiguous"]) for v in per.values() if "blind" in v and "contiguous" in v]
        contrasts["loss_blind_minus_contiguous_f%.1f" % f] = CM.paired_signflip(diffs)
    material = any(c and (c["above_p95"] or c["below_p05"]) for c in contrasts.values())
    out = {"perturbation_id": PID, "parent": TID, "summary": summ, "contrasts": contrasts, "material": material,
           "n_parents": len(parents), "n_rows": len(rows), "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "blind vs contiguous deletion loss: %s" % {k: round(v["loss"], 3) for k, v in summ.items() if k.startswith("parent")},
                      material, detail={"summary": summ, "contrasts": contrasts})
    L.append_evidence("T-E07", PID, "e07's blind deletion family applied to Campaign 4 programs: see T-ARCH4/D1", material)
    print("DONE material=%s (%.0f s) %s" % (material, time.time() - t0, {k: round(v["loss"], 3) for k, v in summ.items()}))


if __name__ == "__main__":
    main()
