"""W-L n-back task, plants and helpers (PLAN.md in this directory).

The n-back builder is injected by monkeypatching prometheus.ananke.envs.build
IN THIS PROCESS ONLY (install()); the frozen files are not edited, so
search.evolve / assays.evaluate run their own code unchanged.
"""
from __future__ import annotations

import dataclasses
import pathlib
import sys

import numpy as np
import torch

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[4]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from prometheus.ananke import assays, c1b_run, envs, plants, rng  # noqa: E402
from prometheus.ananke.engine import Schedule  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402

NS, NS_HELD = 0x5F2, 0x5F3
NBACK_ID = 0x4E42


@dataclasses.dataclass(frozen=True)
class NBackSpec(envs.EnvSpec):
    n: int = 1          # lag; family stays "HOLD" so period()/T() are HOLD's


def m2():
    ph, env, g, r = c1b_run.load("4ab2ba014aac967e")
    return ph, env, g, r


def spec(n: int, env: envs.EnvSpec | None = None) -> NBackSpec:
    env = env or m2()[1]
    d = env.to_dict()
    d.update(n=n)
    return NBackSpec(**d)


def build_nback(ph: Physics, env: NBackSpec, world_seeds) -> envs.Episode:
    B = len(world_seeds)
    assert B % 2 == 0 and env.family == "HOLD"
    N, T, tr, Pd, n = ph.n_sites, env.T(), env.trials, env.period(), env.n
    sidx = np.zeros((B, 1), dtype=np.int64)
    ridx = np.zeros((B, 1), dtype=np.int64)
    sval = np.zeros((T, B, 1), dtype=np.int32)
    ro_tick = np.zeros((B, tr), dtype=np.int64)
    y = np.zeros((B, tr), dtype=np.int64)
    cues = np.zeros((B, tr), dtype=np.int64)
    scored = np.zeros((B, tr), dtype=bool)
    scored[:, n:] = True
    for b in range(B):
        lead = int(world_seeds[b - (b % 2)])
        sg = -1 if b % 2 else 1
        g = np.random.default_rng(rng.H_int(lead, rng.ENV, NBACK_ID + n, env.variant))
        a = int(g.integers(N))
        sidx[b, 0] = a
        ridx[b, 0] = a
        c = np.where(g.random(tr) < 0.5, 1, -1)
        for k in range(tr):
            t0 = k * Pd
            sval[t0:t0 + env.cue_len, b, 0] = sg * env.amp * c[k]
            ds = g.choice([-1, 1], size=env.gap)
            sval[t0 + env.cue_len:t0 + env.cue_len + env.gap, b, 0] = sg * env.amp_dist * ds
            ro_tick[b, k] = t0 + env.cue_len + env.gap
            y[b, k] = sg * c[k - n] if k >= n else sg * c[k]   # unscored filler for k < n
        cues[b] = sg * c
    sch = Schedule(torch.as_tensor(sidx), torch.as_tensor(sval), torch.as_tensor(ridx))
    return envs.Episode(sch, ro_tick, np.zeros_like(ro_tick), y, scored,
                        {"family": f"NBACK{n}", "env": env.to_dict(), "T": T, "cues": cues})


_ORIG_BUILD = envs.build


def _build(ph, env, world_seeds):
    if isinstance(env, NBackSpec):
        return build_nback(ph, env, world_seeds)
    return _ORIG_BUILD(ph, env, world_seeds)


def install():
    envs.build = _build


# ------------------------------------------------------------------ plants
def _cond():
    """T0 := 256 on an awake cue tick (|SENSE| = 256), else 0 (distractor 64 -> 16-17 < 0)."""
    return [("MULQ", "T0", "SENSE", "SENSE", 0),     # 256 cue, 16 distractor, 0 silent
            ("ADDI", "T0", "T0", 0, -17),
            ("GT", "T0", "T0", "ZERO", 0)]


def _gated(dst, src_reg, tmp):
    """dst := src where T0 == 256 (dst += (src - dst) * T0 >> 8)."""
    return [("SUB", tmp, src_reg, dst, 0), ("MULQ", tmp, tmp, "T0", 0), ("ADD", dst, dst, tmp, 0)]


def body(name: str, ph: Physics):
    if name == "P1S":            # n=1, carrier S1
        lines = _cond() + _gated("S0", "S1", "T1") + _gated("S1", "SENSE", "T1")
    elif name == "P2S":          # n=2, S1 = 2*c_k + c_{k-1} (units of 256)
        lines = _cond() + [
            ("GT", "T1", "S1", "ZERO", 0), ("GT", "T2", "ZERO", "S1", 0),
            ("SUB", "T1", "T1", "T2", 0),                  # a = sign(S1)*256 = c_k
            ("SUB", "T2", "S1", "T1", 0), ("SUB", "T2", "T2", "T1", 0),   # b = c_{k-1}
        ] + _gated("S0", "T2", "T3") + [
            ("ADD", "T2", "SENSE", "SENSE", 0), ("ADD", "T2", "T2", "T1", 0),  # 2*cue + a
        ] + _gated("S1", "T2", "T3")
    elif name == "P1K":          # n=1, carrier Kp[3] via WIMM
        lines = _cond() + [
            ("ADDI", "T1", "ZERO", 0, 0),                  # line 3: T1 = Kp[3] (stored cue)
        ] + _gated("S0", "T1", "T2") + [
            ("MOV", "T3", "T1", 0, 0),
        ] + _gated("T3", "SENSE", "T2") + [               # T3 = cue ? SENSE : stored
            ("CONST", "T2", 0, 0, 3),
            ("WIMM", "T1", "T2", "T3", 0),                 # Kp[3] := T3
        ]
    elif name == "LAG0":         # latch current cue (no memory beyond the query)
        lines = _cond() + _gated("S0", "SENSE", "T1")
    elif name == "NULL":
        lines = []
    else:
        raise KeyError(name)
    b = plants.assemble(ph, lines)
    return np.broadcast_to(b, (ph.rules, *b.shape)).copy(), len(lines)


def seeds(ns: int, *keys, M: int = 64):
    return assays.world_seeds(rng.H_int(ns, *keys), M)
