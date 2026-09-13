"""S6 verdict under the frozen rule (S6_PREREG_2026-09-13.json, verdict_rule_frozen), computed from the result files only.
Run from the repository root: python archaeon/docs/h0h5/S6_VERDICT_2026-09-13.py"""
import json
from pathlib import Path

HERE = Path(__file__).parent
PRE = json.loads((HERE / "S6_PREREG_2026-09-13.json").read_text(encoding="utf-8")); BARS = PRE["bars_frozen"]
prim = json.loads((HERE / "S6_PRIMARY_RUNG_2026-09-13.json").read_text(encoding="utf-8"))["primary_rung"]
L9 = json.loads((HERE / "S6_RESULTS_ELIGIBLE_L9_2026-09-13.json").read_text(encoding="utf-8"))
L8 = json.loads((HERE / "S6_RESULTS_ELIGIBLE_L8_2026-09-13.json").read_text(encoding="utf-8"))
U = json.loads((HERE / "S6_RESULTS_UNIVERSE_2026-09-13.json").read_text(encoding="utf-8"))

s9 = L9["summary"]; a9 = s9["arms"][prim]; u = U["summary"][prim]
failures = []
for res, name in ((L8, "L8"), (L9, "L9")):
    for r in res["rows"]:
        for a, v in r["arms"].items():
            if v["cost"] < r["V_star"] - 1e-9:
                failures.append("%s %s %s below V*" % (name, r["eid"], a))
for a, v in U["summary"].items():
    if v["worlds_below_S5_Vstar"]:
        failures.append("universe %s below S5 V* in %d worlds" % (a, v["worlds_below_S5_Vstar"]))
checks = {
    "gap_present_L9": s9["gap_present"],
    "primary_recovery_L9": a9["recovery"], "recovery_ok": a9["recovery"] >= BARS["recovery_meaningful"],
    "regression_eligible_L9_ok": a9["regression_eligible_ok"], "worsened_fraction_L9": a9["worsened_fraction_all"], "worst_regression_L9": a9["worst_regression_rel"],
    "regression_universe_ok": u["regression_universe_ok"], "universe_worsened_ge_2pct": u["worsened_ge_2pct"], "universe_worst": u["worst_regression_rel"], "universe_aggregate_rel": u["aggregate_cost_rel_to_G"],
    "work_ok": a9["work_ok"], "primary_median_units_L9": a9["median_units"], "G_median_units_L9": s9["G_median_units"],
    "CTRL_20_recovery_L9": s9["arms"]["CTRL_20"]["recovery"], "all_rungs_recovery_L9": {a: v["recovery"] for a, v in s9["arms"].items()},
}
if failures:
    verdict = "INSTRUMENT_FAILURE"
elif not checks["gap_present_L9"]:
    verdict = "NO_OBJECTIVE_RESIDUE"
elif checks["recovery_ok"]:
    verdict = "CHEAP_ENDGAME_REPAIR" if (checks["regression_eligible_L9_ok"] and checks["regression_universe_ok"] and checks["work_ok"]) else ("CHEAP_REPAIR_WITH_REGRESSION" if not (checks["regression_eligible_L9_ok"] and checks["regression_universe_ok"]) else "CHEAP_ENDGAME_REPAIR (work bar flagged)")
else:
    every_below = all(v["recovery"] < BARS["recovery_meaningful"] for a, v in s9["arms"].items() if not a.startswith("CTRL"))
    verdict = ("DEEP_SEARCH_REQUIRED" if s9["arms"]["CTRL_20"]["recovery"] >= BARS["control_strong"] else "RESIDUE_NOT_COMPRESSIBLE") if every_below else "CHEAP_REPAIR_WITH_REGRESSION"
out = {"schema": "archaeon.fossil_metabolism_s6.verdict.v0", "preregistration": "S6_PREREG_2026-09-13.json", "primary_rung": prim, "instrument_failures": failures, "checks": checks, "verdict": verdict,
       "note": "computed only from S6_RESULTS_ELIGIBLE_L9, S6_RESULTS_ELIGIBLE_L8 (failure scan) and S6_RESULTS_UNIVERSE under the frozen precedence"}
(HERE / "S6_VERDICT_2026-09-13.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
