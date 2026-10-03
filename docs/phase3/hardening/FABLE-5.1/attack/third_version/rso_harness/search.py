"""G7. Search geometry on landscapes small enough to count exactly.

Genomes are 8-bit strings. A search proposes one random bit flip per step and accepts it under a
rule. Reach is the probability of having visited the target within the budget. For these landscapes
that probability is computed exactly by propagating the whole distribution, so sampled estimates and
the reports written about them can be checked against a known answer.

Two start laws, never to be confused. COLD draws the founder from the registered initial law (here:
uniform over genomes with at most four bits set, so every founder is at least four flips from the
target). REPAIR(d) starts from the target with d bits flipped.

A report is not believed. The gate replays the registered search on the registered seeds and
compares the counts, and computes the positive control itself.
"""
from functools import lru_cache
from itertools import combinations

from . import stats
from .stats import khash, zero_hit_upper
from .verdict import BLOCKED, FAIL, PASS, UNQUALIFIED, Result, combine

L = 8
TARGET = (1 << L) - 1
CAL_ALPHA = 0.002           # a sound estimator fails calibration in at most 2 of 1,000 founder sets
CONTROL = "ASCENT"          # the positive control: a planted target that every step helps toward


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


def _strict(new, old):
    return new > old


def _neutral(new, old):
    return new >= old


LANDSCAPES = {"ASCENT": ascent, "NEEDLE": needle, "VALLEY": valley}
POLICIES = {"STRICT": _strict, "ELITIST": _strict, "NEUTRAL": _neutral}
POLICY_KIND = {"STRICT": "ASCENT_ONLY", "ELITIST": "ASCENT_ONLY", "NEUTRAL": "CROSSES_NEUTRAL_STEPS"}
FOUNDERS = [g for g in range(1 << L) if pop(g) <= 4]


def start_law(kind, distance=0):
    """Probability of each starting genome."""
    if kind == "COLD":
        return {g: 1.0 / len(FOUNDERS) for g in FOUNDERS}
    sets = list(combinations(range(L), distance))
    return {TARGET ^ sum(1 << i for i in s): 1.0 / len(sets) for s in sets}


@lru_cache(maxsize=None)
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


def calibration(landscape, policy, budget, kind, seeds, distance=0, estimator=sample_reach, alpha=CAL_ALPHA):
    """Is the sampled count compatible with the exact reach? Two-sided, exact, at level alpha.

    The test has a resolution: with n founders it sees an error in reach of a few standard errors and
    nothing smaller. meta.known_escapes pins an estimator that is wrong by less.
    """
    if not seeds:
        return Result("G7.calibration", BLOCKED, "no founders: nothing was checked")
    exact = exact_reach(landscape, policy, budget, kind, distance)
    hits, n = estimator(landscape, policy, budget, kind, seeds, distance), len(seeds)
    detail = {"exact": exact, "hits": hits, "n": n}
    if stats.consistent(hits, n, exact, alpha):
        return Result("G7.calibration", PASS, "", detail)
    return Result("G7.calibration", FAIL, "%d hits in %d founders is not compatible with exact reach %.4f"
                  % (hits, n, exact), detail)


# The cells an estimator is scored on. Two have exact reach strictly between 0 and 1, so an estimator
# that never searches, or always reports a hit, fails the panel.
CELLS = (("NEEDLE", "NEUTRAL", "COLD", 0), ("NEEDLE", "NEUTRAL", "REPAIR", 1), ("VALLEY", "NEUTRAL", "REPAIR", 1),
         ("ASCENT", "STRICT", "COLD", 0), ("VALLEY", "STRICT", "COLD", 0))


def calibration_panel(budget, seeds, estimator=sample_reach):
    """G7. An estimator is qualified on the whole panel of cells, not on one."""
    found = [calibration(ls, pol, budget, kind, seeds, d, estimator) for ls, pol, kind, d in CELLS]
    out = combine("G7.calibration", found)
    return Result("G7.calibration", out.verdict, "; ".join(r.reason for r in found if r.verdict != PASS),
                  [r.detail for r in found])


