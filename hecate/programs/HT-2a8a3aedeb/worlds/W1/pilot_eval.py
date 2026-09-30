"""Evaluate pilot rows -> PILOT.json"""
import json
import criteria

rows = [json.loads(l) for l in open("pilot_rows.jsonl")]
by = {}
for r in rows:
    by.setdefault(r["arm"], []).append(r)
attempt = json.load(open("pilot_cpu.json"))["attempt"]
pos = criteria.positive_meets(by["POSITIVE_CONTROL"])
nt = criteria.success(by["NULL_TWIN"])
ch = criteria.success(by["CHEAT"])
# descriptive: null twin expectation |bz-bV|<=1, both near full (36)
d = [(cd["z"]["1e-06"], cd["V"]["1e-06"]) for r in by["NULL_TWIN"] for cd in r["conds"] if cd["lam"] >= 1]
out = {
    "positive_meets_success": pos["meets"],
    "cheat_detected": ch["success"],
    "null_twin_meets_success": nt["success"],
    "pilot_pass": bool(pos["meets"] and ch["success"] and not nt["success"]),
    "stats": {"positive": pos, "cheat": ch, "null_twin": nt,
              "null_twin_desc": {"frac_absdiff_le1": sum(abs(a - b) <= 1 for a, b in d) / len(d),
                                 "mean_bz": sum(a for a, _ in d) / len(d),
                                 "mean_bV": sum(b for _, b in d) / len(d)}},
    "attempt": attempt,
}
json.dump(out, open("PILOT.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("positive_meets_success", "cheat_detected", "null_twin_meets_success", "pilot_pass", "attempt")}))
