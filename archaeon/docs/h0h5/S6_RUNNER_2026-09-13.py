"""S6 runner (preregistered in S6_PREREG_2026-09-13.json). The hidden target lives only here; the sealed oracle is used
only by the evaluator and by the labelled positive controls.
  --L 8            development: eligible L 8 states, all arms
  --L 9            confirmation: eligible L 9 states, all arms (run only after S6_PRIMARY_RUNG is committed)
  --universe       full-universe regression audit: the 233 S5 root worlds (both L), G and every rung, V* from S5 rows
Run from the repository root."""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from archaeon.producer import acquisition as AQ, fossil_inference as FI, s4_producers as P, s5_producers as O5, s6_endgame as S6, work_budget as WB  # noqa: E402

HERE = Path(__file__).parent
PRE = json.loads((HERE / "S6_PREREG_2026-09-13.json").read_text(encoding="utf-8"))
RUNGS = {"A_entropy_0": ("entropy", 0.0), "A_lb2_0": ("lb2", 0.0), "A_v2w_0": ("v2w", 0.0), "B_v2w_10": ("v2w", 0.10), "B_v2w_20": ("v2w", 0.20), "B_lb2_20": ("lb2", 0.20)}
CONTROLS = {"CTRL_0": 0.0, "CTRL_20": 0.20}
B = 10; R_MAX_N = 12
BARS = PRE["bars_frozen"]


def _json(o):
    if isinstance(o, (np.bool_,)): return bool(o)
    if isinstance(o, np.integer): return int(o)
    if isinstance(o, np.floating): return float(o)
    return str(o)


def score(x, t):
    return sum(a == b for a, b in zip(x, t)) / len(t)


def propose(arm, E, si, oracle, cache):
    key = (arm, P.snapshot_id(E), si["step"])
    if key in cache:
        return cache[key]
    with WB.WorkBudget(10 ** 12) as b:
        if arm == "G":
            p = P.produce_G(E, si)
        elif arm in RUNGS:
            stat, w = RUNGS[arm]; p = S6.produce_refined(E, si, stat, w)
        elif arm in CONTROLS:
            p = S6.produce_oracle_control(E, si, oracle, CONTROLS[arm])
        else:
            raise ValueError(arm)
    p.extra["work_units"] = b.units; p.extra["work_counters"] = dict(b.counters)
    cache[key] = p
    return p


def run_arm(arm, E0, targets, L, sid, oracle, cache):
    """Census cost of `arm` from evidence E0: mean probes to identification over every target (censored at B+1)."""
    steps = []; units = []; secs = 0.0; active = 0; decisions = 0
    for t in targets:
        E = list(E0); k = 0
        while AQ.feasible(E).feasible_targets > 1 and k < B:
            si = {"lane": "s6", "L": L, "world": sid, "arm": "G", "step": k + 1}      # G's seed for every arm (identical pools)
            p = propose(arm, E, si, oracle, cache)
            assert p.probe is not None, (arm, p.extra)
            units.append(p.extra["work_units"]); secs += p.compute_seconds; decisions += 1; active += int(bool(p.ancestry.get("active")))
            E.append(FI.Fossil(p.probe, score(p.probe, t))); k += 1
        steps.append(k if AQ.feasible(E).feasible_targets == 1 else B + 1)
    return {"cost": sum(steps) / len(steps), "median_units": float(np.median(units)) if units else 0.0, "max_units": max(units) if units else 0, "seconds": secs, "decisions": decisions, "active_decisions": active}


def eligible_run(L):
    states = [s for s in json.loads((HERE / f"S6_ENDGAME_UNIVERSE_L{L}_2026-09-13.json").read_text(encoding="utf-8")) if 5 <= s["N"] <= 18]
    oracle = S6.SealedOracle(L); rmemo = {}; out = []; t0 = time.time(); arms = ["G"] + list(RUNGS) + list(CONTROLS)
    for i, s in enumerate(states):
        fs = [FI.Fossil(b, sc) for b, sc in s["fossils"]]; S = S6.feasible_ints(fs); targets = [O5._as_bits(int(x), L) for x in S]
        assert len(S) == FI.infer(fs).feasible_targets == s["N"]
        vstar = oracle.V(S); cache = {}
        row = {"eid": s["eid"], "N": s["N"], "depth": s["depth"], "root": s["root"], "V_star": vstar, "arms": {}}
        for a in arms:
            row["arms"][a] = run_arm(a, fs, targets, L, s["eid"], oracle, cache)
            assert row["arms"][a]["cost"] >= vstar - 1e-9, ("IMPOSSIBLE: below V*", a, s["eid"], row["arms"][a]["cost"], vstar)
        row["R_blind"] = S6.random_policy_value(L, S, rmemo) if s["N"] <= R_MAX_N else None
        out.append(row)
        if i % 25 == 0 or i == len(states) - 1:
            print("L", L, "state", i + 1, "/", len(states), "N", s["N"], {a: round(row["arms"][a]["cost"], 3) for a in arms}, "V*", round(vstar, 3), "t=%ds" % (time.time() - t0), flush=True)
    res = {"schema": "archaeon.fossil_metabolism_s6.eligible.v0", "L": L, "preregistration": "S6_PREREG_2026-09-13.json", "versions": {"s4": P.PRODUCER_VERSION, "s5": O5.PRODUCER_VERSION, "s6": S6.PRODUCER_VERSION},
           "oracle_ledger": vars(oracle.ledger), "elapsed_s": time.time() - t0, "rows": out}
    res["summary"] = summarise(out, arms)
    (HERE / f"S6_RESULTS_ELIGIBLE_L{L}_2026-09-13.json").write_text(json.dumps(res, indent=1, default=_json), encoding="utf-8")
    print(json.dumps(res["summary"], indent=1, default=_json))


