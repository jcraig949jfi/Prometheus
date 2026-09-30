"""Evaluate HT-321a8fd8e0 / W1 from rows.jsonl; write OUTCOME.json."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
KS = list(range(1, 9))
LOW_KS = [1, 2, 3]
HIGH_KS = [4, 5, 6, 7, 8]


def main():
    rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl")) if l.strip()]
    stats = {}
    for arm in sorted({r["arm"] for r in rows}):
        ar = [r for r in rows if r["arm"] == arm]
        per_k = {}
        for k in KS:
            c = [r["success_counts"][str(k)] for r in ar]
            m = [r["n_coalitions"] for r in ar]
            per_k[str(k)] = {"rate": sum(c) / sum(m), "n_coalitions": sum(m), "n_seeds": len(ar),
                             "seed_rate_min": min(a / b for a, b in zip(c, m)),
                             "seed_rate_max": max(a / b for a, b in zip(c, m))}
        stats[arm] = per_k

    def rate(arm, k):
        return stats[arm][str(k)]["rate"]

    def code_clause(arm):
        return all(rate(arm, k) <= 0.02 for k in LOW_KS) and all(rate(arm, k) >= 0.5 for k in HIGH_KS)

    treat_code = code_clause("TREATMENT")
    null_clause = rate("CONTROL", 1) >= 0.5
    success = treat_code and null_clause
    failure = any(rate("TREATMENT", k) > 0.02 for k in LOW_KS) or rate("CONTROL", 1) < 0.5
    pc = rate("POSITIVE_CONTROL", 1) >= 0.99
    cheat = code_clause("CHEAT")
    nt = code_clause("NULL_TWIN")

    if not (pc and cheat):
        outcome = "INSTRUMENT_FAIL"
    elif nt:
        outcome = "CONFOUNDED"
    elif success and not failure:
        outcome = "SIGNAL"
    else:
        outcome = "NULL"

    meta = json.load(open(os.path.join(HERE, "run_meta.json")))
    anomalies = []
    for arm in ("CONTROL", "NULL_TWIN"):
        zc = sorted({r.get("zero_columns") for r in rows if r["arm"] == arm})
        if any(z for z in zc):
            anomalies.append(f"{arm}: parity matrix has zero columns {zc}")
    if not treat_code:
        bad_low = [k for k in LOW_KS if rate("TREATMENT", k) > 0.02]
        bad_high = [k for k in HIGH_KS if rate("TREATMENT", k) < 0.5]
        anomalies.append(f"TREATMENT code clause fails: low-k violations {bad_low}, high-k shortfalls {bad_high}")

    tr = {k: round(rate("TREATMENT", k), 4) for k in KS}
    notes = (f"BCH(31,16) with verified d=7 (covering radius {meta['bch_covering_radius']}), exact "
             f"nearest-codeword decoding, exhaustive 2^k coalition search, 4000 coalitions per k. "
             f"TREATMENT manipulation rate by k: {tr}. CONTROL random-parity k=1 rate "
             f"{rate('CONTROL', 1):.4f}; NULL_TWIN k=1 rate {rate('NULL_TWIN', 1):.4f}; "
             f"POSITIVE_CONTROL k=1 rate {rate('POSITIVE_CONTROL', 1):.4f}. Outcome {outcome} "
             f"by the PREREG class rules applied in code.")

    out = {
        "triplicateId": "HT-321a8fd8e0", "world": "W1", "outcome": outcome,
        "statistics": stats,
        "criterion_as_applied": (
            "Pooled rate over 20 seeds x 200 coalitions per k. SUCCESS: TREATMENT rate <= 0.02 for "
            "every k in 1..3 AND >= 0.5 for every k in 4..8, AND CONTROL (random-parity) rate >= 0.5 "
            "at k=1. FAILURE: TREATMENT rate > 0.02 at any k<=3 or CONTROL rate < 0.5 at k=1. "
            "Null twin meets success = code clause holds on NULL_TWIN. Positive control detected = "
            "POSITIVE_CONTROL (16-agent direct rule) rate at k=1 >= 0.99. Cheat detected = code "
            "clause holds on CHEAT."),
        "success_criterion_met": success, "failure_criterion_met": failure,
        "positive_control_detected": pc, "cheat_detected": cheat,
        "null_twin_meets_success": nt,
        "stupid_explanations_status": [
            {"text": "the threshold is exactly the textbook decoding radius, so nothing new",
             "addressed_by_this_run": False,
             "how": "Not addressable: the observed step location is exactly what the unique-decoding "
                    "radius floor((d-1)/2)=3 predicts; the run confirms rather than distinguishes."},
            {"text": "restricting coalition search to own symbols guarantees the result",
             "addressed_by_this_run": False,
             "how": "Coalitions alter only their own symbols by construction (spec); no arm relaxes it."},
            {"text": "majority/repetition voting would show the same robustness",
             "addressed_by_this_run": False,
             "how": "No repetition/majority arm in the spec; not run."}],
        "anomalies": anomalies,
        "core_minutes": meta["core_minutes"],
        "attempts": meta["attempts"],
        "notes": notes,
    }
    json.dump(out, open(os.path.join(HERE, "OUTCOME.json"), "w"), indent=1)
    print(outcome, json.dumps({a: {k: round(v["rate"], 4) for k, v in s.items()} for a, s in stats.items()}))


if __name__ == "__main__":
    main()
