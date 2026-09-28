"""PKG-S1 sufficiency-ladder worlds with EXACT Bayes predictors (ensorain/arc3/packages/PKG_S1_SUFFICIENCY_LADDER.md).

Every world exposes:
  sample(T, rng) -> the stream of observations (1-D int array; W5 also returns queries)
  bayes(stream) -> p_t = P(x_t = . | x_<t) for t = 0..T-1, as a (T, K) array, computed EXACTLY (closed form / forward
                   algorithm / lookup)
  suff_bits(t) -> the bits of the minimal sufficient statistic after t observations (the declared answer key)
Binary alphabet unless stated. All numpy; no WTP."""
import numpy as np

LOG2 = np.log(2)


class W0:
    """iid Bernoulli(p), p KNOWN. Sufficient statistic: nothing."""
    name, K = "W0_iid_known", 2

    def __init__(self, p=0.3):
        self.p = p

    def sample(self, T, rng):
        return (rng.random(T) < self.p).astype(int)

    def bayes(self, x):
        return np.tile([1 - self.p, self.p], (len(x), 1))

    def suff_bits(self, t):
        return 0.0


class W1:
    """Bernoulli with UNKNOWN p ~ Beta(a, a). Sufficient statistic: (count of 1s, t). Ordering is nuisance."""
    name, K = "W1_exchangeable", 2

    def __init__(self, a=1.0):
        self.a = a

    def sample(self, T, rng):
        p = rng.beta(self.a, self.a)
        return (rng.random(T) < p).astype(int)

    def bayes(self, x):
        n1 = np.concatenate([[0], np.cumsum(x)[:-1]])
        n = np.arange(len(x))
        p1 = (n1 + self.a) / (n + 2 * self.a)
        return np.stack([1 - p1, p1], 1)

    def suff_bits(self, t):
        return float(np.log2(t + 1))            # the count of 1s in 0..t


class W2:
    """Order-k binary Markov chain with an UNKNOWN transition table, each context's P(1) ~ Beta(a, a) (drawn per
    stream). Sufficient statistic: per-context counts plus the last k symbols. The Bayes predictor is the per-context
    Beta posterior."""
    K = 2

    def __init__(self, k=2, a=0.5):
        self.k, self.a = k, a
        self.name = f"W2_markov{k}"

    def sample(self, T, rng):
        q = rng.beta(self.a, self.a, size=2 ** self.k)
        x = np.zeros(T, int)
        x[:self.k] = rng.integers(0, 2, self.k)
        for t in range(self.k, T):
            ctx = int("".join(map(str, x[t - self.k:t])), 2)
            x[t] = rng.random() < q[ctx]
        return x

    def bayes(self, x):
        T = len(x)
        c1 = np.zeros(2 ** self.k)
        c = np.zeros(2 ** self.k)
        out = np.full((T, 2), 0.5)
        for t in range(T):
            if t >= self.k:
                ctx = int("".join(map(str, x[t - self.k:t])), 2)
                p1 = (c1[ctx] + self.a) / (c[ctx] + 2 * self.a)
                out[t] = [1 - p1, p1]
                c1[ctx] += x[t]
                c[ctx] += 1
        return out

    def suff_bits(self, t):
        return float(self.k + 2 ** self.k * np.log2(t + 1))


class HMMWorld:
    """A finite HMM with a KNOWN model. Bayes = forward filtering (the belief state is sufficient). Emission-labelled
    transitions: Tm[x][i, j] = P(next state j, emit x | state i)."""
    K = 2

    def __init__(self, name, Tm, pi, causal_states, crypt=None):
        self.name, self.Tm, self.pi = name, [np.asarray(m, float) for m in Tm], np.asarray(pi, float)
        self.S = len(self.pi)
        self.causal_states = causal_states       # number of causal states (answer key; C_mu set below)
        tot = sum(self.Tm)
        w, v = np.linalg.eig(tot.T)
        st = np.real(v[:, np.argmin(np.abs(w - 1))])
        self.stat = st / st.sum()

    def sample(self, T, rng):
        s = rng.choice(self.S, p=self.stat)
        x = np.zeros(T, int)
        for t in range(T):
            probs = np.concatenate([self.Tm[0][s], self.Tm[1][s]])
            k = rng.choice(2 * self.S, p=probs / probs.sum())
            x[t], s = k // self.S, k % self.S
        return x

    def bayes(self, x):
        b = self.stat.copy()
        out = np.zeros((len(x), 2))
        for t, xt in enumerate(x):
            pe = np.array([b @ self.Tm[0].sum(1), b @ self.Tm[1].sum(1)])
            out[t] = pe / pe.sum()
            b = b @ self.Tm[xt]
            b = b / b.sum()
        return out

    def suff_bits(self, t):
        return float(np.log2(self.causal_states)) if self.causal_states else np.inf


