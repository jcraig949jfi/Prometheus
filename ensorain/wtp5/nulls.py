"""WTP-05 null ladder (PREREG_WTP05 s5). Cheap competitors first, always.

All nulls are fitted IN HINDSIGHT on training blocks of a world (favourable to the null) and scored on
held-out blocks, at every scored gate. Each null is the better of a lookup (majority vote per discretised
feature key) and a ridge-linear readout, chosen on a validation split.

  N0  constant         best constant action per gate format
  N1  reactive         current observation only
  N2  short history    last k observations, k in {2, 3, 4} (best k)
  N3  bounded memory   fixed heuristic register: current obs + the payload and tag of the most recent event
  N4  Ensorain menu    WTP-03 memory substrates (table, additive, lowrank, cp, tt, dct) regressing the action
                       on a ternary window tensor index (k = 2), online, at their WTP-03 recipes
  N5  short planner    actions never change observations in these worlds, so a 1-step planner equals N1
                       (reported as N1; recorded, not re-implemented)
  N6  batch reference  ridge on the FULL episode history plus all pairwise products (unbounded memory;
                       a reference, not a bounded competitor, and not used for admission)
"""
import numpy as np

from .worlds import F1, F2

FMT = (F1, F2, 6)       # gate-format channels (f1, f2, fG)


def collect(world, rng, n_blocks, life=True):
    """Simulate n_blocks blocks (a fresh life every world.L blocks). Returns rows of scored gates."""
    rows = []
    b = 0
    while b < n_blocks:
        world.new_life(rng)
        for lb in range(world.L):
            if b >= n_blocks:
                break
            ep = world.block(world.K, rng, lb)
            ks, ts = np.nonzero(ep["wt"] > 0)
            for k, t in zip(ks, ts):
                rows.append((ep["obs"][k], int(t), float(ep["tgt"][k, t]), int(ep["role"][k, t])))
            b += 1
    return rows


def _feat(rows, kind, k=1):
    X = []
    for obs, t, _, _ in rows:
        if kind == "window":
            win = [obs[t - j] if t - j >= 0 else np.zeros(obs.shape[1]) for j in range(k)]
            X.append(np.concatenate(win))
        elif kind == "latch":
            ev = [s for s in range(t) if obs[s, F1] > 0.5]
            last = obs[ev[-1], :6] if ev else np.zeros(6)
            X.append(np.concatenate([obs[t], last]))
        elif kind == "full":
            X.append(obs[:t + 1].reshape(-1) if t + 1 == obs.shape[0] else np.concatenate([obs[:t + 1].reshape(-1), np.zeros((obs.shape[0] - t - 1) * obs.shape[1])]))
    return np.array(X)


def _keys(X):
    D = np.sign(np.round(X, 6)).astype(int) + 1
    return [bytes(r.astype(np.int8)) for r in D]


def _lookup(Xtr, ytr, Xte):
    from collections import defaultdict
    tab = defaultdict(float)
    for key, y in zip(_keys(Xtr), ytr):
        tab[key] += y
    glob = 1.0 if ytr.sum() >= 0 else -1.0
    return np.array([np.sign(tab[k]) if tab.get(k, 0) != 0 else glob for k in _keys(Xte)])


def _ridge(Xtr, ytr, Xte, lam=1e-2):
    A = np.hstack([Xtr, np.ones((len(Xtr), 1))])
    w = np.linalg.solve(A.T @ A + lam * np.eye(A.shape[1]), A.T @ ytr)
    p = np.hstack([Xte, np.ones((len(Xte), 1))]) @ w
    return np.where(p >= 0, 1.0, -1.0)


def _quad(X):
    iu = np.triu_indices(X.shape[1], 1)
    return np.hstack([X, (X[:, :, None] * X[:, None, :])[:, iu[0], iu[1]]])


def _best(Xtr, ytr, Xva, yva, Xte, models=("lookup", "ridge")):
    best, bacc = None, -1
    for m in models:
        f = _lookup if m == "lookup" else _ridge
        acc = float((f(Xtr, ytr, Xva) == yva).mean())
        if acc > bacc:
            best, bacc = m, acc
    f = _lookup if best == "lookup" else _ridge
    Xall, yall = np.vstack([Xtr, Xva]), np.concatenate([ytr, yva])
    return f(Xall, yall, Xte), best


