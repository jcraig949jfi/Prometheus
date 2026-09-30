"""Evaluate HT-47f4c02be4 / W4 from rows.jsonl only; writes OUTCOME.json."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "rows.jsonl")
META = os.path.join(HERE, "run_meta.json")
OUT = os.path.join(HERE, "OUTCOME.json")
ATTEMPTS_FILE = os.path.join(HERE, "attempts.json")

DRIFT_MAX = 0.5   # spec: prior <= 0.5 x ascending on drift world s = 1
NULL_MIN = 0.9    # spec: prior >= 0.9 x ascending on null twin
POS_MIN = 0.99    # spec: first-try success >= 99% at s = 0


def pooled(rows, arm, s, key):
    rs = [r for r in rows if r["arm"] == arm and r["s"] == s]
    n = sum(r[key]["n"] for r in rs)
    tot = sum(r[key]["mean_cost"] * r[key]["n"] for r in rs)
    return tot / n, n, rs


def main():
    rows = [json.loads(l) for l in open(ROWS, encoding="utf-8") if l.strip()]
    st = {}
    for s in (1, 3, 10):
        tm, tn, trs = pooled(rows, "TREATMENT", s, "prior")
        cm, cn, crs = pooled(rows, "CONTROL", s, "ascending")
        npm, nn, nrs = pooled(rows, "NULL_TWIN", s, "prior")
        nam, _, _ = pooled(rows, "NULL_TWIN", s, "ascending")
        mm, mn, _ = pooled(rows, "MEMO", s, "memo")
        st[f"s={s}"] = {
            "TREATMENT_prior_mean_divisions": tm, "TREATMENT_n": tn,
            "CONTROL_ascending_mean_divisions": cm, "CONTROL_n": cn,
            "R_drift": tm / cm,
            "R_drift_per_seed": [t["prior"]["mean_cost"] / c["ascending"]["mean_cost"]
                                 for t, c in zip(sorted(trs, key=lambda r: r["seed"]),
                                                 sorted(crs, key=lambda r: r["seed"]))],
            "NULL_TWIN_prior_mean_divisions": npm, "NULL_TWIN_ascending_mean_divisions": nam,
            "NULL_TWIN_n": nn, "R_null": npm / nam,
            "R_null_per_seed": [r["prior"]["mean_cost"] / r["ascending"]["mean_cost"]
                                for r in sorted(nrs, key=lambda r: r["seed"])],
            "MEMO_mean_divisions_diagnostic": mm, "R_memo_diagnostic": mm / cm,
        }
    pos = [r for r in rows if r["arm"] == "POSITIVE_CONTROL"]
    pos_n = sum(r["prior"]["n"] for r in pos)
    pos_first = sum(r["prior"]["first_try_frac"] * r["prior"]["n"] for r in pos) / pos_n
    cheat_m, cheat_n, _ = pooled(rows, "CHEAT", 1, "prior")
    cheat_asc, _, _ = pooled(rows, "CHEAT", 1, "ascending")
    r_cheat = cheat_m / cheat_asc
    st["POSITIVE_CONTROL"] = {"first_try_frac": pos_first, "n": pos_n,
                              "prior_mean_divisions": sum(r["prior"]["mean_cost"] for r in pos) / len(pos)}
    st["CHEAT"] = {"R_cheat": r_cheat, "n": cheat_n}

    s1 = st["s=1"]
    pos_ok = pos_first >= POS_MIN
    cheat_ok = r_cheat <= DRIFT_MAX
    treat_meets = s1["R_drift"] <= DRIFT_MAX
    null_clause = s1["R_null"] >= NULL_MIN
    null_meets_success = s1["R_null"] <= DRIFT_MAX
    if not (pos_ok and cheat_ok):
        outcome = "INSTRUMENT_FAIL"
    elif null_meets_success:
        outcome = "CONFOUNDED"
    elif treat_meets and null_clause:
        outcome = "SIGNAL"
    else:
        outcome = "NULL"

    meta = json.load(open(META, encoding="utf-8")) if os.path.exists(META) else {}
    attempts = json.load(open(ATTEMPTS_FILE))["attempts"] if os.path.exists(ATTEMPTS_FILE) else 1
    out = {
        "triplicateId": "HT-47f4c02be4", "world": "W4", "outcome": outcome,
        "statistics": st,
        "criterion_as_applied": (
            f"s=1, pooled 5 seeds x 10000: R_drift = mean prior / mean ascending = {s1['R_drift']:.4f} "
            f"(<= 0.5? {treat_meets}); R_null (shuffled twin) = {s1['R_null']:.4f} (>= 0.9? {null_clause}). "
            f"Null twin 'meets success' = R_null <= 0.5: {null_meets_success}. "
            f"Positive control first-try frac {pos_first:.4f} (>= 0.99? {pos_ok}); "
            f"cheat R = {r_cheat:.4f} (<= 0.5? {cheat_ok})."),
        "positive_control_detected": pos_ok, "cheat_detected": cheat_ok,
        "null_twin_meets_success": null_meets_success,
        "stupid_explanations_status": [
            {"text": "any cache beats no cache on a slowly varying stream",
             "addressed_by_this_run": True,
             "how": f"MEMO diagnostic (try last two factors, then ascending) at s=1: R_memo = "
                    f"{s1['R_memo_diagnostic']:.4f} vs R_drift {s1['R_drift']:.4f}; and the shuffled null twin "
                    f"R_null = {s1['R_null']:.4f} shows how much saving survives without temporal order."},
            {"text": "operation count ignores the cost of maintaining the prior",
             "addressed_by_this_run": False,
             "how": "Observable counts trial divisions only; building the order costs 1229 distance "
                    "evaluations + a sort per sample, which exceeds ascending cost; not in the criterion."},
            {"text": "the asymmetry is a property of trial division, not of factoring in general",
             "addressed_by_this_run": False,
             "how": "Only trial division was implemented."},
        ],
        "anomalies": [],
        "core_minutes": meta.get("core_minutes"),
        "attempts": attempts,
        "notes": "",
    }
    if s1["R_null"] < 1.0:
        out["anomalies"].append(
            f"shuffled null twin still favors the prior (R_null={s1['R_null']:.3f} < 1); see TREATMENT rows' "
            f"range_idx_p/q for the index band the s=1 walk occupied")
    out["notes"] = (
        f"Outcome {outcome}. At s=1 the prior-ordered solver used {s1['TREATMENT_prior_mean_divisions']:.2f} "
        f"trial divisions per sample vs {s1['CONTROL_ascending_mean_divisions']:.2f} ascending "
        f"(R_drift={s1['R_drift']:.4f}). On the temporally shuffled twin the ratio was {s1['R_null']:.4f}. "
        f"Positive control first-try {pos_first:.4f}; cheat ratio {r_cheat:.4f}. "
        f"R_drift at s=3/10: {st['s=3']['R_drift']:.4f}/{st['s=10']['R_drift']:.4f}. "
        "Numbers only; generation cost is 1 multiplication so the infer/generate ratio equals the division count.")
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: out[k] for k in ("outcome", "criterion_as_applied", "anomalies", "core_minutes")}, indent=1))


if __name__ == "__main__":
    main()
