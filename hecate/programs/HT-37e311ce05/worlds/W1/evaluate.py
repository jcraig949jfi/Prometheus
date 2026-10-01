"""Reads rows.jsonl only; applies W1 criteria as written (readings in notes)."""
import os, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "rows.jsonl")) as fh:
    rows = [json.loads(l) for l in fh if l.strip()]
by = {}
for r in rows:
    by.setdefault(r["arm"], []).append(r)
mstar = rows[0]["m_star"]


def stab_ok(r):
    return bool(r["f_pool"] >= 0.8 and r["T"] is not None and mstar
                and abs(r["T"] / mstar - 1) <= 0.15)


def ms(arm):
    return float(np.mean([r["mean_success"] for r in by[arm]]))


def part_a(arm):
    return sum(stab_ok(r) for r in by[arm])


def success(arm, ref="CONTROL"):
    return part_a(arm) >= 8 and (ms(arm) - ms(ref)) >= 0.3


stats = {}
for arm, rs in by.items():
    Ts = [r["T"] for r in rs if r["T"] is not None]
    stats[arm] = dict(
        n=len(rs),
        f_pool_per_seed=[round(r["f_pool"], 3) for r in rs],
        T_per_seed=[None if r["T"] is None else round(r["T"], 2) for r in rs],
        T_over_mstar_mean=(float(np.mean(Ts)) / mstar) if Ts else None,
        mean_success_mean=ms(arm),
        mean_m_mean=(float(np.mean([r["mean_m"] for r in rs]))
                     if rs[0]["mean_m"] is not None else None),
        seeds_meeting_part_a=part_a(arm),
        seeds_f_pool_below_0_5=int(sum(r["f_pool"] < 0.5 for r in rs)))
diff = ms("TREATMENT") - ms("CONTROL")
stats["success_difference_TREATMENT_minus_CONTROL"] = diff
stats["m_star"] = mstar

treat_success = success("TREATMENT")
treat_failure = stats["TREATMENT"]["seeds_f_pool_below_0_5"] >= 5 or diff < 0.1
pc = sum(r["T"] is not None and abs(r["T"] / mstar - 1) <= 0.15
         for r in by["POSITIVE_CONTROL"]) >= 8
cheat = success("CHEAT")
null_meets = part_a("NULL_TWIN") >= 8

if not (pc and cheat):
    outcome = "INSTRUMENT_FAIL"
elif null_meets:
    outcome = "CONFOUNDED"
elif treat_success:
    outcome = "SIGNAL"
else:
    outcome = "NULL"

anoms = []
r0 = rows[0]
if abs(r0["null_mean"] - r0["cs_mean"]) > 1e-3:
    anoms.append(f"null mean {r0['null_mean']:.4f} != CS mean {r0['cs_mean']:.4f}")
if abs(r0["null_endpoints"][1] - r0["cs_endpoints"][1]) > 1e-9:
    anoms.append(f"null P(120)={r0['null_endpoints'][1]} vs CS {r0['cs_endpoints'][1]}")
if mstar is not None and 120 < mstar * 1.15:
    anoms.append("m* within 15% of pair cap 120")
if part_a("CONTROL") != part_a("NULL_TWIN"):
    anoms.append(f"CONTROL part(a) seeds {part_a('CONTROL')} vs NULL_TWIN {part_a('NULL_TWIN')}")
if stats["POSITIVE_CONTROL"]["seeds_meeting_part_a"] < 8 and pc:
    anoms.append("positive control T within 15% but f_pool<0.8 in >2 seeds")

# Diagnostics only (added after attempt 1; decision logic above unchanged).
max_diff = 1.0 - ms("CONTROL")
if max_diff < 0.3:
    anoms.append(f"success part (b) unattainable: CONTROL mean success {ms('CONTROL'):.4f}, "
                 f"so max attainable difference is {max_diff:.4f} < 0.3 (CHEAT at 1.0 fails)")
