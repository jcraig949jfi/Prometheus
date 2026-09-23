"""E0 world generator: world classes C (compressible), R (randomised
control) and M_lambda (mixtures), on a directed graph over a 6-mode address
space. See ensorain/PREREG_E0.md s1.

A world CLASS (class_seed) fixes the physics: the latent->observed mode
scramble. A world INSTANCE (inst_seed) fixes the TT cores, the graph and
the R permutation. C and R built from the same (class, instance) share the
graph and the value histogram exactly.
"""
import numpy as np
from .tt import tt_svd  # noqa: F401  (re-export convenience for controls)

D, NV = 6, 4
N = NV ** D
TRUE_RANK = 3


def class_perm(class_seed):
    """perm[j] = latent mode shown as observed coordinate j."""
    rng = np.random.default_rng(10_000_000 + class_seed)
    return rng.permutation(D)


def latent_field(inst_seed, rank=TRUE_RANK):
    rng = np.random.default_rng(inst_seed)
    r = [1] + [rank] * (D - 1) + [1]
    t = rng.normal(size=(1, NV, r[1]))
    for k in range(1, D):
        core = rng.normal(size=(r[k], NV, r[k + 1]))
        t = np.tensordot(t, core, axes=([-1], [0]))
    t = t.reshape([NV] * D)
    # scale only: centring would add a rank-1 constant and make the true rank 4
    return t / t.std()


class World:
    def __init__(self, class_seed, inst_seed, lam=0.0, long_jump_p=0.1, n_exits=4):
        self.class_seed, self.inst_seed, self.lam = class_seed, inst_seed, lam
        self.perm = class_perm(class_seed)
        lat = latent_field(inst_seed)
        # observed axis j is latent axis perm[j]
        xobs = np.transpose(lat, self.perm).reshape(-1).copy()
        rng = np.random.default_rng(20_000_000 + inst_seed)
        # R / mixture: permute values over a random lam-fraction of cells
        k = int(round(lam * N))
        if k > 1:
            cells = rng.choice(N, size=k, replace=False)
            xobs[cells] = xobs[rng.permutation(cells)]
        self.x_c_obs = np.transpose(lat, self.perm).reshape(-1)  # instrumentation only
        self.x = xobs
        self.addr = np.array(np.unravel_index(np.arange(N), [NV] * D)).T  # (N, D)
        grng = np.random.default_rng(30_000_000 + inst_seed)
        strides = NV ** np.arange(D - 1, -1, -1)
        exits = []
        for v in range(N):
            a = self.addr[v]
            nbrs = []
            for j in range(D):
                for val in range(NV):
                    if val != a[j]:
                        nbrs.append(v + (val - a[j]) * strides[j])
            e = list(grng.choice(nbrs, size=n_exits, replace=False))
            if grng.random() < long_jump_p:
                e.append(int(grng.integers(N)))
            exits.append(np.array(e, dtype=np.int64))
        self.exits = exits

    def dense_obs(self):
        return self.x.reshape([NV] * D)