def _menu(rows_tr, rows_te, k=2, cap=1024):
    """N4: WTP-03 substrates on a ternary window tensor index."""
    from ensorain.wtp3.collider import make, RULE
    Xtr, Xte = _feat(rows_tr, "window", k), _feat(rows_te, "window", k)
    keep = [j for j in range(Xtr.shape[1]) if (j % 8) not in (7,)]           # drop the constant bias channel
    Atr = (np.sign(np.round(Xtr[:, keep], 6)) + 1).astype(int)
    Ate = (np.sign(np.round(Xte[:, keep], 6)) + 1).astype(int)
    dims = [3] * Atr.shape[1]
    ytr = np.array([r[2] for r in rows_tr])
    out = {}
    for kind in ("table", "additive", "lowrank", "cp", "tt", "dct"):
        try:
            mem = make(kind, dims, cap, np.random.default_rng(0))
            if mem.n_floats() > cap:
                continue
            rule, lr, passes = RULE.get(kind, ("nlms", 0.5, 1))
            for _ in range(passes):
                for i in range(0, len(ytr), 64):
                    mem.learn(Atr[i:i + 64], ytr[i:i + 64], rule, lr)
            out[kind] = np.where(mem.predict(Ate) >= 0, 1.0, -1.0)
        except (ValueError, MemoryError, IndexError) as ex:
            out[kind] = None
    return out


def ladder(world, seed, n_train=48, n_val=16, n_test=32):
    """-> dict: per null, per role accuracy on held-out gates, plus the scored-gate accuracy 'final'."""
    rng = np.random.default_rng(seed)
    tr, va, te = collect(world, rng, n_train), collect(world, rng, n_val), collect(world, rng, n_test)
    y = {n: np.array([r[2] for r in rows]) for n, rows in (("tr", tr), ("va", va), ("te", te))}
    role_te = np.array([r[3] for r in te])
    preds = {}
    # N0: constant per gate format
    fmt = lambda rows: _feat(rows, "window", 1)[:, list(FMT)]
    preds["N0_const"] = _lookup(fmt(tr), y["tr"], fmt(te))
    p, m = _best(_feat(tr, "window", 1), y["tr"], _feat(va, "window", 1), y["va"], _feat(te, "window", 1))
    preds["N1_reactive"] = p
    bestk, bp, bacc = None, None, -1
    for k in (2, 3, 4):
        p, _ = _best(_feat(tr, "window", k), y["tr"], _feat(va, "window", k), y["va"], _feat(te, "window", k))
        acc = (p == y["te"]).mean()            # k chosen on test is favourable to the null (disclosed)
        if acc > bacc:
            bestk, bp, bacc = k, p, acc
    preds["N2_short_history"] = bp
    p, _ = _best(_feat(tr, "latch"), y["tr"], _feat(va, "latch"), y["va"], _feat(te, "latch"))
    preds["N3_bounded_memory"] = p
    menu = _menu(tr + va, te)
    menu = {k: v for k, v in menu.items() if v is not None}
    if menu:
        kbest = max(menu, key=lambda k: (menu[k] == y["te"]).mean())
        preds["N4_menu"] = menu[kbest]
    Xf = lambda rows: _quad(_feat(rows, "full")[:, [j for j in range(world.T * 8) if j % 8 not in (7,)]]) if world.T <= 16 else None
    if world.family != "C":
        preds["N6_batch_full_quadratic"] = _ridge(np.vstack([Xf(tr), Xf(va)]), np.concatenate([y["tr"], y["va"]]), Xf(te), lam=1.0)
    out = {}
    for name, p in preds.items():
        d = dict(scored=float((p == y["te"]).mean()))
        for rl in np.unique(role_te):
            d[f"role{rl}"] = float((p[role_te == rl] == y["te"][role_te == rl]).mean())
        out[name] = d
    out["_meta"] = dict(n_test_gates=int(len(te)), N2_k=bestk, N4_best=kbest if menu else None)
    return out
