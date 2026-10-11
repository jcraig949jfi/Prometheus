"""A tiny mechanism DSL with ANALYTIC ground truth (frozen in pan/tests/negspace_prereg.json). It serves twice:
  * a held-out calibration source: random pairs of DSL mechanisms labelled by parameter comparison alone (no
    evaluator is consulted), so the distinctness evaluator is tested on pairs nobody designed one by one;
  * arm D's non-LLM symbolic generator (harness.py).

Parameters: storage (list | deque | ring | history | world), delay d (1-4), reset ('none' | 'zero': storage cleared
when x == 0), cap (None | 100 | 1000: from step index cap on the mechanism outputs 0), noop (executed machinery that
never affects output). Behavior depends only on (d, reset, cap, storage == 'world'); storage among the four internal
kinds and noop are representation only.
"""
import random

STORAGES = ("list", "deque", "ring", "history", "world")


def params_space():
    for s in STORAGES:
        for d in (1, 2, 3, 4):
            for r in ("none", "zero"):
                for c in (None, 100, 1000):
                    for n in (False, True):
                        yield dict(storage=s, d=d, reset=r, cap=c, noop=n)


def source(p):
    s, d, reset, cap, noop = p["storage"], p["d"], p["reset"], p["cap"], p["noop"]
    L = []
    if s == "deque":
        L += ["from collections import deque", ""]
    L += ["class Mechanism:", "    def __init__(self, world):"]
    if s == "list":
        L.append("        self.buf = [0] * {}".format(d))
    elif s == "deque":
        L.append("        self.buf = deque([0] * {})".format(d))
    elif s == "ring":
        L += ["        self.ring = [0] * {}".format(d), "        self.i = 0"]
    elif s == "history":
        L.append("        self.seen = []")
    else:
        L += ["        self.world = world", "        self.t = 0"]
    if cap is not None and s != "world":
        L.append("        self.n = 0")
    if noop:
        L.append("        self.aux = 0")
    L.append("    def step(self, x):")
    if cap is not None:
        if s == "world":
            L += ["        if self.t >= {}:".format(cap), "            self.t += 1", "            return 0"]
        else:
            L += ["        self.n += 1", "        if self.n > {}:".format(cap), "            return 0"]
    if reset == "zero":
        L.append("        if x == 0:")
        L.append({"list": "            self.buf = [0] * {}".format(d),
                  "deque": "            self.buf = deque([0] * {})".format(d),
                  "ring": "            self.ring = [0] * {}".format(d),
                  "history": "            self.seen = [0] * {}".format(d),
                  "world": "            self.world.clear()"}[s])
    if noop:
        L.append("        self.aux = (self.aux + x) % 7")
    if s in ("list", "deque"):
        L += ["        self.buf.append(x)",
              "        return self.buf.pop(0)" if s == "list" else "        return self.buf.popleft()"]
    elif s == "ring":
        L += ["        out = self.ring[self.i]", "        self.ring[self.i] = x",
              "        self.i = (self.i + 1) % {}".format(d), "        return out"]
    elif s == "history":
        L += ["        self.seen.append(x)", "        return self.seen[-{}] if len(self.seen) > {} else 0".format(d + 1, d)]
    else:
        L += ["        self.world[self.t] = x", "        y = self.world.get(self.t - {}, 0)".format(d),
              "        self.t += 1", "        return y"]
    return "\n".join(L) + "\n"


def behavior_key(p):
    """What the suite can see: (d, reset, cap visible within the suite's 200 steps, environmental storage)."""
    cap_vis = p["cap"] if (p["cap"] is not None and p["cap"] <= 200) else None
    return (p["d"], p["reset"], cap_vis, p["storage"] == "world")


def label(p, q):
    """Analytic truth for a pair: DISTINCT if the suite can see a difference; UNRESOLVED if the only difference is a cap
    beyond the suite (1000 vs none); else EQUIVALENT (representation-only differences)."""
    if behavior_key(p) != behavior_key(q):
        return "DISTINCT"
    if p["cap"] != q["cap"]:
        return "UNRESOLVED"
    return "EQUIVALENT"


def sample_pairs(n, seed):
    """n pairs drawn so the three labels are represented (stratified by construction: a third each where possible)."""
    rng = random.Random(seed)
    space = list(params_space())
    out, want = [], {"EQUIVALENT": n // 3, "UNRESOLVED": n // 3}
    want["DISTINCT"] = n - want["EQUIVALENT"] - want["UNRESOLVED"]
    got = {k: 0 for k in want}
    guard = 0
    while sum(got.values()) < n and guard < 200000:
        guard += 1
        p = rng.choice(space)
        q = dict(p)
        kind = rng.choice(["EQUIVALENT", "UNRESOLVED", "DISTINCT"])
        if kind == "EQUIVALENT":
            if p["storage"] != "world":
                q["storage"] = rng.choice([s for s in STORAGES if s != "world"])
            q["noop"] = rng.choice([False, True])
        elif kind == "UNRESOLVED":
            if p["cap"] == 100:
                continue
            q["cap"] = None if p["cap"] == 1000 else 1000
            if p["storage"] != "world":
                q["storage"] = rng.choice([s for s in STORAGES if s != "world"])
        else:
            q = rng.choice(space)
        lab = label(p, q)
        if p == q or got.get(lab, n) >= want[lab]:
            continue
        got[lab] += 1
        out.append((p, q, lab))
    return out
