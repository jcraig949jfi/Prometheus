"""Tiny numpy engines that implement explib.lockstep.LockstepEngine. They are the core's known-answer
fixtures (and worked examples of the protocol); none of them is PTE, but each reproduces the STRUCTURE of a
PTE failure (mirror pairs that share all exogenous draws, an actuator that is not the sensor, an unused store
written by the input, a nonlocal leak that breaks locality).

ToyRing: U units (mirror pairs 2p, 2p+1 share their noise seed and see negated cues), N nodes on a ring.
  state   s [U,N]  the scored register (readout = sign(s[:, ro]))
          aux [U,N] a store written from the input and by noise, NEVER read by anything (the W-Y Kp[0] case)
  mail    ring buffer [D,U,N] of summed integer content; a packet emitted at t arrives at t + delay
  modes   'latch'  the sensor keeps sign(input); no traffic
          'relay'  every node adopts sign(input) else sign(arrival); a node whose s changed emits s to n+1
          'loop'   inputs are emitted, never stored; nodes adopt arrivals and forward them (the bit returns to
                   the sensor after N*delay ticks: comm-dependent HOLD)
          'null'   nothing is ever written to s (init_const=True: s starts at a nonzero constant per node,
                   identical in mirror partners)
          'invert' like relay but adopts the NEGATED arrival at non-sensor nodes
  controls zero_comm (nothing is delivered; emission still happens), leak (BUG: aux reads a global sum of s),
           state_rng (BUG: the noise draw depends on the state, breaking common random numbers)
"""
from __future__ import annotations

import dataclasses

import numpy as np


def _noise(seed: np.ndarray, t: int, N: int) -> np.ndarray:
    """State-independent CRN draw in {-1,0,1}, a hash of (seed, t, node)."""
    n = np.arange(N, dtype=np.uint64)[None, :]
    x = (seed.astype(np.uint64)[:, None] * np.uint64(0x9E3779B1) + np.uint64(t) * np.uint64(0x85EBCA77)
         + n * np.uint64(0xC2B2AE3D)) & np.uint64(0xFFFFFFFF)
    x ^= x >> np.uint64(15)
    x = (x * np.uint64(0x2C1B3C6D)) & np.uint64(0xFFFFFFFF)
    x ^= x >> np.uint64(12)
    return (x % np.uint64(3)).astype(np.int64) - 1


@dataclasses.dataclass
class ToyWorld:
    s: np.ndarray
    aux: np.ndarray
    mail: np.ndarray
    sched: np.ndarray
    last_em: np.ndarray


