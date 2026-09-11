"""Run every season-1 ladder through the gate and write the rows.

Rows ship in the same commit as the verdict they support.

Usage:
    python roles/Hypatia/science/season1/run_season.py
"""
from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
import verify_ladder as V  # noqa: E402

PACKETS = HERE / "packets"
LADDERS = HERE / "ladders"
ROWS = HERE / "results"

# ladder file -> (packet, expectation)
#   "PASS"   a positive case: all gates must pass
#   "REJECT" a control: G6 must FAIL and at least one gap step must exist
PLAN = [
    ("run1_POS-1_atalanta.jsonl", "PKT-ATALANTA.json", "PASS"),
    ("run1_POS-2_hypatia.jsonl", "PKT-HYPATIA.json", "PASS"),
    ("run1_POS-3_nephele.jsonl", "PKT-NEPHELE.json", "PASS"),
    ("run1_POS-4_iris.jsonl", "PKT-IRIS.json", "PASS"),
    ("run1_NEG-1_iris_supplied_deadgating.jsonl", "PKT-NEG-1.json", "REJECT"),
    ("run1_CHEAT-1_atalanta_stripped.jsonl", "PKT-CHEAT-1.json", "REJECT"),
]


def main():
    ROWS.mkdir(parents=True, exist_ok=True)
    rows, verdicts = [], {}

    print("%-42s %-6s %-5s %-5s %-5s %-5s %-6s %-5s %-5s %s"
          % ("ladder", "expect", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "outcome"))
    print("-" * 118)

    for lf, pf, expect in PLAN:
        r = V.verify(LADDERS / lf, PACKETS / pf)
        g = r["gates"]
        gaps = r["gap_count"]
        if expect == "PASS":
            ok = r["all_gates_pass"]
        else:
            ok = (not g["G6"]["pass"]) and gaps >= 1
        verdicts[lf] = ok
        r["expectation"] = expect
        r["expectation_met"] = ok
        rows.append(r)

        def f(x):
            return "IND" if x.get("indeterminate") else ("pass" if x["pass"] else "FAIL")

        print("%-42s %-6s %-5s %-5s %-5s %-5s %-6s %-5s %-5s %s"
              % (lf[:42], expect, f(g["G1"]), f(g["G2"]), f(g["G3"]), f(g["G4"]),
                 f(g["G5"]), f(g["G6"]), f(g["G7"]),
                 "OK" if ok else "NOT AS EXPECTED"))

    # ---- CHEAT-2, the instrumental control: gate vs a payload reader -------
    print()
    cheat2 = {}
    for pf in ("PKT-ATALANTA.json", "PKT-HYPATIA.json",
               "PKT-NEPHELE.json", "PKT-IRIS.json"):
        out = ROWS / ("cheat2_payload_%s.jsonl" % pf.replace("PKT-", "").replace(".json", "").lower())
        V.make_payload_reader_ladder(PACKETS / pf, out)
        r = V.verify(out, PACKETS / pf)
        rejected = not r["all_gates_pass"]
        cheat2[pf] = {"rejected": rejected, "clause": r["gates"]["G6"]["clause"]}
        print("CHEAT-2 payload reader vs %-20s rejected=%s  clause=%s"
              % (pf, rejected, r["gates"]["G6"]["clause"]))

    # ---- season verdict, conditions fixed in PREREGISTRATION s8 ----------
    pos = [lf for lf, _, e in PLAN if e == "PASS"]
    ctl = [lf for lf, _, e in PLAN if e == "REJECT"]
    pos_ok = [lf for lf in pos if verdicts[lf]]
    ctl_ok = [lf for lf in ctl if verdicts[lf]]
    ind = [r["ladder"] for r in rows
           if r["expectation"] == "PASS" and r["gates"]["G5"].get("indeterminate")]
    cheat2_ok = all(v["rejected"] for v in cheat2.values())

    if not cheat2_ok:
        verdict = "VOID"
        why = "CHEAT-2 accepted: the gate does not observe reconstruction"
    elif len(ind) >= 2:
        verdict = "INDETERMINATE"
        why = ("G5 indeterminate on %d positive cases (floor %.0f%% specific "
               "density); the unsupported-step measure is too thin to read"
               % (len(ind), 100 * V.SPECIFIC_DENSITY_FLOOR))
    elif len(ctl_ok) < len(ctl):
        verdict = "NO"
        why = "a control was not correctly rejected"
    elif len(pos_ok) < len(pos):
        verdict = "NO"
        why = "a positive case failed a gate"
    else:
        verdict = "YES"
        why = "all positives passed and all controls were correctly rejected"

    summary = {
        "season": 1,
        "positives_passed": "%d/%d" % (len(pos_ok), len(pos)),
        "controls_correctly_rejected": "%d/%d" % (len(ctl_ok), len(ctl)),
        "g5_indeterminate_positives": ind,
        "cheat2_all_rejected": cheat2_ok,
        "cheat2": cheat2,
        "verdict": verdict,
        "verdict_reason": why,
    }

    print()
    print("positives passed:              %s" % summary["positives_passed"])
    print("controls correctly rejected:   %s" % summary["controls_correctly_rejected"])
    print("G5 indeterminate on positives: %d %s" % (len(ind), ind))
    print("CHEAT-2 rejected everywhere:   %s" % cheat2_ok)
    print()
    print("SEASON VERDICT: %s" % verdict)
    print("  %s" % why)

    (ROWS / "rows.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    (ROWS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print("\nrows:    %s" % (ROWS / "rows.json").relative_to(REPO_ROOT).as_posix())
    print("summary: %s" % (ROWS / "summary.json").relative_to(REPO_ROOT).as_posix())


if __name__ == "__main__":
    main()