m_max = r0["params"]["m_max"]
if mstar is not None and mstar <= m_max:
    anoms.append(f"m*={mstar} <= individual cap {m_max}: a lone agent can reach m*, so pooling is "
                 f"not required; POSITIVE_CONTROL mean T/m* = "
                 f"{stats['POSITIVE_CONTROL']['T_over_mstar_mean']:.2f} (pairs sum two solo budgets)")

cpu = max(r["cpu_s_cumulative"] for r in rows)
with open(os.path.join(HERE, "attempts.json")) as fh:
    att = json.load(fh)["attempts"]
cs = r0["cs_table"]; nt = r0["null_table"]


def slope(t, m):
    lo, hi = max(m - 2, 0), min(m + 2, 120)
    return (t[hi] - t[lo]) / (hi - lo)


out = {
    "triplicateId": "HT-37e311ce05", "world": "W1", "outcome": outcome,
    "statistics": stats,
    "criterion_as_applied": (
        f"m*={mstar} (smallest m with P_CS>=0.5). SUCCESS: >=8/10 TREATMENT seeds with "
        "final f_pool>=0.8 and |T/m*-1|<=0.15 (T=mean m1+m2 over both-pool pairs of the "
        "final generation), AND mean-over-seeds success(TREATMENT)-success(CONTROL)>=0.3. "
        "FAILURE: f_pool<0.5 in >=5/10 TREATMENT seeds OR difference<0.1. "
        f"TREATMENT success={treat_success}, failure={treat_failure}, diff={diff:.4f}."),
    "positive_control_detected": bool(pc), "cheat_detected": bool(cheat),
    "null_twin_meets_success": bool(null_meets),
    "stupid_explanations_status": [
        {"text": "mutation bias toward lower m drives free-riding in both arms",
         "addressed_by_this_run": True,
         "how": "mutation is symmetric +-1 by construction, identical across arms; only the "
                "clip at 0 and 60 is asymmetric at the boundaries. Mean m per arm reported."},
        {"text": "m* sits near the max budget so the cap does the work",
         "addressed_by_this_run": True,
         "how": f"m*={mstar}: {mstar/60:.2f} of the individual cap 60, {mstar/120:.2f} of the pair cap 120."},
        {"text": "the linear null has lower marginal return near m*, so selection intensity differs",
         "addressed_by_this_run": False,
         "how": f"slope near m*: CS {slope(cs, mstar):.4f}/row vs null {slope(nt, mstar):.4f}/row; "
                "inherent to the null design, not separable in this run."}],
    "anomalies": anoms,
    "core_minutes": round(cpu / 60, 4), "attempts": att,
    "notes": "",
}
out["notes"] = (
    f"OMP transition midpoint m*={mstar}. Final pooling frequency (mean over seeds): "
    f"TREATMENT {np.mean(stats['TREATMENT']['f_pool_per_seed']):.2f}, CONTROL "
    f"{np.mean(stats['CONTROL']['f_pool_per_seed']):.2f}, NULL_TWIN "
    f"{np.mean(stats['NULL_TWIN']['f_pool_per_seed']):.2f}, POSITIVE_CONTROL "
    f"{np.mean(stats['POSITIVE_CONTROL']['f_pool_per_seed']):.2f}. Seeds meeting the "
    f"stability part: TREATMENT {part_a('TREATMENT')}/10, NULL_TWIN {part_a('NULL_TWIN')}/10. "
    f"Mean success difference TREATMENT-CONTROL {diff:.3f} (threshold 0.3). Outcome {outcome} "
    "decided in code from the PREREG classes.")
with open(os.path.join(HERE, "OUTCOME.json"), "w") as fh:
    json.dump(out, fh, indent=1)
print(json.dumps({k: out[k] for k in ["outcome", "positive_control_detected", "cheat_detected",
                                      "null_twin_meets_success", "core_minutes", "attempts",
                                      "anomalies", "notes"]}, indent=1))
