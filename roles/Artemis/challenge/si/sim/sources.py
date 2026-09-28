"""Sources for the SI Phase-2 simulation (prereg MODEL_AND_PREREG.md s2.5, frozen at 1b573ac95).

A machine is a unifilar HMM:
  nS, nX, F[s][x] -> s' or -1 if T[s][x] == 0, T[s][x] emission probs, s0 start state.
Sequences are 1-indexed: xs[1..T], S[0..T] with S[0] = s0.
"""
import hashlib
import math
import numpy as np

FREEZE_SHA = "1b573ac95bcd103ddd6aa7b63736634827e7c2a4"


def seed_for(family, cell, i):
    h = hashlib.sha256(("SI-ART-P2|" + FREEZE_SHA + "|" + family + "|" + cell + "|" + str(i)).encode()).hexdigest()
    return int(h[:8], 16)


class Machine:
    def __init__(self, name, F, T, s0=0):
        self.name = name
        self.T = np.asarray(T, dtype=float)
        self.nS, self.nX = self.T.shape
        self.F = [[(int(F[s][x]) if self.T[s, x] > 0 else -1) for x in range(self.nX)] for s in range(self.nS)]
        self.s0 = s0
        self.w = max(1, math.ceil(math.log2(self.nS)))
        self.wx = max(1, math.ceil(math.log2(self.nX)))
        # preimage table: PRE[(s', x)] = list of s with F[s][x] == s'
        self.PRE = {}
        for s in range(self.nS):
            for x in range(self.nX):
                sp = self.F[s][x]
                if sp >= 0:
                    self.PRE.setdefault((sp, x), []).append(s)
        # per-symbol transition matrices for filtering: M[x][s, s'] = T[s,x] [F[s][x]==s']
        self.M = np.zeros((self.nX, self.nS, self.nS))
        for s in range(self.nS):
            for x in range(self.nX):
                if self.F[s][x] >= 0:
                    self.M[x, s, self.F[s][x]] += self.T[s, x]
        P = self.M.sum(axis=0)
        vals, vecs = np.linalg.eig(P.T)
        k = int(np.argmin(np.abs(vals - 1)))
        pi = np.real(vecs[:, k])
        pi = pi / pi.sum()
        self.pi = np.clip(pi, 0, None) / np.clip(pi, 0, None).sum()
        self.Fnp = np.array(self.F, dtype=np.int64)

    # ---------- exact source quantities ----------
    def quantities(self):
        H = lambda p: -sum(v * math.log2(v) for v in p if v > 0)
        pi = self.pi
        h = sum(pi[s] * H(self.T[s]) for s in range(self.nS))
        C = H(pi)
        # joint (s_prev, x, s_new)
        J = {}
        for s in range(self.nS):
            for x in range(self.nX):
                if self.F[s][x] >= 0 and self.T[s, x] > 0:
                    J[(s, x, self.F[s][x])] = pi[s] * self.T[s, x]
        # g = H(S_prev | S_new, X)
        by = {}
        for (s, x, sn), v in J.items():
            by.setdefault((sn, x), []).append(v)
        g = sum(sum(vs) * H([v / sum(vs) for v in vs]) for vs in by.values())
        e = h - g
        pm = self.p_merge_given_state()
        return dict(h=h, C=C, g=g, e=e, p_merge=float(np.dot(pi, pm)))

    def merges(self, sn, x):
        return len(self.PRE.get((sn, x), [])) > 1

    def p_merge_given_state(self):
        pm = np.zeros(self.nS)
        for s in range(self.nS):
            for x in range(self.nX):
                sn = self.F[s][x]
                if sn >= 0 and self.merges(sn, x):
                    pm[s] += self.T[s, x]
        return pm

    def co_unifilar(self):
        return all(len(v) == 1 for v in self.PRE.values())

    def perm_extension(self):
        """For co-unifilar machines: extend each F[.,x] to a permutation of range(nS)."""
        P = []
        for x in range(self.nX):
            img = {}
            for s in range(self.nS):
                if self.F[s][x] >= 0:
                    img[s] = self.F[s][x]
            used = set(img.values())
            free_imgs = [v for v in range(self.nS) if v not in used]
            for s in range(self.nS):
                if s not in img:
                    img[s] = free_imgs.pop(0)
            P.append([img[s] for s in range(self.nS)])
        return P

    def image(self, mask_bool, x):
        """image of a state set (bool array) under symbol x (allowed transitions only)."""
        out = np.zeros(self.nS, dtype=bool)
        idx = np.nonzero(mask_bool)[0]
        tgt = self.Fnp[idx, x]
        tgt = tgt[tgt >= 0]
        out[tgt] = True
        return out

    # ---------- sampling ----------
    def sample(self, T, seed):
        rng = np.random.Generator(np.random.PCG64(seed))
        u = rng.random(T + 1)
        cum = np.cumsum(self.T, axis=1)
        xs = np.zeros(T + 1, dtype=np.int64)
        S = np.zeros(T + 1, dtype=np.int64)
        s = self.s0
        S[0] = s
        for t in range(1, T + 1):
            x = int(np.searchsorted(cum[s], u[t], side="right"))
            if x >= self.nX:
                x = self.nX - 1
            while self.T[s, x] <= 0:  # guard against float edge
                x -= 1
            xs[t] = x
            s = self.F[s][x]
            S[t] = s
        return xs, S

    def sync_depth_end(self, xs):
        """D_end[i] = minimal D such that the image of all states under x_{i-D+1..i} is a singleton;
        a very large number if none within x_1..x_i. Uses e(j) monotonicity."""
        T = len(xs) - 1
        INF = 10 ** 12  # "never synchronised" sentinel; larger than any W (learners use 10**9 for W=inf)
        e = np.full(T + 2, INF, dtype=np.int64)
        allm = np.ones(self.nS, dtype=bool)
        dead = False
        for j in range(1, T + 1):
            if dead:
                break
            m = allm
            i = j
            found = False
            while i <= T:
                m = self.image(m, xs[i])
                c = int(m.sum())
                if c <= 1:
                    found = True
                    break
                i += 1
            if found:
                e[j] = i
            else:
                dead = True  # e monotone: all later j also never sync
        D = np.full(T + 1, INF, dtype=np.int64)
        # D_end(i) = i - max{j : e(j) <= i} + 1
        best = 0
        jptr = 1
        for i in range(1, T + 1):
            while jptr <= T and e[jptr] <= i:
                best = jptr
                jptr += 1
            if best > 0:
                D[i] = i - best + 1
        return D

    def filter_belief(self, xs, lo, hi, prior=None):
        b = self.pi.copy() if prior is None else prior.copy()
        for i in range(lo, hi + 1):
            b = b @ self.M[xs[i]]
            z = b.sum()
            b = b / z if z > 0 else self.pi.copy()
        return b


