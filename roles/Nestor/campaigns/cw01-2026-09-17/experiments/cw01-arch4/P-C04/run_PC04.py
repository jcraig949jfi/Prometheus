"""P-C04: edit LOCALITY at radius 4 (distributed vs block vs sequential-viable).

Parent T-ARCH4/M1. Delta: three ways of applying four edits from one length-preserving,
position-addressable family (replacement of one instruction with four random words; operand
perturbation: one operand word +/- delta in [-8, 8] or one bit flipped; reference redirection: one
operand word overwritten uniformly), equiprobable: DISTRIBUTED = 4 edits at uniformly random
instruction positions; BLOCK = 4 edits inside one window of 4 consecutive instructions chosen once;
SEQUENTIAL = 4 distributed edits applied one at a time, each kept only if the intermediate program
stays viable (>= 3/16 on its environment), else redrawn (up to 8 tries). 8 draws per viable parent
per mode; C4-01's classification and displacement. The edits are Nestor's re-implementations of the
grammar's three single-instruction operators (stated, so the comparison is within this run only).
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

PID, TID = "P-C04", "T-ARCH4/M1"
DRAWS, R = 8, 4
MODES = ("distributed", "block", "sequential")


def edit_at(m, i, rng):
    """One length-preserving edit at instruction i; returns a new manifest and the kind."""
    c = json.loads(json.dumps(m))
    g = c["genome"]
    kind = int(rng.next_u32() % 3)                 # equiprobable over the three edit kinds
    base = i * A.IW
    if kind == 0:                                   # replacement
        for j in range(A.IW):
            g[base + j] = int(rng.next_u32())
        return c, "replacement"
    j = 1 + int(rng.next_u32() % 3)
    if kind == 1:                                   # operand perturbation
        if rng.next_u32() % 2 == 0:
            delta = int(rng.next_u32() % 17) - 8
            g[base + j] = (g[base + j] + delta) % (1 << 32)
        else:
            g[base + j] ^= (1 << int(rng.next_u32() % 32))
        return c, "operand_perturbation"
    g[base + j] = int(rng.next_u32())               # reference redirection
    return c, "reference_redirection"


def apply_mode(pm, mode, rng, env_eps):
    n = CM.n_instr(pm)
    cur = pm
    kinds = []
    if mode == "distributed":
        for _ in range(R):
            cur, k = edit_at(cur, int(rng.next_u32() % n), rng)
            kinds.append(k)
    elif mode == "block":
        s = int(rng.next_u32() % max(1, n - R + 1))
        for _ in range(R):
            cur, k = edit_at(cur, s + int(rng.next_u32() % min(R, n)), rng)
            kinds.append(k)
    else:
        for _ in range(R):
            for _try in range(8):
                cand, k = edit_at(cur, int(rng.next_u32() % n), rng)
                r = A.evaluate(cand, env_eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
                if r >= A.C1.FLOOR:
                    cur, kept = cand, k
                    break
            else:
                kept = "none_kept"
            kinds.append(kept)
    return cur, kinds


def census_job(job):
    p = job["parent"]
    env = p["env"]
    eps = {k: A.episodes(k) for k in A.ENVS}
    pm = p["manifest"]
    pev = A.eval_all(pm, eps)
    rows = []
    for mode in MODES:
        for d in range(1, DRAWS + 1):
            rng = A.SplitMix64(A.seed_from("nestor.pc04", A.LOOP_SEED, p["organism_id"], mode, d))
            child, kinds = apply_mode(pm, mode, rng, eps[env])
            cev = A.eval_all(child, eps)
            disp = A.C1.displacement(cev[env]["_answers"], pev[env]["_answers"])
            cl = A.classify(cev, pev, disp, False, env)
            rows.append({"parent_id": p["organism_id"], "stratum": p["stratum"], "mode": mode, "draw": d, "D": cl["label"],
                         "displacement": disp, "reward": cev[env]["reward_per_ask"], "parent_reward": pev[env]["reward_per_ask"], "kinds": kinds})
    return rows


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "scope": CM.SCOPE, "claim_type": "one-axis-census-descriptive",
                         "delta": "locality of four length-preserving edits: distributed vs block(window 4) vs sequential-viable", "draws": DRAWS,
                         "held_fixed": "parents (original words), environments, classification constants, decode (modulo), edit family",
                         "attacks": "'distance predicts P(destruction) not degree' measured only for distributed multi-edit radius (C4-02)",
                         "nonredundant": "C4 varied how many edits, never where or in what order",
                         "measures": "loss (D2+D3), neutral (D5), coherent (D4+D6+D7), displacement histogram, per mode; paired-by-parent sign-flip bands on loss and displacement",
                         "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    with A.pool(8) as ex:
        rows = [r for rs in ex.map(census_job, [{"parent": p} for p in parents]) for r in rs]
    summ = {}
    for mode in MODES:
        rs = [r for r in rows if r["mode"] == mode]
        c = Counter(r["D"] for r in rs)
        n = len(rs)
        disp = [r["displacement"] for r in rs]
        summ[mode] = {"n": n, "loss": (c["D2"] + c["D3"]) / n, "neutral": c["D5"] / n, "coherent": (c["D4"] + c["D6"] + c["D7"]) / n,
                      "D7": c["D7"], "D6": c["D6"], "displacement_mean": float(np.mean(disp)),
                      "displacement_hist": A.C1._hist(disp), "classes": dict(c)}
    def per_parent(mode, key):
        out = {}
        for r in rows:
            if r["mode"] == mode:
                out.setdefault(r["parent_id"], []).append((1.0 if r["D"] in ("D2", "D3") else 0.0) if key == "loss" else r["displacement"])
        return {k: float(np.mean(v)) for k, v in out.items()}
    contrasts = {}
    for key in ("loss", "displacement"):
        dist = per_parent("distributed", key)
        for other in ("block", "sequential"):
            o = per_parent(other, key)
            contrasts["%s_%s_minus_distributed" % (key, other)] = CM.paired_signflip([o[k] - dist[k] for k in dist if k in o])
    material = any(c and (c["above_p95"] or c["below_p05"]) for c in contrasts.values())
    res = {"perturbation_id": PID, "parent": TID, "summary": summ, "contrasts": contrasts, "material": material,
           "n_parents": len(parents), "n_rows": len(rows), "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, res, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "locality at radius 4: loss distributed %.3f / block %.3f / sequential %.3f; displacement %.3f / %.3f / %.3f"
                      % (summ["distributed"]["loss"], summ["block"]["loss"], summ["sequential"]["loss"],
                         summ["distributed"]["displacement_mean"], summ["block"]["displacement_mean"], summ["sequential"]["displacement_mean"]),
                      material, detail={"summary": summ, "contrasts": contrasts})
    print("DONE material=%s %s (%.0f s)" % (material, {m: {k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items() if k not in ("displacement_hist", "classes")} for m, s in summ.items()}, time.time() - t0))


if __name__ == "__main__":
    main()
