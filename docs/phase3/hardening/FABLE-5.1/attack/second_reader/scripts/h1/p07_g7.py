"""G7.calibration and G7.report; exact reach by an independent chain on the number of bits set."""
from drv import *
from math import comb
BUDGET, FOUNDERS, REPORTED = meta.BUDGET, meta.FOUNDERS, meta.REPORTED
cal, report, null, recount, hits = search.calibration, meta.report, meta.null, meta.recount, meta.hits


def show(name, thunk):
    try:
        r = thunk()
        print("%-96s -> %s %s" % (name, r.verdict, ("| " + r.reason[:170]) if r.reason else ""))
    except Exception as e:
        print("%-96s -> RAISES %s: %s" % (name, type(e).__name__, str(e)[:100]))


# ---- independent exact reach: all three landscapes depend on the number of ones only
def f_of(landscape, k):
    if landscape == "ASCENT":
        return k
    if landscape == "NEEDLE":
        return 1 if k == 8 else 0
    return 16 if k == 8 else k if k <= 4 else 0


def reach(landscape, neutral, budget, cold, distance=0):
    if cold:
        tot = sum(comb(8, k) for k in range(5))
        dist = {k: comb(8, k) / tot for k in range(5)}
    else:
        dist = {8 - distance: 1.0}
    hit = dist.pop(8, 0.0)
    for _ in range(budget):
        nxt = {}
        for k, p in dist.items():
            for to, pr in ((k + 1, (8 - k) / 8), (k - 1, k / 8)):
                if pr == 0:
                    continue
                new, old = f_of(landscape, to), f_of(landscape, k)
                dest = to if (new >= old if neutral else new > old) else k
                if dest == 8:
                    hit += p * pr
                else:
                    nxt[dest] = nxt.get(dest, 0.0) + p * pr
        dist = nxt
    return hit


print("--- exact reach: document 3 section 6, mine against search.exact_reach")
for land, pol in (("ASCENT", "STRICT"), ("ASCENT", "NEUTRAL"), ("NEEDLE", "STRICT"), ("NEEDLE", "NEUTRAL"),
                  ("VALLEY", "STRICT"), ("VALLEY", "NEUTRAL")):
    mine = (reach(land, pol == "NEUTRAL", BUDGET, True), reach(land, pol == "NEUTRAL", BUDGET, False, 1))
    theirs = (search.exact_reach(land, pol, BUDGET, "COLD"), search.exact_reach(land, pol, BUDGET, "REPAIR", 1))
    print("  %-7s %-8s cold %.4f / %.4f   repair(1) %.4f / %.4f" % (land, pol, mine[0], theirs[0], mine[1], theirs[1]))
print("  NEEDLE NEUTRAL cold at 380 proposals: mine %.4f theirs %.4f" % (
    reach("NEEDLE", True, 380, True), search.exact_reach("NEEDLE", "NEUTRAL", 380, "COLD")))
print("  exact values that are exactly 0.0 or 1.0:", {(l, p): search.exact_reach(l, p, BUDGET, "COLD")
                                                     for l in ("ASCENT", "NEEDLE", "VALLEY") for p in ("STRICT", "NEUTRAL")})

print("--- G7.calibration: broken estimators")
never = lambda landscape, policy, budget, kind, seeds, distance=0: 0
always = lambda landscape, policy, budget, kind, seeds, distance=0: len(seeds)
show("C1 an estimator that never searches (returns 0), on VALLEY/STRICT/COLD (a registered sound cell)",
     lambda: cal("VALLEY", "STRICT", BUDGET, "COLD", FOUNDERS, 0, never))
show("C1b the same on NEEDLE/STRICT/COLD and VALLEY/NEUTRAL/COLD",
     lambda: combine("x", [cal("NEEDLE", "STRICT", BUDGET, "COLD", FOUNDERS, 0, never), cal("VALLEY", "NEUTRAL", BUDGET, "COLD", FOUNDERS, 0, never)]))
show("C2 an estimator that ran none of the budget, on VALLEY/STRICT/COLD",
     lambda: cal("VALLEY", "STRICT", BUDGET, "COLD", FOUNDERS, 0, meta.short_budget(0.0)))
