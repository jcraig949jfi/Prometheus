"""W2-14 a1: summary of ladder.jsonl against the observed world (arithmetic only, no VM).
Observed: X-TICKET (BASE, 128 world runs, traj to 300, world depth at 2000), C-ATOMIC C1 + X-ATOMIC (7ae3 depth at 2000).
python -B a1_summary.py -> a1_summary.json"""
import glob, json, math
from collections import defaultdict
import ffield as F

def wilson(k, n, z=1.96):
    if not n: return None
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]

def bins(v):
    n = len(v)
    return {"0": sum(x == 0 for x in v), "1-4": sum(1 <= x <= 4 for x in v), "5-26": sum(5 <= x <= 26 for x in v),
            "27-162": sum(27 <= x <= 162 for x in v), ">=163": sum(x >= 163 for x in v), "n": n}

def rates(rows, dkey="depth_f"):
    n = len(rows)
    out = {}
    for name, f in (("depth20", lambda x: x[dkey] >= 20), ("B163", lambda x: x["B"] >= 163), ("maxA40", lambda x: x["maxA"] >= 40),
                    ("any_runaway", lambda x: x[dkey] >= 20 or x["B"] >= 163 or x["maxA"] >= 40 or x.get("stop") == "free_cap256")):
        k = sum(1 for x in rows if f(x)); out[name] = {"k": k, "n": n, "p": round(k / n, 3), "ci95": wilson(k, n)}
    out["B_bins"] = bins([x["B"] for x in rows]); out["Ball_bins"] = bins([x["Ball"] for x in rows])
    return out

d = defaultdict(list)
for l in open(F.HERE / "ladder.jsonl"):
    x = json.loads(l); d["|".join(map(str, (x["rule"], x["struct"], x["partner"], x["ctx"], "MUT" if x["mut"] else "NOMUT")))].append(x)
res = {"configs": {}, "cpu_s_workers": round(sum(x["cpu_s"] for v in d.values() for x in v), 1)}
for k, v in sorted(d.items()):
    r = rates(v); r["stops"] = {s: sum(x["stop"] == s for x in v) for s in sorted({x["stop"] for x in v})}
    r["cpu_s"] = round(sum(x["cpu_s"] for x in v), 1); res["configs"][k] = r

TK = [json.load(open(p)) for p in sorted(glob.glob(str(F.CAMP / "c9x-explore-2026-09-24" / "x_ticket" / "results" / "*.json")))]
obs = [{"s": t["s"], "depth_f": t["depth"], "B": t["traj"][-1][2] if t["traj"] else 0, "Ball": -1,
        "maxA": max([a for _, a, _ in t["traj"]] or [1])} for t in TK]
res["observed"] = {"XTICKET_BASE_all128_world_depth2000": rates(obs),
                   "XTICKET_BASE_seeds0_39": rates([o for o in obs if o["s"] < 40])}
ca = json.load(open(F.CAMP / "c9x-explore-2026-09-24" / "c_atomic" / "RESULTS.json"))
p = [x for x in ca if x["specimen"].startswith("7ae3")]
res["observed"]["C_ATOMIC_C1_depth20_at2000"] = {a: {"k": sum(x["depth"] >= 20 for x in p if x["arm"] == a), "n": sum(x["arm"] == a for x in p)} for a in ("BASE", "ATOMIC")}
res["observed"]["C_ATOMIC_C1_seeds0_29_ATOMIC_depth20"] = sum(x["depth"] >= 20 for x in p if x["arm"] == "ATOMIC" and x["seed"] - 12_000_000 < 30)
res["observed"]["X_ATOMIC_runaways"] = {"BASE": "3/64", "ATOMIC": "36/64"}
# per-seed agreement of the FIELD|BANK ATOMIC rung with C-ATOMIC's world run on the SAME seed
fb = {x["s"]: x for x in d.get("ATOMIC|FIELD|BANK|CARRY|MUT", [])}
wd = {x["seed"] - 12_000_000: x["depth"] for x in p if x["arm"] == "ATOMIC"}
pairs = [(fb[s]["maxA"] >= 40, wd[s] >= 20) for s in fb if s in wd]
res["ATOMIC_FIELD_BANK_vs_world_same_seed"] = {"both": sum(a and b for a, b in pairs), "model_only": sum(a and not b for a, b in pairs),
                                              "world_only": sum(b and not a for a, b in pairs), "neither": sum(not a and not b for a, b in pairs)}
json.dump(res, open(F.HERE / "a1_summary.json", "w"), indent=1)
print("cpu workers", res["cpu_s_workers"])
for k, r in list(res["configs"].items()) + list(res["observed"].items())[:2]:
    print(f"{k:40s} n={r['depth20']['n']:3d} d20={r['depth20']['p']:.3f} B163={r['B163']['p']:.3f} A40={r['maxA40']['p']:.3f} any={r['any_runaway']['p']:.3f} Bbins={[r['B_bins'][b] for b in ('0','1-4','5-26','27-162','>=163')]}")
for k in list(res["observed"])[2:]: print(k, res["observed"][k])
print(res["ATOMIC_FIELD_BANK_vs_world_same_seed"])
