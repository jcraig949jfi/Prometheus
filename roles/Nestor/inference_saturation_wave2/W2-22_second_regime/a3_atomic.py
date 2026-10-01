"""W2-22 a3: ATOMIC world@300 (runs_ATOMIC_world.jsonl) vs W2-14 model FIELD BANK ATOMIC (ladder.jsonl, same seeds 0-29)
vs C-ATOMIC world@2000 depth, on identical readouts. -> a3_atomic.json"""
import json
from scipy.stats import fisher_exact
import w22
W = {r["s"]: r for r in map(json.loads, open(w22.HERE / "runs_ATOMIC_world.jsonl"))}
L = [json.loads(l) for l in open(w22.HERE.parent / "W2-14_F_calibration" / "ladder.jsonl")]
M = {r["s"]: r for r in L if r["rule"] == "ATOMIC" and r["struct"] == "FIELD" and r["partner"] == "BANK" and r["ctx"] == "CARRY" and r["mut"]}
S = sorted(set(W) & set(M))
RO = {"depth_world>=20": lambda r: r["depth_world"] >= 20, "depth_f>=20": lambda r: r["depth_f"] >= 20,
      "B>=163": lambda r: r["B"] >= 163, "maxA>=40": lambda r: r["maxA"] >= 40, "B>=27": lambda r: r["B"] >= 27}
out = {"n": len(S), "cpu_s_world300": round(sum(W[s]["cpu_s"] for s in S), 1), "rows": {}}
for k, f in RO.items():
    w = [f(W[s]) for s in S]; m = [f(M[s]) for s in S]
    both = sum(a and b for a, b in zip(w, m)); wo = sum(a and not b for a, b in zip(w, m)); mo = sum(b and not a for a, b in zip(w, m))
    out["rows"][k] = {"world300": "%d/%d" % (sum(w), len(S)), "model300": "%d/%d" % (sum(m), len(S)),
                      "both/world_only/model_only/neither": [both, wo, mo, len(S) - both - wo - mo],
                      "fisher_2s": fisher_exact([[sum(w), len(S) - sum(w)], [sum(m), len(S) - sum(m)]])[1]}
w2000 = [W[s]["world2000_depth"] >= 20 for s in S]; w300 = [W[s]["depth_world"] >= 20 for s in S]
out["world2000_depth>=20"] = "%d/%d" % (sum(w2000), len(S))
out["world300_vs_world2000_same_seed_agreement"] = sum(a == b for a, b in zip(w300, w2000))
json.dump(out, open(w22.HERE / "a3_atomic.json", "w"), indent=1)
print(json.dumps(out, indent=1))
