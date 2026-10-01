"""W2-AL: classify out_rows.jsonl rows and print the per-family table (no compute)."""
import json, pathlib, collections, math
HERE = pathlib.Path(__file__).resolve().parent
R = [json.loads(l) for l in (HERE / "out_rows.jsonl").read_text().splitlines() if l.strip()]
seen = {}
for r in R:
    seen[r["cell_id"]] = r          # last wins (duplicates none expected)
R = list(seen.values())


def cls(r):
    if r["late_lo99"] > 0.55:
        return "PER-TRIAL"
    if r["latch"]["fit"] >= 0.95 and abs(r["late_acc"] - 0.5) <= 0.03:
        return "LATCH"
    return "MIXED/OTHER"


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"),) * 2
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


out = {"rows": []}
by = collections.defaultdict(collections.Counter)
for r in sorted(R, key=lambda r: (r["family"], -r["held_acc"])):
    c = cls(r)
    by[r["family"]][c] += 1
    bh0 = r["twin"].get("0", {}).get("beyond_hop")
    bh2 = r["twin_recorded"]["beyond_hop"]
    rb_rec = bh2 >= 0.5
    rb_max = max(bh2, bh0 if bh0 is not None else -1) >= 0.5
    r["_cls"] = c; r["_flip"] = (rb_max != rb_rec)
    out["rows"].append({"cell": r["cell_id"], "fam": r["family"], "wave": r["wave"], "topo": r["topology"],
                        "rad": r["radius"], "d": r["env_d"], "held": round(r["held_acc"], 3),
                        "gate": r["gate_exact"], "late": round(r["late_acc"], 3), "late_lo99": round(r["late_lo99"], 3),
                        "fit": round(r["latch"]["fit"], 3), "cue": r["latch"]["cue"], "bh0": bh0, "bh2": bh2,
                        "cls": c, "flip": r["_flip"],
                        "acc_by_trial": r["acc_by_trial"]})
for x in out["rows"]:
    print(f"{x['fam']:5s} {x['cell']} {x['wave']:2s} {x['topo'][:5]:5s} r{x['rad']} d{x['d']} held {x['held']:.3f} gate {int(x['gate'])} "
          f"late {x['late']:.3f} lo {x['late_lo99']:.3f} fit {x['fit']:.3f} bh0 {x['bh0']} bh2 {x['bh2']:.3f} {x['cls']:11s} flip={int(x['flip'])} "
          + " ".join(f"{a:.2f}" for a in x['acc_by_trial']))
print()
for f, c in sorted(by.items()):
    print(f, dict(c), "n=", sum(c.values()))
# A1 = wave A
for fam, denom in (("RELAY", 71), ("MAJ", 70), ("HOLD", 70)):
    a = [r for r in R if r["family"] == fam and r["wave"] == "A"]
    k = sum(r["_cls"] == "PER-TRIAL" for r in a)
    print(f"A1 {fam}: SIGNAL rows covered {len(a)}; PER-TRIAL {k}/{denom} = {k/denom:.3f} Wilson95 {tuple(round(v,3) for v in wilson(k, denom))};"
          f" classes {collections.Counter(r['_cls'] for r in a)}")
fl = [r for r in R if r["_flip"]]
print("REACH_BEYOND_HOP flips under max(trial0, trial2):", collections.Counter((r["family"], r["_cls"]) for r in fl), "of",
      collections.Counter(r["family"] for r in R if r["twin"].get("0")))
print("gate exact:", sum(r["gate_exact"] for r in R), "/", len(R),
      "; twin2 exact:", [r["twin2_repro_exact"] for r in R if r["twin2_repro_exact"] is not None])
print("cpu_s total:", round(sum(r["cpu_s"] for r in R), 1))
(HERE / "out_summary.json").write_text(json.dumps(out, indent=1))
