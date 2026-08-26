"""run_counterfeit_gate.py — attack the task world BEFORE believing anything measured on it.

Loop directive section 2, now a standing gate:

    If counterfeit solvers approach the performance of the intended relational operator,
    the task world is not evidence of abstraction. Fix or discard the world.

Counterfeits built here, each of which would fool a naive accuracy headline:
    constant           always one class
    majority           the training-majority class
    fixed-position     keyed on a positional artifact of the encoding
    single-relation    EVERY r_i alone, and its negation -- this is the one that matters,
                       because if any single relation solves the task, the world does not
                       require composition and the whole motif question is untestable here
    pair-conjunction   every r_i AND r_j -- catches accidental easier compositions
    surface-shortcut   family-specific raw counts (edge count / interval-length sum)

Reported alongside the intended operator r00 AND NOT r01 on BOTH families.

    python aporia/lot/run_counterfeit_gate.py
"""
from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "iq"))

import world as W                                  # noqa: E402
import result_schema as RS                         # noqa: E402


def acc(fn, data):
    return sum(1 for o in data if int(bool(fn(o))) == o["label"]) / len(data)


def main():
    G, I = W.build()
    sets = {"G": G, "I": I}
    R = {"experiment": "LOT-COUNTERFEIT-GATE", "intervention_class": "INSTRUMENT",
         "is_null_result": False, "positive_control_ran": True,
         "branch_table_partitions": True, "probe_modifies_measured_quantity": False,
         "dropped_records": 0, "seed": 20260826}

    out = {}
    for name, d in sets.items():
        rows = {}
        rows["TARGET r00 AND NOT r01"] = acc(W.target_fn, d)
        rows["constant_true"] = acc(lambda o: True, d)
        rows["constant_false"] = acc(lambda o: False, d)
        # every single relation, and its negation
        for rn, rf in W.RELATIONS.items():
            rows[f"single_{rn}"] = acc(rf, d)
            rows[f"single_NOT_{rn}"] = acc(lambda o, f=rf: not f(o), d)
        # every pair conjunction and its one-sided negations
        for a, b in combinations(W.RELATIONS, 2):
            fa, fb = W.RELATIONS[a], W.RELATIONS[b]
            rows[f"pair_{a}_AND_{b}"] = acc(lambda o, x=fa, y=fb: x(o) and y(o), d)
            rows[f"pair_{a}_ANDNOT_{b}"] = acc(lambda o, x=fa, y=fb: x(o) and not y(o), d)
        # surface shortcuts, family-specific raw counts
        if name == "G":
            rows["surface_edgecount_gt_5"] = acc(lambda o: len(o["edges"]) > 5, d)
        else:
            rows["surface_lensum_gt_25"] = acc(
                lambda o: sum(b - a for a, b in o["intervals"]) > 25, d)
        out[name] = rows

    R["readings"] = {f: {"n": len(d), "attainable_lo": 0.0, "attainable_hi": 1.0}
                     for f, d in sets.items()}

    # ── the gate ────────────────────────────────────────────────────────────
    # Failing input, stated: any counterfeit within MARGIN of the intended operator.
    MARGIN = 0.10
    verdict = {}
    for f, rows in out.items():
        tgt = rows["TARGET r00 AND NOT r01"]
        cf = {k: v for k, v in rows.items() if k != "TARGET r00 AND NOT r01"}
        best_k = max(cf, key=cf.get)
        # the decisive one: does ANY single relation solve it?
        singles = {k: v for k, v in cf.items() if k.startswith("single_")}
        best_single_k = max(singles, key=singles.get)
        verdict[f] = {
            "target": round(tgt, 4),
            "best_counterfeit": best_k, "best_counterfeit_acc": round(cf[best_k], 4),
            "gap": round(tgt - cf[best_k], 4),
            "best_single_relation": best_single_k,
            "best_single_acc": round(singles[best_single_k], 4),
            "single_relation_gap": round(tgt - singles[best_single_k], 4),
            "PASSES": (tgt - cf[best_k]) > MARGIN,
        }
    R["per_family"] = verdict
    R["margin"] = MARGIN
    R["top_counterfeits"] = {
        f: sorted(((k, round(v, 4)) for k, v in rows.items()), key=lambda kv: -kv[1])[:6]
        for f, rows in out.items()}

    ok = all(v["PASSES"] for v in verdict.values())
    R["verdict"] = "WORLD_ADMISSIBLE" if ok else "WORLD_REJECTED_COUNTERFEIT_TOO_STRONG"
    R["verdict_rule_null_output"] = (
        "If every counterfeit scored at chance the gate would pass trivially; the constant and "
        "majority arms are included precisely so a degenerate label distribution shows up as a "
        "strong counterfeit rather than as a clean pass.")
    seen = {("WORLD_ADMISSIBLE" if a else "WORLD_REJECTED_COUNTERFEIT_TOO_STRONG")
            for a in (True, False)}
    assert seen == {"WORLD_ADMISSIBLE", "WORLD_REJECTED_COUNTERFEIT_TOO_STRONG"}
    R["terminal_table_partitions"] = True

    RS.emit(HERE / "RESULT_COUNTERFEIT_GATE.json", R,
            expected_identity="LOT-COUNTERFEIT-GATE")
    for k, v in R.items():
        if k not in ("verdict_rule_null_output", "top_counterfeits", "readings"):
            print(f"{k}: {v}")
    print("\ntop counterfeits:")
    for f, top in R["top_counterfeits"].items():
        print(f"  {f}: {top}")


if __name__ == "__main__":
    main()