show("C3 an estimator that always reports every founder a hit, on ASCENT/STRICT/COLD (a registered sound cell)",
     lambda: cal("ASCENT", "STRICT", BUDGET, "COLD", FOUNDERS, 0, always))
show("C3b the same on VALLEY/STRICT/REPAIR(1)", lambda: cal("VALLEY", "STRICT", BUDGET, "REPAIR", FOUNDERS, 1, always))
show("C4 half the budget on the only informative cold cell (registered mutant)",
     lambda: cal("NEEDLE", "NEUTRAL", BUDGET, "COLD", FOUNDERS, 0, meta.short_budget(0.5)))
# cherry-picked founders for calibration of a half-budget estimator
half = meta.short_budget(0.5)
pool = list(range(30000, 31200))
hit = [s for s in pool if half("NEEDLE", "NEUTRAL", BUDGET, "COLD", [s])]
miss = [s for s in pool if s not in set(hit)]
picked = hit[:187] + miss[:69]
show("C5 half the budget, calibrated on 256 distinct founders picked after the fact (187 hits)",
     lambda: cal("NEEDLE", "NEUTRAL", BUDGET, "COLD", picked, 0, half))
print("     pool of %d: half-budget hit rate %.3f; exact reach at the budget %.4f" % (len(pool), len(hit) / len(pool), search.exact_reach("NEEDLE", "NEUTRAL", BUDGET, "COLD")))
show("C6 no founders at all", lambda: cal("NEEDLE", "NEUTRAL", BUDGET, "COLD", [], 0, never))
show("C7 one founder", lambda: cal("NEEDLE", "NEUTRAL", BUDGET, "COLD", FOUNDERS[:1], 0, never))
show("C8 eight founders, an estimator that never searches", lambda: cal("NEEDLE", "NEUTRAL", BUDGET, "COLD", FOUNDERS[:4], 0, never))
import itertools
for n in (1, 2, 4, 5, 6, 8, 16):
    ok = [k for k in range(n + 1) if stats.consistent(k, n, search.exact_reach("NEEDLE", "NEUTRAL", BUDGET, "COLD"), search.CAL_ALPHA)]
    print("     with %2d founders the counts that pass at exact reach 0.7298: %s" % (n, ok))

print("--- G7.report: wrong reports")
# a false null from founders chosen after the fact
pool = list(range(50000, 50700))
missers = [s for s in pool if hits("NEEDLE", "NEUTRAL", seeds=[s]) == 0][:128]
print("     founders tried %d; NEUTRAL misses on NEEDLE in %d of them; exact reach %.4f" % (
    len(pool), sum(1 for s in pool if hits("NEEDLE", "NEUTRAL", seeds=[s]) == 0), search.exact_reach("NEEDLE", "NEUTRAL", BUDGET, "COLD")))
false_null = {"claim": "REACH_BOUNDED", "landscape": "NEEDLE", "budget": BUDGET, "start_law": "COLD", "distance": 0,
              "policies": {"STRICT": {"seeds": missers, "hits": 0}, "NEUTRAL": {"seeds": missers, "hits": 0}},
              "scope": "POLICIES_AND_BUDGET", "upper_bound": stats.zero_hit_upper(128)}
show("P1 a null on NEEDLE from 128 founders chosen because NEUTRAL missed on them (true reach 0.73)",
     lambda: search.check_report(false_null))
show("P1b the registered mutant of the same claim on the registered founders", lambda: search.check_report(null("NEEDLE")))
hitters = [s for s in pool if hits("NEEDLE", "NEUTRAL", seeds=[s]) == 1][:128]
show("P2 a discovery: 128 hits in 128 founders chosen because they hit",
     lambda: search.check_report({"claim": "COLD_DISCOVERY", "landscape": "NEEDLE", "budget": BUDGET, "start_law": "COLD",
                                  "policies": {"NEUTRAL": {"seeds": hitters, "hits": 128}}}))
show("P3 a repair claim whose start is the target itself (distance 0): 128 of 128",
     lambda: search.check_report(report("REPAIR_REACH", "VALLEY", "REPAIR", 0, ("STRICT",))))