def even_process():
    """Even process: A --0 (1/2)--> A, A --1 (1/2)--> B, B --1 (1)--> A. Finite causal states (2); infinite-order
    Markov: no finite window is sufficient."""
    T0 = [[0.5, 0.0], [0.0, 0.0]]
    T1 = [[0.0, 0.5], [1.0, 0.0]]
    return HMMWorld("W3_even", [T0, T1], [2 / 3, 1 / 3], causal_states=2)


def golden_mean():
    """Golden mean: no two consecutive 0s. Order-1 Markov (a control for W3: finite window suffices)."""
    T0 = [[0.0, 0.5], [0.0, 0.0]]
    T1 = [[0.5, 0.0], [1.0, 0.0]]
    return HMMWorld("W3c_golden_mean", [T0, T1], [2 / 3, 1 / 3], causal_states=2)


def simple_nonunifilar_source(p=0.5, q=0.5):
    """SNS: two hidden states, both can emit 1; the state is not a function of past symbols (nonunifilar).
    The belief state is sufficient, and the causal-state count is infinite (countable), so suff_bits = inf."""
    T0 = [[0.0, 0.0], [q, 0.0]]
    T1 = [[1 - p, p], [0.0, 1 - q]]
    return HMMWorld("W4_sns", [T0, T1], [0.5, 0.5], causal_states=0)


class W5:
    """Key-value long tail. Stream items are (key, value) WRITES or key QUERIES. The value of each key is fixed per
    stream, uniform on V symbols. A query asks for the value of a key drawn from a Zipf(s) distribution over n_keys.
    Bayes for a query = the stored value (prob 1) if the key was written before, else uniform over V. Sufficient
    statistic: the set of seen (key, value) pairs. It grows with t: exact history (content-addressable) is necessary."""
    name = "W5_keyvalue"

    def __init__(self, n_keys=2000, V=16, s=1.1, p_query=0.5):
        self.n, self.V, self.s, self.pq = n_keys, V, s, p_query
        self.K = V
        w = 1.0 / np.arange(1, n_keys + 1) ** s
        self.w = w / w.sum()

    def sample(self, T, rng):
        vals = rng.integers(0, self.V, self.n)
        keys = rng.choice(self.n, size=T, p=self.w)
        isq = rng.random(T) < self.pq
        return dict(keys=keys, isq=isq, vals=vals[keys], table=vals)

    def bayes(self, st):
        seen = {}
        out = []
        for k, q, v in zip(st["keys"], st["isq"], st["vals"]):
            if q:
                p = np.full(self.V, 1.0 / self.V)
                if k in seen:
                    p = np.zeros(self.V)
                    p[seen[k]] = 1.0
                out.append(p)
            else:
                seen[k] = v
        return np.array(out)

    def targets(self, st):
        return st["vals"][st["isq"]]

    def suff_bits(self, n_distinct_written):
        return float(n_distinct_written * (np.log2(self.n) + np.log2(self.V)))


def logloss(P, x):
    """Mean log-loss in bits of predictive distributions P (T, K) on symbols x."""
    p = np.clip(P[np.arange(len(x)), x], 1e-12, 1)
    return float(-np.mean(np.log2(p)))


ALL = [W0, W1, lambda: W2(2), lambda: W2(3), even_process, golden_mean, simple_nonunifilar_source]
