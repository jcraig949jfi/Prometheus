"""RIE-01 environmental input physics + topology (operator directive 2026-09-24, Phase C2/C4).

Every input regime is a pure function of (world seed label, cell, epoch, case) -- and, for SELF_CONDITIONED, of the executing
organism's own genome -- computed from its own SplitMix64 stream. None of them draws from the world or mutation RNG (tested), and all
supply exactly NC one-byte cases per execution, like the frozen task ECHO_forced. No regime scores organisms: there is no fitness
channel; inputs only change what a program reads with IN.

Regimes (8):
  IID           each case byte uniform 0..255, fresh per (cell, epoch, case)
  TEMPORAL      piecewise constant in time: per (cell, case) the byte holds for segments of SEG epochs (phase per cell)
  LOCAL         locally correlated: cells in the same group of GROUP consecutive cells share their bytes each epoch
  PERIODIC      deterministic sweep: (7*epoch + 85*case + 3*cell) mod 256 (every byte recurs with period 256 epochs)
  SPARSE        mostly 0; with probability 1/SPARSE_P a case carries a uniform event byte
  HETERO        spatially heterogeneous: each cell has a fixed centre c(cell); bytes uniform in c +/- HETERO_W
  SHIFTING      regime-shifting: every SHIFT epochs the active quarter of byte space (0-63, 64-127, 128-191, 192-255) is redrawn
  SELF_COND     organism-conditioned feedback without a fitness channel: case k reads byte (epoch + k) mod 32 of the executing genome
Topologies (2): WELL_MIXED (core default) and GRID (16 x 8 torus, von Neumann neighbour chosen with the world RNG, as z80atlas grid).
"""
from __future__ import annotations

from proteus.foundry.prng import SplitMix64, seed_from

NC = 3
SEG = 16; GROUP = 8; SPARSE_P = 32; HETERO_W = 8; SHIFT = 500
REGIMES = ["IID", "TEMPORAL", "LOCAL", "PERIODIC", "SPARSE", "HETERO", "SHIFTING", "SELF_COND"]
TOPOLOGIES = ["WELL_MIXED", "GRID"]
W, H = 16, 8                                                              # 128 ecology cells


def _r(label, *parts):
    return SplitMix64(seed_from(label, *parts))


def make_inputs(regime: str, label: str):
    """Returns inputs(world, cell, epoch) -> [(x,)] * NC for the core engine."""
    if regime == "IID":
        def f(w, cell, epoch):
            r = _r(label, "iid", cell, epoch); return [((r.next_u32() >> 24),) for _ in range(NC)]
    elif regime == "TEMPORAL":
        def f(w, cell, epoch):
            ph = _r(label, "tph", cell).next_u32() % SEG; seg = (epoch + ph) // SEG
            return [((_r(label, "tmp", cell, seg, k).next_u32() >> 24),) for k in range(NC)]
    elif regime == "LOCAL":
        def f(w, cell, epoch):
            r = _r(label, "loc", cell // GROUP, epoch); return [((r.next_u32() >> 24),) for _ in range(NC)]
    elif regime == "PERIODIC":
        def f(w, cell, epoch):
            return [(((7 * epoch + 85 * k + 3 * cell) & 255),) for k in range(NC)]
    elif regime == "SPARSE":
        def f(w, cell, epoch):
            r = _r(label, "spa", cell, epoch); out = []
            for _ in range(NC):
                u, v = r.next_u32(), r.next_u32(); out.append(((v >> 24) if u % SPARSE_P == 0 else 0,))
            return out
    elif regime == "HETERO":
        def f(w, cell, epoch):
            c = _r(label, "hc", cell).next_u32() >> 24; r = _r(label, "het", cell, epoch)
            return [(((c + (r.next_u32() % (2 * HETERO_W + 1)) - HETERO_W) & 255),) for _ in range(NC)]
    elif regime == "SHIFTING":
        def f(w, cell, epoch):
            q = _r(label, "shq", epoch // SHIFT).next_u32() % 4; r = _r(label, "shf", cell, epoch)
            return [((q * 64 + (r.next_u32() % 64)),) for _ in range(NC)]
    elif regime == "SELF_COND":
        def f(w, cell, epoch):
            g = w.genomes[cell]; return [((g[(epoch + k) % len(g)] if g is not None else 0),) for k in range(NC)]
    else:
        raise ValueError(regime)
    return f


def grid_neighbour(world, i: int) -> int:
    x, y = i % W, i // W; d = world.rng.randbelow(4)
    if d == 0: x = (x + 1) % W
    elif d == 1: x = (x - 1) % W
    elif d == 2: y = (y + 1) % H
    else: y = (y - 1) % H
    return y * W + x


def neighbour_fn(topology: str):
    return None if topology == "WELL_MIXED" else grid_neighbour
