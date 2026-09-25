"""E2 structure discovery (PREREG_E2). Reuses E1's world mechanics,
memories and life loop unchanged; adds world families with per-instance
hidden structure, a 17-hypothesis space, a shared discovery phase, and the
discovery mechanisms compared as arms."""
import itertools
import json
import os
import time

import numpy as np

from ensorain.e0.tt import ranks_of_order
from ensorain.e1 import mem as M
from ensorain.e1.life import live
from ensorain.e1.world import World1, NV, D, N, latent_cores, full

FAMILIES = ("TT", "MAT", "CP", "NONE")
CAP = 192
DISC_EVENTS, BUF, N_FIT = 300, 512, 384
ORDERS = [o for o in itertools.permutations(range(D)) if o[0] < o[-1]]  # 12, up to reversal
H = [("TT", o) for o in ORDERS] + [("LR", p) for p in range(3)] + [("CP",), ("NONE",)]
P_OF = {"TT": 192, "LR": 128, "CP": 192, "NONE": 0}


def _field(family, inst):
    rng = np.random.default_rng(70_000_000 + inst + 1_000_000 * FAMILIES.index(family))
    if family == "TT":
        lat = full(latent_cores(inst))
    elif family == "MAT":
        u, v = rng.normal(size=(NV, NV)), rng.normal(size=(NV, NV))
        lat = np.einsum("ab,cd->abcd", u, v)
    elif family == "CP":
        f = rng.normal(size=(D, NV, 4))
        lat = np.einsum("ar,br,cr,dr->abcd", f[0], f[1], f[2], f[3])
    else:
        lat = rng.normal(size=(NV,) * D)
    return lat / lat.std()


