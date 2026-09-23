"""Family A -- REGS: a metered register machine.

Physics: information is held in b-bit registers (b = log2 V). Every allocated
register bit costs `bitcost` currency per tick and flips independently with
probability `q` per tick. No repair. Registers are unbounded in number.

Mechanisms are register programs executed in lockstep over E episodes:
  SEL   on the tagged input: ALLOC r0 <- in ; hold ; at ask: OUT r0
  LOG   on every input: ALLOC r_i <- in ; hold all ; at ask: OUT r0
  LAST  no ALLOC ; at ask: OUT the current input register (blank -> 0)
Alternative mechanism (C0m, 2026-09-23): params["code"] = 3 stores every bit 3x and reads by
majority at the ask (3x cost, no in-flight repair). Absent "code" = the reference mechanism.

Self-contained: numpy + the contract signatures only (independence audit).
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from prometheus.cosmos.contract import Family


class Regs(Family):
    name = "regs"
    version = "1"
    lineage = ("prometheus/cosmos/substrates/regs.py",)

    def space(self) -> Dict[str, List[Any]]:
        return {
            "V": [2, 4, 8, 16],
            "H": [8, 16, 32],
            "K": [0, 1, 2, 4, 7],
            "R": [1.0, 10.0],
            "bitcost": [1e-4, 3e-4, 1e-3, 2e-3, 4e-3, 8e-3, 1.6e-2, 3.2e-2, 6.4e-2, 0.128],
            "q": [0.0, 0.001, 0.003, 0.01, 0.03, 0.06],
        }

    @staticmethod
    def _bits(V: int) -> int:
        return max(1, int(np.ceil(np.log2(V))))

    def coords(self, p: Dict[str, Any], cmap: str = "v1") -> Dict[str, float]:
        b = self._bits(p["V"])
        code = p.get("code", 1)
        if code == 1:
            n = p["q"] * b * p["H"]          # no repair: v2 == v1
        elif cmap == "v1":
            n = p["q"] * code * b * p["H"]
        else:                                # repetition-3, majority read at the ask, no repair in flight
            pi = (1 - (1 - 2 * p["q"]) ** p["H"]) / 2
            pm = 3 * pi * pi - 2 * pi ** 3
            n = -b * float(np.log1p(-pm)) if pm < 1 else float("inf")
        return {"C": p["bitcost"] * code * b * p["H"] / p["R"], "N": n, "K": float(p["K"]), "G": 1.0 - 1.0 / p["V"]}

    def units(self, p: Dict[str, Any]) -> Dict[str, float]:
        return {"reward_per_success": float(p["R"])}

    def run(self, p: Dict[str, Any], mech: str, seed: int, episodes: int) -> Dict[str, Any]:
        V, H, K, R, bc, q = p["V"], p["H"], p["K"], p["R"], p["bitcost"], p["q"]
        code = p.get("code", 1)              # alternative mechanism: repetition code per stored bit
        b = self._bits(V) * code
        E = episodes
        env = np.random.default_rng(seed)
        cue = env.integers(0, V, E)
        # distractor arrival ticks: K distinct ticks in 1..H-1 per episode
        times = np.sort(np.argsort(env.random((E, H - 1)), axis=1)[:, :K] + 1, axis=1) if K else np.zeros((E, 0), int)
        dvals = env.integers(0, V, (E, K))
        target = env.integers(0, V, E) if p.get("sham") else cue
        noise = np.random.default_rng(seed ^ 0x5EED5)

        if mech == "LAST":
            out = np.zeros(E, dtype=np.int64)
            cost = np.zeros(E)
            meters = {"reg_bit_ticks": np.zeros(E)}
        else:
            nreg = 1 if mech == "SEL" else 1 + K
            regs = np.zeros((E, nreg), dtype=np.int64)
            alloc_t = np.full((E, nreg), -1, dtype=np.int64)
            regs[:, 0] = self._encode(cue, code)
            alloc_t[:, 0] = 0
            bit_ticks = np.zeros(E)
            weights = (1 << np.arange(b)).astype(np.int64)
            for t in range(1, H + 1):
                if mech == "LOG" and K:
                    for j in range(K):
                        hit = times[:, j] == t
                        regs[hit, 1 + j] = self._encode(dvals[hit, j], code)
                        alloc_t[hit, 1 + j] = t
                live = alloc_t >= 0
                if q > 0:
                    flips = (noise.random((E, nreg, b)) < q) & live[:, :, None]
                    regs ^= (flips.astype(np.int64) * weights).sum(axis=2)
                bit_ticks += live.sum(axis=1) * b
            out = self._decode(regs[:, 0] % (1 << b), code, b // code)
            cost = bit_ticks * bc
            meters = {"reg_bit_ticks": bit_ticks}
        reward = np.where(out == target, R, 0.0)
        return {"reward": reward, "cost": cost, **meters}

    @staticmethod
    def _encode(v, code):
        if code == 1:
            return v
        b0 = int(np.max(v)).bit_length() if np.size(v) else 1
        out = np.zeros_like(v)
        for i in range(max(b0, 5)):
            bit = (v >> i) & 1
            for c in range(code):
                out |= bit << (code * i + c)
        return out

    @staticmethod
    def _decode(v, code, nbits):
        if code == 1:
            return v
        out = np.zeros_like(v)
        for i in range(nbits):
            ones = sum(((v >> (code * i + c)) & 1) for c in range(code))
            out |= ((ones * 2 > code).astype(np.int64)) << i
        return out

    def coord_preserving(self, p: Dict[str, Any], rng) -> List[Dict[str, Any]]:
        out = []
        for m in (0.5, 2.0):          # stretch the horizon, rescale per-tick physics
            H2 = int(round(p["H"] * m))
            if H2 >= 4 and H2 > p["K"] + 1:
                f = p["H"] / H2
                out.append(dict(p, H=H2, bitcost=p["bitcost"] * f, q=p["q"] * f))
        for m in (0.1, 10.0):         # change the currency unit
            out.append(dict(p, R=p["R"] * m, bitcost=p["bitcost"] * m))
        return out


FAMILY = Regs()
