"""Verdicts for S1-S4 from ledgers/*.jsonl against models.py, under the prereg's rules.

Every gate is an interval test: SUPPORTED if the 95% interval of the
statistic lies inside the tolerance, REFUTED if it lies wholly outside,
INDETERMINATE if it straddles (PREREG_SWARM_BOUNDARIES_2026-09-18.md,
"a 95% CI straddling a gate -> INDETERMINATE"). A hypothesis over many
cells is REFUTED if any cell is, else INDETERMINATE if any cell is.
"""
from __future__ import annotations

import json
import math
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import models as M  # noqa: E402

L = HERE / "ledgers"
Z = 1.96


def rows(name):
    return [json.loads(x) for x in (L / f"{name}.jsonl").read_text(encoding="utf-8").splitlines() if x]


def within(point, se, lo, hi):
    a, b = point - Z * se, point + Z * se
    if lo <= a and b <= hi:
        return "SUPPORTED"
    if b < lo or a > hi:
        return "REFUTED"
    return "INDETERMINATE"


def combine(vs):
    vs = list(vs)
    if not vs:
        return "NO_ELIGIBLE_CELLS"
    return "REFUTED" if "REFUTED" in vs else ("INDETERMINATE" if "INDETERMINATE" in vs else "SUPPORTED")


def binse(x, n):
    return math.sqrt(max(x * (1 - x), 1e-12) / n)


def s1():
    cells, a_v, b_v, c_v = [], [], [], []
    for r in rows("s1"):
        d, tau, v, N = r["d"], r["tau"], r["v"], r["N"]
        p = tau * (1 - v)
        r0 = d * p
        sizes = r["sizes"]
        major = [s for s in sizes if s > 0.05 * N]
        pm = len(major) / len(sizes)
        cell = {"d": d, "tau": tau, "v": v, "R0": round(r0, 4), "P_major": pm,
                "model_P_major": M.s1_outbreak_prob(d, p), "n_major": len(major)}
        if major:
            fr = [s / N for s in major]
            cell["final_given_major"] = statistics.fmean(fr)
            cell["final_se"] = statistics.stdev(fr) / math.sqrt(len(fr)) if len(fr) > 1 else 0.0
        cell["model_final"] = M.s1_final_fraction(r0)
        if r0 <= 0.8 and r0 > 0:
            cell["H-S1a"] = within(pm, binse(pm, len(sizes)), -1, 0.05)
            a_v.append(cell["H-S1a"])
        if r0 >= 1.2:
            m = cell["model_P_major"]
            cell["H-S1b"] = within(pm, binse(pm, len(sizes)), m - 0.07, m + 0.07)
            b_v.append(cell["H-S1b"])
            if major:
                z = cell["model_final"]
                cell["H-S1c"] = within(cell["final_given_major"], cell["final_se"], z - 0.05, z + 0.05)
                c_v.append(cell["H-S1c"])
        cells.append(cell)
    boundary = {f"d{d}_tau{t}": M.s1_required_verification(d, t) for d in (2, 4, 8) for t in (0.25, 0.5, 0.75, 1.0)}
    return {"H-S1a": combine(a_v), "H-S1b": combine(b_v), "H-S1c": combine(c_v),
            "required_verification_v_star": boundary, "cells": cells}


def s2a():
    by = {}
    cells, v1, v2 = [], [], []
    for r in rows("s2a"):
        acc = r["accepted_correct"] + r["accepted_wrong"]
        P = M.s2a_precision(r["p"], r["q"], r["t"])
        cell = {k: r[k] for k in ("p", "q", "t", "k")}
        cell.update({"accepted": acc, "model_precision": P})
        if acc >= 400:
            prec = r["accepted_correct"] / acc
            se = binse(P, acc)
            tol = max(0.03, 3 * se)
            cell.update({"precision": prec, "H-S2a1": within(prec, binse(prec, acc), P - tol, P + tol)})
            v1.append(cell["H-S2a1"])
            by.setdefault((r["p"], r["q"], r["t"]), []).append((r["k"], prec, acc, P))
        cells.append(cell)
    for key, lst in by.items():
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                (_, a, na, P), (_, b, nb, _) = lst[i], lst[j]
                sed = math.sqrt(binse(P, na) ** 2 + binse(P, nb) ** 2)
                tol = max(0.04, 3 * sed)
                v2.append(within(a - b, math.sqrt(binse(a, na) ** 2 + binse(b, nb) ** 2), -tol, tol))
    table = {f"q{q}_t{t}": M.s2a_boundary(q, t) for q in (0.005, 0.01, 0.02, 0.05, 0.1) for t in (1.0, 0.8)}
    return {"H-S2a1": combine(v1), "H-S2a2": combine(v2), "solve_rate_boundary_p_star": table,
            "eligible_cells": len(v1), "cells": cells}


