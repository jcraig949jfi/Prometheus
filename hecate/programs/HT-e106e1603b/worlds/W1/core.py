"""HT-e106e1603b / W1 kernels: lazy parity decoder (with optional bulk
deletion eps) and BTW sandpile. See NOTES.md for the spec->code map."""
import numpy as np
from numba import njit

BURN_IN = 2000
MEASURED = 20000
LS = (16, 32, 64)
CHECK_EVERY = 100


def build_lattice(L):
    N = L * L
    eid = -np.ones((N, 4), np.int64)  # 0 right, 1 down, 2 left, 3 up
    ea, eb, es = [], [], []  # endpoint a, endpoint b (-1 boundary), side
    def add(a, b, s):
        ea.append(a); eb.append(b); es.append(s)
        return len(ea) - 1
    for i in range(L):
        for j in range(L):
            v = i * L + j
            eid[v, 0] = add(v, v + 1, -1) if j < L - 1 else add(v, -1, 1)
            eid[v, 1] = add(v, v + L, -1) if i < L - 1 else add(v, -1, 3)
    for i in range(L):
        for j in range(L):
            v = i * L + j
            eid[v, 2] = add(v, -1, 0) if j == 0 else eid[v - 1, 0]
            eid[v, 3] = add(v, -1, 2) if i == 0 else eid[v - L, 1]
    return eid, np.array(ea, np.int64), np.array(eb, np.int64), np.array(es, np.int64)


@njit(cache=True)
def _toggle(u, L, dfx, cnt, act, pos, nact, theta):
    dfx[u] ^= 1
    d = 1 if dfx[u] == 1 else -1
    ui = u // L
    uj = u % L
    for a in range(max(0, ui - 1), min(L, ui + 2)):
        for b in range(max(0, uj - 1), min(L, uj + 2)):
            w = a * L + b
            cnt[w] += d
            if cnt[w] >= theta:
                if pos[w] < 0:
                    act[nact] = w
                    pos[w] = nact
                    nact += 1
            else:
                if pos[w] >= 0:
                    p = pos[w]
                    last = act[nact - 1]
                    act[p] = last
                    pos[last] = p
                    pos[w] = -1
                    nact -= 1
    return nact


@njit(cache=True)
def _flip(e, L, err, ea, eb, dfx, cnt, act, pos, nact, theta):
    err[e] ^= 1
    nact = _toggle(ea[e], L, dfx, cnt, act, pos, nact, theta)
    if eb[e] >= 0:
        nact = _toggle(eb[e], L, dfx, cnt, act, pos, nact, theta)
    return nact


@njit(cache=True)
def _find(par, x):
    while par[x] != x:
        par[x] = par[par[x]]
        x = par[x]
    return x


@njit(cache=True)
def _logical(L, err, ea, eb, es):
    N = L * L
    par = np.arange(N + 4)
    for e in range(err.shape[0]):
        if err[e] == 1:
            a = ea[e]
            b = eb[e] if eb[e] >= 0 else N + es[e]
            ra = _find(par, a)
            rb = _find(par, b)
            if ra != rb:
                par[ra] = rb
    span = (_find(par, N) == _find(par, N + 1)) or (_find(par, N + 2) == _find(par, N + 3))
    # largest error cluster (vertices touched by error edges), fraction of N
    touched = np.zeros(N, np.int64)
    for e in range(err.shape[0]):
        if err[e] == 1:
            touched[ea[e]] = 1
            if eb[e] >= 0:
                touched[eb[e]] = 1
    sz = np.zeros(N + 4, np.int64)
    for v in range(N):
        if touched[v] == 1:
            sz[_find(par, v)] += 1
    return span, sz.max() / N


