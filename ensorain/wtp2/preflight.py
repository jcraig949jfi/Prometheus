"""WTP-02 necessity preflight N1-N5 (PREREG_WTP02 s2). Cheapest gates first:
N1 (arithmetic), N5 (organism-free dry run), N3/N4 (closed-form planted
learners), N2 (short economy lives). Returns (admitted, record)."""
import numpy as np

from ensorain.wtp.world import build_field, reachable, Illegal
from ensorain.wtp.organism import make_memory
from .world2 import streams, build, mem_cap, run_life


def _r2(p, y):
    return float(1 - ((y - p) ** 2).sum() / (((y - y.mean()) ** 2).sum() + 1e-12))


def planted_panel(x, cap, n, noise_sd, rng):
    """Best held-out R^2 of three planted learners fitted from n noisy samples."""
    dims = list(x.shape)
    cells = x.size
    addr = np.array(np.unravel_index(np.arange(cells), dims)).T
    xf = x.reshape(-1)
    n = int(min(n, cells // 2))
    tr = rng.choice(cells, size=n, replace=False)
    te = np.setdiff1d(np.arange(cells), tr)
    y = xf[tr] + noise_sd * rng.standard_normal(n)
    best = {}
    # additive per-mode means
    pred = np.full(len(te), y.mean())
    for m in range(len(dims)):
        means = np.zeros(dims[m])
        for v in range(dims[m]):
            s = addr[tr, m] == v
            means[v] = y[s].mean() - y.mean() if s.any() else 0.0
        pred = pred + means[addr[te, m]]
    best["additive"] = _r2(pred, xf[te])
    # DCT least squares with the lowest-frequency multi-indices, <= cap and <= n/2 coefficients
    kmax = max(1, min(cap, n // 2))
    freqs = [np.arange(d) for d in dims]
    idx = np.array(np.meshgrid(*freqs, indexing="ij")).reshape(len(dims), -1).T
    idx = idx[np.argsort(idx.sum(1), kind="stable")][:kmax]

    def feats(cells_i):
        F = np.ones((len(cells_i), len(idx)))
        for m, d in enumerate(dims):
            F *= np.cos(np.pi * idx[None, :, m] * (addr[cells_i, m][:, None] + 0.5) / d)
        return F
    Ft = feats(tr)
    w = np.linalg.lstsq(Ft.T @ Ft + 1e-3 * np.eye(len(idx)), Ft.T @ y, rcond=None)[0]
    best["dct"] = _r2(feats(te) @ w, xf[te])
    # low-rank ALS on the most balanced unfolding
    s_best = min(range(1, len(dims)), key=lambda s: abs(np.prod(dims[:s]) - np.prod(dims[s:])))
    rows, cols = int(np.prod(dims[:s_best])), int(np.prod(dims[s_best:]))
    r = max(1, cap // (rows + cols))
    if r * (rows + cols) <= cap:
        I = np.ravel_multi_index(addr[tr, :s_best].T, dims[:s_best])
        J = np.ravel_multi_index(addr[tr, s_best:].T, dims[s_best:])
        U = rng.normal(0, 0.3, (rows, r))
        V = rng.normal(0, 0.3, (cols, r))
        for _ in range(10):
            for i in np.unique(I):
                s = I == i
                U[i] = np.linalg.solve(V[J[s]].T @ V[J[s]] + 1e-2 * np.eye(r), V[J[s]].T @ y[s])
            for j in np.unique(J):
                s = J == j
                V[j] = np.linalg.solve(U[I[s]].T @ U[I[s]] + 1e-2 * np.eye(r), U[I[s]].T @ y[s])
        It = np.ravel_multi_index(addr[te, :s_best].T, dims[:s_best])
        Jt = np.ravel_multi_index(addr[te, s_best:].T, dims[s_best:])
        best["lowrank"] = _r2((U[It] * V[Jt]).sum(1), xf[te])
    return max(best.values()), best


def dry_run(g, S, x, rew, adj, T):
    """Organism-free run of the transition laws (same stream order as run_life)."""
    tr = g["transition"]
    V0 = float(x.var())
    wdyn = S["world_dyn"]
    dims = list(x.shape)
    N = len(adj)
    adj = [set(a) for a in adj]
    min_var, min_reach, min_rew = 1.0, 1.0, 1.0
    drift = {}
    if tr["drift"] > 0:
        for t in range(tr["drift_period"], T, tr["drift_period"]):
            try:
                drift[t] = build_field(g["substrate"], wdyn)
            except Illegal:
                pass
    basis = {t: int(wdyn.integers(len(dims))) for t in range(tr["basis_change_period"], T, tr["basis_change_period"])} \
        if tr["basis_change_period"] else {}
    basis = {t: (m, wdyn.permutation(dims[m])) for t, m in basis.items()}
    rewire = {t: (wdyn.random(N), wdyn.integers(N, size=N)) for t in range(tr["rewire_period"], T, tr["rewire_period"])} \
        if tr["rewire_period"] else {}
    cat_u, cat_m, cat_i = wdyn.random(T), wdyn.integers(len(dims), size=T), wdyn.random(T)
    for t in range(T):
        if t in drift and drift[t][0].shape == x.shape:
            d = tr["drift"]
            x = np.sqrt(1 - d) * x + np.sqrt(d) * drift[t][0]
            rew = np.sqrt(1 - d) * rew + np.sqrt(d) * drift[t][1]
        if t in basis:
            m, perm = basis[t]
            x, rew = np.take(x, perm, axis=m), np.take(rew, perm, axis=m)
        if t in rewire:
            u, tgt = rewire[t]
            for v in range(N):
                if u[v] < tr["rewire_frac"] and adj[v]:
                    adj[v].discard(min(adj[v]))
                    adj[v].add(int(tgt[v]))
        if tr["catastrophe_rate"] > 0 and cat_u[t] < tr["catastrophe_rate"]:
            m = int(cat_m[t])
            sl = [slice(None)] * len(dims)
            sl[m] = int(cat_i[t] * dims[m])
            x = x.copy()
            rew = rew.copy()
            x[tuple(sl)] = 0.0
            rew[tuple(sl)] = 0.0
        if t % max(1, T // 20) == 0:
            min_var = min(min_var, float(x.var() / V0))
            min_reach = min(min_reach, reachable(adj, 0) / N)
            min_rew = min(min_rew, float(np.mean(rew > g["resource"]["theta"])))
    return min_var, min_reach, min_rew


def preflight(g, seed, n2_seeds=2, n2_life=300):
    rec = dict(gate=None)
    S, _ = streams(seed)
    try:
        x, rew, dims, adj, node_cell, _ = build(g, S)
    except Exception as ex:
        return False, dict(gate="BUILD", reason=f"{type(ex).__name__}: {ex}")
    cells = x.size
    cap = mem_cap(g, cells)
    # N1 memory pressure
    try:
        m = make_memory(g["memory"]["substrate"], dims, cap, np.random.default_rng(0))
    except ValueError as ex:
        return False, dict(gate="N1", reason=str(ex), cells=cells, cap=cap)
    if m.n_floats() > 0.25 * cells + 1:
        return False, dict(gate="N1", reason=f"{m.n_floats()} floats > 0.25 x {cells}", cells=cells, cap=cap)
    rec.update(cells=cells, cap=cap, n_floats=m.n_floats())
    # N5 noncollapsed (organism-free)
    T = g["time"]["lifetime"]
    mv, reach, rewarding = dry_run(g, S, x, rew, adj, T)
    rec.update(min_var=mv, dry_reach=reach, rewarding=rewarding)
    if mv < 0.1 or reach < 0.3 or rewarding < 0.01:
        return False, dict(rec, gate="N5")
    # N3 learnable / N4 structure matters
    n = 2 * T
    prng = np.random.default_rng(seed + 777)
    real, panel = planted_panel(x, cap, n, g["observation"]["noise_sd"], prng)
    shuf = x.reshape(-1)[prng.permutation(cells)].reshape(dims)
    fake, _ = planted_panel(shuf, cap, n, g["observation"]["noise_sd"], np.random.default_rng(seed + 778))
    rec.update(planted_r2=real, planted_panel=panel, shuffled_r2=fake)
    if real < 0.10:
        return False, dict(rec, gate="N3")
    if fake > 0.05 or fake > 0.5 * real:
        return False, dict(rec, gate="N4")
    # Economy calibration (addendum A2): income rates with metabolism 0 and ample energy
    import copy
    gz = copy.deepcopy(g)
    gz["resource"]["metabolism"], gz["resource"]["energy0"] = 0.0, 1e9
    Lc = min(T, 600)
    base, orc = [], []
    for k in range(n2_seeds):
        for tw in ("random", "frozen"):
            r = run_life(gz, seed * 10 + k, twin=tw, lifetime=Lc, excursions=False)
            if r["status"] != "OK":
                return False, dict(rec, gate="N2", reason=f"{tw}: {r.get('status')} {r.get('reason') or r.get('degenerate_reason')}")
            base.append(r["U"] / r["steps"])
        r = run_life(gz, seed * 10 + 5 + k, twin="oracle", lifetime=Lc, excursions=False)
        if r["status"] != "OK":
            return False, dict(rec, gate="N2b", reason=f"oracle: {r.get('status')}")
        orc.append(r["U"] / r["steps"])
    bmax, omin = max(base), min(orc)
    gap = omin - bmax
    rec.update(rate_base=base, rate_oracle=orc, gap=gap)
    if omin <= 0 or gap <= 0.02 or gap <= 0.2 * abs(bmax):
        return False, dict(rec, gate="N2c")  # information does not pay enough
    m = max(0.0, bmax + 0.5 * gap)
    g["resource"]["metabolism"] = float(m)
    g["resource"]["calibrated"] = True
    rec["metabolism_calibrated"] = m
    # verification with the calibrated economy (N2: no-learning loses; N2b: oracle wins)
    us = []
    for k in range(n2_seeds):
        for tw in ("random", "frozen"):
            us.append(run_life(g, seed * 10 + k, twin=tw, lifetime=n2_life, excursions=False)["U"])
    rec.update(n2_U=us)
    if max(us) >= 0:
        return False, dict(rec, gate="N2")
    ro = run_life(g, seed * 10 + 9, twin="oracle", lifetime=Lc, excursions=False)
    rec.update(oracle_U=ro.get("U"), oracle_steps=ro.get("steps"))
    if ro.get("status") != "OK" or ro.get("U", -1) <= 0:
        return False, dict(rec, gate="N2b")
    return True, dict(rec, gate="ADMITTED")
