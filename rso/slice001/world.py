"""World W-S1: the finite transition fixture of the slice (C-004-T010).

Normative text: rso/slice001/contract/CONTRACT.md v1.0.0 draft A A2 (world and bounds), A3 (runtime boundary),
A4 (truth model), with AMENDMENT_v1.0.1.md. Registered numbers: contract.json `reset_model`.

What is here: the schedule and its 29 schedule points; the exact domain (4096 histories, in the canonical order
rso/slice001/checker.py also uses); the pending-message channel; the runtime interface every runtime under test
implements (`Runtime`); the life runner; the world-side truth table and the no-carry class N, both computed
from the domain alone and never from a runtime; and `closure_blockers`, which reports a registered model whose
horizon is shorter than its modelled delay (plan s3).

What is not here: no ruler, gate, reset predicate or receipt (T011, T012, T013). Runtimes that leave the
registered model raise BoundsViolation; turning that into the P0 BOUNDS outcome is the caller's.

Python >= 3.8, standard library only.
"""
from fractions import Fraction
from itertools import product

# --------------------------------------------------------------------------------------------------------
# Registered model (draft A A2; contract.json reset_model). tests/test_world.py pins these to contract.json.

EPISODES = 6                     # L
RESET_CALLS = EPISODES - 1       # one at every boundary
BOUNDARIES = (1, 2, 3)           # evaluated boundaries
R = len(BOUNDARIES)              # repeat count
H = 3                            # delay horizon, episodes after each evaluated boundary
K = 3                            # max channel delay, episodes
S = 2                            # sends per CUE tick
Q = 8                            # channel capacity (never binding from send(); see Runtime.send)
TICKS = ("DELIVER", "PROBE_A", "CUE", "PROBE_D")
HISTORIES = 4 ** EPISODES        # inputs (u_e, f_e) per episode
VARIANTS = ("STANDARD", "CLOCKED")
RESTORE_TARGETS = ("FRESH", "COMPLEMENT_PREFIX")

SCHEDULE_POINTS = tuple(
    p for e in range(1, EPISODES + 1)
    for p in ((("RESET", e - 1),) if e > 1 else ()) + tuple(("TICK", e, t) for t in TICKS))
"""Every point a hook sees, in order: after each tick, and after each boundary (whether or not it reset)."""

COMPONENT_CLASSES = ("ALLOWED", "FORBIDDEN", "SCHEDULE", "BOOKKEEPING")
BOUND_NAMES = ("SENDS_PER_CUE", "DELAY_RANGE", "CHANNEL_CAPACITY", "OUTPUT_ALPHABET")


class BoundsViolation(ValueError):
    """A runtime left the registered model (draft A A3; reason form AMENDMENT_v1.0.1 V4)."""

    def __init__(self, bound, episode, tick):
        assert bound in BOUND_NAMES
        self.bound, self.episode, self.tick = bound, episode, tick
        ValueError.__init__(self, "runtime outside the registered model: %s at (%s, %s)" % (bound, episode, tick))


def closure_blockers(reset_model):
    """Reasons a registered reset model cannot support closure (plan s3 Truth); [] when there are none.

    Blocks when the modelled channel delay exceeds the horizon, and when an evaluated boundary has fewer than
    H episodes after it inside the life (a delay of that length could land outside the life unseen).
    """
    life = reset_model["episodes_per_life"]
    horizon = reset_model["delay_horizon_H_episodes"]
    delay = reset_model["max_channel_delay_K_episodes"]
    out = []
    if delay > horizon:
        out.append("modelled delay K=%d exceeds horizon H=%d: closure blocked (plan s3)" % (delay, horizon))
    for j in reset_model["evaluated_boundaries"]:
        if j + horizon > life:
            out.append("horizon after boundary %d is %d episode(s) inside a %d-episode life, shorter than H=%d: "
                       "closure blocked (plan s3)" % (j, life - j, life, horizon))
    return out


# --------------------------------------------------------------------------------------------------------
# Domain and truth model (draft A A2, A4). History h in 0..4095; bits MSB first (u_1, f_1, ..., u_6, f_6),
# so increasing h is lexicographic order of the input tuple (the canonical order of A5 / V5).

def _check_variant(variant):
    if variant not in VARIANTS:
        raise ValueError("unknown world variant %r; registered: %s" % (variant, ", ".join(VARIANTS)))


def histories():
    return range(HISTORIES)


def u_of(h, e, variant="STANDARD"):
    """u_e of history h. CLOCKED: u_j = j mod 2 at the evaluated boundaries, the enumeration elsewhere."""
    _check_variant(variant)
    if variant == "CLOCKED" and e in BOUNDARIES:
        return e % 2
    return (h >> (2 * (EPISODES - e) + 1)) & 1


