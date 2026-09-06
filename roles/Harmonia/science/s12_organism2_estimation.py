"""S12 -- ORGANISM 2: the licensing band, estimator bias, transforms, drift.

Harmonia science loop 12, 2026-09-05. Pure simulation; the engine is not the
instrument here and is not used.

  ITEM 2  Sample the P(promote) >= 0.8 band on organism 2. S10 could not: it
          used greedy vs rotate, true d = 0.329, BELOW the 0.5 floor, so
          promotion never rose above 0.05 and the only band the selection law
          is used to LICENSE a claim in went untested. spread vs greedy is
          d ~ +0.899 on the same organism, which reaches it.
  ITEM 5  Estimator bias on a trajectory-valued, bounded, serially coupled
          outcome. S8 found estimator bias is a 3.1x channel independent of
          selection, but measured it on synthetic draws.
  ITEM 6  Measurement TRANSFORMS -- log, rank, clip, round -- which R10 pins
          and which nobody has ever perturbed. Noise was sign-class on
          organism 1 and inert on organism 2; transforms are more common in
          practice than injected noise.
  ITEM 8  NON-STATIONARY worlds: regeneration drifts with campaign order, so
          "the same world" is false in a way neither organism covered.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0] if "/" in __file__ else ".")
from s10_second_organism import new_world, step, PLAYERS, STEPS, BUDGET  # noqa

FLOOR, ALPHA = 0.5, 0.05


def run_arm(player, nworlds, seed_off, steps=STEPS, noise=0.0, regen=0.25,
            drift=0.0, transform=None):
    tot = []
    for w in range(nworlds):
        r = regen + drift * w              # ITEM 8: world properties drift
        world = new_world(seed_off + w, regen=r)
        rng = random.Random("t|%s|%s" % (player, seed_off + w))
        rew = PLAYERS[player](world, steps, seed_off + w, noise)
        v = sum(rew)
        if transform == "log":
            v = math.log1p(max(0.0, v))
        elif transform == "clip":
            v = min(v, 12.0)
        elif transform == "round":
            v = round(v)
        tot.append(v)
    return tot


def hedges(a, b):
    n1, n2 = len(a), len(b)
    va, vb = statistics.variance(a), statistics.variance(b)
    sp = (((n1 - 1) * va + (n2 - 1) * vb) / (n1 + n2 - 2)) ** 0.5
    if sp == 0:
        return 0.0
    d = (statistics.fmean(b) - statistics.fmean(a)) / sp
    return d * (1 - 3 / (4 * (n1 + n2) - 9))


def raw(a, b):
    n1, n2 = len(a), len(b)
    va, vb = statistics.variance(a), statistics.variance(b)
    sp = (((n1 - 1) * va + (n2 - 1) * vb) / (n1 + n2 - 2)) ** 0.5
    return (statistics.fmean(b) - statistics.fmean(a)) / sp if sp else 0.0


def trimmed(a, b):
    def tr(x):
        x = sorted(x)
        k = int(len(x) * 0.2)
        return x[k:len(x) - k] if len(x) - 2 * k >= 2 else x
    ta, tb = tr(a), tr(b)
    va, vb = statistics.variance(ta), statistics.variance(tb)
    sp = ((va + vb) / 2) ** 0.5
    return (statistics.fmean(tb) - statistics.fmean(ta)) / sp if sp else 0.0


def rank(a, b):
    n1, n2 = len(a), len(b)
    wins = sum(1 for x in a for y in b if y > x)
    ties = sum(1 for x in a for y in b if y == x)
    auc = min(max((wins + 0.5 * ties) / (n1 * n2), 1e-6), 1 - 1e-6)
    lo, hi = -8.0, 8.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if 0.5 * (1 + math.erf(mid / math.sqrt(2))) < auc:
            lo = mid
        else:
            hi = mid
    return ((lo + hi) / 2) * math.sqrt(2)


ESTS = {"hedges": hedges, "raw": raw, "trimmed": trimmed, "rank": rank}


def perm_p(a, b, iters=800, rng=None):
    rng = rng or random.Random(0)
    obs = abs(statistics.fmean(a) - statistics.fmean(b))
    pool = list(a) + list(b)
    n = len(a)
    hits = 0
    for _ in range(iters):
        rng.shuffle(pool)
        if abs(statistics.fmean(pool[:n]) - statistics.fmean(pool[n:])) >= obs:
            hits += 1
    return (hits + 1) / (iters + 1)


def truth_for(pa, pb, est=hedges, blocks=30, nw=60, **kw):
    ds = []
    for k in range(blocks):
        a = run_arm(pa, nw, 700000 + 5000 * k, **kw)
        b = run_arm(pb, nw, 700000 + 5000 * k, **kw)
        ds.append(est(a, b))
    return statistics.fmean(ds)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = {}

    # ==================================================================
    print("=" * 78)
    print("ITEM 2  THE >=0.8 LICENSING BAND ON ORGANISM 2 (spread vs greedy)")
    print("=" * 78)
    T = truth_for("greedy", "spread")
    print("\n  reference truth d(spread - greedy) = %+.3f  (floor %.1f)\n" % (T, FLOOR))
    print("   n/arm   P(promote)   Type M    selection inflation")
    rows = []
    for nw in (6, 12, 20, 40, 80):
        prom, allest = [], []
        for i in range(200):
            x = run_arm("greedy", nw, 900000 + i * 700)
            y = run_arm("spread", nw, 900000 + i * 700)
            d = hedges(x, y)
            allest.append(d)
            if perm_p(x, y, 400, random.Random(i)) < ALPHA and abs(d) >= FLOOR:
                prom.append(d)
        pp = len(prom) / 200
        tm = (statistics.fmean(prom) / T) if prom else float("nan")
        sel = (statistics.fmean(prom) / statistics.fmean(allest)) if prom else float("nan")
        rows.append({"n": nw, "p_promote": pp, "type_m": tm, "selection": sel})
        print("   %5d     %.3f       %s      %s"
              % (nw, pp, ("%.2f" % tm) if tm == tm else " -- ",
                 ("%.2f" % sel) if sel == sel else " -- "))
    out["item2"] = {"truth": T, "rows": rows}
    hi = [r for r in rows if r["p_promote"] >= 0.8]
    print("\n  organism 1's law: P(promote)>=0.8 -> Type M ~1.02")
    if hi:
        print("  organism 2 in that band: Type M %s"
              % ", ".join("%.2f" % r["type_m"] for r in hi))
    else:
        print("  band still not reached")

    # ==================================================================
    print("\n" + "=" * 78)
    print("ITEM 5  ESTIMATOR BIAS ON A TRAJECTORY-VALUED OUTCOME")
    print("=" * 78)
    print("\n  estimator   reference truth   mean over runs   uncond bias")
    e5 = []
    for name, est in ESTS.items():
        t = truth_for("greedy", "spread", est=est)
        vals = [est(run_arm("greedy", 40, 1200000 + i * 900),
                    run_arm("spread", 40, 1200000 + i * 900)) for i in range(40)]
        m = statistics.fmean(vals)
        e5.append({"est": name, "truth": t, "mean": m,
                   "bias_ratio": (m / t) if t else float("nan")})
        print("  %-10s    %+.3f            %+.3f          %.2fx"
              % (name, t, m, m / t if t else float("nan")))
    out["item5"] = e5
    print("\n  each estimator is compared to ITS OWN estimand, so a ratio far")
    print("  from 1.0 is small-sample bias rather than a different target.")
    print("  organism 1 worst case: trimmed on heavy tails, 3.10x")

    # ==================================================================
    print("\n" + "=" * 78)
    print("ITEM 6  MEASUREMENT TRANSFORMS -- never previously perturbed")
    print("=" * 78)
    base = statistics.fmean([hedges(run_arm("greedy", 40, 20000 + 1000 * k),
                                    run_arm("spread", 40, 20000 + 1000 * k))
                             for k in range(5)])
    sd = statistics.stdev([hedges(run_arm("greedy", 40, 20000 + 1000 * k),
                                  run_arm("spread", 40, 20000 + 1000 * k))
                           for k in range(5)])
    se = sd / 5 ** 0.5
    print("\n  baseline d = %+.3f  (SE %.3f, material > %.3f)\n" % (base, se, 2 * se))
    print("  transform            d        delta     class")
    print("  " + "-" * 52)
    e6 = []
    for tname in ("log", "clip", "round"):
        ds = [hedges(run_arm("greedy", 40, 20000 + 1000 * k, transform=tname),
                     run_arm("spread", 40, 20000 + 1000 * k, transform=tname))
              for k in range(5)]
        m = statistics.fmean(ds)
        delta = m - base
        klass = ("SIGN" if (m > 0) != (base > 0)
                 else ("MAGNITUDE" if abs(delta) > 2 * se else "INERT"))
        e6.append({"transform": tname, "d": m, "delta": delta, "class": klass})
        print("  %-18s %+.3f   %+.3f    %s" % (tname, m, delta, klass))
    # rank estimator IS a transform of the outcome scale
    dr = statistics.fmean([rank(run_arm("greedy", 40, 20000 + 1000 * k),
                                run_arm("spread", 40, 20000 + 1000 * k))
                           for k in range(5)])
    e6.append({"transform": "rank(estimator)", "d": dr, "delta": dr - base,
               "class": "SIGN" if (dr > 0) != (base > 0)
               else ("MAGNITUDE" if abs(dr - base) > 2 * se else "INERT")})
    print("  %-18s %+.3f   %+.3f    %s"
          % ("rank(estimator)", dr, dr - base, e6[-1]["class"]))
    out["item6"] = e6

    # ==================================================================
    print("\n" + "=" * 78)
    print("ITEM 8  NON-STATIONARY WORLDS: regeneration drifts with run order")
    print("=" * 78)
    print("\n   drift/world   d(spread-greedy)   delta vs stationary   class")
    e8 = []
    for drift in (0.0, 0.002, 0.005, 0.01):
        ds = [hedges(run_arm("greedy", 40, 30000 + 1000 * k, drift=drift),
                     run_arm("spread", 40, 30000 + 1000 * k, drift=drift))
              for k in range(5)]
        m = statistics.fmean(ds)
        e8.append({"drift": drift, "d": m})
        d0 = e8[0]["d"]
        klass = ("baseline" if drift == 0 else
                 ("SIGN" if (m > 0) != (d0 > 0)
                  else ("MAGNITUDE" if abs(m - d0) > 2 * se else "INERT")))
        print("   %8.3f      %+.3f              %+.3f            %s"
              % (drift, m, m - d0, klass))
    out["item8"] = e8
    print("\n  drift also makes world k and world k+n different worlds while")
    print("  every recorded identity field (seed_root, policy, spec) is equal.")

    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("\nrows: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
