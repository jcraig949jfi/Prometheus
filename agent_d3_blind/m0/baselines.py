"""Four history-free search baselines (M0 suite), frozen before any learner.

Each variant uses ONLY substrate-generic information reachable through the Ctx
API: validity, the whitelisted numeric observation dict, generic mutation,
generic recombination, and fresh program construction.  No semantic diagnostic
labels, no failure history, no target knowledge, no filesystem, no host
introspection.  All four receive the identical budget.
"""
from .harness import BudgetExhausted

VARIANTS = ["M0a", "M0b", "M0c", "M0d"]


def m0a_walk(ctx):
    """Generic local mutation walk; accept any valid child; periodic restart."""
    cur = ctx.seed()
    steps = 0
    try:
        while True:
            child = ctx.mutate(cur, 1 + (steps % 2))
            obs = ctx.evaluate(child)
            if obs["valid"]:
                cur = child
            steps += 1
            if steps % 200 == 0:
                cur = ctx.seed()
    except BudgetExhausted:
        pass
    return {"steps": steps}


def _cell(obs):
    d1 = min(11, int(obs["meanlen"]))
    d2 = min(12, int(obs["ndistinct"]))
    d3 = min(4, int(obs["idfrac"] * 4))
    return (d1, d2, d3)


def m0b_qd(ctx):
    """Generic MAP-Elites over substrate-generic behaviour descriptors."""
    archive = {}
    try:
        for s in ctx.seeds:
            obs = ctx.evaluate(s)
            if obs["valid"]:
                archive.setdefault(_cell(obs), s)
        keys = []
        steps = 0
        while True:
            if archive and ctx.rng.random() < 0.9:
                keys = list(archive.keys())
                parent = archive[keys[ctx.rng.randrange(len(keys))]]
            else:
                parent = ctx.seed()
            child = ctx.mutate(parent, ctx.rng.choice([1, 1, 2, 3]))
            obs = ctx.evaluate(child)
            steps += 1
            if not obs["valid"]:
                continue
            c = _cell(obs)
            old = archive.get(c)
            if old is None or len(child) < len(old):
                archive[c] = child
    except BudgetExhausted:
        pass
    return {"cells": len(archive)}


_SIZE_W = None


def _size_dist(ctx):
    global _SIZE_W
    if _SIZE_W is None:
        ws = [(s, 2.0 ** (-s / 8.0)) for s in range(1, 33)]
        tot = sum(w for _s, w in ws)
        acc, cum = 0.0, []
        for s, w in ws:
            acc += w / tot
            cum.append((acc, s))
        _SIZE_W = cum
    r = ctx.rng.random()
    for a, s in _SIZE_W:
        if r <= a:
            return s
    return 32


def m0c_cost_biased(ctx):
    """Cost-biased fresh random sampling of valid programs."""
    n = 0
    try:
        while True:
            p = ctx.fresh(_size_dist(ctx))
            ctx.evaluate(p)
            n += 1
    except BudgetExhausted:
        pass
    return {"samples": n}


def m0d_recomb(ctx):
    """Recombination of previously valid artifacts; no failure history."""
    archive = []
    seen = set()
    try:
        for s in ctx.seeds:
            obs = ctx.evaluate(s)
            if obs["valid"]:
                archive.append(s)
        n = 0
        while True:
            if len(archive) >= 2:
                a = archive[ctx.rng.randrange(len(archive))]
                b = archive[ctx.rng.randrange(len(archive))]
                child = ctx.recombine(a, b)
            else:
                child = ctx.mutate(ctx.seed(), 1)
            if ctx.rng.random() < 0.5:
                child = ctx.mutate(child, 1)
            obs = ctx.evaluate(child)
            n += 1
            if obs["valid"] and child not in seen:
                seen.add(child)
                archive.append(child)
                if len(archive) > 4000:
                    archive.pop(ctx.rng.randrange(len(archive)))
    except BudgetExhausted:
        pass
    return {"archive": len(archive)}


RUNNERS = {"M0a": m0a_walk, "M0b": m0b_qd, "M0c": m0c_cost_biased, "M0d": m0d_recomb}