def s2b():
    rs = rows("s2b")
    ks = sorted({r["k"] for r in rs})
    out, v1, v2, v3 = {}, [], [], []
    for h in sorted({r["h"] for r in rs}):
        model = M.s2b_accuracy(0.1, h, ks)
        sim = {r["k"]: (r["correct"] / r["n"], r["n"]) for r in rs if r["h"] == h}
        series = []
        for k, m in zip(ks, model):
            a, n = sim[k]
            verdict = within(a - m, binse(a, n), -0.025, 0.025)
            v1.append(verdict)
            series.append({"k": k, "sim": a, "model": m, "H-S2b1": verdict})
        if h == 0.0:
            for x, y in zip(series, series[1:]):
                fall = x["sim"] - y["sim"]
                v2.append(within(fall, math.sqrt(binse(x["sim"], 4000) ** 2 + binse(y["sim"], 4000) ** 2), -1, 0.03))
        k_star = ks[max(range(len(ks)), key=lambda i: model[i])]
        if h in (0.01, 0.05):
            a_star, a_last = sim[k_star][0], sim[1024][0]
            drop = a_star - a_last
            v3.append("REFUTED" if k_star >= 1024 else within(drop, math.sqrt(binse(a_star, 4000) ** 2 + binse(a_last, 4000) ** 2), 0.1, 2))
        out[f"h{h}"] = {"k_star_model": k_star, "series": series}
    return {"H-S2b1": combine(v1), "H-S2b2": combine(v2), "H-S2b3": combine(v3), "by_h": out}


def boot(xs, fn, n=2000, seed=12345):
    rng = random.Random(seed)
    reps = sorted(fn([xs[rng.randrange(len(xs))] for _ in xs]) for _ in range(n))
    return reps[int(0.025 * n)], reps[int(0.975 * n) - 1]


