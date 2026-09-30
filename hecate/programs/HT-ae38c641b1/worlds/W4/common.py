"""HT-ae38c641b1 / W4 shared machinery: map family, sound decided test,
ground truth, uniform / oracle / null policies, gamma fit, criterion.

No treatment (sensitivity) policy lives here; see NOTES.md.
"""
import math
import random
import heapq

KS = (4, 6, 8)
TS = (2, 5, 10, 20)
ROTS = (0, 30)
CHECKPOINTS = [64 * 2 ** i for i in range(9)]  # 64 .. 16384
UNIFORM_LEVELS = (3, 4, 5, 6, 7)
TRUTH_DEPTH = 12
SOUND_MAX_DEPTH = 24
PAD = 1e-12
SEEDS = (0, 1, 2, 3, 4)
C = 0.5

CONFIGS = [(k, T, t) for k in KS for T in TS for t in ROTS]


def D_of(k):
    return 2.0 * math.log(k / 2) / math.log(k)


def lamT(k, T):
    return T * math.log(k)


class World:
    """One (k, T, t) configuration with caches for truth and sound tests."""

    def __init__(self, k, T, t):
        self.k, self.T, self.t = k, T, t
        th = math.radians(t)
        self.cs, self.sn = math.cos(th), math.sin(th)
        self.kept = set(range(0, k, 2))
        self._truth = {}
        self._sound = {}

    # ---------------- sound decided test ----------------
    def _meet(self, lo, hi, exact):
        """Meet interval (lo,hi) with kept strips. Returns
        (status, new_lo, new_hi, lost); status: 'empty' | 'multi' | 'one'."""
        k = self.k
        klo, khi = k * lo, k * hi
        a = math.floor(klo)
        b = math.ceil(khi) - 1
        if b < a:
            b = a
        lost = False
        hits = []
        for j in range(a, b + 1):
            if 0 <= j < k and j in self.kept:
                hits.append(j)
            else:
                lost = True
        if not hits:
            return 'empty', 0.0, 0.0, True
        if len(hits) > 1:
            return 'multi', 0.0, 1.0, True
        j = hits[0]
        nlo = klo - j
        nhi = khi - j
        if nlo < 0.0:
            nlo = 0.0
        if nhi > 1.0:
            nhi = 1.0
        if not exact:
            nlo = max(0.0, nlo - PAD)
            nhi = min(1.0, nhi + PAD)
        return 'one', nlo, nhi, lost

    def sound(self, d, i, j):
        """Returns (label, width): label in 'esc','surv','und'."""
        key = (d, i, j)
        r = self._sound.get(key)
        if r is not None:
            return r
        s = 1.0 / (1 << d)
        x0, x1, y0, y1 = i * s, (i + 1) * s, j * s, (j + 1) * s
        exact = (self.t == 0)
        cs, sn = self.cs, self.sn
        lost_any = False
        width = 0.0
        label = None
        # current box in x-frame as centre/half-width
        for step in range(self.T):
            if exact:
                u0, u1, v0, v1 = x0, x1, y0, y1
            else:
                xc, yc = (x0 + x1) / 2 - C, (y0 + y1) / 2 - C
                hx, hy = (x1 - x0) / 2, (y1 - y0) / 2
                # R^-1 (rotate by -t)
                uc = cs * xc + sn * yc + C
                vc = -sn * xc + cs * yc + C
                hu = cs * hx + sn * hy + PAD
                hv = sn * hx + cs * hy + PAD
                u0, u1, v0, v1 = uc - hu, uc + hu, vc - hv, vc + hv
            st1, a0, a1, l1 = self._meet(u0, u1, exact)
            st2, b0, b1, l2 = self._meet(v0, v1, exact)
            if st1 == 'empty' or st2 == 'empty':
                label = 'esc'
                width = max(u1 - u0, v1 - v0)
                break
            if st1 == 'multi' or st2 == 'multi':
                label = 'und'
                width = 1.0
                break
            lost_any = lost_any or l1 or l2
            width = max(a1 - a0, b1 - b0)
            if exact:
                x0, x1, y0, y1 = a0, a1, b0, b1
            else:
                uc, vc = (a0 + a1) / 2 - C, (b0 + b1) / 2 - C
                hu, hv = (a1 - a0) / 2, (b1 - b0) / 2
                xc = cs * uc - sn * vc + C
                yc = sn * uc + cs * vc + C
                hx = cs * hu + sn * hv + PAD
                hy = sn * hu + cs * hv + PAD
                x0, x1, y0, y1 = xc - hx, xc + hx, yc - hy, yc + hy
        if label is None:
            label = 'und' if lost_any else 'surv'
        r = (label, width)
        self._sound[key] = r
        return r

    # ---------------- ground truth ----------------
    def _poly(self, d, i, j):
        s = 1.0 / (1 << d)
        pts = [(i * s, j * s), ((i + 1) * s, j * s), ((i + 1) * s, (j + 1) * s), (i * s, (j + 1) * s)]
        if self.t == 0:
            return pts
        cs, sn = self.cs, self.sn
        out = []
        for (x, y) in pts:
            x -= C
            y -= C
            out.append((cs * x + sn * y + C, -sn * x + cs * y + C))
        return out

    def _overlap(self, poly, ax0, ay0, sz):
        """CLOSED overlap of convex quad with axis square (repair, attempt 2)."""
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        if min(xs) > ax0 + sz or max(xs) < ax0 or min(ys) > ay0 + sz or max(ys) < ay0:
            return False
        if self.t == 0:
            return True
        # polygon edge normals: (cs, -sn)-ish directions; use the two edge dirs
        sq = [(ax0, ay0), (ax0 + sz, ay0), (ax0 + sz, ay0 + sz), (ax0, ay0 + sz)]
        for e in range(2):
            (px, py), (qx, qy) = poly[e], poly[e + 1]
            nx, ny = -(qy - py), (qx - px)
            pp = [nx * p[0] + ny * p[1] for p in poly]
            qq = [nx * p[0] + ny * p[1] for p in sq]
            if min(pp) > max(qq) or max(pp) < min(qq):
                return False
        return True

    def _inside(self, poly, ax0, ay0, sz):
        """Strictly inside the open square (repair, attempt 2)."""
        return all(ax0 < p[0] < ax0 + sz and ay0 < p[1] < ay0 + sz for p in poly)

    def truth(self, d, i, j):
        """True iff the closed cell meets the boundary of K_T (repair,
        attempt 2): meets a level-T kept square S, not inside int(S).
        Cells deeper than TRUTH_DEPTH inherit their depth-12 ancestor."""
        if d > TRUTH_DEPTH:
            sh = d - TRUTH_DEPTH
            return self.truth(TRUTH_DEPTH, i >> sh, j >> sh)
        key = (d, i, j)
        r = self._truth.get(key)
        if r is not None:
            return r
        poly = self._poly(d, i, j)
        k, T = self.k, self.T
        kept = sorted(self.kept)
        found = [False]
        contained = [False]

        def dfs(level, ax0, ay0, sz):
            # square (ax0,ay0,sz) is a kept level-`level` square overlapping poly
            if level == T:
                found[0] = True
                if self._inside(poly, ax0, ay0, sz):
                    contained[0] = True
                return True
            csz = sz / k
            for dx in kept:
                for dy in kept:
                    bx, by = ax0 + dx * csz, ay0 + dy * csz
                    if self._overlap(poly, bx, by, csz):
                        if dfs(level + 1, bx, by, csz):
                            return True
            return False

        if self._overlap(poly, 0.0, 0.0, 1.0):
            dfs(0, 0.0, 0.0, 1.0)
        r = found[0] and not contained[0]
        self._truth[key] = r
        return r


