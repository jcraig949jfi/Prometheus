"""W2-33 statistics over the five splice-on 7ae3 k=1 blocks (read-only over committed JSON)."""
import json, math, pathlib, random, itertools
HERE = pathlib.Path(__file__).resolve().parent
C = HERE.parents[1] / "campaigns" / "c9x-explore-2026-09-24"
S7 = "7ae3f9c1437c8000-s54765-tL-a0"
def L(f): return json.loads((C / f).read_text())
B = {
 "C9": [6, 0, 1, 1, 12, 3, 15, 2, 0, 1, 2, 7, 1, 0, 0, 0],   # verified against observatory/bundles_C9.tar.gz
 "C-NORECOMB": [r["depth"] for r in L("c_norecomb_confirm/RESULTS.json") if r["arm"] == "BASE" and r["spec"] == S7],
 "C-RUNAWAY": [r["depth"] for r in L("c_runaway_confirm/RESULTS.json") if r["arm"] == "BASE"],
 "X-H2-7AE3": [r["depth"] for r in L("x_h2_7ae3/RESULTS.json") if r["k"] == 1],
 "X-H2-NORECOMB": [r["depth"] for r in L("x_h2_norecomb/RESULTS.json") if r["arm"] == "BASE"],
}
out = {}
for k, d in B.items():
    n = len(d)
    out[k] = {"n": n, "ge1": sum(x >= 1 for x in d), "ge2": sum(x >= 2 for x in d), "ge3": sum(x >= 3 for x in d),
              "ge4": sum(x >= 4 for x in d), "ge5": sum(x >= 5 for x in d), "mean": round(sum(d) / n, 3), "max": max(d)}
    print(k, out[k])

def binom_tail(n, p, k):
    return sum(math.comb(n, j) * p**j * (1 - p)**(n - j) for j in range(k, n + 1))

def exact_homog(blocks, thr, nsim=200000, seed=1):
    """Exact-conditional (permutation/hypergeometric) homogeneity test: chi-square statistic,
    total hits fixed, Monte Carlo over random allocation of hits to runs."""
    ns = [len(B[b]) for b in blocks]; ks = [sum(x >= thr for x in B[b]) for b in blocks]
    N, K = sum(ns), sum(ks); p = K / N
    def chi(ks_):
        return sum((k - n * p) ** 2 / (n * p * (1 - p)) for k, n in zip(ks_, ns)) if 0 < p < 1 else 0
    obs = chi(ks); rng = random.Random(seed); lab = list(itertools.chain(*[[i] * n for i, n in enumerate(ns)]))
    ge = 0
    for _ in range(nsim):
        hit = rng.sample(range(N), K); c = [0] * len(ns)
        for h in hit: c[lab[h]] += 1
        ge += chi(c) >= obs - 1e-12
    return {"blocks": blocks, "thr": thr, "hits": ks, "n": ns, "chi2": round(obs, 3), "p_mc": ge / nsim}

res = {"blocks": out, "tests": []}
four = ["C-NORECOMB", "C-RUNAWAY", "X-H2-7AE3", "X-H2-NORECOMB"]
for blocks in (list(B), four, ["C-RUNAWAY", "X-H2-7AE3", "X-H2-NORECOMB"], ["C-NORECOMB", "X-H2-7AE3", "X-H2-NORECOMB"]):
    for thr in (1, 3, 4, 5):
        t = exact_homog(blocks, thr, nsim=40000); res["tests"].append(t); print(t)
# leave-one-out: C-NORECOMB against the other three post-C9 blocks
others = sum(sum(x >= 5 for x in B[b]) for b in four[1:]); no = sum(len(B[b]) for b in four[1:])
p0 = others / no
res["cnr_vs_rest"] = {"rest": [others, no], "p_binom_tail_ge5_of_24": binom_tail(24, p0, 5)}
# Fisher one-sided C-NORECOMB vs C-RUNAWAY on ge5
def fisher_ge(a, n1, b, n2):
    K = a + b; N = n1 + n2
    return sum(math.comb(n1, x) * math.comb(n2, K - x) for x in range(a, min(n1, K) + 1)) / math.comb(N, K)
res["fisher_cnr_vs_crw_ge5"] = fisher_ge(5, 24, 4, 150)
# conditional on reaching depth >= 1, is the tail different?
for b in four:
    d = [x for x in B[b] if x >= 1]
    print(b, "given>=1: n=%d ge3=%d ge5=%d" % (len(d), sum(x >= 3 for x in d), sum(x >= 5 for x in d)))
# post-hoc look-elsewhere: P(max standardized excess among 4 blocks >= observed) under pooled p (incl. multiplicity over 4 blocks)
ns = [len(B[b]) for b in four]; K = sum(sum(x >= 5 for x in B[b]) for b in four); N = sum(ns)
rng = random.Random(7); lab = list(itertools.chain(*[[i] * n for i, n in enumerate(ns)]))
ge = 0; nsim = 100000
for _ in range(nsim):
    c = [0] * 4
    for h in rng.sample(range(N), K): c[lab[h]] += 1
    ge += max(c[i] for i in range(4) if ns[i] <= 24) >= 5
res["p_any_small_block_ge5_of_9"] = ge / nsim
print(res["cnr_vs_rest"], res["fisher_cnr_vs_crw_ge5"], res["p_any_small_block_ge5_of_9"])
(HERE / "stats.json").write_text(json.dumps(res, indent=1))
