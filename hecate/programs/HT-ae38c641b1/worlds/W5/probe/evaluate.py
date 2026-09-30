"""HT-ae38c641b1 / W5 probe evaluator. Writes probe/OUTCOME.json.

Step 1: recompute control clause values from probe/rows.jsonl and compare the
attainable / discriminating / cheat status with the frozen ATTAINABILITY.json.
Any difference -> INSTRUMENT_FAIL (reproducibility), stop.
Step 2: apply frozen success and failure clauses; outcome decided in code
(precedence in NOTES.md, reading 4).
"""
import json, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WDIR = os.path.dirname(HERE)
SPEC = json.load(open(os.path.join(WDIR, "spec.json")))
ATT = json.load(open(os.path.join(WDIR, "ATTAINABILITY.json")))
ROWS = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"))]
SEEDS = SPEC["seeds"]
CL = {c["id"]: c for c in SPEC["success_clauses"] + SPEC["failure_clauses"]}
OPS = {">=": lambda a, b: a >= b, "<": lambda a, b: a < b}


def col(arm, k):
    v = {r["seed"]: r[k] for r in ROWS if r["arm"] == arm}
    assert sorted(v) == SEEDS, (arm, sorted(v))
    return [v[s] for s in SEEDS]


def mean(arm, k):
    return float(np.mean(col(arm, k)))


def meets(cid, x):
    c = CL[cid]
    return bool(OPS[c["comparison"]](x, c["threshold"]))


def stupid(anoms_ctx):
    s = anoms_ctx
    texts = SPEC["stupid_explanations"]
    how = [
        (True, "signed A4 averaged over 20 seeds; treatment-matched twins read "
               f"S1 {s['twin_V']:.3f}, S2 {s['twin_Vrot']:.3f}; per-seed V A4(0) SD {s['sd_V']:.3f}"),
        (True, f"w-weighted statistic; mean w V {s['w_V']:.3f}, V_rot {s['w_Vrot']:.3f}"),
        (True, f"F3 statistic (mean V accepted fraction) = {s['accV']:.4f}; V_rot {s['accVrot']:.4f}"),
        (True, f"V_rot read at world axes A4(0) = {s['F2']:.3f} (F2) and twins at world axes "
               f"{s['twin_V']:.3f}; PC_ROT at world axes {s['pcrot_w']:.3f}"),
        (False, "diagnostic only: median rho(|A|)/rho(A) V "
                f"{s['ar_V']:.3f}, V_rot {s['ar_Vrot']:.3f}, twin {s['ar_twin']:.3f}; "
                "no arm varies the Kleene budget, so budget vs domain geometry is not separated by this run"),
    ]
    return [dict(text=t, addressed_by_this_run=h[0], how=h[1]) for t, h in zip(texts, how)]


