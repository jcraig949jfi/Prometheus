"""Shared primitives for HT-a9e2ba7618 / W3 (see NOTES.md). No arm logic here."""
import numpy as np
from sklearn.metrics import adjusted_rand_score

N = 1024
N_OSC = 64
N_SCALES = 6
K_SCALES = 3
TAU = 0.5
SIGMA_NOISE = 0.5
KC = 1.6
DT = 0.75
STEPS = 2000
PLV_WINDOW = 1800
PLV_THR = 0.9
SEEDS = list(range(50))
WIDTH_RANGES = [(40, 70), (90, 140), (160, 240)]
TAPER = 8
X_OSC = 8 + 16 * np.arange(N_OSC)

PARAMS = dict(N=N, N_OSC=N_OSC, N_SCALES=N_SCALES, K_SCALES=K_SCALES, TAU=TAU,
              SIGMA_NOISE=SIGMA_NOISE, KC=KC, DT=DT, STEPS=STEPS,
              PLV_WINDOW=PLV_WINDOW, PLV_THR=PLV_THR, WIDTH_RANGES=WIDTH_RANGES,
              TAPER=TAPER, freqs="perm linspace(-1,1,64)", repair=1, wavelet="a trous B3-spline smoothing planes j=1..6")


def _plateau(start, width):
    env = np.zeros(N)
    t = np.arange(N)
    env[(t >= start) & (t < start + width)] = 1.0
    for k in range(TAPER):
        v = 0.5 - 0.5 * np.cos(np.pi * (k + 0.5) / TAPER)
        if 0 <= start + k < N:
            env[start + k] = v
        if 0 <= start + width - 1 - k < N:
            env[start + width - 1 - k] = v
    return env


def make_objects(rng, min_gap, margin):
    """Return (clean signal, list of envelopes, list of (start,width))."""
    widths = [int(rng.integers(a, b + 1)) for a, b in WIDTH_RANGES]
    rng.shuffle(widths)
    for _ in range(10000):
        starts = sorted(int(rng.integers(margin, N - margin - w + 1)) for w in widths)
        # starts sorted independently of widths -> reassign widths in order
        ok = True
        spans = list(zip(starts, widths))
        for (s1, w1), (s2, _) in zip(spans, spans[1:]):
            if s2 - (s1 + w1) < min_gap:
                ok = False
                break
        if ok and spans[-1][0] + spans[-1][1] <= N - margin:
            envs = [_plateau(s, w) for s, w in spans]
            return np.sum(envs, axis=0), envs, spans
    raise RuntimeError("placement failed")


def ground_truth(envs):
    lab = np.arange(N_OSC) + 100  # singletons for background
    for m, e in enumerate(envs):
        inside = e[X_OSC] > 0.5
        lab[inside] = m
    return lab


def pink_noise(rng):
    w = rng.standard_normal(N)
    F = np.fft.rfft(w)
    f = np.fft.rfftfreq(N)
    scale = np.zeros_like(f)
    scale[1:] = 1.0 / np.sqrt(f[1:])
    x = np.fft.irfft(F * scale, n=N)
    x -= x.mean()
    return SIGMA_NOISE * x / x.std()


def phase_surrogate(x, rng):
    F = np.fft.rfft(x)
    ph = rng.uniform(0, 2 * np.pi, F.shape)
    G = np.abs(F) * np.exp(1j * ph)
    G[0] = F[0]
    if N % 2 == 0:
        G[-1] = F[-1]
    return np.fft.irfft(G, n=N)


def scale_stack(x):
    h = np.array([1, 4, 6, 4, 1], float) / 16.0
    c = x.astype(float)
    out = []
    pad = 2 ** N_SCALES * 2 + 8
    for j in range(1, N_SCALES + 1):
        step = 2 ** (j - 1)
        cp = np.pad(c, pad, mode="symmetric")
        new = np.zeros_like(c)
        for k, hk in zip(range(-2, 3), h):
            new += hk * cp[pad + k * step: pad + k * step + N]
        c = new
        out.append(c)
    return np.array(out)  # (6, N)


def components(stack):
    """Per scale, component id of each oscillator (-1 if not in superlevel set)."""
    ids = np.full((stack.shape[0], N_OSC), -1)
    for j, c in enumerate(stack):
        mask = c > TAU
        starts = np.concatenate([[mask[0]], mask[1:] & ~mask[:-1]])
        run = np.cumsum(starts)
        lab = np.where(mask, run, -1)
        ids[j] = lab[X_OSC]
    return ids


def cross_scale_graph(ids, k=K_SCALES):
    same = np.zeros((N_OSC, N_OSC), int)
    for row in ids:
        same += ((row[:, None] == row[None, :]) & (row[:, None] >= 0)).astype(int)
    A = (same >= k).astype(int)
    np.fill_diagonal(A, 0)
    return A


def single_scale_graph(ids, j=0):
    row = ids[j]
    A = ((row[:, None] == row[None, :]) & (row[:, None] >= 0)).astype(int)
    np.fill_diagonal(A, 0)
    return A


def n_edges(A):
    return int(np.triu(A, 1).sum())


def match_edge_count(A, target, rng):
    A = A.copy()
    iu = np.triu_indices(N_OSC, 1)
    cur = A[iu]
    e = int(cur.sum())
    if e > target:
        on = np.flatnonzero(cur == 1)
        drop = rng.choice(on, e - target, replace=False)
        cur[drop] = 0
    elif e < target:
        off = np.flatnonzero(cur == 0)
        add = rng.choice(off, target - e, replace=False)
        cur[add] = 1
    B = np.zeros_like(A)
    B[iu] = cur
    return B + B.T


def graph_components(A):
    from scipy.sparse.csgraph import connected_components
    return connected_components(A, directed=False)[1]


def kuramoto_clusters(A, rng):
    w = rng.permutation(np.linspace(-1.0, 1.0, N_OSC))
    th = rng.uniform(0, 2 * np.pi, N_OSC)
    deg = A.sum(1).astype(float)
    g = np.where(deg > 0, KC / np.maximum(deg, 1), 0.0)
    Af = A.astype(float)

    def f(t):
        s, c = np.sin(t), np.cos(t)
        return w + g * (c * (Af @ s) - s * (Af @ c))

    Z = np.zeros((PLV_WINDOW, N_OSC), complex)
    for step in range(STEPS):
        k1 = f(th)
        k2 = f(th + 0.5 * DT * k1)
        k3 = f(th + 0.5 * DT * k2)
        k4 = f(th + DT * k3)
        th = th + DT / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        if step >= STEPS - PLV_WINDOW:
            Z[step - (STEPS - PLV_WINDOW)] = np.exp(1j * th)
    plv = np.abs(Z.conj().T @ Z) / PLV_WINDOW
    P = (plv > PLV_THR).astype(int)
    np.fill_diagonal(P, 0)
    return graph_components(P)


def ari(pred, truth):
    return float(adjusted_rand_score(truth, pred))


def degree_hist(A):
    return np.bincount(A.sum(1), minlength=1).tolist()


def noisy_signal(seed):
    """Signal generator shared by NULL_TWIN (phase 1) and later arms: 3 objects + 1/f noise."""
    rng = np.random.default_rng(1000 + seed)
    clean, envs, spans = make_objects(rng, min_gap=32, margin=32)
    return clean + pink_noise(rng), envs, spans


def clean_separated_signal(seed):
    rng = np.random.default_rng(5000 + seed)
    clean, envs, spans = make_objects(rng, min_gap=128, margin=64)
    return clean, envs, spans
