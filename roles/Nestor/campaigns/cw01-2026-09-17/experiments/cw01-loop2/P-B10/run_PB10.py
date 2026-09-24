"""P-B10 (anti-gravity): is e03's routing-precision plateau a world ceiling or a search limit?

Parent T-X11 (<- e03). feature_overlap in {0.1, 0.2, 0.35, 0.5} x generations {60, 240} x 2
attempt ids; per cell the evolved treatment's routing precision, coverage and score, beside a
hand-built BAYES-OPTIMAL router for the same overlap (posterior over classes from the known
centres and isotropic noise sd = overlap; activates exactly the argmax class's needs) evaluated
on the same streams. Plateau = world ceiling if evolved precision tracks the router's within .05
across overlaps; search limit if the gap stays large and shrinks with generations.
"""
from __future__ import annotations

import math
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "loop"))
import looprun as L            # noqa: E402
import seeds as S              # noqa: E402

W3 = L.import_world("cw01-e03", "world_e03")
PID, TID = "P-B10", "T-X11"
OVS, GENS = (0.1, 0.2, 0.35, 0.5), (60, 240)


def router_episode(cfg, stream_seed, structure, centres, ov):
    """Bayes-optimal router on the same items as run_episode (same rng sequence for items)."""
    wrng = np.random.Generator(np.random.PCG64(stream_seed))
    items = W3.make_items(cfg, wrng, centres=centres)
    af = cfg["affordances"]
    K, M = af["K"], cfg["items"]["M_classes"]
    info = cost = 0.0
    hits = n_act = 0
    cov_sum = 0.0
    for it in items:
        x = it["x"]
        ll = [-np.sum((x - centres[m] * (1 - ov)) ** 2) / (2 * max(ov, 1e-6) ** 2) for m in range(M)]
        m_hat = int(np.argmax(ll))
        idx = set(structure[m_hat])
        need = structure[it["cls"]]
        met = len(idx & need)
        cov = met / max(1, len(need))
        cost += af["base_process_cost"] + af["activation_cost"] * len(idx)
        info += math.log2(1.0 + it["size"]) * cov
        hits += met
        n_act += len(idx)
        cov_sum += cov
    return {"routing_precision": hits / max(1, n_act), "coverage_mean": cov_sum / len(items), "score": info / cost if cost else 0.0}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "claim_type": "exploratory-descriptive",
                         "delta": "feature_overlap x generations sweep with a Bayes-optimal router ceiling per overlap", "unchanged": "e03 organism, economics, selection",
                         "attacks": "the unexplained 0.58-0.63 precision plateau", "decision": "descriptive: world ceiling if evolved precision within .05 of the router across overlaps; search limit if the gap is > .10 and shrinks with generations",
                         "continuation": ["generations 1000", "population 256", "nonlinear activation policy"]})
    rows = []
    for ov in OVS:
        for Gn in GENS:
            for i in range(2):
                cfg = L.load_cfg("cw01-e03", "cw01-loop2-PB10-%d" % i)
                cfg["items"]["feature_overlap"] = ov
                st, ce = W3.attempt_structure(cfg, S.seed), W3.attempt_centres(cfg, S.seed)
                ev = W3.evolve(cfg, "treatment", Gn, 64, S.seed, structure=st, centres=ce)
                h = ev["history"][-1]
                rt = [router_episode(cfg, S.seed(cfg["attempt_id"], "stream|router", j), st, ce, ov) for j in range(8)]
                rec = {"overlap": ov, "G": Gn, "aid": i, "precision": h["mean_routing_precision"], "coverage": h["mean_coverage_mean"], "score": h["mean"],
                       "router_precision": float(np.mean([r["routing_precision"] for r in rt])), "router_coverage": float(np.mean([r["coverage_mean"] for r in rt])), "router_score": float(np.mean([r["score"] for r in rt]))}
                rows.append(rec)
                print("   ov %.2f G %3d id %d  evolved prec %.3f cov %.3f score %.3f | router prec %.3f cov %.3f score %.3f" % (ov, Gn, i, rec["precision"], rec["coverage"], rec["score"], rec["router_precision"], rec["router_coverage"], rec["router_score"]), flush=True)
    summ = {}
    for ov in OVS:
        for Gn in GENS:
            v = [r for r in rows if r["overlap"] == ov and r["G"] == Gn]
            summ["ov%.2f|G%d" % (ov, Gn)] = {"precision": float(np.mean([r["precision"] for r in v])), "router": float(np.mean([r["router_precision"] for r in v])),
                                             "gap": float(np.mean([r["router_precision"] - r["precision"] for r in v])), "score_gap": float(np.mean([r["router_score"] - r["score"] for r in v]))}
    gaps60 = {ov: summ["ov%.2f|G60" % ov]["gap"] for ov in OVS}
    gaps240 = {ov: summ["ov%.2f|G240" % ov]["gap"] for ov in OVS}
    ceiling = all(abs(g) <= 0.05 for g in gaps240.values())
    search_limit = any(g > 0.10 for g in gaps60.values()) and all(gaps240[ov] <= gaps60[ov] for ov in OVS)
    reading = "world ceiling" if ceiling else "search limit" if search_limit else "mixed: gap depends on overlap"
    out = {"perturbation_id": PID, "parent": TID, "summary": summ, "gaps_60": gaps60, "gaps_240": gaps240, "reading": reading, "rows": rows, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "plateau sweep: %s; router-minus-evolved precision gap at G60 %s, G240 %s" % (reading, {k: round(v, 3) for k, v in gaps60.items()}, {k: round(v, 3) for k, v in gaps240.items()}), True, detail=summ)
    print("DONE %s (%.0f s)" % (reading, time.time() - t0))


if __name__ == "__main__":
    main()
