"""Environment families (DESIGN.md s7): sparse sense schedules + scoring.

Every family builds, per world, a list of trials with a readout tick,
an actuator site and a target y in {-1,+1}. Targets are i.i.d. fair
coins and worlds come in MIRROR PAIRS (b even, b+1): the pair shares
positions and draws, and world b+1's target sequence is the exact
negation of world b's. Averaged over a pair, every constant policy scores
exactly 0.5 and no sequential structure exists to exploit. (An earlier
draft balanced targets exactly within blocks by sampling without
replacement; that made consecutive targets anti-correlated, P(same)=1/3
in 4-trial blocks, so "answer the opposite of last time" beat chance
without adaptation. Caught by the plant probe before any search;
calibration ledger 2026-09-24.)
Positions are drawn per world from the ENV stream, so a homogeneous
program cannot memorise where its actuator is: success requires a
position-free mechanism (spread, latch, relay, ...).

Environment randomness is pre-drawn on the host from
numpy.default_rng(H(ws, ENV, family_id, variant)) -- deterministic in
the world seed, independent of every physics stream.
"""
from __future__ import annotations

import dataclasses

import numpy as np
import torch

from . import rng
from .engine import Schedule
from .physics import Physics
from . import topology

FAMILIES = ("RELAY", "XOR", "MAJ", "FLIP", "HOLD")
FAMILY_ID = {f: i + 1 for i, f in enumerate(FAMILIES)}


@dataclasses.dataclass(frozen=True)
class EnvSpec:
    family: str = "RELAY"
    d: int = 3              # spatial scale (env distance)
    delta: int = 8          # ticks from cue onset to readout (RELAY/XOR/MAJ/FLIP)
    gap: int = 8            # HOLD: distractor ticks between cue and readout
    cue_len: int = 2
    amp: int = 256
    amp_teacher: int = 128  # FLIP teacher amplitude (distinguishable from cue)
    amp_dist: int = 64      # HOLD distractor amplitude
    trials: int = 16        # even
    block: int = 4          # FLIP: trials per mapping block (even, divides trials)
    flip_p: float = 0.3     # MAJ: per-sensor flip probability
    n_maj: int = 5
    iti: int = 2            # idle ticks after each readout
    variant: int = 0        # held-out variants use a different value

    def period(self) -> int:
        if self.family == "HOLD":
            return self.cue_len + self.gap + 1 + self.iti
        if self.family == "FLIP":
            return self.delta + 1 + self.cue_len + self.iti
        return self.delta + 1 + self.iti

    def T(self) -> int:
        return self.trials * self.period()

    def to_dict(self):
        return dataclasses.asdict(self)


# ---------------------------------------------------------------- distances
_DIST_CACHE: dict = {}


def dist_matrix(ph: Physics) -> np.ndarray:
    """Env distance: geometric (toroidal Manhattan / circular) on
    torus/ring, BFS hops on graphs, 1 for global."""
    key = (ph.topology, ph.n_sites, ph.radius, ph.k_random, ph.rewire, ph.topo_seed)
    if key in _DIST_CACHE:
        return _DIST_CACHE[key]
    N = ph.n_sites
    if ph.topology == "torus":
        s = ph.side
        y, x = np.divmod(np.arange(N), s)
        dx = np.abs(x[:, None] - x[None, :])
        dy = np.abs(y[:, None] - y[None, :])
        M = np.minimum(dx, s - dx) + np.minimum(dy, s - dy)
    elif ph.topology == "ring":
        i = np.arange(N)
        dd = np.abs(i[:, None] - i[None, :])
        M = np.minimum(dd, N - dd)
    elif ph.topology == "global":
        M = 1 - np.eye(N, dtype=np.int64)
    else:
        M = np.stack([topology.graph_distances(ph, s) for s in range(N)])
        M = np.where(M < 0, 10 ** 6, M)
    _DIST_CACHE[key] = M.astype(np.int64)
    return _DIST_CACHE[key]


def _pick_at(g, Mrow: np.ndarray, d: int, exclude=()) -> int:
    """A site at distance exactly d if any, else the farthest reachable <= d."""
    cand = np.flatnonzero(Mrow == d)
    cand = np.setdiff1d(cand, np.asarray(exclude, dtype=np.int64))
    if cand.size == 0:
        ok = np.flatnonzero((Mrow <= d) & (Mrow > 0))
        ok = np.setdiff1d(ok, np.asarray(exclude, dtype=np.int64))
        if ok.size:
            best = Mrow[ok].max()
            cand = ok[Mrow[ok] == best]
        else:
            # nothing reachable within d (sparse directed graphs): any other
            # site, nearest first
            ok = np.setdiff1d(np.flatnonzero(Mrow > 0), np.asarray(exclude, dtype=np.int64))
            if ok.size == 0:
                ok = np.setdiff1d(np.arange(Mrow.size), np.asarray(exclude, dtype=np.int64))
            best = Mrow[ok].min()
            cand = ok[Mrow[ok] == best]
    return int(cand[g.integers(cand.size)])


def _coin(g, n: int) -> np.ndarray:
    return np.where(g.random(n) < 0.5, 1, -1)


@dataclasses.dataclass
class Episode:
    schedule: Schedule
    ro_tick: np.ndarray     # [B, trials]
    ro_slot: np.ndarray     # [B, trials] index into schedule.read_idx columns
    y: np.ndarray           # [B, trials]
    scored: np.ndarray      # [B, trials] bool
    meta: dict


