"""Meta-experiment v1 analysis, implementing the frozen decision rules of
roles/Hecate/prereg/2026-09-29_meta_experiment_v1/PREREG.md. Written and
committed before any detector or matcher row was read.

    python -m hecate.meta.analyze    # -> hecate/meta/RESULTS_v1.json (+ printed)
"""

from __future__ import annotations

import collections
import json
import math
import os
import re

from hecate.meta.run_arms import load_arms

HERE = os.path.dirname(os.path.abspath(__file__))
DETECT = os.path.join(HERE, "detector", "detect_rows_v1.jsonl")
MATCH = os.path.join(HERE, "matcher", "match_rows_v1.jsonl")
UNITS = range(8)


def _latest(path, key="item"):
    out = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for l in fh:
                if l.strip():
                    r = json.loads(l)
                    out[r[key]] = r
    return out


def _item(item):
    u, arm, m = re.match(r"u(\d+)-([A-Z])-m(\d+)$", item).groups()
    return int(u), arm, int(m)


def binom_sf(k, n, p):
    """P(X >= k), X ~ Bin(n, p)."""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def m1(det):
    fam = collections.defaultdict(list)      # (unit, arm) -> [is_familiar]
    fams = collections.defaultdict(set)      # (unit, arm) -> nearest family names
    failed = 0
    for item, r in det.items():
        u, arm, _ = _item(item)
        p = r.get("parsed") or {}
        if not r.get("ok"):
            failed += 1
            continue
        fam[(u, arm)].append(p.get("classification") == "FAMILIAR")
        np_ = p.get("nearest_priors") or []
        if np_:
            fams[(u, arm)].add(str(np_[0].get("name", "")).strip().lower()[:60])
    frac = {k: sum(v) / len(v) for k, v in fam.items() if v}
    comparisons = {}
    for x in ("S", "P", "O", "G"):
        wins, eligible = 0, 0
        per_unit = []
        for u in UNITS:
            if (u, "T") in frac and (u, x) in frac:
                eligible += 1
                lower = frac[(u, "T")] < frac[(u, x)]      # ties count as NOT lower
                wins += lower
                per_unit.append({"unit": u, "T": frac[(u, "T")], x: frac[(u, x)], "T_lower": lower})
        if eligible < 8:
            verdict = "NOT_ELIGIBLE"
        elif wins >= 7:
            verdict = f"ADDS_VALUE_vs_{x}"
        elif wins <= 4:
            verdict = f"NO_ADDED_VALUE_vs_{x}"
        else:
            verdict = "INDETERMINATE"
        comparisons[x] = {"T_lower_in": wins, "eligible_units": eligible,
                          "sign_test_p_one_sided": binom_sf(wins, eligible, 0.5) if eligible else None,
                          "verdict": verdict, "descriptive_only": x == "G", "per_unit": per_unit}
    v = {x: comparisons[x]["verdict"] for x in ("S", "P", "O")}
    if all(v[x].startswith("ADDS_VALUE") for x in v):
        overall = "TRIPLICATES_REDUCE_FAMILIARITY"
    elif v["O"].startswith("NO_ADDED_VALUE"):
        overall = "TRIPLICATES_DO_NOT_REDUCE_FAMILIARITY"
    else:
        overall = "INDETERMINATE"
    arm_means = {a: sum(frac[(u, a)] for u in UNITS if (u, a) in frac) /
                 max(1, sum(1 for u in UNITS if (u, a) in frac)) for a in "TPSOG"}
    class_counts = {a: dict(collections.Counter(
        (r.get("parsed") or {}).get("classification") for i, r in det.items()
        if r.get("ok") and _item(i)[1] == a)) for a in "TPSOG"}
    m4 = {a: [len(fams[(u, a)]) for u in UNITS] for a in "TPSOG"}
    return {"familiar_fraction_mean_by_arm": arm_means, "classification_counts": class_counts,
            "comparisons": comparisons, "overall": overall, "detector_failed_items": failed,
            "M4_family_spread_by_unit": m4}


def m2(match):
    out = {}
    for arm in ("T", "P"):
        rows = [r for r in match.values() if r["arm"] == arm and r.get("ok")]
        n, k = len(rows), sum(r["correct"] for r in rows)
        acc = k / n if n else None
        if n < 80:
            verdict = f"NOT_ELIGIBLE (n={n})"
        elif k >= 36:
            verdict = "LABELS_SHAPE_OUTPUT"
        elif k <= 25:
            verdict = "LABELS_DECORATIVE"
        else:
            verdict = "INDETERMINATE"
        out[arm] = {"n": n, "correct": k, "accuracy": acc,
                    "binom_p_vs_chance": binom_sf(k, n, 0.25) if n else None, "verdict": verdict}
    return out


COMPARATOR = re.compile(r"\b(baseline|null|control|versus|vs\.?|than|compared)\b", re.I)


def m3():
    per_arm = collections.defaultdict(lambda: collections.Counter())
    for a in load_arms():
        if a["status"] != "OK":
            continue
        for m in a["mechanisms"]:
            c = per_arm[a["arm"]]
            c["n"] += 1
            we = m.get("what_exists")
            c["state_named"] += isinstance(we, list) and len(we) >= 2
            c["change_rule"] += bool(str(m.get("what_changes") or "").strip())
            c["intervention_in_world"] += bool(re.search(r"interven|manipulat|ablat|remove|knock", str(m.get("minimal_world") or ""), re.I))
            c["comparator"] += bool(COMPARATOR.search(str(m.get("distinguishing_observable") or "")))
    return {a: {k: (v / c["n"] if k != "n" else v) for k, v in c.items()} for a, c in sorted(per_arm.items())}


def main():
    det, match = _latest(DETECT), _latest(MATCH)
    res = {"prereg": "roles/Hecate/prereg/2026-09-29_meta_experiment_v1/PREREG.md",
           "calibration": "hecate/gravity/CALIBRATION_v1.json (gate PASS)",
           "detector_items": len(det), "matcher_items": len(match),
           "M1": m1(det), "M2": m2(match), "M3_structural_specificity": m3()}
    with open(os.path.join(HERE, "RESULTS_v1.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(res, indent=2, ensure_ascii=True) + "\n")
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps({"M1_overall": r["M1"]["overall"],
                      "M1_means": r["M1"]["familiar_fraction_mean_by_arm"],
                      "M1_verdicts": {k: v["verdict"] for k, v in r["M1"]["comparisons"].items()},
                      "M2": {k: (v["accuracy"], v["verdict"]) for k, v in r["M2"].items()}}, indent=2))
