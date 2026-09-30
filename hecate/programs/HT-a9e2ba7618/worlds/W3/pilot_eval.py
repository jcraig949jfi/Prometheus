import json, sys
import numpy as np

attempt = int(sys.argv[1]) if len(sys.argv) > 1 else 1
rows = [json.loads(l) for l in open("pilot_rows.jsonl")]
def med(arm, key="ari_osc"):
    v = [r[key] for r in rows if r["arm"] == arm and r[key] is not None]
    return float(np.median(v)) if v else None, len(v)
stats = {}
for arm in ["POSITIVE_CONTROL", "CHEAT", "NULL_TWIN"]:
    m, n = med(arm); mc, _ = med(arm, "ari_comp")
    q = [r["ari_osc"] for r in rows if r["arm"] == arm]
    stats[arm] = dict(median_ari_osc=m, median_ari_comp=mc, n_seeds=n,
                      q10=float(np.quantile(q, .1)), q90=float(np.quantile(q, .9)))
pos = stats["POSITIVE_CONTROL"]["median_ari_osc"] >= 0.95
cheat = stats["CHEAT"]["median_ari_osc"] >= 0.95 and stats["CHEAT"]["median_ari_osc"] >= 0.7
twin = stats["NULL_TWIN"]["median_ari_osc"] >= 0.7
res = dict(positive_meets_success=bool(pos), cheat_detected=bool(cheat),
           null_twin_meets_success=bool(twin), pilot_pass=bool(pos and cheat and not twin),
           stats=stats, attempt=attempt)
json.dump(res, open("PILOT.json", "w"), indent=1)
print(json.dumps(res, indent=1))
