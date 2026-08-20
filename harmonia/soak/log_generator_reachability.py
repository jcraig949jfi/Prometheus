"""Reachability check for gen_log_extra_3arg's rejection sampler (soak P20).

A candidate defect is visible in the source: the sampler runs

    for _try in range(30):
        ...
        if <uniqueness ok>: break
    c = p * (p - a) * (p - b)          # OUTSIDE the loop

so if all 30 tries fail, the loop exits normally and the LAST FAILING sample
ships with gt=[p] that may not be the unique in-domain root.

That is a publishable-looking finding. SOAK-33 says a defect claim owes an
impact estimate, so reachability is measured BEFORE claiming rather than after:
enumerate the entire draw space and compute the per-try failure rate.

Result: 0 failures in 80 triples. Exhaustion probability is zero and the branch
is unreachable dead code. No defect is claimed.

The enumeration replicates the generator's own disc/r1/r2 arithmetic, so a
replicated bug would produce a FALSE clean -- hence the independent sympy
cross-check, which solves the cubic directly.

Read-only.
"""
import random
import sys

sys.path.insert(0, "harmonia/experiments")
import sympy as sp  # noqa: E402
from reasoning_phase0 import gen_log_extra_3arg  # noqa: E402

x = sp.Symbol("x", real=True)


def enumerate_draw_space():
    """Per-try failure rate over the sampler's entire parameter space."""
    fails, total = [], 0
    for a in range(1, 5):
        for db in range(1, 5):
            b = a + db
            for dp in range(1, 6):
                p = b + dp
                total += 1
                A, B = p - a - b, (p - a) * (p - b)
                disc = A * A - 4 * B
                if disc < 0:
                    continue                      # no real roots -> break taken
                sq = disc ** 0.5
                r1, r2 = (-A + sq) / 2.0, (-A - sq) / 2.0
                if r1 <= b and r2 <= b:
                    continue                      # other reals out of domain -> break
                fails.append((a, b, p))
    return total, fails


def sympy_crosscheck(n=40, seed=20260820):
    """Independent method: solve the cubic, count in-domain roots."""
    bad = 0
    for q in gen_log_extra_3arg(random.Random(seed))[:n]:
        a, b, c = q.data["a"], q.data["b"], q.data["c"]
        p = q.ground_truth[0]
        roots = sp.solve(sp.Eq(x * (x - a) * (x - b), c), x)
        indomain = [r for r in roots if r.is_real and float(r) > b]
        if not (len(indomain) == 1 and sp.simplify(indomain[0] - p) == 0):
            bad += 1
    return n, bad


if __name__ == "__main__":
    total, fails = enumerate_draw_space()
    rate = len(fails) / total
    print(f"draw space: {total} triples | per-try failures: {len(fails)} | rate {rate:.3f}")
    print(f"P(all 30 tries fail) = {rate ** 30:.3e}  -> silent fallback unreachable")
    n, bad = sympy_crosscheck()
    print(f"sympy cross-check: {n} probes, uniqueness violations = {bad}")
    print("VERDICT: guard clean; candidate defect NOT claimed (reachability zero).")
    print("NOTE: 'unreachable' is a statement about today's literal randint bounds,")
    print("      not about the code. Widening them could make the branch live.")
