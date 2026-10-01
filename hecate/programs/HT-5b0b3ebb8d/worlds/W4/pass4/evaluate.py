"""HT-5b0b3ebb8d / W4 Pass 4 evaluator. See NOTES.md.

Reads pass4/rows.jsonl and the round-1 rows.jsonl (read only). Reports and
writes the positive/cheat control status FIRST; treatment statistics are
computed only if every control is detected. Writes PASS4_OUTCOME.json.
"""
import json
import os
import sys
import time

sys.dont_write_bytecode = True

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
R1 = os.path.dirname(HERE)
sys.path.insert(0, R1)
import evaluate as e1  # noqa: E402  round-1 evaluator: cmh, strata (unchanged)

OR_T, P_T = 1.5, 0.01      # PREREG
PC_RATE = 0.9              # round-1 spec positive-control rate
ATTEMPTS = 1               # runs of attack.py; changed only for crash/bug reruns (recorded in NOTES.md)
OUT = os.path.join(HERE, "PASS4_OUTCOME.json")


def load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8")]


def pooled(rows, attack, arm):
    return [dict(b, _disabled=r.get("disabled")) for r in rows
            if r.get("attack", "R1") == attack and r["arm"] == arm for b in r["beliefs"]]


def meets(s):
    o, p = s["or_mh"], s["p"]
    return bool(p is not None and np.isfinite(p) and not np.isnan(o) and o >= OR_T and p < P_T)


def fin(x):
    if isinstance(x, (float, np.floating)):
        x = float(x)
        return x if np.isfinite(x) else str(x)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, dict):
        return {str(k): fin(v) for k, v in x.items()}
    if isinstance(x, list):
        return [fin(v) for v in x]
    return x


def arr(B, k):
    return np.array([b[k] for b in B])


def visit_deciles(B):
    return e1.strata(arr(B, "visit").astype(float), 10)


def stat(B, strat):
    L, F = arr(B, "lucky"), arr(B, "fail")
    r = e1.cmh(L, F, strat)
    var_strata = int(sum(1 for k in np.unique(strat) if 0 < F[strat == k].mean() < 1))
    r.update(n=len(B), n_lucky=int(L.sum()), n_grounded=int((L == 0).sum()),
             fail_rate_lucky=float(F[L == 1].mean()) if (L == 1).any() else None,
             fail_rate_grounded=float(F[L == 0].mean()) if (L == 0).any() else None,
             strata_total=int(len(np.unique(strat))), strata_with_outcome_variance=var_strata)
    return r


def endpoint_flag(B):
    out = []
    for b in B:
        di = [1, 2, 3] if b["_disabled"] == "A" else [4, 5, 6]
        out.append(int(b["s"] in di or b["t"] in di))
    return np.array(out)


def orig_strata(B):
    return visit_deciles(B) * 10 + endpoint_flag(B)


def alt_strata(B):
    return visit_deciles(B) * 100 + arr(B, "support_len")


def planted_check(B):
    planted = [b for b in B if b["planted"]]
    flagged = [b for b in planted if b["lucky"] == 1]
    frac = len(flagged) / len(planted) if planted else 0.0
    fr = float(np.mean([b["fail"] for b in flagged])) if flagged else 0.0
    return dict(n_planted=len(planted), n_flagged=len(flagged), flagged_fraction=frac,
                flagged_fail_rate=fr, detected=bool(planted and frac >= PC_RATE and fr >= PC_RATE))


