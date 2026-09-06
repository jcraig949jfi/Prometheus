"""S6 -- SELECTION BIAS UNDER THE FOUNDRY'S ACTUAL PROMOTION RULE.

Harmonia science loop 7, 2026-09-05.

Packet 5 proposed C-7 ("a single passing experiment estimates an upper bound").
That formulation is too strong and is not what was measured. The proposition
actually under test is:

    CONDITIONING ON PROMOTION DISTORTS THE SAMPLING DISTRIBUTION OF THE
    REPORTED EFFECT.

This measures the distortion, for the promotion rule the Foundry would actually
use, and then compares eight candidate defences under an IDENTICAL COMPUTE
BUDGET so the cheapest adequate one can be identified rather than the most
conservative ritual.

KNOWN-EFFECT ORGANISM: two arms of independent normals, arm B shifted by delta.
The true standardised effect IS delta, analytically, with no estimation. That
is the point -- every quantity below is measured against a truth that is known
rather than inferred.

THREE CONCEPTS HELD SEPARATE THROUGHOUT (packet 5 conflated them):
    RELEVANCE FLOOR    smallest effect that would matter if true
    DESIGN EFFECT      the effect used to choose n
    PROMOTION ESTIMATE what an observed sample must show to retain a magnitude
They are NOT assumed equal. SE-1b set all three to 0.5 without noticing.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys

FLOOR = 0.5          # RELEVANCE floor, fixed throughout
ALPHA = 0.05


# --------------------------------------------------------------------------
def draw(n, delta, rng, dist="normal", paired=False):
    """Return (arm_a, arm_b). Truth: standardised mean difference = delta."""
    if paired:
        base = [rng.gauss(0, 1) for _ in range(n)]
        a = [x + rng.gauss(0, 0.3) for x in base]
        b = [x + delta + rng.gauss(0, 0.3) for x in base]
        return a, b
    if dist == "normal":
        return ([rng.gauss(0, 1) for _ in range(n)],
                [rng.gauss(delta, 1) for _ in range(n)])
    if dist == "bounded":
        # beta-like bounded scores, delta expressed on the same sd scale
        a = [min(1, max(0, 0.5 + rng.gauss(0, 0.15))) for _ in range(n)]
        b = [min(1, max(0, 0.5 + delta * 0.15 + rng.gauss(0, 0.15)))
             for _ in range(n)]
        return a, b
    if dist == "skewed":
        a = [math.exp(rng.gauss(0, 0.5)) for _ in range(n)]
        b = [math.exp(rng.gauss(delta * 0.5, 0.5)) for _ in range(n)]
        return a, b
    raise ValueError(dist)


def d_and_ci(a, b):
    """Hedges-corrected standardised difference with a normal-approx CI."""
    n1, n2 = len(a), len(b)
    va, vb = statistics.variance(a), statistics.variance(b)
    sp = (((n1 - 1) * va + (n2 - 1) * vb) / (n1 + n2 - 2)) ** 0.5
    if sp == 0:
        return 0.0, (0.0, 0.0), 1.0
    d = (statistics.fmean(b) - statistics.fmean(a)) / sp
    J = 1 - 3 / (4 * (n1 + n2) - 9)          # small-sample correction
    d *= J
    se = math.sqrt((n1 + n2) / (n1 * n2) + d * d / (2 * (n1 + n2)))
    t = d / se if se else 0.0
    # two-sided p from the normal approximation to the t statistic
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2))))
    return d, (d - 1.96 * se, d + 1.96 * se), p


def promoted(d, p, alpha=ALPHA, floor=FLOOR):
    """THE FOUNDRY'S ACTUAL RULE, as used by SE-1b."""
    return p < alpha and abs(d) >= floor


