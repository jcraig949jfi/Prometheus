"""Reset, preservation, channel and restart predicates over world W-S1 (C-004-T011).

Normative text: CONTRACT.md v1.0.0 draft A A5 (P0 BOUNDS, P3 ERASE, P4 PRESERVE, P5 CHANNEL, P6 RESTART) with
AMENDMENT_v1.0.1 (V4 reason forms, V5 canonical order and pair partner). Every predicate here is behavioural:
it compares outputs of whole lives, so undeclared and hidden runtime state is covered within the registered
model (draft A A7).

Outcome shape (the C1 outcome field, as rso/slice001/checker.py recomputes it): kind, predicate, value
(PASS / FAIL, or None when execution is BLOCKED), reason, witness (first in canonical order, FAIL only),
eligible_count, applicable_count, vacuous, plus `execution` {status: RAN | BLOCKED, missing: [...]}.
A runtime that leaves the registered model blocks every predicate ("runtime inside the registered model")
and fails BOUNDS (draft A A3).

Python >= 3.8, standard library only.
"""
from rso.slice001 import world as W

POINTS = W.SCHEDULE_POINTS
N_POINTS = len(POINTS)
TICK_INDEX = {p: i for i, p in enumerate(POINTS)}
INSIDE = "runtime inside the registered model"


def u_bit(e):
    return 2 * (W.EPISODES - e) + 1


def f_bit(e):
    return 2 * (W.EPISODES - e)


def forbidden_mask(j):
    """History bits forbidden at boundary j: every input of episodes 1..j except u_j (A5 P3)."""
    m = 1 << f_bit(j)
    for e in range(1, j):
        m |= (1 << u_bit(e)) | (1 << f_bit(e))
    return m


def _ran():
    return {"status": "RAN", "missing": []}


def _gate(pid, value, reason, witness, eligible, applicable=None):
    return {"kind": "GATE", "predicate": pid, "execution": _ran(), "value": value, "reason": reason,
            "witness": witness if value == "FAIL" else None, "eligible_count": eligible,
            "applicable_count": applicable, "vacuous": applicable == 0}


def _blocked(pid):
    return {"kind": "GATE", "predicate": pid, "execution": {"status": "BLOCKED", "missing": [INSIDE]},
            "value": None, "reason": None, "witness": None, "eligible_count": None, "applicable_count": None,
            "vacuous": False}


def run_points(rt, h, start, stop, variant="STANDARD", reset_at=None, after=None):
    """Perform schedule points start..stop-1 of history h on `rt`; return the outputs of their TICK points.

    The action of ("RESET", j) is rt.reset() when j is in reset_at (default all five); of ("TICK", e, t) is
    rt.step(t, ...). after(i, rt) runs after point i's action and returns the runtime to continue with.
    Equal to world.run_life from 0 to N_POINTS (tests/test_reset_observer.py TestRunner).
    """
    reset_at = frozenset(range(1, W.EPISODES)) if reset_at is None else reset_at
    xs = W.inputs(h, variant)
    outs = []
    for i in range(start, stop):
        p = POINTS[i]
        if p[0] == "RESET":
            if p[1] in reset_at:
                rt.reset()
        else:
            _, e, tick = p
            out = rt.step(tick, xs[e - 1] if tick == "CUE" else None)
            W._check_output(tick, out, e)
            outs.append(out)
        if after is not None:
            rt = after(i, rt)
    return tuple(outs)


def _episodes(outs):
    """Per episode e: (PROBE_A, CUE, PROBE_D) outputs; DELIVER returns nothing."""
    return {e: (outs[4 * (e - 1) + 1], outs[4 * (e - 1) + 2], outs[4 * (e - 1) + 3])
            for e in range(1, W.EPISODES + 1)}


def _lives(make, variant="STANDARD", reset_at=None):
    return [run_points(make(), h, 0, N_POINTS, variant, reset_at) for h in W.histories()]


# --------------------------------------------------------------------------------------------------------

def bounds(make, variant="STANDARD"):
    """P0: every life of the domain stays inside S, K, Q and the output alphabet."""
    for h in W.histories():
        try:
            run_points(make(), h, 0, N_POINTS, variant)
        except W.BoundsViolation as e:
            return _gate("P0", "FAIL", str(e), {"history": h, "episode": e.episode, "tick": e.tick,
                                                 "bound": e.bound}, W.HISTORIES)
    return _gate("P0", "PASS", "every life stays inside the registered model", None, W.HISTORIES)


def erase(make, variant="STANDARD"):
    """P3: histories agreeing on u_j and on every input after episode j give identical outputs at every tick
    of episodes j+1..j+H. Pair = a history and its class representative (forbidden bits cleared; V5)."""
    try:
        eps = [_episodes(o) for o in _lives(make, variant)]
    except W.BoundsViolation:
        return _blocked("P3")
    masks = {j: forbidden_mask(j) for j in W.BOUNDARIES}
    names = ("PROBE_A", "CUE", "PROBE_D")
    pairs, witness = 0, None
    for h in W.histories():
        for j in W.BOUNDARIES:
            r = h & ~masks[j]
            if r == h:
                continue
            pairs += 1
            if witness is not None:
                continue
            for e in range(j + 1, j + W.H + 1):
                diff = [t for t, x, y in zip(names, eps[h][e], eps[r][e]) if x != y]
                if diff:
                    witness = {"history": h, "partner": r, "j": j, "episode": e, "tick": diff[0]}
                    break
    if witness is not None:
        return _gate("P3", "FAIL", "forbidden influence across boundary %d, first visible at (%d, %s)"
                     % (witness["j"], witness["episode"], witness["tick"]), witness, pairs)
    return _gate("P3", "PASS", "no forbidden influence across boundaries 1-3 within the horizon", None, pairs)


