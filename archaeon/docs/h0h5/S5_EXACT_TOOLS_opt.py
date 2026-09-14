"""Full-horizon exact policies over every shell / two-block product state at L (N <= NMAX).
OPT: adaptive policy minimising expected probes-to-identify (DP over reachable subsets, all 2^L probes).
GREEDY: exact one-step ER minimiser, lexicographic tie-break, followed to identification.
TWOSTEP: exact V2 minimiser (ties: ER1, then lex), followed to identification.
Outputs per state: E[probes] for each, per-target paired comparison OPT vs GREEDY, the two-step gap (coordinate
candidate), the structural proxy, and the number of DP subsets touched (work)."""
import json, sys, time
from functools import lru_cache
import numpy as np
sys.path.insert(0, ".")
from s5_explore import World, block_summary

def main():
    L = int(sys.argv[1]); NMAX = int(sys.argv[2]); W = World(L); res = []; t0 = time.time(); seen = set()
    fam = [("shell", {"m": m}, [(0, m)]) for m in range(1, L)]
    for a in range(1, L):
        b = L - a; xa = (1 << a) - 1
        for uA in range(0, a + 1):
            for uB in range(0, b + 1):
                fam.append(("prod2", {"a": a, "b": b, "uA": uA, "uB": uB}, [(0, uA + uB), (xa, (a - uA) + uB)]))
    dtype = np.arange(1).dtype
    for name, par, fos in fam:
        S0 = W.feasible(fos)
        if len(S0) <= 2 or len(S0) > NMAX or S0.tobytes() in seen: continue
        seen.add(S0.tobytes()); N0 = len(S0); work = {"subsets": 0}
        @lru_cache(maxsize=None)
        def opt(key):
            S = np.frombuffer(key, dtype=S0.dtype)
            if len(S) == 1: return (0.0, -1)
            work["subsets"] += 1
            er, nn = W.er1num_all(S); best = (None, -1)
            # probes inducing the SAME set-partition of S are equivalent for every continuation: keep the smallest probe of each class
            lab = W.D[:, S].astype(np.int64)
            first = np.zeros_like(lab)
            for i in range(lab.shape[0]):
                _, inv = np.unique(lab[i], return_inverse=True); first[i] = inv
            _, reps = np.unique(first, axis=0, return_index=True)
            order = sorted(int(q) for q in reps if nn[q].max() != len(S))
            order.sort(key=lambda q: (int(er[q]), q))                 # promising first (does not change the optimum); ties by smallest probe
            for q in order:
                c = 1.0
                for e in range(L + 1):
                    if nn[q, e] > 1:
                        c += (nn[q, e] / len(S)) * opt(S[W.D[q, S] == e].tobytes())[0]
                        if best[0] is not None and c >= best[0] - 1e-12: break
                if best[0] is None or c < best[0] - 1e-12: best = (c, q)
            return best
        def v2pick(S):
            er1, nn = W.er1num_all(S); v2 = np.zeros(1 << L, dtype=np.int64)
            for q in range(1 << L):
                tot = 0
                for e in range(L + 1):
                    if nn[q, e] == 0: continue
                    tot += 1 if nn[q, e] == 1 else W.best1num(S[W.D[q, S] == e])
                v2[q] = tot
            c = np.flatnonzero(v2 == v2.min()); c = c[er1[c] == er1[c].min()]; return int(c[0]), er1, v2
        def greedypick(S):
            er, _ = W.er1num_all(S); return int(np.flatnonzero(er == er.min())[0])
        cache = {}
        def follow(policy, t):
            S = S0; k = 0
            while len(S) > 1:
                key = (policy, S.tobytes())
                if key not in cache:
                    cache[key] = opt(S.tobytes())[1] if policy == "opt" else (greedypick(S) if policy == "greedy" else v2pick(S)[0])
                q = cache[key]; S = S[W.D[q, S] == W.D[q, t]]; k += 1
            return k
        eo = opt(S0.tobytes())[0]
        per = {p: [follow(p, int(t)) for t in S0] for p in ("greedy", "twostep", "opt")}
        eg = float(np.mean(per["greedy"])); ex = float(np.mean(per["twostep"])); eo2 = float(np.mean(per["opt"]))
        assert abs(eo - eo2) < 1e-9, (eo, eo2)
        q1, er1, v2 = v2pick(S0); Gs = np.flatnonzero(er1 == er1.min()); gap2 = (int(v2[Gs].min()) - int(v2.min())) / N0
        bs = block_summary(W, fos, S0); unres = [x for x in bs if not x["resolved"]]
        d = [g - o for g, o in zip(per["greedy"], per["opt"])]
        r = {"family": name, "par": par, "N0": N0, "E_greedy": eg, "E_twostep": ex, "E_opt": eo, "rel_gain_opt_vs_greedy": (eg - eo) / eg,
             "opt_wins": sum(1 for v in d if v > 0), "greedy_wins": sum(1 for v in d if v < 0), "ties": sum(1 for v in d if v == 0),
             "gap2": gap2, "myopic2": gap2 > 0, "n_unresolved": len(unres), "block_sizes": [x["size"] for x in unres], "block_ones": [x["ones_possible"] for x in unres],
             "proxy": bool(len(unres) == 2 and min(x["size"] for x in unres) >= 3), "dp_subsets": work["subsets"], "log2N0": float(np.log2(N0))}
        res.append(r)
        print(name, par, "N0", N0, "E greedy %.4f twostep %.4f opt %.4f" % (eg, ex, eo), "rel %.4f" % r["rel_gain_opt_vs_greedy"], "gap2 %.4f" % gap2, "proxy", r["proxy"], "wins o/g/t", r["opt_wins"], r["greedy_wins"], r["ties"], "subsets", work["subsets"], "t=%.0fs" % (time.time() - t0), flush=True)
    json.dump(res, open("s5_opt_L%d.json" % L, "w"), indent=0)
    print("done", len(res))
    for label, f in (("myopic2", lambda r: r["myopic2"]), ("not_myopic2", lambda r: not r["myopic2"]), ("proxy", lambda r: r["proxy"]), ("not_proxy", lambda r: not r["proxy"]), ("shell", lambda r: r["family"] == "shell")):
        rs = [r for r in res if f(r)]
        if rs: print(label, "n", len(rs), "opt<greedy in", sum(1 for r in rs if r["E_opt"] < r["E_greedy"] - 1e-9), "mean rel gain %.4f" % np.mean([r["rel_gain_opt_vs_greedy"] for r in rs]), "max %.4f" % max(r["rel_gain_opt_vs_greedy"] for r in rs))

if __name__ == "__main__":
    main()
