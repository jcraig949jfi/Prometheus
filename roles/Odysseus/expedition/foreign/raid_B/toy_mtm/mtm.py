"""raid_B toy: multiple transient memories (MTM). EXPLORATORY. stdlib only.

See PREREG.md (frozen before first run). Worlds:
  W1 particles (Corte/Keim-Nagel random organisation under cyclic shear)
  W2 lattice, nested threshold rule
  W3 lattice, nested + spreading activity
  W4 lattice, non-nested band rule (anti-analogy control)
Usage:
  python3 mtm.py pilot            -> pilot.json
  python3 mtm.py main T_W1 T_LAT  -> results.json  (t_long per family)
"""
import json, math, random, sys, time
from multiprocessing import Pool

# ---------------------------------------------------------------- W1 particles
EPS = 0.5


def w1_init(rng, N=300, phi=0.2):
    L = math.sqrt(N * math.pi / 4.0 / phi)
    xs = [rng.random() * L for _ in range(N)]
    ys = [rng.random() * L for _ in range(N)]
    return xs, ys, L


def w1_active(xs, ys, L, g):
    """set of particles that collide during a cycle of amplitude g."""
    n = len(xs)
    order = sorted(range(n), key=lambda i: ys[i])
    act = set()
    half = L / 2.0
    for a in range(n):
        i = order[a]
        yi = ys[i]; xi = xs[i]
        for b in range(a + 1, n):
            j = order[b]
            dy = ys[j] - yi
            if dy >= 1.0:
                break
            w = math.sqrt(1.0 - dy * dy)
            dx0 = (xs[j] - xi + half) % L - half
            lo = dx0; hi = dx0 + g * dy  # dy >= 0
            if lo < w and hi > -w:
                act.add(i); act.add(j)
    return act


def w1_kick(xs, ys, L, idx, rng):
    for i in idx:
        r = EPS * math.sqrt(rng.random()); th = 2 * math.pi * rng.random()
        xs[i] = (xs[i] + r * math.cos(th)) % L
        y = ys[i] + r * math.sin(th)
        ys[i] = min(max(y, 0.0), L)


def w1_run(seed, amps, T, checkpoints, p_noise, N=300):
    rng = random.Random("w1-%s" % seed)
    xs, ys, L = w1_init(rng, N)
    snaps = {}
    if 0 in checkpoints:
        snaps[0] = (list(xs), list(ys))
    for t in range(1, T + 1):
        g = amps[(t - 1) % len(amps)]
        act = w1_active(xs, ys, L, g)
        if p_noise > 0:
            for i in range(len(xs)):
                if rng.random() < p_noise:
                    act.add(i)
        w1_kick(xs, ys, L, act, rng)
        if t in checkpoints:
            snaps[t] = (list(xs), list(ys))
    return snaps, L


def w1_readout(xs, ys, L, grid):
    n = len(xs)
    return [len(w1_active(xs, ys, L, a)) / n for a in grid]


# ---------------------------------------------------------------- lattices
Q = 64
W_BAND = 3


def cd(a, b):
    d = (a - b) % Q
    return d if d <= Q - d else Q - d


def nbrs(i, L):
    x, y = i % L, i // L
    return (((x + 1) % L) + y * L, ((x - 1) % L) + y * L,
            x + ((y + 1) % L) * L, x + ((y - 1) % L) * L)


def lat_is_active(s, i, NB, a, band):
    si = s[i]
    for j in NB[i]:
        d = cd(si, s[j])
        if band:
            if a - W_BAND <= d < a:
                return True
        elif d < a:
            return True
    return False


