"""PROXY C0-A structure probe (stdlib only). NOT RUN by the author of REPORT.md.

Spec source (the design this operationalises; nothing here is repo code):
  SerendipityFoundry/incubator/PROMETHEUS_INCUBATOR_OEE_RESEARCH_PROGRAM_V0.txt @ 1ac333f43, lines 972-990
    (C0-A: sample generator programs; measure (1) null-battery failure rate, (2) whether bounded search
     finds predictors, (3) predictability vs composition depth, (4) depth-vs-noise, (5) reward-channel
     bandwidth = fraction of exploitable structure PRICED by residual-weighted payout).
  SerendipityFoundry/incubator/PROMETHEUS_INCUBATOR_WORLD0_DESIGN_REVIEW.txt @ 17f2b8d3a, lines 48-54, 931-939
    (minimal frozen null battery; A3 "tail may be noise"; reuse bias edges toward authoring the ladder).

No World-0 generator/instruction set exists in the repo at 0424c372a (see REPORT.md), so the grammar
below is a STAND-IN. Results transfer to World-0 only qualitatively.

What it measures, per (composition depth d, reuse probability r):
  nontrivial  = fraction of channels on which the minimal null battery fails (held-out acc < TAU_NULL)
  exploitable = fraction where bounded search beats the best null by MARGIN on held-out data
  surrogate   = same statistic on a value-permuted copy of the channel (noise control: search "wins"
                there only by overfitting the fit window); band must exceed this false-positive floor
  band        = nontrivial AND exploitable AND the surrogate does NOT show the same win
  priced      = among band channels, mean residual payout (acc_search - acc_null) / (1 - acc_null)

DECISION (what would settle the harvest question on this proxy):
  * K15-like death:  band(d, r=0) <= surrogate floor for every d > SEARCH_DEPTH
                      -> deep random composition is noise; depth needs reuse bias (Q2 is live).
  * Q2 dose-response: r* = smallest r at which band(d > SEARCH_DEPTH) clears the floor. Small r*
                      (e.g. <= 0.1) says a light bias suffices; r* near 1 says only heavily authored
                      reuse makes depth exploitable, i.e. the "line" sits inside ladder-authoring.
  * Bandwidth (Q1 proxy): if 'priced' is small while 'exploitable' is large, the payout, not the
                      world, is the binding constraint (OEE program P1b, line 843).
"""
import random, statistics

M = 16                      # alphabet size of channel values
T_FIT, T_TEST = 64, 64      # fit window, held-out window
TAU_NULL = 0.6              # battery "fails" if best null held-out accuracy < this
MARGIN = 0.15               # search must beat best null by this much on held-out
SEARCH_DEPTH = 2            # predictor expressions are drawn at depth <= this
SEARCH_BUDGET = 3000        # random predictor candidates per channel (plus all depth<=1 exhaustively)
N_CHANNELS = 200
DEPTHS = [1, 2, 3, 4, 6, 8]
REUSE = [0.0, 0.1, 0.25, 0.5, 0.8]
SEED = 20260929

LEAVES = ["t", "x1", "x2", "x3", "c"]
BINOPS = {
    "add": lambda a, b: (a + b) % M,
    "sub": lambda a, b: (a - b) % M,
    "mul": lambda a, b: (a * b) % M,
    "xor": lambda a, b: (a ^ b) % M,
    "max": lambda a, b: max(a, b),
    "lt":  lambda a, b: 1 if a < b else 0,
}


def rand_tree(rng, depth, reuse, pool):
    """Random expression of exact depth; with prob `reuse` reuse a previously built subtree (DAG sharing)."""
    if depth == 0:
        leaf = rng.choice(LEAVES)
        return ("c", rng.randrange(M)) if leaf == "c" else (leaf,)
    if pool.get(depth) and rng.random() < reuse:
        return rng.choice(pool[depth])
    op = rng.choice(list(BINOPS))
    left = rand_tree(rng, depth - 1, reuse, pool)
    right = rand_tree(rng, rng.randrange(depth), reuse, pool)
    node = (op, left, right)
    pool.setdefault(depth, []).append(node)
    return node


