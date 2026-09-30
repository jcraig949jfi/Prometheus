"""Evaluate rows.jsonl -> OUTCOME.json (round-1 fields; outcome by PREREG classes)."""
import json, time
import numpy as np
import criteria

t0 = time.process_time()
rows = [json.loads(l) for l in open("rows.jsonl")]
by = {}
for r in rows:
    by.setdefault(r["arm"], []).append(r)

pos = criteria.positive_meets(by["POSITIVE_CONTROL"])
ch = criteria.success(by["CHEAT"])
nt = criteria.success(by["NULL_TWIN"])
tr = criteria.success(by["TREATMENT"])
fl = criteria.failure(by["TREATMENT"])
tr3 = criteria.success(by["TREATMENT"], tol="0.001")
fl3 = criteria.failure(by["TREATMENT"], tol="0.001")

if not (pos["meets"] and ch["success"]):
    outcome = "INSTRUMENT_FAIL"
elif nt["success"]:
    outcome = "CONFOUNDED"
elif tr["success"] and not fl["failure"]:
    outcome = "SIGNAL"
else:
    outcome = "NULL"

def arm_bonds(arm, key, c=None):
    v = [cd[key]["1e-06"] for r in by[arm] for cd in r["conds"]
         if cd["lam"] >= 1 and (c is None or cd["c"] == c)]
    return {"mean": float(np.mean(v)), "min": int(min(v)), "max": int(max(v))}

per_r = {}
for c in (0.5, 2.0):
    for r_ in (1, 2, 4):
        for lam in (0.1, 0.3, 1.0, 3.0, 10.0):
            v = [(cd["z"]["1e-06"], cd["V"]["1e-06"], cd["tanh"]["1e-06"]) for r in by["TREATMENT"]
                 for cd in r["conds"] if cd["c"] == c and cd["r"] == r_ and cd["lam"] == lam]
            per_r[f"c{c:g}_r{r_}_lam{lam:g}"] = {"mean_bz": float(np.mean([a for a, _, _ in v])),
                                                 "mean_bV": float(np.mean([b for _, b, _ in v])),
                                                 "mean_btanh": float(np.mean([t for _, _, t in v]))}
zd = [cd["zdiag"] for r in by["TREATMENT"] for cd in r["conds"] if cd["lam"] >= 1]
zd_all = [cd["zdiag"] for r in by["TREATMENT"] for cd in r["conds"]]
mix = max(max(r["mixing_dist_P20"]) for r in by["TREATMENT"])
same_tol = (tr["success"] and not fl["failure"]) == (tr3["success"] and not fl3["failure"])

stupid = {
    "tolerance-dependent rank": {
        "status": "ruled_out" if same_tol else "not_ruled_out",
        "detail": f"verdict(success&!failure) at 1e-6={tr['success'] and not fl['failure']}, at 1e-3={tr3['success'] and not fl3['failure']}"},
    "exp underflow to zero creating spurious low rank": {
        "status": "ruled_out" if max(d["frac_lt_1e300"] for d in zd) == 0 else "not_ruled_out",
        "detail": f"log-domain solve; max frac normalised z<1e-300 at lam>=1 = {max(d['frac_lt_1e300'] for d in zd)}, all lam = {max(d['frac_lt_1e300'] for d in zd_all)}"},
    "lambda large makes z nearly constant": {
        "status": "measured_not_adjudicated",
        "detail": f"min rel_std(z) at lam>=1 = {min(d['rel_std'] for d in zd):.4f}; see per-cell means at lam=1 vs 10"},
    "passive dynamics mixing to stationarity erasing structure over 20 steps": {
        "status": "not_ruled_out" if mix < 1e-3 else "measured_not_adjudicated",
        "detail": f"max_i max|P_i^20 - pi| = {mix:.3e} (lazy 0.5 Dirichlet); no horizon sweep was specified"},
}
pilot = json.load(open("PILOT.json"))
cpu = (json.load(open("pilot_cpu.json"))["cpu_seconds"] + 6.23  # attempt-1 pilot cpu (logged)
       + json.load(open("world_cpu.json"))["cpu_seconds"] + (time.process_time() - t0))
out = {
    "triplicateId": "HT-2a8a3aedeb",
    "world": "W1",
    "outcome": outcome,
    "statistics": {"treatment_success": tr, "treatment_failure": fl,
                   "treatment_success_tol1e-3": tr3, "treatment_failure_tol1e-3": {"failure": fl3["failure"]},
                   "null_twin": nt, "cheat": ch, "positive": pos,
                   "bonds_lam_ge1": {"TREATMENT_z_c0.5": arm_bonds("TREATMENT", "z", 0.5),
                                     "TREATMENT_V_c0.5": arm_bonds("TREATMENT", "V", 0.5),
                                     "CONTROL_tanh_c0.5": arm_bonds("CONTROL", "tanh", 0.5),
                                     "CONTROL_quant_c0.5": arm_bonds("CONTROL", "quant", 0.5),
                                     "NULL_TWIN_z": arm_bonds("NULL_TWIN", "z"),
                                     "NULL_TWIN_V": arm_bonds("NULL_TWIN", "V"),
                                     "POSITIVE_z": arm_bonds("POSITIVE_CONTROL", "z"),
                                     "POSITIVE_V": arm_bonds("POSITIVE_CONTROL", "V")},
                   "treatment_cell_means": per_r},
    "criterion_as_applied": "tol 1e-6; c=0.5, lam in {1,3,10}; S1 per (r,lam) cell #seeds bond(z)<=bond(V)-1 >=8/10; S2 per cell #seeds bond(z)<=bond(tanh_centred)-1 >=7/10; S3 per lam Spearman(r,bond z) over 30 points >=0.6 (undefined=fail). Failure: any (c in {0.5,2}, r, lam>=1) cell with #bond(z)>=bond(V) >=5 or #bond(z) not < bond(tanh) >=5. SIGNAL needs success and not failure. See NOTES.md.",
    "positive_control_detected": pos["meets"],
    "cheat_detected": ch["success"],
    "null_twin_meets_success": nt["success"],
    "stupid_explanations_status": stupid,
    "anomalies": ["pilot attempt 1 failed: uncentred tanh(V/sd V) saturated to constant (bond 1) in every arm; one control repair (centring) applied before any treatment code existed",
                  "positive control S3 (Spearman over r) undefined since r does not enter q at c=0; carried by CHEAT"],
    "core_minutes": round(cpu / 60, 3),
    "attempts": {"pilot": pilot["attempt"], "phase2": 1},
    "notes": "Prompt probe_impl_v2 sha256 2021ed66...185e. Pilot pass on attempt 2. Rows: rows.jsonl (phase 2), pilot_rows.jsonl (attempt 2), pilot_rows_attempt1.jsonl.",
}
json.dump(out, open("OUTCOME.json", "w"), indent=1)
print(outcome, json.dumps({k: tr[k] for k in ("S1", "S2", "S3", "rho")}), "failure", fl["failure"])
print({k: out["statistics"]["bonds_lam_ge1"][k] for k in out["statistics"]["bonds_lam_ge1"]})
print("tol1e-3 success", tr3["success"], "failure", fl3["failure"], "core_min", out["core_minutes"])
