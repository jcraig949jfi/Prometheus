"""Assemble the machine-readable Phase-1 verdict from the four binding-run
results. The verdict LOGIC is the frozen gate evaluator's output already
recorded in each results file; this script only aggregates — it computes
nothing gate-relevant.
"""
from __future__ import annotations

import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBS = ["S1_REG", "S2_STACK", "S3_REWRITE", "S4_MEM"]


def main():
    per = {}
    passed = []
    for name in SUBS:
        p = os.path.join(BASE, "results", f"{name}_results.json")
        if not os.path.exists(p):
            per[name] = {"status": "MISSING"}
            continue
        r = json.load(open(p))
        g = r.get("gates", {})
        per[name] = {
            "primary": g.get("primary"),
            "flags": g.get("flags"),
            "witness_viable": r.get("witness", {}).get("viable"),
            "viable_frac": r.get("census", {}).get("viable_frac"),
            "combined_classes": r.get("diversity", {}).get("combined_classes"),
            "pair_pooled_hits": r.get("nav_summary", {}).get("pair_pooled_hits"),
            "best_pair_nav": r.get("nav_summary", {}).get("best_pair_nav"),
            "margins": g.get("margins"),
            "meter_evals_total": r.get("meter", {}).get("evals_total"),
            "wall_seconds": r.get("wall_seconds"),
            "thresholds_status": g.get("thresholds_status"),
        }
        if g.get("primary") == "PASS":
            passed.append(name)
    overall = ("ACCESSIBILITY_GEOMETRY_ESTABLISHED:" + ",".join(passed)
               if passed else "NO_BASIS_PASSED")
    out = {
        "generation": "AGENT_D4_BLIND_PHASE1",
        "date": "2026-08-27",
        "overall_verdict": overall,
        "substrates_passed": passed,
        "per_substrate": per,
        "claim_ceiling": "P1-P4 properties of frozen computational substrates "
                         "only; no P5/P6 claim under any outcome",
    }
    with open(os.path.join(BASE, "results", "phase1_verdict.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print("OVERALL:", overall)
    for name in SUBS:
        print(f"  {name}: {per[name].get('primary')}  flags={per[name].get('flags')}")


if __name__ == "__main__":
    main()
