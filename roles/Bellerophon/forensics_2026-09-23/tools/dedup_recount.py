"""Erratum E2 recount (2026-09-29): pseudo-replication in the grounding round's spontaneous-origin set.

Found by Artemis S3 (comms #1005; Fabric tsk-2b96eda5e96c): grounding.py sets seed = SEED_BASE + lane*1e9 + k with no
cell term, so task / reproduction / representation cells of one lane reuse the same seeds. Pooled G1 + G1T + G7-RANDOM
origins therefore include runs that start from the same initial world.

This recount (read-only over the preserved results) reports:
- distinct seeds among the 160 origins;
- EXACT duplicates: identical (seed, first-SR tape, first-SR tick) -- the same event counted more than once;
- G2 (sustained, depth >= 3 and alive at the end; grounding_analysis.sustained) and G6 (copy-born, as in
  g6_recount.py) on all origins, on unique events, and on one origin per seed.
    python dedup_recount.py C:/Users/James/z80atlas_grounding_2026-09-23/results.jsonl
"""
import collections
import json
import sys

R = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
spont = [r for r in R if r.get("spontaneous") and (r["lane"] in ("G1", "G1T") or (r["lane"] == "G7" and r["cell"].startswith("RANDOM/")))]


def key(r):
    f = r.get("first_self_replication") or {}
    return (r["seed"], f.get("tape"), f.get("tick"))


def sustained(r, d=3):
    s = r["summary"]
    return (s.get("sr_max_depth") or 0) >= d and (s.get("sr_alive_end") or 0) >= 1


def copy_born(r):
    g = (r.get("first_self_replication") or {}).get("genealogy") or []
    return bool(g) and g[0].get("mechanism") is not None


def per_seed(S):
    out = {}
    for r in sorted(S, key=lambda r: r["id"]):          # deterministic: lowest run id per seed
        out.setdefault(r["seed"], r)
    return list(out.values())


uniq = list({key(r): r for r in sorted(spont, key=lambda r: r["id"])}.values())
sets = {"all_origins": spont, "unique_events": uniq, "one_per_seed": per_seed(spont)}
res = {"origins": len(spont), "distinct_seeds": len({r["seed"] for r in spont}),
       "exact_duplicates": len(spont) - len(uniq),
       "by_set": {n: {"n": len(S), "G2_sustained_d3": sum(sustained(r) for r in S), "G6_copy_born": sum(copy_born(r) for r in S)}
                  for n, S in sets.items()},
       "lanes": dict(collections.Counter(r["lane"] for r in spont))}
print(json.dumps(res, indent=1))
