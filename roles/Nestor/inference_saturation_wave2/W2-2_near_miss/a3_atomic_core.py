"""W2-2 a3: depth vs copy volume under ATOMIC (C-ATOMIC, all specimens) and the C-CORE near-misses. Read-only.
python -B a3_atomic_core.py -> a3_atomic_core.json
"""
import json, glob, pathlib, math, statistics as st
HERE = pathlib.Path(__file__).resolve().parent
C = HERE.parents[1] / "campaigns" / "c9x-explore-2026-09-24"
out = {}
A = [json.load(open(f)) for f in glob.glob(str(C / "c_atomic" / "results" / "*.json"))]
sp = {}
for r in A:
    sp.setdefault((r["specimen"][:4], r["arm"]), []).append((r["p11_events"], r["depth"]))
out["per_specimen"] = {f"{k[0]}_{k[1]}": sorted(v) for k, v in sorted(sp.items()) if any(e > 0 for e, _ in v)}
# depth per log(events): a chain-vs-star index. For a random recursive tree of n nodes depth ~ e*ln n.
def idx(e, d):
    return round(d / (math.e * math.log(e)), 3) if e >= 3 else None
out["chain_index"] = {k: [idx(e, d) for e, d in v if e >= 20] for k, v in out["per_specimen"].items()}
# 7ae3 ATOMIC: events vs depth relationship around the gap
a7 = sorted(sp.get(("7ae3", "ATOMIC"), []))
out["7ae3_atomic_events_ge100_depth_lt20"] = [x for x in a7 if x[0] >= 100 and x[1] < 20]
out["7ae3_atomic_depth_hist"] = {b: sum(lo <= d < hi for _, d in a7) for b, (lo, hi) in
                                 {"0": (0, 1), "1-4": (1, 5), "5-19": (5, 20), "20-99": (20, 100), "100+": (100, 10**9)}.items()}
# C-CORE
cc = json.load(open(C / "c_core" / "RESULTS.json"))
runs = cc if isinstance(cc, list) else cc.get("runs", cc)
R = [json.load(open(f)) for f in glob.glob(str(C / "c_core" / "results" / "*.json"))]
core = (23, 24, 52, 53)
rows = []
for r in R:
    fr = r["freq"]
    rows.append(dict(seed=r["seed"], depth=r["depth"], anc0=r["anc0_share"], alive=r["alive"],
                     core_mean=round(sum(fr[i] for i in core) / 4, 3), noncore_max=round(max(fr[i] for i in range(64) if i not in core), 3),
                     n_pos_gt0=sum(x > 0 for x in fr)))
rows.sort(key=lambda x: x["depth"])
out["c_core_depth_hist"] = sorted(r["depth"] for r in rows)
out["c_core_nonrunaway_ge3"] = [r for r in rows if 3 <= r["depth"] < 20]
out["c_core_nonrunaway_summary"] = dict(n=sum(r["depth"] < 20 for r in rows), anc0_max=max(r["anc0"] for r in rows if r["depth"] < 20),
                                        core_mean_max=max(r["core_mean"] for r in rows if r["depth"] < 20))
out["c_core_runaway_anc0_min"] = min(r["anc0"] for r in rows if r["depth"] >= 20)
json.dump(out, open(HERE / "a3_atomic_core.json", "w"), indent=1)
for k, v in out["per_specimen"].items():
    print(k, len(v), v[-12:])
print("chain_index", {k: v for k, v in out["chain_index"].items() if v})
print(out["7ae3_atomic_depth_hist"], out["7ae3_atomic_events_ge100_depth_lt20"])
print(out["c_core_depth_hist"]); print(out["c_core_nonrunaway_ge3"]); print(out["c_core_nonrunaway_summary"], out["c_core_runaway_anc0_min"])
