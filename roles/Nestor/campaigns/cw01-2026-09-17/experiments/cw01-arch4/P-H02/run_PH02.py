"""P-H02 [T-X20 x T-X19 x T-X17, deformation X]: RECOMBINATION of representatives from different temporal
geometries - one-point splices (25/50/75 percent, both orders), middle-third insertions (both orders),
and the frozen grammar's own 'splice' operator with the other parent as mate; every child's full curve
set and rewards on three worlds; children named from the curves (COMPOSE / DOMINATE / INTERFERE /
DISAPPEAR / NEW); NEW children clustered and their shapes reported raw. Computational scope: integer
programs on a bounded VM.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
from itertools import combinations_with_replacement

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import manifold as MF          # noqa: E402
A, L = CM.A, CM.L
sys.path.insert(0, str(HERE.parent / "P-F02"))
from run_PF02 import kmeans, silhouette   # noqa: E402

PID, TID = "P-H02", "T-X20"
SHAPES = {0: "start_anchored", 4: "periodic", 5: "ask_time", 1: "schedule"}
NREP = 3


def cut(g, frac):
    n = len(g) // A.IW
    return int(round(frac * n)) * A.IW


def splice(a, b, frac):
    c = json.loads(json.dumps(a))
    c["genome"] = a["genome"][:cut(a["genome"], frac)] + b["genome"][cut(b["genome"], frac):]
    return c


def insert_third(a, b):
    c = json.loads(json.dumps(a))
    nb = len(b["genome"]) // A.IW
    seg = b["genome"][(nb // 3) * A.IW:(2 * nb // 3) * A.IW]
    mid = (len(a["genome"]) // A.IW // 2) * A.IW
    c["genome"] = a["genome"][:mid] + seg + a["genome"][mid:]
    return c


def valid(c):
    try:
        A.GR.validate_manifest(c) if hasattr(A.GR, "validate_manifest") else None
        if len(c["genome"]) < A.IW or len(c["genome"]) > c["tape_words"] or len(c["genome"]) > 4096:
            return False
        A.evaluate(c, A.episodes("W0")[:1], rng_seed=0, reward_mode="per_ask")
        return True
    except Exception:              # noqa: BLE001
        return False


def job(j):
    a, b = A.canonical(j["a"]["manifest"]), A.canonical(j["b"]["manifest"])
    out = []
    children = []
    for f in (0.25, 0.5, 0.75):
        children.append(("splice_ab_%.2f" % f, splice(a, b, f)))
        children.append(("splice_ba_%.2f" % f, splice(b, a, f)))
    children.append(("insert_b_into_a", insert_third(a, b)))
    children.append(("insert_a_into_b", insert_third(b, a)))
    for d in (1, 2):
        rng = A.SplitMix64(A.seed_from("nestor.ph02", A.LOOP_SEED, j["a"]["organism_id"], j["b"]["organism_id"], d))
        try:
            c1, _ = A.GR.mutate(a, rng, mate=b, name="splice")
            children.append(("grammar_splice_ab_%d" % d, c1))
            c2, _ = A.GR.mutate(b, rng, mate=a, name="splice")
            children.append(("grammar_splice_ba_%d" % d, c2))
        except Exception:          # noqa: BLE001
            pass
    for op, c in children:
        if not valid(c):
            out.append({"pair": j["pair"], "a": j["a"]["organism_id"], "b": j["b"]["organism_id"], "op": op, "valid": False})
            continue
        v, _ = MF.curve(c)
        out.append({"pair": j["pair"], "a": j["a"]["organism_id"], "b": j["b"]["organism_id"], "op": op, "valid": True, "vector": v, "rewards": MF.rewards3(c), "n_instr": CM.n_instr(c), "m": c})
    return out


def name_child(v, va, vb, cents):
    if not all(x == x for x in v):
        return "SILENT"
    da, db = MF.dist(v, va), MF.dist(v, vb)
    dk = min(MF.dist(v, c) for c in cents.values())
    if max(v) < 0.1:
        return "DISAPPEAR"
    A_, B_ = MF.distinctive(va), MF.distinctive(vb)
    if A_ != B_ and A_ and B_ and all(v[i] >= 0.3 for i in A_) and all(v[i] >= 0.3 for i in B_):
        return "COMPOSE"
    if (da < 0.15 and db > 0.3) or (db < 0.15 and da > 0.3):
        return "DOMINATE"
    if da > 0.3 and db > 0.3 and dk > 0.3:
        return "NEW"
    return "INTERFERE"


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "co_parents": ["T-X19", "T-X17"], "deformation": "X", "requires": ["P-G11"], "scope": CM.SCOPE, "claim_type": "recombination",
                         "representatives": NREP, "pairs": "all shape pairs including same-shape controls", "operators": ["splice at .25/.5/.75 both orders", "middle-third insertion both orders", "grammar 'splice' with mate, 2 draws each order"],
                         "naming": {"DISAPPEAR": "all components < .1", "COMPOSE": "both parents' distinctive positions (>= .5) present at >= .3 and the sets differ", "DOMINATE": "within .15 of one parent and > .3 from the other", "NEW": "> .3 from both parents and from every known centroid", "INTERFERE": "otherwise"},
                         "new_shapes": "NEW children clustered (k 2-4 by silhouette); centroids reported raw", "material_rule": "any NEW cluster with >= 5 members, or COMPOSE in >= 10 percent of cross-shape children", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    reps = {c: MF.representatives(c, NREP) for c in SHAPES}
    jobs = []
    for ca, cb in combinations_with_replacement(sorted(SHAPES), 2):
        for ra in reps[ca]:
            for rb in reps[cb]:
                if ca == cb and ra["organism_id"] >= rb["organism_id"]:
                    continue
                jobs.append({"pair": "%s|%s" % (SHAPES[ca], SHAPES[cb]), "a": ra, "b": rb})
    with A.pool(8) as ex:
        rows = [x for rs in ex.map(job, jobs) for x in rs]
    rowsv = MF.rows()
    cents = MF.centroids()
    named = {}
    for r in rows:
        if not r["valid"]:
            r["name"] = "INVALID"
            continue
        va, vb = rowsv[r["a"]]["vector"], rowsv[r["b"]]["vector"]
        r["name"] = name_child(r["vector"], va, vb, cents)
        r["d_a"], r["d_b"] = MF.dist(r["vector"], va), MF.dist(r["vector"], vb)
        r["nearest_known"] = MF.nearest(r["vector"])[1] if all(x == x for x in r["vector"]) else None
    for r in rows:
        named.setdefault(r["pair"], {}).setdefault(r["name"], 0)
        named[r["pair"]][r["name"]] += 1
    cross = [r for r in rows if r["valid"] and r["pair"].split("|")[0] != r["pair"].split("|")[1]]
    new = [r for r in rows if r.get("name") == "NEW"]
    newclusters = []
    if len(new) >= 6:
        X = np.array([r["vector"] for r in new], float)
        sil = {k: silhouette(X, kmeans(X, k)[0]) for k in (2, 3, 4) if k < len(new)}
        kb = max(sil, key=sil.get)
        lab, C = kmeans(X, kb)
        for i in range(kb):
            idx = np.flatnonzero(lab == i)
            newclusters.append({"n": int(len(idx)), "centroid": {k: round(float(x), 3) for k, x in zip(MF.KEYS, C[i])}, "pairs": sorted({new[j]["pair"] for j in idx}), "ops": sorted({new[j]["op"] for j in idx}), "example_ids": [(new[j]["a"], new[j]["b"], new[j]["op"]) for j in idx[:3]]})
    compose_share = float(np.mean([r["name"] == "COMPOSE" for r in cross])) if cross else 0.0
    by_op = {}
    for r in rows:
        by_op.setdefault(r["op"], {}).setdefault(r["name"], 0)
        by_op[r["op"]][r["name"]] += 1
    material = bool(any(c["n"] >= 5 for c in newclusters) or compose_share >= 0.10)
    out = {"perturbation_id": PID, "parent": TID, "n_children": len(rows), "n_valid": sum(r["valid"] for r in rows), "names_by_pair": named, "names_by_op": by_op, "compose_share_cross": compose_share, "n_new": len(new), "new_clusters": newclusters,
           "rewards_by_name": {nm: {w: float(np.mean([r["rewards"][w] for r in rows if r.get("name") == nm])) for w in MF.WORLDS3} for nm in ("COMPOSE", "DOMINATE", "INTERFERE", "DISAPPEAR", "NEW") if any(r.get("name") == nm for r in rows)},
           "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "recombination: %d children (%d valid); names by pair %s; by op %s; COMPOSE share (cross) %.3f; NEW %d in clusters %s" % (len(rows), out["n_valid"], named, by_op, compose_share, len(new), [(c["n"], c["pairs"]) for c in newclusters]), material, detail={"by_pair": named, "new": newclusters})
    for tid in ("T-X19", "T-X17"):
        L.append_evidence(tid, PID, "cross: recombination names %s; NEW shapes %s" % ({k: v for k, v in named.items() if "start_anchored" in k or "ask_time" in k}, [c["n"] for c in newclusters]), material)
    print("DONE material=%s (%.0f s) compose %.3f new %d %s" % (material, time.time() - t0, compose_share, len(new), by_op))


if __name__ == "__main__":
    main()