def preserve(make, variant="STANDARD"):
    """P4: for each pair differing only in u_j (u_j = 1 and its partner with u_j = 0), if y_A at PROBE_A of
    episode j+1 differs with the reset at j replaced by no reset, it must differ with the reset too."""
    try:
        with_reset = _lives(make, variant)
        skip = {j: _lives(make, variant, frozenset(range(1, W.EPISODES)) - {j}) for j in W.BOUNDARIES}
    except W.BoundsViolation:
        return _blocked("P4")

    def y_a(outs, e):
        return outs[4 * (e - 1) + 1][0]
    pairs, applicable, witness = 0, 0, None
    for h in W.histories():
        for j in W.BOUNDARIES:
            if not (h >> u_bit(j)) & 1:
                continue
            r = h & ~(1 << u_bit(j))
            pairs += 1
            if y_a(skip[j][h], j + 1) == y_a(skip[j][r], j + 1):
                continue
            applicable += 1
            if witness is None and y_a(with_reset[h], j + 1) == y_a(with_reset[r], j + 1):
                witness = {"history": h, "partner": r, "j": j}
    if witness is not None:
        return _gate("P4", "FAIL", "reset at %d destroys allowed content carried without it" % witness["j"],
                     witness, pairs, applicable)
    return _gate("P4", "PASS", "every difference carried without a reset survives it", None, pairs, applicable)


def clamp_answers(make, h, variant="STANDARD"):
    """y_A at PROBE_A of episode j+1 after `a` := v is set (capture, edit, restore) right after the reset at j,
    for (j, v) in (1,0), (1,1), (2,0), (2,1), (3,0), (3,1): the trace:clamp row of history h."""
    row = []
    for j in W.BOUNDARIES:
        at = TICK_INDEX[("RESET", j)]
        probe = TICK_INDEX[("TICK", j + 1, "PROBE_A")]
        for v in (0, 1):
            def after(i, rt, at=at, v=v):
                if i == at:
                    c = rt.capture()
                    c["a"] = v
                    rt.restore(c)
                return rt
            outs = run_points(make(), h, 0, probe + 1, variant, after=after)
            row.append(outs[-1][0])
    return tuple(row)


def channel(make, variant="STANDARD"):
    """P5: after the reset at each evaluated j, clamping `a` to v makes the retained answer v. Applied through
    restore, so it is meaningful only with RESTART PASS (draft A A5 couplings)."""
    witness, n = None, 0
    try:
        for h in W.histories():
            row = clamp_answers(make, h, variant)
            for k, (j, v) in enumerate((j, v) for j in W.BOUNDARIES for v in (0, 1)):
                n += 1
                if witness is None and row[k] != v:
                    witness = {"history": h, "j": j, "v": v}
    except W.BoundsViolation:
        return _blocked("P5")
    if witness is not None:
        return _gate("P5", "FAIL", "retained answer does not follow the declared allowed channel at %d"
                     % witness["j"], witness, n)
    return _gate("P5", "PASS", "retained answer follows the declared allowed channel", None, n)


def _freeze(c):
    """A hashable copy of a capture mapping (values are ints, tuples of tuples, or other hashables)."""
    return tuple(sorted((k, v if not isinstance(v, list) else tuple(v)) for k, v in c.items()))


def _point_label(p):
    return "(RESET %d)" % p[1] if p[0] == "RESET" else "(%d, %s)" % (p[1], p[2])


def restart(make, variant="STANDARD"):
    """P6: run to each of the 29 cut points, capture, restore into a target, continue the same history to the
    end of the life; the continuation's outputs equal the uninterrupted run's. Targets FRESH and
    COMPLEMENT_PREFIX (an instance that ran the complement history to the same cut). Canonical order:
    history, cut point, target. Stops comparing at the first witness; the eligible count is the domain."""
    eligible = W.HISTORIES * N_POINTS * len(W.RESTORE_TARGETS)
    n_before = [sum(1 for p in POINTS[:i + 1] if p[0] == "TICK") for i in range(N_POINTS)]
    # A FRESH target's continuation is a function of (cut, capture, inputs after the cut) only, so it is
    # computed once per distinct key. Episodes after the cut's episode are the suffix; the cut's own episode
    # is always included whole (its CUE may still be ahead).
    fresh_memo = {}
    try:
        for h in W.histories():
            base = run_points(make(), h, 0, N_POINTS, variant)
            caps = []
            run_points(make(), h, 0, N_POINTS, variant, after=lambda i, rt: caps.append(rt.capture()) or rt)
            comp = W.complement(h)
            xs = W.inputs(h, variant)
            for i in range(N_POINTS):
                tail = base[n_before[i]:]
                for target in W.RESTORE_TARGETS:
                    if target == "FRESH":
                        key = (i, _freeze(caps[i]), xs[POINTS[i][1] - 1:])
                        cont = fresh_memo.get(key)
                        if cont is None:
                            t = make()
                            t.restore(caps[i])
                            cont = fresh_memo[key] = run_points(t, h, i + 1, N_POINTS, variant)
                    else:
                        t = make()
                        run_points(t, comp, 0, i + 1, variant)
                        t.restore(caps[i])
                        cont = run_points(t, h, i + 1, N_POINTS, variant)
                    if cont != tail:
                        w = {"history": h, "cut": i, "point": list(POINTS[i]), "target": target}
                        return _gate("P6", "FAIL", "capture/restore loses future-influencing state at %s, target %s"
                                     % (_point_label(POINTS[i]), target), w, eligible)
    except W.BoundsViolation:
        return _blocked("P6")
    return _gate("P6", "PASS", "continuations equal the uninterrupted run", None, eligible)