# ---------------- policies ----------------

def run_uniform(w):
    out = {'B': [], 'area_true': [], 'area_sound': []}
    for L in UNIFORM_LEVELS:
        n = 1 << L
        at = asd = 0
        for i in range(n):
            for j in range(n):
                if w.truth(L, i, j):
                    at += 1
                if w.sound(L, i, j)[0] == 'und':
                    asd += 1
        out['B'].append(4 ** L)
        out['area_true'].append(at / 4 ** L)
        out['area_sound'].append(asd / 4 ** L)
    return out


def _children(d, i, j):
    return [(d + 1, 2 * i + a, 2 * j + b) for a in (0, 1) for b in (0, 1)]


def run_oracle(w, seed):
    rng = random.Random(seed)
    heap = []
    area = 1.0 if w.truth(0, 0, 0) else 0.0
    if w.truth(0, 0, 0):
        heapq.heappush(heap, (0, rng.random(), 0, 0))
    leaves, cp = 1, 0
    Bs, areas, depth_seq = [], [], []
    stopped = False
    while cp < len(CHECKPOINTS):
        if not heap:
            stopped = True
            break
        d, _, i, j = heapq.heappop(heap)
        area -= 4.0 ** -d
        depth_seq.append(d)
        for (cd, ci, cj) in _children(d, i, j):
            if w.truth(cd, ci, cj):
                area += 4.0 ** -cd
                if cd < TRUTH_DEPTH:
                    heapq.heappush(heap, (cd, rng.random(), ci, cj))
        leaves += 3
        while cp < len(CHECKPOINTS) and leaves >= CHECKPOINTS[cp]:
            Bs.append(CHECKPOINTS[cp])
            areas.append(max(area, 0.0))
            cp += 1
    return {'B': Bs, 'area': areas, 'stopped_early': stopped,
            'depth_seq': depth_seq, 'max_depth': max(depth_seq) + 1 if depth_seq else 0}


