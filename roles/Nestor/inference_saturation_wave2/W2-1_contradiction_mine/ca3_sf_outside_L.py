"""W2-1 check H: in C-A3-INTERNALIZE, where do state-free genomes FIRST appear relative to the founder lineage L?
Classify each run's first checkpoint with any state-free competent genome by L_share there and by free_in_L, and
report the state-free share of competent genomes at that first appearance. Read-only."""
import json, pathlib, collections
R = pathlib.Path(__file__).resolve().parents[2] / "campaigns/npe-arc3-2026-09-28/c_a3_internalize/results"
cls = collections.Counter(); rows = []
for p in sorted(R.glob("*.json")):
    r = json.loads(p.read_text())
    c = next((c for c in r["checkpoints"] if c["free"] > 0), None)
    if c is None:
        cls["never_SF"] += 1; continue
    where = ("in_L" if c["free_in_L"] == c["free"] else "outside_L" if c["free_in_L"] == 0 else "mixed")
    lz = "L=0" if c["L_share"] == 0 else "L<0.5" if c["L_share"] < 0.5 else "L>=0.5"
    cls[(where, lz)] += 1
    rows.append({"run": "%s %d" % (r["cell"], r["seed"]), "epoch": c["epoch"], "d0_epoch": r["d0_epoch"], "where": where,
                 "L_share": c["L_share"], "free": c["free"], "competent": c["competent"],
                 "sf_share_first": round(c["free"] / c["competent"], 3) if c["competent"] else None,
                 "d0_free": r["d0_free"]})
for k, v in sorted(cls.items(), key=str): print(k, v)
out_L = [x for x in rows if x["where"] == "outside_L" and x["L_share"] == 0]
print("first SF outside L while L_share==0:", len(out_L), "by cell:", collections.Counter(x["run"].split()[0] for x in out_L))
print("of those, SF share >= 0.5 at first sight (competent>=10):", sum(1 for x in out_L if x["competent"] >= 10 and x["sf_share_first"] >= 0.5))
for x in sorted(out_L, key=lambda x: -(x["sf_share_first"] or 0))[:8]: print("  ", x)
pathlib.Path(__file__).with_suffix(".json").write_text(json.dumps({"classes": {str(k): v for k, v in cls.items()}, "rows": rows}, indent=1))