def main():
    meta_p = os.path.join(HERE, "run_meta.json")
    cpu = json.load(open(meta_p))["cpu_core_seconds"] if os.path.exists(meta_p) else None
    TH = 0.40
    out = dict(triplicateId=SPEC["triplicateId"], world=SPEC["id"], attempts=1,
               core_minutes=None if cpu is None else round(cpu / 60.0, 3), anomalies=[])
    # ---- step 1: control reproducibility ----
    s1p, s1t = mean("POSITIVE_CONTROL", "A4_axes0"), mean("NULL_TWIN", "A4_axes0")
    s2p, s2t = mean("POSITIVE_CONTROL_ROT", "A4_axes22_5"), mean("NULL_TWIN", "A4_axes22_5")
    c1, c2 = mean("CHEAT", "A4_axes0"), mean("CHEAT", "A4_axes22_5")
    rerun = {"S1": dict(positive_value=s1p, twin_value=s1t, attainable=s1p >= TH, discriminating=s1t < TH),
             "S2": dict(positive_value=s2p, twin_value=s2t, attainable=s2p >= TH, discriminating=s2t < TH)}
    cheat_det = c1 >= TH and c2 >= TH
    repro = []
    ok = True
    for fc in ATT["clauses"]:
        r = rerun[fc["id"]]
        same = r["attainable"] == fc["attainable"] and r["discriminating"] == fc["discriminating"]
        ok &= same
        repro.append(dict(id=fc["id"], frozen_positive=fc["positive_value"], rerun_positive=r["positive_value"],
                          frozen_twin=fc["twin_value"], rerun_twin=r["twin_value"],
                          frozen_status=[fc["attainable"], fc["discriminating"]],
                          rerun_status=[r["attainable"], r["discriminating"]], status_match=same,
                          max_abs_delta=max(abs(fc["positive_value"] - r["positive_value"]),
                                            abs(fc["twin_value"] - r["twin_value"]))))
    ok &= cheat_det == ATT["cheat_detected"]
    repro.append(dict(id="CHEAT", frozen=ATT["cheat_detected"], rerun=cheat_det, cheat_values=[c1, c2]))
    pos_det = bool(rerun["S1"]["attainable"] and rerun["S2"]["attainable"])
    out.update(positive_control_detected=pos_det, cheat_detected=bool(cheat_det))
    stats = dict(control_reproducibility=repro)
    out["statistics"] = stats
    if not ok:
        out.update(outcome="INSTRUMENT_FAIL", null_twin_meets_success=None,
                   criterion_as_applied="control reproducibility check failed; treatment not read",
                   stupid_explanations_status=[dict(text=t, addressed_by_this_run=False, how="not read")
                                               for t in SPEC["stupid_explanations"]],
                   notes="INSTRUMENT_FAIL (reproducibility): rerun control status differs from ATTAINABILITY.json")
        json.dump(out, open(os.path.join(HERE, "OUTCOME.json"), "w"), indent=1)
        print(json.dumps(out, indent=1)); return
    # ---- step 2: treatment clauses ----
    S1 = mean("V", "A4_axes0"); S2 = mean("V_rot", "A4_axes22_5")
    F2 = mean("V_rot", "A4_axes0"); F3 = mean("V", "mean_accept")
    tV = mean("NULL_TWIN_V", "A4_axes0"); tR = mean("NULL_TWIN_VROT", "A4_axes22_5")
    res = dict(S1=meets("S1", S1), S2=meets("S2", S2), F1=meets("F1", S1), F2=meets("F2", F2), F3=meets("F3", F3))
    twin_meets = bool(tV >= TH or tR >= TH)
    stats.update(
        clause_values=dict(S1=S1, S2=S2, F1=S1, F2=F2, F3=F3), clause_met=res,
        twin_values=dict(NULL_TWIN_V_A4_0=tV, NULL_TWIN_VROT_A4_22_5=tR),
        per_seed=dict(V_A4_0=col("V", "A4_axes0"), V_rot_A4_22_5=col("V_rot", "A4_axes22_5"),
                      V_rot_A4_0=col("V_rot", "A4_axes0")),
        sd_of_seed_mean=dict(V_A4_0=float(np.std(col("V", "A4_axes0"), ddof=1) / math.sqrt(len(SEEDS))),
                             V_rot_A4_22_5=float(np.std(col("V_rot", "A4_axes22_5"), ddof=1) / math.sqrt(len(SEEDS)))),
        diagnostics={arm: dict(A4_axes0=mean(arm, "A4_axes0"), A4_axes22_5=mean(arm, "A4_axes22_5"),
                               A8_axes0=mean(arm, "A8_axes0"), mean_w=mean(arm, "mean_w"),
                               median_lam=mean(arm, "median_lam"), median_abs_ratio=mean(arm, "median_abs_ratio"),
                               mean_accept=mean(arm, "mean_accept"))
                     for arm in ("V", "V_rot", "NULL_TWIN_V", "NULL_TWIN_VROT", "POSITIVE_CONTROL",
                                 "POSITIVE_CONTROL_ROT", "NULL_TWIN")},
        twin_accept_gap=dict(V=mean("NULL_TWIN_V", "mean_abs_accept_gap"),
                             V_rot=mean("NULL_TWIN_VROT", "mean_abs_accept_gap")))
    spec_reading = None
    if not pos_det or not cheat_det:
        outcome, why = "INSTRUMENT_FAIL", "positive or cheat control not detected"
    elif res["F3"]:
        outcome, why = "INSTRUMENT_FAIL", "F3 met: verifier froze evolution; reading invalid per spec"
    elif twin_meets:
        outcome, why = "CONFOUNDED", "treatment-matched null twin meets a success clause"
    elif res["S1"] and res["S2"] and not res["F1"] and not res["F2"]:
        outcome, why = "SIGNAL", "S1 and S2 met, no failure clause, twins below, controls detected"
    else:
        outcome = "NULL"
        fired = [k for k in ("F1", "F2") if res[k]]
        why = "success criterion not met" + (f"; failure clauses met: {fired}" if fired else "")
        if not fired and any(0.15 <= v < TH for v in (S1, S2)):
            spec_reading = "INCONCLUSIVE band per spec (0.15 <= A4 < 0.40), not a falsification of M2"
        elif res["F1"]:
            spec_reading = "F1: M2's 4-fold axis imprint falsified in this world"
    stats["spec_reading"] = spec_reading
    for arm in ("NULL_TWIN_V", "NULL_TWIN_VROT"):
        g = mean(arm, "mean_abs_accept_gap")
        if g > 0.1:
            out["anomalies"].append(f"{arm} acceptance-match gap {g:.3f} > 0.1")
    ctx = dict(twin_V=tV, twin_Vrot=tR, sd_V=float(np.std(col("V", "A4_axes0"), ddof=1)),
               w_V=mean("V", "mean_w"), w_Vrot=mean("V_rot", "mean_w"), accV=F3,
               accVrot=mean("V_rot", "mean_accept"), F2=F2,
               pcrot_w=mean("POSITIVE_CONTROL_ROT", "A4_axes0"),
               ar_V=mean("V", "median_abs_ratio"), ar_Vrot=mean("V_rot", "median_abs_ratio"),
               ar_twin=mean("NULL_TWIN_V", "median_abs_ratio"))
    out.update(outcome=outcome, null_twin_meets_success=twin_meets,
               criterion_as_applied=("S1: mean_seeds A4(0) in V >= 0.40; S2: mean_seeds A4(22.5deg) in V_rot >= 0.40; "
                                     "F1: mean A4(0) in V < 0.15; F2: mean A4(0) in V_rot >= 0.40; "
                                     "F3: mean V accepted fraction < 0.02; twins matched per generation to V (S1) "
                                     "and V_rot (S2); precedence repro > controls > F3 > twin > S1&S2&!F1&!F2 > NULL"),
               stupid_explanations_status=stupid(ctx), notes=why)
    json.dump(out, open(os.path.join(HERE, "OUTCOME.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("outcome", "notes", "core_minutes")}, indent=1))
    print(json.dumps(stats["clause_values"]), json.dumps(stats["twin_values"]))


if __name__ == "__main__":
    main()
