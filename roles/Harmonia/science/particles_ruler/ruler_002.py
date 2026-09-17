"""Harmonia ruler for MECH-PARTICLES-ESSTRIGGER-002 (plan: PLAN_002_2026-09-17.md).

Reuses ruler.py's staging, witness, run_arm, aggregate, var_ratio_ci. Two worlds
(W1 sigmaY 0.2 seed 20260917; W2 sigmaY 1.0 seed 20260918), controls first.
Usage: python ruler_002.py [--seeds 50] [--x-seeds 400] [--quick] [--out DIR]
"""
import argparse, hashlib, json, os, shutil, sys, tempfile, time
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"; sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ruler as R0  # noqa: E402

PACKET_ID = "MECH-PARTICLES-ESSTRIGGER-002"
PACKET_FREEZE = "186047db804af234566eb2a6ece10346823bc69ebeafe87eae0e837a5416d284"
DATA_SEED_W1, DATA_SEED_W2, T = 20260917, 20260918, 100
DATA_W1_SHA_001_RUN = None  # filled from the 001 receipt if present
BANDS = {"POS_Vratio": (2.5, 20.0), "I0_absB": (0.0, 30.0), "I0_R": (90, 99),
         "I1_Vratio": (5.0, 1e6), "I2_Vratio": (0.5, 3.0), "I2_R": (98, 99), "I3_Vratio": (1.05, 5.0),
         "I4_Rmed": (5, 95), "I5_Vratio": (0.5, 3.0), "I5_R": (98, 99), "NEG_Vratio": (0.5, 2.0)}
