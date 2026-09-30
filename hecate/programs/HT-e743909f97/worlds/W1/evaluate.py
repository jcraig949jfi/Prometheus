"""Evaluate HT-e743909f97 / W1 from rows.jsonl only; writes OUTCOME.json."""
import json
import os
import time
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
t0 = time.process_time()

rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"), encoding="utf-8")]
P = rows[0]["params"]
TAU_PRED = P["tau_pred"]
PC_TAU = P["pc_tau_analytic"]
GRID_END = 40  # censoring value: one past tau = 39

groups = defaultdict(lambda: defaultdict(list))  # key -> tau -> [indicator]
extinct = defaultdict(lambda: defaultdict(list))
for r in rows:
    key = (r["arm"], r.get("cheat_role", "main"), r["exhaustion"])
    groups[key][r["tau"]].append(r["indicator"])
    extinct[key][r["tau"]].append(r["p_extinct"])


def tau_obs(key):
    g = groups[key]
    for tau in sorted(g):
        v = g[tau]
        if sum(v) / len(v) >= 0.5:
            return tau, len(v)
    return None, len(next(iter(g.values())))


def summary(key):
    t, n = tau_obs(key)
    g = groups[key]
    return dict(tau_obs=t, n_seeds=n,
                frac_indicator_by_tau={tau: round(sum(v) / len(v), 3) for tau, v in sorted(g.items())},
                frac_extinct_by_tau={tau: round(sum(v) / len(v), 3) for tau, v in sorted(extinct[key].items())})


def assess(off_key, on_key, ctrl_off_key, ctrl_on_key):
    flags = []
    t_off, _ = tau_obs(off_key)
    t_on, _ = tau_obs(on_key)
    c_off, _ = tau_obs(ctrl_off_key)
    c_on, _ = tau_obs(ctrl_on_key)
    if t_off is None or t_off == 0:
        return dict(success=False, failure=True, relerr=None, ratio=None, ctrl_ratio=None,
                    flags=["tau_obs(off) undefined or 0"])
    relerr = abs(t_off - TAU_PRED) / TAU_PRED
    if t_on is None:
        t_on = GRID_END; flags.append("tau_obs(on) censored at 40")
    ratio = t_on / t_off
    if c_off is None or c_off == 0:
        ctrl_ratio = None; flags.append("control tau_obs(off) undefined or 0")
    else:
        if c_on is None:
            c_on = GRID_END; flags.append("control tau_obs(on) censored at 40")
        ctrl_ratio = c_on / c_off
    c3 = ctrl_ratio is not None and (ratio - ctrl_ratio) >= 0.1
    success = relerr <= 0.15 and ratio >= 1.3 and c3
    failure = (relerr > 0.15 or ratio < 1.1 or ctrl_ratio is None or abs(ratio - ctrl_ratio) < 0.1)
    return dict(success=bool(success), failure=bool(failure), relerr=relerr, ratio=ratio,
                ctrl_ratio=ctrl_ratio, clauses=dict(relerr_le_0_15=relerr <= 0.15,
                                                    ratio_ge_1_3=ratio >= 1.3,
                                                    ratio_minus_ctrl_ge_0_1=bool(c3)),
                flags=flags)


T = assess(("TREATMENT", "main", False), ("TREATMENT", "main", True),
           ("CONTROL", "main", False), ("CONTROL", "main", True))
N = assess(("NULL_TWIN", "main", False), ("NULL_TWIN", "main", True),
           ("CONTROL", "main", False), ("CONTROL", "main", True))
C = assess(("CHEAT", "treatment", False), ("CHEAT", "treatment", True),
           ("CHEAT", "control", False), ("CHEAT", "control", True))
pc_t, pc_n = tau_obs(("POSITIVE_CONTROL", "main", False))
pc_err = None if pc_t is None else abs(pc_t - PC_TAU) / PC_TAU
pc_detected = pc_err is not None and pc_err <= 0.05
cheat_detected = C["success"]
null_meets = N["success"]