show("P3b a repair claim with distance omitted", lambda: search.check_report(
    {"claim": "REPAIR_REACH", "landscape": "VALLEY", "budget": BUDGET, "start_law": "REPAIR",
     "policies": {"STRICT": {"seeds": list(REPORTED), "hits": 128}}}))
show("P4 a null under a REPAIR start at distance 4 called a bound on reach (start law not read for a null)",
     lambda: search.check_report(null("VALLEY", start_law="REPAIR") if False else dict(
         report("REACH_BOUNDED", "VALLEY", "REPAIR", 4, ("STRICT", "NEUTRAL")), scope="POLICIES_AND_BUDGET",
         upper_bound=stats.zero_hit_upper(128))))
show("P5 a null with the bound given as True", lambda: search.check_report(null(upper_bound=True)))
show("P6 a null with a bound of 1.0 (says nothing)", lambda: search.check_report(null(upper_bound=1.0)))
show("P7 start law misspelt 'cold' under a null", lambda: search.check_report(null(start_law="cold")))
show("P8 a null where NEUTRAL was given one founder and STRICT 128, bound for 128",
     lambda: search.check_report(dict(null(), policies={"STRICT": {"seeds": list(REPORTED), "hits": 0},
                                                         "NEUTRAL": {"seeds": REPORTED[:1], "hits": 0}})))
show("P9 a null at 90% confidence stated as the bound (0.0178)", lambda: search.check_report(null(upper_bound=1 - 0.1 ** (1 / 128))))
show("P10 budget as a float", lambda: search.check_report(report(budget=400.0)))
show("P11 a discovery on the control landscape itself (ASCENT)", lambda: search.check_report(report("COLD_DISCOVERY", "ASCENT")))
show("P12 a null with scope right and a second policy that is the first under another name (ELITIST+NEUTRAL)",
     lambda: search.check_report(null("VALLEY", ("ELITIST", "NEUTRAL"))))
print("--- G7.report: sound reports")
small = report("COLD_DISCOVERY", "ASCENT", policies=("NEUTRAL",), budget=12)
print("     ASCENT, NEUTRAL, 12 proposals: %d of 128 founders hit; exact %.4f" % (
    small["policies"]["NEUTRAL"]["hits"], search.exact_reach("ASCENT", "NEUTRAL", 12, "COLD")))
show("Q1 SOUND: a true cold discovery at 12 proposals, counts right", lambda: search.check_report(small))
rep5 = report("REPAIR_REACH", "VALLEY", "REPAIR", 1, ("STRICT",), budget=5)
print("     VALLEY, STRICT, repair from one flip, 5 proposals: %d of 128; exact %.4f" % (
    rep5["policies"]["STRICT"]["hits"], search.exact_reach("VALLEY", "STRICT", 5, "REPAIR", 1)))
show("Q2 SOUND: a true repair-reach report at 5 proposals, counts right", lambda: search.check_report(rep5))
show("Q3 SOUND: a null with its bound rounded to three decimals (0.023)", lambda: search.check_report(null(upper_bound=0.023)))
show("Q4 SOUND: a null with its bound rounded UP to three decimals (0.024)", lambda: search.check_report(null(upper_bound=0.024)))
show("Q5 SOUND: a null from NEUTRAL alone on VALLEY (the policy that can cross neutral steps)", lambda: search.check_report(null("VALLEY", ("NEUTRAL",))))
for n in (1, 2, 3, 5, 10, 24, 50, 100, 128, 200, 256, 1000):
    exact = stats.zero_hit_upper(n)
    r4 = round(exact, 4)
    okk = stats.zero_hit_upper(n) - 5e-5 <= r4 <= 1
    if not okk:
        print("     n=%d: bound %.6f rounded to four decimals %.4f is REJECTED" % (n, exact, r4))
bad = [n for n in range(1, 3000) if not (stats.zero_hit_upper(n) - 5e-5 <= round(stats.zero_hit_upper(n), 4) <= 1)]
print("     founder counts 1..2999 whose four-decimal bound is rejected:", bad[:10], "(%d)" % len(bad))
