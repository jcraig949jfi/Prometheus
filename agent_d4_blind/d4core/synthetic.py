"""Synthetic geometry controls C1..C7 with KNOWN qualitative geometry.

Each control implements the Substrate interface. Genome = node id (int).
Fingerprint = (node_id, latent_coord). The instrument sees fingerprints only
through d1/pkey/disp_features — never the latent truth directly.

Known truths (what the instrument MUST recover):
  C1 FRAGMENTED        diverse, locally fine, globally shattered islands
  C2 IDENTITY          connected ring, 98% of mutations are identity
  C3 CORRIDOR          two clusters; ONLY operator 4, from a gateway edge,
                       crosses between them (designed highway)
  C4 TRAPPED           one-way branch chains funneling into a common sink;
                       cross-branch accessibility impossible from most starts
  C5 NAVIGABLE         torus grid, five overlapping isotropic step operators
  C6 CHAOS             huge, hash-random fingerprints, teleport moves —
                       diversity without any navigable structure
  C7 TINY              perfectly navigable 40-node complete graph (poverty)
"""
from __future__ import annotations

import numpy as np

from .interface import Substrate

FEAT_DIM = 12  # [d1, same_pkey, dx(0..7), |dx|, spare]


class SyntheticControl(Substrate):
    name = "synthetic"
    n_ops = 5

    def __init__(self, seed: int):
        super().__init__()
        self.seed = seed
        self.rng0 = np.random.default_rng(seed)
        self.coords: np.ndarray | None = None  # (N, d)
        self.dscale = 1.0
        self.n_nodes = 0

    # genome = int node id ---------------------------------------------------
    def random_genome(self, rng):
        return int(rng.integers(0, self.n_start))  # ab-initio support

    @property
    def n_start(self) -> int:
        return self.n_nodes

    def _evaluate_raw(self, genome):
        gid = int(genome)
        return (gid, self.coords[gid])

    def viable(self, fp) -> bool:
        return True

    def pkey(self, fp):
        return fp[0]

    def fp_bytes(self, fp) -> bytes:
        return int(fp[0]).to_bytes(8, "little")

    def _delta(self, c1, c2) -> np.ndarray:
        return c2 - c1

    def d1(self, f1, f2) -> float:
        d = self._delta(f1[1], f2[1])
        return float(min(1.0, np.sqrt(float(np.dot(d, d))) / self.dscale))

    def disp_features(self, fp, fc) -> np.ndarray:
        out = np.zeros(FEAT_DIM)
        out[0] = self.d1(fp, fc)
        out[1] = 1.0 if fp[0] == fc[0] else 0.0
        d = self._delta(fp[1], fc[1]) / self.dscale
        k = min(8, d.shape[0])
        out[2:2 + k] = d[:k]
        out[10] = float(np.sqrt(np.dot(d, d)))
        return out

    def crossover(self, g1, g2, rng):
        # blend: nearest node to the coordinate midpoint
        mid = (self.coords[int(g1)] + self.coords[int(g2)]) / 2.0
        d = self.coords - mid[None, :]
        return int(np.argmin(np.einsum("ij,ij->i", d, d)))


class C1Fragmented(SyntheticControl):
    name = "C1_FRAGMENTED"

    def __init__(self, seed: int = 4401):
        super().__init__(seed)
        centers = []
        for ix in range(20):
            for iy in range(20):
                centers.append((ix * 200.0, iy * 200.0))
        centers = np.array(centers)  # 400 islands
        offs = self.rng0.normal(0, 2.0, size=(400, 25, 2))
        self.coords = (centers[:, None, :] + offs).reshape(-1, 2)
        self.n_nodes = 400 * 25
        self.dscale = 800.0  # ball 0.1 = 80 units: same island only

    def mutate(self, genome, op_index, rng):
        isl = int(genome) // 25
        return isl * 25 + int(rng.integers(0, 25))

    def crossover(self, g1, g2, rng):
        # stays honest: blend restricted to the two parents' islands
        pick = int(g1) if rng.random() < 0.5 else int(g2)
        isl = pick // 25
        return isl * 25 + int(rng.integers(0, 25))