def f_of(h, e):
    return (h >> (2 * (EPISODES - e))) & 1


def inputs(h, variant="STANDARD"):
    """The exogenous inputs of history h: ((u_1, f_1), ..., (u_6, f_6))."""
    return tuple((u_of(h, e, variant), f_of(h, e)) for e in range(1, EPISODES + 1))


def complement(h):
    """The bitwise complement history (the COMPLEMENT_PREFIX restore target runs it)."""
    return h ^ (HISTORIES - 1)


def truth(h, variant="STANDARD"):
    """World-side answers for history h, written without any runtime.

    retained: truth at PROBE_A of episode j+1 for each evaluated j (= u_j). display: truth at PROBE_D of
    episode e (= f_e); enumerated, not scored by any registered predicate.
    """
    return {"retained": {j: u_of(h, j, variant) for j in BOUNDARIES},
            "display": {e: f_of(h, e) for e in range(1, EPISODES + 1)}}


def ones(j, variant="STANDARD"):
    """Number of histories with u_j = 1."""
    return sum(u_of(h, j, variant) for h in histories())


def no_carry_policies():
    """Class N (A4): every answer at PROBE_A of episode j+1 that is a function of j alone, as (g1, g2, g3)."""
    return tuple(product((0, 1), repeat=R))


def no_carry_success(policy, variant="STANDARD"):
    """Exact success of a policy in N over the (history, j) trials of the domain."""
    hits = sum(ones(j, variant) if policy[i] else HISTORIES - ones(j, variant) for i, j in enumerate(BOUNDARIES))
    return Fraction(hits, HISTORIES * R)


def domain_summary(variant="STANDARD"):
    """Eligible counts of the enumeration (reported beside any use of it)."""
    _check_variant(variant)
    return {"world": "W-S1", "variant": variant, "histories": HISTORIES, "episodes": EPISODES,
            "evaluated_boundaries": list(BOUNDARIES), "retention_trials": HISTORIES * R,
            "u_ones": {j: ones(j, variant) for j in BOUNDARIES}, "schedule_points": len(SCHEDULE_POINTS),
            "no_carry_policies": len(no_carry_policies())}


# --------------------------------------------------------------------------------------------------------
# Runtime boundary (draft A A3). A runtime under test is a composite: organism state, the pending-message
# channel and any adapter state. Subclasses override on_cue / on_deliver / answer / display / reset; the
# channel and the schedule counter are kept here so every realisation shares their semantics.

class Runtime:
    """The interface the harness sees: declare, step, reset, capture, restore.

    Channel entries are (due_episode, slot, bit) in send order: a send (bit, k) made at CUE of episode e is
    due at PROBE_D of e when k = 0, else at DELIVER of e + k. The episode counter `ep` advances at each
    DELIVER tick; it is SCHEDULE state (the same in every history at the same point).

    Base reset() is a no-op on purpose: what a reset erases is each runtime's own behaviour, judged by the
    reset predicates (T011), never assumed here.
    """

    def __init__(self):
        self.a = 0
        self.d = 0
        self.chan = []
        self.ep = 0
        self.log_n = 0
        self._sends = None
        self._tick = None

    # --- interface -------------------------------------------------------------------------------------
    def declare(self):
        return {"a": {"class": "ALLOWED", "domain": (0, 1), "initial": 0},
                "d": {"class": "FORBIDDEN", "domain": (0, 1), "initial": 0},
                "chan": {"class": "FORBIDDEN", "domain": "(due_episode, slot, bit) tuples, <= Q", "initial": ()},
                "ep": {"class": "SCHEDULE", "domain": tuple(range(EPISODES + 1)), "initial": 0},
                "log_n": {"class": "BOOKKEEPING", "domain": "non-negative int", "initial": 0}}

    def step(self, tick, obs=None):
        self._tick = tick
        if tick == "DELIVER":
            self.ep += 1
            self.on_deliver(self._deliver("DELIVER"))
            return None
        if tick == "PROBE_A":
            return (self.answer(), self.display())
        if tick == "CUE":
            self._sends = []
            self.on_cue(*obs)
            sends, self._sends = tuple(self._sends), None
            return sends
        if tick == "PROBE_D":
            self.on_deliver(self._deliver("PROBE_D"))
            return self.display()
        raise ValueError("unknown tick %r" % (tick,))

    def reset(self):
        pass

    def capture(self):
        return {"a": self.a, "d": self.d, "chan": tuple(tuple(p) for p in self.chan), "ep": self.ep,
                "log_n": self.log_n}

    def restore(self, c):
        if len(c["chan"]) > Q:
            raise BoundsViolation("CHANNEL_CAPACITY", c["ep"], "RESTORE")
        self.a, self.d, self.ep, self.log_n = c["a"], c["d"], c["ep"], c["log_n"]
        self.chan = [tuple(p) for p in c["chan"]]

    # --- what a realisation overrides ------------------------------------------------------------------
    def on_cue(self, u, f):
        pass

    def on_deliver(self, bits):
        if bits:
            self.d = bits[0]

    def answer(self):
        return self.a

    def display(self):
        return self.d

    # --- channel ---------------------------------------------------------------------------------------
    def send(self, bit, k):
        """Queue (bit, k). Only during CUE. With S = 2 and K = 3 at most 6 packets are ever in flight, so
        CHANNEL_CAPACITY (Q = 8) is reachable only through restore() of a hand-made capture."""
        if self._sends is None:
            raise BoundsViolation("OUTPUT_ALPHABET", self.ep, self._tick)
        if len(self._sends) >= S:
            raise BoundsViolation("SENDS_PER_CUE", self.ep, "CUE")
        if not (isinstance(k, int) and not isinstance(k, bool) and 0 <= k <= K) or bit not in (0, 1):
            raise BoundsViolation("DELAY_RANGE", self.ep, "CUE")
        if len(self.chan) >= Q:
            raise BoundsViolation("CHANNEL_CAPACITY", self.ep, "CUE")
        self._sends.append((bit, k))
        self.chan.append((self.ep + k, "PROBE_D" if k == 0 else "DELIVER", bit))

    def _deliver(self, slot):
        due = [p for p in self.chan if p[0] == self.ep and p[1] == slot]
        if due:
            self.chan = [p for p in self.chan if not (p[0] == self.ep and p[1] == slot)]
        return tuple(p[2] for p in due)


