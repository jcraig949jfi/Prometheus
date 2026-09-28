"""POST-HOC (not preregistered; labelled in RESULT.md). EXPLORATORY.

Diagnosis after the preregistered run failed P1/P3 in every world: the source
(Paulsen, Keim & Nagel PRE 2013) uses kick size eps = 0.005 d, 100x smaller
than the prereg's 0.5, and ~1e4 cycles. Hypothesis H_margin: the smaller
memory needs SMALL kicks, so that a kicked unit stays near the margin of the
amplitude that kicked it (depletion just below g, pile-up just above).
Test: identical readout/detector, only the kick size changes.
  W1s : particles, eps = 0.05
  W2s/W3s/W4s : lattice, a kicked site moves s -> s + u, u uniform in
               {-KS..KS}\\{0}, KS = 2 (instead of uniform redraw)
  W2big: lattice, uniform redraw (= prereg W2) at the same checkpoints (reference)
Checkpoints: W1s 0,64,256,1024,4096 ; lattice 0,16,64,256,1024,4096.
"""
import json, math, random, sys, time
from multiprocessing import Pool
import mtm

KS = 2


def lat_run_small(seed, world, amps, T, checkpoints, p_noise, small=True, L=48):
    rng = random.Random("lat-ph-%s-%s-%s" % (world, seed, small))
    Q = mtm.Q
    n = L * L
    NB = [mtm.nbrs(i, L) for i in range(n)]
    s = [rng.randrange(Q) for _ in range(n)]
    band = world.startswith("W4")
    spread = 0.25 if world.startswith("W3") else 0.0
    amax = max(amps)
    cd = mtm.cd

    def minnd(i):
        si = s[i]
        return min(cd(si, s[j]) for j in NB[i])

    def kick(v):
        if not small:
            return rng.randrange(Q)
        u = 0
        while u == 0:
            u = rng.randint(-KS, KS)
        return (v + u) % Q
    hot = set(i for i in range(n) if minnd(i) < amax)
    snaps = {0: list(s)} if 0 in checkpoints else {}
    for t in range(1, T + 1):
        a = amps[(t - 1) % len(amps)]
        act = [i for i in hot if mtm.lat_is_active(s, i, NB, a, band)]
        chg = set(act)
        if spread > 0:
            for i in act:
                for j in NB[i]:
                    if rng.random() < spread:
                        chg.add(j)
        if p_noise > 0:
            for i in range(n):
                if rng.random() < p_noise:
                    chg.add(i)
        for i in chg:
            s[i] = kick(s[i])
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


def job(args):
    world, cond, seed, g1, g2, T, cps, p_on = args
    t0 = time.time()
    amps = [g2] if cond.startswith("single") else [g1, g2]
    pn = p_on if cond.endswith("noise") else 0.0
    out = {}
    if world == "W1s":
        mtm.EPS = 0.05
        grid = [round(0.1 * k, 3) for k in range(1, int(round(20 * g2)) + 1)]
        snaps, L = mtm.w1_run(seed, amps, T, set(cps), pn)
        for t, (xs, ys) in snaps.items():
            out[t] = mtm.w1_readout(xs, ys, L, grid)
    else:
        grid = list(range(1, 2 * int(g2) + 1))
        snaps, NB = lat_run_small(seed, world, amps, T, set(cps), pn,
                                  small=(world != "W2big"))
        for t, s in snaps.items():
            out[t] = mtm.lat_readout(s, NB, grid)
    return (world, cond, seed, grid, out, time.time() - t0)


def main():
    conds = ["alt", "alt_noise", "single"]
    W1cps = [0, 64, 256, 1024, 4096]
    Lcps = [0, 16, 64, 256, 1024, 4096]
    jobs = []
    for seed in range(1, 6):
        for c in conds:
            jobs.append(("W1s", c, seed, 1.0, 2.0, 4096, W1cps, 0.002))
            for w in ("W2s", "W3s", "W4s", "W2big"):
                jobs.append((w, c, seed, 3, 6, 4096, Lcps, 0.0005))
    raw = []
    with Pool(4) as pool:
        for r in pool.imap_unordered(job, jobs):
            print(r[0], r[1], r[2], "%.1fs" % r[5], flush=True)
            raw.append(r)
    summary = {}
    for w in ("W1s", "W2s", "W3s", "W4s", "W2big"):
        g1, g2 = (1.0, 2.0) if w == "W1s" else (3, 6)
        hs = 2 if w == "W1s" else 1
        thr = 0.05 if w == "W1s" else 0.02
        cps = W1cps if w == "W1s" else Lcps
        summary[w] = {"g1": g1, "g2": g2}
        for c in conds:
            rs = [r for r in raw if r[0] == w and r[1] == c]
            grid = rs[0][3]
            summary[w]["grid"] = grid
            for t in cps:
                C = mtm.mean_curves([r[4][t] for r in rs])
                summary[w]["%s_t%d" % (c, t)] = {
                    "C": [round(v, 5) for v in C],
                    "det": mtm.detect(C, grid, hs, g1, g2, thr)}
    json.dump(summary, open("posthoc.json", "w"), indent=1)
    for w, s in summary.items():
        print("==", w)
        for k, e in s.items():
            if isinstance(e, dict) and "det" in e:
                d = e["det"]
                print("  %-18s g1 %s K=%.3f | g2 %s K=%.3f | bg_sd %.3f" % (
                    k, "Y" if d["g1"]["detected"] else "-", d["g1"]["K"],
                    "Y" if d["g2"]["detected"] else "-", d["g2"]["K"], d["g1"]["bg_sd"]))


if __name__ == "__main__":
    main()