# ==========================================================================
# PART 1 -- the selection-bias curves
# ==========================================================================
def part1(reps, out):
    print("=" * 78)
    print("PART 1  SELECTION-BIAS CURVES UNDER THE PROMOTION RULE")
    print("        promote iff p < %.2f AND |d| >= %.1f   (relevance floor %.1f)"
          % (ALPHA, FLOOR, FLOOR))
    print("=" * 78)
    rows = []
    DELTAS = [0.0, 0.1, 0.3, 0.5, 0.7, 1.2]
    for n in (16, 32, 64, 128):
        print("\n  n = %d per arm" % n)
        print("   true    mean d    mean d|prom   P(prom)   TypeM   cover   "
              "cover|prom  TypeS")
        for delta in DELTAS:
            rng = random.Random(hash((n, delta)) % 99991)
            all_d, prom_d = [], []
            cov = cov_p = nprom = signerr = 0
            for _ in range(reps):
                a, b = draw(n, delta, rng)
                d, ci, p = d_and_ci(a, b)
                all_d.append(d)
                if ci[0] <= delta <= ci[1]:
                    cov += 1
                if promoted(d, p):
                    nprom += 1
                    prom_d.append(d)
                    if ci[0] <= delta <= ci[1]:
                        cov_p += 1
                    if delta != 0 and (d > 0) != (delta > 0):
                        signerr += 1
                    if delta == 0:
                        pass
            pprom = nprom / reps
            md = statistics.fmean(all_d)
            mdp = statistics.fmean(prom_d) if prom_d else float("nan")
            typem = (abs(mdp) / abs(delta)) if (delta and prom_d) else float("nan")
            row = {"n": n, "delta": delta, "mean_d": md,
                   "mean_d_promoted": mdp, "p_promote": pprom,
                   "type_m": typem, "coverage": cov / reps,
                   "coverage_promoted": (cov_p / nprom) if nprom else float("nan"),
                   "type_s": (signerr / nprom) if nprom else 0.0}
            rows.append(row)
            print("   %.1f    %+.3f     %s     %.3f    %s   %.3f   %s     %.3f"
                  % (delta, md,
                     ("%+.3f" % mdp) if prom_d else "  --  ",
                     pprom,
                     ("%.2f" % typem) if (delta and prom_d) else " -- ",
                     cov / reps,
                     ("%.3f" % (cov_p / nprom)) if nprom else "  --  ",
                     (signerr / nprom) if nprom else 0.0))
    return rows


