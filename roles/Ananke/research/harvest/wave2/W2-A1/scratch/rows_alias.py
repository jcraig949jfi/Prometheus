import gzip, json, collections, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[7]
R = [json.loads(l) for l in gzip.open(ROOT/"roles/Ananke/pte/c1_rows/cells.jsonl.gz","rt")]
print("rows", len(R))
# 1. levels vs physics mismatch, every dial
mm = collections.Counter(); ex = {}
for r in R:
    lv, ph = r["levels"], r["physics"]
    for k, v in lv.items():
        if k == "economy": continue
        if k in ph and ph[k] != v:
            mm[(k, json.dumps(v), json.dumps(ph[k]), r["wave"])] += 1
print("levels!=physics:", mm.most_common())
# 2. topology transects at dest_mode=all base: global level switches dest_mode + activates fanout
c = collections.Counter()
for r in R:
    e = r.get("extra") or {}
    if r["wave"] in ("B","B2") and e.get("transect") == "topology":
        c[(r["wave"], r["env"]["family"], e.get("track"), e["base"], r["levels"]["dest_mode"], r["physics"]["topology"], r["physics"]["dest_mode"], r["physics"]["fanout"])] += 1
for k, v in sorted(c.items()): print("topo-transect", k, v)
# 3. transects whose dial is dest_mode at a global base, or fanout at all-base, etc
c2 = collections.Counter()
for r in R:
    e = r.get("extra") or {}
    if r["wave"] in ("B","B2") and "transect" in e:
        c2[(r["wave"], e["track"], r["env"]["family"], e["transect"], e["base"])] += 1
print("n transect groups", len(c2))
# check physics distinctness per transect group: count distinct physics dicts among levels
g = collections.defaultdict(lambda: collections.defaultdict(set))
for r in R:
    e = r.get("extra") or {}
    if r["wave"] in ("B","B2") and "transect" in e:
        key = (r["wave"], e["track"], r["env"]["family"], e["transect"], e["base"])
        g[key][e["level_index"]].add(json.dumps([r["physics"], r["env"]], sort_keys=True))
for key, lv in sorted(g.items()):
    phs = [next(iter(s)) for i, s in sorted(lv.items())]
    if len(set(phs)) < len(phs):
        print("ALIASED LEVELS (identical physics+env at different level_index):", key, "levels", len(phs), "distinct", len(set(phs)))
