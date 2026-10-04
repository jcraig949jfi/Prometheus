"""Observer qualification over world W-S1 (C-004-T011): draft A A5 P7 with AMENDMENT_v1.0.1 V4 reason forms.

P7 has two parts, both required:
  CAPTURE_PURE  outputs with capture() called after every tick equal outputs with no calls at all;
  OBS_EQ        for every history, outputs AND the declared ALLOWED / FORBIDDEN / SCHEDULE components captured
                after every tick (after the observer's action there) equal those of the null observer.
                BOOKKEEPING components are excluded from the state part and never from the output part.
An observer is qualified only for the runtime it was checked on. Observers act after each of the 24 ticks
(contract count 4096 x (24 outputs + 24 states) = 196608).

An observer is obs(runtime, point, h) -> runtime, point = ("TICK", episode, tick).
Python >= 3.8, standard library only.
"""
from rso.slice001 import reset as RS
from rso.slice001 import world as W

TICK_POINTS = [i for i, p in enumerate(W.SCHEDULE_POINTS) if p[0] == "TICK"]
N_TICKS = len(TICK_POINTS)


def _state_keys(make):
    return [k for k, v in make().declare().items() if v["class"] != "BOOKKEEPING"]


def _trace(make, h, obs, keys, variant):
    """[(point, output, {component: value})] after every tick, the observer having acted first."""
    rows, outs = [], []

    def after(i, rt):
        p = W.SCHEDULE_POINTS[i]
        if p[0] != "TICK":
            return rt
        if obs is not None:
            rt = obs(rt, p, h)
        c = rt.capture()
        rows.append((p, {k: c[k] for k in keys}))
        return rt
    outs = RS.run_points(make(), h, 0, RS.N_POINTS, variant, after=after)
    return [(p, o, s) for (p, s), o in zip(rows, outs)]


def capture_pure(make, variant="STANDARD"):
    eligible = W.HISTORIES * N_TICKS
    try:
        for h in W.histories():
            plain = RS.run_points(make(), h, 0, RS.N_POINTS, variant)
            watched = RS.run_points(make(), h, 0, RS.N_POINTS, variant,
                                    after=lambda i, rt: (rt.capture(), rt)[1])
            for k, (x, y) in enumerate(zip(plain, watched)):
                if x != y:
                    _, e, tick = W.SCHEDULE_POINTS[TICK_POINTS[k]]
                    return RS._gate("P7", "FAIL", "capture() changes future output at (%d, %s)" % (e, tick),
                                    {"history": h, "episode": e, "tick": tick, "what": "output"}, eligible)
    except W.BoundsViolation:
        return RS._blocked("P7")
    return RS._gate("P7", "PASS", "capture() leaves every output unchanged", None, eligible)


def obs_eq(make, obs, name, variant="STANDARD", outputs_only=False):
    keys = [] if outputs_only else _state_keys(make)
    eligible = W.HISTORIES * N_TICKS * (1 if outputs_only else 2)
    try:
        for h in W.histories():
            ref = _trace(make, h, None, keys, variant)
            got = _trace(make, h, obs, keys, variant)
            for (p, o0, s0), (_p, o1, s1) in zip(ref, got):
                what = "output" if o0 != o1 else next(("state:%s" % k for k in keys if s0[k] != s1[k]), None)
                if what is not None:
                    _, e, tick = p
                    return RS._gate("P7", "FAIL", "observer %s changes %s at (%d, %s)" % (name, what, e, tick),
                                    {"history": h, "episode": e, "tick": tick, "what": what}, eligible)
    except W.BoundsViolation:
        return RS._blocked("P7")
    return RS._gate("P7", "PASS", "outputs and declared non-BOOKKEEPING state identical to the null observer",
                    None, eligible)


def observer(make, obs, name, variant="STANDARD"):
    """P7 for the pair (runtime, observer): CAPTURE_PURE, then OBS_EQ."""
    cp = capture_pure(make, variant)
    if cp["value"] != "PASS":
        return cp
    return obs_eq(make, obs, name, variant)
