"""G7. Search geometry on landscapes small enough to count exactly.

Genomes are 8-bit strings. A search proposes one random bit flip per step and accepts it under a
rule. Reach is the probability of having visited the target within the budget. For these landscapes
that probability is computed exactly by propagating the whole distribution, so sampled estimates and
the labels put on them can be checked against a known answer.

Two start laws, never to be confused. COLD draws the founder from the registered initial law (here:
uniform over genomes with at most four bits set, so every founder is at least four flips from the
target). REPAIR(d) starts from the target with d bits flipped.
"""
from itertools import combinations

from .stats import clopper_pearson, khash, zero_hit_upper
from .verdict import BLOCKED, FAIL, PASS, UNQUALIFIED, Result

L = 8
TARGET = (1 << L) - 1


def pop(g):
    return bin(g).count("1")


def ascent(g):
    """Smooth: every bit helps."""
    return pop(g)


def needle(g):
    """A plateau: nothing helps until everything is right."""
    return 1 if g == TARGET else 0


def valley(g):
    """Deceptive: a slope up to four bits, then a valley three wide in front of the target."""
    return 16 if g == TARGET else pop(g) if pop(g) <= 4 else 0


LANDSCAPES = {"ASCENT": ascent, "NEEDLE": needle, "VALLEY": valley}
POLICIES = {"STRICT": lambda new, old: new > old, "NEUTRAL": lambda new, old: new >= old}
FOUNDERS = [g for g in range(1 << L) if pop(g) <= 4]


def start_law(kind, distance=0):
    """Probability of each starting genome."""
    if kind == "COLD":
        return {g: 1.0 / len(FOUNDERS) for g in FOUNDERS}
    sets = list(combinations(range(L), distance))
    return {TARGET ^ sum(1 << i for i in s): 1.0 / len(sets) for s in sets}


def exact_reach(landscape, policy, budget, kind, distance=0):
    """Exact probability that the search has visited the target within `budget` proposals."""
    f, accept = LANDSCAPES[landscape], POLICIES[policy]
    dist = dict(start_law(kind, distance))
    hit = dist.pop(TARGET, 0.0)
    for _ in range(budget):
        nxt = {}
        for g, p in dist.items():
            for i in range(L):
                h = g ^ (1 << i)
                to = h if accept(f(h), f(g)) else g
                if to == TARGET:
                    hit += p / L
                else:
                    nxt[to] = nxt.get(to, 0.0) + p / L
        dist = nxt
    return hit


def sample_reach(landscape, policy, budget, kind, seeds, distance=0):
    """Hits among independent founders, one per seed."""
    f, accept = LANDSCAPES[landscape], POLICIES[policy]
    hits = 0
    for seed in seeds:
        if kind == "COLD":
            g = FOUNDERS[khash(seed, 0) % len(FOUNDERS)]
        else:
            order = sorted(range(L), key=lambda i: khash(seed, 1, i))
            g = TARGET ^ sum(1 << i for i in order[:distance])
        found = g == TARGET
        for step in range(budget):
            if found:
                break
            h = g ^ (1 << (khash(seed, 2, step) % L))
            if accept(f(h), f(g)):
                g = h
            found = g == TARGET
        hits += 1 if found else 0
    return hits


def calibration(landscape, policy, budget, kind, seeds, distance=0, estimator=sample_reach):
    """Is the exact reach inside the 95% interval of the sampled estimate?"""
    exact = exact_reach(landscape, policy, budget, kind, distance)
    hits = estimator(landscape, policy, budget, kind, seeds, distance)
    lo, hi = clopper_pearson(hits, len(seeds))
    detail = {"exact": exact, "hits": hits, "n": len(seeds), "interval": [lo, hi]}
    if lo <= exact <= hi:
        return Result("G7.calibration", PASS, "", detail)
    return Result("G7.calibration", FAIL, "exact reach %.4f is outside the sampled interval [%.4f, %.4f]"
                  % (exact, lo, hi), detail)


def check_report(report):
    """G7. Is a search result labelled as what it is?

    report = {"claim": "COLD_DISCOVERY" | "REPAIR_REACH" | "REACH_BOUNDED",
              "start_law": "COLD" | "REPAIR",
              "policies": {name: {"n": int, "hits": int, "seeds": [...]}},
              "positive_control": {"exact_reach": float} or None,
              "upper_bound": float or None, "label": str}
    """
    gate = "G7.report"
    missing = [k for k in ("claim", "start_law", "policies") if not report.get(k)]
    if missing:
        return Result(gate, BLOCKED, "report lacks: %s" % ", ".join(missing))
    label = (report.get("label") or "").upper()
    if "INCAPABLE" in label or "IMPOSSIBLE" in label:
        return Result(gate, FAIL, "a search null is a bound on reach, not a statement about the substrate")
    for name, p in sorted(report["policies"].items()):
        if len(set(p["seeds"])) != len(p["seeds"]) or len(p["seeds"]) != p["n"]:
            return Result(gate, FAIL, "policy %s: founders are not independent (repeated or missing seeds)" % name)
    if report["claim"] == "COLD_DISCOVERY" and report["start_law"] != "COLD":
        return Result(gate, FAIL, "repair from a designed target is reported as cold discovery")
    control = report.get("positive_control")
    if not control:
        return Result(gate, UNQUALIFIED, "the search has no positive control: no planted target it is known to find")
    if control["exact_reach"] < 0.99:
        return Result(gate, UNQUALIFIED, "the positive control is itself hard to find (%.3f)" % control["exact_reach"])
    if report["claim"] == "REACH_BOUNDED":
        if len(report["policies"]) < 2:
            return Result(gate, BLOCKED, "a null needs at least two search policies; one was run")
        if any(p["hits"] for p in report["policies"].values()):
            return Result(gate, FAIL, "one policy did reach the target; the null does not hold for this physics")
        n = min(p["n"] for p in report["policies"].values())
        if report.get("upper_bound") is None or abs(report["upper_bound"] - zero_hit_upper(n)) > 1e-9:
            return Result(gate, FAIL, "zero hits in %d founders bounds the hit rate at %.4f; the report must say so"
                          % (n, zero_hit_upper(n)))
    return Result(gate, PASS)
