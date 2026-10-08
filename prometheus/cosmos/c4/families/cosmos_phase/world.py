"""cosmos_phase -- a C4 visible world family authored by COSMOS (R-STAT B1: a second mechanism absent from C3).

Mechanism: N noisy, heterogeneous phase oscillators with mean-field (Kuramoto) coupling. An observed symbol kicks the
phases of a symbol-specific subset of oscillators by kappa. Coupling pulls the population back toward its common
rhythm (erasing kick offsets), frequency heterogeneity dephases them, phase noise diffuses them, and an optional
per-oscillator reset redraws a phase uniformly. The policy sees cos/sin of the first R oscillators only.
State is circular (phases), dynamics nonlinear (sin coupling); nothing stores a symbol by construction.

Contract: roles/Cosmos/c4/VISIBLE_FAMILY_CONTRACT.md (the one the foreign author was held to). Authored AFTER the
author had seen the C4 candidate L-0003: this family adds mechanism novelty, not authorship independence.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
from dataclasses import asdict, dataclass

import numpy as np

from prometheus.cosmos.c3.system import System, swap_rows

HERE = os.path.dirname(os.path.abspath(__file__))
TAU = 2 * np.pi


@dataclass(frozen=True)
class Knobs:
    N: int = 24            # oscillators
    K: float = 0.5         # coupling strength (rad/step at full coherence)
    dw: float = 0.2        # SD of natural frequencies around the common rhythm (rad/step)
    sigma: float = 0.1     # phase-noise SD (rad/step)
    kappa: float = 1.5     # kick size (rad)
    frac: float = 0.3      # fraction of oscillators a symbol kicks
    R: int = 6             # oscillators visible to the policy
    reset: float = 0.0     # per-oscillator per-step probability of a uniform phase redraw
    wseed: int = 0         # quenched draw of natural frequencies and symbol subsets


RANGES = {"N": (8, 64), "K": (0.0, 3.0), "dw": (0.0, 1.0), "sigma": (0.0, 1.5), "kappa": (0.0, 3.1416),
          "frac": (0.05, 0.5), "R": (2, 64), "reset": (0.0, 1.0), "wseed": (0, 2 ** 31 - 1)}
NATURAL = {"N": [16, 24, 32], "K": (0.0, 2.0), "dw": (0.0, 0.5), "sigma": (0.02, 0.6), "kappa": (0.5, 2.5),
           "frac": (0.15, 0.4), "R": [4, 6, 8], "reset": (0.0, 0.1), "wseed": "uniform integer"}
HISTORY_FREE = dict(reset=1.0)


def check(kn: Knobs) -> Knobs:
    for f, (lo, hi) in RANGES.items():
        v = getattr(kn, f)
        if not lo <= v <= hi:
            raise ValueError(f"{f}={v} outside {RANGES[f]}")
    if kn.R > kn.N:
        raise ValueError("R must be <= N")
    return kn


class PhaseRing(System):
    family = "cosmos_phase"

    def __init__(self, knobs: Knobs = Knobs()):
        self.kn = check(knobs)
        r = np.random.default_rng(knobs.wseed)
        self.omega = knobs.dw * r.standard_normal(knobs.N)
        self._key = r.integers(1, 2 ** 31 - 1)
        self.name = "phase(%s)" % ",".join("%s=%g" % (k, v) for k, v in asdict(knobs).items())

    def _subset(self, o):
        """(E, N) mask of oscillators kicked by symbol o: a fixed pseudo-random fraction per symbol, any integer."""
        o = np.asarray(o, dtype=np.int64)
        i = np.arange(self.kn.N, dtype=np.int64)
        h = (o[:, None] * 2654435761 + i[None, :] * 40503 + self._key) % 1000003
        return (h / 1000003.0) < self.kn.frac

    def init(self, E):
        return {"th": np.zeros((E, self.kn.N))}

    def noise(self, n, rng):
        N = self.kn.N
        return {"n": rng.standard_normal((n, N)), "u": rng.random((n, N)), "v": rng.random((n, N))}

    def step(self, st, obs_t, nz):
        kn = self.kn
        th = st["th"]
        z = np.exp(1j * th).mean(1, keepdims=True)
        drive = kn.K * np.abs(z) * np.sin(np.angle(z) - th)
        th = th + self.omega + drive + kn.sigma * nz["n"]
        th = np.where(nz["u"] < kn.reset, TAU * nz["v"], th)
        th = th + kn.kappa * self._subset(obs_t)
        return {"th": np.mod(th, TAU)}

    def readout_features(self, st):
        v = st["th"][:, :self.kn.R]
        return np.hstack([np.cos(v), np.sin(v)])

    def full_state(self, st):
        return np.hstack([np.cos(st["th"]), np.sin(st["th"])])


def build_world(**knobs) -> PhaseRing:
    return PhaseRing(Knobs(**knobs))


def sample_natural(rng) -> dict:
    out = {}
    for f, spec in NATURAL.items():
        if f == "wseed":
            out[f] = int(rng.integers(0, 2 ** 31 - 1))
        elif isinstance(spec, list):
            out[f] = spec[int(rng.integers(len(spec)))]
        else:
            out[f] = float(rng.uniform(*spec))
    return out


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
    _, obs = tk.batch(tk.Task(V=4, k=4), 64, np.random.default_rng(seed))
    a, b = _rollout(world, obs, seed), _rollout(world, obs, seed)
    out["replay_identical"] = all(np.array_equal(a[k], b[k]) for k in a)
    perm = np.arange(64).reshape(-1, 2)[:, ::-1].reshape(-1)
    out["interchange_round_trip"] = all(np.array_equal(swap_rows(swap_rows(a, perm), perm)[k], a[k]) for k in a)
    n1, n2 = world.noise(8, np.random.default_rng(3)), world.noise(8, np.random.default_rng(3))
    s0 = world.init(8)
    x = np.arange(8)
    out["noise_is_only_randomness"] = (all(np.array_equal(n1[k], n2[k]) for k in n1) and
                                       np.array_equal(world.step(s0, x, n1)["th"], world.step(s0, x, n2)["th"]))
    hf = build_world(**HISTORY_FREE)
    for kk in (2, 4, 8):
        _, pobs = tk.paired_batch(tk.Task(V=4, k=kk), 32, np.random.default_rng(seed + kk))
        rng = np.random.default_rng(seed)
        st = hf.init(pobs.shape[0])
        for t in range(pobs.shape[1]):
            nz = {k_: np.repeat(v, 2, axis=0) for k_, v in hf.noise(pobs.shape[0] // 2, rng).items()}
            st = hf.step(st, pobs[:, t], nz)
        f = hf.readout_features(st)
        out[f"history_free_control_k{kk}"] = bool(np.allclose(f[0::2], f[1::2]))
    out["history_free_control_declared"] = True
    out["any_symbol_accepted"] = bool(np.isfinite(_rollout(world, np.array([[0, 99, 12345, -3, 7]]), seed)["th"]).all())
    return out


def provenance_stamp() -> dict:
    src = open(os.path.join(HERE, "world.py"), "rb").read().replace(b"\r\n", b"\n")
    return {"python": platform.python_version(), "numpy": np.__version__, "machine": platform.node(),
            "source_sha256_lf": hashlib.sha256(src).hexdigest(), "defaults": asdict(Knobs())}


if __name__ == "__main__":
    res = selftest()
    print(json.dumps(res, indent=1))
    rec = {"selftest": res, "all_pass": all(res.values()), "provenance": provenance_stamp(),
           "command": "python -m prometheus.cosmos.c4.families.cosmos_phase.world"}
    with open(os.path.join(HERE, "SELFTEST.json"), "w") as fh:
        json.dump(rec, fh, indent=1)