if not (pc_detected and cheat_detected):
    outcome = "INSTRUMENT_FAIL"
elif null_meets:
    outcome = "CONFOUNDED"
elif T["success"]:
    outcome = "SIGNAL"
else:
    outcome = "NULL"

# descriptive diagnostics from rows
def mean_field(arm, exh, field):
    v = [r[field] for r in rows if r["arm"] == arm and r["exhaustion"] == exh and r.get(field) is not None]
    return (sum(v) / len(v)) if v else None

anomalies = []
if abs(P["pc_tau_nyquist"] - PC_TAU) / PC_TAU > 1e-3:
    anomalies.append("Nyquist routine disagrees with analytic PC critical delay")
for arm in ("TREATMENT", "CONTROL", "NULL_TWIN", "POSITIVE_CONTROL"):
    d = [r for r in rows if r["arm"] == arm and r.get("diverged")]
    if d:
        anomalies.append(f"{arm}: {len(d)} diverged runs (p > 1e13)")
nt = [r for r in rows if r["arm"] == "NULL_TWIN"]
if nt:
    clipm = sum(r["surrogate_clip_frac"] for r in nt) / len(nt)
    if clipm > 0:
        anomalies.append(f"NULL_TWIN surrogate negative-clip fraction mean {clipm:.4f}")
for arm in ("TREATMENT", "CONTROL"):
    for exh in (False, True):
        ex = [r for r in rows if r["arm"] == arm and r["exhaustion"] == exh and r["p_extinct"]]
        if ex:
            anomalies.append(f"{arm} exh={exh}: p extinct in {len(ex)} of 800 runs (min tau {min(r['tau'] for r in ex)})")

if T["ratio"] is not None and T["ratio"] < 1.0:
    anomalies.append(f"exhaustion LOWERED the onset delay (ratio {T['ratio']:.3f} < 1): opposite sign to the hypothesis")
ef = mean_field("TREATMENT", True, "exh_frac")
ma = mean_field("TREATMENT", True, "mean_a")
if ef is not None:
    anomalies.append(f"exhaustion on in {ef:.3f} of steps on average (mean a = {ma:.5f} = {ma / P['a0']:.3f} a0)")
if T["ctrl_ratio"] is not None and abs(T["ctrl_ratio"] - 1.0) < 1e-9:
    anomalies.append("matched fixed-gain control ratio exactly 1.0: a constant lower a leaves onset unchanged "
                     "(linear loop gain a*k*p* = c*r does not depend on a)")
cpu_world = json.load(open(os.path.join(HERE, "world_cpu.json")))
attempts = int(max(r["attempt"] for r in rows))
prior_cpu = 0.0
pc_path = os.path.join(HERE, "prior_attempts_cpu.json")
if os.path.exists(pc_path):
    prior_cpu = json.load(open(pc_path))["cpu_seconds"]

stats = {
    "tau_pred": TAU_PRED,
    "TREATMENT_off": summary(("TREATMENT", "main", False)),
    "TREATMENT_on": summary(("TREATMENT", "main", True)),
    "CONTROL_off": summary(("CONTROL", "main", False)),
    "CONTROL_on": summary(("CONTROL", "main", True)),
    "NULL_TWIN_off": summary(("NULL_TWIN", "main", False)),
    "NULL_TWIN_on": summary(("NULL_TWIN", "main", True)),
    "POSITIVE_CONTROL": dict(summary(("POSITIVE_CONTROL", "main", False)), tau_analytic=PC_TAU, rel_err=pc_err),
    "CHEAT_treatment_off": tau_obs(("CHEAT", "treatment", False))[0],
    "CHEAT_treatment_on": tau_obs(("CHEAT", "treatment", True))[0],
    "treatment_assessment": T, "null_twin_assessment": N, "cheat_assessment": C,
    "mean_a_treatment_exh_on": mean_field("TREATMENT", True, "mean_a"),
    "mean_exh_frac_treatment_on": mean_field("TREATMENT", True, "exh_frac"),
    "mean_kC_treatment_off": mean_field("TREATMENT", False, "mean_kC"),
    "mean_kC_treatment_on": mean_field("TREATMENT", True, "mean_kC"),
}