# ==========================================================================
# PART 2 -- eight defences under an IDENTICAL compute budget
# ==========================================================================
def part2(reps, out, budget=128):
    """budget = worlds per arm available in total, however the design spends it."""
    print("\n" + "=" * 78)
    print("PART 2  EIGHT DEFENCES, IDENTICAL BUDGET OF %d WORLDS PER ARM" % budget)
    print("=" * 78)
    DELTAS = [0.0, 0.3, 0.5, 0.8]
    results = {}

    def run_design(name, fn):
        out_rows = []
        for delta in DELTAS:
            rng = random.Random(hash((name, delta)) % 99991)
            retained, kept, signerr, falsemag, correct_rej, cov = [], 0, 0, 0, 0, 0
            for _ in range(reps):
                claim = fn(delta, rng)
                if claim["retain"]:
                    kept += 1
                    retained.append(claim["d"])
                    if delta and (claim["d"] > 0) != (delta > 0):
                        signerr += 1
                    if delta < FLOOR and abs(claim["d"]) >= FLOOR:
                        falsemag += 1
                    if claim["ci"][0] <= delta <= claim["ci"][1]:
                        cov += 1
                if claim.get("reject_below_floor") and delta < FLOOR:
                    correct_rej += 1
            bias = (statistics.fmean(retained) - delta) if retained else float("nan")
            out_rows.append({
                "delta": delta, "retain_rate": kept / reps,
                "bias": bias,
                "coverage": (cov / kept) if kept else float("nan"),
                "type_s": (signerr / kept) if kept else 0.0,
                "false_magnitude": (falsemag / kept) if kept else 0.0,
                "correct_reject_below_floor": correct_rej / reps})
        results[name] = out_rows
        print("\n  %s" % name)
        print("    true   retain   bias      cover   TypeS   falseMag  "
              "correctRej")
        for r in out_rows:
            print("    %.1f    %.3f   %s   %s   %.3f   %.3f     %.3f"
                  % (r["delta"], r["retain_rate"],
                     ("%+.3f" % r["bias"]) if r["bias"] == r["bias"] else "  --  ",
                     ("%.3f" % r["coverage"]) if r["coverage"] == r["coverage"]
                     else " --  ",
                     r["type_s"], r["false_magnitude"],
                     r["correct_reject_below_floor"]))

    # A. single stage, whole budget
    def A(delta, rng):
        a, b = draw(budget, delta, rng)
        d, ci, p = d_and_ci(a, b)
        return {"retain": promoted(d, p), "d": d, "ci": ci}

    # B. mandatory full replication: half budget each, both must pass,
    #    report the REPLICATION estimate
    def B(delta, rng):
        n = budget // 2
        a1, b1 = draw(n, delta, rng)
        d1, _, p1 = d_and_ci(a1, b1)
        if not promoted(d1, p1):
            return {"retain": False, "d": d1, "ci": (0, 0)}
        a2, b2 = draw(n, delta, rng)
        d2, ci2, p2 = d_and_ci(a2, b2)
        return {"retain": promoted(d2, p2), "d": d2, "ci": ci2}

    # C. discovery/confirmation split declared up front, 50/50, report
    #    confirmation; confirmation tests only DIRECTION at alpha, magnitude
    #    comes from the confirmation estimate
    def C(delta, rng):
        n = budget // 2
        a1, b1 = draw(n, delta, rng)
        d1, _, p1 = d_and_ci(a1, b1)
        if not (p1 < ALPHA):                    # discovery: direction only
            return {"retain": False, "d": d1, "ci": (0, 0)}
        a2, b2 = draw(n, delta, rng)
        d2, ci2, p2 = d_and_ci(a2, b2)
        return {"retain": p2 < ALPHA and abs(d2) >= FLOOR, "d": d2, "ci": ci2}

    # D. discovery large, confirmation small (70/30)
    def D(delta, rng):
        n1 = int(budget * 0.7)
        n2 = budget - n1
        a1, b1 = draw(n1, delta, rng)
        d1, _, p1 = d_and_ci(a1, b1)
        if not (p1 < ALPHA):
            return {"retain": False, "d": d1, "ci": (0, 0)}
        a2, b2 = draw(n2, delta, rng)
        d2, ci2, p2 = d_and_ci(a2, b2)
        return {"retain": p2 < ALPHA and abs(d2) >= FLOOR, "d": d2, "ci": ci2}

    # E. pooled estimate after a direction-only discovery gate
    def E(delta, rng):
        n = budget // 2
        a1, b1 = draw(n, delta, rng)
        d1, _, p1 = d_and_ci(a1, b1)
        if not (p1 < ALPHA):
            return {"retain": False, "d": d1, "ci": (0, 0)}
        a2, b2 = draw(n, delta, rng)
        d2, ci2, p2 = d_and_ci(a2 + a1, b2 + b1)   # pooled magnitude
        return {"retain": p2 < ALPHA and abs(d2) >= FLOOR, "d": d2, "ci": ci2}

    # F1. single stage, but CLAIM ONLY THE CI LOWER BOUND as the magnitude
    def F1(delta, rng):
        a, b = draw(budget, delta, rng)
        d, ci, p = d_and_ci(a, b)
        lo = ci[0] if d > 0 else ci[1]
        keep = p < ALPHA and abs(lo) >= FLOOR
        return {"retain": keep, "d": lo, "ci": ci}

    # F2. single stage with a transparent shrinkage toward zero
    def F2(delta, rng):
        a, b = draw(budget, delta, rng)
        d, ci, p = d_and_ci(a, b)
        se = (ci[1] - ci[0]) / (2 * 1.96)
        shrunk = d * max(0.0, 1 - (se * se) / (d * d)) if d else 0.0
        return {"retain": p < ALPHA and abs(shrunk) >= FLOOR,
                "d": shrunk, "ci": ci}

    # G. estimation-first: no significance gate at all. Retain a magnitude
    #    claim iff the CI lies ENTIRELY above the floor; separately, declare a
    #    SUCCESSFUL NEGATIVE iff the CI lies entirely below it.
    def G(delta, rng):
        a, b = draw(budget, delta, rng)
        d, ci, p = d_and_ci(a, b)
        above = min(abs(ci[0]), abs(ci[1])) >= FLOOR and ci[0] * ci[1] > 0
        below = max(abs(ci[0]), abs(ci[1])) < FLOOR
        return {"retain": above, "d": d, "ci": ci,
                "reject_below_floor": below}

    # H. two-stage sequential with Pocock-adjusted alpha (valid under the
    #    stopping rule), half budget per look
    def H(delta, rng):
        n = budget // 2
        ap = 0.0294                                   # Pocock, 2 looks, 0.05
        a1, b1 = draw(n, delta, rng)
        d1, ci1, p1 = d_and_ci(a1, b1)
        if p1 < ap:
            return {"retain": abs(d1) >= FLOOR, "d": d1, "ci": ci1}
        a2, b2 = draw(n, delta, rng)
        d2, ci2, p2 = d_and_ci(a1 + a2, b1 + b2)
        return {"retain": p2 < ap and abs(d2) >= FLOOR, "d": d2, "ci": ci2}

    for nm, fn in (("A single-stage (current)", A),
                   ("B mandatory full replication", B),
                   ("C 50/50 discovery+confirm", C),
                   ("D 70/30 discovery+confirm", D),
                   ("E direction gate, pooled magnitude", E),
                   ("F1 claim the CI bound", F1),
                   ("F2 shrinkage", F2),
                   ("G estimation-first (CI vs floor)", G),
                   ("H two-stage Pocock", H)):
        run_design(nm, fn)
    return results


