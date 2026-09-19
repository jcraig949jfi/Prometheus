"""P-H09 [T-X20 x T-X19 x T-ARCH4/R1, serendipity]: STRUCTURAL CORRELATES of the six geometries - manifest
limits, persist policy, length, persistent words, opcode-category histogram, reach share - per cluster
against a label-permutation null. Computational scope: integer programs on a bounded VM.
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
import manifold as MF          # noqa: E402
import scatter as SC           # noqa: E402
A, L = CM.A, CM.L

PID, TID = "P-H09", "T-X20"
CATS = sorted(set(A.CATEGORY.values()))


def job(j):
    m = A.canonical(j["manifest"])
    eps = A.episodes(j["env"])
    ev = A.evaluate(m, eps, rng_seed=0, reward_mode="per_ask")
    g = m["genome"]
    n = len(g) // A.IW
    hist = {c: 0 for c in CATS}
    for i in range(n):
        hist[A.CATEGORY[g[i * A.IW] % A.N_OPCODES]] += 1
    reach = SC.reach_map(m, eps)
    return {"pid": j["pid"], "cluster": j["cluster"], "persist": m["persist"], "n_regs": m["n_regs"], "tape_words": m["tape_words"], "tick_budget": m["tick_budget"], "out_cap": m["out_cap"], "code_writable": m["code_writable"],
            "n_instr": n, "pw": ev["meter"].get("persistent_state_words", 0), "reach_share": float(np.mean(reach)), "cats": {c: hist[c] / n for c in CATS}, "r0": ev["reward_per_ask"]}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "co_parents": ["T-X19", "T-ARCH4/R1"], "scope": CM.SCOPE, "claim_type": "serendipity-census",
                         "programs": "every P-F02 census program with a complete vector, cluster = nearest centroid", "features": ["persist", "n_regs", "tape_words", "tick_budget", "out_cap", "code_writable", "n_instr", "persistent words", "category shares", "reach share (HALT probe)"],
                         "tests": "continuous: cluster mean vs 2000-permutation band of cluster labels; categorical: share vs band", "material_rule": "any feature outside its band for the start-anchored or periodic cluster", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    progs = MF.census_programs()
    rv = MF.rows()
    jobs = []
    for p in progs:
        r = rv.get(p["organism_id"])
        if r and all(x == x for x in r["vector"]):
            jobs.append({"pid": p["organism_id"], "manifest": p["manifest"], "env": p["env"], "cluster": MF.nearest(r["vector"])[0]})
    with A.pool(8) as ex:
        rows = list(ex.map(job, jobs))
    feats = {"n_regs": lambda r: r["n_regs"], "tape_words": lambda r: r["tape_words"], "tick_budget": lambda r: np.log2(r["tick_budget"]), "out_cap": lambda r: r["out_cap"], "code_writable": lambda r: float(r["code_writable"]),
             "n_instr": lambda r: r["n_instr"], "pw": lambda r: r["pw"], "reach_share": lambda r: r["reach_share"], "r0": lambda r: r["r0"]}
    for c in CATS:
        feats["cat_" + c] = (lambda c: (lambda r: r["cats"][c]))(c)
    for pol in ("none", "regs", "tape", "all"):
        feats["persist_" + pol] = (lambda pol: (lambda r: float(r["persist"] == pol)))(pol)
    labs = np.array([r["cluster"] for r in rows])
    rng = np.random.Generator(np.random.PCG64(0))
    perms = [rng.permutation(labs) for _ in range(2000)]
    table = {}
    for fname, fn in feats.items():
        x = np.array([fn(r) for r in rows], float)
        table[fname] = {}
        for c in sorted(set(labs)):
            obs = float(x[labs == c].mean())
            null = np.array([x[p == c].mean() for p in perms])
            table[fname][MF.SHAPE[c] + "#%d" % c] = {"n": int((labs == c).sum()), "mean": obs, "p05": float(np.percentile(null, 5)), "p95": float(np.percentile(null, 95)), "outside": bool(obs < np.percentile(null, 5) or obs > np.percentile(null, 95))}
    hits = {sh: [f for f, v in table.items() if v[sh]["outside"]] for sh in table["n_instr"]}
    material = bool(hits.get("start_anchored#0") or hits.get("periodic#4"))
    out = {"perturbation_id": PID, "parent": TID, "n_programs": len(rows), "features_outside_band": hits, "table": table, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "structural correlates: features outside band per shape %s; start_anchored means %s; periodic means %s"
                      % (hits, {f: round(table[f]["start_anchored#0"]["mean"], 3) for f in hits.get("start_anchored#0", [])}, {f: round(table[f]["periodic#4"]["mean"], 3) for f in hits.get("periodic#4", [])}), material, detail={"hits": hits})
    L.append_evidence("T-X19", PID, "cross: start-anchored structural correlates %s" % hits.get("start_anchored#0"), material)
    print("DONE material=%s (%.0f s) %s" % (material, time.time() - t0, hits))


if __name__ == "__main__":
    main()
