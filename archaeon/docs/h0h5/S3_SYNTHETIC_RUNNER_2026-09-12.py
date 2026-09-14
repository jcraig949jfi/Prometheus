"""S3 synthetic sequential season runner (preregistered in S3_SYNTHETIC_PREREG_2026-09-12.json).

Run from the repository root:  python archaeon/docs/h0h5/S3_SYNTHETIC_RUNNER_2026-09-12.py
Writes S3_SYNTHETIC_RESULTS_2026-09-12.json beside this file. The hidden
target lives only in this harness; the selector receives fossils only.
"""
from __future__ import annotations

import json
import math
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from archaeon.producer import acquisition as AQ, fossil_inference as FI  # noqa: E402

PRE = json.loads((Path(__file__).parent / "S3_SYNTHETIC_PREREG_2026-09-12.json").read_text(encoding="utf-8"))
LENGTHS = PRE["worlds"]["lengths"]; SEEDS = PRE["worlds"]["seeds_per_length"]; STEPS = {int(k): v for k, v in PRE["worlds"]["steps"].items()}


def score(x, t):
    return sum(a == b for a, b in zip(x, t)) / len(t)


def spearman(xs, ys):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    if len(xs) < 3:
        return None
    rx, ry = ranks(xs), ranks(ys); mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry)); den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else None


def run_world(L, seed):
    rng = random.Random(f"S3:{L}:{seed}")
    t = "".join(rng.choice("01") for _ in range(L))
    x0 = "".join(rng.choice("01") for _ in range(L))
    init = [FI.Fossil(x0, score(x0, t))]
    out = {"L": L, "seed": seed, "initial_fossil": {"bits": x0, "score": init[0].score}, "arms": {}}
    for arm in ("I", "U"):
        arng = random.Random(f"S3:{L}:{seed}:{arm}")
        E = list(init); traj = []; ident_step = None; max_sel_time = 0.0
        for step in range(1, STEPS[L] + 1):
            st = AQ.feasible(E)
            t0 = time.perf_counter()
            if arm == "I":
                pool = AQ.probe_pool(st, E, arng, n_random=32)
                sel = AQ.select(st, pool); q = sel.probe; v = sel.value; tie = len(sel.tie_class)
                pool_vals = sel.ranked
            else:
                q = AQ.uniform_probe(L, arng); v = AQ.value(st, q); tie = None; pool_vals = None
            dt = time.perf_counter() - t0; max_sel_time = max(max_sel_time, dt)
            # diversity vs information over the pool (I arm only; the pool is scored anyway)
            rho = None
            if pool_vals:
                dist = [min(AQ.hamming(pv.probe, f.bits) for f in E) for pv in pool_vals]
                info = [-pv.expected_remaining for pv in pool_vals]
                rho = spearman(dist, info)
            s = score(q, t); before = st.feasible_targets; fixed_before = st.n_fixed
            E.append(FI.Fossil(q, s))
            st2 = AQ.feasible(E)
            realised = AQ.outcome_partition(st, q)[sum(a != b for a, b in zip(q, t))]
            traj.append({"step": step, "probe": q, "score": s, "ER_before": v.expected_remaining, "worst_case": v.worst_case_remaining, "entropy_bits": v.outcome_entropy_bits, "n_outcomes": v.n_outcomes,
                         "E_score": v.expected_score, "tie_class_size": tie, "dist_to_nearest_fossil": min(AQ.hamming(q, f.bits) for f in E[:-1]),
                         "feasible_before": before, "feasible_after": st2.feasible_targets, "realised_remaining_equals_after": realised == st2.feasible_targets,
                         "log2_after": math.log2(st2.feasible_targets), "fixed_before": fixed_before, "fixed_after": st2.n_fixed, "fixed_delta": st2.n_fixed - fixed_before,
                         "progress": ("BOTH" if (s > max(f.score for f in E[:-1]) and st2.feasible_targets < before) else ("SOLUTION_PROGRESS" if s > max(f.score for f in E[:-1]) else ("INFORMATION_PROGRESS" if st2.feasible_targets < before else "NEITHER"))),
                         "pool_spearman_dist_vs_info": rho, "select_seconds": dt})
            if ident_step is None and st2.feasible_targets == 1:
                ident_step = step
        out["arms"][arm] = {"trajectory": traj, "final_log2": traj[-1]["log2_after"], "final_fixed": traj[-1]["fixed_after"], "identified_at": ident_step if ident_step else STEPS[L] + 1,
                            "mean_probe_score": sum(x["score"] for x in traj) / len(traj), "max_select_seconds": max_sel_time}
    return out


