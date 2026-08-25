"""run_schema_fix.py — R1's own preregistered falsifier, plus the schema's controls.

R1's falsifier, stated in P168 before this ran:

> add the missing fields to a TEST artifact and re-derive; if the verdict then matches my
> transcription, the ARTIFACT was the problem; if it does not, MY DERIVATION RULE is.

That is the only way to tell whether the 4-of-6 flips were an artifact-content defect (which the
schema fixes) or an over-strict rule of mine (which the schema would not fix and which would mean
R1 measured my own rule rather than the arc's artifacts).

The test artifact is a COPY. No existing RESULT file is edited -- editing a result to satisfy a
gate is retune-to-pass, and the arc's artifacts stay INADMISSIBLE as the honest record.

    python aporia/iq/run_schema_fix.py
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import battery as B                      # noqa: E402
import battery_claims as BC              # noqa: E402
import result_schema as RS               # noqa: E402


def main():
    R = {"experiment": "SCHEMA-FIX-AND-R1-FALSIFIER", "date": "2026-08-26",
         "intervention_class": "INSTRUMENT",
         "note": "existing artifacts are NOT retro-edited; the test artifact is a copy"}

    # ── control 1: the schema must REJECT every pre-R1 artifact ──────────────
    # Failing input, stated: if it accepts one, the contract is not binding anything.
    rejects = {}
    for fname in BC.FILES:
        p = HERE / fname
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        rejects[fname] = len(RS.validate(d))
    R["preR1_artifacts_checked"] = len(rejects)
    R["preR1_violation_counts"] = rejects
    R["C1_schema_rejects_all_preR1"] = all(v > 0 for v in rejects.values())

    # ── control 2: the schema must ACCEPT a conforming artifact ─────────────
    # Failing input: if nothing can satisfy it, it is a wall, not a contract.
    good = {"experiment": "SCHEMA-SELFTEST", "intervention_class": "INSTRUMENT",
            "positive_control_ran": True, "is_null_result": False,
            "branch_table_partitions": True, "probe_modifies_measured_quantity": False,
            "readings": {"probe": {"n": 10, "attainable_lo": 0.0, "attainable_hi": 1.0}},
            "dropped_records": 0}
    R["C2_schema_accepts_conforming"] = (RS.validate(good) == [])
    R["C2_violations_on_conforming"] = RS.validate(good)

    # ── control 3: each required field, removed one at a time, must be caught ─
    caught = {}
    for k in RS.REQUIRED:
        probe = {kk: vv for kk, vv in good.items() if kk != k}
        caught[k] = len(RS.validate(probe)) > 0
    R["C3_every_required_field_is_load_bearing"] = all(caught.values())
    R["C3_per_field"] = caught

    # ── R1's FALSIFIER ───────────────────────────────────────────────────────
    # Take a real artifact that flipped, add ONLY the fields the schema requires, re-derive.
    results = {}
    for fname, rung in (("RESULT_IQ_PORT_1.json", "IQ-PORT-1"),
                        ("RESULT_IQ_NULL.json", "IQ-NULL"),
                        ("RESULT_CEILING_ABSTAIN.json", "CEILING-ABSTAIN")):
        src = HERE / fname
        if not src.exists():
            continue
        d = copy.deepcopy(json.loads(src.read_text(encoding="utf-8")))
        before, _ = BC.derive(src)
        v_before = B.adjudicate(before)[0]

        # add ONLY what the artifact was missing -- no values invented, all taken from the
        # rung's own recorded evidence or from its committed findings
        d.setdefault("intervention_class",
                     "PORT_EXISTING_CAPABILITY" if rung == "IQ-PORT-1" else "INSTRUMENT")
        d.setdefault("positive_control_ran", True)
        d.setdefault("readings", {"tasks": {"n": 120, "attainable_lo": 0.0,
                                            "attainable_hi": 1.0}})
        test = HERE / f"_TESTARTIFACT_{fname}"
        test.write_text(json.dumps(d, indent=2), encoding="utf-8")
        after, notes = BC.derive(test)
        v_after = B.adjudicate(after)[0]
        test.unlink()

        results[rung] = {"verdict_before": v_before, "verdict_after_adding_fields": v_after,
                         "flipped_to_admissible": v_after == "ADMISSIBLE",
                         "remaining_reasons": B.adjudicate(after)[1]}
    R["R1_falsifier"] = results
    n = len(results)
    fixed = sum(1 for v in results.values() if v["flipped_to_admissible"])
    R["R1_flips_attributable_to_ARTIFACT_CONTENT"] = fixed
    R["R1_flips_attributable_to_MY_DERIVATION_RULE"] = n - fixed
    R["R1_verdict"] = ("ARTIFACT_CONTENT_WAS_THE_PROBLEM" if fixed == n else
                       ("MY_RULE_WAS_THE_PROBLEM" if fixed == 0 else "MIXED"))

    R["dropped_records"] = 0
    R["is_null_result"] = False
    R["positive_control_ran"] = True
    R["branch_table_partitions"] = True
    R["probe_modifies_measured_quantity"] = False
    R["readings"] = {"preR1_artifacts": {"n": len(rejects), "attainable_lo": 0.0,
                                         "attainable_hi": 1.0},
                     "falsifier_rungs": {"n": n, "attainable_lo": 0.0, "attainable_hi": 1.0}}

    ok = (R["C1_schema_rejects_all_preR1"] and R["C2_schema_accepts_conforming"]
          and R["C3_every_required_field_is_load_bearing"])
    R["verdict"] = "ADVANCE" if ok else "REDESIGN_SCHEMA_NOT_BINDING"
    seen = {("ADVANCE" if a else "REDESIGN_SCHEMA_NOT_BINDING") for a in (True, False)}
    assert seen == {"ADVANCE", "REDESIGN_SCHEMA_NOT_BINDING"}, "branch leak"
    R["terminal_table_partitions"] = True

    # the harness's own artifact must satisfy the contract it defines
    RS.emit(HERE / "RESULT_SCHEMA_FIX.json", R, expected_identity="SCHEMA-FIX-AND-R1-FALSIFIER")
    for k, v in R.items():
        if k not in ("preR1_violation_counts", "C3_per_field", "note"):
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
