"""W6 controls (HT-55162c0ac0, P3v2). POSITIVE_CONTROL, CHEAT, NULL_TWIN only.

No treatment code: the treatment setting (global leak EPS_G_TREAT > 0 with
group-structured product coupling) is NOT run here. Rows ->
control_rows.jsonl, flushed per row.

World: N = 12 units v_i in [-1, 1], nominal partition into G = 4 groups of 3.
    v_i' = (1 - KAPPA - eps_g) T(v_i) + KAPPA * v_p(i) * v_q(i) + eps_g * mean_j T(v_j)
T(v) = 4 v^3 - 3 v (odd Chebyshev map, chaotic, symmetric invariant density).
p(i), q(i) are unit i's two interaction partners (product = XOR-like
coupling: zero first-order correlation between partners).

Readouts (identical for every arm):
  FTLE grouping: perturb unit i by DELTA at K base times, iterate TAU steps,
  D_ij = mean log10(|dv_j| + 1e-18); similarity D + D^T; average linkage
  into G clusters; ARI against the nominal partition.
  Correlation grouping: max(|corr lag 0|, |corr lag 1| both directions) on an
  L-step trajectory; same clustering; ARI against the nominal partition.

POSITIVE_CONTROL (effect present by construction): partners = the other two
members of the unit's group, eps_g = 0: perturbations can only travel inside
groups, so FTLE grouping recovers the partition by construction, while the
product coupling leaves correlations near zero.
CHEAT: POSITIVE_CONTROL rows with the FTLE partition replaced by the nominal
partition (success injected into the observable).
NULL_TWIN_NOLEAK: as NULL_TWIN with eps_g = 0 (matches the positive control).
NULL_TWIN: same KAPPA, same in-degree 2, same map, eps_g = EPS_G_TWIN, but
partners drawn uniformly at random from all other units (group structure
destroyed); the nominal partition is still the scoring target.
"""
import json, os, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "control_rows.jsonl")

N, G = 12, 4
KAPPA = 0.10
EPS_G_PC = 0.0
EPS_G_TWIN = 0.05          # = treatment eps_g (spec)
DELTA = 1e-9
TAU = 8
K = 100
SPACING = 20
BURN = 500
L = 5000
SEEDS = list(range(10))
CLAUSES = [("S1", "ari_ftle_mean", ">=", 0.8), ("S2", "ari_gap_mean", ">=", 0.5)]

