"""Close cw01-e08 in CAMPAIGN_STATE.json from RESULT.json; totals derived from the ledger and gated."""
from __future__ import annotations

import collections
import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent


def _bootstrap_lib():
    for cand in [HERE] + list(HERE.parents):
        if (cand / "lib" / "repopath.py").exists():
            sys.path.insert(0, str(cand / "lib"))
            return cand / "lib"
    raise RuntimeError("cannot locate lib/repopath.py walking up from %s" % HERE)


_bootstrap_lib()
import repopath as RP          # noqa: E402
import recordsafety as RS      # noqa: E402

CAMPAIGN = RP.find_campaign_root(HERE)
STATE = CAMPAIGN / "CAMPAIGN_STATE.json"
LEDGER = CAMPAIGN / "DEFECTS.jsonl"


def main(rows_commit="", result_commit=""):
    st = json.loads(STATE.read_text(encoding="utf-8"))
    res = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    q = json.loads((HERE / "QUALIFY.json").read_text(encoding="utf-8"))
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    disp = res["disposition"]
    exp = next(e for e in st["experiments"] if e["id"] == "cw01-e08")
    exp["status"] = "COMPLETE"
    exp["attempts"] = [{"attempt_id": "cw01-e08-a01", "phase": "PACKAGE", "disposition": disp,
                        "started_local": "2026-09-18 08:30:00", "ended_local": now,
                        "verdict_contract_sha256": res["verdict_contract_sha256"],
                        "freeze_boundary_commit": "e902f09a3", "executed_under_frozen_contract": True,
                        "qualify_runs": 3, "rows": res["rows"]["n_rows"], "rows_commit": rows_commit,
                        "result_commit": result_commit}]
    exp["disposition"] = disp.split(" / ")[0]
    ct = res.get("contrast") or {}
    exp["headline"] = {
        "disposition_reason": res["disposition_reason"],
        "world": "w13 (the only R4 survivor); organism = substrate tt_digits + evolvable per-bond ranks + read mask",
        "tax": "lambda 390 = 2 x lambda_max (Q3 rule), equal weights over (bond, params, flops, bits)",
        "c_tax": ct.get("c_tax"), "c_tax_null": [ct.get("c_tax_p05"), ct.get("c_tax_p95")],
        "c_int": ct.get("c_int"), "c_int_inside_null": ct.get("c_int_inside"),
        "competent_lineages_per_arm": {a: v["n_competent_lineages"] for a, v in res["per_arm"].items()},
        "noncompetent_excess": res["noncompetent_excess"],
        "scalar_burden_per_arm_all_reps": {a: round(v["scalar_mean_all"], 3) for a, v in res["per_arm"].items()},
        "capability_per_arm_all_reps": {a: round(v["C_mean_all"], 1) for a, v in res["per_arm"].items()},
        "qualification": "Q1-Q7 QUALIFIED on run 3 after two checker repairs (D062, D063); all 8 accounting fixtures charged or refused",
    }
    exp["limitations"] = [
        "One world, one organism family, eight lineages per arm, 200 generations (frozen by the Q4 rule from a pilot that cleared the trivial floor at generation 0).",
        "The tax coefficient was frozen at the top of the sweep because the preregistered rule takes the largest qualifying value and criterion (d) cannot bind above (CW01-D064).",
        "Competence on held64 is a minority outcome in every arm (CW01-D065); the analysis is over competent lineages and reports the non-competent count per arm.",
        "Per-bond rank evolution is a bridge built here; it is not the substrate as previously run.",
    ]
    st["active"] = {"experiment_id": "cw01-e08", "attempt_id": "cw01-e08-a01", "phase": "PACKAGE",
                    "disposition": disp,
                    "phase_completed": ["RECONCILE", "PREFLIGHT", "INSTANTIATE", "QUALIFY", "EXECUTE",
                                        "CLOSE_SCIENCE", "TEARDOWN", "VERIFY_ABSENCE", "PACKAGE"],
                    "next": "CONTINUE -> cw01-e09 algorithmic soup (awaiting operator brief)"}
    st["updated_local"] = now
    st["owned_runtime_resources"] = []
    st["durable_artifacts"] += [
        "experiments/cw01-e08/SUBSTRATE_RECONCILE.md - what the real TT organism possesses, mapped to (bond, params, flops, bits) before any code",
        "experiments/cw01-e08/PREREGISTRATION.md - 2x2 factorial, lineage as unit, capability-adjusted burden, Q1-Q7, dispositions incl. INVALID",
        "experiments/cw01-e08/world_e08.py - per-bond ranks joined to the substrate's TT forward (exact by zero-padding), recount, amputation/sham, assay, stratified randomisation",
        "experiments/cw01-e08/qualify_e08.py + QUALIFY_run1/run2/QUALIFY.json - three runs; tax attainability curve published",
        "experiments/cw01-e08/VERDICT_CONTRACT.json - hashed before EXECUTE",
        "experiments/cw01-e08/rows/cw01-e08-a01.jsonl - generation, assay and lineage rows, every row stamped with the contract hash",
        "experiments/cw01-e08/fossils/representatives.npz - packed genomes of every representative with arm/lineage/sha metadata",
        "experiments/cw01-e08/RESULT.json - disposition through lineage.decide; per-coordinate secondary contrasts",
    ]
    st["factory_findings_so_far"].append(
        "e08 ran on the REAL substrate organism for the first time in the campaign: the reconcile step found that literal "
        "rank exists but is a constant, that the only rank tax in the repo was never joined to evolution, and that the "
        "substrate's entry module needs a redis client the interpreter lacks - all three shaped the design before a line of "
        "evolutionary code. Qualification refused twice on its own fixtures (both checker defects, repaired once each) and "
        "then passed; the frozen tax landed at the top of its sweep because a preregistered upper-bound criterion could not "
        "bind, which is the kind of rule defect e07's D058 predicted and this time was caught as an observation rather than a "
        "wall. Disposition: %s." % disp)
    entries = [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]
    per = collections.Counter(d.get("experiment_id") for d in entries)
    tot = st["campaign_totals"]
    tot["experiments_attempted"] = 8
    key = {"COMPLETE": "complete", "NULL": "null", "NEGATIVE": "negative", "INCONCLUSIVE": "inconclusive"}.get(exp["disposition"])
    if key:
        tot[key] = tot.get(key, 0) + 1
    tot["defects_logged"] = len(entries)
    tot["defects_per_experiment"] = {str(k).replace("cw01-", ""): v for k, v in sorted(per.items())}
    STATE.write_text(json.dumps(st, indent=1, ensure_ascii=True), encoding="utf-8")
    RS.require_ascii_safe(STATE)
    RS.require_ascii_safe(HERE / "RESULT.json")
    v = RS.require_tally_consistent(STATE, LEDGER)
    print("CAMPAIGN_STATE closed for e08: %s | tally %s (%d)" % (disp, v["outcome"], v["derived"]["total"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
