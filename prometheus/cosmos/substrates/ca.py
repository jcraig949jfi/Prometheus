"""Family C -- CA: a block cellular tape with an optional majority repair rule.

Physics: a binary tape of Lc cells. A retained symbol is written as b = log2 V
bit-blocks of r cells each (r in {1, 3}). Every written cell costs `ccell`
currency per tick and flips with probability `p` per tick. When r = 3 the local
rule replaces each cell by the majority of its 3-cell block after the noise step
(a repair physics that regs and ring do not have). The tape is finite: writing
past Lc overwrites from the start (the oldest symbol first).

Mechanisms:
  SEL   write the tagged input only ; at ask: read blocks by majority
  LOG   write every input at the next free offset (wrapping) ; at ask: read slot 0
  LAST  write nothing ; at ask: emit 0

Self-contained: numpy + the contract signatures only.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from prometheus.cosmos.contract import Family


class CA(Family):
    name = "ca"
    version = "1"
    lineage = ("prometheus/cosmos/substrates/ca.py",)

    def space(self) -> Dict[str, List[Any]]:
        return {
            "V": [2, 4, 8, 16],
            "H": [10, 20, 40],
            "K": [0, 1, 2, 4, 8],
            "R": [2.0, 20.0],
            "r": [1, 3],
            "Lc": [24, 510],
            "ccell": [1e-4, 3e-4, 1e-3, 2e-3, 4e-3, 8e-3, 1.6e-2, 3.2e-2, 6.4e-2, 0.128],
            "p": [0.0, 0.0005, 0.0015, 0.005, 0.015, 0.03],
        }

    @staticmethod
    def _bits(V: int) -> int:
        return max(1, int(np.ceil(np.log2(V))))

    def coords(self, pr: Dict[str, Any], cmap: str = "v1") -> Dict[str, float]:
        b, r, H, p = self._bits(pr["V"]), pr["r"], pr["H"], pr["p"]
        if cmap == "v1":
            n = p * b * r * H
        else:  # effective per-block failure hazard after the majority rule
            per_block = p if r == 1 else 3 * p * p - 2 * p ** 3
            n = per_block * b * H
        return {"C": pr["ccell"] * b * r * H / pr["R"], "N": n, "K": float(pr["K"]), "G": 1.0 - 1.0 / pr["V"]}

    def units(self, pr: Dict[str, Any]) -> Dict[str, float]:
        return {"reward_per_success": float(pr["R"])}

    def run(self, pr: Dict[str, Any], mech: str, seed: int, episodes: int) -> Dict[str, Any]:
        V, H, K, R, r, Lc, cc, p = (pr[k] for k in ("V", "H", "K", "R", "r", "Lc", "ccell", "p"))
        b = self._bits(V)
        E = episodes
        g = np.random.default_rng(seed)
        cue = g.integers(0, V, E)
        tk = np.sort(np.argsort(g.random((E, H - 1)), axis=1)[:, :K] + 1, axis=1) if K else np.zeros((E, 0), int)
        dv = g.integers(0, V, (E, K))
        target = g.integers(0, V, E) if pr.get("sham") else cue
        heat = np.random.default_rng(seed * 31 + 17)

        if mech == "LAST":
            return {"reward": np.where(0 == target, R, 0.0), "cost": np.zeros(E), "cell_ticks": np.zeros(E)}

        w = b * r                                  # cells per symbol
        tape = np.zeros((E, Lc), dtype=np.int8)
        written = np.zeros((E, Lc), dtype=bool)
        owner = np.full((E, Lc), -1, dtype=np.int16)   # which symbol index owns each cell

        def write(rows, sym_idx, values, offset):
            bits = ((values[:, None] >> np.arange(b)[None, :]) & 1).astype(np.int8)   # (n, b)
            cells = np.repeat(bits, r, axis=1)                                         # (n, b*r)
            idx = (offset[:, None] + np.arange(w)[None, :]) % Lc
            tape[rows[:, None], idx] = cells
            written[rows[:, None], idx] = True
            owner[rows[:, None], idx] = sym_idx

        allrows = np.arange(E)
        if w > Lc:
            raise ValueError("symbol wider than tape")
        write(allrows, 0, cue, np.zeros(E, dtype=np.int64))
        next_off = np.full(E, w, dtype=np.int64)
        cell_ticks = np.zeros(E)
        for t in range(1, H + 1):
            if mech == "LOG":
                for j in range(K):
                    hit = np.nonzero(tk[:, j] == t)[0]
                    if hit.size:
                        write(hit, j + 1, dv[hit, j], next_off[hit])
                        next_off[hit] += w
            if p > 0:
                flip = (heat.random((E, Lc)) < p) & written
                tape ^= flip.astype(np.int8)
            if r == 3:
                blk = tape.reshape(E, Lc // 3, 3) if Lc % 3 == 0 else None
                if blk is None:
                    raise ValueError("Lc must be a multiple of 3 when r = 3")
                maj = (blk.sum(axis=2) >= 2).astype(np.int8)
                tape[:] = np.where(written, np.repeat(maj, 3, axis=1), tape)
            cell_ticks += written.sum(axis=1)
        # read slot 0 (cells [0, w)); if any of them was overwritten, the symbol is gone
        intact = (owner[:, :w] == 0).all(axis=1)
        bits = tape[:, :w].reshape(E, b, r).sum(axis=2) * 2 > r
        val = (bits.astype(np.int64) << np.arange(b)[None, :]).sum(axis=1)
        out = np.where(intact, val, 0)
        return {"reward": np.where(out == target, R, 0.0), "cost": cell_ticks * cc, "cell_ticks": cell_ticks}

    def coord_preserving(self, pr: Dict[str, Any], rng) -> List[Dict[str, Any]]:
        out = []
        r2 = 3 if pr["r"] == 1 else 1        # change the carrier redundancy, keep v1 coordinates
        f = pr["r"] / r2
        out.append(dict(pr, r=r2, ccell=pr["ccell"] * f, p=min(0.5, pr["p"] * f)))
        H2 = pr["H"] * 2
        out.append(dict(pr, H=H2, ccell=pr["ccell"] / 2, p=pr["p"] / 2))
        out.append(dict(pr, R=pr["R"] * 10, ccell=pr["ccell"] * 10))
        out.append(dict(pr, Lc=24 if pr["Lc"] != 24 else 510))   # capacity: not a declared coordinate
        return out


FAMILY = CA()
