exec(open(__file__.replace("p06_escapes_c.py", "drv.py")).read())
import random
from rso_harness import stats, retain1, rulers, search, torture, audits, claims, registration
from rso_harness.verdict import *
from rso_harness.stats import khash


def show(tag, r):
    print("%-90s -> %s %s" % (tag, r.verdict, ("| " + r.reason) if r.reason else ""))


F, B = meta.FOUNDERS, meta.BUDGET
print("################ exact_reach against brute force")
# independent exact computation: absorbing Markov chain over all 256 genomes, by explicit transition lists
def exact_ref(landscape, policy, budget, kind, distance=0):
    f, accept = search.LANDSCAPES[landscape], search.POLICIES[policy]
    L, T = 8, 255
    if kind == "COLD":
        starts = [g for g in range(256) if bin(g).count("1") <= 4]
    else:
        from itertools import combinations
        starts = [T ^ sum(1 << i for i in s) for s in combinations(range(L), distance)]
    p = [0.0] * 256
    for g in starts:
        p[g] += 1.0 / len(starts)
    done = p[T]
    p[T] = 0.0
    for _ in range(budget):
        q = [0.0] * 256
        for g in range(256):
            if p[g] == 0.0:
                continue
            for i in range(L):
                h = g ^ (1 << i)
                to = h if accept(f(h), f(g)) else g
                if to == T:
                    done += p[g] / L
                else:
                    q[to] += p[g] / L
        p = q
    return done


def monte(landscape, policy, budget, kind, distance, n, seed=12345):
    f, accept = search.LANDSCAPES[landscape], search.POLICIES[policy]
    rng = random.Random(seed)
    founders = [g for g in range(256) if bin(g).count("1") <= 4]
    hits = 0
    for _ in range(n):
        if kind == "COLD":
            g = rng.choice(founders)
        else:
            g = 255
            for i in rng.sample(range(8), distance):
                g ^= 1 << i
        found = g == 255
        for _s in range(budget):
            if found:
                break
            h = g ^ (1 << rng.randrange(8))
            if accept(f(h), f(g)):
                g = h
            found = g == 255
        hits += found
    return hits / n


for ls in sorted(search.LANDSCAPES):
    for pol in sorted(search.POLICIES):
        for kind, d in (("COLD", 0), ("REPAIR", 1)):
            e = search.exact_reach(ls, pol, B, kind, d)
            r = exact_ref(ls, pol, B, kind, d)
            m = monte(ls, pol, B, kind, d, 20000)
            s = search.sample_reach(ls, pol, B, kind, F, d)
            print("  %-7s %-8s %-6s exact %.6f  ref %.6f  monte-carlo(20000) %.4f  harness sample %2d/48  %s"
                  % (ls, pol, kind, e, r, m, s, "OK" if abs(e - r) < 1e-12 and abs(e - m) < 0.012 else "MISMATCH"))
print("  NEEDLE/STRICT/COLD == 0.0 exactly:", search.exact_reach("NEEDLE", "STRICT", B, "COLD") == 0.0,
      "| ASCENT cold strict %.10f neutral %.10f" % (search.exact_reach("ASCENT", "STRICT", B, "COLD"), search.exact_reach("ASCENT", "NEUTRAL", B, "COLD")))
print("  founders with at most 4 bits:", len(search.FOUNDERS))

print("################ G7.calibration")
for ls, pol in (("ASCENT", "NEUTRAL"), ("NEEDLE", "NEUTRAL"), ("VALLEY", "STRICT"), ("VALLEY", "NEUTRAL"), ("ASCENT", "STRICT"), ("NEEDLE", "STRICT")):
    r = search.calibration(ls, pol, B, "COLD", F, 0, meta.repair_as_cold)
    show("repair runs reported as cold reach on %s/%s (exact cold %.4f, hits %d)" % (ls, pol, r.detail["exact"], r.detail["hits"]), r)


