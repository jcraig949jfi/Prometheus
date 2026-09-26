import json, os, collections
W = r"C:\Users\James\z80atlas_campaign_2026-09-19"
runs = [json.loads(l) for l in open(os.path.join(W, "runs.jsonl"), encoding="utf-8")]
idx = collections.defaultdict(list)
for r in runs: idx[(r["family"], r["seed"])].append(r)
d = [v for v in idx.values() if len(v) > 1]
for g in d[:4]:
    cfgs = [json.load(open(os.path.join(r["dir"], "config.json"))) for r in g]
    keys = [k for k in cfgs[0] if any(c.get(k) != cfgs[0].get(k) for c in cfgs)]
    print([r["id"] for r in g], [r["reason"] for r in g], "differing config keys:", keys,
          "init_tapes lens", [len(c["init_tapes"]) for c in cfgs], "solvers_tail", [r["summary"]["solvers_tail"] for r in g])
c = collections.Counter()
for g in d:
    cfgs = [json.load(open(os.path.join(r["dir"], "config.json"))) for r in g]
    c[tuple(k for k in cfgs[0] if k not in ("id",) and any(c2.get(k) != cfgs[0].get(k) for c2 in cfgs))] += 1
print(c)
