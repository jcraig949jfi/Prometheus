"""Target witnesses: nontrivial transformations specified behaviourally.

None of W1-W3 is a single human edit category: each needs interacting parts
(a predicate plus a structural transform, a comparison plus a deletion, an
accumulator plus a map).  W4 is an artifact-level witness: a program that turns
every reference artifact into a *different live* artifact.

The oracle is a human-side construction-cost instrument only.  No M0 baseline
imports this module (statically enforced).
"""
from substrates.common import clampl, clampv, h16
from probes import battery

NAMES = ["W1_REVCOND", "W2_DEDUP", "W3_PREFIXSUM", "W4_UNIVERSAL"]


def w1(x):
    return tuple(reversed(x)) if sum(x) % 2 == 0 else tuple(x)


def w2(x):
    out = []
    for v in x:
        if not out or out[-1] != v:
            out.append(v)
    return tuple(out)


def w3(x):
    acc, out = 0, []
    for v in x:
        acc = clampv(acc + v)
        out.append(acc)
    return tuple(out)


ORACLES = {"W1_REVCOND": w1, "W2_DEDUP": w2, "W3_PREFIXSUM": w3}


def oracle_outputs(name):
    f = ORACLES[name]
    return [clampl(f(x)) for x in battery.VALUE_PROBES]


def oracle_fp(name):
    return h16(oracle_outputs(name))


def value_fitness(name, outs):
    """Per-probe exact match plus token-level partial credit."""
    tgt = oracle_outputs(name)
    score = 0.0
    for t, o in zip(tgt, outs):
        if not isinstance(o, tuple):
            continue
        if o == t:
            score += 1.0
        else:
            n = min(len(t), len(o))
            same = sum(1 for i in range(n) if t[i] == o[i])
            denom = max(len(t), len(o), 1)
            score += 0.35 * (same / denom)
    return score


def w4_fitness(sub, common, prog, artifact_probes, self_fp_cache):
    """Universal live self-transformer: for every reference artifact A, P(A) must
    be valid, live and semantically different from A."""
    good = 0
    for a in artifact_probes:
        y, st = sub.run(prog, a)
        if st != "ok" or not sub.is_valid(y):
            continue
        if y == a:
            continue
        if not common.is_live_short(sub, y, battery.LIVENESS_PROBES):
            continue
        fa = self_fp_cache.get(a)
        fy = common.sem_profile(sub, y, battery.VALUE_PROBES)["fp"]
        if fy != fa:
            good += 1
    return float(good)
