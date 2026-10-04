"""Runtime and observer fixtures for world W-S1 (C-004-T011): draft A A6 cases and the C3 escape placement (A7).

Each runtime is a world.Runtime realisation. Behaviour, not name, is binding (CONTRACT.md R5). Undeclared
attributes (hidden state) are deliberate where a case needs state that capture() omits.

ESCAPES lists every IN-MODEL known escape of draft A A7 as a named fixture with the predicate that must now
catch it. STATED_LIMITS pins OUT-OF-MODEL faults that the registered model passes by construction, so a
passing slice is never read as covering them. tests/test_reset_observer.py runs both lists.

Python >= 3.8, standard library only.
"""
from rso.slice001 import world as W


# --------------------------------------------------------------------------------------------------------
# Sound references.

class REG(W.Runtime):
    """a := u, d := f at CUE; reset clears d and the channel, keeps a."""

    def on_cue(self, u, f):
        self.a, self.d = u, f

    def reset(self):
        self.d = 0
        self.chan = []


class PKTD(REG):
    """Display realised through the channel with k = 0 (non-empty channel mid-episode)."""

    def on_cue(self, u, f):
        self.a = u
        self.send(f, 0)


# --------------------------------------------------------------------------------------------------------
# Retention-side cases (T01, T02; used by T012 and by CHANNEL here).

class AMNESIAC(REG):
    """No carry: a is never written; the answer is read from a (X05: answer from a, so CHANNEL PASS)."""

    def on_cue(self, u, f):
        self.d = f


class FLIP(REG):
    """Answers 1 - a: carries u perfectly, answers it wrong (RETENTION NOT_SHOWN, s = 0)."""

    def answer(self):
        return 1 - self.a


class QCARRY(REG):
    """Right answer through the FORBIDDEN channel: sends (u, 1), a := delivered bit; reset keeps the channel."""

    def on_cue(self, u, f):
        self.d = f
        self.send(u, 1)

    def on_deliver(self, bits):
        if bits:
            self.a = bits[0]

    def reset(self):
        self.d = 0


# --------------------------------------------------------------------------------------------------------
# Reset cases (T03-T05, T08).

class WIPE(REG):
    """T05: the reset also erases the allowed register."""

    def reset(self):
        self.a, self.d, self.chan = 0, 0, []


class LAGD(REG):
    """T04: display-only erase; the forbidden bit is also sent with k = 1 and arrives after the reset."""

    def on_cue(self, u, f):
        self.a, self.d = u, f
        self.send(f, 1)

    def reset(self):
        self.d = 0


class EVERY3(REG):
    """T08: flushes the channel on every call, clears d on every call except the third."""

    def __init__(self):
        REG.__init__(self)
        self.calls = 0

    def reset(self):
        self.calls += 1
        self.chan = []
        if self.calls % 3:
            self.d = 0


class SLEEPER(REG):
    """T08: undeclared two-slot memory of f; display at PROBE_D of episode e is f_e XOR f_(e-2)."""

    def __init__(self):
        REG.__init__(self)
        self.old, self.older = 0, 0

    def on_cue(self, u, f):
        use, self.older, self.old = self.older, self.old, f
        self.a, self.d = u, f ^ use


class SNEAKY(REG):
    """State that survives reset and shows only when a cue arrives: display = f_e XOR f_(e-1)."""

    def __init__(self):
        REG.__init__(self)
        self.prev = 0

    def on_cue(self, u, f):
        self.a, self.d, self.prev = u, f ^ self.prev, f


class SPLIT1(REG):
    """T08 split: a := u and undeclared c := f XOR u, both kept by the reset. After a reset the display shows
    c XOR a = f of the previous episode. Neither share alone carries f."""

    def __init__(self):
        REG.__init__(self)
        self.c, self.fresh = 0, True

    def on_cue(self, u, f):
        self.a, self.d, self.c, self.fresh = u, f, f ^ u, True

    def display(self):
        return self.d if self.fresh else self.c ^ self.a

    def reset(self):
        REG.reset(self)
        self.fresh = False


class SPLIT2(REG):
    """T08 split: a := u, sends (f XOR u, 1) and does not flush; on delivery d := bit XOR a. The packet alone
    is uniform and independent of f."""

    def on_cue(self, u, f):
        self.a, self.d = u, f
        self.send(f ^ u, 1)

    def on_deliver(self, bits):
        if bits:
            self.d = bits[0] ^ self.a

    def reset(self):
        self.d = 0


