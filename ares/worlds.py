"""Ares toy worlds W1-W12, batched over a population.

Interface: w = World(mode, T); w.reset(rng) draws the episode schedule
(common random numbers: every organism in the batch meets the same
episode); obs = w.first_obs(P); obs, r, alive, info = w.step(actions).
Observations are (P, OBS_DIM): ch0-ch3 world-specific, ch4 = t/T clock,
ch5 = 1.0 constant. Rewards are (P,). `alive` is (P,) bool (only W12
kills). `info` holds the hidden schedule for later conditional analysis;
it is never shown to the organism.

mode is one of "present" (the pressure), "absent" (the pressure's
defining feature neutralised), "shuffled" (the feature present but
decoupled from anything observable). Nothing in a world names or
rewards a mechanism.
"""
from __future__ import annotations

import numpy as np

from .substrate import OBS_DIM

MODES = ("present", "absent", "shuffled")


def _markov(rng, T, p_on, p_off):
    x = np.zeros(T, dtype=np.int8)
    s = 0
    for t in range(T):
        if s == 0 and rng.random() < p_on:
            s = 1
        elif s == 1 and rng.random() < p_off:
            s = 0
        x[t] = s
    return x


class World:
    name = "base"
    T = 60
    chance_actions = (0, 1, 2)   # actions a fixed policy may hold

    def __init__(self, mode="present", T=None):
        assert mode in MODES, mode
        self.mode = mode
        if T is not None:
            self.T = int(T)
        self.t = 0
        self.P = 0

    def reset(self, rng, P):
        self.t = 0
        self.P = P
        self.last_r = np.zeros(P, dtype=np.float32)
        self.last_a = np.zeros(P, dtype=np.int64)
        self._draw(rng)
        return self._obs()

    def _base_obs(self):
        o = np.zeros((self.P, OBS_DIM), dtype=np.float32)
        o[:, 4] = self.t / self.T
        o[:, 5] = 1.0
        return o

    def _draw(self, rng):
        raise NotImplementedError

    def _obs(self):
        raise NotImplementedError

    def step(self, a):
        r, alive, info = self._step(a)
        self.last_r = r.astype(np.float32)
        self.last_a = a
        self.t += 1
        obs = self._obs() if self.t < self.T else self._base_obs()
        return obs, r, alive, info


# ----------------------------------------------------------------------
class W1CatastrophicTail(World):
    """Most errors cost 1; acting during a weakly cued danger wipes 90%
    of accumulated reward. No detector: the cue is just channel 1."""
    name = "W1"
    T = 60

    def _draw(self, rng):
        T = self.T
        self.s = rng.choice([-1.0, 1.0], size=T)
        self.s_obs = self.s + rng.normal(0, 0.5, size=T)
        self.d = _markov(rng, T, 0.03, 0.35)
        self.cue = self.d + rng.normal(0, 0.6, size=T)
        self.d_cat = _markov(rng, T, 0.03, 0.35) if self.mode == "shuffled" else self.d
        self.acc = np.zeros(self.P, dtype=np.float32)

    def _obs(self):
        o = self._base_obs(); t = self.t
        o[:, 0] = self.s_obs[t]; o[:, 1] = self.cue[t]; o[:, 2] = np.clip(self.last_r, -5, 5) / 5
        return o

    def _step(self, a):
        t = self.t
        act = (a == 1)
        r = np.where(act, 1.0 if self.s[t] > 0 else -1.0, 0.0).astype(np.float32)
        if self.d_cat[t] == 1:
            if self.mode == "absent":
                r = np.where(act, -3.0, r)
            else:
                r = np.where(act, -0.9 * np.maximum(self.acc, 0) - 5.0, r)
        self.acc += r
        return r, np.ones(self.P, bool), dict(danger=int(self.d[t]), cat=int(self.d_cat[t]))