core_minutes = (prior_cpu + cpu_world["cpu_seconds"] + (time.process_time() - t0)) / 60.0
out = {
    "triplicateId": "HT-e743909f97", "world": "W1", "outcome": outcome,
    "statistics": stats,
    "criterion_as_applied": (
        "tau_obs = smallest tau in 0..39 with CV(p, last 2000 of 5000 steps) > 0.2 in >= 50%% of 20 seeds. "
        "SUCCESS iff |tau_obs(no exh) - tau_pred|/tau_pred <= 0.15 (tau_pred = %.3f, linearised Nyquist) AND "
        "tau_obs(exh)/tau_obs(no exh) >= 1.3 AND that ratio - control ratio >= 0.1, where control = same loop, "
        "exhaustion off, clonal gain a fixed at the time-average of a(t) of the matched adaptive run; undefined "
        "tau_obs(exh) censored at 40. Positive control detected iff its tau_obs is within 5%% of analytic 25.5. "
        "Cheat detected iff the success function passes on injected rows." % TAU_PRED),
    "positive_control_detected": bool(pc_detected), "cheat_detected": bool(cheat_detected),
    "null_twin_meets_success": bool(null_meets),
    "stupid_explanations_status": [
        {"text": "exhaustion only reduces mean gain (checked by the matched fixed-gain control)",
         "addressed_by_this_run": True,
         "how": "CONTROL arm fixes a at the adaptive run's mean a(t); ratio compared (clause 3)."},
        {"text": "stochastic extinction at low counts ends oscillation early and looks like stability",
         "addressed_by_this_run": True,
         "how": "p extinction recorded per row; fraction by tau in statistics.*.frac_extinct_by_tau; counts ~1e5."},
        {"text": "the CV threshold 0.2 is tuned to the result",
         "addressed_by_this_run": False,
         "how": "threshold fixed by spec and not varied; per-row cv values are in rows.jsonl for a later sweep, "
                "but no threshold sensitivity was run here."},
    ],
    "anomalies": anomalies,
    "core_minutes": round(core_minutes, 3),
    "attempts": attempts,
    "notes": "",
}

def fmt(x):
    return "none" if x is None else (f"{x:.3f}" if isinstance(x, float) else str(x))

out["notes"] = (
    f"Outcome {outcome}. Predicted critical delay {TAU_PRED:.2f}; treatment onset without exhaustion "
    f"{fmt(stats['TREATMENT_off']['tau_obs'])} (rel err {fmt(T['relerr'])}), with exhaustion "
    f"{fmt(stats['TREATMENT_on']['tau_obs'])} (ratio {fmt(T['ratio'])}); matched fixed-gain control onsets "
    f"{fmt(stats['CONTROL_off']['tau_obs'])}/{fmt(stats['CONTROL_on']['tau_obs'])} (ratio {fmt(T['ctrl_ratio'])}); "
    f"null twin onsets {fmt(stats['NULL_TWIN_off']['tau_obs'])}/{fmt(stats['NULL_TWIN_on']['tau_obs'])}; "
    f"positive control onset {fmt(pc_t)} vs 25.5 analytic (err {fmt(pc_err)}); cheat detected {cheat_detected}. "
    "Numbers only; the class is assigned by code from the PREREG rules."
)
json.dump(out, open(os.path.join(HERE, "OUTCOME.json"), "w", encoding="utf-8"), indent=1)
print(json.dumps({k: out[k] for k in ("outcome", "positive_control_detected", "cheat_detected",
                                        "null_twin_meets_success", "core_minutes", "attempts", "notes", "anomalies")}, indent=1))
