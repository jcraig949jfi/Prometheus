"""Independent exact binomial tails in integer arithmetic. p = (a, b) means a/b."""
from fractions import Fraction as F
from functools import lru_cache
from math import comb

@lru_cache(maxsize=None)
def weights(n, a, b):
    w = [comb(n, i) * a**i * (b - a)**(n - i) for i in range(n + 1)]
    up = [0] * (n + 2)            # up[k] = sum_{i>=k} w_i
    for i in range(n, -1, -1):
        up[i] = up[i + 1] + w[i]
    return w, up, b**n

def tge(n, k, p):
    a, b = p
    w, up, tot = weights(n, a, b)
    k = max(k, 0)
    return F(up[k], tot) if k <= n else F(0)

def tle(n, k, p):
    a, b = p
    w, up, tot = weights(n, a, b)
    if k < 0:
        return F(0)
    k = min(k, n)
    return F(tot - up[k + 1], tot)

def crit(n, p0, alpha):
    for k in range(n + 1):
        if tge(n, k, p0) <= alpha:
            return k
    return None

def lowcrit(n, p, alpha):
    best = None
    for k in range(n + 1):
        if tle(n, k, p) > alpha:
            break
        best = k
    return best
