"""T25: a CSSR-style causal-state learner (Shalizi and Klinkner 2004), binary alphabet, no fixed number of states.

Steps:
- fit(x) groups past suffixes (length <= Lmax) into states by next-symbol distribution. It uses a 1-df chi-square
  goodness-of-fit test at significance alpha against each state's pooled P(1).
- It then determinizes: a state is split until every length-Lmax history in it moves to the same successor state
  under each symbol.
- The predictor synchronizes on the longest known suffix, then follows the deterministic transitions (so it can track
  a causal state that no finite window determines, e.g. the Even process). It predicts with KT on the state's pooled
  counts.
- run(x) refits online every `refit` symbols on x[:t] and replays the stored history to re-synchronize.
- Before the first fit it predicts order-0 KT.

Memory accounting follows the HMM_EM convention: stored history + state table.
"""
import math
from collections import defaultdict

import numpy as np


def _suffix_counts(x, Lmax):
    cnt = [defaultdict(lambda: [0, 0]) for _ in range(Lmax + 1)]
    for t in range(len(x)):
        for L in range(0, min(t, Lmax) + 1):
            cnt[L][tuple(x[t - L:t])][x[t]] += 1
    return cnt


def _pval(c, p1):
    """1-df chi-square goodness-of-fit p-value of counts c = [n0, n1] against P(1) = p1."""
    n = c[0] + c[1]
    if n == 0:
        return 1.0
    if p1 <= 0.0:
        return 1.0 if c[1] == 0 else 0.0
    if p1 >= 1.0:
        return 1.0 if c[0] == 0 else 0.0
    chi2 = (c[1] - n * p1) ** 2 / (n * p1 * (1 - p1))
    return math.erfc(math.sqrt(chi2 / 2))


