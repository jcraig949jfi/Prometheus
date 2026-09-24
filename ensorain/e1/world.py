"""E1 world (PREREG_E1 s1): a 4-mode TT field with a held-out (A,C) region,
delayed fiber observations along B and D, and tight-tolerance locks.

Coordinates: LATENT modes 0..3 = A, B, C, D. The organism sees OBSERVED
coordinates: observed axis j carries latent axis perm[j]. All event
addresses are in observed coordinates.
"""
import numpy as np

D, NV, N = 4, 8, 8 ** 4
TRUE_RANKS = (3, 3, 3)
N_EVENTS, PHASE2 = 1200, 600
P_OBS = (0.9, 0.3)
LOCK_MIX = (("L1", 0.3), ("L2", 0.4), ("L3", 0.3))


def class_perm(class_seed):
    return np.random.default_rng(10_000_000 + class_seed).permutation(D)


def latent_cores(inst_seed):
    rng = np.random.default_rng(inst_seed)
    r = [1, *TRUE_RANKS, 1]
    return [rng.normal(size=(r[k], NV, r[k + 1])) for k in range(D)]


def full(cores):
    t = cores[0]
    for c in cores[1:]:
        t = np.tensordot(t, c, axes=([-1], [0]))
    return t.reshape([NV] * D)


class World1:
    def __init__(self, class_seed, inst_seed, lam=0.0, relabel_seed=None):
        self.class_seed, self.inst_seed, self.lam = class_seed, inst_seed, lam
        cores = latent_cores(inst_seed)
        lat = full(cores)
        scale = lat.std()
        lat = lat / scale
        self.perm = class_perm(class_seed)
        rng = np.random.default_rng(40_000_000 + inst_seed)
        # held-out (A,C) pairs in LATENT labels: 16 of 64
        pairs = rng.permutation(64)[:16]
        ho = np.zeros((NV, NV), dtype=bool)
        ho[pairs // NV, pairs % NV] = True
        if relabel_seed is not None:  # transplant: undisclosed relabeling + new observed order
            rr = np.random.default_rng(relabel_seed)
            labels = [rr.permutation(NV) for _ in range(D)]
            lat = lat[np.ix_(*labels)]
            ho = ho[np.ix_(labels[0], labels[2])]
            self.perm = rr.permutation(D)
        self.lat_heldout = ho
        xobs = np.transpose(lat, self.perm).copy()
        if lam > 0:  # WORLD R: permute values over cells
            flat = xobs.reshape(-1)
            k = int(round(lam * N))
            cells = np.random.default_rng(20_000_000 + inst_seed).choice(N, size=k, replace=False)
            flat[cells] = flat[np.random.default_rng(20_000_001 + inst_seed).permutation(cells)]
            xobs = flat.reshape([NV] * D)
        self.x = xobs  # observed-coordinate field (instrumentation / truth)
        inv = np.argsort(self.perm)  # latent axis k is observed axis inv[k]
        self.ax = {name: int(inv[k]) for k, name in enumerate("ABCD")}
        addr = np.array(np.unravel_index(np.arange(N), [NV] * D)).T
        self.addr = addr
        self.heldout_cell = ho[addr[:, self.ax["A"]], addr[:, self.ax["C"]]]
        # query-type scales (over the world, for the tolerance)
        xf = self.x.reshape(-1)
        self.sd = {"L1": float(xf[~self.heldout_cell].std()), "L2": float(xf[self.heldout_cell].std())}
        g = np.random.default_rng(50_000_000 + inst_seed)
        vals = []
        for _ in range(2000):
            a = addr[g.integers(N)].copy()
            w = g.normal(size=NV)
            w /= np.linalg.norm(w)
            vals.append(self._contract(a, w))
        self.sd["L3"] = float(np.std(vals))

    def _fiber_addrs(self, a, axis):
        out = np.repeat(np.asarray(a)[None, :], NV, 0)
        out[:, axis] = np.arange(NV)
        return out

    def _contract(self, a, w):
        fa = self._fiber_addrs(a, self.ax["D"])
        return float(self.x[tuple(fa.T)] @ w)

    def events(self, seed_offset=0):
        """Deterministic event stream for this instance (identical for every arm)."""
        rng = np.random.default_rng(60_000_000 + self.inst_seed + seed_offset)
        seen_cells = np.nonzero(~self.heldout_cell)[0]
        ho_cells = np.nonzero(self.heldout_cell)[0]
        observed = np.zeros(N, dtype=bool)
        ev = []
        for t in range(N_EVENTS):
            p_obs = P_OBS[0] if t < PHASE2 else P_OBS[1]
            if rng.random() < p_obs:
                v = int(rng.choice(seen_cells))
                axis = self.ax["B"] if rng.random() < 0.5 else self.ax["D"]
                fa = self._fiber_addrs(self.addr[v], axis)
                idx = np.ravel_multi_index(fa.T, [NV] * D)
                observed[idx] = True
                ev.append(("obs", fa, rng.normal(0, 0.1, NV)))
            else:
                u = rng.random()
                kind = "L1" if u < 0.3 else ("L2" if u < 0.7 else "L3")
                if kind == "L1":
                    cand = seen_cells[~observed[seen_cells]]
                    v = int(rng.choice(cand if len(cand) else seen_cells))
                    a = self.addr[v]
                    ev.append(("L1", a, None, float(self.x[tuple(a)])))
                elif kind == "L2":
                    a = self.addr[int(rng.choice(ho_cells))]
                    ev.append(("L2", a, None, float(self.x[tuple(a)])))
                else:
                    pool = ho_cells if rng.random() < 0.5 else seen_cells
                    a = self.addr[int(rng.choice(pool))].copy()
                    w = rng.normal(size=NV)
                    w /= np.linalg.norm(w)
                    ho = bool(self.heldout_cell[np.ravel_multi_index(tuple(a), [NV] * D)])
                    ev.append(("L3", a, w, self._contract(a, w), ho))
        return ev
