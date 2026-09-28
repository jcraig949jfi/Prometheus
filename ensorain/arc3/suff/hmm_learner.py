"""PKG-S1 learned-compression arm: an S-state emission-labelled (Mealy) HMM fitted by Baum-Welch EM.

HMM_EM(S, refit_every, window):
- every refit_every symbols, EM (n_iter iterations, warm-started, 3 random restarts at the first fit) is run over the
  stored history (the full verbatim history if window is None, else the last `window` symbols);
- between refits it predicts online with the forward filter under the current parameters.
- Persistent state between refits: the parameters (2 x S x S) plus the belief (S) plus the stored history. The history is
  the part that makes discovery possible, and its size is the retention being tested.
The HMM with the right S can represent the Even process EXACTLY (2 causal states). Whether EM FINDS it, and from how much
retained history, is the learned-compression question."""
import numpy as np


def _normalize_rows(Tm):
    tot = Tm[0].sum(1) + Tm[1].sum(1)
    tot = np.where(tot > 0, tot, 1)
    return [Tm[0] / tot[:, None], Tm[1] / tot[:, None]]


def _em(x, S, Tm, n_iter):
    T = len(x)
    for _ in range(n_iter):
        pi = np.full(S, 1.0 / S)
        al = np.zeros((T + 1, S))
        sc = np.zeros(T)
        al[0] = pi
        for t in range(T):
            a = al[t] @ Tm[x[t]]
            sc[t] = a.sum() + 1e-300
            al[t + 1] = a / sc[t]
        be = np.ones(S)
        acc = [np.zeros((S, S)), np.zeros((S, S))]
        for t in range(T - 1, -1, -1):
            M = Tm[x[t]]
            xi = (al[t][:, None] * M) * be[None, :]
            s = xi.sum()
            if s > 0:
                acc[x[t]] += xi / s
            be = (M @ be) / sc[t]
        Tm = _normalize_rows([acc[0] + 1e-6, acc[1] + 1e-6])
    ll = float(np.sum(np.log2(sc)))
    return Tm, ll


class HMM_EM:
    def __init__(self, S, refit_every=250, window=None, n_iter=15, seed=0):
        self.S, self.re, self.win, self.it, self.seed = S, refit_every, window, n_iter, seed
        self.name = f"HMM{S}_EM_{'full' if window is None else 'W' + str(window)}"

    def run(self, x):
        S, T = self.S, len(x)
        rng = np.random.default_rng(self.seed)
        Tm = None
        b = np.full(S, 1.0 / S)
        P = np.full((T, 2), 0.5)
        for t in range(T):
            if t > 0 and t % self.re == 0:
                h = x[:t] if self.win is None else x[max(0, t - self.win):t]
                if Tm is None:                               # 3 random restarts at the first fit
                    best = None
                    for _ in range(3):
                        init = _normalize_rows([rng.random((S, S)), rng.random((S, S))])
                        cand = _em(h, S, init, self.it)
                        if best is None or cand[1] > best[1]:
                            best = cand
                    Tm = best[0]
                else:
                    Tm = _em(h, S, Tm, self.it)[0]
                b = np.full(S, 1.0 / S)                      # re-filter the stored history under the new parameters
                for s in h:
                    b = b @ Tm[s]
                    b = b / b.sum()
            if Tm is not None:
                pe = np.array([b @ Tm[0].sum(1), b @ Tm[1].sum(1)])
                P[t] = pe / pe.sum()
                b = b @ Tm[x[t]]
                b = b / max(b.sum(), 1e-300)
        stored = T if self.win is None else self.win
        return P, dict(bits=float(stored + 2 * S * S * 32 + S * 32), query_ops=float(S * S))
