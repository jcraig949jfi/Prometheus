"""S18 / #11 -- DOES FOSSIL-DIRECTED EXPERIMENT SELECTION BEAT UNINFORMED
SELECTION UNDER THE SAME BUDGET?

Harmonia science loop 18, 2026-09-05.

Not an archaeology experiment. S15 closed that direction: selection performed
upstream of submission is information-theoretically absent, and no policy here
attempts to recover it. The question is operational.

    Given a fixed budget of experiments, does choosing the NEXT experiment from
    fossil-derived prospective information discover more claim failures than
    choosing without it?

EPISTEMIC BOUNDARY, enforced in the code and not merely stated: every policy
below reads ONLY features of SUBMITTED fossils -- observations, their world
grouping, n. No policy reasons about absence. The absence of a selection fossil
is never treated as evidence that selection did not occur.

WHAT POLICY C IS ALLOWED TO USE. S17 established WITHIN-DIMENSION ranking
(out-of-sample AUC 0.75-0.90 on four of five dimensions, replicated on three
populations) and FAILED at cross-dimension ranking (top-1 0.080, worse than
random, withdrawn). So policy C ranks claims within each dimension using the
frozen rules and ROUND-ROBINS across dimensions. That requires no comparison of
incomparable score scales and repairs nothing on this population.

Where S17 has no rule -- the noise dimension, which produced zero fragile cases
on its development population -- policy C falls back to random within that
dimension. It has no information there and does not pretend to.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0] if "/" in __file__ else ".")
import s17_prospective_fragility as S17                            # noqa: E402

# ==========================================================================
# PRE-REGISTRATION -- frozen before any evaluation outcome is revealed
# ==========================================================================
MANIFEST = {
    "experiment": "S18 / #11",
    "question": "does fossil-directed experiment selection discover claim "
                "failures more efficiently than uninformed selection under an "
                "identical budget?",
    "candidate_universe": "every (claim, perturbation dimension) pair; "
                          "dimensions are exactly S17's five, unchanged",
    "n_claims_per_population": 200,
    "budget_experiments": 100,
    "exhaustive_size": 1000,
    "budget_fraction_of_exhaustive": 0.10,
    "primary_endpoint": "failures discovered per experiment executed "
                        "(fragile pairs found / budget spent)",
    "secondary_endpoint": "fraction of the oracle ceiling attained",
    "stopping_rule": "spend the whole budget; no early stop, no interim look "
                     "that could change a policy",
    "policies": {
        "A_random": "uniform over unexecuted pairs",
        "B_simple_fossil": "rank all pairs by the claim's CI width, the "
                           "uncertainty proxy already present in any record. "
                           "This is the strongest SIMPLE fossil baseline S17 "
                           "measured.",
        "C_frozen_S17": "within each dimension, rank claims by that "
                        "dimension's frozen S17 rule; round-robin across "
                        "dimensions. No cross-dimension score is formed.",
        "D_oracle": "evaluated only afterwards; establishes the ceiling",
    },
    "prohibited": "any calibration, threshold or feature fitted on this "
                  "population; any repair of S17's withdrawn cross-dimension "
                  "ranking; any inference from the ABSENCE of a fossil",
}
MH = hashlib.sha256(json.dumps(MANIFEST, sort_keys=True).encode()).hexdigest()


# ==========================================================================
def build(pop_seed, n_claims):
    """A fresh claim population. Same generator family as S17, new seeds."""
    rng = random.Random(pop_seed)
    pop = []
    per = max(1, n_claims // len(S17.KINDS))
    for k in S17.KINDS:
        for _ in range(per):
            pop.append(S17.make_claim(
                k, rng, nw=rng.choice([16, 24, 40]),
                nobs=rng.choice([8, 12, 20]),
                effect=rng.choice([0.0, 0.2, 0.4, 0.6, 0.9])))
    return pop[:n_claims]


def truth_table(pop, seed):
    """(claim index, dimension) -> fragile. Revealed only to the scorer."""
    outs = S17.outcomes(pop, seed=seed)
    return {(i, d): outs[i][d] for i in range(len(pop)) for d in S17.DIMS}


def run_policy(name, order, truth, budget):
    """Execute the first `budget` pairs in the policy's order."""
    found = 0
    executed = []
    for pair in order[:budget]:
        executed.append(pair)
        if truth[pair]:
            found += 1
    return {"policy": name, "executed": len(executed), "found": found,
            "rate": found / len(executed) if executed else float("nan")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--populations", type=int, default=5)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    rules = json.load(open("ledgers/s17_fragility.json"))["predictor"]["rules"]
    print("=" * 78)
    print("S18 / #11  FOSSIL-DIRECTED EXPERIMENT SELECTION")
    print("=" * 78)
    print("  frozen manifest      sha256:%s" % MH[:32])
    print("  frozen S17 predictor sha256:%s"
          % json.load(open("ledgers/s17_fragility.json"))["predictor_hash"][:32])
    print("  budget %d of %d exhaustive (%.0f%%), endpoint: failures per "
          "experiment\n" % (MANIFEST["budget_experiments"],
                            MANIFEST["exhaustive_size"],
                            100 * MANIFEST["budget_fraction_of_exhaustive"]))
    for d in S17.DIMS:
        r = rules[d]
        print("     %-10s rule: %s" % (
            d, ("%s, %s" % (r["feature"], "higher=fragile"
                            if r["higher_is_fragile"] else "lower=fragile"))
            if r["feature"] else "NO RULE -- policy C falls back to random"))

    N, B = MANIFEST["n_claims_per_population"], MANIFEST["budget_experiments"]
    rows = []
    for p in range(a.populations):
        pop = build(20000 + p * 977, N)
        feats = [S17.features(c) for c in pop]
        universe = [(i, d) for i in range(len(pop)) for d in S17.DIMS]

        # ---- orders are fixed BEFORE outcomes are revealed --------------
        rng = random.Random(9000 + p)
        order_A = universe[:]
        rng.shuffle(order_A)

        order_B = sorted(universe, key=lambda t: -feats[t[0]]["ci_width"])

        per_dim = {}
        for d in S17.DIMS:
            r = rules[d]
            if r["feature"]:
                per_dim[d] = sorted(
                    range(len(pop)),
                    key=lambda i: -(feats[i][r["feature"]]
                                    if r["higher_is_fragile"]
                                    else -feats[i][r["feature"]]))
            else:
                idx = list(range(len(pop)))
                random.Random(500 + p).shuffle(idx)
                per_dim[d] = idx
        order_C, cursor = [], {d: 0 for d in S17.DIMS}
        while len(order_C) < len(universe):
            for d in S17.DIMS:
                if cursor[d] < len(per_dim[d]):
                    order_C.append((per_dim[d][cursor[d]], d))
                    cursor[d] += 1

        # ---- outcomes revealed ONLY now ---------------------------------
        truth = truth_table(pop, seed=30000 + p * 131)
        total_fragile = sum(1 for k in universe if truth[k])
        ceiling = min(B, total_fragile) / B

        res = [run_policy("A_random", order_A, truth, B),
               run_policy("B_ci_width", order_B, truth, B),
               run_policy("C_frozen_S17", order_C, truth, B)]
        res.append({"policy": "D_oracle", "executed": B,
                    "found": min(B, total_fragile), "rate": ceiling})
        for r in res:
            r["population"] = p
            r["base_rate"] = total_fragile / len(universe)
        rows += res
        print("\n  population %d: %d of %d pairs fragile (base rate %.3f)"
              % (p, total_fragile, len(universe), total_fragile / len(universe)))
        for r in res:
            print("     %-14s found %3d/%d  rate %.3f%s"
                  % (r["policy"], r["found"], B, r["rate"],
                     "   <- ceiling" if r["policy"] == "D_oracle" else ""))

    print("\n" + "=" * 78)
    print("RESULT ACROSS %d POPULATIONS" % a.populations)
    print("=" * 78)
    summary = {}
    for pol in ("A_random", "B_ci_width", "C_frozen_S17", "D_oracle"):
        rs = [r["rate"] for r in rows if r["policy"] == pol]
        summary[pol] = {"mean_rate": statistics.fmean(rs),
                        "sd": statistics.pstdev(rs) if len(rs) > 1 else 0.0,
                        "rates": rs}
        print("  %-14s mean failures/experiment %.3f  (sd %.3f)"
              % (pol, summary[pol]["mean_rate"], summary[pol]["sd"]))
    a_m = summary["A_random"]["mean_rate"]
    b_m = summary["B_ci_width"]["mean_rate"]
    c_m = summary["C_frozen_S17"]["mean_rate"]
    d_m = summary["D_oracle"]["mean_rate"]
    print("\n  lift of C over random     : %+.1f%%"
          % (100 * (c_m - a_m) / a_m if a_m else float("nan")))
    print("  lift of C over ci_width   : %+.1f%%"
          % (100 * (c_m - b_m) / b_m if b_m else float("nan")))
    print("  C as a fraction of oracle : %.3f" % (c_m / d_m if d_m else 0))
    print("  A as a fraction of oracle : %.3f" % (a_m / d_m if d_m else 0))
    wins = sum(1 for p in range(a.populations)
               if [r for r in rows if r["policy"] == "C_frozen_S17"
                   and r["population"] == p][0]["rate"] >
               [r for r in rows if r["policy"] == "A_random"
                and r["population"] == p][0]["rate"])
    print("  populations where C beat A: %d of %d" % (wins, a.populations))
    verdict = ("FOSSIL-DIRECTED SELECTION BEATS UNINFORMED"
               if c_m > a_m and c_m > b_m and wins == a.populations
               else "NO RELIABLE ADVANTAGE DEMONSTRATED")
    print("\n  VERDICT: %s" % verdict)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"manifest": MANIFEST, "manifest_hash": MH,
                   "rows": rows, "summary": summary, "verdict": verdict,
                   "populations_C_beat_A": wins}, f, indent=1)
    print("\nrows: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
