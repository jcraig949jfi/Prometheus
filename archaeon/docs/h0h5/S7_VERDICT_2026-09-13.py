"""S7 verdict under the frozen rule (S7_PREREG_2026-09-13.json), from the result files only.
Run from the repository root: python archaeon/docs/h0h5/S7_VERDICT_2026-09-13.py"""
import json
from pathlib import Path

HERE = Path(__file__).parent
E8 = json.loads((HERE / "S7_RESULTS_ELIGIBLE_L8_2026-09-13.json").read_text(encoding="utf-8"))
E9 = json.loads((HERE / "S7_RESULTS_ELIGIBLE_L9_2026-09-13.json").read_text(encoding="utf-8"))
U = json.loads((HERE / "S7_RESULTS_UNIVERSE_2026-09-13.json").read_text(encoding="utf-8"))
L10 = json.loads((HERE / "S7_RESULTS_L10_2026-09-13.json").read_text(encoding="utf-8")) if (HERE / "S7_RESULTS_L10_2026-09-13.json").exists() else None

failures = []
for name, r in (("L8", E8), ("L9", E9), ("universe", U)) + ((("L10", L10),) if L10 else ()):
    if r["identity_audit"]["violations"]:
        failures.append("%s: %d identity violations" % (name, len(r["identity_audit"]["violations"])))
inside = {"L8_worsened": E8["summary"]["worsened"], "L9_worsened": E9["summary"]["worsened"], "worsened_ids": E8["summary"]["worsened_ids"] + E9["summary"]["worsened_ids"]}
checks = {
    "outside_gate_identity": all(not r["identity_audit"]["violations"] for r in (E8, E9, U)),
    "canaries_all_pass": U["summary"]["canaries_all_pass"],
    "inside_gate_exact_nonregression": inside["L8_worsened"] == 0 and inside["L9_worsened"] == 0, "inside": inside,
    "full_universe_ok": U["summary"]["regression_universe_ok"], "universe_worsened_any": U["summary"]["worsened_any"], "universe_worst": U["summary"]["worst_regression_rel"],
    "L10_ok": (L10["summary"]["L10_ok"] if L10 else None),
    "improvement_L9": {"recovery": E9["summary"]["recovery"], "aggregate_reduction": E9["summary"]["aggregate_probe_reduction_rel"], "ok": E9["summary"]["recovery"] >= 0.33 and E9["summary"]["aggregate_probe_reduction_rel"] >= 0.01},
    "improvement_L8_reported": {"recovery": E8["summary"]["recovery"], "aggregate_reduction": E8["summary"]["aggregate_probe_reduction_rel"]},
    "work": {"L8_median": E8["summary"]["C_median_units"], "L9_median": E9["summary"]["C_median_units"], "L8_ratio": E8["summary"]["median_ratio"], "L9_ratio": E9["summary"]["median_ratio"], "max": max(E8["summary"]["C_max_units"], E9["summary"]["C_max_units"], U["summary"]["C_max_units"]),
             "ok": max(E8["summary"]["C_median_units"], E9["summary"]["C_median_units"]) <= 25000 and max(E8["summary"]["median_ratio"], E9["summary"]["median_ratio"]) <= 10 and max(E8["summary"]["C_max_units"], E9["summary"]["C_max_units"], U["summary"]["C_max_units"]) <= 100000},
}
if failures or not checks["outside_gate_identity"]:
    verdict = "INSTRUMENT_FAILURE"
elif not (checks["canaries_all_pass"] and checks["inside_gate_exact_nonregression"] and checks["full_universe_ok"]):
    verdict = "GATE_FAILS_TO_ISOLATE"
elif not (checks["improvement_L9"]["ok"] and checks["work"]["ok"] and (checks["L10_ok"] is True)):
    verdict = "SAFE_BUT_NOT_WORTH_IT"
else:
    verdict = "LICENSED_ENDGAME_REPAIR"
out = {"schema": "archaeon.fossil_metabolism_s7.verdict.v0", "preregistration": "S7_PREREG_2026-09-13.json", "candidate_version": E8["candidate_version"], "instrument_failures": failures, "checks": checks, "verdict": verdict}
(HERE / "S7_VERDICT_2026-09-13.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
