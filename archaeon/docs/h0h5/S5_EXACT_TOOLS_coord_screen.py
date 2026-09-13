"""Coordinate screen: cheap, pre-target, one-step-computable state quantities vs the EXACT full-horizon
myopia of greedy (rel_gain_opt_vs_greedy from s5_opt_L{L}.json). Nothing here uses a target or a producer outcome.
Candidates (all from the feasible set T(E) and the 2^L probe values alone):
  c_gap2      exact two-step (count) disagreement gap > 0
  c_proxy     two unresolved blocks, both size >= 3
  c_ent       the ER1-optimal class and the max-entropy class are DISJOINT (count-greedy disagrees with entropy-greedy)
  c_tie       |G*| / 2^L (size of the one-step tie class)
  c_maxcell   max_d n_d / N of the greedy probe (how big its largest surviving cell is)
  c_H_deficit (H_max - H(greedy probe)) in bits: entropy the greedy probe forgoes
  c_log2N     log2 N
  c_shellness n_unresolved == 1
"""
import json, sys
import numpy as np
sys.path.insert(0, ".")
from s5_explore import World

def main():
    L = int(sys.argv[1]); W = World(L); rows = json.load(open("s5_opt_L%d.json" % L))
    out = []
    for r in rows:
        par = r["par"]
        fos = [(0, par["m"])] if r["family"] == "shell" else [(0, par["uA"] + par["uB"]), ((1 << par["a"]) - 1, (par["a"] - par["uA"]) + par["uB"])]
        S = W.feasible(fos); N = len(S); er1, n = W.er1num_all(S)
        P = n / N
        with np.errstate(divide="ignore", invalid="ignore"):
            H = -(np.where(P > 0, P * np.log2(np.where(P > 0, P, 1.0)), 0.0)).sum(1)
        G = np.flatnonzero(er1 == er1.min()); E = np.flatnonzero(np.abs(H - H.max()) < 1e-12)
        g = int(G[0])
        c = {"c_gap2": r["gap2"] > 0, "c_proxy": r["proxy"], "c_ent": len(set(G.tolist()) & set(E.tolist())) == 0, "c_tie": len(G) / (1 << L),
             "c_maxcell": float(n[g].max() / N), "c_H_deficit": float(H.max() - H[g]), "c_log2N": float(np.log2(N)), "c_shellness": r["n_unresolved"] == 1,
             "H_greedy": float(H[g]), "H_max": float(H.max()), "ER1_of_entropy_best": float(er1[E].min() / N), "ER1_min": float(er1.min() / N)}
        out.append(dict(r, **c))
    json.dump(out, open("s5_coord_L%d.json" % L, "w"), indent=0)
    gains = np.array([r["rel_gain_opt_vs_greedy"] for r in out]); myo = gains > 1e-9
    print("L", L, "states", len(out), "greedy strictly myopic (opt < greedy) in", int(myo.sum()), "mean rel gain %.4f max %.4f" % (gains.mean(), gains.max()))
    for k in ("c_gap2", "c_proxy", "c_ent", "c_shellness"):
        a = np.array([bool(r[k]) for r in out])
        for v in (True, False):
            m = a == v
            if m.any(): print("  %-12s=%-5s n %3d  myopic %3d (%.2f)  mean rel gain %.4f  max %.4f" % (k, v, m.sum(), (myo & m).sum(), (myo & m).sum() / m.sum(), gains[m].mean(), gains[m].max()))
    for k in ("c_tie", "c_maxcell", "c_H_deficit", "c_log2N"):
        a = np.array([float(r[k]) for r in out])
        # rank correlation with the gain, and the gain split at the median
        rk = np.argsort(np.argsort(a)); rg = np.argsort(np.argsort(gains)); rho = np.corrcoef(rk, rg)[0, 1] if a.std() > 0 else float("nan")
        med = np.median(a); hi = a > med; lo = ~hi
        print("  %-12s spearman %.3f | above median: n %d myopic %d mean %.4f | at/below: n %d myopic %d mean %.4f" % (k, rho, hi.sum(), (myo & hi).sum(), gains[hi].mean() if hi.any() else 0, lo.sum(), (myo & lo).sum(), gains[lo].mean() if lo.any() else 0))
    print("top states by rel gain:")
    for r in sorted(out, key=lambda r: -r["rel_gain_opt_vs_greedy"])[:12]:
        print("  ", r["family"], r["par"], "N0", r["N0"], "rel %.4f" % r["rel_gain_opt_vs_greedy"], "E g/x/o %.3f/%.3f/%.3f" % (r["E_greedy"], r["E_twostep"], r["E_opt"]), "ent-disjoint", r["c_ent"], "Hdef %.3f" % r["c_H_deficit"], "maxcell %.2f" % r["c_maxcell"], "gap2 %.3f" % r["gap2"], "blocks", r["block_sizes"], r["block_ones"])

if __name__ == "__main__":
    main()
