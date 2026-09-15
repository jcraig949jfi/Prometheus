"""C3-3 region gate: what the declared rule actually yields, and what would fix it.

Harmonia[m2-f541bed9], 2026-09-14. Companion to c3_3_region_recompute_2026-09-14.json.
Exact binomial masses under the producer's own convention
(archaeon/producer/campaign_c3_3.py:91, idx = #edges strictly below popcount).
Options scored, none chosen here (the design is Archaeon's; the requirement is
mine):

  A  as declared: 10 popcount 'deciles', corpus 120
  B  10 regions, corpus raised until P(every region >= 8) >= 0.80
  C  9 regions: merge the two single-value bins pc04 (popcount 64) and
     pc05 (popcount 65), corpus 120
  D  option C with corpus raised as in B

For each: masses, expected occupancy, P(region >= 8), expected regions >= 8,
P(all regions >= 8) by Monte Carlo (occupancies are multinomial, not
independent), and the D3 band's corpus-level chance floor at true ratio 1.0.
Writes JSON to argv[1].
"""
import json
import math
import sys

import numpy as np

N_BITS = 128
EDGES10 = [57, 59, 61, 63, 64, 65, 67, 69, 71]
EDGES9 = [57, 59, 61, 63, 65, 67, 69, 71]
BAND = (1 / 3.0, 3.0)
REPS = 4000

pmf = [math.comb(N_BITS, k) / 2.0 ** N_BITS for k in range(N_BITS + 1)]


def masses(edges):
    m = [0.0] * (len(edges) + 1)
    for k, p in enumerate(pmf):
        m[sum(1 for e in edges if k > e)] += p
    return m


def binom_sf(n, p, k):
    return sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))


def mc(m, n, rng):
    all8 = 0
    any_out = 0
    ge2 = 0
    for _ in range(REPS):
        reg = rng.choice(len(m), size=n, p=m)
        occ = np.bincount(reg, minlength=len(m))
        all8 += bool((occ >= 8).all())
        vals = rng.normal(0.5, 0.0049, size=n)
        groups = [vals[reg == r] for r in range(len(m))]
        var = [np.var(g, ddof=1) if len(g) >= 2 else None for g in groups]
        k = 0
        for r in range(len(m)):
            if var[r] is None:
                continue
            num = sum((len(groups[o]) - 1) * var[o] for o in range(len(m)) if o != r and var[o] is not None)
            df = sum(len(groups[o]) - 1 for o in range(len(m)) if o != r and var[o] is not None)
            ratio = var[r] / (num / df)
            k += not (BAND[0] <= ratio <= BAND[1])
        any_out += k > 0
        ge2 += k >= 2
    return {"P_all_regions_ge8": all8 / REPS, "band_P_any_outside": any_out / REPS,
            "band_P_ge2_outside": ge2 / REPS}


def score(name, edges, n, rng):
    m = masses(edges)
    pge8 = [binom_sf(n, p, 8) for p in m]
    out = {"option": name, "n_regions": len(m), "corpus": n,
           "mass": [round(p, 5) for p in m], "min_mass": round(min(m), 5),
           "expected": [round(n * p, 2) for p in m],
           "P_ge8": [round(p, 4) for p in pge8],
           "expected_regions_ge8": round(sum(pge8), 3)}
    out.update(mc(m, n, rng))
    return out


def corpus_for(edges, target=0.80, rng=None):
    n = 120
    while True:
        m = masses(edges)
        # cheap screen with the independence product, then confirm by MC
        if float(np.prod([binom_sf(n, p, 8) for p in m])) >= target:
            if mc(m, n, rng)["P_all_regions_ge8"] >= target:
                return n
        n += 6


def main():
    rng = np.random.default_rng(914)
    res = []
    res.append(score("A as declared", EDGES10, 120, rng))
    nb = corpus_for(EDGES10, rng=rng)
    res.append(score("B 10 regions, corpus raised", EDGES10, nb, rng))
    res.append(score("C 9 regions (pc04+pc05 merged)", EDGES9, 120, rng))
    nd = corpus_for(EDGES9, rng=rng)
    res.append(score("D 9 regions, corpus raised", EDGES9, nd, rng))
    json.dump({"schema": "harmonia.c3_3_region_remedies.v1", "instance": "m2-f541bed9",
               "reps": REPS, "band": BAND, "options": res}, open(sys.argv[1], "w"), indent=1)
    for r in res:
        print("%-34s n=%3d regions=%d min_mass=%.4f E[>=8]=%.2f P(all>=8)=%.3f band_any=%.3f band_ge2=%.3f"
              % (r["option"], r["corpus"], r["n_regions"], r["min_mass"], r["expected_regions_ge8"],
                 r["P_all_regions_ge8"], r["band_P_any_outside"], r["band_P_ge2_outside"]))


if __name__ == "__main__":
    main()
