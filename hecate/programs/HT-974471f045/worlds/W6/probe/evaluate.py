"""HT-974471f045 / W6 probe round 3 evaluator. Writes OUTCOME.json."""
import os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
WORLD = os.path.dirname(HERE)
sys.path.insert(0, WORLD)
import controls as C
import json
import numpy as np

TAG = sys.argv[1] if len(sys.argv) > 1 else "p1"
rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"), encoding="utf-8")]
rows = [r for r in rows if r.get("run") == TAG]
ATT = json.load(open(os.path.join(WORLD, "ATTAINABILITY.json"), encoding="utf-8"))
SPEC = json.load(open(os.path.join(WORLD, "spec.json"), encoding="utf-8"))
TH = {c["id"]: c["threshold"] for c in SPEC["success_clauses"]}
FTH = {c["id"]: c["threshold"] for c in SPEC["failure_clauses"]}
assert TH == C.THRESH, (TH, C.THRESH)
cpu = sum(r["cpu_seconds"] for r in rows if r["arm"] == "CPU")
arm = lambda a: [r for r in rows if r["arm"] == a]
mean = lambda a, k: float(np.mean([r[k] for r in arm(a)]))

# 1. reproducibility of controls vs frozen ATTAINABILITY.json
pc, tw, ch = (C.clause_values(rows, a) for a in ("POSITIVE_CONTROL", "NULL_TWIN", "CHEAT"))
repro, repro_ok = [], True
for c in ATT["clauses"]:
    k = c["id"]
    att = bool(pc[k] >= TH[k]); dis = not bool(tw[k] >= TH[k])
    ok = (att == c["attainable"]) and (dis == c["discriminating"])
    repro_ok &= ok
    repro.append(dict(id=k, positive_value=round(pc[k], 4), frozen_positive=c["positive_value"],
                      twin_value=round(tw[k], 4), frozen_twin=c["twin_value"],
                      abs_diff_pos=abs(round(pc[k], 4) - c["positive_value"]),
                      abs_diff_twin=abs(round(tw[k], 4) - c["twin_value"]),
                      attainable=att, discriminating=dis, status_matches=ok))

pos_det = all(pc[k] >= TH[k] for k in TH)
cheat_det = all(ch[k] >= TH[k] for k in TH)
twin_meets = all(tw[k] >= TH[k] for k in TH)
tr = C.clause_values(rows, "TREATMENT")
S = {k: bool(tr[k] >= TH[k]) for k in TH}
F = {"F1": bool(tr["S1"] < FTH["F1"]), "F2": bool(tr["S3"] < FTH["F2"])}

if not repro_ok:
    outcome = "INSTRUMENT_FAIL"
elif not (pos_det and cheat_det):
    outcome = "INSTRUMENT_FAIL"
elif twin_meets:
    outcome = "CONFOUNDED"
elif all(S.values()) and not any(F.values()):
    outcome = "SIGNAL"
else:
    outcome = "NULL"

stats = {}
if repro_ok:
    for a in ("TREATMENT", "NULL_TWIN", "CONTROL", "POSITIVE_CONTROL", "PERMUTED_TWIN", "CHEAT"):
        d = {k: round(mean(a, k), 4) for k in ("I_full", "I_perp", "I_ones")}
        d["I_perp_per_seed"] = [round(r["I_perp"], 4) for r in arm(a)]
        for k in ("tnr_mean", "max_unit_share_mean", "I_perp_norec"):
            if k in arm(a)[0]:
                d[k] = round(mean(a, k), 4)
        stats[a] = d
    stats["TREATMENT"].update(best_fit_g1=round(mean("TREATMENT", "best_fit_g1"), 4),
                              best_fit_g60=round(mean("TREATMENT", "best_fit_g60"), 4),
                              mean_fit_g60=round(mean("TREATMENT", "mean_fit_g60"), 4))
    stats["clause_values"] = {"TREATMENT": {k: round(v, 4) for k, v in tr.items()},
                              "POSITIVE_CONTROL": {k: round(v, 4) for k, v in pc.items()},
                              "NULL_TWIN": {k: round(v, 4) for k, v in tw.items()},
                              "CHEAT": {k: round(v, 4) for k, v in ch.items()}}
    stats["permuted_twin_S3_diag"] = round(mean("TREATMENT", "I_perp") - mean("PERMUTED_TWIN", "I_perp"), 4)