# ==========================================================================
# PART 3 -- the successful negative
# ==========================================================================
def part3(reps, budget=128):
    print("\n" + "=" * 78)
    print("PART 3  'REAL BUT TOO SMALL TO MATTER' AS A SUCCESSFUL CONCLUSION")
    print("=" * 78)
    print("  equivalence test (TOST) against the relevance floor %.1f" % FLOOR)
    print("\n   true    P(claim effect)   P(SUCCESSFUL NEGATIVE)   P(inconclusive)")
    rows = []
    for delta in (0.0, 0.1, 0.2, 0.3, 0.5, 0.8):
        rng = random.Random(hash(("p3", delta)) % 99991)
        pos = neg = 0
        for _ in range(reps):
            a, b = draw(budget, delta, rng)
            d, ci, p = d_and_ci(a, b)
            if min(abs(ci[0]), abs(ci[1])) >= FLOOR and ci[0] * ci[1] > 0:
                pos += 1
            elif max(abs(ci[0]), abs(ci[1])) < FLOOR:
                neg += 1
        rows.append({"delta": delta, "p_effect": pos / reps,
                     "p_successful_negative": neg / reps,
                     "p_inconclusive": 1 - (pos + neg) / reps})
        print("   %.1f      %.3f            %.3f                 %.3f"
              % (delta, pos / reps, neg / reps, 1 - (pos + neg) / reps))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=4000)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    # instrument check first: at delta=0 the CI must cover ~95% of the time
    rng = random.Random(1)
    cov = 0
    for _ in range(4000):
        x, y = draw(64, 0.0, rng)
        d, ci, p = d_and_ci(x, y)
        if ci[0] <= 0 <= ci[1]:
            cov += 1
    print("INSTRUMENT CHECK: CI coverage at delta=0, n=64 -> %.3f "
          "(nominal 0.95)\n" % (cov / 4000))

    r1 = part1(a.reps, a.out)
    r2 = part2(a.reps, a.out)
    r3 = part3(a.reps)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"curves": r1, "designs": r2, "successful_negative": r3,
                   "floor": FLOOR, "alpha": ALPHA,
                   "ci_coverage_check": cov / 4000}, f, indent=1)
    print("\nrows: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
