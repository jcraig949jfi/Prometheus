"""S10 -- A SECOND ORGANISM: do the constraints survive, or were they facts
about bitstrings?

Harmonia science loop 10, 2026-09-05.

Every scientific finding in S1-S9 rests on ONE model organism: a bitstring
hill-climber on a matching landscape. By my own taxonomy that is L3-at-best
evidence for constraints I have been proposing as general. This builds a second
organism that shares as little structure with the first as I can manage, and
pushes it through the IDENTICAL machinery.

ORGANISM 1 (all prior loops)     ORGANISM 2 (here)
  discrete binary state            continuous multi-dimensional allocation
  static hidden target             patches that DEPLETE and REGENERATE
  score = final state quality      score = cumulative harvest over a trajectory
  decisions independent            decisions coupled by a shared budget
  only the PLAYER can hold state   the ENVIRONMENT holds state; players need not
  no time dynamics                 the world evolves whether or not you act

That last inversion is the point. S3's headline was player state leaking across
worlds. Here the WORLD is the stateful thing, which is the mirror image, and it
tests whether the machinery was detecting a general phenomenon or one specific
plumbing arrangement.

THREE CONSTRAINTS PUT AT RISK, chosen because they are the ones I have been
recommending most confidently:

  T1  unit of analysis: does pseudo-replication still inflate at the same rate
      when observations within a world are coupled by depletion rather than by
      sharing a draw?
  T2  the perturbation classification (inert / magnitude / sign): does the
      CLASSIFICATION transport, or only the method of producing it?
  T3  the selection law, Type M as a function of P(promote).
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys

# ==========================================================================
# THE ORGANISM: N patches. Each holds a stock that regenerates logistically
# and is depleted by harvesting. A player splits a fixed per-step effort
# budget across patches. Reward is what it actually harvests, so the score is
# a property of the whole trajectory and of choices made many steps earlier.
# ==========================================================================
NPATCH, STEPS, BUDGET = 6, 40, 1.0


def new_world(seed, npatch=NPATCH, regen=0.25, cap=1.0):
    r = random.Random("w|%s" % seed)
    return {"stock": [r.uniform(0.3, 1.0) for _ in range(npatch)],
            "regen": regen, "cap": cap, "npatch": npatch,
            "quality": [r.uniform(0.5, 1.5) for _ in range(npatch)]}


def step(world, alloc, noise=0.0, rng=None):
    """Harvest, then regenerate. Returns the reward for this step."""
    got = 0.0
    for i, a in enumerate(alloc):
        take = min(world["stock"][i], a * world["quality"][i])
        world["stock"][i] -= take
        got += take
    for i in range(world["npatch"]):
        s = world["stock"][i]
        world["stock"][i] = min(world["cap"],
                                s + world["regen"] * s * (1 - s / world["cap"]))
    if noise and rng:
        got += rng.gauss(0, noise)
    return got


# ---- players. Deliberately NOT hill-climbers. ----------------------------
def p_greedy(world, steps, seed, noise=0.0):
    """Put the whole budget on the patch with the largest immediate yield."""
    rng = random.Random("g|%s" % seed)
    out = []
    for _ in range(steps):
        yields = [world["stock"][i] * world["quality"][i]
                  for i in range(world["npatch"])]
        best = max(range(world["npatch"]), key=lambda i: yields[i])
        alloc = [0.0] * world["npatch"]
        alloc[best] = BUDGET
        out.append(step(world, alloc, noise, rng))
    return out


def p_spread(world, steps, seed, noise=0.0):
    """Split the budget evenly -- never depletes any single patch."""
    rng = random.Random("s|%s" % seed)
    out = []
    for _ in range(steps):
        alloc = [BUDGET / world["npatch"]] * world["npatch"]
        out.append(step(world, alloc, noise, rng))
    return out


def p_rotate(world, steps, seed, noise=0.0):
    """Harvest one patch at a time in rotation, giving each time to regrow."""
    rng = random.Random("r|%s" % seed)
    out = []
    for t in range(steps):
        alloc = [0.0] * world["npatch"]
        alloc[t % world["npatch"]] = BUDGET
        out.append(step(world, alloc, noise, rng))
    return out


PLAYERS = {"greedy": p_greedy, "spread": p_spread, "rotate": p_rotate}


# ==========================================================================
def cohen_d(a, b):
    va, vb = statistics.variance(a), statistics.variance(b)
    sp = (((len(a) - 1) * va + (len(b) - 1) * vb) / (len(a) + len(b) - 2)) ** 0.5
    return (statistics.fmean(b) - statistics.fmean(a)) / sp if sp else 0.0


def perm_p(a, b, iters=2000, rng=None):
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


def run_arm(player, nworlds, seed_off, **kw):
    """Returns (per-world totals, per-step rewards flattened)."""
    tot, flat = [], []
    for w in range(nworlds):
        world = new_world(seed_off + w, **{k: v for k, v in kw.items()
                                           if k in ("npatch", "regen", "cap")})
        rew = PLAYERS[player](world, kw.get("steps", STEPS), seed_off + w,
                              kw.get("noise", 0.0))
        tot.append(sum(rew))
        flat += rew
    return tot, flat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--reps", type=int, default=300)
    a = ap.parse_args()
    out = {}

    print("=" * 78)
    print("S10  SECOND ORGANISM -- depleting patches, coupled budget,")
    print("     trajectory-valued score, STATEFUL WORLD / stateless players")
    print("=" * 78)

    # sanity: the organism must actually produce a phenomenon
    base = {}
    for p in PLAYERS:
        tot, _ = run_arm(p, 40, 1000)
        base[p] = statistics.fmean(tot)
    print("\n  mean total harvest over 40 worlds:")
    for p, v in sorted(base.items(), key=lambda kv: -kv[1]):
        print("      %-8s %.3f" % (p, v))
    order = [p for p, _ in sorted(base.items(), key=lambda kv: -kv[1])]
    print("  ordering: %s" % " > ".join(order))
    out["baseline"] = base

    # ==================================================================
    # T1 -- does pseudo-replication still inflate, with a DIFFERENT
    #       coupling mechanism (depletion, not a shared draw)?
    # ==================================================================
    print("\n" + "=" * 78)
    print("T1  UNIT OF ANALYSIS under a KNOWN NULL (same player both arms)")
    print("=" * 78)
    fp_world = fp_step = 0
    for i in range(a.reps):
        # both arms are the SAME player on DIFFERENT worlds -> null
        ta, fa = run_arm("greedy", 6, 5000 + i * 100)
        tb, fb = run_arm("greedy", 6, 8000 + i * 100)
        rng = random.Random(i)
        if perm_p(ta, tb, 600, rng) < 0.05:
            fp_world += 1
        if perm_p(fa, fb, 600, rng) < 0.05:
            fp_step += 1
    r_world, r_step = fp_world / a.reps, fp_step / a.reps
    print("  %d known-null campaigns, 6 worlds x %d steps per arm" % (a.reps, STEPS))
    print("  unit = WORLD (n=6/arm)          false positive rate: %.3f" % r_world)
    print("  unit = STEP  (n=%d/arm)        false positive rate: %.3f"
          % (6 * STEPS, r_step))
    print("  organism 1 measured 0.050 (world) vs 0.517 (observation)")
    out["T1"] = {"world": r_world, "step": r_step}
    verdict1 = ("SURVIVES" if r_step > 2 * max(r_world, 0.05) else "DOES NOT")
    print("\n  CONSTRAINT 'declare the unit' -> %s on organism 2" % verdict1)

    # ==================================================================
    # T2 -- does the PERTURBATION CLASSIFICATION transport?
    # ==================================================================
    print("\n" + "=" * 78)
    print("T2  PERTURBATION CLASSIFICATION -- greedy vs spread")
    print("=" * 78)
    NW = 40

    def eff(**kw):
        ds = []
        for k in range(5):
            ta, _ = run_arm("greedy", NW, 20000 + 1000 * k, **kw)
            tb, _ = run_arm("spread", NW, 20000 + 1000 * k, **kw)
            ds.append(cohen_d(ta, tb))
        return statistics.fmean(ds), statistics.stdev(ds)

    b_m, b_sd = eff()
    se = b_sd / 5 ** 0.5
    print("\n  baseline d(spread - greedy) = %+.3f  (SE %.3f, material > %.3f)"
          % (b_m, se, 2 * se))
    PERT = [("seed stream (new blocks)", dict(_seedshift=True)),
            ("scoring scale x100", dict(_scale=True)),
            ("observation noise sd=0.02", dict(noise=0.02)),
            ("observation noise sd=0.20", dict(noise=0.20)),
            ("horizon 40 -> 10 steps", dict(steps=10)),
            ("horizon 40 -> 120 steps", dict(steps=120)),
            ("patches 6 -> 24", dict(npatch=24)),
            ("regeneration 0.25 -> 0.05", dict(regen=0.05)),
            ("regeneration 0.25 -> 0.60", dict(regen=0.60))]
    rows = []
    print("  perturbation                       d        delta     class")
    print("  " + "-" * 66)
    for label, kw in PERT:
        if kw.pop("_seedshift", False):
            ds = []
            for k in range(5):
                ta, _ = run_arm("greedy", NW, 90000 + 1000 * k)
                tb, _ = run_arm("spread", NW, 90000 + 1000 * k)
                ds.append(cohen_d(ta, tb))
            m, sd = statistics.fmean(ds), statistics.stdev(ds)
        elif kw.pop("_scale", False):
            m, sd = b_m, b_sd            # d is scale-invariant by construction
        else:
            m, sd = eff(**kw)
        delta = m - b_m
        if (m > 0) != (b_m > 0):
            klass = "SIGN"
        elif abs(delta) > 2 * se:
            klass = "MAGNITUDE"
        else:
            klass = "INERT"
        rows.append({"perturbation": label, "d": m, "delta": delta,
                     "class": klass})
        print("  %-32s %+.3f   %+.3f    %s" % (label, m, delta, klass))
    out["T2"] = rows
    n_sign = sum(1 for r in rows if r["class"] == "SIGN")
    n_inert = sum(1 for r in rows if r["class"] == "INERT")
    print("\n  organism 1: 3 inert, 2 magnitude, 5 SIGN of 10")
    print("  organism 2: %d inert, %d magnitude, %d SIGN of %d"
          % (n_inert, len(rows) - n_inert - n_sign, n_sign, len(rows)))

    # ==================================================================
    # T3 -- the selection law on this organism
    # ==================================================================
    print("\n" + "=" * 78)
    print("T3  SELECTION LAW: Type M vs P(promote), organism 2")
    print("=" * 78)
    FLOOR, ALPHA = 0.5, 0.05
    print("\n   n/arm   true d    P(promote)   Type M")
    t3 = []
    for nw in (6, 12, 30, 80):
        # establish 'truth' for this contrast at this n by a large reference
        ref = []
        for k in range(40):
            ta, _ = run_arm("greedy", 60, 300000 + 1000 * k)
            tb, _ = run_arm("rotate", 60, 300000 + 1000 * k)
            ref.append(cohen_d(ta, tb))
        truth = statistics.fmean(ref)
        prom, n_pro = [], 0
        for i in range(120):
            ta, _ = run_arm("greedy", nw, 400000 + i * 500)
            tb, _ = run_arm("rotate", nw, 400000 + i * 500)
            d = cohen_d(ta, tb)
            p = perm_p(ta, tb, 400, random.Random(i))
            if p < ALPHA and abs(d) >= FLOOR:
                n_pro += 1
                prom.append(d)
        pp = n_pro / 120
        tm = (statistics.fmean(prom) / truth) if prom and truth else float("nan")
        t3.append({"n": nw, "truth": truth, "p_promote": pp, "type_m": tm})
        print("   %5d   %+.3f     %.3f       %s"
              % (nw, truth, pp, ("%.2f" % tm) if tm == tm else " -- "))
    out["T3"] = t3
    print("\n  organism 1 law: P(prom)<0.2 -> TypeM ~3.7 ; >=0.8 -> ~1.0")

    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("\nrows: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
