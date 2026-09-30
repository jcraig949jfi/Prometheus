"""HT-37e311ce05 / W1: CS benefit curve vs free-riding in pooled row budgets.
See IMPLEMENTATION_NOTES.md for every reading of the spec."""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import json, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "rows.jsonl")
ATTEMPTS = os.path.join(HERE, "attempts.json")

P = dict(n=100, k=8, omp_trials=40, m_table_max=120, N=100, generations=500,
         mut_m=0.05, flip=0.01, c=0.005, m_max=60, table_seed=12345,
         omp_tol=1e-4)


def omp(A, y, k):
    m, n = A.shape
    r = y.copy(); S = []; coef = np.zeros(0)
    for _ in range(min(k, m)):
        j = int(np.argmax(np.abs(A.T @ r)))
        if j not in S:
            S.append(j)
        coef, *_ = np.linalg.lstsq(A[:, S], y, rcond=None)
        r = y - A[:, S] @ coef
    x = np.zeros(n)
    if S:
        x[S] = coef
    return x


def omp_table():
    rng = np.random.default_rng(P["table_seed"])
    n, k = P["n"], P["k"]
    tab = np.zeros(P["m_table_max"] + 1)
    for m in range(P["m_table_max"] + 1):
        if m == 0:
            continue
        s = 0
        for _ in range(P["omp_trials"]):
            A = rng.standard_normal((m, n)); A /= np.linalg.norm(A, axis=0)
            x = np.zeros(n); sup = rng.choice(n, k, replace=False)
            x[sup] = rng.standard_normal(k)
            xh = omp(A, A @ x, k)
            s += np.linalg.norm(xh - x) / np.linalg.norm(x) < P["omp_tol"]
        tab[m] = s / P["omp_trials"]
    return tab


def null_table(cs):
    M = len(cs) - 1
    ramp = cs[0] + (cs[M] - cs[0]) * np.arange(M + 1) / M
    target = cs.mean()
    f = lambda a: np.clip(ramp * a, 0, 1).mean() - target
    lo, hi = 0.0, 1.0
    while f(hi) < 0 and hi < 1e6:
        hi *= 2
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return np.clip(ramp * hi, 0, 1), hi


def evolve(tab, seed):
    rng = np.random.default_rng(seed)
    N, c, mmax = P["N"], P["c"], P["m_max"]
    m = rng.integers(0, mmax + 1, N)
    pool = rng.random(N) < 0.5
    last = None
    for g in range(P["generations"]):
        perm = rng.permutation(N); a, b = perm[0::2], perm[1::2]
        both = pool[a] & pool[b]
        tot = m[a] + m[b]
        succ = np.empty(N)
        succ[a] = np.where(both, tab[tot], tab[m[a]])
        succ[b] = np.where(both, tab[tot], tab[m[b]])
        fit = succ - c * m
        last = dict(f_pool=float(pool.mean()),
                    T=float(tot[both].mean()) if both.any() else None,
                    n_pool_pairs=int(both.sum()),
                    mean_success=float(succ.mean()),
                    mean_m=float(m.mean()),
                    pool_pair_totals=[int(t) for t in tot[both]])
        if g == P["generations"] - 1:
            break  # observables taken from the final generation's pairing
        w = np.maximum(fit, 0.0)
        w = w / w.sum() if w.sum() > 0 else np.full(N, 1.0 / N)
        idx = rng.choice(N, N, p=w)
        m, pool = m[idx].copy(), pool[idx].copy()
        mu = rng.random(N) < P["mut_m"]
        m = np.clip(m + mu * rng.choice([-1, 1], N), 0, mmax)
        pool = pool ^ (rng.random(N) < P["flip"])
    return last


def main():
    att = 1
    if os.path.exists(ATTEMPTS):
        with open(ATTEMPTS) as fh:
            att = json.load(fh)["attempts"] + 1
    with open(ATTEMPTS, "w") as fh:
        json.dump({"attempts": att}, fh)
    t0 = time.process_time()
    cs = omp_table()
    nt, alpha = null_table(cs)
    mstar = int(np.argmax(cs >= 0.5)) if (cs >= 0.5).any() else None
    step = (np.arange(len(cs)) >= mstar).astype(float)
    t_table = time.process_time() - t0
    tables = {"TREATMENT": cs, "CONTROL": nt, "NULL_TWIN": nt, "POSITIVE_CONTROL": step}
    seeds = {"TREATMENT": range(10), "CONTROL": range(10),
             "NULL_TWIN": range(1000, 1010), "POSITIVE_CONTROL": range(10)}
    common = dict(params=P, attempt=att, m_star=mstar,
                  cs_table=[round(float(v), 4) for v in cs],
                  null_table=[round(float(v), 4) for v in nt], null_alpha=alpha,
                  cs_mean=float(cs.mean()), null_mean=float(nt.mean()),
                  null_endpoints=[float(nt[0]), float(nt[-1])],
                  cs_endpoints=[float(cs[0]), float(cs[-1])],
                  table_cpu_s=t_table)
    with open(ROWS, "w") as fh:
        for arm in ["TREATMENT", "CONTROL", "NULL_TWIN", "POSITIVE_CONTROL"]:
            for s in seeds[arm]:
                obs = evolve(tables[arm], s)
                row = dict(arm=arm, seed=s, **obs, **common,
                           cpu_s_cumulative=time.process_time() - t0)
                fh.write(json.dumps(row) + "\n"); fh.flush()
        for s in range(10):
            row = dict(arm="CHEAT", seed=s, f_pool=1.0, T=float(mstar),
                       n_pool_pairs=50, mean_success=1.0, mean_m=None,
                       pool_pair_totals=None, **common,
                       cheat_note="observables injected; no dynamics run",
                       cpu_s_cumulative=time.process_time() - t0)
            fh.write(json.dumps(row) + "\n"); fh.flush()


if __name__ == "__main__":
    main()
