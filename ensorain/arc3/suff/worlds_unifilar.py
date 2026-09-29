"""Held-out world family for T25: random binary UNIFILAR machines (known epsilon-machine-like HMMs).

random_unifilar(S, seed):
- each state i emits 1 with prob p_i ~ Beta(0.5, 0.5) and moves deterministically to delta(i, x), which is uniform
  random over the states;
- it is resampled until the transition graph (edges with emission prob > 1e-3) is strongly connected, so the
  stationary distribution is unique.
Bayes = forward filtering with the known machine (worlds.HMMWorld). Not guaranteed minimal: the causal-state count is
<= S. The excess metric does not need minimality."""
import numpy as np

from ensorain.arc3.suff.worlds import HMMWorld


def _strongly_connected(adj):
    S = len(adj)
    def reach(a):
        seen, st = {0}, [0]
        while st:
            u = st.pop()
            for v in range(S):
                if a[u][v] and v not in seen:
                    seen.add(v); st.append(v)
        return len(seen) == S
    return reach(adj) and reach([[adj[j][i] for j in range(S)] for i in range(S)])


def random_unifilar(S, seed):
    rng = np.random.default_rng(seed)
    while True:
        p = rng.beta(0.5, 0.5, S)
        d = rng.integers(0, S, (S, 2))
        T0, T1 = np.zeros((S, S)), np.zeros((S, S))
        adj = [[False] * S for _ in range(S)]
        for i in range(S):
            T0[i, d[i, 0]] += 1 - p[i]
            T1[i, d[i, 1]] += p[i]
            if 1 - p[i] > 1e-3: adj[i][d[i, 0]] = True
            if p[i] > 1e-3: adj[i][d[i, 1]] = True
        if _strongly_connected(adj):
            tot = T0 + T1
            w, v = np.linalg.eig(tot.T)
            st = np.real(v[:, np.argmin(np.abs(w - 1))]); st = st / st.sum()
            return HMMWorld(f"U{S}_s{seed}", [T0, T1], st, causal_states=S)
