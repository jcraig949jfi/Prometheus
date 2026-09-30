"""Self-growing sieve hierarchy agent (M1/M10/M2), stream-agnostic.

Labels: 0 = silent, 1 = prime (non-composite event), 2 = composite.
See NOTES.md R1-R6.
"""
import numpy as np

SILENT, PRIME, COMPOSITE = 0, 1, 2
INF = np.iinfo(np.int32).max


def run_agent(labels, N, kmax=40):
    """labels: int array indexed by n (0..N), entries for n in [2,N] used.
    Returns r_by_K (K=0..kmax), periods (cap kmax), residual masks helper."""
    minlev = np.full(N + 1, INF, dtype=np.int64)   # min index of a firing level
    periods = []
    for n in range(2, N + 1):
        if minlev[n] == INF and labels[n] != SILENT and len(periods) < kmax:
            idx = len(periods)
            periods.append(n)
            seg = minlev[2 * n::n]
            np.minimum(seg, idx, out=seg)
    lab = labels[2:N + 1]
    m = minlev[2:N + 1]
    nonsil = lab != SILENT
    notcomp = lab != COMPOSITE
    r = []
    for K in range(kmax + 1):
        fires = m < K
        resid = nonsil & ((~fires) | (fires & notcomp))
        r.append(int(resid.sum()) / (N - 1))
    return r, periods, m


def run_agent_literal(labels, N, K):
    """Literal per-cap streaming simulation (for the equivalence self-check)."""
    levels = []
    resid = 0
    for n in range(2, N + 1):
        fires = any(n % p == 0 and n > p for p in levels)
        lab = labels[n]
        if lab == SILENT:
            continue
        if not fires:
            resid += 1
            if len(levels) < K:
                levels.append(n)
        elif lab != COMPOSITE:
            resid += 1
    return resid / (N - 1), levels


def self_check(labels_fn, N=3000, caps=(0, 1, 3, 7, 15, 40)):
    labels = labels_fn(N)
    r, periods, _ = run_agent(labels, N)
    for K in caps:
        rl, lv = run_agent_literal(labels, N, K)
        assert abs(rl - r[K]) < 1e-12, (K, rl, r[K])
        assert lv == periods[:K], (K, lv[:5], periods[:5])
    return True
