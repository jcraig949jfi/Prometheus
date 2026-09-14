"""S7 runner (preregistered in S7_PREREG_2026-09-13.json). Arms G and GATED_V2W only; at EVERY candidate decision the
identity invariant is checked against an independent G / A_v2w_0 call with the same seed.
  --eligible 8|9   S6 eligible endgame states, complete census, V* reused from S6 result files
  --universe       the 233 S5 root worlds, V* from S5 rows; the seven canaries reported by name
  --L10            additional confirmation: L 10 state family, sealed oracle under a 50 M-unit budget per world
Run from the repository root."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from archaeon.producer import acquisition as AQ, fossil_inference as FI, s4_producers as P, s5_producers as O5, s6_endgame as S6, s7_gated as G7, work_budget as WB  # noqa: E402

HERE = Path(__file__).parent
PRE = json.loads((HERE / "S7_PREREG_2026-09-13.json").read_text(encoding="utf-8"))
B = 10
# ARCH-46A: identical trial, exact v2w; results are written under a tag so S7's rows are never overwritten
TAG = ("_" + sys.argv[sys.argv.index("--tag") + 1]) if "--tag" in sys.argv else ""


def _json(o):
    if isinstance(o, np.bool_): return bool(o)
    if isinstance(o, np.integer): return int(o)
    if isinstance(o, np.floating): return float(o)
    return str(o)


def score(x, t):
    return sum(a == b for a, b in zip(x, t)) / len(t)


def _same(a, b):
    return a.probe == b.probe and a.tie_class == b.tie_class and a.objective_value == b.objective_value


def propose(arm, E, si, cache, audit):
    key = (arm, P.snapshot_id(E), si["step"])
    if key in cache:
        return cache[key]
    with WB.WorkBudget(10 ** 12) as b:
        p = P.produce_G(E, si) if arm == "G" else G7.produce_gated_v2w(E, si)
    p.extra["work_units"] = b.units; p.extra["work_counters"] = dict(b.counters)
    if arm == "GATED_V2W":
        g = p.extra["gate"]; ref = S6.produce_refined(E, si, "v2w", 0.0) if g["active"] else P.produce_G(E, si)
        ok = _same(p, ref); audit["decisions"] += 1; audit["inside" if g["active"] else "outside"] += 1
        if not ok:
            audit["violations"].append({"snapshot": p.evidence_snapshot_id, "N": g["N"], "active": g["active"], "candidate": p.probe, "reference": ref.probe})
    cache[key] = p
    return p


def run_arm(arm, E0, targets, L, sid, lane, cache, audit):
    steps = []; units = []; gate_units = []; secs = 0.0; fired = 0; decisions = 0
    for t in targets:
        E = list(E0); k = 0
        while AQ.feasible(E).feasible_targets > 1 and k < B:
            si = {"lane": lane, "L": L, "world": sid, "arm": "G", "step": k + 1}
            p = propose(arm, E, si, cache, audit)
            assert p.probe is not None, (arm, p.extra)
            units.append(p.extra["work_units"]); secs += p.compute_seconds; decisions += 1
            if arm == "GATED_V2W":
                fired += int(p.extra["gate"]["active"]); gate_units.append(p.extra["gate"]["gate_units"])
            E.append(FI.Fossil(p.probe, score(p.probe, t))); k += 1
        steps.append(k if AQ.feasible(E).feasible_targets == 1 else B + 1)
    return {"cost": sum(steps) / len(steps), "median_units": float(np.median(units)), "max_units": int(max(units)), "total_units": int(sum(units)), "decisions": decisions, "fired": fired,
            "median_gate_units": float(np.median(gate_units)) if gate_units else 0.0, "seconds": secs}


def eligible(L):
    s6 = json.loads((HERE / f"S6_RESULTS_ELIGIBLE_L{L}_2026-09-13.json").read_text(encoding="utf-8"))
    vstar = {r["eid"]: r["V_star"] for r in s6["rows"]}; s6cost = {r["eid"]: {a: v["cost"] for a, v in r["arms"].items()} for r in s6["rows"]}
    states = [s for s in json.loads((HERE / f"S6_ENDGAME_UNIVERSE_L{L}_2026-09-13.json").read_text(encoding="utf-8")) if 5 <= s["N"] <= 18]
    audit = {"decisions": 0, "inside": 0, "outside": 0, "violations": []}; out = []; t0 = time.time()
    for i, s in enumerate(states):
        fs = [FI.Fossil(b, sc) for b, sc in s["fossils"]]; S = S6.feasible_ints(fs); targets = [O5._as_bits(int(x), L) for x in S]
        assert len(S) == FI.infer(fs).feasible_targets == s["N"]
        cache = {}; row = {"eid": s["eid"], "N": s["N"], "depth": s["depth"], "V_star": vstar[s["eid"]], "S6_costs": s6cost[s["eid"]], "arms": {}}
        for a in ("G", "GATED_V2W"):
            row["arms"][a] = run_arm(a, fs, targets, L, s["eid"], "s6", cache, audit)
            assert row["arms"][a]["cost"] >= row["V_star"] - 1e-9, ("IMPOSSIBLE below V*", a, s["eid"])
        assert abs(row["arms"]["G"]["cost"] - s6cost[s["eid"]]["G"]) < 1e-9, ("G does not replicate S6", s["eid"])
        out.append(row)
        if i % 50 == 0 or i == len(states) - 1:
            print("eligible L", L, i + 1, "/", len(states), "t=%ds" % (time.time() - t0), flush=True)
    res = {"schema": "archaeon.fossil_metabolism_s7.eligible.v0", "L": L, "candidate_version": G7.CANDIDATE_VERSION, "identity_audit": audit, "rows": out, "elapsed_s": time.time() - t0}
    res["summary"] = summarise_eligible(out)
    (HERE / f"S7_RESULTS_ELIGIBLE_L{L}{TAG}_2026-09-13.json").write_text(json.dumps(res, indent=1, default=_json), encoding="utf-8")
    print(json.dumps({"identity_audit": {k: (v if k != "violations" else len(v)) for k, v in audit.items()}, "summary": res["summary"]}, indent=1, default=_json))


def summarise_eligible(rows):
    n = len(rows); gap = [r for r in rows if r["arms"]["G"]["cost"] - r["V_star"] > 1e-9]; tot_gap = sum(r["arms"]["G"]["cost"] - r["V_star"] for r in gap)
    totG = sum(r["arms"]["G"]["cost"] for r in rows); totC = sum(r["arms"]["GATED_V2W"]["cost"] for r in rows)
    d = [r["arms"]["G"]["cost"] - r["arms"]["GATED_V2W"]["cost"] for r in rows]
    worse = [r["eid"] for r in rows if r["arms"]["GATED_V2W"]["cost"] > r["arms"]["G"]["cost"] + 1e-9]
    byN = {}
    for r in rows:
        b = byN.setdefault(r["N"], {"states": 0, "gap": 0.0, "recovered": 0.0, "worsened": 0})
        b["states"] += 1; b["gap"] += r["arms"]["G"]["cost"] - r["V_star"]; b["recovered"] += r["arms"]["G"]["cost"] - r["arms"]["GATED_V2W"]["cost"]; b["worsened"] += int(r["eid"] in worse)
    gu = [r["arms"]["G"]["median_units"] for r in rows]; cu = [r["arms"]["GATED_V2W"]["median_units"] for r in rows]
    return {"states": n, "gap_states": len(gap), "improved": sum(1 for x in d if x > 1e-9), "unchanged": sum(1 for x in d if abs(x) <= 1e-9), "worsened": len(worse), "worsened_ids": worse,
            "worst_regression_rel": max((r["arms"]["GATED_V2W"]["cost"] - r["arms"]["G"]["cost"]) / r["arms"]["G"]["cost"] for r in rows),
            "recovery": (sum(r["arms"]["G"]["cost"] - r["arms"]["GATED_V2W"]["cost"] for r in gap) / tot_gap) if tot_gap else None, "aggregate_probe_reduction_rel": (totG - totC) / totG,
            "S6_A_v2w_0_recovery_same_states": (sum(r["arms"]["G"]["cost"] - r["S6_costs"]["A_v2w_0"] for r in gap) / tot_gap) if tot_gap else None,
            "by_N": byN, "G_median_units": float(np.median(gu)), "C_median_units": float(np.median(cu)), "median_ratio": float(np.median(cu)) / float(np.median(gu)), "C_max_units": max(r["arms"]["GATED_V2W"]["max_units"] for r in rows),
            "fired_fraction": sum(r["arms"]["GATED_V2W"]["fired"] for r in rows) / max(1, sum(r["arms"]["GATED_V2W"]["decisions"] for r in rows)),
            "total_incremental_units": sum(r["arms"]["GATED_V2W"]["total_units"] - r["arms"]["G"]["total_units"] for r in rows),
            "probes_saved_census": sum((r["arms"]["G"]["cost"] - r["arms"]["GATED_V2W"]["cost"]) * r["N"] for r in rows)}


def universe():
    can = {c["root"] for c in json.loads((HERE / "S7_CANARIES_FROM_S6_2026-09-13.json").read_text(encoding="utf-8"))}
    s6u = {r["root"]: r for r in json.loads((HERE / "S6_RESULTS_UNIVERSE_2026-09-13.json").read_text(encoding="utf-8"))["rows"]}
    audit = {"decisions": 0, "inside": 0, "outside": 0, "violations": []}; out = []; t0 = time.time()
    for L in (8, 9):
        r5 = json.loads((HERE / f"S5_RESULTS_RUN2_L{L}_SLIM_2026-09-13.json").read_text(encoding="utf-8"))
        for w in r5["worlds"]:
            fs = [FI.Fossil(b, s) for b, s in w["fossils"]]; targets = [O5._as_bits(int(x), L) for x in S6.feasible_ints(fs)]; cache = {}
            row = {"root": w["state_id"], "L": L, "N": w["N"], "V_star_from_S5": w["summary"]["O"]["E_probes"], "canary": w["state_id"] in can, "S6_costs": {a: v["cost"] for a, v in s6u[w["state_id"]]["arms"].items()}, "arms": {}}
            for a in ("G", "GATED_V2W"):
                row["arms"][a] = run_arm(a, fs, targets, L, w["state_id"], "s6", cache, audit)
                assert row["arms"][a]["cost"] >= row["V_star_from_S5"] - 1e-9, ("IMPOSSIBLE below V*", a, w["state_id"])
            assert abs(row["arms"]["G"]["cost"] - row["S6_costs"]["G"]) < 1e-9, ("G does not replicate S6", w["state_id"])
            si = {"lane": "s6", "L": L, "world": w["state_id"], "arm": "G", "step": 1}
            row["root_decision"] = {"G": P.produce_G(fs, si).probe, "GATED_V2W": G7.produce_gated_v2w(fs, si).probe, "S6_A_v2w_0": S6.produce_refined(fs, si, "v2w", 0.0).probe}
            out.append(row)
            if len(out) % 40 == 0:
                print("universe", len(out), "t=%ds" % (time.time() - t0), flush=True)
    totG = sum(x["arms"]["G"]["cost"] * x["N"] for x in out); totC = sum(x["arms"]["GATED_V2W"]["cost"] * x["N"] for x in out)
    rel = [(x["arms"]["GATED_V2W"]["cost"] - x["arms"]["G"]["cost"]) / x["arms"]["G"]["cost"] for x in out]
    canaries = [{"root": x["root"], "N": x["N"], "G_cost": x["arms"]["G"]["cost"], "GATED_cost": x["arms"]["GATED_V2W"]["cost"], "S6_A_v2w_0_cost": x["S6_costs"]["A_v2w_0"], "V_star": x["V_star_from_S5"],
                 "root_decision_equals_G": x["root_decision"]["GATED_V2W"] == x["root_decision"]["G"], "S6_refinement_differed_at_root": x["root_decision"]["S6_A_v2w_0"] != x["root_decision"]["G"],
                 "fired_downstream": x["arms"]["GATED_V2W"]["fired"], "passes": (x["root_decision"]["GATED_V2W"] == x["root_decision"]["G"] and x["arms"]["GATED_V2W"]["cost"] <= x["arms"]["G"]["cost"] + 1e-9)} for x in out if x["canary"]]
    summ = {"worlds": len(out), "worsened_any": sum(1 for v in rel if v > 1e-9), "worsened_ge_2pct": sum(1 for v in rel if v >= 0.02), "worst_regression_rel": max(rel), "improved_any": sum(1 for v in rel if v < -1e-9), "improved_ge_2pct": sum(1 for v in rel if v <= -0.02),
            "aggregate_cost_rel_to_G": (totC - totG) / totG, "probes_saved_census": totG - totC, "regression_universe_ok": (sum(1 for v in rel if v >= 0.02) == 0 and totC <= totG + 1e-9),
            "canaries": canaries, "canaries_all_pass": all(c["passes"] for c in canaries), "fired_fraction": sum(x["arms"]["GATED_V2W"]["fired"] for x in out) / sum(x["arms"]["GATED_V2W"]["decisions"] for x in out),
            "C_median_units": float(np.median([x["arms"]["GATED_V2W"]["median_units"] for x in out])), "G_median_units": float(np.median([x["arms"]["G"]["median_units"] for x in out])), "C_max_units": max(x["arms"]["GATED_V2W"]["max_units"] for x in out),
            "total_incremental_units": sum(x["arms"]["GATED_V2W"]["total_units"] - x["arms"]["G"]["total_units"] for x in out)}
    res = {"schema": "archaeon.fossil_metabolism_s7.universe.v0", "candidate_version": G7.CANDIDATE_VERSION, "identity_audit": audit, "rows": out, "summary": summ, "elapsed_s": time.time() - t0}
    (HERE / f"S7_RESULTS_UNIVERSE{TAG}_2026-09-13.json").write_text(json.dumps(res, indent=1, default=_json), encoding="utf-8")
    print(json.dumps({"identity_audit": {k: (v if k != "violations" else len(v)) for k, v in audit.items()}, "summary": summ}, indent=1, default=_json))


def l10():
    L = 10; fam = [("shell", {"m": m}, [(0, m)]) for m in range(1, L)]
    for a in range(1, L):
        b = L - a; xa = (1 << a) - 1
        for uA in range(a + 1):
            for uB in range(b + 1):
                fam.append(("prod2", {"a": a, "b": b, "uA": uA, "uB": uB}, [(0, uA + uB), (xa, (a - uA) + uB)]))
    worlds = []; seen = set()
    for name, par, fos in fam:
        fs = [FI.Fossil(O5._as_bits(x, L), (L - m) / L) for x, m in fos]
        try:
            T = FI.enumerate_targets(fs)
        except Exception:
            continue
        if len(T) < 3 or len(T) > 24 or tuple(sorted(T)) in seen:
            continue
        seen.add(tuple(sorted(T))); worlds.append({"state_id": "L10_%s_%s" % (name, "_".join("%s%d" % kv for kv in par.items())), "fossils": [(f.bits, f.score) for f in fs], "N": len(T)})
    assert len(worlds) == 110, len(worlds)
    oracle = S6.SealedOracle(L); audit = {"decisions": 0, "inside": 0, "outside": 0, "violations": []}; out = []; t0 = time.time()
    for i, w in enumerate(worlds):
        fs = [FI.Fossil(b, s) for b, s in w["fossils"]]; S = S6.feasible_ints(fs); targets = [O5._as_bits(int(x), L) for x in S]; cache = {}
        row = {"root": w["state_id"], "L": L, "N": w["N"], "arms": {}}
        for a in ("G", "GATED_V2W"):
            row["arms"][a] = run_arm(a, fs, targets, L, w["state_id"], "s7", cache, audit)
        try:
            with WB.WorkBudget(50_000_000):
                row["V_star"] = oracle.V(S)
            for a in ("G", "GATED_V2W"):
                assert row["arms"][a]["cost"] >= row["V_star"] - 1e-9, ("IMPOSSIBLE below V*", a, w["state_id"])
        except WB.BudgetExhausted:
            row["V_star"] = None
        out.append(row)
        if i % 10 == 0 or i == len(worlds) - 1:
            print("L10", i + 1, "/", len(worlds), w["state_id"], "N", w["N"], {a: round(row["arms"][a]["cost"], 3) for a in row["arms"]}, "V*", row["V_star"], "t=%ds" % (time.time() - t0), flush=True)
    totG = sum(x["arms"]["G"]["cost"] * x["N"] for x in out); totC = sum(x["arms"]["GATED_V2W"]["cost"] * x["N"] for x in out)
    rel = [(x["arms"]["GATED_V2W"]["cost"] - x["arms"]["G"]["cost"]) / x["arms"]["G"]["cost"] for x in out]
    withV = [x for x in out if x["V_star"] is not None]; gap = [x for x in withV if x["arms"]["G"]["cost"] - x["V_star"] > 1e-9]; tot_gap = sum(x["arms"]["G"]["cost"] - x["V_star"] for x in gap)
    summ = {"worlds": len(out), "worsened_any": sum(1 for v in rel if v > 1e-9), "worsened_ge_2pct": sum(1 for v in rel if v >= 0.02), "worst_regression_rel": max(rel), "improved_any": sum(1 for v in rel if v < -1e-9),
            "aggregate_cost_rel_to_G": (totC - totG) / totG, "probes_saved_census": totG - totC, "L10_ok": (sum(1 for v in rel if v >= 0.02) == 0 and totC <= totG + 1e-9),
            "oracle_available_worlds": len(withV), "gap_worlds": len(gap), "recovery_where_available": (sum(x["arms"]["G"]["cost"] - x["arms"]["GATED_V2W"]["cost"] for x in gap) / tot_gap) if tot_gap else None,
            "fired_fraction": sum(x["arms"]["GATED_V2W"]["fired"] for x in out) / sum(x["arms"]["GATED_V2W"]["decisions"] for x in out), "C_median_units": float(np.median([x["arms"]["GATED_V2W"]["median_units"] for x in out])), "G_median_units": float(np.median([x["arms"]["G"]["median_units"] for x in out])),
            "C_max_units": max(x["arms"]["GATED_V2W"]["max_units"] for x in out), "oracle_ledger": vars(oracle.ledger)}
    res = {"schema": "archaeon.fossil_metabolism_s7.l10.v0", "candidate_version": G7.CANDIDATE_VERSION, "identity_audit": audit, "rows": out, "summary": summ, "elapsed_s": time.time() - t0}
    (HERE / f"S7_RESULTS_L10{TAG}_2026-09-13.json").write_text(json.dumps(res, indent=1, default=_json), encoding="utf-8")
    print(json.dumps({"identity_audit": {k: (v if k != "violations" else len(v)) for k, v in audit.items()}, "summary": summ}, indent=1, default=_json))


if __name__ == "__main__":
    if "--eligible" in sys.argv:
        eligible(int(sys.argv[sys.argv.index("--eligible") + 1]))
    elif "--universe" in sys.argv:
        universe()
    elif "--L10" in sys.argv:
        l10()