t_tnr = stats.get("TREATMENT", {}).get("tnr_mean")
se = [
 {"text": SPEC["stupid_explanations"][0], "addressed_by_this_run": False,
  "how": f"not ruled out: no clause separates collapse from an invariant functional; recorded rms(M_in)/0.3 of elites = {t_tnr} (gen-0 CONTROL {stats.get('CONTROL', {}).get('tnr_mean')}, twin {stats.get('NULL_TWIN', {}).get('tnr_mean')})"},
 {"text": SPEC["stupid_explanations"][1], "addressed_by_this_run": True,
  "how": f"diagnostic: elites re-measured on the same streams with recurrent W = 0: I_perp_norec = {stats.get('TREATMENT', {}).get('I_perp_norec')} vs I_perp {stats.get('TREATMENT', {}).get('I_perp')} (reservoir contribution, not a clause); norec > with-recurrence means the recurrence acts as noise and the decodable part is carried by the input template"},
 {"text": SPEC["stupid_explanations"][2], "addressed_by_this_run": True,
  "how": f"mean largest single-unit share of w_perp^2 = {stats.get('TREATMENT', {}).get('max_unit_share_mean')}; per-seed I_perp {stats.get('TREATMENT', {}).get('I_perp_per_seed')}; elites measured on 20 resamples x 5 elites x 6 seeds"},
 {"text": SPEC["stupid_explanations"][3], "addressed_by_this_run": True,
  "how": "analytic: any function of channels other than u2 has corr^2 <= 0.5 with u1 - u2; S1 threshold 0.60 sits above that ceiling, so an S1 pass cannot be single-channel; an S1 fail makes it moot"},
]

out = dict(
    triplicateId="HT-974471f045", world="W6", outcome=outcome, statistics=stats,
    criterion_as_applied=dict(
        success={k: {"statistic": [c for c in SPEC["success_clauses"] if c["id"] == k][0]["statistic"],
                     "comparison": ">=", "threshold": TH[k], "treatment_value": round(tr[k], 4), "met": S[k]} for k in TH},
        failure={"F1": {"statistic": "mean over 6 seeds of I_perp", "comparison": "<", "threshold": FTH["F1"],
                        "treatment_value": round(tr["S1"], 4), "met": F["F1"]},
                 "F2": {"statistic": "mean I_perp minus NULL_TWIN mean I_perp", "comparison": "<", "threshold": FTH["F2"],
                        "treatment_value": round(tr["S3"], 4), "met": F["F2"]}},
        rule="repro fail or PC/cheat undetected -> INSTRUMENT_FAIL; twin meets all S -> CONFOUNDED; all S and no F -> SIGNAL; else NULL",
        twin_used="NULL_TWIN (controls.drift_population, as frozen in ATTAINABILITY.json)"),
    control_reproducibility=dict(all_status_match=repro_ok, clauses=repro, frozen_cheat_detected=ATT["cheat_detected"]),
    positive_control_detected=pos_det, cheat_detected=cheat_det, null_twin_meets_success=twin_meets,
    stupid_explanations_status=se,
    anomalies=[],
    core_minutes=round(cpu / 60, 3),
    attempts=1,
    notes="See NOTES.md. Kept elites keep their one-life fitness (reading 1). PERMUTED_TWIN is diagnostic only. "
          "The spec's alternative_explanation (template collapse) is not distinguished by any clause; read the tnr beside the outcome.",
)
if repro_ok and stats["TREATMENT"]["tnr_mean"] > 3:
    out["anomalies"].append("elite template-to-noise ratio > 3: collapse reading plausible")
if repro_ok and stats["TREATMENT"]["best_fit_g60"] - stats["TREATMENT"]["I_full"] > 0.15:
    out["anomalies"].append(f"elite one-life fitness (best {stats['TREATMENT']['best_fit_g60']}) far above instrument I_full {stats['TREATMENT']['I_full']}: selection partly on lucky reservoir draws (kept elites keep their one-life fitness, NOTES reading 1)")
if repro_ok and stats["TREATMENT"].get("I_perp_norec", 0) > stats["TREATMENT"]["I_perp"]:
    out["anomalies"].append("treatment elites decode better with recurrent W removed: recurrence is noise to the selected readout")
if repro_ok and not S["S1"] and stats["TREATMENT"]["I_perp"] < 0.5:
    out["anomalies"].append("S1 fails below the 0.5 single-channel ceiling although S2 and S3 pass: selection found a partial decoder, not the invariant the positive control carries")
json.dump(out, open(os.path.join(HERE, "OUTCOME.json"), "w", encoding="utf-8"), indent=1)
print(json.dumps({k: out[k] for k in ("outcome", "positive_control_detected", "cheat_detected", "null_twin_meets_success", "core_minutes")}))
print(json.dumps(out["criterion_as_applied"], indent=1)); print(json.dumps(repro, indent=0))