def check_report(report, registered_seeds=None):
    """G7. Is a search result what it says it is? Every problem is reported; the verdict is the worst.

    report = {"claim": "COLD_DISCOVERY" | "REPAIR_REACH" | "REACH_BOUNDED",
              "landscape": name, "budget": int, "start_law": "COLD" | "REPAIR", "distance": int,
              "policies": {registered policy name: {"seeds": [...], "hits": int}},
              "scope": "POLICIES_AND_BUDGET" | "SUBSTRATE", "upper_bound": float or None}
    registered_seeds: the founders registered for this cell before the search ran. They come from
    the registration, not from the report: a report may not choose its founders.

    The gate replays the registered search on those seeds and compares the counts. On these toy
    landscapes it also compares a null with the exact reach. Prose is not read: the scope field is
    what the gate holds a null to.
    """
    gate = "G7.report"
    missing = [k for k in ("claim", "landscape", "budget", "start_law", "policies") if not report.get(k)]
    if missing:
        return Result(gate, BLOCKED, "report lacks: %s" % ", ".join(missing))
    if not registered_seeds or len(set(registered_seeds)) != len(registered_seeds):
        return Result(gate, BLOCKED, "the founders registered for this cell are not on hand, or repeat")
    unknown = sorted(p for p in report["policies"] if p not in POLICIES)
    if unknown or report["landscape"] not in LANDSCAPES:
        return Result(gate, BLOCKED, "not registered: %s" % ", ".join(unknown or [report["landscape"]]))
    claim, law, budget, found = report["claim"], report["start_law"], report["budget"], []
    if claim not in ("COLD_DISCOVERY", "REPAIR_REACH", "REACH_BOUNDED") or law not in ("COLD", "REPAIR"):
        return Result(gate, BLOCKED, "unknown claim or start law: %r, %r" % (claim, law))
    distance, n = report.get("distance", 0), len(registered_seeds)
    for name, p in sorted(report["policies"].items()):
        if list(p["seeds"]) != list(registered_seeds):
            found.append(Result(name, FAIL, "the founders reported are not the founders registered, each once"))
            continue
        replayed = sample_reach(report["landscape"], name, budget, law, registered_seeds, distance)
        if replayed != p["hits"]:
            found.append(Result(name, FAIL, "reports %d hits; the registered search on the registered seeds gives %d"
                                % (p["hits"], replayed)))
    total = sum(p["hits"] for p in report["policies"].values())
    if law == "REPAIR" and distance < 1:
        found.append(Result("claim", FAIL, "a repair start at distance 0 is the target itself"))
    if claim == "COLD_DISCOVERY":
        if law != "COLD":
            found.append(Result("claim", FAIL, "repair from a designed target is reported as cold discovery"))
        if total == 0:
            found.append(Result("claim", FAIL, "a discovery is claimed and nothing was found"))
    elif claim == "REPAIR_REACH":
        if law != "REPAIR":
            found.append(Result("claim", FAIL, "a repair claim needs a repair start"))
    else:
        kinds = {POLICY_KIND[p] for p in report["policies"]}
        if len(report["policies"]) < 2 or "CROSSES_NEUTRAL_STEPS" not in kinds:
            found.append(Result("claim", BLOCKED, "a null needs at least two search policies, one of them able to cross "
                                "a neutral step"))
        if total:
            found.append(Result("claim", FAIL, "a policy did reach the target; the null does not hold"))
        for name in sorted(report["policies"]):
            control = exact_reach(CONTROL, name, budget, "COLD")
            if control < 0.99:
                found.append(Result(name, UNQUALIFIED, "no positive control: at this budget the policy reaches a "
                                    "planted target on a smooth slope with probability %.3f" % control))
        scope = report.get("scope")
        if scope is None:
            found.append(Result("scope", BLOCKED, "a null must state its scope"))
        elif scope != "POLICIES_AND_BUDGET":
            found.append(Result("scope", FAIL, "a search null is a bound on reach for these policies at this budget; "
                                "it is not a statement about the substrate"))
        bound = report.get("upper_bound")
        if bound is None:
            found.append(Result("bound", FAIL, "zero hits in %d founders bounds the hit rate at %.4f; the report must "
                                "say so" % (n, zero_hit_upper(n))))
        elif not zero_hit_upper(n) - 5e-5 <= bound <= 1:
            found.append(Result("bound", FAIL, "the stated bound %.4f is smaller than %d founders warrant (%.4f)"
                                % (bound, n, zero_hit_upper(n))))
        else:
            over = ["%s %.4f" % (name, exact_reach(report["landscape"], name, budget, law, distance))
                    for name in sorted(report["policies"])
                    if exact_reach(report["landscape"], name, budget, law, distance) > bound]
            if over:
                found.append(Result("exact", FAIL, "the exact reach is above the stated bound: %s" % ", ".join(over)))
    out = combine(gate, found or [Result("all", PASS)])
    return Result(gate, out.verdict, out.reason)
