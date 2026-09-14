"""S5 phase 1-2 exploration: EXACT myopia over structurally defined evidence states.
No producer (G/W/M) is called. Definitions:
  state E = list of (fossil bits, mismatch count m); T(E) = feasible targets (brute force, L <= 10)
  ER1(q|E)  = sum_d n_d^2 / N                       (one-step expected remaining)
  V2(q|E)   = (1/N) sum_d min_{q'} sum_e n_e(q'|T_d)^2   (expected remaining after the BEST second probe, given q first)
  G*(E)     = argmin_q ER1 (exact, all 2^L probes)  ; V2* = min_q V2
  gap_best  = min_{q in G*} V2(q) - V2*   (>0  <=>  NO one-step optimal probe is two-step optimal: the state is MYOPIC)
  gap_lex   = V2(lexmin G*) - V2*         (what a lexicographic tie-break actually pays)
"""
import itertools, json, sys, time
import numpy as np

def popcount_table(L):
    n = 1 << L
    D = np.zeros((n, n), dtype=np.uint8)
    xs = np.arange(n)
    for q in range(n):
        D[q] = np.array([bin(q ^ t).count("1") for t in xs], dtype=np.uint8) if L <= 6 else None
    return D

def dist_matrix(L):
    n = 1 << L
    xs = np.arange(n, dtype=np.int64)
    X = ((xs[:, None] >> np.arange(L)) & 1).astype(np.uint8)          # n x L bits
    D = np.zeros((n, n), dtype=np.uint8)
    for j in range(L):
        D += (X[:, j][:, None] != X[:, j][None, :])
    return D, X

class World:
    def __init__(self, L):
        self.L = L; self.D, self.X = dist_matrix(L); self.cache = {}
    def feasible(self, fossils):
        T = np.arange(1 << self.L)
        for x, m in fossils:
            T = T[self.D[x, T] == m]
        return T
    def counts(self, S):
        """n[q, e] = number of targets in S at distance e from probe q (all q)."""
        M = self.D[:, S]
        return np.stack([(M == e).sum(1) for e in range(self.L + 1)], axis=1)
    def er1num_all(self, S):
        n = self.counts(S); return (n.astype(np.int64) ** 2).sum(1), n
    def best1num(self, S):
        key = S.tobytes()
        v = self.cache.get(key)
        if v is None:
            v = int(self.er1num_all(S)[0].min()); self.cache[key] = v
        return v
    def analyse(self, fossils):
        S = self.feasible(fossils); N = len(S)
        er1, n = self.er1num_all(S)
        v2 = np.zeros(1 << self.L, dtype=np.int64)
        for q in range(1 << self.L):
            tot = 0
            for e in range(self.L + 1):
                if n[q, e] == 0: continue
                if n[q, e] == 1: tot += 1; continue
                tot += self.best1num(S[self.D[q, S] == e])
            v2[q] = tot
        er1min = int(er1.min()); Gstar = np.flatnonzero(er1 == er1min)
        v2min = int(v2.min()); V2star = np.flatnonzero(v2 == v2min)
        gap_best = int(v2[Gstar].min()) - v2min
        gap_lex = int(v2[Gstar[0]]) - v2min            # lexicographic on the integer = smallest bitstring with bit0 as LSB; fine for a tie-break
        # also: the best two-step probe's one-step cost (how much immediate reduction the far-sighted probe gives up)
        er1_of_v2best = int(er1[V2star].min())
        return {"N": N, "ER1*": er1min / N, "|G*|": int(len(Gstar)), "V2(G*)best": int(v2[Gstar].min()) / N, "V2(G*)lex": int(v2[Gstar[0]]) / N,
                "V2*": v2min / N, "|V2*|": int(len(V2star)), "ER1(V2best)": er1_of_v2best / N, "gap_best": gap_best / N, "gap_lex": gap_lex / N,
                "myopic": gap_best > 0, "S": S, "Gstar": Gstar, "V2star": V2star}