def lat_run(seed, world, amps, T, checkpoints, p_noise, L=48):
    rng = random.Random("lat-%s-%s" % (world, seed))
    n = L * L
    NB = [nbrs(i, L) for i in range(n)]
    s = [rng.randrange(Q) for _ in range(n)]
    band = (world == "W4")
    spread = 0.25 if world == "W3" else 0.0
    amax = max(amps)

    def minnd(i):
        si = s[i]
        return min(cd(si, s[j]) for j in NB[i])
    # hot = sites that could be active at some training amplitude
    hot = set(i for i in range(n) if minnd(i) < amax)
    snaps = {}
    if 0 in checkpoints:
        snaps[0] = list(s)
    for t in range(1, T + 1):
        a = amps[(t - 1) % len(amps)]
        act = [i for i in hot if lat_is_active(s, i, NB, a, band)]
        chg = set(act)
        if spread > 0:
            for i in act:
                for j in NB[i]:
                    if rng.random() < spread:
                        chg.add(j)
        if p_noise > 0:
            # geometric skipping for speed
            k = n * p_noise
            m = sum(1 for _ in range(n) if rng.random() < p_noise) if k > 5 else None
            if m is None:
                i = -1
                while True:
                    u = rng.random()
                    i += 1 + int(math.log(1 - u) / math.log(1 - p_noise))
                    if i >= n:
                        break
                    chg.add(i)
            else:
                for i in range(n):
                    if rng.random() < p_noise:
                        chg.add(i)
        for i in chg:
            s[i] = rng.randrange(Q)
        touched = set(chg)
        for i in chg:
            touched.update(NB[i])
        for i in touched:
            if minnd(i) < amax:
                hot.add(i)
            else:
                hot.discard(i)
        if t in checkpoints:
            snaps[t] = list(s)
    return snaps, NB


def lat_readout(s, NB, grid, band=False):
    n = len(s)
    return [sum(1 for i in range(n) if lat_is_active(s, i, NB, a, band)) / n
            for a in grid]


# ---------------------------------------------------------------- analysis
def kinks(C, grid, h_steps):
    out = {}
    for k in range(h_steps, len(grid) - h_steps):
        H = grid[k + h_steps] - grid[k]
        out[k] = (C[k + h_steps] - C[k]) / H - (C[k] - C[k - h_steps]) / H
    return out


def detect(C, grid, h_steps, g1, g2, thr):
    K = kinks(C, grid, h_steps)
    step = grid[1] - grid[0]
    far = [v for k, v in K.items()
           if abs(grid[k] - g1) >= 3 * h_steps * step - 1e-9
           and abs(grid[k] - g2) >= 3 * h_steps * step - 1e-9]
    mu = sum(far) / len(far)
    sd = math.sqrt(sum((v - mu) ** 2 for v in far) / max(1, len(far) - 1))
    res = {}
    for name, g in (("g1", g1), ("g2", g2)):
        k = min(range(len(grid)), key=lambda q: abs(grid[q] - g))
        kv = K.get(k, 0.0)
        res[name] = {"K": kv, "bg_sd": sd,
                     "detected": bool(kv > thr and kv > 3 * sd)}
    return res


