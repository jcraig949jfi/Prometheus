"""Exact expected scores at 3 symbols (all 6^6 keys, all 6 orders of the ninth family) for the author's organisms.
Is the bound exact for TABLE_CACHE, which keeps ALL eight tables and picks among fixed re-indexings by feedback?"""
import sys, itertools
from fractions import Fraction as F
sys.dont_write_bytecode = True
sys.path.insert(0, "harness")
from rso_harness import ladder as L
L.N = 3
N = 3
PERMS = list(itertools.permutations(range(N)))
ORDERS = list(itertools.permutations(range(N)))
H = sum(F(1, k) for k in range(1, N + 1))

def exact(make, control=False):
    total, count = 0, 0
    for Ls in itertools.product(PERMS, repeat=3):
        for Ps in itertools.product(PERMS, repeat=3):
            if control:
                # the eight shown come from another key: average over one fixed other key is enough by symmetry? no:
                # enumerate a small set of other keys (all would be 6^12); use the identity-shifted key family instead
                others = [(Ls[1:] + Ls[:1], Ps[2:] + Ps[:2])]
            else:
                others = [(Ls, Ps)]
            for oL, oP in others:
                org = make(); org.begin_life()
                for (j, k) in L.SHOWN:
                    org.begin_family((j, k))
                    for x in range(N):
                        y = oP[k][oL[j][x]]
                        org.predict(x); org.learn(x, y)
                    org.end_family()
                # snapshot the kept tables, then try every order of the ninth family on a copy of the state
                kept = dict(org.tables)
                for order in ORDERS:
                    o2 = make(); o2.begin_life(); o2.tables = dict(kept)
                    o2.begin_family(L.UNSEEN); right = 0
                    for x in order:
                        y = Ps[2][Ls[2][x]]
                        right += o2.predict(x) == y
                        o2.learn(x, y)
                    total += right; count += 1
    return F(total, count)

print("3 symbols; exact bound H_3 = %s = %.6f" % (H, float(H)))
for name in ("ELIM", "TABLE_CACHE", "TWO_TABLES", "SCHEMA_CACHE", "COMPOSER"):
    e = exact(L.PAIR_ORGANISMS[name])
    print("  %-13s ninth pair: exact mean %s = %.6f  (%s the bound)" % (name, e, float(e), "above" if e > H else "at" if e == H else "below"))
