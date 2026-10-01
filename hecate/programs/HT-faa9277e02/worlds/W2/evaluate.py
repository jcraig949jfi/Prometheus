"""Reads rows.jsonl only; applies W2 criteria as recorded in IMPLEMENTATION_NOTES.md; writes OUTCOME.json."""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"), encoding="utf-8")]
A = {}
for r in rows:
    A.setdefault(r["arm"], {})[r["seed"]] = r
seeds = sorted(A["TREATMENT"])
TS = ["1", "2", "4", "8", "16", "32"]


def b(arm, s, T="1"):
    return A[arm][s]["bits_mm"][T]


def sl(arm, s):
    return A[arm][s]["slope_T_le_8"]


def clauses(arm, s):
    a = b(arm, s) >= 0.8 * b("POSITIVE_CONTROL", s)
    bb = (b(arm, s) - b("NULL_TWIN", s)) >= 0.5
    c = 0.3 <= sl(arm, s) <= 0.7
    return a, bb, c


per_seed = {arm: [dict(seed=s, **dict(zip(["a_ratio", "b_null_margin", "c_slope"], clauses(arm, s))))
                  for s in seeds] for arm in ["TREATMENT", "CHEAT", "NULL_TWIN", "CONTROL"]}
treat_success = all(d["a_ratio"] and d["b_null_margin"] and d["c_slope"] for d in per_seed["TREATMENT"])
m_h1 = np.mean([b("TREATMENT", s) for s in seeds])
m_c1 = np.mean([b("CONTROL", s) for s in seeds])
m_hs = np.mean([sl("TREATMENT", s) for s in seeds])
treat_failure = bool(m_h1 <= m_c1 + 0.1 or not (0.15 <= m_hs <= 0.85))
null_meets = all(d["a_ratio"] and d["c_slope"] for d in per_seed["NULL_TWIN"])
pc_det = all(b("POSITIVE_CONTROL", s) - b("NULL_TWIN", s) >= 0.5 for s in seeds)
cheat_det = all(d["a_ratio"] and d["b_null_margin"] and d["c_slope"] for d in per_seed["CHEAT"])

if not (pc_det and cheat_det):
    outcome = "INSTRUMENT_FAIL"
elif null_meets:
    outcome = "CONFOUNDED"
elif treat_success and not treat_failure:
    outcome = "SIGNAL"
else:
    outcome = "NULL"

stats = {}
for arm in ["TREATMENT", "CONTROL", "NULL_TWIN", "POSITIVE_CONTROL", "CHEAT"]:
    bits = {T: dict(mean=float(np.mean([b(arm, s, T) for s in seeds])),
                    sd=float(np.std([b(arm, s, T) for s in seeds], ddof=1))) for T in TS}
    slopes = [sl(arm, s) for s in seeds]
    st = dict(n_seeds=len(seeds), n_test_per_T=50000, bits_mm_by_T=bits,
              slope_T_le_8_mean=float(np.mean(slopes)), slope_T_le_8_min=float(np.min(slopes)),
              slope_T_le_8_max=float(np.max(slopes)))
    if arm != "CHEAT":
        st["ratio_to_PC_T1_mean"] = float(np.mean([b(arm, s) / b("POSITIVE_CONTROL", s) for s in seeds]))
        st["mm_minus_plugin_T1_mean"] = float(np.mean([b(arm, s) - A[arm][s]["bits_plugin"]["1"] for s in seeds]))
        st["occupied_r_T1_min"] = int(min(A[arm][s]["occupied_r"]["1"] for s in seeds))
    if arm in ["TREATMENT", "NULL_TWIN", "CONTROL"]:
        st["clause_pass_counts"] = {k: int(sum(d[k] for d in per_seed[arm])) for k in ["a_ratio", "b_null_margin", "c_slope"]}
    stats[arm] = st

anom = []
if any(b("CHEAT", s, T) > 3.0 for s in seeds for T in TS):
    anom.append("CHEAT injected bits exceed log2(8)=3 at some T: injection is not a physically realisable 8-output readout")
pc1 = stats["POSITIVE_CONTROL"]["bits_mm_by_T"]["1"]["mean"]
need8 = 0.8 * pc1 + 0.3 * 3
anom.append(f"attainability: clauses (a)+(c) need bits(T=8) >= ~0.8*PC(T=1)+0.9 = {need8:.3f} vs cap 3.0")
cs = stats["CONTROL"]["slope_T_le_8_mean"]
if 0.3 <= cs <= 0.7:
    anom.append(f"CONTROL (no Hebb) slope {cs:.3f} is inside [0.3,0.7]")
