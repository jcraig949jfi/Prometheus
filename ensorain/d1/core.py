"""D-series Round 1: randomized dial search in Ensorain's lock worlds
(PREREG_D1). World = E2 family worlds + drift + noise. Organism = an E1
memory (TT/CP/LR) + replay store + error store + dial-controlled
consolidation. Every dial is a knob on the same life loop."""
import json
import os
import time

import numpy as np

from ensorain.e0.tt import tt_svd, n_params_for_ranks
from ensorain.e1 import mem as M
from ensorain.e1.life import live as live_e1
from ensorain.e1.world import NV, D, N, full
from ensorain.e2.core import World2

PHASE2 = 600


# ---------------------------------------------------------------- world

def _params(family, rng):
    if family == "TT":
        r = [1, 3, 3, 3, 1]
        return [rng.normal(size=(r[k], NV, r[k + 1])) for k in range(D)]
    if family == "MAT":
        return [rng.normal(size=(NV, NV)), rng.normal(size=(NV, NV))]
    if family == "CP":
        return [rng.normal(size=(D, NV, 4))]
    return [rng.normal(size=(NV,) * D)]


def _lat(family, p):
    if family == "TT":
        return full(p)
    if family == "MAT":
        return np.einsum("ab,cd->abcd", p[0], p[1])
    if family == "CP":
        f = p[0]
        return np.einsum("ar,br,cr,dr->abcd", f[0], f[1], f[2], f[3])
    return p[0]


class WorldD(World2):
    """E2 world mechanics; generative parameters drift at event 600."""

    def __init__(self, family, inst, drift=0.0, noise=0.1):
        super().__init__(family, inst)
        rng = np.random.default_rng(71_000_000 + inst)
        p0 = _params(family, rng)
        p1 = [np.sqrt(1 - drift) * a + np.sqrt(drift) * rng.normal(size=a.shape) for a in p0]
        l0, l1 = _lat(family, p0), _lat(family, p1)
        self.x = np.transpose(l0 / l0.std(), self.perm).copy()
        self.x_new = np.transpose(l1 / l1.std(), self.perm).copy()
        self.x_old = self.x
        self.drift, self.noise = drift, noise
        xf = self.x.reshape(-1)
        self.sd = {"L1": float(xf[~self.heldout_cell].std()), "L2": float(xf[self.heldout_cell].std()), "L3": 1.0}
        g = np.random.default_rng(50_000_000 + inst)
        vals = []
        for _ in range(2000):
            a = self.addr[g.integers(N)].copy()
            w = g.normal(size=NV)
            vals.append(self._contract(a, w / np.linalg.norm(w)))
        self.sd["L3"] = float(np.std(vals))

    def drift_events(self):
        """E2 event stream; truths from event 600 on use the drifted field."""
        ev = self.events()
        out = []
        for t, e in enumerate(ev):
            if t >= PHASE2 and e[0] != "obs":
                if e[0] == "L3":
                    fa = self._fiber_addrs(e[1], self.ax["D"])
                    e = (e[0], e[1], e[2], float(self.x_new[tuple(fa.T)] @ e[2]), e[4])
                else:
                    e = (e[0], e[1], e[2], float(self.x_new[tuple(e[1])]))
            out.append(e)
        return out


# ---------------------------------------------------------------- organism

def _pack(A):
    return np.ravel_multi_index(np.asarray(A).T, [NV] * D)


def _unpack(k):
    return np.array(np.unravel_index(np.asarray(k), [NV] * D)).T


def _param_arrays(m):
    if isinstance(m, M.TTAls):
        return m.tt.cores
    if isinstance(m, M.CP):
        return [m.U]
    return [m.Ur, m.Vc]


def _flat(m):
    return np.concatenate([a.reshape(-1) for a in _param_arrays(m)])


