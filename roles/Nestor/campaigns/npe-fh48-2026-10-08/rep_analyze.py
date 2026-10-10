"""X-REPUTATION reducer: paired (seed) causal depth RESET vs INHERIT, final CS / TCS, exchange ratio.
Declared rule: SIGNAL if INHERIT median depth >= 1.5x RESET median AND INHERIT > RESET in >= 9/12 paired seeds."""
import json, pathlib, statistics as S, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
d = HERE / "runs" / "X-REPUTATION"
rows = [json.loads(p.read_text()) for p in sorted(d.glob("*.json")) if not p.name.startswith(("RECEIPT", "REP_"))]
by = {}
for r in rows:
    by.setdefault(r["arm"], {})[r["seed"]] = r
seeds = sorted(set(by.get("RESET", {})) & set(by.get("INHERIT", {})))
dr = [by["RESET"][s]["depth"] for s in seeds]
di = [by["INHERIT"][s]["depth"] for s in seeds]
wins = sum(i > r for i, r in zip(di, dr))
med_r, med_i = S.median(dr), S.median(di)
cls = ("SIGNAL" if med_i >= 1.5 * med_r and wins >= 9 else
       "CLEAN_NULL" if med_i < 1.5 * med_r and wins < 9 else "WEAK_SIGNAL")


def ex(r):
    l = r["ledger"]
    return round(l.get("GAIN_COPY", 0) / max(1, l.get("LOST_OVERWRITE", 0)), 2)


out = {"classification": cls, "paired_seeds": len(seeds), "depth_RESET": dr, "depth_INHERIT": di,
       "median_depth": {"RESET": med_r, "INHERIT": med_i}, "INHERIT_deeper_pairs": wins,
       "final_CS": {a: [round(by[a][s]["CS"], 3) for s in seeds] for a in ("RESET", "INHERIT")},
       "final_TCS": {a: [by[a][s].get("TCS") for s in seeds] for a in ("RESET", "INHERIT")},
       "maintained_TCS_ge_0.10": {a: sum((by[a][s].get("TCS") or 0) >= 0.10 for s in seeds if by[a][s]["depth"] >= 20)
                                  for a in ("RESET", "INHERIT")},
       "exchange_ratio_median": {a: S.median([ex(by[a][s]) for s in seeds]) for a in ("RESET", "INHERIT")}}
(d / "REP_REDUCED.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
