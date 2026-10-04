"""E06 twins of the sound register REG (C-004-T018): run and reported, not an exit criterion of the slice.

Normative text: CONTRACT.md draft A A5 P8 (TWIN_EQ) and A6 rows E06, AMENDMENT_v1.0.1 V4 (TWIN_EQ compares outcome
VALUES only), closure F (E06 belongs to the native witness) and D08 (two realisations related by a reversible
encoding, or sharing code, are ONE physics).

  REG_ONEHOT  REG with a and d stored only as one-hot pairs (x, 1 - x); capture/restore map to the declared
              components, as an adapter would.
  REG_FLAT    REG flattened into one transition table over its reachable declared state (plus every clamp
              of a), built once by exploring REG; the runtime holds a single state tuple and only looks up.
  LOSSY       the false case: an "encoding" mapping both values of a to one code.

A twin earns no second physics and no promotion: every report row says physics ONE. Nothing here renders a
claim (draft B's).
Python >= 3.8, standard library only.
"""
from rso.slice001 import observer as OB
from rso.slice001 import reset as RS
from rso.slice001 import rulers as RU
from rso.slice001 import world as W
from rso.slice001.fixtures import world_cases as WC

PREDICATES = ("P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7")
NAMES = {"P0": "BOUNDS", "P1": "CALIBRATION", "P2": "RETENTION", "P3": "ERASE", "P4": "PRESERVE",
         "P5": "CHANNEL", "P6": "RESTART", "P7": "OBSERVER"}


# --------------------------------------------------------------------------------------------------------

class REG_ONEHOT(W.Runtime):
    """REG with a and d held only as one-hot pairs."""

    def __init__(self):
        W.Runtime.__init__(self)
        del self.a, self.d
        self.aa, self.dd = (1, 0), (1, 0)

    @staticmethod
    def _enc(x):
        return (1 - x, x)

    @staticmethod
    def _dec(p):
        return p[1]

    def on_cue(self, u, f):
        self.aa, self.dd = self._enc(u), self._enc(f)

    def on_deliver(self, bits):
        if bits:
            self.dd = self._enc(bits[0])

    def answer(self):
        return self._dec(self.aa)

    def display(self):
        return self._dec(self.dd)

    def reset(self):
        self.dd = self._enc(0)
        self.chan = []

    def capture(self):
        return {"a": self._dec(self.aa), "d": self._dec(self.dd), "chan": tuple(tuple(p) for p in self.chan),
                "ep": self.ep, "log_n": self.log_n}

    def restore(self, c):
        if len(c["chan"]) > W.Q:
            raise W.BoundsViolation("CHANNEL_CAPACITY", c["ep"], "RESTORE")
        self.aa, self.dd, self.ep, self.log_n = self._enc(c["a"]), self._enc(c["d"]), c["ep"], c["log_n"]
        self.chan = [tuple(p) for p in c["chan"]]


def _key(c):
    return (c["a"], c["d"], tuple(c["chan"]), c["ep"])


def _actions():
    acts = [("TICK", t, None) for t in ("DELIVER", "PROBE_A", "PROBE_D")]
    acts += [("TICK", "CUE", (u, f)) for u in (0, 1) for f in (0, 1)]
    return acts + [("RESET", None, None)]


def _build_table(source=WC.REG):
    """{(state, action): (next state, output)} over every declared state reachable from the initial state, closed
    under clamping a (P5) so restore of any reachable capture with either value of a is covered."""
    table, todo, seen = {}, [], set()

    def push(state):
        for a in (0, 1):
            s = (a,) + state[1:]
            if s not in seen:
                seen.add(s)
                todo.append(s)
    push(_key(source().capture()))
    while todo:
        s = todo.pop()
        if s[3] > W.EPISODES:
            continue
        for act in _actions():
            rt = source()
            rt.restore({"a": s[0], "d": s[1], "chan": s[2], "ep": s[3], "log_n": 0})
            if act[0] == "RESET":
                rt.reset()
                out = None
            else:
                rt._tick = act[1]
                out = rt.step(act[1], act[2])
            nxt = _key(rt.capture())
            table[(s, act)] = (nxt, out)
            push(nxt)
    return table