def blocks_of_state(L, fossils):
    """Structural, target-free description: positions grouped by fossil column pattern; per block the feasible set of 'ones' counts."""
    pats = {}
    for j in range(L):
        pat = tuple((x >> j) & 1 for x, _ in fossils); pats.setdefault(pat, []).append(j)
    return pats

def block_summary(W, fossils, S):
    pats = blocks_of_state(W.L, fossils); out = []
    for pat, pos in sorted(pats.items()):
        us = sorted({int(sum((t >> j) & 1 for j in pos)) for t in S})
        out.append({"size": len(pos), "ones_possible": us, "resolved": (len(us) == 1 and us[0] in (0, len(pos)))})
    return out

def bits(x, L): return format(x, "0%db" % L)[::-1]   # bit j = position j

def main():
    L = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    W = World(L); rows = []; t0 = time.time()
    fam = []
    # F1 single shell: one fossil 0^L with m ones
    for m in range(1, L):
        fam.append(("shell", {"m": m}, [(0, m)]))
    # F2 two-block product: fossils 0^L (m0=uA+uB) and 1^a 0^b (m1=(a-uA)+uB)
    for a in range(1, L):
        b = L - a; xa = (1 << a) - 1
        for uA in range(0, a + 1):
            for uB in range(0, b + 1):
                fam.append(("prod2", {"a": a, "b": b, "uA": uA, "uB": uB}, [(0, uA + uB), (xa, (a - uA) + uB)]))
    # F3 three-block product
    for a in (range(1, L - 1) if L <= 9 else []):
        for b in range(1, L - a):
            c = L - a - b; xa = (1 << a) - 1; xb = ((1 << b) - 1) << a
            for uA in range(0, a + 1):
                for uB in range(0, b + 1):
                    for uC in range(0, c + 1):
                        fam.append(("prod3", {"a": a, "b": b, "c": c, "uA": uA, "uB": uB, "uC": uC},
                                    [(0, uA + uB + uC), (xa, (a - uA) + uB + uC), (xb, uA + (b - uB) + uC)]))
    seen = set()
    for name, par, fos in fam:
        S = W.feasible(fos)
        if len(S) <= 2: continue
        key = S.tobytes()
        if key in seen: continue        # identical feasible sets are the same state
        seen.add(key)
        r = W.analyse(fos); bs = block_summary(W, fos, r["S"])
        unres = [b for b in bs if not b["resolved"]]
        row = {"family": name, "par": par, "N": r["N"], "ER1*": round(r["ER1*"], 4), "V2*": round(r["V2*"], 4), "V2(G*)best": round(r["V2(G*)best"], 4), "V2(G*)lex": round(r["V2(G*)lex"], 4),
               "gap_best": round(r["gap_best"], 4), "gap_lex": round(r["gap_lex"], 4), "myopic": bool(r["myopic"]), "|G*|": r["|G*|"], "ER1(V2best)": round(r["ER1(V2best)"], 4),
               "n_unresolved_blocks": len(unres), "block_sizes": [b["size"] for b in unres], "block_ones": [b["ones_possible"] for b in unres],
               "G_probe": bits(int(r["Gstar"][0]), L), "V2_probe": bits(int(r["V2star"][0]), L)}
        rows.append(row)
        if r["myopic"]:
            print("MYOPIC", name, par, "N", r["N"], "ER1*", row["ER1*"], "V2(G*)best", row["V2(G*)best"], "V2*", row["V2*"], "gap", row["gap_best"], "blocks", row["block_sizes"], row["block_ones"], flush=True)
    print("states", len(rows), "myopic", sum(r["myopic"] for r in rows), "t=%.0fs" % (time.time() - t0))
    # coordinate screen: by number of unresolved blocks
    by = {}
    for r in rows:
        by.setdefault(r["n_unresolved_blocks"], []).append(r["myopic"])
    for k, v in sorted(by.items()):
        print("unresolved blocks", k, "states", len(v), "myopic", sum(v), "frac", round(sum(v) / len(v), 3))
    json.dump(rows, open(sys.argv[2] if len(sys.argv) > 2 else "s5_explore_L%d.json" % L, "w"), indent=0, default=int)

if __name__ == "__main__":
    main()
