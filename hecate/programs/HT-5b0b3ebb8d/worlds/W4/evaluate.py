"""HT-5b0b3ebb8d / W4 evaluator. Reads rows.jsonl only; writes OUTCOME.json."""
import json
import os
import time

import numpy as np
from scipy.stats import chi2

HERE = os.path.dirname(os.path.abspath(__file__))
OR_SUCCESS, P_SUCCESS = 1.5, 0.01
OR_FAIL, P_FAIL = 1.2, 0.1
PC_RATE = 0.9
ATTEMPTS = 1  # every run of world.py counts; updated by hand only for crash/bug reruns (see notes)


def strata(vals, nq):
    edges = np.quantile(vals, np.linspace(0, 1, nq + 1)[1:-1])
    return np.searchsorted(edges, vals, side="right")


def cmh(lucky, fail, strat):
    num = den = 0.0
    sa = sE = sV = 0.0
    used = 0
    for k in np.unique(strat):
        m = strat == k
        L, F = lucky[m], fail[m]
        a = float(np.sum((L == 1) & (F == 1)))
        b = float(np.sum((L == 1) & (F == 0)))
        c = float(np.sum((L == 0) & (F == 1)))
        d = float(np.sum((L == 0) & (F == 0)))
        n = a + b + c + d
        n1, n0, m1, m0 = a + b, c + d, a + c, b + d
        if n1 == 0 or n0 == 0 or n < 2:
            continue
        used += 1
        num += a * d / n
        den += b * c / n
        sa += a
        sE += n1 * m1 / n
        sV += n1 * n0 * m1 * m0 / (n * n * (n - 1))
    orr = num / den if den > 0 else (float("inf") if num > 0 else float("nan"))
    if sV > 0:
        x2 = (max(abs(sa - sE) - 0.5, 0.0)) ** 2 / sV
        p = float(chi2.sf(x2, 1))
    else:
        x2, p = float("nan"), float("nan")
    return dict(or_mh=orr, p=p, chi2=x2, strata_used=used)


def pooled(rows, arm):
    B = [b for r in rows if r["arm"] == arm for b in r["beliefs"]]
    return B


def arm_stats(B, nq=10):
    lucky = np.array([b["lucky"] for b in B])
    fail = np.array([b["fail"] for b in B])
    vis = np.array([b["visit"] for b in B])
    st = strata(vis, nq)
    res = cmh(lucky, fail, st)
    res.update(n=len(B), n_lucky=int(lucky.sum()), n_grounded=int((lucky == 0).sum()),
               fail_rate_lucky=float(fail[lucky == 1].mean()) if (lucky == 1).any() else None,
               fail_rate_grounded=float(fail[lucky == 0].mean()) if (lucky == 0).any() else None)
    return res


def meets_success(s):
    o, p = s["or_mh"], s["p"]
    return bool(np.isfinite(p) and not np.isnan(o) and o >= OR_SUCCESS and p < P_SUCCESS)


def meets_failure(s):
    o, p = s["or_mh"], s["p"]
    return bool((not np.isnan(o) and o < OR_FAIL) or (np.isnan(p) or p > P_FAIL))


def fin(x):
    if isinstance(x, float) and not np.isfinite(x):
        return str(x)
    return x