def s3():
    rs = rows("s3a")
    res, va = {}, []
    for g in sorted({r["g"] for r in rs}):
        cells = sorted((r for r in rs if r["g"] == g), key=lambda r: r["a"])
        runs = [r["final_fractions"] for r in cells]
        a_grid = [r["a"] for r in cells]

        def crossing(run_sets):
            for a, fr in zip(a_grid, run_sets):
                if statistics.fmean(fr) < 0.5:
                    return a
            return float("inf")

        point = crossing(runs)
        rng = random.Random(12345)
        reps = sorted(crossing([[fr[rng.randrange(len(fr))] for _ in fr] for fr in runs]) for _ in range(2000))
        lo, hi = reps[50], reps[1949]
        star = M.s3_audit_boundary(g)
        v = "SUPPORTED" if (star - 0.04 <= lo and hi <= star + 0.04) else (
            "REFUTED" if (hi < star - 0.04 or lo > star + 0.04) else "INDETERMINATE")
        va.append(v)
        res[f"g{g}"] = {"a_star_model": star, "crossing": point, "ci95": [lo, hi], "verdict": v,
                        "mean_final_by_a": {a: round(statistics.fmean(fr), 3) for a, fr in zip(a_grid, runs)}}
    pers = {r["c"]: r for r in rows("s3p")}
    runs0 = pers[0.0]["runs"]
    frac_persist = statistics.fmean([1.0 if x["x_end"] >= 0.8 else 0.0 for x in runs0])
    # bug fixed after first run: the gate is ">= 90% of runs"; the first version
    # closed it at 1.0 + 1e-9, so an all-runs result "straddled" an upper bound
    # the prereg never set (first-run verdict INDETERMINATE; see RESULTS).
    h3b = within(frac_persist, binse(frac_persist, len(runs0)), 0.9, math.inf)
    runs1 = pers[0.1]["runs"]
    x0 = statistics.fmean([x["x_at_fix"] for x in runs1])
    model_half = M.s3_persistence_half_gen(x0, 0.1, 0.005, 300)
    halves = [x["half_gen"] if x["half_gen"] is not None else 10 ** 6 for x in runs1]
    med = statistics.median(halves)
    lo, hi = boot(halves, statistics.median)
    never_sim = all(x["half_gen"] is None for x in runs1)
    if math.isinf(model_half) and never_sim:
        # the prereg compared finite medians; when the model predicts no halving
        # and no run halves, the gate is undefined. First-run code printed
        # REFUTED here (inf vs inf). Reported NOT_EVALUABLE with the reason.
        h3c = "NOT_EVALUABLE (model and all runs never halve: honest variant extinct at fix)"
    else:
        h3c = "SUPPORTED" if (0.75 * model_half <= lo and hi <= 1.25 * model_half) else (
            "REFUTED" if (hi < 0.75 * model_half or lo > 1.25 * model_half) else "INDETERMINATE")
    runs2 = pers[0.02]["runs"]
    return {"H-S3a": combine(va), "H-S3b": h3b, "H-S3c": h3c, "by_g": res,
            "persistence": {"c0_fraction_runs_end_ge_0.8": frac_persist,
                            "c0.1_x_at_fix_mean": x0, "c0.1_model_half_gen": model_half,
                            "c0.1_median_half_gen": med, "c0.1_ci95": [lo, hi],
                            "c0.02_end_mean": statistics.fmean([x["x_end"] for x in runs2]),
                            "c0.02_model_equilibrium": M.s3_equilibrium(0.02, 0.005)}}


def s4():
    rs = rows("s4")
    va, vb, vc = [], [], []
    maj = {(r["p"], r["n"], r["rho"]): r["correct"] / r["trials"] for r in rs if r["kind"] == "majority"}
    her = {(r["p"], r["n"]): r["correct"] / r["trials"] for r in rs if r["kind"] == "herding"}
    trials = rs[0]["trials"]
    cells = []
    for (p, n, rho), a in sorted(maj.items()):
        m = M.s4_majority(n, p, rho)
        v = within(a - m, binse(a, trials), -0.015, 0.015)
        va.append(v)
        cells.append({"p": p, "n": n, "rho": rho, "sim": a, "model": m, "H-S4a": v})
    for p in (0.4, 0.45):
        a1, a81 = maj[(p, 1, 0.0)], maj[(p, 81, 0.0)]
        vb.append(within(a1 - a81, math.sqrt(binse(a1, trials) ** 2 + binse(a81, trials) ** 2), 0.05, 2))
    herd = {}
    for p in (0.55, 0.6, 0.7):
        chain = M.s4_herding_last_correct(81, p)
        a = her[(p, 81)]
        vc.append(within(a - chain, binse(a, trials), -0.015, 0.015))
        herd[p] = {"sim_n81": a, "chain_n81": chain, "recalled_closed_form": M.s4_recalled_closed_form(p),
                   "gamblers_ruin_limit": p * p / (p * p + (1 - p) ** 2),
                   "independent_majority_n81": maj[(p, 81, 0.0)],
                   "by_n": {n: her[(p, n)] for n in (1, 3, 9, 27, 81)}}
    gap = maj[(0.7, 81, 0.0)] - her[(0.7, 81)]
    vc.append(within(gap, math.sqrt(binse(maj[(0.7, 81, 0.0)], trials) ** 2 + binse(her[(0.7, 81)], trials) ** 2), 0.1, 2))
    return {"H-S4a": combine(va), "H-S4b": combine(vb), "H-S4c": combine(vc), "herding": herd, "cells": cells}


if __name__ == "__main__":
    out = {"S1": s1(), "S2a": s2a(), "S2b": s2b(), "S3": s3(), "S4": s4()}
    (L / "VERDICTS.json").write_text(json.dumps(out, indent=1, sort_keys=True, default=str), encoding="utf-8")
    for t, b in out.items():
        print(t, {k: v for k, v in b.items() if k.startswith("H-")})
