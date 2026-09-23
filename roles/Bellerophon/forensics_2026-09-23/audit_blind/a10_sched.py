import json, os, sys, collections
sys.path.insert(0, r"D:\Prometheus-worktrees\bellerophon-post-campaign-forensics")
from prometheus.z80atlas import grammar as G, controls as C
W = r"C:\Users\James\z80atlas_campaign_2026-09-19"
runs = [json.loads(l) for l in open(os.path.join(W, "runs.jsonl"), encoding="utf-8")]
byid = {r["id"]: r for r in runs}
# 1. duplicate (family, seed, init_tapes-less) submissions
dup = collections.Counter((r["family"], r["seed"]) for r in runs)
d = [k for k, v in dup.items() if v > 1]
kinds = collections.Counter(tuple(sorted(x["kind"] for x in runs if (x["family"], x["seed"]) == k)) for k in d[:2000])
print("(family, seed) pairs submitted more than once:", len(d), "extra runs:", sum(dup[k] - 1 for k in d))
print("  kinds of the duplicated submissions (first 2000):", kinds.most_common(8))
# are duplicated runs byte-identical in outcome? (a replicate that is not a replicate)
same = diff = 0
idx = collections.defaultdict(list)
for r in runs: idx[(r["family"], r["seed"])].append(r)
for k in d:
    rs = [x for x in idx[k] if x["kind"] != "intervention"]
    if len(rs) >= 2:
        if all(json.dumps(x["summary"], sort_keys=True) == json.dumps(rs[0]["summary"], sort_keys=True) for x in rs): same += 1
        else: diff += 1
print("  duplicated non-intervention groups with IDENTICAL summaries:", same, "; differing:", diff)
# 2. late verification matched controls: seed should equal the family's own fresh-seed run
ver = [r for r in runs if r["kind"] == "verification"]
fresh = collections.defaultdict(set)
for r in ver:
    if "fresh seed" in (r["reason"] or ""): fresh[r["parents"][0]].add(r["seed"])
ok = bad = 0
for r in ver:
    if "matched control" in (r["reason"] or ""):
        if r["seed"] in fresh[r["parents"][0]]: ok += 1
        else: bad += 1
print("late matched controls seeded with THEIR family's fresh seed:", ok, "; seeded with ANOTHER family's seed (specs[0] bug):", bad)
# 3. positive controls that share a family id
ids = [(c["name"], G.vec_id(c["vec"])) for c in C.CONTROL_VECS]
print("positive-control family ids:", ids)
# 4. runs of positive-control families other than the positive controls
pcf = {i for _, i in ids}
print("non-positive-control runs landing in positive-control families:", sum(1 for r in runs if r["family"] in pcf and r["kind"] != "positive_control"))
# 5. intervention runs (init_tapes) share family ids with ordinary runs; how many flagged families contain them
flags = json.load(open(os.path.join(W, "flags.json")))
byf = collections.defaultdict(list)
for r in runs: byf[r["family"]].append(r)
for name in ("REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL", "REACHED_INCREMENTAL_NOT_ATOMIC", "RESERVOIR_CROSSED_MOAT"):
    fl = [f for f in flags if f["flag"] == name]
    def solved(r): return (r["summary"].get("solvers_tail") or 0) >= 1
    only_by_intervention = sum(1 for f in fl if all(r["kind"] == "intervention" for r in byf[f["family"]] if solved(r)))
    ctrl_has_intervention = sum(1 for f in fl if any(r["kind"] == "intervention" for r in byf[f["control_family"]]))
    # would the flag survive if intervention runs were excluded from BOTH arms?
    surv = 0
    for f in fl:
        a = [r for r in byf[f["family"]] if r["kind"] != "intervention"]; b = [r for r in byf[f["control_family"]] if r["kind"] != "intervention"]
        surv += bool(a) and bool(b) and any(map(solved, a)) and not any(map(solved, b))
    print(name, len(fl), "| treatment solved ONLY by intervention (transplant) runs:", only_by_intervention, "| control contains intervention runs:", ctrl_has_intervention, "| survive excluding interventions:", surv)
# 6. seeded inits among flags
for name in ("REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL", "REACHED_INCREMENTAL_NOT_ATOMIC", "RESERVOIR_CROSSED_MOAT"):
    fl = [f for f in flags if f["flag"] == name]
    print(name, "init of treatment:", collections.Counter(byf[f["family"]][0]["vec"]["init"] for f in fl))