class LAG_MULTI(LAGD):
    """Two forbidden packets in flight at once (k = 1 and k = 2): beyond a one-bit in-flight model."""

    def on_cue(self, u, f):
        self.a, self.d = u, f
        self.send(f, 1)
        self.send(f, 2)


class EVERY4(EVERY3):
    """STATED LIMIT: leaks on the fourth call only, a tail boundary that is not evaluated (A7)."""

    def reset(self):
        self.calls += 1
        self.chan = []
        if self.calls % 4:
            self.d = 0


# --------------------------------------------------------------------------------------------------------
# Restart cases (T06).

class PKTD_NOQ(PKTD):
    """T06: capture omits the channel (in flight between CUE and PROBE_D every episode)."""

    def capture(self):
        c = PKTD.capture(self)
        c["chan"] = ()
        return c


class HCOUNT(REG):
    """T06: undeclared reset counter that capture omits; the answer is inverted once 2 or more resets happened."""

    def __init__(self):
        REG.__init__(self)
        self.n = 0

    def reset(self):
        REG.reset(self)
        self.n += 1

    def answer(self):
        return self.a if self.n < 2 else 1 - self.a


class KEEPSTALE(REG):
    """Restore that keeps the target's allowed bit when it is already set (fill-if-empty)."""

    def restore(self, c):
        keep = self.a
        REG.restore(self, c)
        if keep:
            self.a = keep


class APPEND(PKTD):
    """Restore that appends the captured channel to what the target already holds."""

    def restore(self, c):
        old = list(self.chan)
        PKTD.restore(self, c)
        self.chan = old + self.chan


class CUE1_BADCAPTURE(REG):
    """Capture wrong straight after the first CUE only (drops d); right at every other point."""

    def capture(self):
        c = REG.capture(self)
        if self.ep == 1 and self._tick == "CUE":
            c["d"] = 0
        return c


class ENDBAD(REG):
    """STATED LIMIT: capture wrong only after the last tick of the life; no output follows it (A7)."""

    def capture(self):
        c = REG.capture(self)
        if self.ep == W.EPISODES and self._tick == "PROBE_D":
            c["a"] = 1 - c["a"]
        return c


# --------------------------------------------------------------------------------------------------------
# Bounds (P0).

class OVERDELAY(REG):
    """Sends (f, 4): outside K = 3."""

    def on_cue(self, u, f):
        self.a, self.d = u, f
        self.send(f, 4)


# --------------------------------------------------------------------------------------------------------
# Observers: obs(runtime, point, h) -> runtime, called after every tick (draft A A5 P7). They write only
# through capture/restore unless the case is about hidden state.

def _flip_d(rt):
    c = rt.capture()
    c["d"] ^= 1
    rt.restore(c)


def NULL(rt, point, h):
    return rt


def BOOKKEEP(rt, point, h):
    """T07 true case: increments the declared BOOKKEEPING log_n."""
    c = rt.capture()
    c["log_n"] += 1
    rt.restore(c)
    return rt


def HEAL(rt, point, h):
    """T07 false case: flips d after CUE, restores the true f after PROBE_D: an output changes, the final
    score does not."""
    _, e, tick = point
    if tick == "CUE":
        _flip_d(rt)
    elif tick == "PROBE_D":
        c = rt.capture()
        c["d"] = W.f_of(h, e)
        rt.restore(c)
    return rt


def STATE_HEAL(rt, point, h):
    """Flips a after PROBE_A; the next CUE overwrites it, so no output changes but the recorded state does."""
    if point[2] == "PROBE_A":
        c = rt.capture()
        c["a"] ^= 1
        rt.restore(c)
    return rt


def LATE(rt, point, h):
    """Disturbs from episode 3 on only."""
    if point[1] >= 3 and point[2] == "CUE":
        _flip_d(rt)
    return rt


RARE_HISTORY = 0b10_01_11_00_11_01


def RARE(rt, point, h):
    """Disturbs one history of 4096 only."""
    if h == RARE_HISTORY and point[1] == 4 and point[2] == "CUE":
        _flip_d(rt)
    return rt


def IMPOSTOR_ONLY(rt, point, h):
    """Disturbs only the no-carry impostor: qualified on REG, not on AMNESIAC."""
    if isinstance(rt, AMNESIAC) and point[2] == "CUE":
        _flip_d(rt)
    return rt


def HIDDEN_WRITE(rt, point, h):
    """Writes an undeclared field (SLEEPER's older) that a later display uses."""
    if point[2] == "PROBE_D" and hasattr(rt, "older"):
        rt.older ^= 1
    return rt


