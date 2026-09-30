import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_common import clause_A, success, pc_success, max_rel_dev

HERE = os.path.dirname(os.path.abspath(__file__))
rows = [json.loads(l) for l in open(os.path.join(HERE, "pilot_rows.jsonl"), encoding="utf-8")]
cpu = json.load(open(os.path.join(HERE, "pilot_cpu.json")))
pc = [r for r in rows if r["arm"] == "POSITIVE_CONTROL"]
ch = [r for r in rows if r["arm"] == "CHEAT"]
tw = [r for r in rows if r["arm"] == "NULL_TWIN"]
assert len(pc) >= 5 and len(ch) >= 5 and len(tw) >= 5

positive = bool(all(pc_success(r) for r in pc))
cheat = bool(all(success(r["r_by_K"], r["twin_ratio_injected"]) for r in ch))
tw_mean = list(np.mean([r["r_by_K"] for r in tw], axis=0))
twin_meets = bool(any(clause_A(r["r_by_K"]) for r in tw) or clause_A(tw_mean))

p = os.path.join(HERE, "PILOT.json")

res = {
    "positive_meets_success": positive,
    "cheat_detected": cheat,
    "null_twin_meets_success": twin_meets,
    "pilot_pass": positive and cheat and not twin_meets,
    "stats": {
        "pc_depth_final": [r["depth_final"] for r in pc],
        "pc_periods": pc[0]["periods"],
        "pc_residual_after_4th_promotion": [r["residual_after_4th_promotion"] for r in pc],
        "cheat_max_rel_dev": [round(max_rel_dev(r["r_by_K"]), 4) for r in ch],
        "twin_max_rel_dev_per_seed": [round(max_rel_dev(r["r_by_K"]), 4) for r in tw],
        "twin_max_rel_dev_mean_curve": round(max_rel_dev(tw_mean), 4),
        "twin_ratio_20_0_per_seed": [round(r["ratio_20_0"], 4) for r in tw],
        "twin_ratio_20_0_mean": round(float(np.mean([r["ratio_20_0"] for r in tw])), 4),
        "twin_periods_seed0_first10": tw[0]["periods"][:10],
        "cpu_seconds": cpu["cpu_seconds"],
    },
    "attempt": cpu["attempt"],
}
json.dump(res, open(p, "w"), indent=1)
print(json.dumps(res, indent=1))