def main():
    worlds = []
    for L in LENGTHS:
        for seed in range(SEEDS):
            worlds.append(run_world(L, seed)); print("world", L, seed, "I log2", round(worlds[-1]["arms"]["I"]["final_log2"], 2), "U log2", round(worlds[-1]["arms"]["U"]["final_log2"], 2), flush=True)
    summary = {}
    for L in LENGTHS:
        ws = [w for w in worlds if w["L"] == L]
        d = [w["arms"]["U"]["final_log2"] - w["arms"]["I"]["final_log2"] for w in ws]
        wins = sum(1 for x in d if x > 0); ties = sum(1 for x in d if x == 0)
        fixI = [w["arms"]["I"]["final_fixed"] for w in ws]; fixU = [w["arms"]["U"]["final_fixed"] for w in ws]
        idI = [w["arms"]["I"]["identified_at"] for w in ws]; idU = [w["arms"]["U"]["identified_at"] for w in ws]
        scI = [w["arms"]["I"]["mean_probe_score"] for w in ws]; scU = [w["arms"]["U"]["mean_probe_score"] for w in ws]
        rhos = [s["pool_spearman_dist_vs_info"] for w in ws for s in w["arms"]["I"]["trajectory"] if s["pool_spearman_dist_vs_info"] is not None]
        rhos.sort()
        traj_I = [sum(w["arms"]["I"]["trajectory"][k]["log2_after"] for w in ws) / len(ws) for k in range(STEPS[L])]
        traj_U = [sum(w["arms"]["U"]["trajectory"][k]["log2_after"] for w in ws) / len(ws) for k in range(STEPS[L])]
        fx_I = [sum(w["arms"]["I"]["trajectory"][k]["fixed_after"] for w in ws) / len(ws) for k in range(STEPS[L])]
        fx_U = [sum(w["arms"]["U"]["trajectory"][k]["fixed_after"] for w in ws) / len(ws) for k in range(STEPS[L])]
        sc_I = [sum(w["arms"]["I"]["trajectory"][k]["score"] for w in ws) / len(ws) for k in range(STEPS[L])]
        sc_U = [sum(w["arms"]["U"]["trajectory"][k]["score"] for w in ws) / len(ws) for k in range(STEPS[L])]
        summary[str(L)] = {"n": len(ws), "steps": STEPS[L], "mean_final_log2_I": sum(w["arms"]["I"]["final_log2"] for w in ws) / len(ws), "mean_final_log2_U": sum(w["arms"]["U"]["final_log2"] for w in ws) / len(ws),
                           "paired_mean_U_minus_I_bits": sum(d) / len(d), "I_le_U_count": wins + ties, "I_lt_U_count": wins, "ties": ties,
                           "mean_final_fixed_I": sum(fixI) / len(fixI), "mean_final_fixed_U": sum(fixU) / len(fixU), "mean_identified_at_I": sum(idI) / len(idI), "mean_identified_at_U": sum(idU) / len(idU),
                           "identified_within_budget_I": sum(1 for x in idI if x <= STEPS[L]), "identified_within_budget_U": sum(1 for x in idU if x <= STEPS[L]),
                           "mean_probe_score_I": sum(scI) / len(scI), "mean_probe_score_U": sum(scU) / len(scU),
                           "traj_log2_I": traj_I, "traj_log2_U": traj_U, "traj_fixed_I": fx_I, "traj_fixed_U": fx_U, "traj_score_I": sc_I, "traj_score_U": sc_U,
                           "diversity_spearman_median": rhos[len(rhos) // 2] if rhos else None, "diversity_spearman_iqr": [rhos[len(rhos) // 4], rhos[3 * len(rhos) // 4]] if rhos else None, "n_pool_correlations": len(rhos),
                           "max_select_seconds": max(w["arms"]["I"]["max_select_seconds"] for w in ws),
                           "clause_mean_ge_1": sum(d) / len(d) >= 1.0, "clause_sign_24_of_30": (wins + ties) >= 24}
    validated = all(v["clause_mean_ge_1"] and v["clause_sign_24_of_30"] for v in summary.values())
    intractable = any(v["max_select_seconds"] > 60 for v in summary.values())
    misaligned = all((v["mean_final_fixed_I"] <= v["mean_final_fixed_U"]) and (v["mean_identified_at_I"] >= v["mean_identified_at_U"]) for v in summary.values())
    verdict = "COMPUTATIONALLY_INTRACTABLE" if intractable else ("INFORMATION_SELECTOR_VALIDATED" if validated else ("INFORMATION_OBJECTIVE_MISALIGNED" if misaligned else "NO_ADVANTAGE_OVER_UNIFORM"))
    res = {"schema": "archaeon.fossil_metabolism_s3.synthetic_results.v0", "preregistration": "S3_SYNTHETIC_PREREG_2026-09-12.json", "summary": summary, "verdict": verdict, "worlds": worlds}
    (Path(__file__).parent / "S3_SYNTHETIC_RESULTS_2026-09-12.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if not kk.startswith("traj")} for k, v in summary.items()}, indent=1)); print("VERDICT", verdict)


if __name__ == "__main__":
    main()
