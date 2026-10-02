"""Independent exact binomial against stats.py, and the documented numbers."""
from drv import *
from fractions import Fraction as F
import itertools
from exactbin import tge, tle, crit, lowcrit

A = F(1, 10**6)
H, W = (1, 2), (15, 16)
print("crit(64,1/2,1e-6) mine", crit(64, H, A), "stats", stats.critical_k(64, 0.5, 1e-6))
print("  P(X>=51|.5) = %.4g  P(X>=50|.5) = %.4g" % (float(tge(64, 51, H)), float(tge(64, 50, H))))
print("lowcrit(64,1/2) mine", lowcrit(64, H, A), "stats", stats.lower_critical(64, 0.5, 1e-6))
print("lowcrit(64,15/16) mine", lowcrit(64, W, A), "stats", stats.lower_critical(64, 15 / 16, 1e-6))
print("  P(X<=47|15/16) = %.4g  P(X<=48|15/16) = %.4g" % (float(tle(64, 47, W)), float(tle(64, 48, W))))
print("power at 15/16: mine %.9f stats %.9f" % (float(tge(64, 51, W)), stats.tail_ge(64, 51, 15 / 16)))
print("crit(20,.5)", crit(20, H, A), stats.critical_k(20, 0.5, 1e-6), " crit(16,.5)", crit(16, H, A), stats.critical_k(16, 0.5, 1e-6))
lab = [stats.classify(k, 64, 0.5, 1e-6, 15 / 16) for k in range(65)]
print("classify 0..64:", [(key, len(list(g))) for key, g in itertools.groupby(lab)])
labF = [stats.classify(k, 64, 0.5, 1e-6, 15 / 16, exact_rate=False) for k in range(65)]
print("classify exact_rate=False:", [(key, len(list(g))) for key, g in itertools.groupby(labF)])
print("power at .85: mine %.4f; at .75: %.4f" % (float(tge(64, 51, (85, 100))), float(tge(64, 51, (3, 4)))))
print("lower_bound(20,20)", stats.lower_bound(20, 20), 0.01 ** (1 / 20))
print("lower_bound(256,256)", stats.lower_bound(256, 256), 0.01 ** (1 / 256))
lb = stats.lower_bound(61, 64)
print("lower_bound(61,64)", lb, "check tail_ge(64,61,lb)=", stats.tail_ge(64, 61, lb))
print("lower_bound(0,10)", stats.lower_bound(0, 10), "lower_bound(1,1)", stats.lower_bound(1, 1), "lower_bound(5,0)", stats.lower_bound(5, 0))
def eq(k, n=2048): return stats.equivalence(k, n, 0.5, 0.1, 1e-6)
labs = [eq(k) for k in range(2049)]
runs, pos = [], 0
for key, g in itertools.groupby(labs):
    m = len(list(g)); runs.append((key, pos, pos + m - 1)); pos += m
print("equivalence 0..2048:", runs)
a2 = A / 2
out_lo = max(k for k in range(2049) if tle(2048, k, H) <= a2)
out_hi = min(k for k in range(2049) if tge(2048, k, H) <= a2)
w_lo = min(k for k in range(2049) if tge(2048, k, (4, 10)) <= a2)
w_hi = max(k for k in range(2049) if tle(2048, k, (6, 10)) <= a2)
print("mine: OUTSIDE <=%d or >=%d ; WITHIN %d..%d" % (out_lo, out_hi, w_lo, w_hi))
exact = search.exact_reach("NEEDLE", "NEUTRAL", 400, "COLD")
ok = [k for k in range(257) if stats.consistent(k, 256, exact, 0.002)]
print("exact", exact, "consistent counts", ok[0], ok[-1], "contiguous", ok == list(range(ok[0], ok[-1] + 1)))
pe = F(exact).limit_denominator(10**9)
pp = (pe.numerator, pe.denominator)
okm = [k for k in range(257) if tge(256, k, pp) > F(1, 1000) and tle(256, k, pp) > F(1, 1000)]
print("mine", okm[0], okm[-1])
print("zero_hit_upper 24: %.6f  128: %.6f  128@.99: %.6f" % (stats.zero_hit_upper(24), stats.zero_hit_upper(128), stats.zero_hit_upper(128, 0.99)))
print("pmf(5,0.0)", stats.pmf(5, 0.0), "pmf(5,1.0)", stats.pmf(5, 1.0))
print("consistent(0,256,0.0)", stats.consistent(0, 256, 0.0, 0.002), "consistent(1,256,0.0)", stats.consistent(1, 256, 0.0, 0.002),
      "consistent(256,256,1.0)", stats.consistent(256, 256, 1.0, 0.002), "consistent(255,256,1.0)", stats.consistent(255, 256, 1.0, 0.002))
print("lower_critical(64,1.0,1e-6)", stats.lower_critical(64, 1.0, 1e-6), "-> classify(50,64,.5,1e-6,1.0) =", stats.classify(50, 64, 0.5, 1e-6, 1.0))
print("preflight with True as the positive's rate:", stats.preflight(64, 0.5, 1e-6, True).verdict)
for n in range(40, 140):
    hi, weak = stats.critical_k(n, 0.5, 1e-6), stats.lower_critical(n, 15 / 16, 1e-6)
    if hi is not None and weak is not None and weak >= hi:
        print("first n with weak >= hi:", n, "hi", hi, "weak", weak); break
n = 128
hi, weak = stats.critical_k(n, 0.5, 1e-6), stats.lower_critical(n, 15 / 16, 1e-6)
print("n=128 hi", hi, "weak", weak, "classify(95,128)=", stats.classify(95, 128, 0.5, 1e-6, 15 / 16))
