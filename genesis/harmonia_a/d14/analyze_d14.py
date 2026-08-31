#!/usr/bin/env python
"""D-14 frozen verdict logic, per FREEZE_D14.txt sections 6-10.
Deterministic. Run after run_d14.py."""

import json
from collections import Counter, defaultdict

THRESH = 0.05
MID_LO, MID_HI = 0.0, 0.25


def main():
    rows = [json.loads(l) for l in open("results/pairs_raw.jsonl")]
    meta = json.load(open("results/run_meta.json"))

    excl = Counter()
    eligible = []
    for r in rows:
        if "geno_error" in r:
            excl["genotype_fetch_error"] += 1
            continue
        if r["diff_count"] == -1:
            excl["length_changed"] += 1
            continue
        if r["diff_count"] == 0:
            excl["diff0_noop_class"] += 1
            continue
        if r["diff_count"] > 1:
            excl["locality_violation_diffgt1"] += 1
            continue
        if r.get("parent_faulted"):
            excl["parent_faulted"] += 1
            continue
        if r.get("child_faulted"):
            excl["child_faulted_FAULT_class"] += 1
            continue
        eligible.append(r)

    # C2 no-op control: diff==0 pairs must be behaviorally identical
    noop_bad = [r for r in rows
                if r.get("diff_count") == 0
                and not (r.get("displacement") == 0
                         and r.get("exact_match"))]
    # frozen first-hit selection: order = (seed asc, order asc)
    eligible.sort(key=lambda r: (r["seed"], r["order"]))
    influence = {}
    extras = defaultdict(list)
    for r in eligible:
        key = (r["parent_id"], r["site"])
        if key not in influence:
            influence[key] = r["displacement"]
        else:
            extras[str(key)].append(r["displacement"])

    vals = list(influence.values())
    n = len(vals)
    zero = sum(1 for v in vals if v == 0)
    mid = sum(1 for v in vals if MID_LO < v <= MID_HI)
    high = sum(1 for v in vals if v > MID_HI)
    middle_mass = mid / n if n else None
    parents = {k[0] for k in influence}

    gates = dict(
        n_parents=len(parents), n_measured_sites=n,
        distinct_influence_values=len(set(vals)),
        varies=len(set(vals)) >= 3,
        locality_violations=excl.get("locality_violation_diffgt1", 0),
        noop_control_bad=len(noop_bad),
        replay_control=meta.get("replay_check"),
        handcheck=meta.get("handcheck"),
        metrics={c["seed"]: c["metric"] for c in meta["calls"]},
        exclusions=dict(excl))
    support_ok = (len(parents) >= 100 and n >= 1000
                  and gates["varies"]
                  and gates["locality_violations"] == 0
                  and len(noop_bad) == 0
                  and meta["replay_check"]["displacements_equal"]
                  and meta["replay_check"]["pair_ids_equal"]
                  and all(h["match"] for h in meta.get("handcheck", [])))

    if not support_ok:
        verdict = "D14_INDETERMINATE"
    elif middle_mass <= THRESH:
        verdict = "D14_PREDICTION_SURVIVES"
    else:
        verdict = "D14_MECHANISM_FALSIFIED"

    report = dict(
        spectrum=dict(n_sites=n,
                      zero_mass=round(zero / n, 6) if n else None,
                      middle_mass=round(middle_mass, 6)
                      if middle_mass is not None else None,
                      high_mass=round(high / n, 6) if n else None,
                      counts=dict(zero=zero, middle=mid, high=high)),
        threshold=THRESH, gates=gates, support_ok=bool(support_ok),
        verdict=verdict,
        n_duplicate_site_samples=sum(len(v) for v in extras.values()))
    json.dump(report, open("results/analysis_d14.json", "w"), indent=1)
    json.dump({f"{k[0]}|{k[1]}": v for k, v in influence.items()},
              open("results/influence_sites.json", "w"), indent=1)
    print(json.dumps(report["spectrum"], indent=1))
    print("support_ok:", support_ok)
    print("exclusions:", dict(excl))
    print("VERDICT:", verdict,
          "| middle_mass =", report["spectrum"]["middle_mass"])


if __name__ == "__main__":
    main()
