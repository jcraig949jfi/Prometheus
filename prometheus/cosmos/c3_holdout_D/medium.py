"""Holdout family D: a drifting, reacting, noisy 1-D chemical medium ("reactive channel").

Physical picture
----------------
A narrow channel of L well-mixed compartments ("sites") carries a solvent that flows downstream at
velocity v. S = V dissolved chemical species live in it; the state is the concentration field
c[site, species] (arbitrary concentration units, "cu"). Every observed symbol is a chemical PULSE:
  cue symbol s in 0..V-1          -> q cu of species s is injected at site x_in
  distractor symbol V+j           -> q cu of species j is injected at site x_in
                                     (distractors are the SAME molecules as cues: the medium cannot
                                     tell a cue pulse from a distractor pulse chemically)
  query / hint symbols (>= 2V)    -> nothing is injected
Native physics then acts on the whole field each step (in this order, with an explicit monotone
integrator using n_sub internal sub-steps chosen from the rates):
  advection   solvent drift, upwind, speed v (sites/step), downstream = increasing site index
  diffusion   molecular diffusion, coefficient D (sites^2/step)
  reaction    pairwise annihilation of UNLIKE species, c_i + c_j -> 0 (i != j), rate constant kappa
  boundaries  both channel ends are open (absorbing): material leaving the channel is lost
  decay       first-order spontaneous decomposition, fraction p_decay of every molecule per step
  noise       thermal/counting fluctuation, additive Gaussian of amplitude sigma cu per step,
              concentrations are floored at 0 (no negative matter)
Integrator note: the first-order upwind advection scheme adds numerical dispersion of about
(v/2) * (1 - v*dt) sites^2/step on top of D; that is part of this world's physics as implemented
(the declared D is the explicit diffusion coefficient only). Mass is conserved except at the open ends,
by decay and by annihilation; the centre of mass of a pulse drifts exactly v sites/step.
A sensor patch of w_patch sites starting d_patch sites downstream of the injection site measures all
species concentrations there; that patch is the ONLY thing the system's readout policy sees.

Contract (roles/Cosmos/c3/D_CONTRACT.md) compliance
---------------------------------------------------
- Batched System interface of prometheus/cosmos/c3/system.py.
- All randomness enters through noise(): one (n, L, S) standard-normal array per step.
- The state dict {"c": (E, L, S) float64} is the WHOLE causal state (the dynamics are autonomous:
  no clock, no hidden counters), so exchanging rows between episodes is a valid state.
- Deterministic given (world, seed).
- No cross-substrate coordinate is declared; each knob below is a native physical quantity.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, replace
from typing import Dict, Iterable, Tuple

import numpy as np

from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task

FAMILY_NAME = "D-reactive-channel"
FAMILY_VERSION = 1

# ----------------------------------------------------------------------------------------------
# Native parameters (contract s4): name -> (units, physical meaning, declared range)
# Ranges are closed intervals; integer knobs are marked int. Geometric knobs are jointly constrained
# by x_in + d_patch + w_patch <= L (the sensor patch must lie inside the channel).
# ----------------------------------------------------------------------------------------------
KNOBS: Dict[str, Tuple[str, str, Tuple[float, float], type]] = {
    "L":       ("sites", "channel length (number of well-mixed compartments)", (6, 48), int),
    "D":       ("sites^2/step", "molecular diffusion coefficient of every species", (0.0, 2.0), float),
    "v":       ("sites/step", "solvent drift velocity, downstream positive", (0.0, 3.0), float),
    "p_decay": ("1/step (fraction per step)", "first-order spontaneous decomposition: fraction of every "
                "molecule destroyed per step", (0.0, 1.0), float),
    "kappa":   ("1/(cu*step)", "rate constant of pairwise annihilation of unlike species c_i + c_j -> 0",
                (0.0, 1.0), float),
    "q":       ("cu", "amount injected at x_in by one observed symbol pulse (cue or distractor)",
                (0.25, 4.0), float),
    "sigma":   ("cu/step", "amplitude of additive thermal/counting fluctuations per site, species, step",
                (0.0, 1.0), float),
    "x_in":    ("sites", "index of the injection compartment", (0, 47), int),
    "d_patch": ("sites", "distance from the injection compartment to the first sensed compartment",
                (0, 47), int),
    "w_patch": ("sites", "number of contiguous compartments the sensor patch measures", (1, 48), int),
    "V":       ("symbols", "alphabet size = number of chemical species", (2, 8), int),
    "k":       ("steps", "number of distractor pulses between cue and query (task, declared)", (2, 8), int),
}
K_ALLOWED = (2, 4, 8)


@dataclass(frozen=True)
class World:
    """One world = (family D, knob values, k, V)."""
    V: int
    k: int
    L: int
    D: float
    v: float
    p_decay: float
    kappa: float
    q: float
    sigma: float
    x_in: int
    d_patch: int
    w_patch: int

    def as_dict(self) -> dict:
        return asdict(self)

    def task(self) -> Task:
        return Task(V=self.V, k=self.k)


def validate(w: World) -> World:
    for name, (_u, _m, (lo, hi), typ) in KNOBS.items():
        x = getattr(w, name)
        if typ is int and (not isinstance(x, (int, np.integer)) or isinstance(x, bool)):
            raise ValueError("knob %s must be an integer, got %r" % (name, x))
        if not (lo <= x <= hi) or (isinstance(x, float) and not math.isfinite(x)):
            raise ValueError("knob %s=%r outside declared range [%s, %s]" % (name, x, lo, hi))
    if w.k not in K_ALLOWED:
        raise ValueError("k must be one of %s" % (K_ALLOWED,))
    if w.x_in + w.d_patch + w.w_patch > w.L:
        raise ValueError("sensor patch must lie inside the channel: x_in + d_patch + w_patch <= L")
    return w


# ----------------------------------------------------------------------------------------------
# The system
# ----------------------------------------------------------------------------------------------
class ReactiveChannel(System):
    def __init__(self, world: World):
        self.w = validate(world)
        self.name = "D:" + ",".join("%s=%s" % (k, v) for k, v in world.as_dict().items())
        self.S = world.V
        rate = 2.0 * world.D + world.v
        self.n_sub = max(1, int(math.ceil(rate / 0.8)))          # keeps dt*(2D+v) <= 0.8: monotone
        self.dt = 1.0 / self.n_sub
        self.patch = slice(world.x_in + world.d_patch, world.x_in + world.d_patch + world.w_patch)

    # -- state ------------------------------------------------------------------------------
    def init(self, E: int):
        return {"c": np.zeros((E, self.w.L, self.S), dtype=np.float64)}

    def noise(self, n: int, rng) -> Dict[str, np.ndarray]:
        return {"xi": rng.standard_normal((n, self.w.L, self.S))}

    # -- physics ----------------------------------------------------------------------------
    def _inject(self, c: np.ndarray, obs: np.ndarray) -> None:
        V = self.w.V
        obs = np.asarray(obs, dtype=np.int64)
        species = np.where(obs < V, obs, obs - V)
        pulse = obs < 2 * V                                     # query/hint symbols inject nothing
        rows = np.nonzero(pulse)[0]
        c[rows, self.w.x_in, species[rows]] += self.w.q

    def _transport_react(self, c: np.ndarray) -> np.ndarray:
        w, dt = self.w, self.dt
        for _ in range(self.n_sub):
            pad = np.zeros((c.shape[0], c.shape[1] + 2, c.shape[2]))
            pad[:, 1:-1] = c                                     # absorbing ghost compartments
            left, mid, right = pad[:, :-2], pad[:, 1:-1], pad[:, 2:]
            c = mid - dt * w.v * (mid - left) + dt * w.D * (right - 2.0 * mid + left)
            if w.kappa > 0:
                tot = c.sum(axis=2, keepdims=True)
                c = c - dt * w.kappa * c * (tot - c)
            c = np.maximum(c, 0.0)
        return c

    def step(self, state, obs_t, noise):
        c = state["c"].copy()
        self._inject(c, obs_t)
        c = self._transport_react(c)
        c = c * (1.0 - self.w.p_decay)
        if self.w.sigma > 0:
            c = c + self.w.sigma * noise["xi"]
        return {"c": np.maximum(c, 0.0)}

    # -- observation of the state ------------------------------------------------------------
    def readout_features(self, state) -> np.ndarray:
        return state["c"][:, self.patch, :].reshape(state["c"].shape[0], -1).copy()

    def full_state(self, state) -> np.ndarray:
        return state["c"].reshape(state["c"].shape[0], -1).copy()


# ----------------------------------------------------------------------------------------------
# Intervention API (contract s5)
# ----------------------------------------------------------------------------------------------
def build(**knobs) -> ReactiveChannel:
    """Build the world at any knob setting inside the declared ranges (all knobs required)."""
    missing = set(KNOBS) - set(knobs)
    extra = set(knobs) - set(KNOBS)
    if missing or extra:
        raise ValueError("knobs missing %s / unknown %s" % (sorted(missing), sorted(extra)))
    return ReactiveChannel(World(**knobs))


def intervene(world: World, **changes) -> World:
    """do(knob: a -> b): the same world with the named knobs changed (validated)."""
    unknown = set(changes) - set(KNOBS)
    if unknown:
        raise ValueError("unknown knobs %s" % sorted(unknown))
    return validate(replace(world, **changes))


def world_from_dict(d: dict) -> World:
    return validate(World(**{k: KNOBS[k][3](d[k]) for k in KNOBS}))


# ----------------------------------------------------------------------------------------------
# World grammar (contract s6): a finite lattice; a world is a lattice point satisfying the geometric
# constraint. The history-free control (p_decay = 1: every molecule decomposes within the step it
# was injected) is a lattice point.
# ----------------------------------------------------------------------------------------------
LATTICE: Dict[str, Tuple] = {
    "V": (2, 3, 4, 5),
    "k": (2, 4, 8),
    "L": (12, 16, 24, 32),
    "D": (0.0, 0.05, 0.2, 0.5, 1.0),
    "v": (0.0, 0.25, 0.5, 1.0, 2.0),
    "p_decay": (0.0, 0.01, 0.03, 0.1, 0.3, 1.0),
    "kappa": (0.0, 0.1, 0.5),
    "q": (1.0, 2.0),
    "sigma": (0.0, 0.05, 0.2, 0.5),
    "x_in": (0, 2),
    "d_patch": (0, 2, 4, 8, 12, 16),
    "w_patch": (1, 2, 4),
}

CONTROL_HISTORY_FREE = World(V=4, k=4, L=12, D=0.2, v=1.0, p_decay=1.0, kappa=0.1, q=2.0, sigma=0.05,
                             x_in=0, d_patch=2, w_patch=4)


def in_lattice(w: World) -> bool:
    return all(getattr(w, k) in vals for k, vals in LATTICE.items()) and \
        w.x_in + w.d_patch + w.w_patch <= w.L


def draw_worlds(n: int, rng) -> list:
    """Draw n lattice worlds (uniform per knob, rejection on the geometric constraint)."""
    out = []
    while len(out) < n:
        d = {k: vals[int(rng.integers(len(vals)))] for k, vals in LATTICE.items()}
        if d["x_in"] + d["d_patch"] + d["w_patch"] > d["L"]:
            continue
        out.append(world_from_dict(d))
    return out


def knob_table() -> Iterable[Tuple[str, str, str, Tuple]]:
    return [(k, u, m, r) for k, (u, m, r, _t) in KNOBS.items()]