class W2RareOverride(World):
    """Safe +1; risky -3 except inside rare cued windows where it pays +60."""
    name = "W2"
    T = 60

    def _draw(self, rng):
        T = self.T
        self.w = _markov(rng, T, 0.02, 0.5)
        w_cue = _markov(rng, T, 0.02, 0.5) if self.mode == "shuffled" else self.w
        self.cue = w_cue + rng.normal(0, 0.5, size=T)
        self.noise = rng.normal(0, 1.0, size=T)

    def _obs(self):
        o = self._base_obs(); t = self.t
        o[:, 0] = self.noise[t]; o[:, 1] = self.cue[t]; o[:, 2] = np.clip(self.last_r, -10, 60) / 10
        return o

    def _step(self, a):
        t = self.t
        risky = (a == 1)
        pay = 60.0 if (self.w[t] == 1 and self.mode != "absent") else -3.0
        r = np.where(risky, pay, 1.0).astype(np.float32)
        return r, np.ones(self.P, bool), dict(window=int(self.w[t]))


class W3ChangingRules(World):
    """Act on the sign of a noisy channel; the mapping reverses once at a
    random step. Last reward and last action are visible."""
    name = "W3"
    T = 60

    def _draw(self, rng):
        T = self.T
        self.x = rng.choice([-1.0, 1.0], size=T)
        self.x_obs = self.x + rng.normal(0, 0.3, size=T)
        if self.mode == "present":
            f = rng.integers(15, 46)
            self.sign = np.where(np.arange(T) < f, 1.0, -1.0)
            self.flip = int(f)
        elif self.mode == "absent":
            self.sign = np.ones(T); self.flip = -1
        else:
            self.sign = rng.choice([-1.0, 1.0], size=T); self.flip = -2

    def _obs(self):
        o = self._base_obs(); t = self.t
        o[:, 0] = self.x_obs[t]; o[:, 2] = self.last_r
        o[:, 3] = (self.last_a == 1).astype(np.float32) - (self.last_a == 2).astype(np.float32)
        return o

    def _step(self, a):
        t = self.t
        correct = 1 if self.x[t] * self.sign[t] > 0 else 2
        r = np.where(a == correct, 1.0, np.where(a == 0, 0.0, -1.0)).astype(np.float32)
        return r, np.ones(self.P, bool), dict(sign=float(self.sign[t]), flip=self.flip, correct=correct)


class W4HiddenRegime(World):
    """Regime bit shown for the first 3 steps only; no reward channel;
    +1 for the regime's action, -1 for the other, 0 for abstain."""
    name = "W4"
    T = 40

    def _draw(self, rng):
        T = self.T
        self.r = int(rng.integers(0, 2))
        shown = int(rng.integers(0, 2)) if self.mode == "shuffled" else self.r
        self.cue = rng.normal(0, 0.3, size=T)
        k = T if self.mode == "absent" else 3
        self.cue[:k] = (2 * shown - 1) + rng.normal(0, 0.2, size=k)
        self.noise = rng.normal(0, 1.0, size=T)

    def _obs(self):
        o = self._base_obs(); t = self.t
        o[:, 0] = self.noise[t]; o[:, 1] = self.cue[t]
        return o

    def balance_key(self):
        return (self.r,)

    def _step(self, a):
        good = self.r + 1
        r = np.where(a == good, 1.0, np.where(a == 0, 0.0, -1.0)).astype(np.float32)
        return r, np.ones(self.P, bool), dict(regime=self.r)


class W5DelayedRevelation(World):
    """Token at step 2 decides which action pays +50 at step T-2; the
    same channel carries distractor noise in between; timing pulses on
    ch1 (token step) and ch2 (decision step) are environmental."""
    name = "W5"
    T = 30
    TOK = 2

    def _draw(self, rng):
        T = self.T
        self.token = float(rng.choice([-1.0, 1.0]))
        self.pay = self.token if self.mode != "shuffled" else float(rng.choice([-1.0, 1.0]))
        self.ch0 = rng.uniform(-0.8, 0.8, size=T)
        self.ch0[self.TOK] = self.token
        if self.mode == "absent":
            self.ch0[T - 2] = self.pay
        self.dec = T - 2

    def balance_key(self):
        # both hidden binaries: the token shown and the side that pays
        # (identical in present/absent; independent in shuffled)
        return (int(self.token > 0), int(self.pay > 0))

    def _obs(self):
        o = self._base_obs(); t = self.t
        o[:, 0] = self.ch0[t]; o[:, 1] = 1.0 if t == self.TOK else 0.0; o[:, 2] = 1.0 if t == self.dec else 0.0
        return o

    def _step(self, a):
        if self.t == self.dec:
            good = 1 if self.pay > 0 else 2
            r = np.where(a == good, 50.0, np.where(a == 0, 0.0, -50.0)).astype(np.float32)
        else:
            r = np.zeros(self.P, dtype=np.float32)
        return r, np.ones(self.P, bool), dict(token=self.token, pay=self.pay)


