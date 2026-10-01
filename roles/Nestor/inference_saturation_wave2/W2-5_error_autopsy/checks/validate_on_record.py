"""Retrospective validation: run the checks on the REAL frozen records of the incidents they were
built from (read-only). Each check must re-find its historical defect from committed data.

    cd W2-5_error_autopsy && python -B -m checks.validate_on_record

Writes RECORD_VALIDATION.json next to REPORT.md. Reads only roles/Nestor/campaigns/*.
"""
import glob
import json
import os

from .identical_arms import detect_identical_arms, detect_identical_summaries
from .plugin_baseline import check_plugin_baseline
from .run_level_label import check_label_holds_for_unit

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "RECORD_VALIDATION.json")
CAMP = os.path.normpath(os.path.join(HERE, "..", "..", "..", "campaigns"))


def _load(p):
    with open(os.path.join(CAMP, p), encoding="utf-8") as f:
        return json.load(f)


def main():
    out = {}
    # 1. C9 H1 (C9-D16): only arm summaries survive in the adjudication
    h1 = _load("z80atlas-verify-2026-09-22/observatory/ADJUDICATION_C9.json")["hypotheses"]["H1"]
    summ = {a: {"held": h1["means_held_final"][a], **h1["readouts_only"][a]} for a in h1["means_held_final"]}
    out["C9_H1_frozen"] = detect_identical_summaries(summ).__dict__

    # 2. C9-H1R repaired rerun: per-seed rows; the cost-free pair is identical by construction
    rows = _load("c9x-explore-2026-09-24/c9_h1r/RESULTS.json")
    rows = [dict(r, crossed_ever=int(bool(r.get("crossed_ever"))),
                 crossed_at_final=int(bool(r.get("crossed_at_final")))) for r in rows]
    out["C9_H1R_undeclared"] = detect_identical_arms(rows).__dict__
    out["C9_H1R_declared"] = detect_identical_arms(
        rows, declared_identical={("gate_off_cost_free", "gate_on_cost_free"):
                                  "author-declared: a free cue makes the gate a no-op (GRAPH:75)"}).__dict__

    # 3. W1 X-DD-ESTABLISH: run label ESTABLISHED vs the D0's own causal births (dossier D U1)
    recs = []
    for p in sorted(glob.glob(os.path.join(CAMP, "npe-w1-donor-discovery-2026-09-26/x_dd_establish/results/*.json"))):
        with open(p, encoding="utf-8") as f:
            r = json.load(f)
        recs.append({"run": "%s_%s" % (r.get("cell"), r.get("seed")), "status": r.get("status"),
                     "lineage_births": r.get("lineage_births")})
    out["XDD_ESTABLISH_label"] = check_label_holds_for_unit(recs, "status", "ESTABLISHED", "lineage_births").__dict__

    # 4. C-CRITICAL-MASS (D-12) plug-in vs joint; then the declared X-DOSE-CURVE
    cm = _load("c9x-explore-2026-09-24/c_critical_mass/VERDICT.json")
    n = cm["n_per_k"]
    out["C_CRITICAL_MASS_two_doses"] = check_plugin_baseline(
        {int(k): (v, n) for k, v in cm["depth_ge5"].items()}, target_k=4).__dict__
    dc = _load("c9x-explore-2026-09-24/x_dose_curve/SUMMARY.json")
    m = dc["n_per_k"]
    out["X_DOSE_CURVE"] = check_plugin_baseline({int(k): (v, m) for k, v in dc["depth_ge5"].items()},
                                                target_k=4).__dict__
    out["X_DOSE_CURVE"]["recorded_lrt_p"] = dc["lrt_p"]

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    for k, v in out.items():
        print("%-28s %-26s %s" % (k, v["verdict"], v["reason"]))


if __name__ == "__main__":
    main()
