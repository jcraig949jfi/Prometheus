"""Cycle 062, experiment C: the reviewer's hostile re-census, plus orthogonal dimensions.

THE ATTACK, quoted: *take all 47 and have a dumb rule-based classifier answer only one question
-- "Is something presently false, unavailable, non-reproducible, or knowingly corrupted in the
tested system?" I predict your "zero" explodes.*

WHY THE ORIGINAL PARTITION WAS THE PROBLEM. Cycle 061 used MUTUALLY EXCLUSIVE buckets, so every
node id got exactly one label and the label that won was the one describing its immediate
mechanism. That structure lets a defect migrate -- failure, then known failure, then deliberate
red, then "not an unaddressed defect" -- with nothing in the world improving. The reviewer calls
this ontology capture and I accept the diagnosis.

THE REPLACEMENT: orthogonal dimensions, so a case can be defect_present AND known_before AND
repair_blocked at once and none of the three cancels the others.

    DISCOVERY STATE AND WORLD STATE MAY NEVER SHARE A FIELD.
    "Previously diagnosed" is discovery state. "Those 48 volumes are still 0.0" is world state.

HONEST LIMIT OF THIS SCRIPT. The bucket -> dimension mapping below is MY judgement. What it is
not is per-node judgement: the rule is declared once, in one table, and applied uniformly to all
47, so it can be disagreed with wholesale rather than case by case. That is weaker than an
oracle and stronger than deciding each row while looking at it.

    python techne/loop/measure_062_hostile_census.py
"""
from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ROWS = REPO / "techne" / "loop" / "rung_notes"
DEST = ROWS / "cycle_062_hostile_census.json"

TRI = json.loads((ROWS / "cycle_061_red_triage.json").read_text(encoding="utf-8"))

import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("claims_061", REPO / "techne/loop/claims_061.py")
_c61 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c61)

#: Declared ONCE and applied uniformly. Columns:
#:   defect_present                is something presently false / unavailable / non-reproducible
#:                                 / knowingly corrupted?          <- WORLD STATE
#:   known_before_cycle            had this been diagnosed already? <- DISCOVERY STATE
#:   red_caused_by_defect          is the red a symptom of it?
#:   reproducible_in_isolation     does the failure reproduce alone?
#:   repair_available              is a repair known and possible?
#:   repair_blocked_by_missing_data is it blocked on data nobody has?
#:   capability_claim_affected     does the arsenal advertise this as available?
DIMENSIONS = {
    "MISSING_DEPENDENCY": dict(
        defect_present=True,          # the capability is UNAVAILABLE, which is a world fact
        known_before_cycle=True,      # standing as HITL #242
        red_caused_by_defect=True,
        reproducible_in_isolation=True,
        repair_available=True,        # install the package
        repair_blocked_by_missing_data=False,   # blocked on a RULING, not on data
        capability_claim_affected=True,         # techne/inventory.json advertises these tools
    ),
    "NO_LONGER_FAILS": dict(
        defect_present=True,          # suite non-determinism IS a defect in the tested system
        known_before_cycle=False,     # opened as #18 in cycle 061
        red_caused_by_defect=True,
        reproducible_in_isolation=False,
        repair_available=False,       # mechanism undiagnosed, so no repair is known
        repair_blocked_by_missing_data=False,
        capability_claim_affected=False,
    ),
    "DELIBERATELY_RED": dict(
        defect_present=True,          # 48 hyperbolic knots still carry volume 0.0
        known_before_cycle=True,      # cycle 046
        red_caused_by_defect=True,
        reproducible_in_isolation=True,
        repair_available=False,
        repair_blocked_by_missing_data=True,    # the real volumes are unavailable
        capability_claim_affected=True,
    ),
    "STALE_ASSERTION": dict(
        defect_present=True,          # the ORACLE asserts a false literal
        known_before_cycle=True,      # standing as HITL #341
        red_caused_by_defect=True,
        reproducible_in_isolation=True,
        repair_available=True,
        repair_blocked_by_missing_data=False,
        capability_claim_affected=False,
    ),
    "ENVIRONMENT": dict(
        defect_present=True,          # a wall-clock gate with no tolerance is an invalid test
        known_before_cycle=False,     # opened as #19 in cycle 061
        red_caused_by_defect=True,
        reproducible_in_isolation=False,        # verdict depends on machine load
        repair_available=True,
        repair_blocked_by_missing_data=False,
        capability_claim_affected=False,
    ),
}


def bucket_of(row) -> str:
    b = row["bucket"]
    if b == "UNCLASSIFIED":
        return _c61.READ_ASSIGNMENTS.get(row["node"].split("::")[-1], "UNCLASSIFIED")
    return b


def main() -> int:
    rows = []
    for r in TRI["rows"]:
        b = bucket_of(r)
        dims = DIMENSIONS.get(b)
        if dims is None:
            raise SystemExit(f"REFUSING: no dimension rule for bucket {b!r}")
        rows.append({"node": r["node"], "bucket": b, **dims})

    hostile_yes = [r for r in rows if r["defect_present"]]

    # PREDICTION 4's quantity: symptoms vs distinct unavailable capabilities.
    missing_rows = [r for r in TRI["rows"] if bucket_of(r) == "MISSING_DEPENDENCY"]
    distinct_modules = sorted({m.split(" ")[0].rstrip(";")
                               for m in TRI["missing_modules"] if m})
    distinct_test_files = sorted({r["node"].split("::")[0] for r in missing_rows})

    # D_open, the reviewer's metric: new defects PLUS known-unrepaired defects. Discovery state
    # is not allowed to reduce the second term -- only repair is.
    d_new = sum(1 for r in rows if not r["known_before_cycle"])
    d_known_unrepaired = sum(1 for r in rows if r["known_before_cycle"] and r["defect_present"])

    out = {
        "population": ("all 47 red node ids from techne/loop/rung_notes/cycle_061_red_triage.json, "
                       "re-expressed under orthogonal dimensions. Full scan."),
        "command": "python techne/loop/measure_062_hostile_census.py",
        "method_note": ("the bucket -> dimension mapping is declared ONCE in DIMENSIONS and "
                        "applied uniformly; it is my judgement, but not per-node judgement"),
        "hostile_single_question": ("is something presently false, unavailable, non-reproducible "
                                    "or knowingly corrupted in the tested system?"),
        "hostile_YES": len(hostile_yes),
        "hostile_NO": len(rows) - len(hostile_yes),
        "of_total": len(rows),
        "dimension_totals": {
            k: sum(1 for r in rows if r[k])
            for k in ("defect_present", "known_before_cycle", "red_caused_by_defect",
                      "reproducible_in_isolation", "repair_available",
                      "repair_blocked_by_missing_data", "capability_claim_affected")
        },
        "symptoms_vs_capabilities": {
            "missing_dependency_symptoms": len(missing_rows),
            "distinct_absent_packages": len(distinct_modules),
            "distinct_absent_packages_named": distinct_modules,
            "distinct_test_files_affected": len(distinct_test_files),
        },
        "D_open": {
            "D_new_this_cycle": d_new,
            "D_known_unrepaired": d_known_unrepaired,
            "D_open_total": d_new + d_known_unrepaired,
            "note": ("discovery state may not reduce D_known_unrepaired; only REPAIR may. "
                     "This is the metric that makes ontology capture visible."),
        },
        "rows": rows,
    }
    DEST.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
