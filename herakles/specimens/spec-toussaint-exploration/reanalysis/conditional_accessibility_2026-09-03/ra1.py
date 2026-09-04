"""RA-1: conditional prospective accessibility, exactly as preregistered in
RA1_PREREGISTRATION.md. Reads only frozen HC-T01 rows. No evolution is run.

    python ra1.py
"""
import csv
import glob
import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.dirname(os.path.dirname(HERE))
GRID = os.path.join(SPEC, "derived", "grid")

COLS = ("tag gen best mean md_on md_off nd_on nd_off mit_on mit_off mia_on "
        "mia_off miu_on miu_off af_on af_off glen nops ousage al_on al_off "
        "minlen geno").split()

HORIZONS = [150, 400]          # preregistered, inherited from HC-T01 K7 windows
E1_MIN_HEADROOM = 15
E2_MIN_DISTINCT = 8
STABILITY = 0.95
NBOOT = 2000
NPERM = 2000
random.seed(20260903)


# ------------------------------------------------------------------ rank stats
def rankavg(xs):
    idx = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and xs[idx[j + 1]] == xs[idx[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[idx[k]] = avg
        i = j + 1
    return r


def pearson(x, y):
    n = len(x)
    if n < 3:
        return float("nan")
    mx = sum(x) / n
    my = sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return float("nan")
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def spearman(x, y):
    return pearson(rankavg(x), rankavg(y))


def partial_spearman(A, G, F):
    """rho of A with G, conditioning on F, all rank-based."""
    rAG, rAF, rGF = spearman(A, G), spearman(A, F), spearman(G, F)
    for r in (rAG, rAF, rGF):
        if r != r:
            return float("nan"), rAG, rAF, rGF, "NAN_INPUT"
    if abs(rGF) > STABILITY or abs(rAF) > STABILITY:
        return float("nan"), rAG, rAF, rGF, "UNSTABLE"
    den = math.sqrt((1 - rAF ** 2) * (1 - rGF ** 2))
    if den == 0:
        return float("nan"), rAG, rAF, rGF, "ZERO_DENOM"
    return (rAG - rAF * rGF) / den, rAG, rAF, rGF, "OK"


# ------------------------------------------------------------------- data
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
    cells = sorted(set((a, b) for (a, b, s) in runs))

    ts_rows, nc_rows = [], []
    per_cell = {}

    for (a, b) in cells:
        cell = "alpha=%s_beta=%s" % (a, b)
        seeds = sorted(s for (aa, bb, s) in runs if aa == a and bb == b)
        per_cell[cell] = {}
        for h in HORIZONS:
            pts = []
            for t in gens:
                if (t + h) not in runs[(a, b, seeds[0])]:
                    continue
                A = [float(runs[(a, b, s)][t]["md_on"]) for s in seeds]
                F = [float(runs[(a, b, s)][t]["best"]) for s in seeds]
                G = [float(runs[(a, b, s)][t + h]["best"]) - F[i]
                     for i, s in enumerate(seeds)]
                Ah = [float(runs[(a, b, s)][t + h]["md_on"]) for s in seeds]

                keep = [i for i in range(len(seeds)) if F[i] < 0.0]
                nhead = len(keep)
                gsub = [G[i] for i in keep]
                ndist = len(set(round(v, 9) for v in gsub))

                elig = (nhead >= E1_MIN_HEADROOM and ndist >= E2_MIN_DISTINCT)

                rec = dict(cell=cell, alpha=a, beta=b, t=t, h=h,
                           n_total=len(seeds), n_headroom=nhead,
                           n_distinct_gain=ndist,
                           frac_at_ceiling=1.0 - nhead / len(seeds),
                           eligible=int(elig))

                if elig:
                    As, Gs, Fs = ([A[i] for i in keep], gsub,
                                  [F[i] for i in keep])
                    rp, rAG, rAF, rGF, st = partial_spearman(As, Gs, Fs)
                    rec.update(marginal_A_G=rAG, marginal_F_G=rGF,
                               marginal_A_F=rAF, partial_A_G_given_F=rp,
                               status=st)
                    # secondary: all 30 runs, for K7 comparability
                    rp_all, rAG_all, _, rGF_all, st_all = partial_spearman(A, G, F)
                    rec.update(all30_marginal_A_G=rAG_all,
                               all30_marginal_F_G=rGF_all,
                               all30_partial=rp_all, all30_status=st_all)
                    # bootstrap
                    if st == "OK":
                        bs = []
                        for _ in range(NBOOT):
                            idx = [random.randrange(len(keep))
                                   for _ in range(len(keep))]
                            v, _, _, _, s2 = partial_spearman(
                                [As[i] for i in idx], [Gs[i] for i in idx],
                                [Fs[i] for i in idx])
                            if s2 == "OK" and v == v:
                                bs.append(v)
                        if len(bs) > 100:
                            bs.sort()
                            rec["ci_lo"] = bs[int(0.025 * len(bs))]
                            rec["ci_hi"] = bs[int(0.975 * len(bs))]
                        pts.append((t, rp, st))
                    # NC1 reverse precedence, same subset
                    Ahs = [Ah[i] for i in keep]
                    rp_nc, rAG_nc, _, _, st_nc = partial_spearman(Ahs, Gs, Fs)
                    nc_rows.append(dict(cell=cell, t=t, h=h, control="NC1_reverse",
                                        n=len(keep), marginal=rAG_nc,
                                        partial=rp_nc, status=st_nc))
                ts_rows.append(rec)

            # series statistic + NC2 permutation
            ok = [(t, v) for (t, v, st) in pts if st == "OK" and v == v]
            entry = dict(n_eligible_points=len(ok),
                         points=[t for t, _ in ok],
                         values=[v for _, v in ok])
            if len(ok) >= 2:
                obs = sum(v for _, v in ok) / len(ok)
                entry["mean_partial"] = obs
                entry["sign_consistent"] = all(
                    (v > 0) == (obs > 0) for _, v in ok)
                # cross-seed permutation preserving each run's time series
                cnt = 0
                for _ in range(NPERM):
                    perm = seeds[:]
                    random.shuffle(perm)
                    vals = []
                    for t, _ in ok:
                        A = [float(runs[(a, b, s)][t]["md_on"]) for s in perm]
                        F = [float(runs[(a, b, s)][t]["best"]) for s in seeds]
                        G = [float(runs[(a, b, s)][t + h]["best"])
                             - float(runs[(a, b, s)][t]["best"]) for s in seeds]
                        keep = [i for i in range(len(seeds)) if F[i] < 0.0]
                        v, _, _, _, st = partial_spearman(
                            [A[i] for i in keep], [G[i] for i in keep],
                            [F[i] for i in keep])
                        if st == "OK" and v == v:
                            vals.append(v)
                    if vals and abs(sum(vals) / len(vals)) >= abs(obs) - 1e-12:
                        cnt += 1
                entry["perm_p_two_sided"] = (cnt + 1) / (NPERM + 1)
                nc_rows.append(dict(cell=cell, t="series", h=h,
                                    control="NC2_cross_seed_perm",
                                    n=NPERM, marginal="",
                                    partial=entry["perm_p_two_sided"],
                                    status="p_value"))
            else:
                entry["verdict_note"] = ("fewer than two eligible points; "
                                         "INDETERMINATE by preregistration")
            per_cell[cell]["h=%d" % h] = entry

    # write outputs
    keys = sorted({k for r in ts_rows for k in r})
    with open(os.path.join(HERE, "RA1_TIME_SERIES.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in ts_rows:
            w.writerow(r)
    nkeys = sorted({k for r in nc_rows for k in r})
    with open(os.path.join(HERE, "RA1_NEGATIVE_CONTROLS.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=nkeys)
        w.writeheader()
        for r in nc_rows:
            w.writerow(r)
    json.dump(per_cell, open(os.path.join(HERE, "RA1_SUMMARY.json"), "w",
                             encoding="utf-8"), indent=1)

    # console
    print("ELIGIBILITY AND CONDITIONAL RESULT, per cell and horizon\n")
    for cell in per_cell:
        for hk, e in per_cell[cell].items():
            print("%-24s %-6s eligible_points=%d %s"
                  % (cell, hk, e["n_eligible_points"],
                     ("mean_partial=%+.4f sign_consistent=%s perm_p=%.4f"
                      % (e["mean_partial"], e["sign_consistent"],
                         e["perm_p_two_sided"]))
                     if e["n_eligible_points"] >= 2 else "-> INDETERMINATE"))
    print("\nPER-POINT DETAIL (eligible points only)\n")
    print("%-24s %5s %4s %4s %4s | %8s %8s %8s | %8s %8s"
          % ("cell", "t", "h", "nhr", "ceil", "r(A,G)", "r(F,G)",
             "partial", "ci_lo", "ci_hi"))
    for r in ts_rows:
        if r["eligible"]:
            print("%-24s %5d %4d %4d %4.2f | %8.4f %8.4f %8s | %8s %8s"
                  % (r["cell"], r["t"], r["h"], r["n_headroom"],
                     r["frac_at_ceiling"], r["marginal_A_G"], r["marginal_F_G"],
                     ("%.4f" % r["partial_A_G_given_F"])
                     if r.get("status") == "OK" else r.get("status"),
                     ("%.3f" % r["ci_lo"]) if "ci_lo" in r else "-",
                     ("%.3f" % r["ci_hi"]) if "ci_hi" in r else "-"))


if __name__ == "__main__":
    main()
