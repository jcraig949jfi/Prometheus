"""SEDIMENT LEDGER -- a C4 visible world family authored by Theseus (non-Cosmos author).

Contract: roles/Cosmos/c4/VISIBLE_FAMILY_CONTRACT.md (the only Cosmos design file read).
Interface: prometheus.cosmos.c3.system.System; task: prometheus.cosmos.c3.task.

Mechanism (a 1-D channel of N cells carrying sediment, per episode):

  susp[N]  sediment suspended in the flow
  bed[N]   sediment lying on the channel bed

Each step, in this order:
  1. INJECT   the observed symbol x drops a pulse of `load` units into the flow at
              site(x) = (x * groove) mod N. Every integer symbol is accepted.
  2. DRIFT    the suspended load moves `drift` cells downstream (periodic channel).
  3. FLUSH    a fraction `flush` of the suspended load leaves the channel for good.
  4. SETTLE   in each cell, with probability `settle`, the WHOLE suspended load of that cell
              drops onto the bed at once (all-or-nothing clumps; driven by noise['u_settle']).
  5. SCOUR    in each cell, with probability `scour`, the WHOLE bed of that cell is lifted back
              into suspension (driven by noise['u_scour']).
  6. CREEP    a fraction `creep` of every bed cell slides one cell downstream (deterministic).

Whatever the cue left on the bed and survives scour, creep and later deposits is all the channel
"remembers"; nothing else carries history. The policy reads the bed and the suspended load.

Native parameters (knobs), their units and meanings are in NATIVE.json. All randomness enters
through noise(n, rng); step() is a deterministic function of (state, obs, noise).
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
from dataclasses import dataclass, asdict

import numpy as np

from prometheus.cosmos.c3.system import System, swap_rows

HERE = os.path.dirname(os.path.abspath(__file__))


@dataclass(frozen=True)
class Knobs:
    n_cells: int = 24        # channel length, cells
    groove: int = 5          # site spacing: site(x) = x * groove mod n_cells (cells per symbol index)
    load: float = 1.0        # sediment units dropped per observed symbol
    drift: int = 1           # flow speed, cells per step
    flush: float = 0.2       # fraction of suspended load exported per step
    settle: float = 0.5      # per-cell probability per step that the suspended clump drops to the bed
    scour: float = 0.05      # per-cell probability per step that the bed is lifted back into the flow
    creep: float = 0.05      # fraction of each bed cell sliding one cell downstream per step


RANGES = {
    "n_cells": (8, 64), "groove": (1, 63), "load": (0.1, 10.0), "drift": (0, 4),
    "flush": (0.0, 1.0), "settle": (0.0, 1.0), "scour": (0.0, 1.0), "creep": (0.0, 1.0),
}

# The family's ordinary operating space (Cosmos samples uniformly from it).
NATURAL = {
    "n_cells": [16, 24, 32],
    "groove": [3, 5, 7],
    "load": [1.0],
    "drift": [0, 1, 2],
    "flush": (0.0, 0.6),
    "settle": (0.05, 0.95),
    "scour": (0.0, 0.3),
    "creep": (0.0, 0.3),
}

# Declared history-free control: nothing ever settles and the flow is fully flushed every step,
# so the state after any step is a function of the current symbol only.
HISTORY_FREE = dict(settle=0.0, flush=1.0)


def check(kn: Knobs) -> Knobs:
    for f, (lo, hi) in RANGES.items():
        v = getattr(kn, f)
        if not lo <= v <= hi:
            raise ValueError(f"{f}={v} outside declared range [{lo}, {hi}]")
    if kn.groove >= kn.n_cells:
        raise ValueError("groove must be < n_cells")
    return kn


class SedimentLedger(System):
    name = "theseus_sediment"

    def __init__(self, knobs: Knobs = Knobs()):
        self.kn = check(knobs)

    # -- API -----------------------------------------------------------------------------------
    def init(self, E):
        N = self.kn.n_cells
        return {"susp": np.zeros((E, N)), "bed": np.zeros((E, N))}

    def noise(self, n, rng):
        N = self.kn.n_cells
        return {"u_settle": rng.random((n, N)), "u_scour": rng.random((n, N))}

    def step(self, state, obs_t, noise):
        kn = self.kn
        N = kn.n_cells
        E = obs_t.shape[0]
        susp = state["susp"].copy()
        bed = state["bed"].copy()
        sites = (np.asarray(obs_t, dtype=np.int64) * kn.groove) % N
        susp[np.arange(E), sites] += kn.load                                   # 1 inject
        if kn.drift:
            susp = np.roll(susp, kn.drift, axis=1)                              # 2 drift
        susp *= (1.0 - kn.flush)                                                # 3 flush
        drop = noise["u_settle"] < kn.settle                                    # 4 settle
        bed = bed + np.where(drop, susp, 0.0)
        susp = np.where(drop, 0.0, susp)
        lift = noise["u_scour"] < kn.scour                                      # 5 scour
        susp = susp + np.where(lift, bed, 0.0)
        bed = np.where(lift, 0.0, bed)
        if kn.creep:                                                            # 6 creep
            moving = kn.creep * bed
            bed = bed - moving + np.roll(moving, 1, axis=1)
        return {"susp": susp, "bed": bed}

    def readout_features(self, state):
        return np.concatenate([state["bed"], state["susp"]], axis=1)

    def full_state(self, state):
        return np.concatenate([state["susp"], state["bed"]], axis=1)

    # -- declared native measurement (optional per contract s3) ---------------------------------
    def transport_work(self, before, after):
        """Sediment units that changed compartment or cell in one step, per episode (units)."""
        return (np.abs(after["bed"] - before["bed"]).sum(1) + np.abs(after["susp"] - before["susp"]).sum(1)) / 2.0


def build_world(**knobs) -> SedimentLedger:
    """A system at any knob setting inside the declared ranges."""
    return SedimentLedger(Knobs(**knobs))


def sample_natural(rng) -> dict:
    """One knob setting drawn uniformly from the declared natural distribution."""
    out = {}
    for f, spec in NATURAL.items():
        if isinstance(spec, list):
            out[f] = spec[int(rng.integers(len(spec)))]
        else:
            out[f] = float(rng.uniform(*spec))
    return out


# ------------------------------------------------------------------------------------------------
# controls-only selftest (contract s5)


def _rollout(sys_, obs, seed):
    rng = np.random.default_rng(seed)
    st = sys_.init(obs.shape[0])
    for t in range(obs.shape[1]):
        st = sys_.step(st, obs[:, t], sys_.noise(obs.shape[0], rng))
    return st


def selftest(seed: int = 0) -> dict:
    from prometheus.cosmos.c3 import task as tk

    out = {}
    world = build_world()
    task = tk.Task(V=4, k=4)
    _, obs = tk.batch(task, 64, np.random.default_rng(seed))
    a, b = _rollout(world, obs, seed), _rollout(world, obs, seed)
    out["replay_identical"] = all(np.array_equal(a[k], b[k]) for k in a)
    perm = np.arange(64).reshape(-1, 2)[:, ::-1].reshape(-1)
    out["interchange_round_trip"] = all(np.array_equal(swap_rows(swap_rows(a, perm), perm)[k], a[k]) for k in a)
    n1 = world.noise(8, np.random.default_rng(3))
    n2 = world.noise(8, np.random.default_rng(3))
    s0 = world.init(8)
    x = np.arange(8)
    out["noise_is_only_randomness"] = (all(np.array_equal(n1[k], n2[k]) for k in n1) and
                                       all(np.array_equal(world.step(s0, x, n1)[k], world.step(s0, x, n2)[k])
                                           for k in s0))
    hf = build_world(**HISTORY_FREE)
    for kk in (2, 4, 8):
        cues, pobs = tk.paired_batch(tk.Task(V=4, k=kk), 32, np.random.default_rng(seed + kk))
        rng = np.random.default_rng(seed)
        st = hf.init(pobs.shape[0])
        for t in range(pobs.shape[1]):
            nz = hf.noise(pobs.shape[0] // 2, rng)
            nz = {k_: np.repeat(v, 2, axis=0) for k_, v in nz.items()}
            st = hf.step(st, pobs[:, t], nz)
        f = hf.readout_features(st)
        out[f"history_free_control_k{kk}"] = bool(np.array_equal(f[0::2], f[1::2]))
    out["history_free_control_declared"] = True
    out["any_symbol_accepted"] = bool(np.isfinite(_rollout(world, np.array([[0, 99, 12345, -3, 7]]), seed)["bed"]).all())
    return out


def provenance_stamp() -> dict:
    src = open(os.path.join(HERE, "world.py"), "rb").read().replace(b"\r\n", b"\n")
    return {"python": platform.python_version(), "numpy": np.__version__, "machine": platform.node(),
            "source_sha256_lf": hashlib.sha256(src).hexdigest(), "defaults": asdict(Knobs())}


if __name__ == "__main__":
    r = selftest()
    print(json.dumps(r, indent=1))
    print(json.dumps(provenance_stamp(), indent=1))
    raise SystemExit(0 if all(r.values()) else 1)
