"""Literature ceiling (dev seeds): batch TT completion by ALS on m stored
samples (unbounded scratch, many sweeps). NOT an organism: it shows how
many samples a standard method needs, i.e. what online learners are
competing against. Provenance: ALS for TT completion, e.g. Grasedyck,
Kluge, Kraemer, SIAM J. Sci. Comput. 37(5) 2015 (doi:10.1137/130942401)."""
import numpy as np, sys, json
from concurrent.futures import ProcessPoolExecutor
from .world import World, D, NV
from .tt import TT


def als(w, m, rank, order, seed, sweeps=30, reg=1e-3):
    rng = np.random.default_rng(seed)
    cells = rng.choice(len(w.x), m, replace=False)
    A = w.addr[cells][:, list(order)]
    y = w.x[cells] + rng.normal(0, 0.1, m)
    t = TT([NV] * D, (rank,) * (D - 1), init_scale=1.0, rng=rng)
    for _ in range(sweeps):
        for k in list(range(D)) + list(range(D - 2, 0, -1)):
            # left/right interface vectors per sample
            L = np.ones((m, 1))
            for j in range(k):
                L = np.einsum('ma,mab->mb', L, t.cores[j][:, A[:, j], :].transpose(1, 0, 2))
            R = np.ones((m, 1))
            for j in range(D - 1, k, -1):
                R = np.einsum('mab,mb->ma', t.cores[j][:, A[:, j], :].transpose(1, 0, 2), R)
            a, n, b = t.cores[k].shape
            for v in range(n):
                s = A[:, k] == v
                if s.sum() == 0:
                    continue
                F = np.einsum('ma,mb->mab', L[s], R[s]).reshape(s.sum(), a * b)
                G = F.T @ F + reg * np.eye(a * b)
                t.cores[k][:, v, :] = np.linalg.solve(G, F.T @ y[s]).reshape(a, b)
    p = np.array([t.eval(tuple(a[list(np.argsort(order))])) for a in w.addr[:, list(order)]])
    full = w.x
    # t was fit on permuted addresses; evaluate the same way
    pa = np.array([t.eval(tuple(r)) for r in w.addr[:, list(order)]])
    return float(1 - ((full - pa) ** 2).sum() / ((full - full.mean()) ** 2).sum())


def job(a):
    inst, m, rank, which = a
    w = World(0, inst)
    order = tuple(int(i) for i in np.argsort(w.perm)) if which == "lat" else tuple(range(D))
    return (which, rank, m, inst, als(w, m, rank, order, inst))


if __name__ == "__main__":
    jobs = [(i, m, r, wh) for i in range(4) for m in (200, 400, 800, 1600) for (r, wh) in ((3, "lat"), (3, "obs"), (4, "obs"))]
    with ProcessPoolExecutor(24) as ex:
        res = list(ex.map(job, jobs))
    import collections
    agg = collections.defaultdict(list)
    for wh, r, m, i, v in res:
        agg[(wh, r, m)].append(v)
    for k in sorted(agg):
        print(k, round(float(np.median(agg[k])), 3))
    with open("ensorain/runs/dev_als_ceiling.jsonl", "a") as f:
        for row in res:
            f.write(json.dumps(row) + "\n")
