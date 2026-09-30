"""-> OUTCOME.json (round-1 fields); outcome decided in code (NOTES A6-A9)."""
import json
import numpy as np

rows = [json.loads(l) for l in open("rows.jsonl", encoding="utf-8")]
by = {}
for r in rows:
    by.setdefault(r["arm"], []).append(r)
med = lambda a, k: float(np.median([r[k] for r in by[a]]))
st = {a: {"n": len(by[a]), "median_stat_kl": med(a, "stat_kl"), "median_late_kl": med(a, "late_kl"),
          "median_rt": med(a, "rt"), "n_rt_censored": int(sum(r["rt_censored"] for r in by[a]))}
      for a in by}
for a in ("TREATMENT", "CONTROL", "NULL_TWIN"):
    st[a]["median_mean_sd_applied"] = med(a, "mean_sd_applied")
    st[a]["median_sd_applied_post50"] = med(a, "sd_applied_post50")
rtT, rtC, rtN = (st[a]["median_rt"] for a in ("TREATMENT", "CONTROL", "NULL_TWIN"))
ratio = lambda x, y: (x / y) if y > 0 else (0.0 if x == 0 else float("inf"))
rTC, rTN, rNC = ratio(rtT, rtC), ratio(rtT, rtN), ratio(rtN, rtC)
st["ratios"] = {"T_over_C": rTC, "T_over_N": rTN, "N_over_C": rNC}
klT, klN = st["TREATMENT"]["median_stat_kl"], st["NULL_TWIN"]["median_stat_kl"]

pos = st["POSITIVE_CONTROL"]["median_stat_kl"] < 0.02
cheat = (st["CHEAT"]["median_stat_kl"] < 0.1 and st["CHEAT"]["median_rt"] <= 0.7 * rtC
         and st["CHEAT"]["median_rt"] <= 0.7 * rtN)
null_meets = klN < 0.1 and rtN <= 0.7 * rtC
success = klT < 0.1 and rTC <= 0.7 and rTN <= 0.7
failure = klT >= 0.1 or rTC > 0.9 or rTN > 0.9
if not (pos and cheat):
    outcome = "INSTRUMENT_FAIL"
elif null_meets:
    outcome = "CONFOUNDED"
elif success:
    outcome = "SIGNAL"
else:
    outcome = "NULL"
anomalies = ["pilot null-twin check was structurally False (ratio vs itself); phase-2 confound check uses rt_null vs rt_control only (NOTES A6)"]
if not success and not failure:
    anomalies.append("treatment in the 0.7-0.9 ratio gap: meets neither criterion; classed NULL")
for a in ("TREATMENT", "CONTROL", "NULL_TWIN"):
    if st[a]["n_rt_censored"]:
        anomalies.append(f"{a}: {st[a]['n_rt_censored']} seeds re-tracking censored at 1000")
pilot_cpu = json.load(open("pilot_cpu.json"))["cpu_seconds"]
world_cpu = json.load(open("world_cpu.json"))["cpu_seconds"]
out = {
    "triplicateId": "HT-e743909f97", "world": "W3", "outcome": outcome, "statistics": st,
    "criterion_as_applied": {
        "success": "median stat KL(T) < 0.1 AND median rt(T) <= 0.7*median rt(C) AND <= 0.7*median rt(N), 30 seeds",
        "failure": "KL(T) >= 0.1 OR rt ratio > 0.9 vs C or N",
        "success_met": bool(success), "failure_met": bool(failure),
        "klT_lt_0.1": bool(klT < 0.1), "T_over_C": rTC, "T_over_N": rTN},
    "positive_control_detected": bool(pos), "cheat_detected": bool(cheat),
    "null_twin_meets_success": bool(null_meets),
    "stupid_explanations_status": {
        "larger mutation after the switch just raises exploration":
            "NOT RULED OUT: error coupling IS larger post-switch mutation; the time-permuted null twin separates coupling from marginal sd statistics, not from 'more exploration when error is high'",
        "grid coarseness makes KL small anyway":
            "NOT TESTED (single 64-bin grid; no finer-grid rerun)",
        "it is sequential Monte Carlo renamed":
            "NOT RULED OUT: implementation is a bootstrap particle filter with per-particle jitter by construction"},
    "anomalies": anomalies,
    "core_minutes": round((pilot_cpu + world_cpu) / 60, 3),
    "attempts": {"pilot": 1, "phase2": 1},
    "notes": "pilot passed attempt 1 (PILOT.json); parameters fixed in NOTES.md before any run; single-threaded numpy.",
}
json.dump(out, open("OUTCOME.json", "w"), indent=1)
print(json.dumps(out, indent=1))