inband = R0.inband


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=r"C:\Prometheus-vault\fossils\particles-chopin-0.4\upstream\tree\particles-0.4")
    ap.add_argument("--out", default=None); ap.add_argument("--seeds", type=int, default=50)
    ap.add_argument("--x-seeds", type=int, default=400); ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    if a.quick: a.seeds, a.x_seeds = 3, 0
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    out = a.out or os.path.join(HERE, "out", "002_" + stamp + ("_QUICK" if a.quick else "")); os.makedirs(out, exist_ok=True)
    t0 = time.time()
    stage_root = tempfile.mkdtemp(prefix="harmonia_particles_002_"); stage = R0.stage_body(a.vault, stage_root); sys.path.insert(0, stage)
    witness = R0.runtime_witness(stage); witness.update({"vault_tree": a.vault, "staged_copy": stage})
    receipt = {"packet_id": PACKET_ID, "packet_freeze": PACKET_FREEZE, "started_utc": stamp, "runtime_witness": witness,
               "seeds": a.seeds, "x_seeds": a.x_seeds, "quick": a.quick,
               "ruler_002_sha256": R0.sha256_file(os.path.abspath(__file__)), "ruler_sha256": R0.sha256_file(R0.__file__)}
    indet = []
    if witness["payload_hash_mismatch"]: indet.append(f"payload hash mismatch: {witness['payload_hash_mismatch']}")
    if not witness["numba_jit_active"]: indet.append("numba jit not active")
    if a.seeds < 50: indet.append(f"fewer than 50 seeds ({a.seeds})")

    import numpy as np, particles
    from particles import state_space_models as ssms, kalman
    from particles.collectors import Moments

    def world(name, sigmaY, seed):
        model = kalman.LinearGauss(sigmaY=sigmaY) if sigmaY is not None else kalman.LinearGauss()
        np.random.seed(seed); x, y = model.simulate(T)
        p = os.path.join(out, f"data_{name}.npz"); np.savez(p, x=np.asarray(x), y=np.asarray(y).reshape(T, -1))
        kf = kalman.Kalman(ssm=model, data=y); kf.filter()
        m = np.array([float(np.asarray(f.mean).ravel()[0]) for f in kf.filt]); logL = float(np.sum(kf.logpyt))
        return {"name": name, "model": model, "y": y, "m": m, "logL": logL, "data_sha256": R0.sha256_file(p),
                "params": {"rho": model.rho, "sigmaX": model.sigmaX, "sigmaY": model.sigmaY, "sigma0": float(model.sigma0)}, "seed": seed}
    W1 = world("W1", None, DATA_SEED_W1); W2 = world("W2", 1.0, DATA_SEED_W2)
    receipt["worlds"] = {w["name"]: {k: w[k] for k in ("params", "seed", "data_sha256", "logL")} for w in (W1, W2)}
    # W1 dataset must equal the 001 run's dataset
    r001 = os.path.join(HERE, "out", "20260917T152855Z", "receipt.json")
    if os.path.exists(r001):
        sha001 = json.load(open(r001))["world"]["data_sha256"]; receipt["W1_data_matches_001_run"] = (sha001 == W1["data_sha256"])
        if sha001 != W1["data_sha256"]: indet.append("W1 dataset differs from the 001 run's data.npz")

    rows_f = open(os.path.join(out, "rows.jsonl"), "w", encoding="utf-8", newline="\n")

    def arm(label, w, N, scheme, e, seeds, model_=None, cheat=False):
        rows, means = [], []
        for s in range(1, seeds + 1):
            r, m = R0.run_arm(np, particles, ssms, Moments, model_ or w["model"], w["y"], s, N, scheme, e,
                              cheat=(w["m"], w["logL"]) if cheat else None)
            r["arm"] = label; r["world"] = w["name"]; rows.append(r); means.append(m); rows_f.write(json.dumps(r) + "\n")
        agg = R0.aggregate(np, rows, means, w["m"], w["logL"]); agg.update({"arm": label, "world": w["name"], "N": N, "scheme": scheme, "ESSrmin": e})
        agg["R_per_seed"] = [r["R"] for r in rows]
        return agg

    res = {"controls": {}, "arms": {}, "checks": {}}
    ns = a.seeds
    # controls
    cheat_ok = True; ctrl = {}
    for label, w, N, sch, e in [("I0", W1, 100, "systematic", 0.5), ("I1", W1, 100, "systematic", 0.0), ("I2", W1, 100, "systematic", 1.0),
                                ("I3", W1, 100, "multinomial", 0.5), ("I4", W2, 100, "systematic", 0.5), ("I5", W2, 100, "systematic", 1.0)]:
        g = arm("CHEAT-" + label, w, N, sch, e, min(ns, 5), cheat=True); ctrl["CHEAT-" + label] = g
        cheat_ok = cheat_ok and g["RMSE"] == 0.0 and g["V"] == 0.0 and g["B"] == 0.0
    res["controls"]["C-CHEAT-ORACLE-IN-THE-LOOP"] = {"pass": cheat_ok, "rows": ctrl}
    if not cheat_ok: indet.append("C-CHEAT-ORACLE-IN-THE-LOOP failed")
    p200 = arm("POS-N200", W1, 200, "systematic", 0.5, ns); p1000 = arm("POS-N1000", W1, 1000, "systematic", 0.5, ns)
    pr = p200["V"] / p1000["V"]; pos_ok = inband(pr, BANDS["POS_Vratio"]) and p200["RMSE"] > p1000["RMSE"]
    res["controls"]["C-POS-N-SCALING-IN-REGIME"] = {"pass": pos_ok, "V_ratio_200_over_1000": pr, "band": BANDS["POS_Vratio"],
                                                    "ci95": R0.var_ratio_ci(pr, ns - 1, ns - 1), "N200": p200, "N1000": p1000}
    if not pos_ok: indet.append(f"C-POS-N-SCALING-IN-REGIME failed: ratio {pr:.4g}, RMSE200 {p200['RMSE']:.4g} vs RMSE1000 {p1000['RMSE']:.4g}")
    mneg = kalman.LinearGauss(sigmaY=1000.0)
    n0 = arm("NEG-I0", W1, 100, "systematic", 0.5, ns, model_=mneg); n1 = arm("NEG-I1", W1, 100, "systematic", 0.0, ns, model_=mneg)
    nr = n1["V"] / n0["V"] if n0["V"] > 0 else float("inf"); neg_ok = n0["R_max"] == 0 and inband(nr, BANDS["NEG_Vratio"])
    res["controls"]["C-NEG-UNINFORMATIVE"] = {"pass": neg_ok, "R_max_I0": n0["R_max"], "V_ratio": nr, "band": BANDS["NEG_Vratio"], "I0": n0, "I1": n1}
    mandatory = cheat_ok and pos_ok; res["checks"]["mandatory_controls_pass"] = mandatory

    V = {}
    if mandatory:
        I0 = arm("I0", W1, 100, "systematic", 0.5, ns); I1 = arm("I1", W1, 100, "systematic", 0.0, ns)
        I2 = arm("I2", W1, 100, "systematic", 1.0, ns); I3 = arm("I3", W1, 100, "multinomial", 0.5, ns)
        res["arms"].update({"I0": I0, "I1": I1, "I2": I2, "I3": I3})
        r1, r2, r3, rm1 = I1["V"] / I0["V"], I2["V"] / I0["V"], I3["V"] / I0["V"], I1["RMSE"] / I0["RMSE"]
        ci3 = R0.var_ratio_ci(r3, ns - 1, ns - 1)
        V["I0"] = {"absB": abs(I0["B"]), "absB_in_band": inband(abs(I0["B"]), BANDS["I0_absB"]), "R_range": [I0["R_min"], I0["R_max"]],
                   "R_in_band_all_seeds": I0["R_min"] >= 90 and I0["R_max"] <= 99}
        V["I1"] = {"R_max": I1["R_max"], "R_exactly_0_all_seeds": I1["R_max"] == 0, "V_ratio": r1, "V_ratio_in_band": inband(r1, BANDS["I1_Vratio"]), "RMSE_ratio": rm1}
        V["I2"] = {"R_range": [I2["R_min"], I2["R_max"]], "R_in_98_99_all_seeds": I2["R_min"] >= 98 and I2["R_max"] <= 99,
                   "V_ratio": r2, "V_ratio_in_band": inband(r2, BANDS["I2_Vratio"]), "identical_to_I0_seed_for_seed": I2["R_per_seed"] == I0["R_per_seed"] and abs(I2["V"] - I0["V"]) == 0.0}
        V["I3"] = {"V_ratio": r3, "V_ratio_in_band": inband(r3, BANDS["I3_Vratio"]), "ci95": ci3, "ci_covers_1": ci3[0] <= 1.0 <= ci3[1], "df": [ns - 1, ns - 1]}
        if a.x_seeds:
            I0x = arm("I0x", W1, 100, "systematic", 0.5, a.x_seeds); I3x = arm("I3x", W1, 100, "multinomial", 0.5, a.x_seeds)
            res["arms"].update({"I0x": I0x, "I3x": I3x}); r3x = I3x["V"] / I0x["V"]; ci3x = R0.var_ratio_ci(r3x, a.x_seeds - 1, a.x_seeds - 1)
            V["I3x"] = {"V_ratio": r3x, "V_ratio_in_band": inband(r3x, BANDS["I3_Vratio"]), "ci95": ci3x, "ci_covers_1": ci3x[0] <= 1.0 <= ci3x[1], "df": [a.x_seeds - 1, a.x_seeds - 1]}
        # W2: I4 first
        I4 = arm("I4", W2, 100, "systematic", 0.5, ns); res["arms"]["I4"] = I4
        V["I4"] = {"R_median": I4["R_median"], "R_range": [I4["R_min"], I4["R_max"]], "Rmed_in_band": inband(I4["R_median"], BANDS["I4_Rmed"]),
                   "V": I4["V"], "B": I4["B"], "RMSE": I4["RMSE"]}
        if V["I4"]["Rmed_in_band"]:
            I5 = arm("I5", W2, 100, "systematic", 1.0, ns); res["arms"]["I5"] = I5; r5 = I5["V"] / I4["V"]
            V["I5"] = {"R_range": [I5["R_min"], I5["R_max"]], "R_in_98_99_all_seeds": I5["R_min"] >= 98 and I5["R_max"] <= 99,
                       "V_ratio": r5, "V_ratio_in_band": inband(r5, BANDS["I5_Vratio"]), "ci95": R0.var_ratio_ci(r5, ns - 1, ns - 1),
                       "R_equal_to_I4_seed_for_seed": I5["R_per_seed"] == I4["R_per_seed"], "RMSE_ratio": I5["RMSE"] / I4["RMSE"], "B_I5": I5["B"], "B_I4": I4["B"]}
            if V["I5"]["R_equal_to_I4_seed_for_seed"]: indet.append("I5: R(I5) == R(I4) seed for seed (no contrast)")
            if not V["I5"]["R_in_98_99_all_seeds"]: indet.append(f"I5: R outside [98, 99] in some seed ({V['I5']['R_range']})")
        else:
            indet.append(f"I4: median R {I4['R_median']} outside [5, 95]; W2 gave no contrast; I5 not run")
        kill = (I1["R_max"] > 0) or (I2["R_min"] < 98 or I2["R_max"] > 99) or (r1 < 2.0 and rm1 < 2.0)
        res["checks"]["CUT_KILL_fires"] = bool(kill)
        res["checks"]["kill_components"] = {"I1_R_gt_0": I1["R_max"] > 0, "I2_R_outside_98_99": I2["R_min"] < 98 or I2["R_max"] > 99, "I1_Vratio_lt_2_and_RMSEratio_lt_2": r1 < 2.0 and rm1 < 2.0}
        if V["I3"]["ci_covers_1"]: indet.append("I3 at 50 seeds: F-interval covers 1 (underpowered as predicted)")
    res["verdict_rows"] = V; res["indeterminate_items"] = indet
    if a.quick: rt = "NON_ADJUDICATIVE_SMOKE"
    elif not mandatory or witness["payload_hash_mismatch"] or not witness["numba_jit_active"] or a.seeds < 50: rt = "PREDICTION_INDETERMINATE"
    elif res["checks"]["CUT_KILL_fires"]: rt = "CUT_CHALLENGE"
    else: rt = "CUT_SUPPORTED" if (V["I1"]["R_exactly_0_all_seeds"] and V["I2"]["R_in_98_99_all_seeds"] and V["I1"]["V_ratio_in_band"]) else "PREDICTION_FAILED"
    res["return_type_boundary"] = rt
    if not a.quick and mandatory:
        rr = {"I0": "IN_BAND" if V["I0"]["absB_in_band"] and V["I0"]["R_in_band_all_seeds"] else "OUT_OF_BAND (informative row)",
              "I1": "IN_BAND" if V["I1"]["V_ratio_in_band"] and V["I1"]["R_exactly_0_all_seeds"] else "OUT_OF_BAND",
              "I2": "IN_BAND" if V["I2"]["V_ratio_in_band"] and V["I2"]["R_in_98_99_all_seeds"] else "OUT_OF_BAND",
              "I3": "INDETERMINATE" if V["I3"]["ci_covers_1"] else ("IN_BAND" if V["I3"]["V_ratio_in_band"] else "OUT_OF_BAND"),
              "I4": "IN_BAND" if V["I4"]["Rmed_in_band"] else "OUT_OF_BAND -> W2 rows INDETERMINATE"}
        if "I3x" in V: rr["I3x"] = "INDETERMINATE" if V["I3x"]["ci_covers_1"] else ("IN_BAND" if V["I3x"]["V_ratio_in_band"] else "OUT_OF_BAND")
        if "I5" in V: rr["I5"] = "INDETERMINATE" if (V["I5"]["R_equal_to_I4_seed_for_seed"] or not V["I5"]["R_in_98_99_all_seeds"]) else ("IN_BAND" if V["I5"]["V_ratio_in_band"] else "OUT_OF_BAND")
        res["row_readings"] = rr
    rows_f.close()
    receipt.update({"finished_utc": time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()), "seconds": round(time.time() - t0, 1), "rows_sha256": R0.sha256_file(os.path.join(out, "rows.jsonl"))})
    json.dump(res, open(os.path.join(out, "results.json"), "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True)
    json.dump(receipt, open(os.path.join(out, "receipt.json"), "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True)
    L = [f"{PACKET_ID} freeze {PACKET_FREEZE[:8]} host {witness['host']} python {witness['python']} numba {witness['numba']} jit {witness['numba_jit_active']} payload {'MATCH' if not witness['payload_hash_mismatch'] else 'MISMATCH'}",
         f"W1 logL_exact {W1['logL']:.4f} (data matches 001 run: {receipt.get('W1_data_matches_001_run')}); W2 sigmaY 1.0 seed {DATA_SEED_W2} logL_exact {W2['logL']:.4f}", "", "controls"]
    for k, v in res["controls"].items(): L.append(f"  {k:30s} {'PASS' if v['pass'] else 'FAIL'}")
    c = res["controls"]["C-POS-N-SCALING-IN-REGIME"]; L.append(f"    POS V(200)/V(1000) = {c['V_ratio_200_over_1000']:.4g} band {c['band']} ci95 {[round(x,3) for x in c['ci95']]}  RMSE200 {c['N200']['RMSE']:.4f} RMSE1000 {c['N1000']['RMSE']:.4f}")
    c = res["controls"]["C-NEG-UNINFORMATIVE"]; L.append(f"    NEG R_max(I0) {c['R_max_I0']} V ratio {c['V_ratio']:.4g}")
    L += ["", f"{'arm':5s} {'W':3s} {'N':>5s} {'scheme':12s} {'ESSrmin':>7s} {'seeds':>5s} {'V':>10s} {'B':>9s} {'RMSE':>8s} {'R min/med/max':>15s}"]
    for k, v in res["arms"].items(): L.append(f"{k:5s} {v['world']:3s} {v['N']:5d} {v['scheme']:12s} {v['ESSrmin']:7.2f} {v['n_seeds']:5d} {v['V']:10.4g} {v['B']:9.4f} {v['RMSE']:8.4f} {v['R_min']:4d}/{v['R_median']:5.1f}/{v['R_max']:3d}")
    L.append("")
    for k, v in V.items(): L.append(f"  {k}: {json.dumps({kk: vv for kk, vv in v.items()})}")
    L += ["", f"mandatory controls pass: {mandatory}   CUT_KILL fires: {res['checks'].get('CUT_KILL_fires')}", f"indeterminate items: {indet or 'none'}",
          f"return_type (boundary claim): {rt}", f"row readings: {res.get('row_readings')}", f"elapsed {receipt['seconds']} s; rows sha256 {receipt['rows_sha256'][:12]}; out {out}"]
    txt = "\n".join(L) + "\n"; open(os.path.join(out, "ledger.txt"), "w", encoding="utf-8", newline="\n").write(txt); print(txt)
    shutil.rmtree(stage_root, ignore_errors=True)


if __name__ == "__main__":
    main()
