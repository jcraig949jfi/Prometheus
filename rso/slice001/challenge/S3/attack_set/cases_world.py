"""C-004-T030 S3 attack set: fresh world-plane runtimes and observers (attack tooling, never production code).

Written by Pallas[m2-e7da6bde] BEFORE any S2 test body was opened and before any of this was executed.
Every class realises rso.slice001.world.Runtime; nothing under rso/slice001/ outside challenge/S3/ is changed.
Expected verdicts and their derivations are in ATTACK_SET.md and expected.json, not here.

Scored cases:  S3_LATCH, S3_BEACON (sound); observer S3_MIGRATE on REG (sound);
               S3_INVERT, S3_SHADOW, S3_LOGDEP + BOOKKEEP (broken).
Witness-only:  S3_LAG3_EP3, S3_RELAY, S3_RESETCUT, observer S3_DFLIP (behavioural witnesses for edits E01-E04).
"""
from rso.slice001 import world as W
from rso.slice001.fixtures import world_cases as WC


# ---------------------------------------------------------------------------------------------- sound

class S3_LATCH(W.Runtime):
    """The cue writes only an undeclared latch g (captured and restored as an extra key); the reset copies
    g into the allowed component a, clears d and the channel. After every reset a = u of the episode before."""

    def __init__(self):
        W.Runtime.__init__(self)
        self.g = 0

    def on_cue(self, u, f):
        self.g, self.d = u, f

    def reset(self):
        self.a = self.g
        self.d = 0
        self.chan = []

    def capture(self):
        c = W.Runtime.capture(self)
        c["g"] = self.g
        return c

    def restore(self, c):
        W.Runtime.restore(self, c)
        self.g = c["g"]


class S3_BEACON(WC.REG):
    """REG plus a constant packet (1, 2) sent at every CUE; the reset clears d and KEEPS the channel. The
    FORBIDDEN channel is non-empty across every boundary but carries a constant: no history content."""

    def on_cue(self, u, f):
        self.a, self.d = u, f
        self.send(1, 2)

    def reset(self):
        self.d = 0


def S3_MIGRATE(rt, point, h):
    """Observer: after every tick, capture, restore into a NEW instance of the same class, continue with it."""
    n = type(rt)()
    n.restore(rt.capture())
    return n


# ---------------------------------------------------------------------------------------------- broken

class S3_INVERT(W.Runtime):
    """The reset complements a and sets an undeclared, uncaptured flag; the answer un-complements while the
    flag is set. Answers u_j correctly in every trial; the state after a reset is not in the capture."""

    def __init__(self):
        W.Runtime.__init__(self)
        self.flipped = False

    def on_cue(self, u, f):
        self.a, self.d, self.flipped = u, f, False

    def answer(self):
        return self.a ^ 1 if self.flipped else self.a

    def reset(self):
        self.a ^= 1
        self.flipped = True
        self.d = 0
        self.chan = []


class S3_SHADOW(WC.REG):
    """a is written but never read: the answer comes from an undeclared register g that IS captured and
    restored (extra key). Complete capture, right answers, and the declared allowed channel is a decoy."""

    def __init__(self):
        WC.REG.__init__(self)
        self.g = 0

    def on_cue(self, u, f):
        self.a, self.d, self.g = u, f, u

    def answer(self):
        return self.g

    def capture(self):
        c = WC.REG.capture(self)
        c["g"] = self.g
        return c

    def restore(self, c):
        WC.REG.restore(self, c)
        self.g = c["g"]


class S3_LOGDEP(WC.REG):
    """REG whose answer also reads the component it DECLARES as BOOKKEEPING (log_n parity). Identical to REG
    while log_n stays 0; an observer that only increments log_n changes its answers."""

    def answer(self):
        return self.a ^ (self.log_n & 1)


# ---------------------------------------------------------------------------------------------- witnesses

class S3_LAG3_EP3(WC.REG):
    """Forbidden f of episode 3 sent with k = 3 (episode 3 only); the reset clears d and keeps the channel.
    The only leak is f_3 at PROBE_A of episode 6: lag exactly H = 3 after boundary 3."""

    def on_cue(self, u, f):
        self.a, self.d = u, f
        if self.ep == 3:
            self.send(f, 3)

    def reset(self):
        self.d = 0


class S3_RELAY(WC.REG):
    """Undeclared pf = f of the previous episode survives the reset and is SENT (pf, 3) at the next CUE;
    deliveries are ignored and the reset flushes the channel. The leak is visible only in the CUE output."""

    def __init__(self):
        WC.REG.__init__(self)
        self.pf = 0

    def on_cue(self, u, f):
        self.a, self.d = u, f
        self.send(self.pf, 3)
        self.pf = f

    def on_deliver(self, bits):
        pass


class S3_RESETCUT(WC.REG):
    """capture() reports a complemented exactly when it is called right after a reset and before the next
    tick; right at every after-tick point."""

    def __init__(self):
        WC.REG.__init__(self)
        self.just_reset = False

    def step(self, tick, obs=None):
        self.just_reset = False
        return WC.REG.step(self, tick, obs)

    def reset(self):
        WC.REG.reset(self)
        self.just_reset = True

    def capture(self):
        c = WC.REG.capture(self)
        if self.just_reset:
            c["a"] = 1 - c["a"]
        return c


def S3_DFLIP(rt, point, h):
    """Observer: flips the FORBIDDEN display d after every PROBE_D. On REG the next reset clears d before any
    output reads it, so no output changes; the declared state captured after the action does."""
    if point[2] == "PROBE_D":
        c = rt.capture()
        c["d"] ^= 1
        rt.restore(c)
    return rt


RUNTIMES = {c.__name__: c for c in (S3_LATCH, S3_BEACON, S3_INVERT, S3_SHADOW, S3_LOGDEP, S3_LAG3_EP3, S3_RELAY,
                                    S3_RESETCUT)}
OBSERVERS = {f.__name__: f for f in (S3_MIGRATE, S3_DFLIP)}