class ToyRing:
    def __init__(self, U=8, N=6, T=24, mode="relay", delay=2, sensor=0, ro=None, t_cue=2, cue_len=1,
                 zero_comm=False, leak=False, state_rng=False, cue_twin=False, seed0=11, mirrored=True,
                 init_const=False):
        assert U % 2 == 0
        self.n_units, self.n_nodes, self.T = U, N, T
        self.mode, self.delay, self.sensor = mode, delay, sensor
        self.ro = sensor if ro is None else ro
        self.t_cue, self.cue_len = t_cue, cue_len
        self.zero_comm, self.leak, self.state_rng, self.cue_twin = zero_comm, leak, state_rng, cue_twin
        self.D = delay + 1
        rng = np.random.default_rng(seed0)
        base = rng.integers(1, 2 ** 31, size=U)
        self.seeds = np.array([base[u - (u % 2)] for u in range(U)], dtype=np.int64) if mirrored else base
        pair_sign = rng.choice([-1, 1], size=U // 2)
        self.y = np.empty(U, np.int64)                      # target = cue sign; partner negated
        self.y[0::2] = pair_sign
        self.y[1::2] = -pair_sign if mirrored else rng.choice([-1, 1], size=U // 2)
        self.arms_identical = not cue_twin
        self.init_const = init_const

    # ------------------------------------------------------------ protocol
    def _schedule(self, arm: str) -> np.ndarray:
        sch = np.zeros((self.T, self.n_units, self.n_nodes), np.int64)
        sch[self.t_cue:self.t_cue + self.cue_len, :, self.sensor] = 4 * self.y[None, :]
        if arm == "B" and self.cue_twin:
            sch[self.t_cue:self.t_cue + self.cue_len] *= -1
        return sch

    def make(self, arm: str) -> ToyWorld:
        U, N = self.n_units, self.n_nodes
        s0 = _noise(self.seeds, 10 ** 6, N) * 2 + 1 if self.init_const else np.zeros((U, N), np.int64)
        s0 = np.where(s0 == 0, 1, s0)
        return ToyWorld(s0.astype(np.int64), np.zeros((U, N), np.int64),
                        np.zeros((self.D, U, N), np.int64), self._schedule(arm), np.zeros((U, N), np.int64))

    def inputs(self, w: ToyWorld, t: int) -> np.ndarray:
        return w.sched[t]

    def arrivals(self, w: ToyWorld, t: int) -> np.ndarray:
        a = w.mail[t % self.D]
        return np.zeros_like(a) if self.zero_comm else a

    def inflight(self, w: ToyWorld, t: int) -> np.ndarray:
        return np.stack([w.mail[(t + 1 + h) % self.D] for h in range(self.D - 1)])

    def step(self, w: ToyWorld, t: int) -> None:
        slot = t % self.D
        a = w.mail[slot].copy()
        w.mail[slot] = 0
        if self.zero_comm:
            a[:] = 0
        inp = w.sched[t]
        old = w.s.copy()
        sens = np.zeros(self.n_nodes, bool)
        sens[self.sensor] = True
        em = np.zeros_like(w.s)
        if self.mode == "latch":
            w.s = np.where(inp != 0, np.sign(inp), w.s)
        elif self.mode in ("relay", "invert"):
            adopt = np.sign(a) if self.mode == "relay" else np.where(sens[None, :], np.sign(a), -np.sign(a))
            w.s = np.where(inp != 0, np.sign(inp), np.where(a != 0, adopt, w.s))
            em = np.where(w.s != old, w.s, 0)
        elif self.mode == "loop":
            w.s = np.where(a != 0, np.sign(a), w.s)
            em = np.where(inp != 0, np.sign(inp), np.where(w.s != old, w.s, 0))
        elif self.mode == "null":
            pass
        else:
            raise ValueError(self.mode)
        nz = _noise(self.seeds, t, self.n_nodes)
        if self.state_rng:                                  # BUG fixture: draw depends on state
            nz = _noise(self.seeds + (w.s.sum(1) > 0), t, self.n_nodes)
        w.aux = w.aux + inp + nz
        if self.leak:                                       # BUG fixture: nonlocal read
            w.aux = w.aux + (w.s.sum(1, keepdims=True) > 0)
        w.last_em = em
        w.mail[(t + self.delay) % self.D] += np.roll(em, 1, axis=1)

    def trace(self, w: ToyWorld) -> dict:
        return {"s": w.s, "aux": w.aux}

    def edges(self, wa: ToyWorld, wb: ToyWorld, t: int):
        if self.zero_comm:
            return []
        d = wa.last_em != wb.last_em
        out = []
        for u, n in zip(*np.nonzero(d)):
            out.append((int(u), int(n), t, int((n + 1) % self.n_nodes), t + self.delay))
        return out

    def intervene(self, w: ToyWorld, target, t: int) -> None:
        kind, node = target if isinstance(target, tuple) else (target, None)
        if kind == "flip_s":
            w.s[:, node] = -w.s[:, node]
        elif kind == "add_aux":
            w.aux[:, node] += 7
        elif kind == "flip_s_except":
            m = np.ones(self.n_nodes, bool)
            m[node] = False
            w.s[:, m] = -w.s[:, m] + 3
        elif kind == "flush":
            w.mail[:] = 0
        elif kind == "swap_partner_s":
            p = np.arange(self.n_units) ^ 1
            w.s[:] = w.s[p]
        elif kind == "swap_site":                          # every node array, between mirror partners
            p = np.arange(self.n_units) ^ 1
            w.s[:] = w.s[p]
            w.aux[:] = w.aux[p]
        elif kind == "swap_chan":                          # every in-flight packet, between mirror partners
            p = np.arange(self.n_units) ^ 1
            w.mail[:] = w.mail[:, p]
        elif kind == "noop":
            pass
        else:
            raise ValueError(kind)

    def readout(self, w: ToyWorld, t: int) -> np.ndarray:
        return w.s[:, self.ro].copy()

    # ------------------------------------------------------------ scoring helpers
    def run_scores(self, t_read: int, ctrl=None) -> np.ndarray:
        """Per-unit score (1 correct, 0 wrong, .5 tie) of sign(s[ro]) at t_read against y."""
        w = self.make("A")
        for t in range(t_read + 1):
            self.step(w, t)
        return unit_scores(w.s[:, self.ro], self.y)


def unit_scores(readout: np.ndarray, y: np.ndarray) -> np.ndarray:
    s = np.sign(np.asarray(readout))
    return np.where(s == 0, 0.5, (s == np.sign(y)).astype(float))


def pair_means(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, float)
    return x.reshape(-1, 2).mean(-1)
