"""T25: EM refinement initialized from the split-CSSR machine (S proposed by CSSR, not fixed; soft belief tracking).

At each refit:
- fit split-CSSR on x[:t];
- turn its deterministic machine into an emission-labelled HMM, Tm[x][i, trans[i][x]] = P(x | i), smoothed toward
  uniform by eps so that EM can move transition mass;
- run n_iter Baum-Welch iterations (hmm_learner._em) on x[:t];
- predict online with the forward filter.
Undefined CSSR transitions are spread uniformly. Persistent memory follows the HMM_EM convention."""
import numpy as np

from ensorain.arc3.suff.cssr import CSSR
from ensorain.arc3.suff.hmm_learner import _em, _normalize_rows


class CSSR_EM:
    def __init__(self, Lmax=6, alpha=1e-3, refit=1000, n_iter=10, eps=0.01):
        self.Lmax, self.alpha, self.refit, self.it, self.eps = Lmax, alpha, refit, n_iter, eps
        self.name = f"CSSR_EM_L{Lmax}"

    def _init(self, m):
        S = len(m.counts)
        Tm = [np.zeros((S, S)), np.zeros((S, S))]
        for i in range(S):
            n0, n1 = m.counts[i]
            p1 = (n1 + 0.5) / (n0 + n1 + 1.0)
            for x, px in ((0, 1 - p1), (1, p1)):
                j = m.trans[i][x]
                if j is None:
                    Tm[x][i, :] += px / S
                else:
                    Tm[x][i, j] += px
        U = 1.0 / (2 * S)
        Tm = [(1 - self.eps) * Tm[x] + self.eps * U for x in (0, 1)]
        return S, _normalize_rows(Tm)

    def run(self, x):
        x = np.asarray(x, int)
        T = len(x)
        P = np.full((T, 2), 0.5)
        Tm, b, S, c0 = None, None, 0, [0, 0]
        for t in range(T):
            if t > 0 and t % self.refit == 0:
                m = CSSR(Lmax=self.Lmax, alpha=self.alpha, mode="split").fit([int(v) for v in x[:t]])
                S, Tm = self._init(m)
                Tm = self._fit(x[:t], S) if Tm is None else _em(x[:t], S, Tm, self.it)[0]
                b = np.full(S, 1.0 / S)
                for s in x[:t]:
                    b = b @ Tm[s]
                    b = b / max(b.sum(), 1e-300)
            if Tm is not None:
                pe = np.array([b @ Tm[0].sum(1), b @ Tm[1].sum(1)])
                P[t] = pe / pe.sum()
                b = b @ Tm[x[t]]
                b = b / max(b.sum(), 1e-300)
            else:
                p = (c0[1] + 0.5) / (c0[0] + c0[1] + 1.0)
                P[t] = [1 - p, p]
            c0[x[t]] += 1
        return P, dict(bits=float(T + 2 * S * S * 32 + S * 32), query_ops=float(S * S), states=S)


class RAND_EM(CSSR_EM):
    """Q2 ablation: the SAME state count S as the split-CSSR fit at each refit, but EM from random initializations
    (restarts x n_iter, best log-likelihood kept), with no use of the CSSR machine's structure."""

    def __init__(self, restarts=3, seed=12345, **kw):
        super().__init__(**kw)
        self.restarts, self.seed = restarts, seed
        self.name = f"RAND_EM_L{self.Lmax}_r{restarts}"

    def run(self, x):
        self._rng = np.random.default_rng(self.seed)
        return super().run(x)

    def _init(self, m):
        S = len(m.counts)
        self._S = S
        return S, None

    def _fit(self, h, S):
        best = None
        for _ in range(self.restarts):
            init = _normalize_rows([self._rng.random((S, S)), self._rng.random((S, S))])
            cand = _em(h, S, init, self.it)
            if best is None or cand[1] > best[1]:
                best = cand
        return best[0]