def main():
    t0 = time.process_time()
    rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"), encoding="utf-8")]
    meta = [r for r in rows if r["arm"] == "_META"][0]
    rows = [r for r in rows if r["arm"] != "_META"]
    seeds = {a: len({r["seed"] for r in rows if r["arm"] == a}) for a in
             ("TREATMENT", "CONTROL", "NULL_TWIN", "POSITIVE_CONTROL", "CHEAT")}

    T = pooled(rows, "TREATMENT")
    st_T = arm_stats(T)
    st_NT = arm_stats(pooled(rows, "NULL_TWIN"))
    st_CH = arm_stats(pooled(rows, "CHEAT"))
    PCB = pooled(rows, "POSITIVE_CONTROL")
    st_PC = arm_stats(PCB)
    planted = [b for b in PCB if b["planted"]]
    flagged = [b for b in planted if b["lucky"] == 1]
    pc_flag_frac = len(flagged) / len(planted) if planted else 0.0
    pc_fail = float(np.mean([b["fail"] for b in flagged])) if flagged else 0.0
    pc_detected = bool(planted and pc_flag_frac >= PC_RATE and pc_fail >= PC_RATE)
    st_PC.update(n_planted=len(planted), n_planted_flagged=len(flagged),
                 planted_flagged_fraction=pc_flag_frac, planted_flagged_fail_rate=pc_fail)

    # CONTROL: visit deciles only, grounding ignored
    C = pooled(rows, "CONTROL")
    vis = np.array([b["visit"] for b in C])
    fail = np.array([b["fail"] for b in C])
    lk = np.array([b["lucky_ignored"] for b in C])
    dec = strata(vis, 10)
    per_dec = {int(k): dict(n=int((dec == k).sum()), fail_rate=float(fail[dec == k].mean()),
                            lucky_frac=float(lk[dec == k].mean())) for k in np.unique(dec)}
    a = float(((lk == 1) & (fail == 1)).sum()); b_ = float(((lk == 1) & (fail == 0)).sum())
    c = float(((lk == 0) & (fail == 1)).sum()); d = float(((lk == 0) & (fail == 0)).sum())
    crude = (a * d) / (b_ * c) if b_ * c > 0 else float("inf")
    from scipy.stats import spearmanr
    rho, rho_p = spearmanr(vis, fail)
    st_C = dict(n=len(C), fail_rate=float(fail.mean()), per_visit_decile=per_dec,
                crude_or_lucky_vs_grounded=crude, spearman_visit_vs_fail=float(rho),
                spearman_p=float(rho_p))

    T_success = meets_success(st_T)
    T_failure = meets_failure(st_T)
    cheat_detected = meets_success(st_CH)
    nt_success = meets_success(st_NT)

    if not (pc_detected and cheat_detected):
        outcome = "INSTRUMENT_FAIL"
    elif nt_success:
        outcome = "CONFOUNDED"
    elif T_success:
        outcome = "SIGNAL"
    else:
        outcome = "NULL"

    # prespecified diagnostics
    Tl = [x for x in T if x["lucky"]]; Tg = [x for x in T if not x["lucky"]]
    frac = lambda L, k: float(np.mean([x[k] for x in L])) if L else None
    fine = arm_stats(T, nq=20)
    stupid = [
        dict(text="lucky beliefs concentrate on the disabled mechanism by construction of the shift",
             addressed_by_this_run=False,
             how=f"described only: witness touches disabled-mechanism interior in "
                 f"{frac(Tl,'touches_disabled')} of lucky vs {frac(Tg,'touches_disabled')} of grounded beliefs; not stratified on it"),
        dict(text="witness selection picks shortest paths that happen to use abduced edges",
             addressed_by_this_run=False,
             how=f"only one witness rule run; lucky witnesses using an abduced edge {frac(Tl,'uses_abduced')}, "
                 f"fabricated edge {frac(Tl,'uses_fabricated')}; grounded: abduced {frac(Tg,'uses_abduced')}, "
                 f"fabricated {frac(Tg,'uses_fabricated')}"),
        dict(text="visit-count strata too coarse to remove the confound",
             addressed_by_this_run=True,
             how=f"prespecified 20-quantile strata: OR_MH={fin(fine['or_mh'])}, p={fin(fine['p'])} "
                 f"(10-decile: OR_MH={fin(st_T['or_mh'])}, p={fin(st_T['p'])})"),
    ]
    anomalies = []
    for arm, n in seeds.items():
        if n < 60:
            anomalies.append(f"{arm} has only {n} seeds")
    if st_T["n_lucky"] < 30:
        anomalies.append(f"few lucky treatment beliefs: {st_T['n_lucky']}")
    if st_PC["n_planted"] != 300:
        anomalies.append(f"planted beliefs {st_PC['n_planted']} != 300 (some not true/verified)")

    ev_cpu = time.process_time() - t0
    core_min = (meta["world_cpu_seconds"] + ev_cpu) / 60.0

    def clean(d):
        return {k: (clean(v) if isinstance(v, dict) else fin(v)) for k, v in d.items()}

    out = {
        "triplicateId": "HT-5b0b3ebb8d", "world": "W4", "outcome": outcome,
        "statistics": {"TREATMENT": clean(st_T), "NULL_TWIN": clean(st_NT), "CHEAT": clean(st_CH),
                       "POSITIVE_CONTROL": clean(st_PC), "CONTROL": clean(st_C),
                       "TREATMENT_20_strata": clean(fine), "seeds_per_arm": seeds},
        "criterion_as_applied": (
            "Mantel-Haenszel common OR of post-shift failure, lucky vs grounded, stratified by pooled "
            "visit-count deciles (mean visits over witness states), CMH chi2 with 0.5 continuity "
            "correction, 60 seeds x 30 formulas (true & verified beliefs only). Success: OR>=1.5 and "
            "p<0.01. Failure criterion: OR<1.2 or p>0.1. Not-success -> NULL per PREREG."),
        "treatment_meets_success": T_success, "treatment_meets_failure_criterion": T_failure,
        "positive_control_detected": pc_detected, "cheat_detected": cheat_detected,
        "null_twin_meets_success": nt_success,
        "stupid_explanations_status": stupid, "anomalies": anomalies,
        "core_minutes": round(core_min, 4), "attempts": ATTEMPTS,
        "notes": "",
    }
    L, G = st_T["fail_rate_lucky"], st_T["fail_rate_grounded"]
    out["notes"] = (
        f"Outcome {outcome}. Treatment: {st_T['n']} true verified beliefs ({st_T['n_lucky']} lucky, "
        f"{st_T['n_grounded']} grounded); post-shift failure rate lucky {L}, grounded {G}; "
        f"MH OR {fin(st_T['or_mh'])}, p {fin(st_T['p'])}. Null twin MH OR {fin(st_NT['or_mh'])}, p {fin(st_NT['p'])}. "
        f"Cheat OR {fin(st_CH['or_mh'])}. Positive control: {len(flagged)}/{len(planted)} planted flagged, "
        f"failure rate among flagged {pc_fail}. Numbers only; no claim beyond this toy configuration.")
    with open(os.path.join(HERE, "OUTCOME.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: out[k] for k in ("outcome", "notes", "anomalies", "core_minutes")}, indent=1))


if __name__ == "__main__":
    main()