for arm in ["TREATMENT", "NULL_TWIN", "CONTROL", "POSITIVE_CONTROL"]:
    if stats[arm]["occupied_r_T1_min"] < 8:
        anom.append(f"{arm} uses fewer than 8 outputs at T=1 in some seed (min {stats[arm]['occupied_r_T1_min']})")

meta = json.load(open(os.path.join(HERE, "run_meta.json")))
m1 = os.path.join(HERE, "attempt1_run_meta.json")
prior_cpu = json.load(open(m1))["cpu_seconds"] if os.path.exists(m1) else 0.0
ATTEMPTS = 2 if os.path.exists(m1) else 1
h, c, n, p = (stats[a]["bits_mm_by_T"]["1"]["mean"] for a in ["TREATMENT", "CONTROL", "NULL_TWIN", "POSITIVE_CONTROL"])
out = {
    "triplicateId": "HT-faa9277e02", "world": "W2", "outcome": outcome,
    "statistics": stats,
    "criterion_as_applied": ("SUCCESS iff in every one of 10 seeds: (a) Hebb MM-bits(T=1) >= 0.8*PC bits(T=1); "
                             "(b) Hebb - NULL_TWIN bits(T=1) >= 0.5; (c) OLS slope of bits vs log2 T over T in {1,2,4,8} in [0.3,0.7]. "
                             "FAILURE iff seed-mean Hebb bits(T=1) <= seed-mean CONTROL bits(T=1)+0.1 or seed-mean Hebb slope outside [0.15,0.85]. "
                             f"Result: success={treat_success}, failure={treat_failure}."),
    "positive_control_detected": bool(pc_det), "cheat_detected": bool(cheat_det),
    "null_twin_meets_success": bool(null_meets),
    "treatment_success": bool(treat_success), "treatment_failure": treat_failure,
    "stupid_explanations_status": [
        {"text": "MI estimator bias favours whichever readout has more occupied bins",
         "addressed_by_this_run": True,
         "how": f"MM correction recorded; mean MM-minus-plugin at T=1 per arm: " +
                ", ".join(f"{a}={stats[a]['mm_minus_plugin_T1_mean']:.4f}" for a in ["TREATMENT", "CONTROL", "NULL_TWIN", "POSITIVE_CONTROL"]) +
                "; min occupied outputs at T=1: " + ", ".join(f"{a}={stats[a]['occupied_r_T1_min']}" for a in ["TREATMENT", "CONTROL", "NULL_TWIN", "POSITIVE_CONTROL"])},
        {"text": "optimal bound computed with wrong noise model making ratio look high",
         "addressed_by_this_run": True,
         "how": "At T=1 (where the ratio clause applies) the decoder uses the exact generating lognormal model; for T>1 it uses the Fenton-Wilkinson approximation (not exact). The PC is an 8-class Bayes classifier, not a proven MI upper bound."},
        {"text": "the 0.5 log2 T law follows from Gaussian averaging with no role for Hebb",
         "addressed_by_this_run": True,
         "how": f"CONTROL (fixed quantizer, same averaging, no Hebb) slope mean {cs:.3f} vs TREATMENT {stats['TREATMENT']['slope_T_le_8_mean']:.3f}."},
    ],
    "anomalies": anom,
    "core_minutes": round((meta["cpu_seconds"] + prior_cpu) / 60.0, 3),
    "attempts": ATTEMPTS,
    "prereg_consequence": ("NOT_BUILT (second INSTRUMENT_FAIL after one repair)" if (outcome == "INSTRUMENT_FAIL" and ATTEMPTS >= 2) else None),
    "instrument_repair": "CHEAT injection repaired to satisfy clause (b); see IMPLEMENTATION_NOTES attempt log" if ATTEMPTS >= 2 else None,
    "notes": (f"At T=1, seed-mean Miller-Madow bits: Hebbian {h:.3f}, uniform quantizer {c:.3f}, random-centre null twin {n:.3f}, "
              f"Bayes 8-class decoder {p:.3f}. Mean slopes over T<=8: Hebbian {stats['TREATMENT']['slope_T_le_8_mean']:.3f}, "
              f"control {cs:.3f}, null {stats['NULL_TWIN']['slope_T_le_8_mean']:.3f}, PC {stats['POSITIVE_CONTROL']['slope_T_le_8_mean']:.3f}. "
              f"Outcome {outcome} by the PREREG class rules applied in code."),
}
json.dump(out, open(os.path.join(HERE, "OUTCOME.json"), "w"), indent=1)
print(json.dumps({k: out[k] for k in ["outcome", "positive_control_detected", "cheat_detected", "null_twin_meets_success", "treatment_success", "treatment_failure", "core_minutes", "anomalies", "notes"]}, indent=1))