LABELS = np.repeat(np.arange(G), N // G)


def T(v):
    return 4.0 * v ** 3 - 3.0 * v


def group_partners():
    P = np.zeros((N, 2), dtype=int)
    for i in range(N):
        mates = [j for j in range(N) if LABELS[j] == LABELS[i] and j != i]
        P[i] = mates
    return P


def random_partners(rng):
    P = np.zeros((N, 2), dtype=int)
    for i in range(N):
        P[i] = rng.choice([j for j in range(N) if j != i], size=2, replace=False)
    return P


def step(V, P, eps_g):
    """V: (..., N)."""
    TV = T(V)
    return (1.0 - KAPPA - eps_g) * TV + KAPPA * V[..., P[:, 0]] * V[..., P[:, 1]] \
        + eps_g * TV.mean(axis=-1, keepdims=True)


def trajectory(v0, P, eps_g, n):
    out = np.empty((n, N))
    v = v0.copy()
    for t in range(n):
        v = step(v, P, eps_g)
        out[t] = v
    return out


def ftle_matrix(traj, P, eps_g):
    base = traj[BURN + SPACING * np.arange(K)]            # (K, N)
    ref = base.copy()
    pert = np.repeat(base[:, None, :], N, axis=1)          # (K, N_pert, N)
    idx = np.arange(N)
    pert[:, idx, idx] += DELTA
    for _ in range(TAU):
        ref = step(ref, P, eps_g)
        pert = step(pert, P, eps_g)
    d = np.abs(pert - ref[:, None, :])                     # (K, i, j)
    return np.log10(d + 1e-18).mean(axis=0)


def corr_matrix(traj):
    X = traj[BURN:]
    X = (X - X.mean(0)) / X.std(0)
    n = X.shape[0]
    c0 = np.abs(X.T @ X / n)
    c1 = np.abs(X[1:].T @ X[:-1] / (n - 1))
    return np.maximum(c0, np.maximum(c1, c1.T))


def average_linkage(S, k):
    """agglomerative average linkage on similarity S (higher = closer)."""
    clusters = [[i] for i in range(S.shape[0])]
    while len(clusters) > k:
        best, bi, bj = -np.inf, 0, 1
        for a in range(len(clusters)):
            for b in range(a + 1, len(clusters)):
                s = S[np.ix_(clusters[a], clusters[b])].mean()
                if s > best:
                    best, bi, bj = s, a, b
        clusters[bi] = clusters[bi] + clusters[bj]
        del clusters[bj]
    lab = np.empty(S.shape[0], dtype=int)
    for c, members in enumerate(clusters):
        lab[members] = c
    return lab


def ari(a, b):
    from math import comb
    a = np.asarray(a); b = np.asarray(b)
    ua, ub = np.unique(a), np.unique(b)
    M = np.array([[np.sum((a == x) & (b == y)) for y in ub] for x in ua])
    s_ij = sum(comb(int(v), 2) for v in M.ravel())
    s_a = sum(comb(int(v), 2) for v in M.sum(1))
    s_b = sum(comb(int(v), 2) for v in M.sum(0))
    n2 = comb(len(a), 2)
    exp = s_a * s_b / n2
    mx = 0.5 * (s_a + s_b)
    return 0.0 if mx == exp else float((s_ij - exp) / (mx - exp))


def run_arm(arm, seed, P, eps_g):
    rng = np.random.default_rng(seed)
    v0 = rng.uniform(-1, 1, N)
    traj = trajectory(v0, P, eps_g, BURN + max(L, SPACING * K + TAU + 1))
    D = ftle_matrix(traj, P, eps_g)
    Sf = D + D.T
    np.fill_diagonal(Sf, np.nan)
    Sf = np.where(np.isnan(Sf), np.nanmax(Sf), Sf)
    part_f = average_linkage(Sf, G)
    C = corr_matrix(traj)
    part_c = average_linkage(C, G)
    off = ~np.eye(N, dtype=bool)
    same = (LABELS[:, None] == LABELS[None, :]) & off
    return {"arm": arm, "seed": seed, "eps_g": eps_g, "kappa": KAPPA,
            "partners": P.tolist(),
            "partition_ftle": part_f.tolist(), "partition_corr": part_c.tolist(),
            "ari_ftle": ari(part_f, LABELS), "ari_corr": ari(part_c, LABELS),
            "ftle_within_mean": float(D[same].mean()), "ftle_between_mean": float(D[off & ~same].mean()),
            "corr_within_mean": float(C[same].mean()), "corr_between_mean": float(C[off & ~same].mean()),
            "traj_min": float(traj.min()), "traj_max": float(traj.max())}


def summarize(rows):
    f = np.array([r["ari_ftle"] for r in rows]); c = np.array([r["ari_corr"] for r in rows])
    return {"n": len(rows), "ari_ftle_mean": float(f.mean()), "ari_corr_mean": float(c.mean()),
            "ari_gap_mean": float((f - c).mean()), "ari_ftle_min": float(f.min()),
            "ari_corr_max": float(c.max())}


def clause_pass(s):
    res = {cid: bool(s[key] >= thr) for cid, key, cmp, thr in CLAUSES}
    res["all"] = all(res.values())
    return res


def main():
    t0 = time.process_time()
    f = open(OUT, "w", encoding="utf-8")

    def emit(r):
        f.write(json.dumps(r) + "\n"); f.flush()

    Pg = group_partners()
    pc, cheat, twin = [], [], []
    for sd in SEEDS:
        r = run_arm("POSITIVE_CONTROL", sd, Pg, EPS_G_PC); pc.append(r); emit(r)
        c = dict(r); c["arm"] = "CHEAT"; c["partition_ftle"] = LABELS.tolist()
        c["ari_ftle"] = ari(LABELS, LABELS); cheat.append(c); emit(c)
    for sd in SEEDS:
        Pr = random_partners(np.random.default_rng(500 + sd))
        r = run_arm("NULL_TWIN", sd, Pr, EPS_G_TWIN); twin.append(r); emit(r)
    twin0 = []
    for sd in SEEDS:
        Pr = random_partners(np.random.default_rng(500 + sd))
        r = run_arm("NULL_TWIN_NOLEAK", sd, Pr, EPS_G_PC); twin0.append(r); emit(r)
    S = {"POSITIVE_CONTROL": summarize(pc), "CHEAT": summarize(cheat), "NULL_TWIN": summarize(twin),
         "NULL_TWIN_NOLEAK": summarize(twin0)}
    summary = {"arm": "SUMMARY", **S, "clauses": {k: clause_pass(v) for k, v in S.items()},
               "params": {"N": N, "G": G, "KAPPA": KAPPA, "EPS_G_PC": EPS_G_PC, "EPS_G_TWIN": EPS_G_TWIN,
                          "DELTA": DELTA, "TAU": TAU, "K": K, "L": L, "seeds": SEEDS},
               "cpu_seconds": time.process_time() - t0}
    emit(summary); f.close()
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