def build(ph: Physics, env: EnvSpec, world_seeds) -> Episode:
    B = len(world_seeds)
    M = dist_matrix(ph)
    N = ph.n_sites
    T = env.T()
    tr = env.trials
    assert tr % 2 == 0
    fam = env.family
    K = {"RELAY": 1, "XOR": 2, "MAJ": env.n_maj, "FLIP": 2, "HOLD": 1}[fam]
    sidx = np.zeros((B, K), dtype=np.int64)
    sval = np.zeros((T, B, K), dtype=np.int32)
    ridx = np.zeros((B, 1), dtype=np.int64)
    ro_tick = np.zeros((B, tr), dtype=np.int64)
    y = np.zeros((B, tr), dtype=np.int64)
    scored = np.ones((B, tr), dtype=bool)
    Pd = env.period()
    assert B % 2 == 0, "worlds come in mirror pairs"
    for b, ws in enumerate(world_seeds):
        lead = int(world_seeds[b - (b % 2)])
        sg = -1 if b % 2 else 1          # mirror sign
        g = np.random.default_rng(rng.H_int(lead, rng.ENV, FAMILY_ID[fam], env.variant))
        if fam == "HOLD":
            a = int(g.integers(N))
            sidx[b, 0] = a
            ridx[b, 0] = a
            yy = _coin(g, tr)
            for k in range(tr):
                t0 = k * Pd
                sval[t0:t0 + env.cue_len, b, 0] = sg * env.amp * yy[k]
                ds = g.choice([-1, 1], size=env.gap)
                sval[t0 + env.cue_len:t0 + env.cue_len + env.gap, b, 0] = sg * env.amp_dist * ds
                ro_tick[b, k] = t0 + env.cue_len + env.gap
            y[b] = sg * yy
            continue
        if fam in ("RELAY", "FLIP"):
            s = int(g.integers(N))
            a = _pick_at(g, M[s], env.d)
            sidx[b, 0] = s
            ridx[b, 0] = a
            x = _coin(g, tr)
            if fam == "RELAY":
                yy = x
            else:
                sidx[b, 1] = a                 # teacher arrives at the actuator
                assert tr % env.block == 0 and (tr // env.block) % 2 == 0
                m0 = int(g.choice([-1, 1]))
                m = np.array([m0 * (-1) ** (k // env.block) for k in range(tr)])
                yy = m * x
                scored[b] = (np.arange(tr) % env.block) != 0
            for k in range(tr):
                t0 = k * Pd
                sval[t0:t0 + env.cue_len, b, 0] = sg * env.amp * x[k]
                ro_tick[b, k] = t0 + env.delta
                if fam == "FLIP":
                    t1 = t0 + env.delta + 1
                    sval[t1:t1 + env.cue_len, b, 1] = sg * env.amp_teacher * yy[k]
            y[b] = sg * yy
        elif fam == "XOR":
            s1 = int(g.integers(N))
            s2 = _pick_at(g, M[s1], env.d)
            half = max(1, env.d // 2)
            ok = np.flatnonzero((M[s1] >= half) & (M[s2] >= half) & (M[s1] < 10 ** 6))
            ok = np.setdiff1d(ok, [s1, s2])
            a = int(ok[g.integers(ok.size)]) if ok.size else _pick_at(g, M[s1], half, (s1, s2))
            sidx[b] = (s1, s2)
            ridx[b, 0] = a
            combos = np.stack([_coin(g, tr), _coin(g, tr)], 1)
            combos[:, 0] *= sg                 # mirror: negate input 1 -> y negated
            for k in range(tr):
                t0 = k * Pd
                sval[t0:t0 + env.cue_len, b, 0] = env.amp * combos[k, 0]
                sval[t0:t0 + env.cue_len, b, 1] = env.amp * combos[k, 1]
                ro_tick[b, k] = t0 + env.delta
            y[b] = combos[:, 0] * combos[:, 1]
        elif fam == "MAJ":
            a = int(g.integers(N))
            ridx[b, 0] = a
            ss = []
            for j in range(env.n_maj):
                ss.append(_pick_at(g, M[a], env.d, exclude=ss))
            sidx[b] = ss
            x = _coin(g, tr)
            for k in range(tr):
                t0 = k * Pd
                flips = np.where(g.random(env.n_maj) < env.flip_p, -1, 1)
                sval[t0:t0 + env.cue_len, b, :] = sg * env.amp * x[k] * flips
                ro_tick[b, k] = t0 + env.delta
            y[b] = sg * x
    sch = Schedule(torch.as_tensor(sidx), torch.as_tensor(sval), torch.as_tensor(ridx))
    return Episode(sch, ro_tick, np.zeros_like(ro_tick), y, scored,
                   {"family": fam, "env": env.to_dict(), "T": T})


def score(ep: Episode, trace: np.ndarray) -> np.ndarray:
    """Per-world accuracy on scored trials. trace [T, B, A] of S0."""
    B, tr = ep.y.shape
    s0 = trace[ep.ro_tick, np.arange(B)[:, None], ep.ro_slot]    # [B, trials]
    corr = np.where(s0 == 0, 0.5, (np.sign(s0) == ep.y).astype(float))
    return (corr * ep.scored).sum(1) / ep.scored.sum(1)


def per_trial(ep: Episode, trace: np.ndarray) -> np.ndarray:
    B, tr = ep.y.shape
    s0 = trace[ep.ro_tick, np.arange(B)[:, None], ep.ro_slot]
    return np.where(s0 == 0, 0.5, (np.sign(s0) == ep.y).astype(float))