@njit(cache=True)
def run_decoder(L, theta, eps, seed, eid, ea, eb, es, burn, meas, check_every):
    np.random.seed(seed)
    N = L * L
    E = ea.shape[0]
    err = np.zeros(E, np.int8)
    dfx = np.zeros(N, np.int8)
    cnt = np.zeros(N, np.int64)
    act = np.zeros(N, np.int64)
    pos = -np.ones(N, np.int64)
    nact = 0
    sizes = np.zeros(meas, np.int64)
    dels = np.zeros(meas, np.int64)
    wd = np.zeros(9, np.int64)
    pe = np.zeros(24, np.int64)
    dirs = np.zeros(4, np.int64)
    viol = 0
    nlog = 0
    dens_sum = 0.0
    lcf = 0.0
    for t in range(burn + meas):
        nact = _flip(np.random.randint(E), L, err, ea, eb, dfx, cnt, act, pos, nact, theta)
        s = 0
        dl = 0
        while nact > 0:
            v = act[np.random.randint(nact)]
            vi = v // L
            vj = v % L
            i0 = max(0, vi - 1); i1 = min(L, vi + 2)
            j0 = max(0, vj - 1); j1 = min(L, vj + 2)
            nd = 0
            np_ = 0
            for a in range(i0, i1):
                for b in range(j0, j1):
                    u = a * L + b
                    if dfx[u] == 1:
                        wd[nd] = u; nd += 1
                        if b + 1 < j1 and dfx[u + 1] == 1:
                            pe[np_] = eid[u, 0]; np_ += 1
                        if a + 1 < i1 and dfx[u + L] == 1:
                            pe[np_] = eid[u, 1]; np_ += 1
            if np_ > 0:
                e = pe[np.random.randint(np_)]
            else:
                u = wd[np.random.randint(nd)]
                ui = u // L
                uj = u % L
                dist = np.array([L - 1 - uj, L - 1 - ui, uj, ui])
                m = dist.min()
                k = 0
                for d in range(4):
                    if dist[d] == m:
                        dirs[k] = d; k += 1
                e = eid[u, dirs[np.random.randint(k)]]
            nact = _flip(e, L, err, ea, eb, dfx, cnt, act, pos, nact, theta)
            s += 1
            if eps > 0.0 and np.random.random() < eps:
                nd = 0
                for a in range(i0, i1):
                    for b in range(j0, j1):
                        u = a * L + b
                        if dfx[u] == 1:
                            wd[nd] = u; nd += 1
                if nd > 0:
                    nact = _toggle(wd[np.random.randint(nd)], L, dfx, cnt, act, pos, nact, theta)
                    dl += 1
        if t >= burn:
            k = t - burn
            sizes[k] = s
            dels[k] = dl
            viol += dl
            dens_sum += dfx.sum() / N
            if (k + 1) % check_every == 0:
                sp, lcf = _logical(L, err, ea, eb, es)
                if sp:
                    nlog += 1
    # parity audit: vertices whose defect bit disagrees with the syndrome of err
    mism = 0
    for v in range(N):
        syn = 0
        for d in range(4):
            syn ^= err[eid[v, d]]
        if syn != dfx[v]:
            mism += 1
    return sizes, dels, viol, mism, nlog, dens_sum / meas, lcf


@njit(cache=True)
def run_btw(L, seed, burn, meas):
    np.random.seed(seed)
    N = L * L
    z = np.zeros(N, np.int64)
    stack = np.zeros(8 * N + 16, np.int64)
    sizes = np.zeros(meas, np.int64)
    for t in range(burn + meas):
        v = np.random.randint(N)
        z[v] += 1
        sp = 0
        s = 0
        if z[v] >= 4:
            stack[sp] = v; sp += 1
        while sp > 0:
            sp -= 1
            u = stack[sp]
            if z[u] < 4:
                continue
            z[u] -= 4
            s += 1
            if z[u] >= 4:
                stack[sp] = u; sp += 1
            ui = u // L
            uj = u % L
            if uj + 1 < L:
                z[u + 1] += 1
                if z[u + 1] == 4:
                    stack[sp] = u + 1; sp += 1
            if uj > 0:
                z[u - 1] += 1
                if z[u - 1] == 4:
                    stack[sp] = u - 1; sp += 1
            if ui + 1 < L:
                z[u + L] += 1
                if z[u + L] == 4:
                    stack[sp] = u + L; sp += 1
            if ui > 0:
                z[u - L] += 1
                if z[u - L] == 4:
                    stack[sp] = u - L; sp += 1
        if t >= burn:
            sizes[t - burn] = s
    return sizes


def decoder(L, theta, eps, seed, burn=BURN_IN, meas=MEASURED):
    eid, ea, eb, es = build_lattice(L)
    sizes, dels, viol, mism, nlog, dens, lcf = run_decoder(
        L, theta, float(eps), seed, eid, ea, eb, es, burn, meas, CHECK_EVERY)
    return dict(sizes=sizes, violations=int(viol), audit_mismatch=int(mism),
                logical_per_1000=nlog / meas * 1000,
                logical_checkpoints=int(nlog), density=float(dens), largest_cluster_frac=float(lcf))


def btw(L, seed, burn=BURN_IN, meas=MEASURED):
    return dict(sizes=run_btw(L, seed, burn, meas))


def mean_nonempty(sizes):
    nz = sizes[sizes > 0]
    return float(nz.mean()) if nz.size else 0.0


def calibrate_eps(L, theta=3, calib_seeds=(900001, 900002), burn=BURN_IN, meas=10000, steps=14):
    """Largest eps in (0,1] whose mean non-empty avalanche size is within 5%
    of the eps=0 rule's (NOTES A2). Returns eps and the trace."""
    def m(eps):
        return float(np.mean([mean_nonempty(decoder(L, theta, eps, s, burn, meas)['sizes'])
                              for s in calib_seeds]))
    m0 = m(0.0)
    trace = [(0.0, m0)]
    m1 = m(1.0)
    trace.append((1.0, m1))
    if abs(m1 / m0 - 1) <= 0.05:
        return 1.0, m0, trace
    lo, hi = -6.0, 0.0
    for _ in range(steps):
        mid = 0.5 * (lo + hi)
        mm = m(10 ** mid)
        trace.append((10 ** mid, mm))
        if abs(mm / m0 - 1) <= 0.05:
            lo = mid
        else:
            hi = mid
    return 10 ** lo, m0, trace