class C2Identity(SyntheticControl):
    name = "C2_IDENTITY"

    def __init__(self, seed: int = 4402):
        super().__init__(seed)
        self.n_nodes = 10_000
        th = 2 * np.pi * np.arange(self.n_nodes) / self.n_nodes
        r = self.n_nodes / (2 * np.pi)
        self.coords = np.stack([r * np.cos(th), r * np.sin(th)], axis=1)
        self.dscale = 2500.0

    def d1(self, f1, f2) -> float:
        i, j = int(f1[0]), int(f2[0])
        d = abs(i - j)
        d = min(d, self.n_nodes - d)
        return float(min(1.0, d / self.dscale))

    def mutate(self, genome, op_index, rng):
        if rng.random() < 0.98:
            return int(genome)
        step = 1 if rng.random() < 0.5 else -1
        return (int(genome) + step) % self.n_nodes

    def crossover(self, g1, g2, rng):
        i, j = int(g1), int(g2)
        return (i + j) // 2 if abs(i - j) <= self.n_nodes // 2 else ((i + j) // 2 + self.n_nodes // 2) % self.n_nodes


class C3Corridor(SyntheticControl):
    """Clusters A (ids 0..4999, x 0..49) and B (ids 5000..9999, x 330..379).
    Ab-initio genomes live in A only. Ops 0-3: isotropic small steps within
    the current cluster. Op 4: identity everywhere EXCEPT at the gateway
    (A: x>=48 -> jump to B x-330 edge; B: x<=331 -> jump back to A x=49)."""
    name = "C3_CORRIDOR"

    def __init__(self, seed: int = 4403):
        super().__init__(seed)
        a = np.array([(x, y) for x in range(50) for y in range(100)], dtype=float)
        b = a.copy()
        b[:, 0] += 330.0
        self.coords = np.vstack([a, b])
        self.n_nodes = 10_000
        self.dscale = 400.0

    @property
    def n_start(self) -> int:
        return 5000  # ab-initio support: cluster A only

    def _xy(self, gid):
        c = self.coords[gid]
        return int(round(c[0])), int(round(c[1]))

    def _gid(self, cluster, x, y):
        return cluster * 5000 + x * 100 + y

    def mutate(self, genome, op_index, rng):
        gid = int(genome)
        cluster = gid // 5000
        x, y = self._xy(gid)
        cx = x - 330 if cluster == 1 else x
        if op_index == 4:
            if cluster == 0 and cx >= 48:
                return self._gid(1, 0, y)          # A gateway -> B edge
            if cluster == 1 and cx <= 1:
                return self._gid(0, 49, y)         # B gateway -> A edge
            return gid                              # identity elsewhere
        # ops 0-3: identical isotropic step, magnitude 1-2, clamped in-cluster
        ang = rng.random() * 2 * np.pi
        mag = 1 + int(rng.integers(0, 2))
        nx = int(np.clip(round(cx + mag * np.cos(ang)), 0, 49))
        ny = int(np.clip(round(y + mag * np.sin(ang)), 0, 99))
        return self._gid(cluster, nx, ny)

    def crossover(self, g1, g2, rng):
        gid1, gid2 = int(g1), int(g2)
        if gid1 // 5000 != gid2 // 5000:
            return gid1 if rng.random() < 0.5 else gid2
        return super().crossover(gid1, gid2, rng)


class C4Trapped(SyntheticControl):
    """60 one-way chains (branches) of 200 nodes converging into a shared
    100-node sink. Moves only go down-chain (1-3 steps) or, at the sink,
    shuffle within the sink. No branch-to-branch transitions exist."""
    name = "C4_TRAPPED"

    def __init__(self, seed: int = 4404):
        super().__init__(seed)
        nb, npos = 60, 200
        coords = np.zeros((nb * npos + 100, 2))
        for b in range(nb):
            th = 2 * np.pi * b / nb
            for p in range(npos):
                r = 200.0 - p
                coords[b * npos + p] = (r * np.cos(th) + self.rng0.normal(0, 0.5),
                                        r * np.sin(th) + self.rng0.normal(0, 0.5))
        # sink: tight cluster at origin
        coords[nb * npos:] = self.rng0.normal(0, 1.5, size=(100, 2))
        self.coords = coords
        self.nb, self.npos = nb, npos
        self.n_nodes = nb * npos + 100
        self.dscale = 300.0

    def mutate(self, genome, op_index, rng):
        gid = int(genome)
        if gid >= self.nb * self.npos:  # in sink: absorbing shuffle
            return self.nb * self.npos + int(rng.integers(0, 100))
        b, p = gid // self.npos, gid % self.npos
        step = 1 + int(rng.integers(0, 3))
        p2 = p + step
        if p2 >= self.npos:
            return self.nb * self.npos + int(rng.integers(0, 100))
        return b * self.npos + p2

    def crossover(self, g1, g2, rng):
        return int(g1) if rng.random() < 0.5 else int(g2)