def short_budget(frac):
    def est(landscape, policy, budget, kind, seeds, distance=0):
        return search.sample_reach(landscape, policy, int(budget * frac), kind, seeds, distance)
    return est


for frac in (0.9, 0.8, 0.7, 0.6, 0.5, 0.4):
    r = search.calibration("NEEDLE", "NEUTRAL", B, "COLD", F, 0, short_budget(frac))
    show("E estimator that ran %d%% of the registered budget (NEEDLE/NEUTRAL; hits %d)" % (round(100 * frac), r.detail["hits"]), r)


def inflate(k):
    def est(landscape, policy, budget, kind, seeds, distance=0):
        return min(len(seeds), search.sample_reach(landscape, policy, budget, kind, seeds, distance) + k)
    return est


for k in (2, 4, 6, 8):
    r = search.calibration("NEEDLE", "NEUTRAL", B, "COLD", F, 0, inflate(k))
    show("E estimator that adds %d phantom hits (NEEDLE/NEUTRAL; reported %d of 48)" % (k, r.detail["hits"]), r)
# how often does a SOUND estimator fail this gate? different founder sets
fails = 0
trials = 400
for t in range(trials):
    seeds = list(range(100000 + 48 * t, 100000 + 48 * (t + 1)))
    fails += search.calibration("NEEDLE", "NEUTRAL", B, "COLD", seeds).verdict != PASS
print("  S sound estimator, NEEDLE/NEUTRAL, %d other founder sets: FAIL in %d (%.1f%%); the design asks 0.99 for every registered answer"
      % (trials, fails, 100.0 * fails / trials))

print("################ G7.report")
show("clean cold discovery", search.check_report(meta.search_report()))
zero = {"STRICT": {"n": 48, "seeds": list(F), "hits": 0}}
show("E COLD_DISCOVERY claimed with zero hits", search.check_report(meta.search_report(policies=zero)))
show("E COLD_DISCOVERY with 480 hits of 48 founders", search.check_report(meta.search_report(policies={"NEUTRAL": {"n": 48, "seeds": list(F), "hits": 480}})))
two_strict = {p: {"n": 48, "seeds": list(F), "hits": search.sample_reach("NEEDLE", "STRICT", B, "COLD", F)} for p in ("STRICT", "STRICT_AGAIN")}
show("E a null on the needle from two policies, neither able to cross a neutral step", search.check_report(meta.search_report(
    claim="REACH_BOUNDED", policies=two_strict, upper_bound=stats.zero_hit_upper(48))))
show("E label 'the substrate cannot do it'", search.check_report(meta.null_report(label="the substrate cannot do it")))
show("E label 'no capacity in this physics'", search.check_report(meta.null_report(label="no capacity in this physics")))
show("S label 'a bound on reach; not a claim that the target is impossible'", search.check_report(meta.null_report(label="a bound on reach; not a claim that the target is impossible")))
show("S bound rounded to four places (0.0605)", search.check_report(meta.null_report(upper_bound=0.0605)))
show("S a more cautious bound (99%%: %.4f)" % stats.zero_hit_upper(48, 0.99), search.check_report(meta.null_report(upper_bound=stats.zero_hit_upper(48, 0.99))))
show("E positive control taken from another policy and landscape (as in the clean case)", search.check_report(meta.null_report()))
show("E start_law says COLD, the runs were repair (label only)", search.check_report(meta.search_report(
    policies={"NEUTRAL": {"n": 48, "seeds": list(F), "hits": search.sample_reach("VALLEY", "STRICT", B, "REPAIR", F, 1)}})))
show("E founders 'independent' by seed but all the same genome (seeds differ, start identical)", search.check_report(meta.search_report(
    policies={"NEUTRAL": {"n": 48, "seeds": list(range(48)), "hits": 5}})))
show("precedence: no positive control AND repair-as-cold", search.check_report(meta.search_report(start_law="REPAIR", positive_control=None)))
