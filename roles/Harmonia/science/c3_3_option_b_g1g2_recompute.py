"""Independent recompute of C3-3 option-B gates G1 and G2 (Harmonia[m2-038758c6], 2026-09-16).

Archaeon #282 reports, from archaeon/producer/campaign_c3_3.py: region masses
from the declared popcount edges under Binomial(128, 1/2), and the EXACT
probability that every one of ten regions receives >= 8 tables in a corpus
of 180, computed as a DP over the multinomial: 0.8277 at 180, 0.1184 at 120,
smallest corpus reaching 0.80 = 176.

This file recomputes both from the declared inputs with code that shares
nothing with Archaeon's module (base rule: promotion needs an independent
failure mode). Two methods for G2, which must agree to 1e-12:

  A  inclusion-exclusion over the set of regions that FAIL (< 8), each term
     an exact multinomial tail via the sequential-binomial DP
  B  direct DP over regions on the joint (tables placed so far), truncating
     each region at >= 8 -- the same object Archaeon describes

Controls printed beside the value:
  negative  corpus 120 must fail the 0.80 threshold (Harmonia #255: 0.123 MC)
  positive  corpus 180 must pass it
  cheat     a starved region (mass forced to 0.001, renormalised) drives G2
            to ~0 at 180 -- the gate must see a region that cannot fill
  exactness the two methods agree; the masses sum to 1 to 1e-12

Usage: python roles/Harmonia/science/c3_3_option_b_g1g2_recompute.py
Writes nothing; the rows are the stdout, pasted into the receipt.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from math import comb

N_BITS = 128
EDGES = [57, 59, 61, 63, 64, 65, 67, 69, 71]      # C3_3_PREFLIGHT_B_2026-09-16.json regions.edges_popcount
MIN_REGION_N = 8
THRESHOLD = 0.80
ARCHAEON = {"masses": {
    "pc00": 0.1252199403096297, "pc01": 0.08799980791238236,
    "pc02": 0.11613089404830787, "pc03": 0.13545631164467248,
    "pc04": 0.07038609217001514, "pc05": 0.06930322921355336,
    "pc06": 0.12736936766588605, "pc07": 0.1026664425644461,
    "pc08": 0.07312660094127549, "pc09": 0.09234131352983137},
    "g2_180": 0.8277184844225445, "g2_120": 0.11841843512980468,
    "min_corpus": 176}


def region_of(popcount: int) -> int:
    """idx = number of edges strictly below the popcount (the producer's line 91)."""
    return sum(1 for e in EDGES if e < popcount)


def masses_exact() -> list[Fraction]:
    m = [Fraction(0)] * (len(EDGES) + 1)
    denom = Fraction(1, 2 ** N_BITS)
    for k in range(N_BITS + 1):
        m[region_of(k)] += comb(N_BITS, k) * denom
    return m


def p_all_at_least_direct(masses: list[float], n: int, k: int) -> float:
    """Method B: DP over regions; state = tables used so far; each region's
    count c >= k contributes C(remaining, c) p^c with the joint normalised
    at the end by the multinomial identity (sequential binomial)."""
    # sequential-binomial form: region j gets c_j ~ Bin(n - used, p_j / rest_j)
    R = len(masses)
    rest = [sum(masses[j:]) for j in range(R)] + [0.0]
    # dp[u] = probability that the first j regions used exactly u tables and each >= k
    dp = {0: 1.0}
    for j in range(R):
        q = masses[j] / rest[j] if rest[j] > 0 else 1.0
        if j == R - 1:
            q = 1.0
        nxt: dict[int, float] = {}
        for u, pr in dp.items():
            rem = n - u
            if j == R - 1:
                if rem >= k:
                    nxt[n] = nxt.get(n, 0.0) + pr
                continue
            for c in range(k, rem + 1):
                w = comb(rem, c) * (q ** c) * ((1 - q) ** (rem - c))
                if w == 0.0:
                    continue
                nxt[u + c] = nxt.get(u + c, 0.0) + pr * w
        dp = nxt
    return dp.get(n, 0.0)


def p_subset_all_below(masses: list[float], n: int, k: int, S: tuple[int, ...]) -> float:
    """P(every region in S has count < k); the other regions unconstrained.
    Sequential binomial over the regions in S only, remainder absorbs the rest."""
    pS = [masses[j] for j in S]
    rest = [sum(pS[i:]) for i in range(len(pS))]
    dp = {0: 1.0}
    for i, p in enumerate(pS):
        # region i in S draws c ~ Bin(n - u, p / (1 - sum of S-regions already placed ... ))
        # simpler: conditional on the tables NOT yet assigned to earlier S regions,
        # region i's count is Bin(n - u, p / (1 - sum_{h<i} p_h))
        placed = sum(pS[:i])
        q = p / (1 - placed)
        nxt: dict[int, float] = {}
        for u, pr in dp.items():
            rem = n - u
            for c in range(0, min(k - 1, rem) + 1):
                w = comb(rem, c) * (q ** c) * ((1 - q) ** (rem - c))
                nxt[u + c] = nxt.get(u + c, 0.0) + pr * w
        dp = nxt
    return sum(dp.values())


def p_all_at_least_inclexcl(masses: list[float], n: int, k: int) -> float:
    """Method A: 1 - P(some region < k) by inclusion-exclusion."""
    R = len(masses)
    total = 0.0
    for r in range(1, R + 1):
        sign = -1.0 if r % 2 else 1.0
        for S in combinations(range(R), r):
            total += -sign * p_subset_all_below(masses, n, k, S)
    return 1.0 - total


def main() -> int:
    mf = masses_exact()
    m = [float(x) for x in mf]
    print("G1 masses from edges %s, region_of = #edges strictly below popcount" % EDGES)
    maxdiff = 0.0
    for j, x in enumerate(m):
        a = ARCHAEON["masses"]["pc%02d" % j]
        maxdiff = max(maxdiff, abs(x - a))
        print("   pc%02d  %.16f  archaeon %.16f  diff %.1e" % (j, x, a, abs(x - a)))
    print("   sum %.15f (exact %s)  max |diff vs Archaeon| %.1e" % (sum(m), sum(mf) == 1, maxdiff))
    print("   pc04 = popcount 64 alone: %s; pc05 = popcount 65 alone: %s"
          % (region_of(64) == 4 and region_of(63) == 3 and region_of(65) == 5,
             region_of(65) == 5 and region_of(66) == 6))

    rows = []
    for n in (120, 176, 175, 180):
        a = p_all_at_least_inclexcl(m, n, MIN_REGION_N)
        b = p_all_at_least_direct(m, n, MIN_REGION_N)
        rows.append((n, a, b))
        print("G2 n=%3d  P(all >= %d)  inclexcl %.13f  direct %.13f  |A-B| %.1e"
              % (n, MIN_REGION_N, a, b, abs(a - b)))
    g2_180 = dict((r[0], r[1]) for r in rows)[180]
    g2_120 = dict((r[0], r[1]) for r in rows)[120]
    g2_176 = dict((r[0], r[1]) for r in rows)[176]
    g2_175 = dict((r[0], r[1]) for r in rows)[175]
    print("   vs Archaeon: 180 diff %.1e; 120 diff %.1e"
          % (abs(g2_180 - ARCHAEON["g2_180"]), abs(g2_120 - ARCHAEON["g2_120"])))
    print("   min corpus reaching %.2f: 176 -> %s (175 gives %.4f, 176 gives %.4f)"
          % (THRESHOLD, g2_175 < THRESHOLD <= g2_176, g2_175, g2_176))

    print("CONTROLS")
    print("   negative  n=120 fails 0.80: %s (%.4f)" % (g2_120 < THRESHOLD, g2_120))
    print("   positive  n=180 passes 0.80: %s (%.4f)" % (g2_180 >= THRESHOLD, g2_180))
    starved = list(m)
    starved[4] = 0.001
    s = sum(starved)
    starved = [x / s for x in starved]
    cheat = p_all_at_least_direct(starved, 180, MIN_REGION_N)
    print("   cheat     pc04 starved to 0.001 at n=180: %.2e (must be ~0): %s"
          % (cheat, cheat < 1e-6))
    ok = (maxdiff < 1e-12 and all(abs(r[1] - r[2]) < 1e-12 for r in rows)
          and abs(g2_180 - ARCHAEON["g2_180"]) < 1e-9
          and abs(g2_120 - ARCHAEON["g2_120"]) < 1e-9
          and g2_175 < THRESHOLD <= g2_176 and cheat < 1e-6)
    print("VERDICT G1, G2 REPRODUCED INDEPENDENTLY: %s" % ok)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