class World2(World1):
    """E1 world mechanics with a family-specific field and a per-instance hidden permutation."""

    def __init__(self, family, inst_seed):
        self.family, self.inst_seed, self.class_seed, self.lam = family, inst_seed, None, 0.0
        lat = _field(family, inst_seed)
        self.perm = np.random.default_rng(80_000_000 + inst_seed + 1_000_000 * FAMILIES.index(family)).permutation(D)
        rng = np.random.default_rng(40_000_000 + inst_seed)
        pairs = rng.permutation(64)[:16]
        ho = np.zeros((NV, NV), dtype=bool)
        ho[pairs // NV, pairs % NV] = True
        self.lat_heldout = ho
        self.x = np.transpose(lat, self.perm).copy()
        inv = np.argsort(self.perm)
        self.ax = {name: int(inv[k]) for k, name in enumerate("ABCD")}
        self.addr = np.array(np.unravel_index(np.arange(N), [NV] * D)).T
        self.heldout_cell = ho[self.addr[:, self.ax["A"]], self.addr[:, self.ax["C"]]]
        xf = self.x.reshape(-1)
        self.sd = {"L1": float(xf[~self.heldout_cell].std()), "L2": float(xf[self.heldout_cell].std())}
        g = np.random.default_rng(50_000_000 + inst_seed)
        vals = []
        for _ in range(2000):
            a = self.addr[g.integers(N)].copy()
            w = g.normal(size=NV)
            w /= np.linalg.norm(w)
            vals.append(self._contract(a, w))
        self.sd["L3"] = float(np.std(vals))

    def correct(self, h):
        if self.family == "TT":
            return h[0] == "TT" and ranks_of_order(self.x, h[1]) == [3, 3, 3]
        if self.family == "MAT":
            if h[0] != "LR":
                return False
            rows = set(M.PARTITIONS[h[1]][0])
            ab = {self.ax["A"], self.ax["B"]}
            return rows == ab or rows == set(range(D)) - ab
        if self.family == "CP":
            return h[0] == "CP"
        return h[0] == "NONE"

    def correct_h(self):
        return next(h for h in H if self.correct(h))


def build(h, consts, seed=0, disc=False):
    c = dict(consts[h[0]]) if h[0] != "NONE" else {}
    if disc and h[0] != "NONE":  # part 2: from-scratch fits use a light ridge, not the proximal lam
        c["lam"] = consts["disc_lam"]
    if h[0] == "TT":
        m = M.TTAls(CAP, order=h[1], ranks=(3, 3, 3), seed=seed, **c)
    elif h[0] == "LR":
        m = M.LowRank(CAP, part=h[1], R=1, seed=seed, **c)
    elif h[0] == "CP":
        m = M.CP(CAP, R=6, seed=seed, **c)
    else:
        return M.NoMem(CAP)
    if disc:
        m.prox_zero = True  # from-scratch fit: ordinary ridge toward 0
    return m


def fit(mem, A, y, sweeps):
    if isinstance(mem, M.NoMem) or sweeps <= 0:
        return 0
    old = mem.sweeps
    mem.sweeps = int(sweeps)
    u = mem.consolidate(A, y)
    mem.sweeps = old
    return u


def val_mse(mem, A, y):
    return float(np.mean((mem.predict_many(A) - y) ** 2))


# ---------------- mechanisms: (buffer split, consts, D, rng) -> (h, units, trace)

def _cost(h, sweeps):
    return N_FIT * P_OF[h[0]] * sweeps


def mech_exhaustive(Af, yf, Av, yv, consts, Dmax, rng, hs=H):
    per = sum(_cost(h, 1) for h in hs)
    s = max(1, int(Dmax // per)) if per else 1
    units, scores = 0, {}
    for h in hs:
        if units + _cost(h, s) > Dmax and h[0] != "NONE":
            continue
        m = build(h, consts, disc=True)
        units += fit(m, Af, yf, s)
        scores[h] = val_mse(m, Av, yv)
    best = min(scores, key=scores.get)
    return best, units, [dict(sweeps=s, n=len(scores), best=float(scores[best]))]


def mech_sd(Af, yf, Av, yv, consts, Dmax, rng):
    alive = list(H)
    mems = {h: build(h, consts, disc=True) for h in alive}
    units, s, trace = 0, 1, []
    scores = {}
    while True:
        need = sum(_cost(h, s) for h in alive)
        if units + need > Dmax:
            break
        for h in alive:
            units += fit(mems[h], Af, yf, s)
            scores[h] = val_mse(mems[h], Av, yv)
        alive.sort(key=lambda h: scores[h])
        trace.append(dict(sweeps=s, n=len(alive), best=float(scores[alive[0]])))
        if len(alive) == 1:
            break
        alive = alive[: (len(alive) + 1) // 2]
        s *= 2
    return alive[0], units, trace


def _neighbors(h):
    tt_id, lr0 = ("TT", ORDERS[0]), ("LR", 0)
    if h[0] == "TT":
        o = list(h[1])
        out = []
        for i in range(D - 1):
            q = o[:]
            q[i], q[i + 1] = q[i + 1], q[i]
            q = tuple(q) if q[0] < q[-1] else tuple(reversed(q))
            out.append(("TT", q))
        return out + [("CP",), lr0, ("NONE",)]
    if h[0] == "LR":
        return [("LR", p) for p in range(3) if p != h[1]] + [tt_id, ("CP",), ("NONE",)]
    if h[0] == "CP":
        return [tt_id, lr0, ("NONE",)]
    return [tt_id, lr0, ("CP",)]


def mech_greedy(Af, yf, Av, yv, consts, Dmax, rng, s=5):
    cur = ("TT", ORDERS[0])
    m = build(cur, consts, disc=True)
    units = fit(m, Af, yf, s)
    score = {cur: val_mse(m, Av, yv)}
    trace = [dict(step=0, h=str(cur), best=score[cur])]
    while True:
        moved = False
        cand = [h for h in _neighbors(cur) if h not in score]
        for h in cand:
            if units + _cost(h, s) > Dmax:
                break
            mm = build(h, consts, disc=True)
            units += fit(mm, Af, yf, s)
            score[h] = val_mse(mm, Av, yv)
        best = min(score, key=score.get)
        if best != cur:
            cur, moved = best, True
            trace.append(dict(step=len(trace), h=str(cur), best=score[cur]))
        if not moved or units >= Dmax:
            break
    return cur, units, trace


def mech_mi(Af, yf, Av, yv, consts, Dmax, rng):
    A = np.vstack([Af, Av])
    y2 = np.concatenate([yf, yv]) ** 2
    dep = np.zeros((D, D))
    for i, j in itertools.combinations(range(D), 2):
        g = np.zeros((NV, NV))
        c = np.zeros((NV, NV))
        np.add.at(g, (A[:, i], A[:, j]), y2)
        np.add.at(c, (A[:, i], A[:, j]), 1)
        m = np.where(c > 0, g / np.maximum(c, 1), np.nan)
        mi = np.nanmean(m, axis=1, keepdims=True)
        mj = np.nanmean(m, axis=0, keepdims=True)
        mu = np.nanmean(m)
        dep[i, j] = dep[j, i] = float(np.nanvar(m - mi - mj + mu))
    best = max(ORDERS, key=lambda o: sum(dep[o[k], o[k + 1]] for k in range(D - 1)))
    return ("TT", best), len(A) * 6, [dict(dep=dep.round(4).tolist())]


def mech_lrsel(Af, yf, Av, yv, consts, Dmax, rng):
    hs = [("LR", p) for p in range(3)]
    s = max(1, min(int(consts["LR"].get("sweeps", 20)), int(Dmax // sum(_cost(h, 1) for h in hs))))
    return mech_exhaustive(Af, yf, Av, yv, consts, sum(_cost(h, s) for h in hs), rng, hs=hs)


# ---------------- one life

def discovery_buffer(w, ev, rng):
    """Reservoir buffer over the discovery phase + a fit/validation split BY CELL."""
    # discovery buffer: reservoir over observed samples of the discovery phase
    bufA, bufy, seen = [], [], 0
    for e in ev[:DISC_EVENTS]:
        if e[0] != "obs":
            continue
        ys = w.x[tuple(e[1].T)] + e[2]
        for a, v in zip(e[1], ys):
            seen += 1
            if len(bufA) < BUF:
                bufA.append(a)
                bufy.append(v)
            else:
                k = int(rng.integers(seen))
                if k < BUF:
                    bufA[k], bufy[k] = a, v
    bufA, bufy = np.array(bufA), np.array(bufy)
    # split by CELL so a cell seen twice cannot sit on both sides (dev fix, part 2)
    cells = np.ravel_multi_index(bufA.T, [NV] * D)
    uc = rng.permutation(np.unique(cells))
    vset, nv = set(), 0
    for c in uc:
        if nv >= len(bufy) - N_FIT:
            break
        vset.add(int(c))
        nv += int((cells == c).sum())
    vmask = np.isin(cells, list(vset))
    fi, vi = np.nonzero(~vmask)[0], np.nonzero(vmask)[0]
    return bufA, bufy, fi, vi



def run_life(family, inst, arm, org, consts, econ, Dmax, outer_h=None):
    w = World2(family, inst)
    ev = w.events()
    rng = np.random.default_rng(90_000_000 + inst * 7 + org)
    kappa = econ["kappa"]
    out = dict(family=family, inst_seed=inst, arm=arm, org_seed=org)
    if arm == "NOMEM":
        r = live(w, M.NoMem(CAP), ev, econ)
        out.update(r, h="NONE", correct=w.family == "NONE", disc_units=0, init_units=0)
        return out
    r1 = live(w, M.NoMem(CAP), ev[:DISC_EVENTS], econ)
    bufA, bufy, fi, vi = discovery_buffer(w, ev, rng)
    Af, yf, Av, yv = bufA[fi], bufy[fi], bufA[vi], bufy[vi]
    trace = []
    if arm == "ORACLE_H":
        h, du = w.correct_h(), 0
    elif arm == "BLIND1":
        h, du = H[int(rng.integers(len(H)))], 0
    elif arm == "RANDPERM":
        h, du = ("TT", ORDERS[int(rng.integers(len(ORDERS)))]), 0
    elif arm == "OUTER":
        h, du = outer_h, 0
    else:
        mech = {"EXHAUSTIVE": mech_exhaustive, "SD": mech_sd, "GREEDY": mech_greedy,
                "MI": mech_mi, "LRSEL": mech_lrsel}[arm]
        h, du, trace = mech(Af, yf, Av, yv, consts, Dmax, rng)
    h = tuple(tuple(x) if isinstance(x, list) else x for x in h)
    mem = build(h, consts, seed=org, disc=True)
    iu = fit(mem, bufA, bufy, consts[h[0]]["sweeps"]) if h[0] != "NONE" else 0
    if h[0] != "NONE":
        mem.lam = float(consts[h[0]]["lam"])
        mem.prox_zero = False  # life consolidation: E1's proximal ridge
    e2 = dict(econ, energy0=r1["energy"] - kappa * (du + iu))
    if r1["died"] or e2["energy0"] <= 0:
        r2 = dict(reward=0.0, comp_energy=0.0, steps=0, died=True, P_used=int(M.audit(mem, CAP)) if h[0] != "NONE" else 0,
                  r2_ho=float("nan"), r2_seen=float("nan"), comp_learn=0.0,
                  **{f"{p}_{k}": 0 for p in ("n", "ok") for k in ("L1", "L2", "L3s", "L3h")})
    else:
        r2 = live(w, mem, ev[DISC_EVENTS:], e2)
    comp_e = r1["comp_energy"] + kappa * (du + iu) + r2["comp_energy"]
    reward = r1["reward"] + r2["reward"]
    out.update(h="|".join(map(str, h)), correct=bool(w.correct(h)), disc_units=du, init_units=iu,
               trace=trace, reward=reward, comp_energy=comp_e, U=reward - comp_e,
               steps=r1["steps"] + r2["steps"], died=bool(r2["died"]), P_used=r2["P_used"],
               r2_ho=r2["r2_ho"], r2_seen=r2["r2_seen"], comp_learn=r2.get("comp_learn", 0.0) + iu,
               **{f"{p}_{k}": r1[f"{p}_{k}"] + r2[f"{p}_{k}"] for p in ("n", "ok") for k in ("L1", "L2", "L3s", "L3h")})
    return out


def _job(j):
    t0 = time.time()
    try:
        r = run_life(j["family"], j["inst_seed"], j["arm"], j["org_seed"], j["consts"], j["econ"], j["Dmax"],
                     tuple(tuple(x) if isinstance(x, list) else x for x in j["outer_h"]) if j.get("outer_h") else None)
        r["status"] = "OK"
    except M.AuditError as ex:
        r = dict(status="AUDIT_REFUSED", reason=str(ex))
    r.update({k: v for k, v in j.items() if k not in ("consts", "econ")})
    r["secs"] = round(time.time() - t0, 2)
    return r


def run(jobs, out_path, workers=None):
    from concurrent.futures import ProcessPoolExecutor
    for v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(v, "1")
    workers = workers or int(os.environ.get("ENSORAIN_WORKERS", "18"))
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as ex, open(out_path, "a") as f:
        for r in ex.map(_job, jobs, chunksize=1):
            f.write(json.dumps(r, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)) + "\n")
            f.flush()
            rows.append(r)
    return rows