class CSSR:
    def __init__(self, Lmax=6, alpha=1e-3, refit=500, mode="split"):
        assert mode in ("split", "vote")
        self.Lmax, self.alpha, self.refit, self.mode = Lmax, alpha, refit, mode
        self.name = f"CSSR_{mode}_L{Lmax}_a{alpha:g}"

    # ---- structure learning ----
    def fit(self, x):
        Lmax, alpha = self.Lmax, self.alpha
        cnt = _suffix_counts(x, Lmax)
        hist = [{()}]                                        # state -> set of suffixes
        pool = [list(cnt[0][()])]                            # state -> pooled [n0, n1]

        def p1(s):
            n = pool[s][0] + pool[s][1]
            return pool[s][1] / n if n else 0.5

        def add(s, h, c):
            hist[s].add(h)
            pool[s][0] += c[0]
            pool[s][1] += c[1]

        for L in range(0, Lmax):
            for s in range(len(hist)):
                for h in [h for h in list(hist[s]) if len(h) == L]:
                    for a in (0, 1):
                        child = (a,) + h
                        c = cnt[L + 1].get(child)
                        if not c or c[0] + c[1] == 0:
                            continue
                        if _pval(c, p1(s)) > alpha:
                            add(s, child, c)
                            continue
                        best, bp = None, alpha
                        for r in range(len(hist)):
                            if r != s:
                                pv = _pval(c, p1(r))
                                if pv > bp:
                                    best, bp = r, pv
                        if best is None:
                            hist.append(set())
                            pool.append([0, 0])
                            best = len(hist) - 1
                        add(best, child, c)
        # keep only maximal-length histories; the state partition over them is what the machine uses
        groups = [sorted(h for h in hs if len(h) == Lmax) for hs in hist]
        groups = [g for g in groups if g]
        state_of = {h: i for i, g in enumerate(groups) for h in g}
        # determinize. "split" (standard CSSR): split states until every history's successors agree. "vote": keep the
        # step-2 partition and give each (state, symbol) its count-weighted modal successor. At finite Lmax the
        # successor h[1:] + b drops the oldest symbol, so a history can land in an ambiguous (window-truncated) state;
        # "split" propagates that ambiguity backwards through the chain, and "vote" out-votes it.
        changed = self.mode == "split"
        while changed:
            changed = False
            new_groups = []
            for g in groups:
                sig = defaultdict(list)
                for h in g:
                    key = tuple(state_of.get(h[1:] + (b,)) for b in (0, 1))
                    sig[key].append(h)
                if len(sig) > 1:
                    changed = True
                new_groups.extend(sig.values())
            groups = new_groups
            state_of = {h: i for i, g in enumerate(groups) for h in g}
        trans = {}
        counts = []
        for i, g in enumerate(groups):
            if self.mode == "split":
                h = g[0]
                trans[i] = tuple(state_of.get(h[1:] + (b,)) for b in (0, 1))
            else:
                tr = []
                for b in (0, 1):
                    votes = defaultdict(int)
                    for hh in g:
                        nxt = state_of.get(hh[1:] + (b,))
                        if nxt is not None:
                            votes[nxt] += cnt[Lmax].get(hh, [0, 0])[b]
                    tr.append(max(votes, key=votes.get) if votes and max(votes.values()) > 0 else None)
                trans[i] = tuple(tr)
            n = [0, 0]
            for hh in g:
                c = cnt[Lmax].get(hh, [0, 0])
                n[0] += c[0]
                n[1] += c[1]
            counts.append(n)
        # shorter-suffix fallback for synchronization: a suffix of length < Lmax maps to a state only if every
        # length-Lmax extension of it that occurs is in that one state
        short = {}
        for h, s in state_of.items():
            for L in range(1, Lmax):
                k = h[-L:]
                short.setdefault(k, set()).add(s)
        self.state_of, self.trans, self.counts = state_of, trans, counts
        self.short = {k: next(iter(v)) for k, v in short.items() if len(v) == 1}
        return self

    def _sync(self, x, n):
        """State from the tail of x[:n]: the full-length suffix, else the longest unambiguous shorter suffix."""
        if n >= self.Lmax:
            s = self.state_of.get(tuple(x[n - self.Lmax:n]))
            if s is not None:
                return s
        for L in range(min(n, self.Lmax - 1), 0, -1):
            s = self.short.get(tuple(x[n - L:n]))
            if s is not None:
                return s
        return None

    def _pred(self, s):
        if s is None:
            return None
        n0, n1 = self.counts[s]
        p = (n1 + 0.5) / (n0 + n1 + 1.0)
        return np.array([1 - p, p])

    # ---- online prediction ----
    def run(self, x):
        x = [int(v) for v in x]
        T = len(x)
        P = np.full((T, 2), 0.5)
        fitted, cur, c0 = False, None, [0, 0]
        occupied = []
        for t in range(T):
            if t > 0 and t % self.refit == 0:
                self.fit(x[:t])
                fitted, cur = True, None
                for u in range(t):                           # replay the stored history to re-synchronize
                    cur = self._step(cur, x, u + 1)
            if fitted and cur is not None:
                P[t] = self._pred(cur)
            else:
                p = (c0[1] + 0.5) / (c0[0] + c0[1] + 1.0)
                P[t] = [1 - p, p]
            c0[x[t]] += 1
            occupied.append(cur if fitted else None)
            if fitted:
                cur = self._step(cur, x, t + 1)
        self.occupied = occupied
        nstates = len(self.counts) if fitted else 0
        return P, dict(bits=float(T + nstates * (2 * 32 + 2 * math.log2(max(nstates, 2)))), query_ops=1.0,
                       states=nstates)

    def _step(self, cur, x, n):
        """After x[:n]: follow the deterministic transition on x[n-1]; if undefined or unsynchronized, re-synchronize."""
        if cur is not None:
            nxt = self.trans[cur][x[n - 1]]
            if nxt is not None:
                return nxt
        return self._sync(x, n)