RUNTIMES = {c.__name__: c for c in (
    REG, PKTD, AMNESIAC, FLIP, QCARRY, WIPE, LAGD, EVERY3, SLEEPER, SNEAKY, SPLIT1, SPLIT2, LAG_MULTI, EVERY4,
    PKTD_NOQ, HCOUNT, KEEPSTALE, APPEND, CUE1_BADCAPTURE, ENDBAD, OVERDELAY)}
OBSERVERS = {f.__name__: f for f in (NULL, BOOKKEEP, HEAL, STATE_HEAL, LATE, RARE, IMPOSTOR_ONLY, HIDDEN_WRITE)}

# Draft A A7, IN-MODEL rows: (id, source, runtime, observer, predicate that must FAIL). CALIBRATION rows are
# T012's (world CLOCKED) and are listed for completeness, not run here.
ESCAPES = (
    ("FABLE-G6.reset-sleeper", "harness/rso_harness/meta.py:982", "SLEEPER", None, "ERASE"),
    ("FABLE-G6.reset-every-third", "harness/rso_harness/meta.py:985; closure_reader N27", "EVERY3", None, "ERASE"),
    ("FABLE-G6.restart-hidden-counter", "harness/rso_harness/meta.py:988", "HCOUNT", None, "RESTART"),
    ("FABLE-G6.observer-rare", "harness/rso_harness/meta.py:975", "REG", "RARE", "OBSERVER"),
    ("FABLE-G6.observer-hidden-field", "harness/rso_harness/meta.py:979 (IN half)", "SLEEPER", "HIDDEN_WRITE",
     "OBSERVER"),
    ("FABLE-mutants-C18-Y21-mark", "harness/RECEIPT_mutation_probe.json survived", "LAGD", None, "ERASE"),
    ("FABLE-G8.demand-kept-mark", "harness/rso_harness/meta.py:1013 (IN half)", "LAGD", None, "ERASE"),
    ("FABLE-G8.demand-clock", "harness/rso_harness/meta.py:1007", None, None, "CALIBRATION"),
    ("FABLE-N9-healing", "attack/closure_reader/REPORT.md N9", "REG", "STATE_HEAL", "OBSERVER"),
    ("FABLE-M24-cued-carry", "attack/REPORT_of_the_reader.md M24", "SNEAKY", None, "ERASE"),
    ("FABLE-M25-keep-stale", "attack/REPORT_of_the_reader.md M25", "KEEPSTALE", None, "RESTART"),
    ("FABLE-M25-append", "attack/REPORT_of_the_reader.md M25", "APPEND", None, "RESTART"),
    ("FABLE-2R-T02-T03-cut", "attack/second_reader/REPORT_final.md T02, T03", "CUE1_BADCAPTURE", None, "RESTART"),
    ("FABLE-2R-T04-six-seeds", "attack/second_reader/REPORT_final.md T04", "REG", "LATE", "OBSERVER"),
    ("FABLE-2R-N6-impostor-only", "attack/second_reader/REPORT_final.md N6", "AMNESIAC", "IMPOSTOR_ONLY",
     "OBSERVER"),
    ("ASTRA-one-in-flight-bit", "reference_harness/finite.py:113-118", "LAG_MULTI", None, "ERASE"),
    ("ASTRA-display-only-reset", "reference_harness/test_finite.py:52", "LAGD", None, "ERASE"),
    ("ASTRA-continuation-missing-bit", "reference_harness/test_finite.py:45", "PKTD_NOQ", None, "RESTART"),
    ("ASTRA-interacting-leaks-1", "HARDENED_TEST_PLAN_v0.3.md s4", "SPLIT1", None, "ERASE"),
    ("ASTRA-interacting-leaks-2", "HARDENED_TEST_PLAN_v0.3.md s4", "SPLIT2", None, "ERASE"),
    ("CADMUS-forbidden-channel-carry", "draft A A7 (found while drafting)", "QCARRY", None, "CHANNEL"),
)

# Draft A A7 OUT-OF-MODEL faults the registered model passes by construction: (id, runtime, predicate, why).
STATED_LIMITS = (
    ("LEAK-ON-CALL-4", "EVERY4", "ERASE", "leak first appears at reset call 4, a tail boundary"),
    ("END-ONLY-CAPTURE", "ENDBAD", "RESTART", "no output follows the last tick inside the life"),
)
