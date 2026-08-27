"""Frozen shared machinery for AGENT D-3 Phase 1.

One value domain for every basis.  A program IS a value, so homoiconicity is
structural rather than bolted on: `run(P, Q)` where Q is another program's
serialisation is the ordinary execution path, and the result is again a value
that may be read back as a program.

Nothing in this module knows anything about mutation families, targets,
witnesses or oracles.
"""
import hashlib

MAXVAL = 512
MAXLEN = 48
PROG_MAX = 32

# The single resource meter.  Every substrate `run` increments it.
METER = {"runs": 0}


def meter():
    return METER["runs"]


def clampv(x):
    x = int(x)
    if x > MAXVAL:
        return MAXVAL
    if x < -MAXVAL:
        return -MAXVAL
    return x


def clampl(seq):
    out = []
    n = 0
    for x in seq:
        if n >= MAXLEN:
            break
        out.append(clampv(x))
        n += 1
    return tuple(out)


class Fuel(Exception):
    pass


def h16(obj):
    return hashlib.sha1(repr(obj).encode()).hexdigest()[:16]


def sem_profile(sub, prog, probes):
    """Probe-relative semantic profile of an artifact."""
    if not sub.is_valid(prog):
        return {"fp": "INVALID", "outs": None, "nok": 0, "ndistinct": 0,
                "valid": False, "live": False}
    outs = []
    nok = 0
    for x in probes:
        o, st = sub.run(prog, x)
        if st == "ok":
            nok += 1
            outs.append(o)
        else:
            outs.append(st)
    nd = len(set(outs))
    live = (nok >= (len(probes) + 1) // 2) and nd >= 2
    return {"fp": h16(outs), "outs": outs, "nok": nok, "ndistinct": nd,
            "valid": True, "live": live}


def is_live_short(sub, prog, lprobes):
    """Liveness on the short battery, used only for downstream consumers."""
    if not sub.is_valid(prog):
        return False
    outs = []
    nok = 0
    for x in lprobes:
        o, st = sub.run(prog, x)
        if st == "ok":
            nok += 1
            outs.append(o)
        else:
            outs.append(st)
    return nok >= 2 and len(set(outs)) >= 2


def _lenbucket(d):
    if d <= -8:
        return -3
    if d <= -3:
        return -2
    if d < 0:
        return -1
    if d == 0:
        return 0
    if d < 3:
        return 1
    if d < 8:
        return 2
    return 3


def struct_profile(sub, prog, artifact_probes, lprobes):
    """Behaviour of an artifact *as a transformer of executable artifacts*."""
    if not sub.is_valid(prog):
        return {"fp": "INVALID", "live_consumer": False, "n_valid_out": 0}
    desc = []
    live_consumer = False
    n_valid_out = 0
    for a in artifact_probes:
        y, st = sub.run(prog, a)
        if st != "ok":
            desc.append((st,))
            continue
        v = sub.is_valid(y)
        if v:
            n_valid_out += 1
        sketch = tuple(sorted(set(int(t) % 8 for t in y)))
        desc.append(("ok", v, _lenbucket(len(y) - len(a)), y == a, sketch))
        if v and not live_consumer:
            if is_live_short(sub, y, lprobes):
                live_consumer = True
    return {"fp": h16(desc), "live_consumer": live_consumer,
            "n_valid_out": n_valid_out}


def token_edit_distance(p, q):
    """Levenshtein on token sequences (small programs, so exact is fine)."""
    n, m = len(p), len(q)
    if n == 0:
        return m
    if m == 0:
        return n
    prev = list(range(m + 1))
    for i in range(1, n + 1):
        cur = [i] + [0] * m
        pi = p[i - 1]
        for j in range(1, m + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1,
                         prev[j - 1] + (0 if pi == q[j - 1] else 1))
        prev = cur
    return prev[m]