def detect_band_dip(Cb, grid, g1, g2):
    step = grid[1] - grid[0]
    far = sorted(Cb[k] for k in range(len(grid))
                 if abs(grid[k] - g1) >= 3 * step and abs(grid[k] - g2) >= 3 * step)
    med = far[len(far) // 2]
    res = {}
    for name, g in (("g1", g1), ("g2", g2)):
        k = min(range(len(grid)), key=lambda q: abs(grid[q] - g))
        res[name] = {"Cb": Cb[k], "median": med, "dip": bool(Cb[k] < 0.5 * med)}
    return res


def mean_curves(curves):
    return [sum(c[k] for c in curves) / len(curves) for k in range(len(curves[0]))]


# ---------------------------------------------------------------- jobs
def job(args):
    fam, world, cond, seed, g1, g2, T, cps, p_on = args
    t0 = time.time()
    amps = [g2] if cond.startswith("single") else [g1, g2]
    pn = p_on if cond.endswith("noise") else 0.0
    out = {}
    if fam == "W1":
        grid = [round(0.1 * k, 3) for k in range(1, int(round(20 * g2)) + 1)]
        snaps, L = w1_run(seed, amps, T, set(cps), pn)
        for t, (xs, ys) in snaps.items():
            out[t] = w1_readout(xs, ys, L, grid)
    else:
        grid = list(range(1, 2 * int(g2) + 1))
        snaps, NB = lat_run(seed, world, amps, T, set(cps), pn)
        for t, s in snaps.items():
            out[t] = {"C": lat_readout(s, NB, grid)}
            if world == "W4":
                out[t]["Cb"] = lat_readout(s, NB, grid, band=True)
    return (fam, world, cond, seed, grid, out, time.time() - t0)


def pilot():
    res = {}
    with Pool(4) as pool:
        jobs = []
        for f in (1.0, 0.75, 0.5625):
            jobs.append(("W1", "W1", "single", 999, 1.0 * f, 2.0 * f, 4096,
                         [2 ** k for k in range(0, 13)], 0.0))
            jobs.append(("LAT", "W2", "single", 999, round(5 * f), round(10 * f), 8192,
                         [2 ** k for k in range(0, 14)], 0.0))
        for r in pool.imap_unordered(job, jobs):
            fam, world, cond, seed, grid, out, dt = r
            g2 = [j for j in jobs if j[1] == world][0]
            key = "%s_g2grid_%s" % (world, len(grid))
            # C at g2 (grid index of 2*? ) -> g2 is grid midpoint
            k2 = len(grid) // 2 - 1
            res[key] = {"g2": grid[k2], "sec": round(dt, 1),
                        "C_at_g2": {t: v[k2] if isinstance(v, list) else v["C"][k2]
                                    for t, v in sorted(out.items())}}
            print(key, res[key], flush=True)
    json.dump(res, open("pilot.json", "w"), indent=1)


def main(T1, TL, g1w, g2w, g1l, g2l):
    conds = ["alt", "alt_noise", "single"]
    jobs = []
    for seed in range(1, 6):
        for c in conds:
            cps = [0, max(4, T1 // 16), T1]
            jobs.append(("W1", "W1", c, seed, g1w, g2w, T1, cps, 0.002))
            for w in ("W2", "W3", "W4"):
                cpl = [0, max(4, TL // 16), TL]
                jobs.append(("LAT", w, c, seed, g1l, g2l, TL, cpl, 0.0005))
    raw = []
    with Pool(4) as pool:
        for r in pool.imap_unordered(job, jobs):
            print(r[1], r[2], r[3], "%.1fs" % r[6], flush=True)
            raw.append(r)
    summary = {}
    for w in ("W1", "W2", "W3", "W4"):
        g1, g2 = (g1w, g2w) if w == "W1" else (g1l, g2l)
        T = T1 if w == "W1" else TL
        tm = max(4, T // 16)
        hs = 2 if w == "W1" else 1
        thr = 0.05 if w == "W1" else 0.02
        summary[w] = {"g1": g1, "g2": g2, "t_mid": tm, "t_long": T}
        for c in conds:
            rs = [r for r in raw if r[1] == w and r[2] == c]
            grid = rs[0][4]
            for t, lab in ((0, "rand"), (tm, "mid"), (T, "long")):
                if w == "W1":
                    C = mean_curves([r[5][t] for r in rs])
                else:
                    C = mean_curves([r[5][t]["C"] for r in rs])
                ent = {"C": [round(v, 5) for v in C],
                       "det": detect(C, grid, hs, g1, g2, thr)}
                if w == "W4":
                    Cb = mean_curves([r[5][t]["Cb"] for r in rs])
                    ent["Cb"] = [round(v, 5) for v in Cb]
                    ent["dip"] = detect_band_dip(Cb, grid, g1, g2)
                summary[w]["%s_%s" % (c, lab)] = ent
            summary[w]["grid"] = grid
        d = lambda key, g: summary[w][key]["det"][g]["detected"]
        P = {"P1_mid_both": d("alt_mid", "g1") and d("alt_mid", "g2"),
             "P2_long_forget_g1": d("alt_long", "g2") and not d("alt_long", "g1"),
             "P3_noise_long_both": d("alt_noise_long", "g1") and d("alt_noise_long", "g2"),
             "P4_single_no_g1": not d("single_mid", "g1") and not d("single_long", "g1"),
             "P5_rand_none": not d("alt_rand", "g1") and not d("alt_rand", "g2")}
        P["MTM"] = all(P.values())
        summary[w]["predictions"] = P
        print(w, P, flush=True)
    json.dump(summary, open("results.json", "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1] == "pilot":
        pilot()
    else:
        a = sys.argv[2:]
        main(int(a[0]), int(a[1]), float(a[2]), float(a[3]), int(a[4]), int(a[5]))
