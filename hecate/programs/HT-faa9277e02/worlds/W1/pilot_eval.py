import json, sys
import numpy as np
from criteria import success, null_twin_meets

ATTEMPT = int(sys.argv[1]) if len(sys.argv) > 1 else 1
src = "pilot_rows.jsonl" if ATTEMPT == 1 else f"pilot_rows_attempt{ATTEMPT}.jsonl"
rows = [json.loads(l) for l in open(src)]
by = {}
for r in rows:
    by.setdefault(r["arm"], {})[r["seed"]] = r["r"]
seeds = sorted(by["NULL_TWIN"])
pos = [by["POSITIVE_CONTROL"][s] for s in seeds]
nul = [by["NULL_TWIN"][s] for s in seeds]
che = [by["CHEAT"][s] for s in seeds]
pos_mean = float(np.mean(pos))
pos_ok, pos_st = success(pos, nul, pos_mean)
che_ok, che_st = success(che, nul, pos_mean)
nt = null_twin_meets(nul)
out = {"positive_meets_success": bool(pos_ok), "cheat_detected": bool(che_ok),
       "null_twin_meets_success": bool(nt),
       "pilot_pass": bool(pos_ok and che_ok and not nt),
       "stats": {"n_seeds": len(seeds), "positive": {**pos_st, "per_seed": pos},
                 "cheat": {**che_st, "per_seed": che},
                 "null_twin": {"mean_r": float(np.mean(nul)), "per_seed": nul},
                 "degenerate_rows": sum(r.get("degenerate", False) for r in rows),
                 "cpu_s_total": sum(r["cpu_s"] + (r["phaseA_cpu_s"] if r["arm"] == "CHEAT" else 0) for r in rows)},
       "attempt": ATTEMPT}
json.dump(out, open("PILOT.json" if ATTEMPT == 1 else f"PILOT_attempt{ATTEMPT}.json", "w"), indent=1, default=bool)
print(json.dumps(out, indent=1, default=bool))
