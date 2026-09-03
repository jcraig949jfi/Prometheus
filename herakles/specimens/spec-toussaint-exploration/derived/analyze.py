#!/usr/bin/env python3
"""HC-T01 primary run-level analysis (X7).

Implements OPERATOR_HISTORY_DID_SPEC.md exactly. The unit of analysis is the
run pair. Nothing here touches exploratory analyses.
"""
import glob
import json
import os
import random
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.dirname(HERE)
CFG = json.load(open(os.path.join(SPEC, "HC_T01_FROZEN_CONFIG.json"), encoding="utf-8"))
CKS = CFG["checkpoints"]
T_EARLY = CFG["primary"]["t_primary_early"]
T_LATE = CFG["primary"]["t_primary_late"]
NPERM = 10000
random.seed(20260903)

COLS = ("tag gen best mean md_on md_off nd_on nd_off mit_on mit_off "
        "mia_on mia_off miu_on miu_off af_on af_off glen nops ousage "
        "al_on al_off minlen geno").split()


def load(pat):
    out = {}
    for f in sorted(glob.glob(os.path.join(HERE, pat))):
        base = os.path.basename(f)[:-4]           # a<alpha>_b<beta>_s<seed>
        a = base.split("_")[0][1:]
        b = base.split("_")[1][1:]
        s = int(base.split("_")[2][1:])
        series = {}
        for line in open(f, encoding="utf-8", errors="replace"):
            p = line.rstrip("\n").split(",", 22)
            if len(p) < 22:
                continue
            d = dict(zip(COLS, p))
            series[int(d["gen"])] = d
        if series:
            out[(a, b, s)] = series
    return out


def perm_test(vals):
    """Two-sided paired permutation test: random sign flips over run pairs."""
    n = len(vals)
    obs = abs(st.mean(vals))
    hits = 0
    for _ in range(NPERM):
        m = sum(v if random.getrandbits(1) else -v for v in vals) / n
        if abs(m) >= obs - 1e-15:
            hits += 1
    return (hits + 1) / (NPERM + 1)


def holm(pvals):
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    out = [None] * len(pvals)
    running = 0.0
    for rank, i in enumerate(order):
        adj = min(1.0, pvals[i] * (len(pvals) - rank))
        running = max(running, adj)
        out[i] = running
    return out


def ci95(vals):
    n = len(vals)
    if n < 2:
        return (float("nan"), float("nan"))
    m = st.mean(vals)
    se = st.stdev(vals) / (n ** 0.5)
    tcrit = 2.045 if n >= 29 else 2.262
    return (m - tcrit * se, m + tcrit * se)


def main():
    runs = load("grid/*.csv")
    alphas = sorted(set(k[0] for k in runs))
    print("loaded %d runs, alphas %s" % (len(runs), alphas))

    noise = {}
    npath = os.path.join(HERE, "noise_floor.json")
    if os.path.exists(npath):
        noise = json.load(open(npath, encoding="utf-8"))

    stats = [("md", "md_on", "md_off", "modular_degree  PRIMARY"),
             ("nd", "nd_on", "nd_off", "neutral_degree"),
             ("mia", "mia_on", "mia_off", "mi_aligned"),
             ("af", "af_on", "af_off", "avgfit  POSITIVE CONTROL")]

    report = {}
    for a in alphas:
        seeds = sorted(s for (aa, b, s) in runs if aa == a and b == "0.1"
                       and (aa, "0.0", s) in runs)
        print("\n" + "=" * 78)
        print("alpha = %s   %d complete run pairs" % (a, len(seeds)))
        print("=" * 78)

        # ---- acquisition, O4
        for t in (T_EARLY, T_LATE, max(CKS)):
            bon = [float(runs[(a, "0.1", s)][t]["best"]) for s in seeds]
            boff = [float(runs[(a, "0.0", s)][t]["best"]) for s in seeds]
            d = [x - y for x, y in zip(bon, boff)]
            lo, hi = ci95(d)
            p = perm_test(d)
            print("O4 acquisition  gen %4d  best_on=%.4f best_off=%.4f  "
                  "diff=%+.4f [%+.4f,%+.4f] p=%.4f"
                  % (t, st.mean(bon), st.mean(boff), st.mean(d), lo, hi, p))

        for key, con, coff, label in stats:
            print("\n  --- %s ---" % label)
            # O1 mechanical contrast at generation zero, common initial pop
            m0 = [float(runs[(a, "0.1", s)][0][con]) - float(runs[(a, "0.1", s)][0][coff])
                  for s in seeds]
            m0b = [float(runs[(a, "0.0", s)][0][con]) - float(runs[(a, "0.0", s)][0][coff])
                   for s in seeds]
            e0 = [x - y for x, y in zip(m0, m0b)]
            print("  O1 M(P_0)  on-history=%+.5f  off-history=%+.5f   E(0)=%+.6f"
                  % (st.mean(m0), st.mean(m0b), st.mean(e0)))

            pv_H, pv_E = [], []
            rows = []
            for t in CKS:
                Hd = [float(runs[(a, "0.1", s)][t][con])
                      - float(runs[(a, "0.0", s)][t][con]) for s in seeds]
                Mon = [float(runs[(a, "0.1", s)][t][con])
                       - float(runs[(a, "0.1", s)][t][coff]) for s in seeds]
                Moff = [float(runs[(a, "0.0", s)][t][con])
                        - float(runs[(a, "0.0", s)][t][coff]) for s in seeds]
                Ed = [x - y for x, y in zip(Mon, Moff)]
                rows.append((t, Hd, Ed, Mon, Moff))
                if t in (T_EARLY, T_LATE):
                    pv_H.append(perm_test(Hd))
                    pv_E.append(perm_test([e - st.mean(e0) for e in Ed]))
            aH = holm(pv_H)
            aE = holm(pv_E)

            nf = noise.get(key, None)
            print("  %6s %12s %22s %12s %10s"
                  % ("gen", "O2 H(t)", "95% CI", "O3 E(t)", "M_on"))
            for (t, Hd, Ed, Mon, Moff) in rows:
                lo, hi = ci95(Hd)
                mark = ""
                if t in (T_EARLY, T_LATE):
                    i = 0 if t == T_EARLY else 1
                    mark = "  pH=%.4f(holm %.4f) pE=%.4f(holm %.4f)" % (
                        pv_H[i], aH[i], pv_E[i], aE[i])
                    if nf:
                        mark += "  |H|/noise=%.1f" % (abs(st.mean(Hd)) / nf)
                print("  %6d %12.5f  [%+9.5f,%+9.5f] %12.5f %10.5f%s"
                      % (t, st.mean(Hd), lo, hi, st.mean(Ed), st.mean(Mon), mark))
            report[(a, key)] = dict(pH=pv_H, pE=pv_E, holmH=aH, holmE=aE)
    return report


if __name__ == "__main__":
    main()
