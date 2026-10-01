"""N15b: lifetime conversions (sum over T=20 steps) of a founder-type individual vs kin-partner share q, BASE write-back.
Estimates the critical q where mean lifetime conversions cross 1 (supercritical), mapped to lineage size N = q*256."""
import sys, os, random, json
sys.path.insert(0, os.path.dirname(__file__))
from kin import g0, step
res = {}
T = 20; L = 300
for q in (0.0, 0.02, 0.04, 0.06, 0.1, 0.15):
    R = random.Random(int(q * 10000) + 99)
    tot = 0
    for life in range(L):
        g = g0; regs = None
        for t in range(T):
            partner = g if R.random() < q else bytes(R.randrange(256) for _ in range(64))
            g, regs, c = step(g, regs, partner, R.randrange(2), R)
            tot += c
    res[q] = round(tot / L, 3)
    print('q=%.2f (N~%d of 256): mean lifetime conversions %.3f' % (q, q * 256, tot / L), flush=True)
json.dump(res, open(os.path.join(os.path.dirname(__file__), 'kin_fine.json'), 'w'), indent=1)