# --------------------------------------------------------------------------------------------------------
# Life runner.

def _check_output(tick, out, episode):
    bits = (0, 1)
    if tick == "DELIVER":
        ok = out is None
    elif tick == "PROBE_A":
        ok = isinstance(out, tuple) and len(out) == 2 and all(type(x) is int and x in bits for x in out)
    elif tick == "CUE":
        ok = (isinstance(out, tuple) and len(out) <= S
              and all(isinstance(s, tuple) and len(s) == 2 and s[0] in bits and type(s[1]) is int
                      and 0 <= s[1] <= K for s in out))
    else:
        ok = type(out) is int and out in bits
    if not ok:
        raise BoundsViolation("OUTPUT_ALPHABET", episode, tick)


class LifeRecord:
    """Outputs of one life: 24 tick outputs in schedule order, plus what the channel delivered."""

    def __init__(self, h, variant, reset_at):
        self.history, self.variant, self.reset_at = h, variant, reset_at
        self.outputs = []
        self._deliveries = {}

    def _at(self, e, tick):
        return self.outputs[(e - 1) * len(TICKS) + TICKS.index(tick)]

    def probe_a(self, e):
        return self._at(e, "PROBE_A")

    def probe_d(self, e):
        return self._at(e, "PROBE_D")

    def sends(self, e):
        return self._at(e, "CUE")

    def deliveries(self, e):
        """(bits delivered at DELIVER, bits delivered at PROBE_D) of episode e, read from the channel."""
        return self._deliveries[e]


def _due(rt, e, slot):
    return tuple(p[2] for p in getattr(rt, "chan", ()) if p[0] == e and p[1] == slot)


def run_life(make, h, variant="STANDARD", reset_at=None, hook=None):
    """Run one life of history h on a runtime from `make()`.

    reset_at: boundaries at which reset() is called (default: all five). hook(runtime, point) is called at
    every SCHEDULE_POINT and returns the runtime to continue with (it may capture, restore into another
    instance, clamp or observe). Raises BoundsViolation if the runtime leaves the registered model.
    """
    reset_at = frozenset(range(1, EPISODES)) if reset_at is None else frozenset(reset_at)
    xs = inputs(h, variant)
    rec = LifeRecord(h, variant, reset_at)
    rt = make()
    for e in range(1, EPISODES + 1):
        if e > 1:
            if (e - 1) in reset_at:
                rt.reset()
            if hook is not None:
                rt = hook(rt, ("RESET", e - 1))
        got = []
        for tick in TICKS:
            if tick in ("DELIVER", "PROBE_D"):
                got.append(_due(rt, e, tick))
            out = rt.step(tick, xs[e - 1] if tick == "CUE" else None)
            _check_output(tick, out, e)
            rec.outputs.append(out)
            if hook is not None:
                rt = hook(rt, ("TICK", e, tick))
        rec._deliveries[e] = tuple(got)
    rec.outputs = tuple(rec.outputs)
    return rec