def ev(node, t, x1, x2, x3):
    k = node[0]
    if k == "t": return t % M
    if k == "x1": return x1
    if k == "x2": return x2
    if k == "x3": return x3
    if k == "c": return node[1]
    return BINOPS[k](ev(node[1], t, x1, x2, x3), ev(node[2], t, x1, x2, x3))


def run_channel(gen, n, rng):
    xs = [rng.randrange(M) for _ in range(3)]
    for t in range(n):
        xs.append(ev(gen, t, xs[-1], xs[-2], xs[-3]))
    return xs[3:]


def acc(pred_fn, xs, lo, hi):
    ok = 0
    for i in range(max(lo, 3), hi):
        ok += pred_fn(i, xs) == xs[i]
    return ok / max(1, hi - max(lo, 3))


def null_battery(xs):
    """Frozen minimal battery: constant (mode of fit window), last value, first difference, period-p p<=4."""
    fit = xs[:T_FIT]
    mode = max(set(fit), key=fit.count)
    preds = [lambda i, s: mode,
             lambda i, s: s[i - 1],
             lambda i, s: (2 * s[i - 1] - s[i - 2]) % M]
    preds += [(lambda p: (lambda i, s: s[i - p]))(p) for p in (2, 3, 4)]
    return max(acc(p, xs, T_FIT, T_FIT + T_TEST) for p in preds)


def all_depth_le1():
    leaves = [(l,) for l in LEAVES if l != "c"] + [("c", v) for v in range(M)]
    out = list(leaves)
    for op in BINOPS:
        for a in leaves:
            for b in leaves:
                out.append((op, a, b))
    return out


DEPTH1 = all_depth_le1()


def search(xs, rng):
    """Bounded search: select on FIT window, report HELD-OUT accuracy of the selected predictor."""
    cands = DEPTH1 + [rand_tree(rng, rng.randint(1, SEARCH_DEPTH), 0.0, {}) for _ in range(SEARCH_BUDGET)]
    best, best_fit = None, -1.0
    for c in cands:
        f = acc(lambda i, s, c=c: ev(c, i, s[i - 1], s[i - 2], s[i - 3]), xs, 0, T_FIT)
        if f > best_fit:
            best, best_fit = c, f
    return acc(lambda i, s: ev(best, i, s[i - 1], s[i - 2], s[i - 3]), xs, T_FIT, T_FIT + T_TEST)


def cell(d, r, rng):
    rows = []
    for _ in range(N_CHANNELS):
        gen = rand_tree(rng, d, r, {})
        xs = run_channel(gen, T_FIT + T_TEST, rng)
        surr = xs[:]; rng.shuffle(surr)
        a_null, a_srch = null_battery(xs), search(xs, rng)
        s_null, s_srch = null_battery(surr), search(surr, rng)
        nontriv = a_null < TAU_NULL
        expl = a_srch >= a_null + MARGIN
        s_expl = s_srch >= s_null + MARGIN
        band = nontriv and expl and not s_expl
        priced = (a_srch - a_null) / (1 - a_null) if band else None
        rows.append((nontriv, expl, s_expl, band, priced))
    f = lambda k: sum(1 for r_ in rows if r_[k]) / len(rows)
    pr = [r_[4] for r_ in rows if r_[4] is not None]
    return {"nontrivial": f(0), "exploitable": f(1), "surrogate_fp": f(2), "band": f(3),
            "priced_mean": statistics.mean(pr) if pr else None}


def main():
    rng = random.Random(SEED)
    print("d\tr\tnontrivial\texploitable\tsurrogate_fp\tband\tpriced_mean")
    for r in REUSE:
        for d in DEPTHS:
            c = cell(d, r, rng)
            print(f"{d}\t{r}\t{c['nontrivial']:.3f}\t{c['exploitable']:.3f}\t{c['surrogate_fp']:.3f}"
                  f"\t{c['band']:.3f}\t{c['priced_mean']}")


if __name__ == "__main__":
    main()
