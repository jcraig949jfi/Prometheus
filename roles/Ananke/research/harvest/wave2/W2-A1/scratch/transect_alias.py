import gzip, json, collections, pathlib
from canon import canon
ROOT = pathlib.Path(__file__).resolve().parents[7]
R = [json.loads(l) for l in gzip.open(ROOT/"roles/Ananke/pte/c1_rows/cells.jsonl.gz","rt")]
g = collections.defaultdict(lambda: collections.defaultdict(set))
for r in R:
    e = r.get("extra") or {}
    if r["wave"] in ("B","B2") and "transect" in e:
        key = (r["wave"], e["track"], r["env"]["family"], e["transect"], e["base"])
        g[key][e["level_index"]].add(canon(r["physics"], r["env"]))
inert, partial = [], []
for key, lv in sorted(g.items()):
    cs = [next(iter(s)) for i, s in sorted(lv.items())]
    groups = collections.defaultdict(list)
    for i, c in zip(sorted(lv), cs): groups[c].append(i)
    if len(groups) == 1: inert.append(key)
    elif len(groups) < len(cs): partial.append((key, [v for v in groups.values() if len(v) > 1]))
print("transect groups:", len(g), " fully inert:", len(inert), " partially aliased:", len(partial))
for k in inert: print("  INERT", k)
for k, v in partial: print("  PARTIAL", k, "identical level sets:", v)
# which boundary candidates sit on an aliased pair?
B = json.load(open(ROOT/"roles/Ananke/pte/c1_rows/boundaries_verdicts.json"))
for c in B:
    key = ("B", c["track"], c["family"], c["dial"], c["base"])
    lv = g.get(key)
    if not lv: continue
    a, b = c["between"]
    if lv[a] == lv[b]:
        print("BOUNDARY ON IDENTICAL PHYSICS:", c["family"], c["dial"], c["track"], c["base"], c["metric"], c["between"], c["label"])