FLAT_TABLE = _build_table()


class REG_FLAT(W.Runtime):
    """REG as one state tuple advanced by FLAT_TABLE lookups only."""

    def __init__(self):
        self.state = (0, 0, (), 0)
        self.log_n = 0
        self._tick = None

    def step(self, tick, obs=None):
        self._tick = tick
        self.state, out = FLAT_TABLE[(self.state, ("TICK", tick, obs))]
        return out

    def reset(self):
        self.state = FLAT_TABLE[(self.state, ("RESET", None, None))][0]

    def capture(self):
        a, d, chan, ep = self.state
        return {"a": a, "d": d, "chan": chan, "ep": ep, "log_n": self.log_n}

    def restore(self, c):
        if len(c["chan"]) > W.Q:
            raise W.BoundsViolation("CHANNEL_CAPACITY", c["ep"], "RESTORE")
        self.state, self.log_n = _key(c), c["log_n"]


class LOSSY(WC.REG):
    """False twin: both values of a map to one code (0); the bit is lost at the CUE and on restore."""

    def on_cue(self, u, f):
        self.a, self.d = 0, f

    def restore(self, c):
        WC.REG.restore(self, dict(c, a=0))


# --------------------------------------------------------------------------------------------------------

def outcome_vector(make, variant="STANDARD"):
    """Outcome VALUES of P0-P7 for a runtime (P7 with the null observer)."""
    return {"P0": RS.bounds(make, variant)["value"],
            "P1": RU.calibration(variant)["value"],
            "P2": RU.retention_of_runtime(make, variant)["value"],
            "P3": RS.erase(make, variant)["value"],
            "P4": RS.preserve(make, variant)["value"],
            "P5": RS.channel(make, variant)["value"],
            "P6": RS.restart(make, variant)["value"],
            "P7": OB.observer(make, WC.NULL, "NULL", variant)["value"]}


def twin_eq(make, twin, vectors=None):
    """P8: PASS iff the twin's P0-P7 outcome values equal the runtime's. Reason form V4 on FAIL."""
    m_name, t_name = make.__name__, twin.__name__
    vm, vt = vectors if vectors is not None else (outcome_vector(make), outcome_vector(twin))
    for p in PREDICATES:
        if vm[p] != vt[p]:
            return RS._gate("P8", "FAIL", "twin %s differs from %s on %s: %s vs %s"
                            % (t_name, m_name, NAMES[p], vm[p], vt[p]), {"predicate": p, "m": vm[p], "twin": vt[p]},
                            len(PREDICATES))
    return RS._gate("P8", "PASS", "twin %s has the outcome values of %s on P0-P7" % (t_name, m_name), None,
                    len(PREDICATES))


TWINS = ((REG_ONEHOT, "reversible re-encoding of a and d (one-hot pairs)"),
         (REG_FLAT, "flattened transition table of REG"),
         (LOSSY, "non-reversible encoding (false case)"))


def e06_report(vectors=None, base=WC.REG):
    """One row per twin: TWIN_EQ value, outcome vectors, and physics ONE. Never an exit criterion."""
    vectors = dict(vectors or {})
    for m in (base,) + tuple(t for t, _ in TWINS):
        if m not in vectors:
            vectors[m] = outcome_vector(m)
    rows = []
    for twin, relation in TWINS:
        out = twin_eq(base, twin, (vectors[base], vectors[twin]))
        rows.append({"case": "E06", "runtime": base.__name__, "twin": twin.__name__, "relation": relation,
                     "twin_eq": out["value"], "reason": out["reason"], "vector": vectors[twin],
                     "physics": "ONE", "exit_criterion": False,
                     "promotion": "none: one physics, no cross-physics or recursion claim"})
    return rows