def rp(q, a=0.25):
    # X: 0 -> '0', 1 -> '1', 2 -> 'R'
    T = []
    F = []
    for p in (0, 1):
        b = a if p == 0 else 1 - a
        T.append([(1 - q) * (1 - b), (1 - q) * b, q])
        F.append([p, 1 - p, 0])
    return Machine("RP(q=%g,a=%g)" % (q, a), F, T, 0)


def golden_mean(p=0.5):
    return Machine("GM", [[0, 1], [0, -1]], [[1 - p, p], [1.0, 0.0]], 0)


def even(p=0.5):
    return Machine("EVEN", [[0, 1], [-1, 0]], [[1 - p, p], [0.0, 1.0]], 0)


def _strongly_connected(F, nS, nX):
    def reach(adj, s0):
        seen = {s0}
        st = [s0]
        while st:
            u = st.pop()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    st.append(v)
        return seen
    adj = [[F[s][x] for x in range(nX)] for s in range(nS)]
    radj = [[] for _ in range(nS)]
    for s in range(nS):
        for x in range(nX):
            radj[F[s][x]].append(s)
    return len(reach(adj, 0)) == nS and len(reach(radj, 0)) == nS


def _synchronizing(F, nS, nX):
    # every pair can be merged (pair-graph reachability to diagonal)
    from collections import deque
    good = set((s, s) for s in range(nS))
    # backward BFS from diagonal over pair graph
    pre = {}
    for a in range(nS):
        for b in range(a, nS):
            for x in range(nX):
                fa, fb = F[a][x], F[b][x]
                key = (min(fa, fb), max(fa, fb))
                pre.setdefault(key, []).append((a, b))
    dq = deque(good)
    while dq:
        u = dq.popleft()
        for v in pre.get(u, []):
            if v not in good:
                good.add(v)
                dq.append(v)
    return all((a, b) in good for a in range(nS) for b in range(a, nS))


def _minimal(F, T, nS, nX):
    # Moore partition refinement on (emission row, successor classes)
    cls = {}
    lab = []
    for s in range(nS):
        key = tuple(np.round(T[s], 12))
        lab.append(cls.setdefault(key, len(cls)))
    while True:
        cls2 = {}
        new = []
        for s in range(nS):
            key = (lab[s],) + tuple(lab[F[s][x]] for x in range(nX))
            new.append(cls2.setdefault(key, len(cls2)))
        if len(cls2) == len(set(lab)):
            return len(cls2) == nS
        lab = new


def random_machine(k, nX, seed):
    rng = np.random.Generator(np.random.PCG64(seed))
    nS = 2 ** k
    rejects = 0
    while True:
        F = rng.integers(0, nS, size=(nS, nX)).tolist()
        T = rng.dirichlet(np.ones(nX), size=nS)
        if _strongly_connected(F, nS, nX) and _synchronizing(F, nS, nX) and _minimal(F, T, nS, nX):
            m = Machine("RND(k=%d,X=%d,seed=%d)" % (k, nX, seed), F, T, 0)
            m.rejects = rejects
            return m
        rejects += 1


def r_prime_exact(m, W, cap_states=200000):
    """Rate of merges whose predecessor S_{t-1} is not recoverable from the retained window
    x_{t-W+1..t-1} (W-1 symbols) by synchronisation (window-only test; A5). Exact DP over
    (true state, image set); returns (value, 'exact'|'mc'|'closed')."""
    if W is None:  # infinite
        return 0.0, "exact"
    L = W - 1
    pm = m.p_merge_given_state()
    full = (1 << m.nS) - 1
    dist = {}
    for s in range(m.nS):
        if m.pi[s] > 0:
            dist[(s, full)] = m.pi[s]
    for _ in range(L):
        nd = {}
        for (s, I), p in dist.items():
            if I & (I - 1) == 0:  # singleton: already synced; stays synced -> drop (recoverable)
                continue
            for x in range(m.nX):
                sp = m.F[s][x]
                if sp < 0:
                    continue
                # image of I
                J = 0
                II = I
                while II:
                    b = II & -II
                    u = b.bit_length() - 1
                    t = m.F[u][x]
                    if t >= 0:
                        J |= 1 << t
                    II ^= b
                key = (sp, J)
                nd[key] = nd.get(key, 0.0) + p * m.T[s, x]
        dist = nd
        if len(dist) > cap_states:
            return None, "dp_cap"
    tot = 0.0
    for (s, I), p in dist.items():
        if I & (I - 1) != 0:
            tot += p * pm[s]
    return tot, "exact"