def summarise(rows, arms):
    gap = [r for r in rows if r["arms"]["G"]["cost"] - r["V_star"] > 1e-9]; n = len(rows)
    tot_gap = sum(r["arms"]["G"]["cost"] - r["V_star"] for r in gap); totG = sum(r["arms"]["G"]["cost"] for r in rows)
    out = {"states": n, "gap_states": len(gap), "gap_fraction": len(gap) / n, "aggregate_gap_fraction_of_G": tot_gap / totG, "gap_present": (len(gap) / n >= 0.20 and tot_gap / totG >= 0.01),
           "G_median_units": float(np.median([r["arms"]["G"]["median_units"] for r in rows])), "arms": {}}
    rb = [r for r in rows if r["R_blind"] is not None]
    out["blind_exact"] = {"states": len(rb), "R_mean": (sum(r["R_blind"] for r in rb) / len(rb)) if rb else None, "G_mean_same_states": (sum(r["arms"]["G"]["cost"] for r in rb) / len(rb)) if rb else None}
    for a in arms:
        if a == "G":
            continue
        d = [(r["arms"]["G"]["cost"] - r["arms"][a]["cost"]) for r in gap]; rec = sum(d) / tot_gap if tot_gap else None
        per = [(r["arms"]["G"]["cost"] - r["arms"][a]["cost"]) / (r["arms"]["G"]["cost"] - r["V_star"]) for r in gap]
        worse = [r for r in rows if r["arms"][a]["cost"] > r["arms"]["G"]["cost"] + 1e-9]
        worst = max(((r["arms"][a]["cost"] - r["arms"]["G"]["cost"]) / r["arms"]["G"]["cost"]) for r in rows)
        out["arms"][a] = {"recovery": rec, "median_state_recovery": float(np.median(per)) if per else None, "gap_improved": sum(1 for x in d if x > 1e-9), "gap_worsened": sum(1 for x in d if x < -1e-9), "gap_unchanged": sum(1 for x in d if abs(x) <= 1e-9),
                          "worsened_states_all": len(worse), "worsened_fraction_all": len(worse) / n, "worst_regression_rel": worst,
                          "aggregate_probe_reduction_rel": (totG - sum(r["arms"][a]["cost"] for r in rows)) / totG, "residual_to_O": (sum(r["arms"][a]["cost"] - r["V_star"] for r in gap) / tot_gap) if tot_gap else None,
                          "median_units": float(np.median([r["arms"][a]["median_units"] for r in rows])), "max_units": max(r["arms"][a]["max_units"] for r in rows), "active_fraction": sum(r["arms"][a]["active_decisions"] for r in rows) / max(1, sum(r["arms"][a]["decisions"] for r in rows)),
                          "regression_eligible_ok": (len(worse) / n <= 0.05 and worst <= 0.05), "work_ok": float(np.median([r["arms"][a]["median_units"] for r in rows])) <= 25000}
    return out


def universe_run():
    """The 233 S5 root worlds, G and every rung under the S6 seed; V* from the S5 run-2 rows (O's exact census cost)."""
    out = []; t0 = time.time(); arms = ["G"] + list(RUNGS)
    for L in (8, 9):
        r = json.loads((HERE / f"S5_RESULTS_RUN2_L{L}_SLIM_2026-09-13.json").read_text(encoding="utf-8")); oracle = S6.SealedOracle(L)
        for w in r["worlds"]:
            fs = [FI.Fossil(b, s) for b, s in w["fossils"]]; targets = [O5._as_bits(int(x), L) for x in S6.feasible_ints(fs)]; cache = {}
            row = {"root": w["state_id"], "L": L, "N": w["N"], "V_star_from_S5": w["summary"]["O"]["E_probes"], "arms": {}}
            for a in arms:
                row["arms"][a] = run_arm(a, fs, targets, L, w["state_id"], oracle, cache)
            out.append(row)
            if len(out) % 20 == 0:
                print("universe", len(out), w["state_id"], {a: round(row["arms"][a]["cost"], 3) for a in arms}, "t=%ds" % (time.time() - t0), flush=True)
    summ = {}
    totG = sum(x["arms"]["G"]["cost"] * x["N"] for x in out)
    for a in RUNGS:
        rel = [(x["arms"][a]["cost"] - x["arms"]["G"]["cost"]) / x["arms"]["G"]["cost"] for x in out]
        summ[a] = {"worlds": len(out), "worsened_ge_2pct": sum(1 for v in rel if v >= 0.02), "worst_regression_rel": max(rel), "improved_ge_2pct": sum(1 for v in rel if v <= -0.02),
                   "aggregate_cost_rel_to_G": (sum(x["arms"][a]["cost"] * x["N"] for x in out) - totG) / totG, "regression_universe_ok": (sum(1 for v in rel if v >= 0.02) == 0 and sum(x["arms"][a]["cost"] * x["N"] for x in out) <= totG + 1e-9),
                   "worlds_below_S5_Vstar": sum(1 for x in out if x["arms"][a]["cost"] < x["V_star_from_S5"] - 1e-9)}
    res = {"schema": "archaeon.fossil_metabolism_s6.universe.v0", "rows": out, "summary": summ, "elapsed_s": time.time() - t0}
    (HERE / "S6_RESULTS_UNIVERSE_2026-09-13.json").write_text(json.dumps(res, indent=1, default=_json), encoding="utf-8")
    print(json.dumps(summ, indent=1, default=_json))


if __name__ == "__main__":
    if "--universe" in sys.argv:
        universe_run()
    else:
        eligible_run(int(sys.argv[sys.argv.index("--L") + 1]))
