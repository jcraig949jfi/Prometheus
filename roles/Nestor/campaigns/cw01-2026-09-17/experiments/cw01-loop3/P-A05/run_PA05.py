"""P-A05 (T-X03): can a world's composability be predicted BEFORE running it?

Two predictors computed from the attempt-stable latent facts alone (capability map + item pool):
  P1 coverage overlap      mean pairwise Jaccard of the disjunctive templates each capability serves
  P2 conjunctive concentration   max over 3-subsets of capabilities of the share of conjunctive
                           templates fully covered (the inverse of conjunctive-demand spread)
Split rule (preregistered here): threshold = midpoint of the class means on the EXISTING e05 worlds
(RESULT.json replicates), direction = the side of the clearing class. Then 48 fresh worlds are
drawn, the contracted outcome (superadditivity of the enumerated BEST set clears its 8-block
measured null, budget B=3) is computed by running the statistic (no evolution needed), and each
predictor's accuracy is scored against a 2000-permutation label null.
"""
from __future__ import annotations

import itertools
import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "loop"))
import looprun as L            # noqa: E402
import seeds as S              # noqa: E402
import infometrics as IM       # noqa: E402

W = L.import_world("cw01-e05", "world_e05")
PID, TID = "P-A05", "T-X03"
B, N_FRESH, N_BLOCKS = 3, 48, 8
IDS = ["cw01-loop3-PA05-%02d" % i for i in range(N_FRESH)]


def predictors(cfg, mk):
    capmap = W.attempt_capabilities(cfg, mk)
    pool = W.attempt_item_pool(cfg, mk)
    K = cfg["components"]["K"]
    disj = [t["need"] for t in pool if not t["conj"]]
    conj = [t["need"] for t in pool if t["conj"]]
    serve = {k: {i for i, need in enumerate(disj) if k in need} for k in range(K)}
    jac = []
    for a, b in itertools.combinations(range(K), 2):
        u = serve[a] | serve[b]
        jac.append(len(serve[a] & serve[b]) / len(u) if u else 0.0)
    p1 = float(np.mean(jac))
    p2 = (max(sum(1 for need in conj if need.issubset(set(s))) for s in itertools.combinations(range(K), B)) / len(conj)) if conj else 0.0
    return {"P1_coverage_overlap": p1, "P2_conjunctive_concentration": float(p2), "n_conj": len(conj), "n_disj": len(disj)}


def nsa(cfg, pool, capmap, comps, mk, aid, tag, n):
    s = W.superadditivity(cfg, "treatment", pool, capmap, W.genome_with(cfg, comps), mk, aid, tag, n)
    add = s["additive_prediction"]
    return 100.0 * s["superadditivity"] / add if add else float("nan")


def outcome(aid):
    cfg = L.load_cfg("cw01-e05", aid)
    mk = S.seed
    capmap = W.attempt_capabilities(cfg, mk)
    pool = W.attempt_item_pool(cfg, mk)
    K = cfg["components"]["K"]
    scored = sorted(((W.mean_score(W.genome_with(cfg, list(s)), cfg, "treatment", pool, capmap, mk, aid, "enum", 10), list(s)) for s in itertools.combinations(range(K), B)), reverse=True)
    best = scored[0][1]
    blocks = [nsa(cfg, pool, capmap, best, mk, aid, "nf%d" % b, 12) for b in range(N_BLOCKS)]
    sa = float(np.mean(blocks))
    cl = IM.effect_clears_null(sa, [b + 100.0 for b in blocks], direction="positive")
    return {"aid": aid, "best": best, "sa_mean_pct": sa, "clears": bool(cl["clears"]), "null_p95": cl["null_p95"], **predictors(cfg, mk)}


def accuracy_perm(pred, y, n=2000, seed=0):
    pred, y = np.asarray(pred, bool), np.asarray(y, bool)
    acc = float((pred == y).mean())
    rng = np.random.Generator(np.random.PCG64(seed))
    null = np.array([(pred == rng.permutation(y)).mean() for _ in range(n)])
    return {"accuracy": acc, "p95": float(np.percentile(null, 95)), "clears": bool(acc > np.percentile(null, 95)), "base_rate": float(y.mean())}


def main():
    t0 = time.time()
    existing = json.loads((HERE.parents[1] / "cw01-e05" / "RESULT.json").read_text(encoding="utf-8"))["replicates"]
    ex_rows = []
    for r in existing:
        cfg = L.load_cfg("cw01-e05", r["attempt_id"])
        ex_rows.append({"aid": r["attempt_id"], "clears": bool(r["superadditivity_clears_null"]), **predictors(cfg, S.seed)})
    rules = {}
    for k in ("P1_coverage_overlap", "P2_conjunctive_concentration"):
        a = [r[k] for r in ex_rows if r["clears"]]
        b = [r[k] for r in ex_rows if not r["clears"]]
        thr = 0.5 * (np.mean(a) + np.mean(b))
        rules[k] = {"threshold": float(thr), "clears_if": "ge" if np.mean(a) >= np.mean(b) else "le", "class_means": {"clears": float(np.mean(a)), "not": float(np.mean(b))}}
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "claim_type": "confirmatory-new", "existing_worlds": ex_rows, "split_rules": rules, "fresh_worlds": N_FRESH, "budget_B": B,
                         "outcome": "superadditivity of the exhaustively enumerated BEST set clears its %d-block measured null (contract statistic; no evolution needed)" % N_BLOCKS,
                         "scoring": "accuracy of each rule on the 48 fresh worlds vs a 2000-permutation label null (p95)", "material_rule": "either predictor's accuracy clears its permutation p95",
                         "continuation": ["predictor from the BEST set's own coverage", "conjunctive_fraction sweep (P-A06)"]})
    rows = []
    for aid in IDS:
        rows.append(outcome(aid))
        print("   %s clears %s sa %.2f P1 %.3f P2 %.3f" % (aid[-2:], rows[-1]["clears"], rows[-1]["sa_mean_pct"], rows[-1]["P1_coverage_overlap"], rows[-1]["P2_conjunctive_concentration"]), flush=True)
    y = [r["clears"] for r in rows]
    scores = {}
    for k, ru in rules.items():
        pred = [(r[k] >= ru["threshold"]) if ru["clears_if"] == "ge" else (r[k] <= ru["threshold"]) for r in rows]
        scores[k] = accuracy_perm(pred, y)
        scores[k]["spearman_with_sa"] = float(np.corrcoef(np.argsort(np.argsort([r[k] for r in rows])), np.argsort(np.argsort([r["sa_mean_pct"] for r in rows])))[0, 1])
    material = any(v["clears"] for v in scores.values())
    out = {"perturbation_id": PID, "parent": TID, "rules": rules, "scores": scores, "base_rate": float(np.mean(y)), "rows": rows, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "pre-run composability predictors on 48 fresh worlds (base rate %.2f): %s" % (float(np.mean(y)), {k: (round(v["accuracy"], 3), round(v["p95"], 3), v["clears"], round(v["spearman_with_sa"], 3)) for k, v in scores.items()}), material, detail=scores)
    print("DONE material=%s (%.0f s) %s" % (material, time.time() - t0, scores))


if __name__ == "__main__":
    main()
