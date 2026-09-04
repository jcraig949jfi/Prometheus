"""Two supporting analyses for RA-1, both preregistered as reporting duties
rather than as bases for the verdict.

 1. SENSITIVITY. Report the partial that the stability guard suppressed, clearly
    flagged as numerically unreliable, so a reviewer can see whether the guard
    hid a signal rather than a singularity.
 2. K7 REPRODUCTION. Recompute HC-T01's original marginal Spearman numbers from
    the same frozen rows, to prove this re-analysis is reading the same data the
    original verdict was built on.

    python ra1_sensitivity_and_k7.py
"""
import csv
import glob
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.dirname(os.path.dirname(HERE))
GRID = os.path.join(SPEC, "derived", "grid")
COLS = ("tag gen best mean md_on md_off nd_on nd_off mit_on mit_off mia_on "
        "mia_off miu_on miu_off af_on af_off glen nops ousage al_on al_off "
        "minlen geno").split()


def rankavg(xs):
    idx = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and xs[idx[j + 1]] == xs[idx[i]]:
            j += 1
        for k in range(i, j + 1):
            r[idx[k]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def pearson(x, y):
    n = len(x)
    if n < 3:
        return float("nan")
    mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return float("nan")
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def spear(x, y):
    return pearson(rankavg(x), rankavg(y))


def load():
    runs = {}
    for f in sorted(glob.glob(os.path.join(GRID, "*.csv"))):
        p = os.path.basename(f)[:-4].split("_")
        a, b, s = p[0][1:], p[1][1:], int(p[2][1:])
        d = {}
        for line in open(f, encoding="utf-8", errors="replace"):
            q = line.rstrip("\n").split(",", 22)
            if len(q) >= 22:
                r = dict(zip(COLS, q))
                d[int(r["gen"])] = r
        runs[(a, b, s)] = d
    return runs


def main():
    runs = load()
    gens = sorted(next(iter(runs.values())).keys())
    out = {}

    # ---------------- 1. K7 reproduction, exactly the original specification
    print("K7 REPRODUCTION -- HC-T01's original marginal Spearman, beta=0.1 only")
    print("%-8s %-12s %-32s %8s" % ("alpha", "window", "predictor", "rho"))
    k7 = []
    for a in ("0.03", "0.06"):
        seeds = sorted(s for (aa, bb, s) in runs if aa == a and bb == "0.1")
        for (t, t2) in ((100, 500), (50, 200)):
            gain = [float(runs[(a, "0.1", s)][t2]["best"])
                    - float(runs[(a, "0.1", s)][t]["best"]) for s in seeds]
            preds = {
                "current best fitness (cheap)":
                    [float(runs[(a, "0.1", s)][t]["best"]) for s in seeds],
                "avgfit (positive control)":
                    [float(runs[(a, "0.1", s)][t]["af_on"]) for s in seeds],
                "modular degree (accessibility)":
                    [float(runs[(a, "0.1", s)][t]["md_on"]) for s in seeds],
                "mi_aligned (accessibility)":
                    [float(runs[(a, "0.1", s)][t]["mia_on"]) for s in seeds],
                "neutral degree (accessibility)":
                    [float(runs[(a, "0.1", s)][t]["nd_on"]) for s in seeds],
                "operator count (cheap state)":
                    [float(runs[(a, "0.1", s)][t]["nops"]) for s in seeds],
            }
            for k, v in preds.items():
                r = spear(v, gain)
                k7.append(dict(alpha=a, window="%d->%d" % (t, t2),
                               predictor=k, rho=r))
                print("%-8s %-12s %-32s %+8.3f" % (a, "%d->%d" % (t, t2), k, r))
    out["k7_reproduction"] = k7

    # ---------------- 2. sensitivity: unguarded partials
    print("\nSENSITIVITY -- partials with the stability guard REMOVED.")
    print("These are reported as a reviewer aid ONLY. Where |r(F,G)| approaches")
    print("1 the denominator approaches 0 and the value is a numerical artifact,")
    print("not an effect size. It is never a basis for the verdict.\n")
    print("%-24s %5s %4s %4s | %8s %8s %10s %12s"
          % ("cell", "t", "h", "nhr", "r(A,G)", "r(F,G)", "1-r(F,G)^2",
             "unguarded"))
    sens = []
    for (a, b) in sorted(set((x, y) for (x, y, z) in runs)):
        seeds = sorted(s for (aa, bb, s) in runs if aa == a and bb == b)
        for h in (150, 400):
            for t in gens:
                if (t + h) not in runs[(a, b, seeds[0])]:
                    continue
                F = [float(runs[(a, b, s)][t]["best"]) for s in seeds]
                keep = [i for i in range(len(seeds)) if F[i] < 0.0]
                if len(keep) < 15:
                    continue
                A = [float(runs[(a, b, seeds[i])][t]["md_on"]) for i in keep]
                Fs = [F[i] for i in keep]
                G = [float(runs[(a, b, seeds[i])][t + h]["best"]) - F[i]
                     for i in keep]
                if len(set(round(v, 9) for v in G)) < 8:
                    continue
                rAG, rAF, rGF = spear(A, G), spear(A, Fs), spear(G, Fs)
                if rAG != rAG or rGF != rGF:
                    continue
                den = math.sqrt(max(0.0, (1 - rAF ** 2) * (1 - rGF ** 2)))
                val = (rAG - rAF * rGF) / den if den > 1e-12 else float("nan")
                row = dict(cell="alpha=%s_beta=%s" % (a, b), t=t, h=h,
                           n_headroom=len(keep), r_A_G=rAG, r_F_G=rGF,
                           one_minus_rFG2=1 - rGF ** 2, unguarded_partial=val,
                           guard_passed=int(abs(rGF) <= 0.95
                                            and abs(rAF) <= 0.95))
                sens.append(row)
                print("%-24s %5d %4d %4d | %+8.4f %+8.4f %10.5f %12s"
                      % (row["cell"], t, h, len(keep), rAG, rGF,
                         row["one_minus_rFG2"],
                         ("%+.4f" % val) if val == val else "undefined"))
    out["sensitivity_unguarded"] = sens

    with open(os.path.join(HERE, "RA1_SENSITIVITY_AND_K7.csv"), "w",
              newline="", encoding="utf-8") as f:
        keys = sorted({k for r in sens for k in r})
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in sens:
            w.writerow(r)
    json.dump(out, open(os.path.join(HERE, "RA1_SENSITIVITY_AND_K7.json"), "w",
                        encoding="utf-8"), indent=1)
    print("\nwrote RA1_SENSITIVITY_AND_K7.csv and .json")


if __name__ == "__main__":
    main()