class W7IncompatibleRegimes(World):
    """Blocks of 15 steps alternate: regime A pays +2 for hitting a
    rotating option; regime B pays +1 for option 0 and -5 for anything
    else. No regime bit; obs = last reward and last action."""
    name = "W7"
    T = 60
    BLOCK = 15

    def _draw(self, rng):
        T = self.T
        start = int(rng.integers(0, 2))
        blocks = ((np.arange(T) // self.BLOCK) + start) % 2
        if self.mode == "present":
            self.regime = blocks
        elif self.mode == "absent":
            self.regime = np.zeros(T, dtype=np.int64)
        else:
            self.regime = rng.integers(0, 2, size=T)
        self.off = int(rng.integers(0, 3))

    def _obs(self):
        o = self._base_obs()
        o[:, 0] = self.last_r / 5.0
        o[:, 1] = (self.last_a == 0); o[:, 2] = (self.last_a == 1); o[:, 3] = (self.last_a == 2)
        return o

    def _step(self, a):
        t = self.t
        if self.regime[t] == 0:
            p = (t // 3 + self.off) % 3
            r = np.where(a == p, 2.0, 0.0)
        else:
            r = np.where(a == 0, 1.0, -5.0)
        return r.astype(np.float32), np.ones(self.P, bool), dict(regime=int(self.regime[t]))


class W11IrreversibleCommitment(World):
    """Probe (-0.1) reveals noisy evidence; committing to A or B is
    permanent and pays +2/-2 per remaining step by correctness. absent:
    the choice is reversible every step. shuffled: evidence is noise."""
    name = "W11"
    T = 30

    def _draw(self, rng):
        T = self.T
        self.truth = float(rng.choice([-1.0, 1.0]))
        mean = 0.4 * self.truth if self.mode != "shuffled" else 0.0
        self.ev = mean + rng.normal(0, 1.0, size=T)
        self.committed = np.zeros(self.P, dtype=np.int64)   # 0 none, 1 A, 2 B

    def balance_key(self):
        return (int(self.truth > 0),)

    def _obs(self):
        o = self._base_obs(); t = self.t
        o[:, 0] = np.where(self.committed == 0, self.ev[t], 0.0)
        o[:, 1] = (self.committed != 0).astype(np.float32)
        o[:, 2] = self.last_r / 2.0
        return o

    def _step(self, a):
        good = 1 if self.truth > 0 else 2
        if self.mode == "absent":
            r = np.where(a == 0, -0.1, np.where(a == good, 2.0, -2.0))
            return r.astype(np.float32), np.ones(self.P, bool), dict(truth=self.truth)
        newly = (self.committed == 0) & (a != 0)
        self.committed = np.where(newly, a, self.committed)
        r = np.where(self.committed == 0, -0.1, np.where(self.committed == good, 2.0, -2.0))
        return r.astype(np.float32), np.ones(self.P, bool), dict(truth=self.truth)


class W12DyingLineage(World):
    """Energy declines 1/step; safe +0.6 cannot keep up; risky 30% +6 /
    70% -2; death at 0; +1 per step alive. absent: safe +1.2. shuffled:
    the energy channel is noise."""
    name = "W12"
    T = 80
    E0 = 8.0

    def _draw(self, rng):
        self.roll = rng.random(self.T) < 0.3
        self.noise = rng.normal(0, 0.3, size=self.T)
        self.E = np.full(self.P, self.E0, dtype=np.float32)
        self.alive = np.ones(self.P, dtype=bool)

    def _obs(self):
        o = self._base_obs(); t = self.t
        o[:, 0] = (self.E / 10.0) if self.mode != "shuffled" else self.noise[t] + 0.5
        o[:, 2] = self.last_r
        return o

    def _step(self, a):
        t = self.t
        risky = (a == 1)
        safe_gain = 1.2 if self.mode == "absent" else 0.6
        gain = np.where(risky, 6.0 if self.roll[t] else -2.0, safe_gain)
        E_before = self.E.copy()
        self.E = np.where(self.alive, self.E + gain - 1.0, self.E)
        self.alive = self.alive & (self.E > 0)
        r = self.alive.astype(np.float32)
        return r, self.alive.copy(), dict(energy=E_before, risky=risky.copy())


class W9MatchingPennies:
    """Two-sided world: A wins on match, B on mismatch. Each side sees
    the opponent's last two choices and its own. present: both sides
    are evolving populations (coupled); absent: B is i.i.d. 50/50;
    shuffled: B is the fixed pattern 1,1,2. Choices: 1 or 2 (0 -> 1)."""
    name = "W9"
    T = 40

    def __init__(self, mode="present", T=None):
        self.mode = mode
        if T is not None:
            self.T = int(T)

    def reset(self, rng, P):
        self.t = 0; self.P = P
        self.histA = np.zeros((P, 2), dtype=np.float32)
        self.histB = np.zeros((P, 2), dtype=np.float32)
        self.iid = rng.choice([1, 2], size=self.T)
        return self._obs(self.histB, self.histA), self._obs(self.histA, self.histB)

    def _obs(self, opp, own):
        o = np.zeros((self.P, OBS_DIM), dtype=np.float32)
        o[:, 0:2] = opp; o[:, 2:4] = own; o[:, 4] = self.t / self.T; o[:, 5] = 1.0
        return o

    def static_b(self):
        if self.mode == "absent":
            return np.full(self.P, self.iid[self.t])
        if self.mode == "shuffled":
            return np.full(self.P, [1, 1, 2][self.t % 3])
        return None

    def step(self, aA, aB):
        aA = np.where(aA == 0, 1, aA); aB = np.where(aB == 0, 1, aB)
        match = (aA == aB)
        rA = np.where(match, 1.0, -1.0).astype(np.float32)
        rB = -rA
        self.histA = np.stack([self.histA[:, 1], 2.0 * aA - 3.0], axis=1)
        self.histB = np.stack([self.histB[:, 1], 2.0 * aB - 3.0], axis=1)
        self.t += 1
        return self._obs(self.histB, self.histA), self._obs(self.histA, self.histB), rA, rB


class W13CarrierStress(World):
    """W4 + W5 combined, cycle-1 carrier stress test ONLY (operator
    directive 2026-09-21 item 4). Regime cue on ch1 for steps 0-2; then
    ch1 carries distractor noise (sd 1.0, louder than W4's 0.3) for
    steps 3-59; reward exists ONLY in steps 60-79 (+1/-1 for the regime
    action, 0 abstain). No reward channel. absent: cue every step.
    shuffled: early cue independent of the regime."""
    name = "W13"
    T = 80
    CUE = 3
    PAY_FROM = 60

    def _draw(self, rng):
        T = self.T
        self.r = int(rng.integers(0, 2))
        shown = int(rng.integers(0, 2)) if self.mode == "shuffled" else self.r
        self.cue = rng.normal(0, 1.0, size=T)
        k = T if self.mode == "absent" else self.CUE
        self.cue[:k] = (2 * shown - 1) + rng.normal(0, 0.2, size=k)
        self.noise = rng.normal(0, 1.0, size=T)

    def balance_key(self):
        return (self.r,)

    def _obs(self):
        o = self._base_obs(); t = self.t
        o[:, 0] = self.noise[t]; o[:, 1] = self.cue[t]
        return o

    def _step(self, a):
        if self.t < self.PAY_FROM:
            return np.zeros(self.P, dtype=np.float32), np.ones(self.P, bool), dict(regime=self.r)
        good = self.r + 1
        r = np.where(a == good, 1.0, np.where(a == 0, 0.0, -1.0)).astype(np.float32)
        return r, np.ones(self.P, bool), dict(regime=self.r)


WORLDS = {
    "W13": W13CarrierStress,
    "W1": W1CatastrophicTail, "W2": W2RareOverride, "W3": W3ChangingRules,
    "W4": W4HiddenRegime, "W5": W5DelayedRevelation, "W7": W7IncompatibleRegimes,
    "W11": W11IrreversibleCommitment, "W12": W12DyingLineage,
}
# W6 (scarcity) = W3 under a scarce substrate config; W8 (transplant) is
# a sweep protocol; W9 is two-sided (above); W10 (development) is a
# genome encoding (ares/develop.py). All are wired in ares/sweep.py.
