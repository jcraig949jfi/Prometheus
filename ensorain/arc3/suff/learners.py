"""PKG-S1 learners: the three compression loci (lit D8) plus a nonparametric one, each at a declared memory budget.

Binary-sequence learners predict P(x_t | x_<t) online. Each reports its persistent memory bits and its query ops (the
readout cost, accounted analytically where an incremental implementation gives identical predictions).
  STAT(k)            compression at STORAGE: keeps only order-k context counts (KT estimator) + the last k symbols.
                     Bits = 2^k x 2 counters x log2(t+1) + k.
  VERB_SUM(B, k)     verbatim window of the last B symbols; at query time it fits order-k KT counts OVER THE WINDOW
                     (compression at READOUT). Implemented incrementally (add newest / remove oldest), which gives the
                     identical predictive distribution; query ops charged as B x k.
  VERB_RESTRICT(B)   verbatim window, but the readout family is restricted to order 1 (V-information limit).
  NEAREST(B, Lmax)   verbatim window; the readout is PPM-style: the longest context (<= Lmax) with support in the
                     window, KT-smoothed. Query ops B x Lmax.
Key-value learners (W5): TABLE(B) a bounded table with random eviction (storage compression to B slots); LOG a verbatim
write log with exact lookup (unbounded); WINDOW(B) the last B writes only."""
import collections

import numpy as np


def _kt(c1, c):
    p1 = (c1 + 0.5) / (c + 1.0)
    return np.array([1 - p1, p1])


class STAT:
    def __init__(self, k):
        self.k, self.name = k, f"STAT_k{k}"

    def run(self, x):
        k, T = self.k, len(x)
        c1, c = np.zeros(2 ** k), np.zeros(2 ** k)
        P = np.full((T, 2), 0.5)
        for t in range(T):
            if t >= k:
                ctx = int("".join(map(str, x[t - k:t])), 2) if k else 0
                P[t] = _kt(c1[ctx], c[ctx])
                c1[ctx] += x[t]
                c[ctx] += 1
        bits = (2 ** k) * 2 * np.log2(T + 1) + k
        return P, dict(bits=float(bits), query_ops=float(k))


class VERB_SUM:
    def __init__(self, B, k):
        self.B, self.k, self.name = B, k, f"VERB_SUM_B{B}_k{k}"

    def run(self, x):
        B, k, T = self.B, self.k, len(x)
        c1, c = np.zeros(2 ** k), np.zeros(2 ** k)
        events = collections.deque()                  # (ctx, symbol) pairs inside the window
        P = np.full((T, 2), 0.5)
        for t in range(T):
            if t >= k:
                ctx = int("".join(map(str, x[t - k:t])), 2) if k else 0
                P[t] = _kt(c1[ctx], c[ctx])
                c1[ctx] += x[t]
                c[ctx] += 1
                events.append((ctx, x[t]))
                if len(events) > max(1, B - k):          # the window holds B symbols = B - k complete events
                    oc, ox = events.popleft()
                    c1[oc] -= ox
                    c[oc] -= 1
        return P, dict(bits=float(B), query_ops=float(B * max(k, 1)))


class VERB_RESTRICT(VERB_SUM):
    def __init__(self, B):
        super().__init__(B, 1)
        self.name = f"VERB_RESTRICT_B{B}"


class NEAREST:
    def __init__(self, B, Lmax=12):
        self.B, self.L, self.name = B, Lmax, f"NEAREST_B{B}_L{Lmax}"

    def run(self, x):
        B, L, T = self.B, self.L, len(x)
        tabs = [collections.defaultdict(lambda: [0, 0]) for _ in range(L + 1)]
        events = collections.deque()
        P = np.full((T, 2), 0.5)
        for t in range(T):
            p = None
            for l in range(min(L, t), -1, -1):           # longest supported context first
                key = tuple(x[t - l:t])
                c = tabs[l].get(key)
                if c and (c[0] + c[1]) > 0:
                    p = _kt(c[1], c[0] + c[1])
                    break
            if p is not None:
                P[t] = p
            for l in range(0, min(L, t) + 1):
                key = tuple(x[t - l:t])
                tabs[l][key][x[t]] += 1
                events.append((l, key, x[t]))
            while len(events) > B * (L + 1):
                l, key, s = events.popleft()
                tabs[l][key][s] -= 1
        return P, dict(bits=float(B), query_ops=float(B * L))


class TABLE:
    """W5: bounded content-addressable table with random eviction (storage compression)."""

    def __init__(self, B, V):
        self.B, self.V, self.name = B, V, f"TABLE_B{B}"

    def run(self, st, rng):
        tab, out = {}, []
        for k, q, v in zip(st["keys"], st["isq"], st["vals"]):
            if q:
                p = np.full(self.V, 1.0 / self.V)
                if k in tab:
                    p = np.full(self.V, 1e-6)
                    p[tab[k]] = 1.0
                    p /= p.sum()
                out.append(p)
            else:
                if k not in tab and len(tab) >= self.B:
                    del tab[list(tab)[rng.integers(len(tab))]]
                tab[k] = v
        return np.array(out), dict(bits=float(self.B))


class LOG(TABLE):
    def __init__(self, V):
        super().__init__(10 ** 12, V)
        self.name = "LOG_full"


class WINDOW:
    """W5: only the last B writes are readable (recency-bounded verbatim store)."""

    def __init__(self, B, V):
        self.B, self.V, self.name = B, V, f"WINDOW_B{B}"

    def run(self, st, rng):
        win, out = collections.OrderedDict(), []
        for k, q, v in zip(st["keys"], st["isq"], st["vals"]):
            if q:
                p = np.full(self.V, 1.0 / self.V)
                if k in win:
                    p = np.full(self.V, 1e-6)
                    p[win[k]] = 1.0
                    p /= p.sum()
                out.append(p)
            else:
                win.pop(k, None)
                win[k] = v
                if len(win) > self.B:
                    win.popitem(last=False)
        return np.array(out), dict(bits=float(self.B))