def run_null(w, seed, depth_seq):
    """Random refinement replaying a reference policy's split-depth sequence."""
    rng = random.Random(10_000 + seed)
    by_depth = {0: [(0, 0)]}
    lab = w.sound(0, 0, 0)[0]
    area = 1.0 if lab == 'und' else 0.0
    leaves, cp = 1, 0
    Bs, areas = [], []
    for d in depth_seq:
        lst = by_depth[d]
        idx = rng.randrange(len(lst))
        lst[idx], lst[-1] = lst[-1], lst[idx]
        i, j = lst.pop()
        if w.sound(d, i, j)[0] == 'und':
            area -= 4.0 ** -d
        for (cd, ci, cj) in _children(d, i, j):
            by_depth.setdefault(cd, []).append((ci, cj))
            if w.sound(cd, ci, cj)[0] == 'und':
                area += 4.0 ** -cd
        leaves += 3
        while cp < len(CHECKPOINTS) and leaves >= CHECKPOINTS[cp]:
            Bs.append(CHECKPOINTS[cp])
            areas.append(max(area, 0.0))
            cp += 1
    return {'B': Bs, 'area': areas}


# ---------------- statistics ----------------

def fit_gamma(Bs, areas, upper_half=False):
    pts = [(b, a) for b, a in zip(Bs, areas) if a > 0]
    if upper_half:
        pts = pts[len(pts) // 2:]
    if len(pts) < 3:
        return None
    xs = [math.log(b) for b, _ in pts]
    ys = [math.log(a) for _, a in pts]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return -sxy / sxx


def pc_eligible(k, T):
    return k ** (-T) <= 2.0 ** (-TRUTH_DEPTH)


def cheat_r(k, T):
    lts = [lamT(kk, TT) for kk in KS for TT in TS]
    lo, hi = min(lts), max(lts)
    return 1.0 - 0.7 * (lamT(k, T) - lo) / (hi - lo)


def spearman(x, y):
    from scipy.stats import spearmanr
    return float(spearmanr(x, y).correlation)


def arm_criterion(ratio):
    """ratio: dict (k,T,t) -> gamma_arm/gamma_oracle (seed means).
    Returns dict with S1,S2,S3,rho,meets."""
    s1 = all(ratio[(k, 2, 0)] is not None and ratio[(k, 2, 0)] >= 0.8 for k in KS)
    s2 = all(ratio[(k, 20, 30)] is not None and ratio[(k, 20, 30)] <= 0.6 for k in KS)
    keys = [c for c in CONFIGS if ratio[c] is not None]
    rho = spearman([lamT(k, T) for (k, T, t) in keys], [ratio[c] for c in keys]) if len(keys) >= 3 else None
    s3 = rho is not None and not math.isnan(rho) and rho <= -0.7
    return {'S1': s1, 'S2': s2, 'S3': s3, 'rho': rho, 'meets': bool(s1 and s2 and s3),
            'n_configs': len(keys)}


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None