def main():
    t0 = time.process_time()
    rows = load(os.path.join(HERE, "rows.jsonl"))
    meta = [r for r in rows if r["arm"] == "_META"][0]
    rows = [r for r in rows if r["arm"] != "_META"]
    r1 = [dict(r, attack="R1") for r in load(os.path.join(R1, "rows.jsonl")) if r["arm"] != "_META"]
    seeds = {f"{a}/{m}": len({r["seed"] for r in rows if r["attack"] == a and r["arm"] == m})
             for a in ("R", "ALT") for m in ("TREATMENT", "NULL_TWIN", "POSITIVE_CONTROL", "CHEAT")}

    # ---------------- controls FIRST
    R_pc = planted_check(pooled(rows, "R", "POSITIVE_CONTROL"))
    R_ch_B = pooled(rows, "R", "CHEAT")
    R_ch = stat(R_ch_B, visit_deciles(R_ch_B))
    A_pc = planted_check(pooled(rows, "ALT", "POSITIVE_CONTROL"))
    A_ch_B = pooled(rows, "ALT", "CHEAT")
    A_ch = stat(A_ch_B, alt_strata(A_ch_B))
    O_ch_B = pooled(r1, "R1", "CHEAT")
    O_ch = stat(O_ch_B, orig_strata(O_ch_B))
    controls = {
        "R": {"positive": R_pc, "cheat": dict(R_ch, detected=meets(R_ch))},
        "ALT": {"positive": A_pc, "cheat": dict(A_ch, detected=meets(A_ch))},
        "ORIG_analysis": {"cheat": dict(O_ch, detected=bool(meets(O_ch) and O_ch["strata_with_outcome_variance"] > 0))},
    }
    pos_ok = bool(R_pc["detected"] and A_pc["detected"])
    cheat_ok = bool(controls["R"]["cheat"]["detected"] and controls["ALT"]["cheat"]["detected"]
                    and controls["ORIG_analysis"]["cheat"]["detected"])
    print("CONTROLS (reported before any treatment statistic):")
    print(json.dumps(fin({"R_positive": R_pc["detected"], "R_cheat": controls["R"]["cheat"]["detected"],
                          "ALT_positive": A_pc["detected"], "ALT_cheat": controls["ALT"]["cheat"]["detected"],
                          "ORIG_cheat": controls["ORIG_analysis"]["cheat"]["detected"],
                          "R_planted": [R_pc["n_flagged"], R_pc["n_planted"], R_pc["flagged_fail_rate"]],
                          "ALT_planted": [A_pc["n_flagged"], A_pc["n_planted"], A_pc["flagged_fail_rate"]]}), indent=1))

    out = {"triplicateId": "HT-5b0b3ebb8d", "world": "W4",
           "R": {"reproduced": False, "stats": {}}, "ORIG": {"fired": False, "stats": {}},
           "ALT": {"status": "NOT_ELIGIBLE", "stats": {}},
           "controls": {"positive_detected": pos_ok, "cheat_detected": cheat_ok, "detail": fin(controls)},
           "predicate": "PARK", "anomalies": [], "core_minutes": None, "attempts": ATTEMPTS, "notes": "",
           "seeds_per_attack_arm": seeds}
    anomalies = out["anomalies"]
    for k, n in seeds.items():
        if n != 60:
            anomalies.append(f"{k} has {n} seeds, expected 60")

    if not (pos_ok and cheat_ok):
        out["notes"] = "Control(s) not detected; no treatment statistic computed (one repair allowed per PREREG)."
    else:
        # ---------------- R
        T = pooled(rows, "R", "TREATMENT")
        sT = stat(T, visit_deciles(T))
        NT = pooled(rows, "R", "NULL_TWIN")
        sN = stat(NT, visit_deciles(NT))
        reproduced = bool(meets(sT) and not meets(sN))
        out["R"] = {"reproduced": reproduced, "stats": fin({"TREATMENT": sT, "NULL_TWIN": sN,
                                                            "null_twin_meets": meets(sN)})}

        # ---------------- ORIG (primary: round-1 rows; secondary: R rows)
        def orig(B):
            s = stat(B, orig_strata(B))
            no_var = s["strata_with_outcome_variance"] == 0
            o, p = s["or_mh"], s["p"]
            or_low = bool(np.isnan(o) or o < OR_T)
            p_high = bool(p is None or np.isnan(p) or p >= P_T)
            E = endpoint_flag(B)
            F = arr(B, "fail")
            s.update(no_stratum_with_outcome_variance=no_var, or_below=or_low, p_not_below=p_high,
                     fired=bool(no_var or or_low or p_high),
                     fail_rate_endpoint_in=float(F[E == 1].mean()) if (E == 1).any() else None,
                     fail_rate_endpoint_out=float(F[E == 0].mean()) if (E == 0).any() else None,
                     n_endpoint_in=int(E.sum()))
            return s
        o1 = orig(pooled(r1, "R1", "TREATMENT"))
        oR = orig(T)
        out["ORIG"] = {"fired": o1["fired"], "stats": fin({"primary_round1_rows": o1, "secondary_R_rows": oR})}
        if o1["fired"] != oR["fired"]:
            anomalies.append(f"ORIG disagrees between round-1 rows (fired={o1['fired']}) and R rows (fired={oR['fired']})")

        # ---------------- ALT
        AT = pooled(rows, "ALT", "TREATMENT")
        aT = stat(AT, alt_strata(AT))
        AN = pooled(rows, "ALT", "NULL_TWIN")
        aN = stat(AN, alt_strata(AN))
        if np.isnan(aT["or_mh"]) or aT["p"] is None or np.isnan(aT["p"]):
            alt_status = "NOT_ELIGIBLE"
        elif meets(aT) and not meets(aN):
            alt_status = "PASS"
        else:
            alt_status = "FAIL"
        # diagnostics (not in predicate)
        E = arr(AT, "endpoint_in_disabled"); F = arr(AT, "fail"); L = arr(AT, "lucky")
        RF = arr(AT, "reach_fail")
        diag = dict(
            fail_rate_endpoint_in_disabled=float(F[E == 1].mean()) if (E == 1).any() else None,
            fail_rate_endpoint_not_in=float(F[E == 0].mean()) if (E == 0).any() else None,
            endpoint_x_decile_strata=stat(AT, orig_strata(AT)),
            reach_fail_rate_lucky=float(RF[L == 1].mean()), reach_fail_rate_grounded=float(RF[L == 0].mean()),
            reach_fail_overall=float(RF.mean()),
            support_len_mean_lucky=float(arr(AT, "support_len")[L == 1].mean()),
            support_len_mean_grounded=float(arr(AT, "support_len")[L == 0].mean()),
            visit_decile_only=stat(AT, visit_deciles(AT)),
            witness_len_x_decile=stat(AT, visit_deciles(AT) * 100 + arr(AT, "witness_len")),
            witness_hit_rate_lucky=float(arr(AT, "witness_hit")[L == 1].mean()),
            witness_hit_rate_grounded=float(arr(AT, "witness_hit")[L == 0].mean()),
        )
        out["ALT"] = {"status": alt_status, "stats": fin({"TREATMENT": aT, "NULL_TWIN": aN,
                                                          "null_twin_meets": meets(aN), "diagnostics": diag})}

        # ---------------- predicate (PREREG)
        if alt_status != "PASS":
            pred = "PARK"
        elif reproduced and not o1["fired"]:
            pred = "SURVIVES"
        else:
            pred = "ORIG_FOSSIL_ALT_PASS"
        out["predicate"] = pred
        out["notes"] = (
            f"R: OR {fin(sT['or_mh'])}, p {fin(sT['p'])} (null twin OR {fin(sN['or_mh'])}) -> reproduced={reproduced}. "
            f"ORIG (round-1 rows, endpoint x decile): OR {fin(o1['or_mh'])}, p {fin(o1['p'])}, strata with outcome "
            f"variance {o1['strata_with_outcome_variance']}/{o1['strata_total']} -> fired={o1['fired']}. "
            f"ALT: OR {fin(aT['or_mh'])}, p {fin(aT['p'])}, null twin OR {fin(aN['or_mh'])}, p {fin(aN['p'])} -> {alt_status}. "
            f"Predicate {pred}. Numbers only; toy configuration.")

    ev_cpu = time.process_time() - t0
    out["core_minutes"] = round((meta["attack_cpu_seconds"] + ev_cpu) / 60.0, 4)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(fin(out), f, indent=1)
    print(json.dumps(fin({k: out[k] for k in ("predicate", "notes", "anomalies", "core_minutes")}), indent=1))


if __name__ == "__main__":
    main()
