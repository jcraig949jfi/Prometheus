"""PARADIGM-P26 worked example — Continuous Relaxation / LP Bound, executed.

The paradigm's move: relax a discrete-extremal problem to a continuous LP
whose optimum is computable; a CONSTRUCTIVE witness meeting the relaxation
proves optimality (Cohn-Elkies/Viazovska shape). Executable instance: the
Delsarte LP bound for binary codes A(n, d), with:

  - Krawtchouk polynomials DERIVED exactly (explicit alternating-sum formula
    in integers, gated on the orthogonality identity sum_j C(n,j) K_k(j)^2
    = 2^n C(n,k) — an exact-integer comparator).
  - LP upper bound via scipy linprog on the distance distribution (B_0 = 1,
    B_j = 0 for 0 < j < d, Krawtchouk nonnegativity constraints).
  - LOWER bounds by exact exhaustive maximum-code search for n <= 6 (branch
    and bound over the 2^n hypercube) and by CONSTRUCTION for (7,3): the
    Hamming [7,4] code built from its parity-check matrix, its 16 codewords
    and min distance 3 verified over all 120 pairs — the 'magic witness'
    role at toy scale.
  - The sweep reports where the pincer CLOSES (LP == witness: optimality
    PROVEN, the paradigm's payoff) and where it GAPS (LP > best code: the
    relaxation is honest about its looseness) — both outcomes are structure,
    and which cases close is READ FROM THE RUN, not assumed.

Pre-stated readings (BEFORE run):
  RELAXATION-INFORMATIVE  Krawtchouk gate exact; every LP optimum >= its
                          case's witness (LP is a valid upper bound — any
                          witness EXCEEDING the LP is an instrument fault);
                          at least one case CLOSES (perfect-code territory).
  LP-FAULT                instrument-first: Krawtchouk signs, constraint
                          direction, linprog tolerance (bounds reported to
                          1e-6 and rounded honestly).
"""
from __future__ import annotations
import json
import pathlib
from itertools import combinations
from math import comb

import numpy as np
from scipy.optimize import linprog

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p26_results.json"


def kraw(n, k, j):
    return sum((-1) ** i * comb(j, i) * comb(n - j, k - i) for i in range(k + 1))


# --- Krawtchouk gate: exact orthogonality ------------------------------------
for n in (5, 6, 7):
    for k in range(n + 1):
        lhs = sum(comb(n, j) * kraw(n, k, j) ** 2 for j in range(n + 1))
        assert lhs == 2 ** n * comb(n, k), f"orthogonality FAILS at n={n},k={k}"
print("Krawtchouk gate: orthogonality exact for n in {5,6,7} — PASS", flush=True)


def lp_bound(n, d):
    js = list(range(d, n + 1))
    c = [-1.0] * len(js)                          # maximize sum B_j
    A_ub, b_ub = [], []
    for k in range(1, n + 1):
        A_ub.append([-float(kraw(n, k, j)) for j in js])
        b_ub.append(float(kraw(n, k, 0)))         # sum B_j K_k(j) >= -K_k(0)
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None)] * len(js), method="highs")
    assert res.success, f"LP failed at ({n},{d})"
    return 1.0 - res.fun


def exact_max_code(n, d):
    words = list(range(2 ** n))
    best = [0]
    def compatible(w, chosen):
        return all(bin(w ^ c).count("1") >= d for c in chosen)
    def bnb(start, chosen):
        if len(chosen) + (len(words) - start) <= best[0]:
            return
        best[0] = max(best[0], len(chosen))
        for i in range(start, len(words)):
            if compatible(words[i], chosen):
                chosen.append(words[i])
                bnb(i + 1, chosen)
                chosen.pop()
    bnb(0, [])
    return best[0]


def hamming_7_4():
    H = [(1, 0, 1, 0, 1, 0, 1), (0, 1, 1, 0, 0, 1, 1), (0, 0, 0, 1, 1, 1, 1)]
    code = [w for w in range(2 ** 7)
            if all(sum((w >> (6 - i)) & 1 for i in range(7) if row[i]) % 2 == 0 for row in H)]
    dmin = min(bin(a ^ b).count("1") for a, b in combinations(code, 2))
    return len(code), dmin


CASES = [(5, 3), (6, 3), (6, 4), (7, 3)]
rows = []
closed = 0
ok = True
for n, d in CASES:
    ub = lp_bound(n, d)
    if n <= 6:
        lb = exact_max_code(n, d)
        lb_kind = "exhaustive-exact"
    else:
        size, dmin = hamming_7_4()
        assert dmin >= 3 and size == 16, f"Hamming construction FAILS: {size}, dmin {dmin}"
        lb = size
        lb_kind = "constructed (Hamming [7,4], dmin verified over 120 pairs)"
    ok &= (lb <= ub + 1e-6)
    meets = abs(ub - lb) < 1e-6
    closed += meets
    rows.append({"n": n, "d": d, "lp_upper": round(ub, 6), "lower": lb,
                 "lower_kind": lb_kind, "closes": bool(meets)})
    print(f"A({n},{d}): LP upper {ub:.6f}  lower {lb} ({lb_kind})  "
          f"{'CLOSES - optimality PROVEN' if meets else 'gap'}", flush=True)

verdict = "RELAXATION-INFORMATIVE" if (ok and closed >= 1) else "LP-FAULT"
print(f"-> {verdict} ({closed}/{len(CASES)} cases close)", flush=True)
OUT.write_text(json.dumps({
    "protocol": "Delsarte LP (exact Krawtchouks, orthogonality-gated) vs exact exhaustive codes (n<=6) and the constructed Hamming [7,4] witness; closures read from the run",
    "cases": rows, "n_closed": closed, "verdict": verdict}, indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
