"""ELEN-03: stratified sample of the 187 unreviewed shadow-loop passes.

Doctrine: enumerate the inventory first, never read a prefix. Stratify, draw
with a recorded seed, report the eligible count beside the draw.
"""
import json
import random
import collections
import pathlib

root = pathlib.Path("F:/Prometheus-worktrees/elenchus-baserole")
wl = [json.loads(l) for l in (root / "engine/shadow/WORKLOG.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
rv = [json.loads(l) for l in (root / "engine/shadow/REVIEWS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
done = {r.get("pass_id") for r in rv}

print("=== INVENTORY (enumerated, not sampled) ===")
print("worklog entries:", len(wl), " reviewed:", len(done & {w['pass_id'] for w in wl}), " unreviewed:", len([w for w in wl if w['pass_id'] not in done]))

un = [w for w in wl if w["pass_id"] not in done]
by_day = collections.Counter(w["pass_id"][:10] for w in un)
print("\nunreviewed by day (the strata):")
for d, n in sorted(by_day.items()):
    print(f"  {d}  {n:3d}")

print("\n=== FIELD POPULATION ACROSS ALL 187 (what is actually in them) ===")
keys = collections.Counter()
empty = collections.Counter()
for w in un:
    for k, v in w.items():
        keys[k] += 1
        if v in (None, "", [], {}):
            empty[k] += 1
for k, n in keys.most_common():
    print(f"  {k:<28} present {n:3d}/187   empty {empty[k]:3d}")

print("\n=== CLAIM AND EVIDENCE DENSITY ===")
nclaims = [len(w.get("claims") or []) for w in un]
nev = [len(w.get("evidence") or []) for w in un]
ncit = [len(w.get("citations") or []) for w in un]
nfetch = [len(w.get("external_links_fetched") or []) for w in un]
nweak = [len(w.get("self_identified_weaknesses") or []) for w in un]
def stat(name, xs):
    print(f"  {name:<34} total {sum(xs):5d}  zero-in {sum(1 for x in xs if x==0):3d}/187")
stat("claims", nclaims); stat("evidence", nev); stat("citations", ncit)
stat("external_links_fetched", nfetch); stat("self_identified_weaknesses", nweak)

print("\n=== STRATIFIED DRAW (seed 20260911, 2 per day-stratum where available) ===")
rng = random.Random(20260911)
draw = []
bucket = collections.defaultdict(list)
for w in un:
    bucket[w["pass_id"][:10]].append(w)
for d in sorted(bucket):
    draw.extend(rng.sample(bucket[d], min(2, len(bucket[d]))))
print("drawn:", len(draw), "of", len(un))
for w in draw:
    claims = w.get("claims") or []
    top = ""
    if claims:
        c = claims[0]
        top = c if isinstance(c, str) else (c.get("claim") or c.get("text") or str(c))
    print(f"\n  {w['pass_id']}")
    print(f"    intent : {str(w.get('intent'))[:150]}")
    print(f"    claim0 : {str(top)[:190]}")
    print(f"    claims {len(claims)} evidence {len(w.get('evidence') or [])} cites {len(w.get('citations') or [])} weaknesses {len(w.get('self_identified_weaknesses') or [])}")