class Organism:
    MIN_MODEL = {"TT": 32, "CP": 32, "LR": 128}

    def __init__(self, dials, world, seed):
        d = dials
        self.d = d
        self.rng = np.random.default_rng(seed)
        fam = d["org_family"]
        C = max(int(d["cap"]), self.MIN_MODEL[fam])  # LR needs 128 floats; actual cap recorded
        # stores share the cap; shrink them if the model would not fit (actual fractions recorded)
        rf, ef = d["replay_frac"], d["err_frac"]
        room = max(0.0, 1.0 - self.MIN_MODEL[fam] / C)
        if rf + ef > room:
            s = room / (rf + ef)
            rf, ef = rf * s, ef * s
        self.n_rep = int(rf * C) // 2
        self.n_err = int(ef * C) // 3
        cap_model = C - 2 * self.n_rep - 3 * self.n_err
        self.actual = dict(replay_frac_actual=2 * self.n_rep / C, err_frac_actual=3 * self.n_err / C,
                           cap_model=cap_model, cap_actual=C)
        latent = tuple(int(i) for i in np.argsort(world.perm))
        if fam == "TT":
            order = latent if d["start"] == "correct" else tuple(int(i) for i in self.rng.permutation(D))
            self.model = M.TTAls(cap_model, order=order, ranks=M.uniform_ranks(cap_model), lam=d["lam"],
                                 sweeps=d["sweeps"], init_scale=0.5, seed=seed)
        elif fam == "CP":
            self.model = M.CP(cap_model, R=max(1, cap_model // 32), lam=d["lam"], sweeps=d["sweeps"], init_scale=0.5, seed=seed)
        else:
            if d["start"] == "correct":
                ab = {world.ax["A"], world.ax["B"]}
                part = next(p for p, (r, _) in enumerate(M.PARTITIONS) if set(r) in (ab, set(range(D)) - ab))
            else:
                part = int(self.rng.integers(3))
            self.model = M.LowRank(cap_model, part=part, R=max(1, cap_model // 128), lam=d["lam"], sweeps=d["sweeps"],
                                   init_scale=0.5, seed=seed)
        self.rep_k = np.full(self.n_rep, -1, dtype=np.int64)
        self.rep_v = np.zeros(self.n_rep)
        self.rep_seen = 0
        self.err_k = np.full(self.n_err, -1, dtype=np.int64)
        self.err_v = np.zeros(self.n_err)
        self.err_age = np.zeros(self.n_err)
        self.cap = C

    def persistent_floats(self):
        return M.audit(self.model, self.actual["cap_model"]) + 2 * self.n_rep + 3 * self.n_err

    def predict(self, a):
        return self.model.predict(a)

    def eval_cost(self):
        return self.model.eval_cost()

    def _pred(self, A):
        return np.array([self.model.predict(a) for a in A])

    def consolidate(self, A, y, sd):
        d, m, rng = self.d, self.model, self.rng
        units = 0.0
        pre = self._pred(A)
        units += len(A) * m.eval_cost()
        surprise = float(np.mean((pre - y) ** 2))
        parts_A, parts_y = [A], [y]
        if self.n_rep and (self.rep_k >= 0).any():
            k = self.rep_k[self.rep_k >= 0]
            parts_A.append(_unpack(k))
            parts_y.append(self.rep_v[self.rep_k >= 0])
        if self.n_err and (self.err_k >= 0).any():
            k = self.err_k[self.err_k >= 0]
            parts_A.append(_unpack(k))
            parts_y.append(self.err_v[self.err_k >= 0])
        nd = int(d["dream_ratio"] * len(y))
        if nd:
            dA = _unpack(rng.integers(N, size=nd))
            parts_A.append(dA)
            parts_y.append(self._pred(dA))
            units += nd * m.eval_cost()
        BA, By = np.vstack(parts_A), np.concatenate(parts_y)
        if d["surprise_alpha"] > 0:
            e = np.abs(self._pred(BA) - By) + 1e-3
            units += len(BA) * m.eval_cost()
            w = e ** d["surprise_alpha"]
            idx = rng.choice(len(By), size=len(By), p=w / w.sum())
            BA, By = BA[idx], By[idx]
        before = _flat(m).copy()
        if d["disturb"] > 0:
            for arr in _param_arrays(m):
                arr += d["disturb"] * (arr.std() + 1e-12) * rng.normal(size=arr.shape)
        units += m.consolidate(BA, By)
        if d["forget"] > 0:
            _param_arrays(m)[-1][...] *= (1 - d["forget"])
        restruct = 0
        if isinstance(m, M.TTAls) and d["p_restruct"] > 0 and rng.random() < d["p_restruct"]:
            restruct, u = self._restructure(A, y)
            units += u
        change = float(np.linalg.norm(_flat(m) - before) / (np.linalg.norm(before) + 1e-12))
        # replay store: reservoir over real samples
        for kk, v in zip(_pack(A), y):
            self.rep_seen += 1
            if self.n_rep == 0:
                break
            if self.rep_seen <= self.n_rep:
                self.rep_k[self.rep_seen - 1], self.rep_v[self.rep_seen - 1] = kk, v
            else:
                j = int(rng.integers(self.rep_seen))
                if j < self.n_rep:
                    self.rep_k[j], self.rep_v[j] = kk, v
        # error store: keep worst unresolved residuals up to `persist` consolidations
        if self.n_err:
            self.err_age[self.err_k >= 0] += 1
            live = self.err_k >= 0
            if live.any():
                r = np.abs(self._pred(_unpack(self.err_k[live])) - self.err_v[live])
                keep = (r > 0.15 * sd) & (self.err_age[live] < d["persist"])
                idx = np.nonzero(live)[0]
                self.err_k[idx[~keep]] = -1
            res = np.abs(self._pred(A) - y)
            units += len(A) * m.eval_cost()
            order = np.argsort(-res)
            free = list(np.nonzero(self.err_k < 0)[0])
            for i in order:
                if not free or res[i] <= 0.15 * sd:
                    break
                j = free.pop(0)
                self.err_k[j], self.err_v[j], self.err_age[j] = _pack(A[i:i + 1])[0], y[i], 0
        return units, surprise, change, restruct

    def _restructure(self, A, y):
        m = self.model
        o = list(m.order)
        i = int(self.rng.integers(D - 1))
        o2 = o[:]
        o2[i], o2[i + 1] = o2[i + 1], o2[i]
        t = m.tt.cores[0]
        for c in m.tt.cores[1:]:
            t = np.tensordot(t, c, axes=([-1], [0]))
        dense_obs = np.transpose(t.reshape([NV] * D), np.argsort(o))  # observed axis order
        cand = M.TTAls(m.cap, order=tuple(o2), ranks=m.ranks, lam=m.lam, sweeps=m.sweeps)
        cores, _ = tt_svd(np.transpose(dense_obs, o2), max_rank=list(m.ranks))
        for k, c in enumerate(cores):
            cand.tt.cores[k][...] = 0.0
            a, n, b = c.shape
            cand.tt.cores[k][:a, :, :b] = c
        units = N * m.tt.n_params()
        e_old = np.mean((self._pred(A) - y) ** 2)
        e_new = np.mean((np.array([cand.predict(a) for a in A]) - y) ** 2)
        if e_new < e_old:
            self.model = cand
            return 1, units
        return 0, units


def effective_ranks(m, tol=1e-2):
    if not isinstance(m, M.TTAls):
        return None
    t = m.tt.cores[0]
    for c in m.tt.cores[1:]:
        t = np.tensordot(t, c, axes=([-1], [0]))
    t = t.reshape([NV] * D)
    out = []
    for k in range(1, D):
        s = np.linalg.svd(t.reshape(NV ** k, -1), compute_uv=False)
        out.append(int((s > tol * s[0]).sum()) if s[0] > 0 else 0)
    return out


# ---------------------------------------------------------------- life

def live_d(world, org, events, econ, trace_every=4, sample_cells=None):
    e = econ
    energy = e["energy0"]
    S = int(org.d["scratch"])
    sA, sy, fill = np.zeros((S, D), dtype=np.int64), np.zeros(S), 0
    comp_e, comp_u = 0.0, 0.0
    n = {k: 0 for k in ("L1", "L2", "L3s", "L3h")}
    ok = dict(n)
    ok2 = {"L2_p2": 0, "n_p2": 0}
    rew = 0.0
    trace, n_cons, restructs = [], 0, 0
    win_ok = win_n = 0
    t = -1
    for t, ev in enumerate(events):
        energy -= e["metabolism"]
        if ev[0] == "obs":
            xf = world.x_new if t >= PHASE2 else world.x_old
            ys = xf[tuple(ev[1].T)] + ev[2] / 0.1 * world.noise
            for a, v in zip(ev[1], ys):
                sA[fill], sy[fill] = a, v
                fill += 1
                if fill == S:
                    if comp_u < e["budget"]:
                        u, surprise, change, rs = org.consolidate(sA.copy(), sy.copy(), world.sd["L1"])
                        comp_u += u
                        comp_e += e["kappa"] * u
                        energy -= e["kappa"] * u
                        restructs += rs
                        n_cons += 1
                        if n_cons % trace_every == 0:
                            cur = world.x_new if t >= PHASE2 else world.x_old
                            yv = cur.reshape(-1)[sample_cells]
                            p = np.array([org.predict(a) for a in world.addr[sample_cells]])
                            r2 = float(1 - ((yv - p) ** 2).sum() / ((yv - yv.mean()) ** 2).sum())
                            trace.append(dict(t=t, cons=n_cons, r2=r2, win_L2=win_ok / win_n if win_n else None,
                                              change=change, surprise=surprise, energy=energy,
                                              ranks=effective_ranks(org.model),
                                              err_fill=int((org.err_k >= 0).sum()), restructs=restructs))
                            win_ok = win_n = 0
                    fill = 0
        else:
            kind = ev[0]
            if kind == "L3":
                a, w, truth, ho = ev[1], ev[2], ev[3], ev[4]
                key = "L3h" if ho else "L3s"
                fa = np.repeat(np.asarray(a)[None, :], NV, 0)
                fa[:, world.ax["D"]] = np.arange(NV)
                ans = float(sum(wi * org.predict(x) for wi, x in zip(w, fa)))
                cost, sd = NV * org.eval_cost(), world.sd["L3"]
            else:
                a, truth, key = ev[1], ev[3], kind
                ans, cost, sd = org.predict(a), org.eval_cost(), world.sd[kind]
            comp_u += cost
            comp_e += e["kappa"] * cost
            energy -= e["kappa"] * cost
            hit = abs(ans - truth) < e["tau"] * sd
            n[key] += 1
            ok[key] += int(hit)
            if key == "L2":
                win_n += 1
                win_ok += int(hit)
                if t >= PHASE2:
                    ok2["n_p2"] += 1
                    ok2["L2_p2"] += int(hit)
            if hit:
                rew += e["reward"]
                energy += e["reward"]
        if energy <= 0:
            break
    cur = world.x_new
    xf = cur.reshape(-1)
    ho = world.heldout_cell
    p = np.array([org.predict(a) for a in world.addr[ho]])
    y = xf[ho]
    r2_final = float(1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum())
    return dict(steps=t + 1, died=bool(energy <= 0), reward=rew, comp_energy=comp_e, U=rew - comp_e,
                comp_units=comp_u, r2_ho=r2_final, mse_ho=float(np.mean((y - p) ** 2)), L2=ok["L2"] / max(n["L2"], 1),
                L2_p2=ok2["L2_p2"] / max(ok2["n_p2"], 1), n_cons=n_cons, restructs=restructs,
                P_used=int(org.persistent_floats()), trace=trace)


# ---------------------------------------------------------------- dial sampling

def sample_dials(rng):
    lu = lambda a, b: float(np.exp(rng.uniform(np.log(a), np.log(b))))
    fam_w = rng.choice(["TT", "MAT", "CP", "NONE"], p=[0.3, 0.3, 0.3, 0.1])
    return dict(
        world_family=str(fam_w), drift=float(rng.uniform(0, 0.6)), noise=float(rng.uniform(0.05, 0.5)),
        kappa_mult=lu(0.25, 4.0),
        lam=lu(0.3, 300), sweeps=int(rng.integers(1, 21)), scratch=int(round(lu(32, 512))), cap=int(round(lu(96, 512))),
        replay_frac=float(rng.uniform(0, 0.5)), dream_ratio=float(rng.uniform(0, 2)),
        surprise_alpha=float(rng.uniform(0, 2)), disturb=float(rng.uniform(0, 0.3)), forget=float(rng.uniform(0, 0.2)),
        err_frac=float(rng.uniform(0, 0.3)), persist=int(rng.integers(1, 21)), p_restruct=float(rng.uniform(0, 1)),
        org_family=str(rng.choice(["TT", "CP", "LR"])), start=str(rng.choice(["correct", "random"])))


def sample_dials_local(rng):
    """PREREG_D3 (final ranges): local random design inside the competent regime."""
    lu = lambda a, b: float(np.exp(rng.uniform(np.log(a), np.log(b))))
    return dict(
        world_family="TT", drift=float(rng.uniform(0, 0.6)), noise=float(rng.uniform(0.05, 0.25)),
        kappa_mult=lu(0.25, 4.0), lam=lu(15, 120), sweeps=int(rng.integers(5, 21)), scratch=int(round(lu(64, 512))),
        cap=int(round(lu(192, 512))), replay_frac=float(rng.uniform(0, 0.3)), dream_ratio=float(rng.uniform(0, 1)),
        surprise_alpha=float(rng.uniform(0, 0.3)), disturb=float(rng.uniform(0, 0.05)), forget=float(rng.uniform(0, 0.1)),
        err_frac=float(rng.uniform(0, 0.15)), persist=int(rng.integers(1, 21)), p_restruct=float(rng.uniform(0, 1)),
        org_family="TT", start=str(rng.choice(["correct", "random"])))


ECON = dict(energy0=400.0, metabolism=0.5, reward=10.0, tau=0.15, kappa=5e-6, budget=3e7, scratch=128)


def run_life(job):
    t0 = time.time()
    d = job["dials"]
    w = WorldD(d["world_family"], job["inst"], d["drift"], d["noise"])
    ev = w.drift_events()
    econ = dict(ECON, kappa=ECON["kappa"] * d["kappa_mult"])
    org = Organism(d, w, job["seed"])
    cells = np.nonzero(w.heldout_cell)[0]
    cells = np.random.default_rng(job["inst"]).choice(cells, size=min(512, len(cells)), replace=False)
    r = live_d(w, org, ev, econ, sample_cells=cells)
    nm = live_e1(w, M.NoMem(0), ev, econ)
    r["U_nomem"] = nm["U"]
    r["EFF"] = (r["U"] - nm["U"]) / max(r["P_used"], 1)
    fire = next((k for k, tr in enumerate(r["trace"]) if tr["r2"] >= 0.5), None)
    r.update(job, **org.actual, fire_idx=fire, status="OK", secs=round(time.time() - t0, 2))
    return r


def run(jobs, out_path, workers=None):
    from concurrent.futures import ProcessPoolExecutor
    for v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(v, "1")
    workers = workers or int(os.environ.get("ENSORAIN_WORKERS", "20"))

    with ProcessPoolExecutor(max_workers=workers) as ex, open(out_path, "a") as f:
        for r in ex.map(_safe_run, jobs, chunksize=1):
            f.write(json.dumps(r, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)) + "\n")
            f.flush()


def _safe_run(job):
    try:
        return run_life(job)
    except Exception as ex:  # a crashed life is a row, not a lost row
        return dict(job, status="ERROR", reason=f"{type(ex).__name__}: {ex}")
