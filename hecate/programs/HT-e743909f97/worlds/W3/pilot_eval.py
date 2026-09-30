"""Pilot evaluation -> PILOT.json (readings: NOTES.md A6-A8)."""
import json, sys
import numpy as np

rows = [json.loads(l) for l in open("pilot_rows.jsonl", encoding="utf-8")]
attempt = max(r["attempt"] for r in rows)
by = {}
for r in rows:
    by.setdefault(r["arm"], []).append(r)
med = lambda arm, k: float(np.median([r[k] for r in by[arm]]))
st = {a: {"n": len(by[a]), "median_stat_kl": med(a, "stat_kl"), "median_late_kl": med(a, "late_kl"),
          "median_rt": med(a, "rt"), "n_rt_censored": sum(r["rt_censored"] for r in by[a])} for a in by}
pos = st["POSITIVE_CONTROL"]["median_stat_kl"] < 0.02
rt_n = st["NULL_TWIN"]["median_rt"]
cheat = st["CHEAT"]["median_stat_kl"] < 0.1 and st["CHEAT"]["median_rt"] <= 0.7 * rt_n
# A6: literal reading, null twin in treatment role vs itself -> ratio 1 > 0.7
null = st["NULL_TWIN"]["median_stat_kl"] < 0.1 and rt_n <= 0.7 * rt_n
out = {"positive_meets_success": bool(pos), "cheat_detected": bool(cheat),
       "null_twin_meets_success": bool(null), "pilot_pass": bool(pos and cheat and not null),
       "stats": st, "attempt": attempt,
       "note": "null_twin_meets_success is structurally False in the pilot (NOTES A6); the "
               "informative confound check is phase 2's rt_null vs rt_control."}
json.dump(out, open("PILOT.json", "w"), indent=1)
print(json.dumps(out, indent=1))
