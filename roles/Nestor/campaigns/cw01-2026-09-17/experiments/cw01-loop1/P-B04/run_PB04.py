"""P-B04: e02 with T2 IMPOSSIBLE without T1 (the stated design consequence of e02's NULL).

Parent T-X09 (<- T-E02). Delta: t2_cost returns a prohibitive price (1e6) unless the payload
has been normalised (dispersion <= 0.2, reachable only through T1 since initial dispersion is
U[0.55, 1.0]); selection weakened per D028 (elite_fraction 0.5, sigma 0.06); K1 revert-A
EXECUTED: each evolved genome's p_norm is reverted to the ancestor-population mean and the
loss on 24 matched streams is compared with a sham revert of neutral_a. 4 replicates.
Unchanged: everything else in e02 (T1/T3/T4 prices, organism, episode, detector procedure).
Claim: break-NULL under changed economics; decision rule preregistered below.
"""
from __future__ import annotations

import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "loop"))
import looprun as L            # noqa: E402
import seeds as S              # noqa: E402
import lineage as LG           # noqa: E402

W2 = L.import_world("cw01-e02", "world_e02")
PID, TID, AID = "P-B04", "T-X09", "cw01-loop1-PB04"
N_REP, G, N_STREAMS, PROHIBITIVE, NORMALISED = 4, 80, 24, 1.0e6, 0.2

_orig_t2 = W2.t2_cost


def t2_cost_gated(cfg, dispersion):
    return _orig_t2(cfg, dispersion) if dispersion <= NORMALISED else PROHIBITIVE


W2.t2_cost = t2_cost_gated


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "claim_type": "break-null-changed-economics",
                         "delta": "T2 prohibitive (cost 1e6) unless dispersion <= 0.2 (only T1 gets there); elite_fraction 0.5, sigma 0.06; K1 revert executed with a neutral-gene sham",
                         "unchanged": "T1/T3/T4 prices, 9-gene organism, episode, 80 generations, fixation ruler",
                         "attacks": "e02's valley (foundation alone a loss, later gain profitable without it) and the never-run knockout",
                         "replicates": N_REP, "streams_k1": N_STREAMS,
                         "statistic": "fixation order p_norm vs p_factor; K1 loss = score(evolved) - score(p_norm reverted to ancestor mean) minus sham loss (neutral_a reverted), paired over streams and organisms",
                         "decision": {"RATCHET_SUPPORTED": "p_norm FIRST in >= 3/4 replicates AND K1 loss exceeds sham loss in >= 3/4 replicates",
                                      "NULL": "otherwise, with the order and losses reported", "INCONCLUSIVE": "no gene travels in >= 2 replicates"}})
    runs = []
    for rep in range(N_REP):
        cfg = L.load_cfg("cw01-e02", AID + "|r%d" % rep)
        cfg["population"]["elite_fraction"] = 0.5
        cfg["population"]["mutation_sigma"] = 0.06
        ev = W2.evolve(cfg, "treatment", G, cfg["population"]["organisms"], S.seed)
        fo = LG.fixation_order(ev["history"], "p_norm", "p_factor", W2.NEUTRAL_GENES)
        anc = ev["ancestor_pop"]
        anc_norm = float(np.mean([g["p_norm"] for g in anc]))
        anc_neut = float(np.mean([g["neutral_a"] for g in anc]))
        pop = ev["final_pop"]
        top = list(range(16))          # the first 16 of the final population (mutated elite copies)
        streams = [S.seed(AID, "k1stream", j) for j in range(N_STREAMS)]

        def score(g, j):
            return W2.run_episode(g, cfg, "treatment", streams[j], policy_seed=S.seed(AID, "k1policy", j))["score"]

        loss_k1, loss_sham = [], []
        for i in top:
            g = pop[i]
            for j in range(N_STREAMS):
                base = score(g, j)
                loss_k1.append(base - score(dict(g, p_norm=anc_norm), j))
                loss_sham.append(base - score(dict(g, neutral_a=anc_neut), j))
        rec = {"rep": rep, "fix_norm": fo["fix_a"], "fix_factor": fo["fix_b"], "verdict": fo["verdict"],
               "k1_loss_mean": float(np.mean(loss_k1)), "sham_loss_mean": float(np.mean(loss_sham)),
               "k1_exceeds_sham": bool(np.mean(loss_k1) > np.mean(loss_sham)),
               "gene_p_norm": ev["history"][-1]["gene_p_norm"], "gene_p_factor": ev["history"][-1]["gene_p_factor"],
               "ancestor_relative_pct": 100 * ev["history"][-1]["ancestor_relative"] / max(ev["ancestor_mean"], 1e-9),
               "mean_ordered": ev["history"][-1]["mean_ordered"], "mean_unordered": ev["history"][-1]["mean_unordered"]}
        runs.append(rec)
        print("   r%d  norm@%s factor@%s %s | K1 loss %.5f vs sham %.5f | p_norm %.2f p_factor %.2f | ordered %.1f unordered %.1f | anc-rel %+.1f%%"
              % (rep, fo["fix_a"], fo["fix_b"], fo["verdict"], rec["k1_loss_mean"], rec["sham_loss_mean"], rec["gene_p_norm"],
                 rec["gene_p_factor"], rec["mean_ordered"], rec["mean_unordered"], rec["ancestor_relative_pct"]), flush=True)
    n_first = sum(1 for r in runs if r["verdict"] == "p_norm FIRST")
    n_k1 = sum(1 for r in runs if r["k1_exceeds_sham"])
    n_travel = sum(1 for r in runs if r["fix_norm"] is not None and r["fix_factor"] is not None)
    if n_travel < 2:
        disp = "INCONCLUSIVE (genes did not travel)"
    elif n_first >= 3 and n_k1 >= 3:
        disp = "RATCHET_SUPPORTED"
    else:
        disp = "NULL"
    res = {"perturbation_id": PID, "parent": TID, "disposition": disp, "foundation_first": n_first, "k1_exceeds_sham": n_k1,
           "runs": runs, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, res, ph)
    L.append_evidence(TID, PID, "T2-impossible-without-T1: %s (foundation-first %d/4, K1>sham %d/4)" % (disp, n_first, n_k1),
                      disp != "NULL" or n_first >= 2, detail={"runs": runs})
    L.append_evidence("T-E02", PID, "changed economics re-pose: %s" % disp, disp == "RATCHET_SUPPORTED")
    print("DISPOSITION %s (%.0f s)" % (disp, time.time() - t0))


if __name__ == "__main__":
    main()
