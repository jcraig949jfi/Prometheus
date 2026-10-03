"""G2.preflight: does PASS mean both registered answers are attainable at 0.99?
The negative's registered answer under classify() is AT_BOUND (NEGATIVE). Compute its probability
for a member of the class (rate p0) with an independent exact binomial, wherever preflight says PASS."""
from drv import *
from fractions import Fraction as F
from exactbin import tge, tle

def p_negative(n, p0, alpha, ppos, exact_rate=True):
    """P(classify == AT_BOUND) for X ~ Bin(n, p0), using stats.classify for the labels and exact weights."""
    num, den = p0
    tot = F(0)
    for k in range(n + 1):
        if stats.classify(k, n, num / den, alpha, ppos, exact_rate) == "AT_BOUND":
            tot += tle(n, k, p0) - tle(n, k - 1, p0)
    return float(tot)

worst = []
for p0 in ((1, 2), (1, 4), (1, 10), (1, 16), (1, 50)):
    for ppos in (15 / 16, 0.9, 0.75, 0.6, 0.5, 0.4, 0.3, 0.2):
        if ppos <= p0[0] / p0[1]:
            continue
        for alpha in (1e-6, 1e-3, 0.009):
            for n in range(4, 400):
                r = stats.preflight(n, p0[0] / p0[1], alpha, ppos)
                if r.verdict == PASS:
                    pn = p_negative(n, p0, alpha, ppos)
                    if pn < 0.99:
                        worst.append((pn, n, p0, ppos, alpha, r.detail["power"]))
                    break          # the smallest n that preflight admits
worst.sort()
print("cases where preflight PASSes at its smallest admitted n and P(negative answers NEGATIVE) < 0.99:", len(worst))
for pn, n, p0, ppos, alpha, power in worst[:12]:
    print("  n=%3d bound=%d/%d weakest positive=%.4f alpha=%g: power %.4f, P(class member -> NEGATIVE) = %.4f"
          % (n, p0[0], p0[1], ppos, alpha, power, pn))
# the registered setting itself
print("registered setting: n=64 p0=1/2 alpha=1e-6 weakest 15/16: P(class member -> NEGATIVE) = %.8f" % p_negative(64, (1, 2), 1e-6, 15 / 16))
print("  of which UNDECIDED %.3g, INVERTED %.3g, EXCLUDES %.3g" % (
    float(tle(64, 50, (1, 2)) - tle(64, 47, (1, 2))), float(tle(64, 13, (1, 2))), float(tge(64, 51, (1, 2)))))
# declared inputs
print("preflight_from_design with a million declared design hits:", stats.preflight_from_design(64, 0.5, 1e-6, 10**6, 10**6).verdict)
print("preflight with the rate declared as True:", stats.preflight(64, 0.5, 1e-6, True).verdict)
print("preflight(64, .5, .01, 1.0):", stats.preflight(64, 0.5, 0.01, 1.0).verdict, " (1-alpha == 0.99?)", 1 - 0.01 == 0.99)
print("preflight n as 64.0:", stats.preflight(64.0, 0.5, 1e-6, 1.0).verdict)
