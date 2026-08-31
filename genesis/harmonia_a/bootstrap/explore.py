"""BOOTSTRAP explorations -- exploratory evidence only, per expedition brief s.3.
Five bounded deterministic computations. Nothing here is a scientific finding."""
import itertools, json, time
import numpy as np

out = {}

# ---- P1: Frankl union-closed, ground set n<=4, exhaustive
def frankl(n):
    universe = list(range(n)); sets = list(range(1 << n))
    worst = 1.0; counts = 0; families_checked = 0
    # families = subsets of nonempty sets, must contain their unions; require nonempty family with at least one nonempty set
    all_sets = range(1, 1 << n)
    from itertools import combinations
    # enumerate union-closed families over the 2^n - 1 nonempty sets: too many for n=4 (2^15);
    # instead enumerate all families as bitmasks over sets for n<=3, and for n=4 sample closure-generated families
    results = []
    if n <= 3:
        m = (1 << n) - 1  # nonempty sets
        for fam_mask in range(1, 1 << m):
            fam = [s + 1 for s in range(m) if (fam_mask >> s) & 1]
            ok = True
            for a, b in combinations(fam, 2):
                if (a | b) not in fam: ok = False; break
            if not ok: continue
            families_checked += 1
            N = len(fam)
            best = max(sum(1 for s in fam if (s >> e) & 1) for e in range(n))
            frac = best / N
            worst = min(worst, frac)
    return dict(n=n, union_closed_families=families_checked, worst_max_element_frequency=worst)
t0=time.time(); out["P1_frankl"] = [frankl(2), frankl(3)]
# n=4: generate closure of random generating sets
rng = np.random.default_rng(7); worst4 = 1.0
for trial in range(20000):
    k = rng.integers(1, 6)
    gens = set(int(x) for x in rng.integers(1, 16, size=k))
    fam = set(gens)
    frontier = True
    while frontier:
        add = {a | b for a in fam for b in fam} - fam
        frontier = bool(add); fam |= add
    N = len(fam)
    best = max(sum(1 for s in fam if (s >> e) & 1) for e in range(4))
    worst4 = min(worst4, best / N)
out["P1_frankl"].append(dict(n=4, sampled_closures=20000, worst_max_element_frequency=worst4))
out["P1_time"] = round(time.time()-t0,1)

# ---- P2: Lehmer -- Mahler measure floor over small integer polynomials
def mahler(coeffs):
    r = np.roots(coeffs)
    return float(abs(coeffs[0]) * np.prod(np.maximum(1.0, np.abs(r))))
t0=time.time()
best = []
rng = np.random.default_rng(11)
lehmer = [1,1,0,-1,-1,-1,-1,-1,0,1,1]  # Lehmer's polynomial deg 10
for trial in range(120000):
    d = int(rng.integers(4, 11))
    c = rng.integers(-1, 2, size=d+1); c[0]=1; c[-1]=int(rng.choice([-1,1]))
    m = mahler(c)
    if 1.0 + 1e-9 < m < 1.30:
        # exclude cyclotomic-ish (measure 1); record near-floor
        best.append((round(m,6), c.tolist()))
best.sort(); uniq=[]; seen=set()
for m,c in best:
    if m not in seen: uniq.append((m,c)); seen.add(m)
out["P2_lehmer"] = dict(lehmer_measure=round(mahler(lehmer),6),
                        near_floor_measures=[m for m,_ in uniq[:8]],
                        n_sampled=120000, floor_beaten=bool(uniq and uniq[0][0] < mahler(lehmer)-1e-6),
                        time=round(time.time()-t0,1))

# ---- P3: lonely runner, k runners (k-1 nonzero distinct speeds), verify gap 1/k reachable
def lonely(speeds, grid=20011):
    # max over t of min distance of s*t mod 1 to 0
    t = np.arange(1, grid) / grid
    dmin = np.ones(len(t))
    for s in speeds:
        x = (s * t) % 1.0
        dmin = np.minimum(dmin, np.minimum(x, 1 - x))
    return float(dmin.max())
t0=time.time(); worst_cases = {}
for k, speedsets in ((3, [(1,2)]), (4, [(1,2,3),(1,2,4),(1,3,4),(2,3,5),(1,4,6)]),
                     (5, [(1,2,3,4),(1,3,4,7),(2,3,4,5)])):
    vals = {str(s): round(lonely(s),5) for s in speedsets}
    worst_cases[k] = dict(bound=round(1.0/k,5), cases=vals,
                          all_meet_bound=all(v >= 1.0/k - 2e-4 for v in vals.values()))
out["P3_lonely_runner"] = worst_cases; out["P3_time"]=round(time.time()-t0,1)

# ---- P4: Collatz -- do low 2-adic digits predict stopping time?
def stopping(n0, cap=10000):
    n, c = n0, 0
    while n != 1 and c < cap:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        c += 1
    return c
t0=time.time()
N = 2**16
sts = np.array([stopping(n) for n in range(1, N)])
lows = np.array([n & 0xFF for n in range(1, N)])
# variance in stopping time explained by low 8 bits (eta^2 by residue class)
gm = sts.mean(); ssb = 0.0
for r in range(256):
    m = lows == r
    if m.any(): ssb += m.sum() * (sts[m].mean() - gm) ** 2
out["P4_collatz"] = dict(n=int(N-1), eta2_low8bits_on_stopping=round(float(ssb / ((sts - gm) ** 2).sum()), 4),
                         mean_stop=round(float(gm),2), time=round(time.time()-t0,1))

# ---- P5: shortest addition chains, exact l(n) for n<=256 via IDDFS
def chain_len(target):
    def dfs(chain, depth_left):
        top = chain[-1]
        if top == target: return True
        if depth_left == 0: return False
        if top * (2 ** depth_left) < target: return False
        sums = sorted({a + b for a in chain for b in chain if a + b > top and a + b <= target}, reverse=True)
        for s in sums:
            if dfs(chain + [s], depth_left - 1): return True
        return False
    d = 0
    while True:
        if dfs([1], d): return d
        d += 1
t0=time.time()
l = {n: chain_len(n) for n in range(2, 129)}
# Scholz conjecture spot check: l(2^n - 1) <= n - 1 + l(n) for small n
scholz = {}
for n in (2,3,4,5,6):
    lhs = chain_len(2**n - 1); rhs = n - 1 + l.get(n, chain_len(n))
    scholz[n] = dict(l_2n_minus_1=lhs, bound=rhs, holds=bool(lhs <= rhs))
# mutation-geometry observation: how catastrophic is a single-step substitution in a chain?
out["P5_addition_chains"] = dict(l_128=l[128], l_127=l[127], l_77=l[77],
                                 scholz_check=scholz, time=round(time.time()-t0,1))

json.dump(out, open("bootstrap_results.json","w"), indent=1)
for k,v in out.items():
    print(k, ":", json.dumps(v)[:300])
