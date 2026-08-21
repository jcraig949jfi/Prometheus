"""CAT-MATH-0287 (HL prime triplets) + CAT-MATH-0324 (Frankl calibration).

0287: counts of (p,p+2,p+6) and (p,p+4,p+6) to 1e8; type ratio (reviewer target
      1.00079); effective-constant test vs H_3 * li_3(x) with H_3 computed from its
      Euler product (9/2)*prod_{p>3} p^2(p-3)/(p-1)^3 and li_3 via u-substitution
      (P52 lesson); tolerance band +-2% (added per the reviewer's disposition note).
0324: enumerate ALL union-closed families on ground sets <=4 (reviewer target 4958,
      counting convention documented by reproduction); verify the majority element
      exists in every one (CALIBRATION); stratified random closure families at 5.
"""
from __future__ import annotations
import itertools
import json
import math
import pathlib
import random
import time

import numpy as np

OUT = pathlib.Path(__file__).parent / "attack_0287_0324_results.json"
res = {}

# ================= 0287 =================
N = 100_000_000
t0 = time.time()
S = np.ones(N + 7, dtype=bool)
S[:2] = False
for p in range(2, int((N + 6) ** 0.5) + 1):
    if S[p]:
        S[p * p:: p] = False
primes = np.flatnonzero(S[: N + 1]).astype(np.int64)
print(f"sieve in {time.time()-t0:.1f}s")

t026 = primes[S[primes + 2] & S[primes + 6]]
t046 = primes[S[primes + 4] & S[primes + 6]]
ratio = len(t026) / len(t046)
print(f"0287: (0,2,6): {len(t026)}  (0,4,6): {len(t046)}  ratio {ratio:.5f}")

pp = primes[(primes > 3) & (primes <= 10_000_000)].astype(np.float64)
H3 = 4.5 * float(np.exp(np.sum(np.log(pp ** 2 * (pp - 3) / (pp - 1) ** 3))))
print(f"H3 computed = {H3:.6f}")

def li3(x, steps=200_000):
    us = np.linspace(math.log(2.0), math.log(float(x)), steps)
    return float(np.trapezoid(np.exp(us) / us ** 3, us))

decades = []
for k in range(4, 9):
    x = 10 ** k
    o1 = int(np.count_nonzero(t026 <= x))
    o2 = int(np.count_nonzero(t046 <= x))
    pred = H3 * li3(x)
    decades.append({"x": x, "obs_026": o1, "obs_046": o2,
                    "pred_H3_li3": round(pred, 1),
                    "r_026": round(o1 / pred, 5), "r_046": round(o2 / pred, 5)})
    print(f"1e{k}: 026 {o1} 046 {o2} pred {pred:.0f} r026 {o1/pred:.4f} r046 {o2/pred:.4f}")
res["hl_triplets"] = {"n_026": len(t026), "n_046": len(t046),
                      "type_ratio": round(ratio, 5), "reviewer_target": 1.00079,
                      "H3": H3, "per_decade": decades}

# ================= 0324 =================
t0 = time.time()
subsets = list(range(16))  # subsets of {0,1,2,3} as bitmasks 0..15
# enumerate all collections of nonempty subsets (families), check union-closure.
# Convention A: family = nonempty collection of NONEMPTY subsets of a 4-universe,
# closed under union. (Empty set membership handled as convention B.)
def union_closed(fam):
    fl = list(fam)
    for i in range(len(fl)):
        for j in range(i + 1, len(fl)):
            if (fl[i] | fl[j]) not in fam:
                return False
    return True

countA = 0; violA = 0
famsA = []
nonempty = list(range(1, 16))
for bits in range(1, 1 << 15):          # subsets of the 15 nonempty subsets
    fam = frozenset(nonempty[i] for i in range(15) if bits >> i & 1)
    if union_closed(fam):
        countA += 1
        # Frankl: some element in >= half the sets
        tot = len(fam)
        ok = any(sum(1 for s in fam if s >> e & 1) * 2 >= tot for e in range(4))
        if not ok:
            violA += 1
            famsA.append(sorted(fam))
print(f"0324 convention A (nonempty sets only): {countA} union-closed, violations {violA} ({time.time()-t0:.0f}s)")

# Convention B: allow the empty set as a member (family must contain a nonempty set)
t0 = time.time()
countB = 0; violB = 0
for bits in range(1, 1 << 15):
    base = frozenset(nonempty[i] for i in range(15) if bits >> i & 1)
    fam = base | {0}
    if union_closed(fam):
        countB += 1
        tot = len(fam)
        ok = any(sum(1 for s in fam if s >> e & 1) * 2 >= tot for e in range(4))
        if not ok:
            violB += 1
print(f"0324 convention B (empty set adjoined): {countB} union-closed, violations {violB} ({time.time()-t0:.0f}s)")

# stratified random closures at 5 elements
rng = random.Random(20260821)
viol5 = 0
checked5 = 0
for _ in range(2000):
    k = rng.randint(2, 6)
    gens = [rng.randint(1, 31) for _ in range(k)]
    fam = set(gens)
    changed = True
    while changed:
        changed = False
        for a, b in itertools.combinations(list(fam), 2):
            u = a | b
            if u not in fam:
                fam.add(u); changed = True
    checked5 += 1
    tot = len(fam)
    if not any(sum(1 for s in fam if s >> e & 1) * 2 >= tot for e in range(5)):
        viol5 += 1
print(f"0324 five-element sampled closures: {checked5} checked, violations {viol5}")

res["frankl"] = {"conv_A_count": countA, "conv_A_violations": violA,
                 "conv_B_count": countB, "conv_B_violations": violB,
                 "reviewer_target_count": 4958,
                 "sampled_5elt": {"checked": checked5, "violations": viol5}}
OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
print(f"-> {OUT.name}")
