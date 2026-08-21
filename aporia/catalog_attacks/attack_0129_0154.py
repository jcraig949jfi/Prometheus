"""CAT-MATH-0129 (Erdos minimum overlap, exact n<=12) + CAT-MATH-0154 (EFL calibration).

0129: M(n) = min over |A|=n subsets of [1..2n] (B = complement) of
      max_k #{(a,b) in AxB : a-b = k}. Exact via FFT cross-correlation over all
      subsets with 1 in A (complement symmetry). Corrections binding: values must
      EXACTLY match the reviewer-executed 1,1,2,2,3,3,3,4,4,5,5,5; the M(n)/n
      trend is reported descriptively with NO bracket comparison.
0154: EFL configurations (n cliques of size n, pairwise sharing <=1 vertex):
      exhaustive canonical generation for n<=4; randomized certified sampling for
      n=5..7 (stated as sampling); verify n-colorability by exact backtracking.
      CALIBRATION: small n is classically settled; a PASS certifies the harness.
"""
from __future__ import annotations
import itertools
import json
import pathlib
import random
import time

import numpy as np

OUT = pathlib.Path(__file__).parent / "attack_0129_0154_results.json"
res = {}

# ================= 0129 =================
t0 = time.time()
TARGET = [1, 1, 2, 2, 3, 3, 3, 4, 4, 5, 5, 5]
Ms = []
for n in range(1, 13):
    L = 2 * n
    combos = itertools.combinations(range(1, L), n - 1)   # 0 always in A (complement symmetry)
    fft_len = 1
    while fft_len < 2 * L:
        fft_len <<= 1
    best = None
    CHUNK = 60_000
    it = iter(combos)
    while True:
        block = list(itertools.islice(it, CHUNK))
        if not block:
            break
        A = np.zeros((len(block), L), dtype=np.float64)
        A[:, 0] = 1.0
        for i, c in enumerate(block):
            A[i, list(c)] = 1.0
        B = 1.0 - A
        fa = np.fft.rfft(A, fft_len, axis=1)
        fb = np.fft.rfft(B[:, ::-1], fft_len, axis=1)     # reversal -> cross-correlation
        cc = np.fft.irfft(fa * fb, fft_len, axis=1)[:, : 2 * L - 1]
        m = np.rint(cc).astype(np.int64).max(axis=1)
        bm = int(m.min())
        best = bm if best is None else min(best, bm)
    Ms.append(best)
    print(f"0129 n={n}: M={best}")
print(f"0129 M(1..12) = {Ms}  match={Ms == TARGET}  ({time.time()-t0:.0f}s)")
res["min_overlap"] = {"M": Ms, "target": TARGET, "match": Ms == TARGET,
                      "trend_M_over_n": [round(m / n, 4) for n, m in enumerate(Ms, 1)],
                      "seconds": round(time.time() - t0, 1)}

# ================= 0154 =================
def gen_configs_exhaustive(n):
    """Canonical generation: cliques added one at a time; each new clique reuses a
    set of existing vertices (at most 1 shared with EACH earlier clique) and fills
    with fresh vertices introduced in increasing order. Dedupe by canonical
    intersection signature under clique relabeling."""
    configs = []
    seen = set()

    def canon(cliques):
        best = None
        for perm in itertools.permutations(range(len(cliques))):
            # signature: for each pair (i<j) the size of intersection, plus the
            # partition structure of shared vertices (which pairs share the SAME vertex)
            shared = {}
            for i in range(len(cliques)):
                for j in range(i + 1, len(cliques)):
                    inter = cliques[perm[i]] & cliques[perm[j]]
                    if inter:
                        v = next(iter(inter))
                        shared.setdefault(v, []).append((i, j))
            sig = tuple(sorted(tuple(sorted(v)) for v in shared.values()))
            if best is None or sig < best:
                best = sig
        return best

    def build(cliques, next_v):
        if len(cliques) == n:
            c = canon(cliques)
            if c not in seen:
                seen.add(c)
                configs.append([set(x) for x in cliques])
            return
        pool = sorted(set().union(*cliques)) if cliques else []
        # choose reused vertices: any subset of pool where no two reused vertices
        # come from... constraint: new clique shares <=1 with EACH existing clique
        for r in range(0, min(n, len(pool)) + 1):
            for reuse in itertools.combinations(pool, r):
                ok = True
                for cl in cliques:
                    if len(cl & set(reuse)) > 1:
                        ok = False
                        break
                if not ok:
                    continue
                fresh = list(range(next_v, next_v + (n - r)))
                newc = frozenset(list(reuse) + fresh)
                build(cliques + [newc], next_v + (n - r))
    build([frozenset(range(n))], n)
    return configs

def n_colorable(cliques, n, budget=2_000_000):
    verts = sorted(set().union(*cliques))
    vc = {v: [c for c in range(len(cliques)) if v in cliques[c]] for v in verts}
    # order vertices by number of cliques (most constrained first)
    verts.sort(key=lambda v: -len(vc[v]))
    color = {}
    nodes = 0
    def dfs(i):
        nonlocal nodes
        if i == len(verts):
            return True
        nodes += 1
        if nodes > budget:
            raise TimeoutError
        v = verts[i]
        used = set()
        for c in vc[v]:
            for w in cliques[c]:
                if w in color:
                    used.add(color[w])
        for col in range(n):
            if col not in used:
                color[v] = col
                if dfs(i + 1):
                    return True
                del color[v]
        return False
    return dfs(0)

t0 = time.time()
efl = {}
for n in (2, 3, 4):
    cfgs = gen_configs_exhaustive(n)
    bad = 0
    for cl in cfgs:
        if not n_colorable([frozenset(c) for c in cl], n):
            bad += 1
    efl[n] = {"mode": "exhaustive-canonical", "configs": len(cfgs), "uncolorable": bad}
    print(f"0154 n={n}: {len(cfgs)} configs (canonical), uncolorable={bad}")

rng = random.Random(20260821)
for n in (5, 6, 7):
    bad = 0; timeouts = 0; N_SAMP = 200
    for _ in range(N_SAMP):
        cliques = [frozenset(range(n))]
        next_v = n
        for _k in range(n - 1):
            pool = sorted(set().union(*cliques))
            reuse = []
            rng.shuffle(pool)
            for v in pool:
                if rng.random() < 0.35 and len(reuse) < n:
                    cand = reuse + [v]
                    if all(len(set(cand) & cl) <= 1 for cl in cliques):
                        reuse = cand
            fresh = list(range(next_v, next_v + (n - len(reuse))))
            cliques.append(frozenset(reuse + fresh))
            next_v += n - len(reuse)
        try:
            if not n_colorable(cliques, n):
                bad += 1
        except TimeoutError:
            timeouts += 1
    efl[n] = {"mode": "randomized-sampling (NOT exhaustive)", "configs": N_SAMP,
              "uncolorable": bad, "search_timeouts": timeouts}
    print(f"0154 n={n}: {N_SAMP} sampled configs, uncolorable={bad}, timeouts={timeouts}")
res["efl"] = efl
res["efl_seconds"] = round(time.time() - t0, 1)

OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
print(f"-> {OUT.name}")
