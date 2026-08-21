"""CAT-MATH-0211 + CAT-MATH-0212 — two CALIBRATION attacks (specs ELENCHUS-SOUND).

0211 Dedekind: M(0..6) by iterative monotone-pair construction
    (monotone functions on n+1 vars = pairs f<=g on n vars). Targets: the
    reviewer-executed 2,3,6,20,168,7581,7828354.
0212 van der Waerden: W(2,3)=9, W(2,4)=35, W(3,3)=27 by DFS backtracking
    (data_source names the pruning per the reviewer's note): extend positions
    left-to-right, prune on any monochromatic AP ending at the newest position;
    witness coloring must exist at W-1 and the full tree must exhaust at W.
CALIBRATION means: a PASS certifies the harness against theorems of finite
computation and says NOTHING about any open question.
"""
from __future__ import annotations
import json
import pathlib
import time

import numpy as np

OUT = pathlib.Path(__file__).parent / "attack_0211_0212_results.json"
res = {}

# ---------------- 0211 Dedekind ----------------
t0 = time.time()
levels = [np.array([0, 1], dtype=np.int64)]           # n=0: functions on 1 point
counts = [2]
for n in range(6):
    L = levels[-1]
    size = 1 << (1 << n)                              # bitmask width of level n
    if n < 5:
        # build explicit list for next level: h = f | (g << 2^n) for f <= g
        nxt = []
        for f in L:
            ge = L[(L & f) == f]                      # all g with f <= g
            nxt.append(f | (ge << (1 << n)))
        levels.append(np.concatenate(nxt))
        counts.append(len(levels[-1]))
    else:
        # M(6) = number of pairs f <= g in level 5 (no need to materialize)
        total = 0
        for f in L:
            total += int(np.count_nonzero((L & f) == f))
        counts.append(total)
dedekind = counts
print(f"0211 M(0..6) = {dedekind}  ({time.time()-t0:.1f}s)")
res["dedekind"] = {"M": dedekind, "seconds": round(time.time() - t0, 1),
                   "target": [2, 3, 6, 20, 168, 7581, 7828354],
                   "match": dedekind == [2, 3, 6, 20, 168, 7581, 7828354]}

# ---------------- 0212 van der Waerden ----------------
def has_ap_ending_at(colors, i, k):
    """Monochromatic k-AP ending at index i (0-based positions 0..i)?"""
    c = colors[i]
    for d in range(1, i // (k - 1) + 1):
        if all(colors[i - j * d] == c for j in range(1, k)) and colors[i] == c:
            return True
    return False

def exists_valid_coloring(n, r, k):
    """DFS: is there an r-coloring of [0,n) with no monochromatic k-AP?"""
    colors = [0] * n
    def dfs(i):
        if i == n:
            return True
        start_colors = range(1 if i == 0 else r)  # symmetry: pin color of first cell
        for c in (range(r) if i > 0 else range(1)):
            colors[i] = c
            if not has_ap_ending_at(colors, i, k):
                if dfs(i + 1):
                    return True
        return False
    return dfs(0)

t0 = time.time()
vdw = {}
for (r, k, W) in ((2, 3, 9), (2, 4, 35), (3, 3, 27)):
    t1 = time.time()
    witness_at_W_minus_1 = exists_valid_coloring(W - 1, r, k)
    none_at_W = not exists_valid_coloring(W, r, k)
    vdw[f"W({r},{k})"] = {"claimed": W, "witness_at_W-1": witness_at_W_minus_1,
                          "exhausted_at_W": none_at_W,
                          "confirmed": witness_at_W_minus_1 and none_at_W,
                          "seconds": round(time.time() - t1, 1)}
    print(f"0212 W({r},{k})={W}: witness@{W-1}={witness_at_W_minus_1}, "
          f"exhausted@{W}={none_at_W}  ({time.time()-t1:.1f}s)")
res["vdw"] = vdw
res["vdw_total_seconds"] = round(time.time() - t0, 1)

OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
print(f"-> {OUT.name}")
