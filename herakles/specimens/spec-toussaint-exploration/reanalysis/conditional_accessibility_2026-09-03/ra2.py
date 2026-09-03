"""RA-2: machinery-presence diagnostic, within the treated arm only.

Exactly as preregistered. No beta=0.0 contrast is used as evidence for A to C.
Reads only frozen HC-T01 rows.

    python ra2.py
"""
import csv
import glob
import json
import math
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.dirname(os.path.dirname(HERE))
GRID = os.path.join(SPEC, "derived", "grid")
COLS = ("tag gen best mean md_on md_off nd_on nd_off mit_on mit_off mia_on "
        "mia_off miu_on miu_off af_on af_off glen nops ousage al_on al_off "
        "minlen geno").split()
MIN_STRATUM = 10          # preregistered


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
    detail = []

    for a in ("0.03", "0.06"):
        cell = "alpha=%s_beta=0.1" % a
        seeds = sorted(s for (aa, bb, s) in runs if aa == a and bb == "0.1")
        obs = []
        for s in seeds:
            for g in gens:
                r = runs[(a, "0.1", s)][g]
                obs.append(dict(seed=s, gen=g, md=float(r["md_on"]),
                                nops=float(r["nops"]),
                                best=float(r["best"])))
        res = {}

        # A. does accessibility scale with nops
        res["A_spearman_md_vs_nops"] = spear([o["nops"] for o in obs],
                                             [o["md"] for o in obs])
        res["A_n"] = len(obs)

        # A2. the same, excluding generation 0 where every run is identical
        o1 = [o for o in obs if o["gen"] > 0]
        res["A_spearman_excl_gen0"] = spear([o["nops"] for o in o1],
                                            [o["md"] for o in o1])

        # C. monotonicity: mean md by integer nops bin
        bins = defaultdict(list)
        for o in obs:
            bins[int(math.floor(o["nops"]))].append(o["md"])
        mono = []
        for k in sorted(bins):
            v = bins[k]
            if len(v) >= MIN_STRATUM:
                mono.append(dict(nops_bin=k, n=len(v),
                                 mean_md=sum(v) / len(v),
                                 min_md=min(v), max_md=max(v)))
        res["C_monotonicity"] = mono
        res["C_is_monotone_increasing"] = all(
            mono[i]["mean_md"] <= mono[i + 1]["mean_md"] + 1e-9
            for i in range(len(mono) - 1)) if len(mono) > 1 else None

        # B. generation trend WITHIN nops strata
        strat = []
        for k in sorted(bins):
            sub = [o for o in obs if int(math.floor(o["nops"])) == k]
            if len(sub) < MIN_STRATUM:
                continue
            rho_gen = spear([o["gen"] for o in sub], [o["md"] for o in sub])
            strat.append(dict(nops_bin=k, n=len(sub),
                              spearman_gen_vs_md_within_stratum=rho_gen,
                              mean_md=sum(o["md"] for o in sub) / len(sub)))
        res["B_generation_trend_within_nops_strata"] = strat
        # unconditional generation trend, for comparison
        res["B_generation_trend_unconditional"] = spear(
            [o["gen"] for o in obs], [o["md"] for o in obs])

        # D. sufficiency: variance of md explained by nops alone (rank R^2),
        #    then whether generation adds anything within strata
        r_nops = res["A_spearman_md_vs_nops"]
        res["D_rank_R2_nops_alone"] = r_nops ** 2 if r_nops == r_nops else None
        within = [s["spearman_gen_vs_md_within_stratum"] for s in strat
                  if s["spearman_gen_vs_md_within_stratum"] ==
                  s["spearman_gen_vs_md_within_stratum"]]
        res["D_mean_abs_within_stratum_gen_effect"] = (
            sum(abs(x) for x in within) / len(within)) if within else None
        res["D_max_abs_within_stratum_gen_effect"] = (
            max(abs(x) for x in within)) if within else None

        out[cell] = res
        for m in mono:
            detail.append(dict(cell=cell, kind="monotonicity", **m))
        for st in strat:
            detail.append(dict(cell=cell, kind="within_stratum_gen_trend", **st))

    # ---- preregistered verdict per cell
    for cell, res in out.items():
        strong = (res["A_spearman_md_vs_nops"] or 0) >= 0.7
        uncond = abs(res["B_generation_trend_unconditional"] or 0)
        within = res["D_mean_abs_within_stratum_gen_effect"] or 0
        collapses = within < 0.5 * uncond if uncond > 0 else None
        if strong and collapses:
            v = "RA2_MACHINERY_COUNT_EXPLAINS_EFFECT"
        elif (not strong) and (collapses is False):
            v = "RA2_HISTORY_EFFECT_SURVIVES_NOPS"
        elif strong and collapses is False:
            v = "RA2_MIXED"
        elif (not strong) and collapses:
            v = "RA2_MIXED"
        else:
            v = "RA2_INDETERMINATE"
        res["verdict"] = v
        res["verdict_inputs"] = dict(
            spearman_md_nops=res["A_spearman_md_vs_nops"],
            uncond_gen_trend=res["B_generation_trend_unconditional"],
            mean_within_stratum_gen_trend=within,
            collapses_by_half=collapses)

    json.dump(out, open(os.path.join(HERE, "RA2_SUMMARY.json"), "w",
                        encoding="utf-8"), indent=1)
    keys = sorted({k for r in detail for k in r})
    with open(os.path.join(HERE, "RA2_DETAIL.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in detail:
            w.writerow(r)

    for cell, res in out.items():
        print("=" * 70)
        print(cell)
        print("  A  spearman(md_on, nops)            = %+.4f   (n=%d)"
              % (res["A_spearman_md_vs_nops"], res["A_n"]))
        print("     excluding generation 0            = %+.4f"
              % res["A_spearman_excl_gen0"])
        print("  B  generation trend, unconditional   = %+.4f"
              % res["B_generation_trend_unconditional"])
        print("     mean |trend| within nops strata   = %+.4f"
              % (res["D_mean_abs_within_stratum_gen_effect"] or float("nan")))
        print("     max  |trend| within nops strata   = %+.4f"
              % (res["D_max_abs_within_stratum_gen_effect"] or float("nan")))
        print("  D  rank R^2 of nops alone            = %.4f"
              % (res["D_rank_R2_nops_alone"] or float("nan")))
        print("  C  monotone increasing in nops       = %s"
              % res["C_is_monotone_increasing"])
        print("     mean md_on by nops bin:")
        for m in res["C_monotonicity"]:
            print("       nops=%d  n=%5d  mean_md=%.4f  [%.3f, %.3f]"
                  % (m["nops_bin"], m["n"], m["mean_md"],
                     m["min_md"], m["max_md"]))
        print("     generation trend within each stratum:")
        for s in res["B_generation_trend_within_nops_strata"]:
            print("       nops=%d  n=%5d  spearman(gen, md)=%+.4f"
                  % (s["nops_bin"], s["n"],
                     s["spearman_gen_vs_md_within_stratum"]))
        print("  VERDICT: %s" % res["verdict"])


if __name__ == "__main__":
    main()