class C5Navigable(SyntheticControl):
    """100x100 torus. Five operators with identical isotropic step mixtures
    (magnitude <= 3). The known-neutral pole: connected, diverse, multiply
    navigable, no operator owns a direction or corridor."""
    name = "C5_NAVIGABLE"

    def __init__(self, seed: int = 4405):
        super().__init__(seed)
        self.side = 100
        self.n_nodes = self.side * self.side
        self.coords = np.array([(x, y) for x in range(self.side) for y in range(self.side)], dtype=float)
        self.dscale = 70.71  # max torus distance

    def _delta(self, c1, c2) -> np.ndarray:
        d = c2 - c1
        s = self.side
        d = (d + s / 2) % s - s / 2
        return d

    def mutate(self, genome, op_index, rng):
        gid = int(genome)
        x, y = gid // self.side, gid % self.side
        dx = int(rng.integers(-3, 4))
        dy = int(rng.integers(-3, 4))
        if dx == 0 and dy == 0:
            dx = 1
        return ((x + dx) % self.side) * self.side + ((y + dy) % self.side)

    def crossover(self, g1, g2, rng):
        x1, y1 = int(g1) // self.side, int(g1) % self.side
        x2, y2 = int(g2) // self.side, int(g2) % self.side
        s = self.side
        mx = (x1 + int(round((((x2 - x1) + s / 2) % s - s / 2) / 2))) % s
        my = (y1 + int(round((((y2 - y1) + s / 2) % s - s / 2) / 2))) % s
        return mx * s + my


class C6Chaos(SyntheticControl):
    """100k nodes, 8-dim hash-random fingerprints, uniform teleport moves.
    Diversity without locality: nothing is navigable or re-findable."""
    name = "C6_CHAOS"

    def __init__(self, seed: int = 4406):
        super().__init__(seed)
        self.n_nodes = 100_000
        self.coords = self.rng0.random((self.n_nodes, 8))
        self.dscale = 1.5

    def mutate(self, genome, op_index, rng):
        return int(rng.integers(0, self.n_nodes))

    def crossover(self, g1, g2, rng):
        return int(g1) if rng.random() < 0.5 else int(g2)


class C7Tiny(SyntheticControl):
    """40 nodes, complete teleport graph: perfectly navigable, poverty-level
    diversity."""
    name = "C7_TINY"

    def __init__(self, seed: int = 4407):
        super().__init__(seed)
        self.n_nodes = 40
        self.coords = self.rng0.random((self.n_nodes, 2)) * 100.0
        self.dscale = 141.4

    def mutate(self, genome, op_index, rng):
        return int(rng.integers(0, self.n_nodes))

    def crossover(self, g1, g2, rng):
        return int(g1) if rng.random() < 0.5 else int(g2)


ALL_CONTROLS = {
    "C1_FRAGMENTED": C1Fragmented,
    "C2_IDENTITY": C2Identity,
    "C3_CORRIDOR": C3Corridor,
    "C4_TRAPPED": C4Trapped,
    "C5_NAVIGABLE": C5Navigable,
    "C6_CHAOS": C6Chaos,
    "C7_TINY": C7Tiny,
}

# What the frozen gate evaluator MUST produce for the instrument to pass.
# A set means: any member is an acceptable primary flag (the pathology has
# more than one honest description); the control must NOT pass overall and
# must not be attributed to a listed-excluded cause.
EXPECTED = {
    "C1_FRAGMENTED": {"ACCESSIBILITY_FRAGMENTED"},
    "C2_IDENTITY": {"DISPLACEMENT_COLLAPSE"},
    "C3_CORRIDOR": {"PRIVILEGED_CORRIDOR"},
    "C4_TRAPPED": {"ACCESSIBILITY_FRAGMENTED", "NAVIGATION_FAILURE", "REFINDABILITY_FAILURE"},
    "C5_NAVIGABLE": {"PASS"},
    "C6_CHAOS": {"NAVIGATION_FAILURE", "REFINDABILITY_FAILURE"},
    "C7_TINY": {"PHENOTYPE_POVERTY"},
}
