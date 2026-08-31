"""POST-HOC DIAGNOSTIC (does not change any gate or verdict).

The preregistered G6 statistic aggregates over all mutation radii.  At composed
radii the substrate-generic syntactic taxonomy degenerates towards its
catch-all bucket, so the aggregated statistic conflates *mutation-operator
family bias* with *composition depth*.  This script reports the radius-1
decomposition, which is the honest measure of operator bias, and the
atomic-operator -> family confusion table asked for by the mutation-bias audit.

The preregistered verdict stands as computed by analysis/verdict.py.  This file
exists to expose a defect in that instrument, not to repair a result.
"""
import collections
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from substrates import common, registry            # noqa: E402
from probes import battery                          # noqa: E402
from mutation import mutators                       # noqa: E402
from classifiers import families                    # noqa: E402

G = json.load(open(os.path.join(ROOT, "prereg", "gates.json")))
C = G["constants"]
N_DIAG = 4000


def rows_r1(b):
    fam = collections.Counter()
    for line in open(os.path.join(ROOT, "ledgers", "census_rows_%s.jsonl" % b)):
        r = json.loads(line)
        if r["order"] != 0 or r["r"] != 1:
            continue
        if r["valid"] and not r.get("identity", 0):
            fam[r["family"]] += 1
    return fam


def confusion(b):
    registry.set_order(b, 0)
    sub = registry.get(b)
    rng = random.Random(C["SEED_RNG"])
    seeds = []
    tries = 0
    while len(seeds) < C["N_SEEDS"] and tries < C["SEED_TRIES"]:
        tries += 1
        p = sub.random_program(rng, rng.randrange(4, 16))
        if sub.is_valid(p) and common.sem_profile(sub, p, battery.VALUE_PROBES)["live"]:
            if p not in seeds:
                seeds.append(p)
    donors = mutators.make_donors(sub)
    r2 = random.Random(4242424)
    conf = collections.defaultdict(collections.Counter)
    for _ in range(N_DIAG):
        s = seeds[r2.randrange(len(seeds))]
        cand, kinds = mutators.mutate(b, sub, s, r2, 1, donors)
        k = kinds[0] if kinds else "NONE"
        conf[k][families.classify(s, cand)] += 1
    return {k: dict(v) for k, v in conf.items()}


def main():
    out = {}
    for b in G["bases"]:
        fam = rows_r1(b)
        tot = max(1, sum(fam.values()))
        shares, mx, n5 = families.charged_shares(fam)
        out[b] = {"r1_family_counts": dict(fam),
                  "r1_family_shares_charged": shares,
                  "r1_max_family_share_charged": mx,
                  "r1_n_families_ge_5pct": n5,
                  "r1_n": tot,
                  "r1_would_pass_G6": bool(mx <= 0.60 and n5 >= 4),
                  "operator_to_family": confusion(b)}
    json.dump(out, open(os.path.join(ROOT, "results", "mutation_bias_r1.json"), "w"),
              indent=1)
    for b in out:
        print(b, "max=%.3f n5=%d would_pass_G6=%s" %
              (out[b]["r1_max_family_share_charged"], out[b]["r1_n_families_ge_5pct"],
               out[b]["r1_would_pass_G6"]))


if __name__ == "__main__":
    main()
