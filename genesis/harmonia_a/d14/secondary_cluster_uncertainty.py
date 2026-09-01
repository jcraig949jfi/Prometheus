#!/usr/bin/env python
"""D-14 SECONDARY, EXPLICITLY NON-ADJUDICATING uncertainty analysis.

Purpose (campaign order s.2): characterize how much population-level
generalization the measured A2 sample supports. Sites cluster within
parents and are NOT IID; a parent-cluster bootstrap is used.

THIS SCRIPT CANNOT ALTER THE FROZEN D-14 VERDICT. It reads the same
rows the frozen adjudicator reads and reports intervals only. Frozen
before A2 results were read; stat seed 20260915; 10,000 resamples.
"""

import json
from collections import defaultdict

import numpy as np

STAT_SEED = 20260915
N_BOOT = 10_000


def main():
    sites = [json.loads(l) for l in open("results/a2_sites.jsonl")]
    measured = [r for r in sites if "influence" in r]
    by_parent = defaultdict(list)
    for r in measured:
        by_parent[r["parent"]].append(r["influence"])
    parents = sorted(by_parent)
    n_parents = len(parents)
    vals = [v for p in parents for v in by_parent[p]]
    n = len(vals)

    def masses(vs):
        vs = np.asarray(vs)
        return (float(np.mean(vs == 0)),
                float(np.mean((vs > 0) & (vs <= 0.25))),
                float(np.mean(vs > 0.25)))

    z0, m0, h0 = masses(vals)
    rng = np.random.default_rng(STAT_SEED)
    boots = {"zero": [], "middle": [], "high": []}
    for _ in range(N_BOOT):
        pick = rng.integers(n_parents, size=n_parents)
        vs = [v for i in pick for v in by_parent[parents[i]]]
        z, m, h = masses(vs)
        boots["zero"].append(z)
        boots["middle"].append(m)
        boots["high"].append(h)

    def ci(key):
        a = np.array(boots[key])
        return dict(lo95=float(np.percentile(a, 2.5)),
                    hi95=float(np.percentile(a, 97.5)),
                    ucb95_one_sided=float(np.percentile(a, 95)))

    # parent-level middle-mass distribution (heterogeneity view)
    per_parent_mid = [float(np.mean([(0 < v <= 0.25)
                                     for v in by_parent[p]]))
                      for p in parents]

    report = dict(
        LABEL="SECONDARY_NON_ADJUDICATING",
        note=("Population-generalization characterization only; the "
              "frozen D-14 verdict is untouched by this analysis."),
        n_parents=n_parents, n_sites=n,
        point=dict(zero=round(z0, 6), middle=round(m0, 6),
                   high=round(h0, 6)),
        cluster_bootstrap=dict(
            resamples=N_BOOT, seed=STAT_SEED,
            zero=ci("zero"), middle=ci("middle"), high=ci("high")),
        parent_level_middle=dict(
            mean=round(float(np.mean(per_parent_mid)), 6),
            max=round(float(np.max(per_parent_mid)), 6),
            n_parents_with_any_middle=int(
                sum(1 for x in per_parent_mid if x > 0))))
    json.dump(report, open("results/secondary_uncertainty.json", "w"),
              indent=1)
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
