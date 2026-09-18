"""Close QUALIFY and enter EXECUTE for cw01-e05, in recoverable campaign state.

Records that QUALIFY is CLOSED and EXECUTE is ADMISSIBLE. It does NOT record a
result: no experimental genome has been evaluated under this attempt_id yet.

Provenance is read out of SELFCHECK.json rather than transcribed by hand, and the
timestamp is the real system clock rather than an invented one.
"""
from __future__ import annotations

import json
import pathlib
import time

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parents[1]
STATE = BASE / "CAMPAIGN_STATE.json"

NEW_ARTIFACTS = [
 "lib/contract.py - verdict contracts as first-class objects; canonical hash, freeze(), require_matches()",
 "experiments/cw01-e05/VERDICT_CONTRACT.json - the frozen binding specification, hashed",
 "experiments/cw01-e05/QUALIFY.json - 17 predicates + 7 measurement/specification defects, failed reasoning preserved",
 "experiments/cw01-e05/fixtures_e05.py - F1-F7 against the real driver; F7 proves refusal BEFORE evaluation",
 "experiments/cw01-e05/consistency_e05.py - gate; specification consistency SEPARATED from empirical reconstruction",
 "experiments/cw01-e05/selfcheck_e05.py - verifies COMMITTED state by extracting HEAD, not the working tree",
 "experiments/cw01-e05/SELFCHECK.json - pre-EXECUTE receipt: commit, contract hash, F1-F7, gate, admissibility",
]


def main():
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    sc = json.loads((HERE / "SELFCHECK.json").read_text(encoding="utf-8"))
    assert sc["execute_admissible"], "self-check did not admit EXECUTE; refusing to transition"

    st = json.loads(STATE.read_text(encoding="utf-8"))
    st["updated_local"] = now

    for e in st["experiments"]:
        if e["id"] == "cw01-e05":
            e["status"] = "IN_PROGRESS"
            e["attempts"] = [{
                "attempt_id": sc["attempt_id"],
                "phase": "EXECUTE",
                "disposition": None,
                "qualify_closed_local": now,
                "verdict_contract_sha256": sc["verdict_contract_sha256"],
                "freeze_boundary_commit": sc["commit_sha"],
                "execute_admissible": True,
                "_no_result_yet": "No experimental genome has been evaluated under this attempt_id.",
            }]

    st["active"] = {
        "experiment_id": "cw01-e05",
        "attempt_id": sc["attempt_id"],
        "phase": "EXECUTE",
        "phase_completed": ["RECONCILE", "PREFLIGHT", "INSTANTIATE", "QUALIFY"],
        "title": "Mixture of marginally useful organisms",
        "freeze_boundary": {
            "verdict_contract_sha256": sc["verdict_contract_sha256"],
            "commit": sc["commit_sha"],
            "branch": sc["branch"],
            "fixtures": "%d/%d" % (sum(1 for f in sc["fixtures"] if f["passed"]), len(sc["fixtures"])),
            "consistency_gate": sc["consistency_gate"]["gate"],
            "self_check": "%d/%d" % (sum(1 for f in sc["findings"] if f["passed"]), len(sc["findings"])),
            "binding": {k: sc["binding_specification"][k]
                        for k in ("budget_B", "statistic_name", "BEST", "WORST", "n_subsets")},
            "freeze_rule": sc["freeze_rule"],
            "_rule": "Any required criterion change VOIDS this attempt and opens a new attempt_id. "
                     "Criteria are never repaired in place while evidence accumulates."},
    }

    for a in NEW_ARTIFACTS:
        if a not in st["durable_artifacts"]:
            st["durable_artifacts"].append(a)

    t = st["campaign_totals"]
    t["defects_logged"] = 43
    t["science_defects"] = 26
    t["defects_per_experiment"]["e05"] = 7
    if "lib/contract.py" not in t["reusable_components_landed"]:
        t["reusable_components_landed"].append("lib/contract.py")

    st.setdefault("factory_findings_so_far", []).append(
        "e05's seven QUALIFY defects were one failure: the criterion itself became an experimental "
        "object, three times as a pass criterion. Runtime guards cannot catch that, because each "
        "individual measurement looks clean. lib/contract.py is the missing object - the binding "
        "specification is hashed and frozen before the first organism is evaluated, and the driver "
        "refuses on any drift. The consistency gate separates SPECIFICATION agreement from EMPIRICAL "
        "reconstruction, and it earned its keep on its first run by catching WORLD.json still "
        "defining superadditivity on score after the specification had moved to information.")

    # ASCII-safe: a recovery reader's default platform encoding is not ours to choose
    # (CW01-D050 - ensure_ascii=False made this file crash a naive open() on Windows).
    STATE.write_text(json.dumps(st, indent=1, ensure_ascii=True), encoding="utf-8")

    back = json.loads(STATE.read_text(encoding="utf-8"))
    print("active.phase          : %s" % back["active"]["phase"])
    print("phase_completed       : %s" % back["active"]["phase_completed"])
    print("contract              : %s" % back["active"]["freeze_boundary"]["verdict_contract_sha256"][:16])
    print("fixtures / gate / self: %s / %s / %s"
          % (back["active"]["freeze_boundary"]["fixtures"],
             back["active"]["freeze_boundary"]["consistency_gate"],
             back["active"]["freeze_boundary"]["self_check"]))
    print("e05 status            : %s" % [e["status"] for e in back["experiments"] if e["id"] == "cw01-e05"][0])
    print("e05 disposition       : %s (no result yet, by design)"
          % back["experiments"][4]["attempts"][0]["disposition"])
    print("durable_artifacts     : %d" % len(back["durable_artifacts"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
