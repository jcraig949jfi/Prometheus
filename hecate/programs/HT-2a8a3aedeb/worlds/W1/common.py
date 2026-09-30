"""Shared machinery for HT-2a8a3aedeb/W1 (see NOTES.md). No arm logic here."""
import os
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np
from scipy.special import logsumexp
from scipy.stats import rankdata, norm

D, N, H = 4, 6, 20
R = (1, 2, 4)
C = (0.5, 2.0)
LAMS = (0.1, 0.3, 1.0, 3.0, 10.0)
SEEDS = tuple(range(10))
TOLS = (1e-6, 1e-3)
LAZY = 0.5


def make_world(seed):
    rng = np.random.default_rng(1000 + seed)
    P = [LAZY * np.eye(N) + (1 - LAZY) * rng.dirichlet(np.ones(N), size=N) for _ in range(D)]
    qi = [rng.uniform(0, 1, N) for _ in range(D)]
    u = [[rng.uniform(0, 1, N) for _ in range(D)] for _ in range(max(R))]
    return {"seed": seed, "P": P, "qi": qi, "u": u}


def outer(vs):
    t = vs[0]
    for v in vs[1:]:
        t = np.multiply.outer(t, v)
    return t


def additive_q(w):
    q = np.zeros((N,) * D)
    for i, v in enumerate(w["qi"]):
        shp = [1] * D
        shp[i] = N
        q = q + v.reshape(shp)
    return q


def make_q(w, r, c):
    q = additive_q(w)
    if c != 0:
        for k in range(r):
            t = outer(w["u"][k])
            q = q + c * t / t.max()
    return q


def shuffle_q(q, seed, r, c):
    rng = np.random.default_rng(5000 + 100 * seed + 10 * r + int(c == 2.0))
    return rng.permutation(q.ravel()).reshape(q.shape)


def solve(q, P, lam):
    """Log-domain linear Bellman. Returns (logz0, V)."""
    logP = [np.log(p) for p in P]
    L = np.zeros((N,) * D)
    for _ in range(H):
        for i in range(D):
            Lm = np.moveaxis(L, i, -1)                       # (...,j)
            Y = logsumexp(logP[i] + Lm[..., None, :], axis=-1)  # (...,a)
            L = np.moveaxis(Y, -1, i)
        L = -q / lam + L
    return L, -lam * L


def tt_bonds(A, eps):
    A = np.asarray(A, dtype=float)
    nrm = np.linalg.norm(A)
    if nrm == 0:
        return [0] * (D - 1)
    delta = eps / np.sqrt(D - 1) * nrm
    Cm = A.reshape(N, -1)
    r = 1
    bonds = []
    for _ in range(D - 1):
        Cm = Cm.reshape(r * N, -1)
        U, S, Vt = np.linalg.svd(Cm, full_matrices=False)
        tail = np.sqrt(np.cumsum((S ** 2)[::-1]))[::-1]  # tail[k] = ||S[k:]||
        rk = len(S)
        for k in range(1, len(S) + 1):
            if k == len(S) or tail[k] <= delta:
                rk = k
                break
        bonds.append(int(rk))
        Cm = S[:rk, None] * Vt[:rk]
        r = rk
    return bonds


def controls(V):
    t = np.tanh((V - V.mean()) / V.std())  # attempt-2 repair: centred (see NOTES.md)
    g = norm.ppf((rankdata(V.ravel(), method="average") - 0.5) / V.size).reshape(V.shape)
    return t, g


def bonds_all(A):
    return {f"{e:g}": max(tt_bonds(A, e)) for e in TOLS}


def z_from_logz(L):
    return np.exp(L - L.max())


def z_diag(z):
    return {"frac_lt_1e300": float((z < 1e-300).mean()), "frac_lt_1e16": float((z < 1e-16).mean()),
            "rel_std": float(z.std() / z.mean())}


def mixing_dist(P):
    out = []
    for p in P:
        w, v = np.linalg.eig(p.T)
        pi = np.real(v[:, np.argmin(abs(w - 1))]); pi = pi / pi.sum()
        out.append(float(np.abs(np.linalg.matrix_power(p, H) - pi[None, :]).max()))
    return out


def planted_rank_r(seed, r, c):
    rng = np.random.default_rng(9000 + 100 * seed + 10 * r + int(c == 2.0))
    return sum(outer([rng.uniform(0.5, 1.5, N) for _ in range(D)]) for _ in range(r))


def measure(q, P, lam):
    """Solve and measure z, V, tanh, quantile bonds for one condition."""
    L, V = solve(q, P, lam)
    z = z_from_logz(L)
    t, g = controls(V)
    return {"z": bonds_all(z), "V": bonds_all(V), "tanh": bonds_all(t), "quant": bonds_all(g),
            "zdiag": z_diag(z)}, V
