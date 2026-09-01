#!/usr/bin/env python
"""D-14 frozen verdict logic under AMENDMENT A1. Deterministic.
Run after run_d14_a1.py. Implements FREEZE_D14.txt sections 1, 7-10
with A1's eligibility instantiation."""

import json
from collections import Counter

THRESH = 0.05


def main():
    sites = [json.loads(l) for l in open("results/a1_sites.jsonl")]
    kids = [json.loads(l) for l in open("results/a1_children.jsonl")]
    meta = json.load(open("results/a1_run_meta.json"))

    excl = Counter()
    for r in kids:
        if "excl" in r:
            excl[r["excl"]] += 1
        if r.get("note") == "parent_faulted":
            excl["parent_faulted"] += 1

    fault_sites = [r for r in sites if r.get("cls") == "FAULT"]
    measured = [r for r in sites if "influence" in r]
    vals = [r["influence"] for r in measured]
    n = len(vals)
    parents = {r["parent"] for r in measured}

    zero = sum(1 for v in vals if v == 0)
    mid = sum(1 for v in vals if 0 < v <= 0.25)
    high = sum(1 for v in vals if v > 0.25)
    middle_mass = mid / n if n else None

    c = meta["controls"]
    gates = dict(
        n_parents=len(parents), n_measured_sites=n,
        n_fault_sites=len(fault_sites),
        distinct_influence_values=len(set(vals)),
        varies=len(set(vals)) >= 3,
        locality_violations=excl.get("locality_violation", 0),
        c1_replay_eval=c["c1_replay_eval"],
        c1_replay_mutate=c["c1_replay_mutate"],
        c2_noop_bad=c["c2_noop_bad"],
        c5_handcheck_all_match=all(h["match"]
                                   for h in c["c5_handcheck"]),
        exclusions=dict(excl))
    support_ok = (len(parents) >= 100 and n >= 1000
                  and gates["varies"]
                  and gates["locality_violations"] == 0
                  and gates["c2_noop_bad"] == 0
                  and gates["c1_replay_eval"] is True
                  and gates["c1_replay_mutate"] is True
                  and gates["c5_handcheck_all_match"])

    if not support_ok:
        verdict = "D14_INDETERMINATE"
    elif middle_mass <= THRESH:
        verdict = "D14_PREDICTION_SURVIVES"
    else:
        verdict = "D14_MECHANISM_FALSIFIED"

    hist = Counter(round(v, 4) for v in vals)
    report = dict(
        spectrum=dict(
            n_sites=n,
            zero_mass=round(zero / n, 6) if n else None,
            middle_mass=round(middle_mass, 6)
            if middle_mass is not None else None,
            high_mass=round(high / n, 6) if n else None,
            counts=dict(zero=zero, middle=mid, high=high,
                        fault=len(fault_sites)),
            value_histogram=dict(sorted(hist.items()))),
        threshold=THRESH, gates=gates, support_ok=bool(support_ok),
        verdict=verdict)
    json.dump(report, open("results/analysis_d14_a1.json", "w"),
              indent=1)
    print(json.dumps(report["spectrum"], indent=1))
    print("gates:", {k: v for k, v in gates.items()
                     if k != "exclusions"})
    print("exclusions:", dict(excl))
    print("support_ok:", support_ok)
    print("VERDICT:", verdict,
          "| middle_mass =", report["spectrum"]["middle_mass"])


if __name__ == "__main__":
    main()
