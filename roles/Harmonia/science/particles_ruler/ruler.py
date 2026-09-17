"""Harmonia ruler for MECH-PARTICLES-ESSTRIGGER-001 (plan: PLAN_2026-09-17.md).

Runs on M3-native CPython against a DISPOSABLE COPY of the particles-0.4
body. Controls first; abort on failure. Writes rows.jsonl, results.json,
receipt.json and ledger.txt into out/<stamp>/.

Usage: python ruler.py [--vault DIR] [--out DIR] [--seeds 50] [--x-seeds 400] [--quick]
"""
import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True

PACKET_ID = "MECH-PARTICLES-ESSTRIGGER-001"
PACKET_FREEZE = "5b8d6ae4908abb3b4473a106a741563663006a7236e52cd248293bbbb4bc4c47"
PAYLOAD = {
    "core.py": "1c99eb9884fc49a45c7e02e24d0d897c92e2300111385160628b97fe313ffb3c",
    "resampling.py": "6657f40f1a7cafecdfe958bdd0fb2403b3f06cc31ced294abc1eebcfc0f24e18",
}
DATA_SEED = 20260917
T = 100

BANDS = {  # copied from the packet; PLAN section "Decision rules"
    "I0_absB": (0.0, 2.0), "I0_R": (10, 90),
    "I1_Vratio": (5.0, 1e6), "I1_R": (0, 0),
    "I2_Vratio": (0.5, 3.0), "I2_R": (98, 99),
    "I3_Vratio": (1.05, 5.0),
    "POS_Vratio": (10.0, 1000.0),
    "NEG_Vratio": (0.5, 2.0),
}


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stage_body(vault_tree, stage_root):
    dst = os.path.join(stage_root, "particles-0.4")
    shutil.copytree(vault_tree, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return dst


def runtime_witness(stage_dir):
    import particles  # noqa: E402
    from particles import core, resampling, kalman, state_space_models, collectors  # noqa

    pf = os.path.abspath(particles.__file__)
    assert pf.startswith(os.path.abspath(stage_dir)), f"particles imported from {pf}, not the staged copy"
    hashes = {
        "core.py": sha256_file(core.__file__),
        "resampling.py": sha256_file(resampling.__file__),
        "kalman.py": sha256_file(kalman.__file__),
        "state_space_models.py": sha256_file(state_space_models.__file__),
        "collectors.py": sha256_file(collectors.__file__),
    }
    mismatch = {k: (hashes[k], v) for k, v in PAYLOAD.items() if hashes[k] != v}
    freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True).stdout
    import numpy, scipy
    try:
        import numba
        numba_v = numba.__version__
    except Exception:  # pragma: no cover
        numba_v = None
    try:
        import joblib
        joblib_v = joblib.__version__
    except Exception:  # pragma: no cover
        joblib_v = None
    disp = type(resampling.inverse_cdf).__name__
    return {
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "particles_file": pf,
        "imported_payload_hashes": hashes,
        "payload_hash_mismatch": mismatch,
        "pip_freeze_sha256": hashlib.sha256(freeze.encode()).hexdigest(),
        "pip_freeze_n": len([l for l in freeze.splitlines() if l.strip()]),
        "numpy": numpy.__version__, "scipy": scipy.__version__,
        "numba": numba_v, "joblib": joblib_v,
        "inverse_cdf_type": disp,
        "numba_jit_active": disp == "CPUDispatcher",
        "dont_write_bytecode": sys.dont_write_bytecode,
    }


def run_arm(np, particles, ssms, Moments, model, y, seed, N, scheme, essrmin, cheat=None):
    """One SMC run. cheat=(m_exact, logL_exact) injects the oracle into the channel."""
    np.random.seed(seed)
    fk = ssms.Bootstrap(ssm=model, data=y)
    pf = particles.SMC(fk=fk, N=N, resampling=scheme, ESSrmin=essrmin, collect=[Moments()], verbose=False)
    pf.run()
    means = np.array([float(np.asarray(m["mean"]).ravel()[0]) for m in pf.summaries.moments])
    logLt = float(pf.summaries.logLts[-1])
    R = int(sum(bool(f) for f in pf.summaries.rs_flags))
    ess = [float(e) for e in pf.summaries.ESSs]
    if cheat is not None:
        means = cheat[0].copy()
        logLt = float(cheat[1])
    return {"seed": seed, "N": N, "scheme": scheme, "ESSrmin": essrmin, "logLt": logLt, "R": R,
            "T_steps": len(pf.summaries.rs_flags), "ess_min": min(ess), "ess_median": float(np.median(ess))}, means


def aggregate(np, rows, means_list, m_exact, logL_exact):
    L = np.array([r["logLt"] for r in rows])
    M = np.stack(means_list)  # seeds x T
    V = float(np.var(L, ddof=1)) if len(L) > 1 else float("nan")
    B = float(np.mean(L - logL_exact))
    rmse = float(np.sqrt(np.mean((M - m_exact[None, :]) ** 2)))
    Rs = np.array([r["R"] for r in rows])
    return {"n_seeds": len(rows), "V": V, "B": B, "RMSE": rmse,
            "R_min": int(Rs.min()), "R_median": float(np.median(Rs)), "R_max": int(Rs.max()),
            "logLt_mean": float(L.mean()), "logL_exact": float(logL_exact)}


def var_ratio_ci(ratio, df1, df2, alpha=0.05):
    from scipy.stats import f
    lo = ratio / f.ppf(1 - alpha / 2, df1, df2)
    hi = ratio / f.ppf(alpha / 2, df1, df2)
    return [float(lo), float(hi)]


def inband(x, band):
    return band[0] <= x <= band[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=r"C:\Prometheus-vault\fossils\particles-chopin-0.4\upstream\tree\particles-0.4")
    ap.add_argument("--out", default=None)
    ap.add_argument("--seeds", type=int, default=50)
    ap.add_argument("--x-seeds", type=int, default=400)
    ap.add_argument("--quick", action="store_true", help="smoke: 3 seeds, no 400-seed arms; NOT adjudicative")
    a = ap.parse_args()
    if a.quick:
        a.seeds, a.x_seeds = 3, 0
    here = os.path.dirname(os.path.abspath(__file__))
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    out = a.out or os.path.join(here, "out", stamp + ("_QUICK" if a.quick else ""))
    os.makedirs(out, exist_ok=True)
    t0 = time.time()

    stage_root = tempfile.mkdtemp(prefix="harmonia_particles_")
    stage = stage_body(a.vault, stage_root)
    sys.path.insert(0, stage)
    witness = runtime_witness(stage)
    witness["vault_tree"] = a.vault
    witness["staged_copy"] = stage
    witness["vault_tree_sha256_core_resampling"] = {k: sha256_file(os.path.join(a.vault, "particles", k)) for k in PAYLOAD}
    receipt = {"packet_id": PACKET_ID, "packet_freeze": PACKET_FREEZE, "started_utc": stamp,
               "runtime_witness": witness, "seeds": a.seeds, "x_seeds": a.x_seeds, "quick": a.quick,
               "ruler_sha256": sha256_file(os.path.abspath(__file__))}
    indeterminate = []
    if witness["payload_hash_mismatch"]:
        indeterminate.append(f"payload hash mismatch at run time: {witness['payload_hash_mismatch']}")
    if not witness["numba_jit_active"]:
        indeterminate.append(f"numba jit not active on inverse_cdf (type {witness['inverse_cdf_type']})")
    if a.seeds < 50:
        indeterminate.append(f"fewer than 50 seeds ({a.seeds})")

    import numpy as np
    import particles
    from particles import state_space_models as ssms
    from particles import kalman
    from particles.collectors import Moments

    # world: model, one dataset, oracle
    model = kalman.LinearGauss()
    np.random.seed(DATA_SEED)
    x, y = model.simulate(T)
    y_arr = np.asarray(y).reshape(T, -1)
    data_path = os.path.join(out, "data.npz")
    np.savez(data_path, x=np.asarray(x), y=y_arr)
    kf = kalman.Kalman(ssm=model, data=y)
    kf.filter()
    m_exact = np.array([float(np.asarray(f.mean).ravel()[0]) for f in kf.filt])
    logL_exact = float(np.sum(kf.logpyt))
    receipt["world"] = {
        "model": {"rho": model.rho, "sigmaX": model.sigmaX, "sigmaY": model.sigmaY, "sigma0": float(model.sigma0)},
        "T": T, "data_seed": DATA_SEED, "data_sha256": sha256_file(data_path),
        "oracle": "particles.kalman.Kalman filter on the same model/data; logL_exact = sum(logpyt)",
        "logL_exact": logL_exact, "m_exact_first5": [float(v) for v in m_exact[:5]],
    }

    rows_f = open(os.path.join(out, "rows.jsonl"), "w", encoding="utf-8", newline="\n")

    def arm(label, N, scheme, essrmin, seeds, model_=model, cheat=False):
        rows, means = [], []
        for s in range(1, seeds + 1):
            r, m = run_arm(np, particles, ssms, Moments, model_, y, s, N, scheme, essrmin,
                           cheat=(m_exact, logL_exact) if cheat else None)
            r["arm"] = label
            rows.append(r); means.append(m)
            rows_f.write(json.dumps(r) + "\n")
        agg = aggregate(np, rows, means, m_exact, logL_exact)
        agg.update({"arm": label, "N": N, "scheme": scheme, "ESSrmin": essrmin})
        return agg

    results = {"arms": {}, "controls": {}, "checks": {}}
    ns = a.seeds

    # ---------------- controls first ----------------
    ctrl = {}
    # cheat: every arm's code path with the oracle injected
    cheat_ok = True
    for label, N, sch, e in [("I0", 100, "systematic", 0.5), ("I1", 100, "systematic", 0.0),
                             ("I2", 100, "systematic", 1.0), ("I3", 100, "multinomial", 0.5)]:
        agg = arm("CHEAT-" + label, N, sch, e, min(ns, 5), cheat=True)
        ctrl["CHEAT-" + label] = agg
        ok = agg["RMSE"] == 0.0 and agg["V"] == 0.0 and agg["B"] == 0.0
        cheat_ok = cheat_ok and ok
    results["controls"]["C-CHEAT-ORACLE-IN-THE-LOOP"] = {"pass": cheat_ok, "rows": {k: v for k, v in ctrl.items()}}
    if not cheat_ok:
        indeterminate.append("C-CHEAT-ORACLE-IN-THE-LOOP failed: channel reports nonzero error on the exact answer")

    pos10 = arm("POS-N10", 10, "systematic", 0.5, ns)
    pos1000 = arm("POS-N1000", 1000, "systematic", 0.5, ns)
    pos_ratio = pos10["V"] / pos1000["V"]
    pos_ok = inband(pos_ratio, BANDS["POS_Vratio"]) and pos10["RMSE"] > pos1000["RMSE"]
    results["controls"]["C-POS-N-SCALING"] = {"pass": pos_ok, "V_ratio_10_over_1000": pos_ratio,
                                              "band": BANDS["POS_Vratio"], "N10": pos10, "N1000": pos1000}
    if not pos_ok:
        indeterminate.append(f"C-POS-N-SCALING failed: V ratio {pos_ratio:.3g}, RMSE10 {pos10['RMSE']:.4g} vs RMSE1000 {pos1000['RMSE']:.4g}")

    model_neg = kalman.LinearGauss(sigmaY=1000.0)
    neg0 = arm("NEG-I0", 100, "systematic", 0.5, ns, model_=model_neg)
    neg1 = arm("NEG-I1", 100, "systematic", 0.0, ns, model_=model_neg)
    neg_ratio = neg1["V"] / neg0["V"] if neg0["V"] > 0 else float("inf")
    neg_ok = neg0["R_max"] == 0 and inband(neg_ratio, BANDS["NEG_Vratio"])
    results["controls"]["C-NEG-UNINFORMATIVE"] = {"pass": neg_ok, "R_max_I0": neg0["R_max"], "V_ratio_I1_over_I0": neg_ratio,
                                                  "band": BANDS["NEG_Vratio"], "I0": neg0, "I1": neg1,
                                                  "note": "welcome control; not mandatory for the reading"}

    mandatory_ok = cheat_ok and pos_ok
    results["checks"]["mandatory_controls_pass"] = mandatory_ok

    # ---------------- arms ----------------
    verdict_rows = {}
    if mandatory_ok:
        I0 = arm("I0", 100, "systematic", 0.5, ns)
        I1 = arm("I1", 100, "systematic", 0.0, ns)
        I2 = arm("I2", 100, "systematic", 1.0, ns)
        I3 = arm("I3", 100, "multinomial", 0.5, ns)
        results["arms"].update({"I0": I0, "I1": I1, "I2": I2, "I3": I3})
        r1 = I1["V"] / I0["V"]; r2 = I2["V"] / I0["V"]; r3 = I3["V"] / I0["V"]
        rm1 = I1["RMSE"] / I0["RMSE"]
        ci3 = var_ratio_ci(r3, ns - 1, ns - 1)
        verdict_rows["I0"] = {"absB": abs(I0["B"]), "absB_in_band": inband(abs(I0["B"]), BANDS["I0_absB"]),
                              "R_range": [I0["R_min"], I0["R_max"]], "R_in_band": inband(I0["R_min"], BANDS["I0_R"]) and inband(I0["R_max"], BANDS["I0_R"])}
        verdict_rows["I1"] = {"R_max": I1["R_max"], "R_exactly_0_all_seeds": I1["R_max"] == 0,
                              "V_ratio": r1, "V_ratio_in_band": inband(r1, BANDS["I1_Vratio"]), "RMSE_ratio": rm1}
        verdict_rows["I2"] = {"R_range": [I2["R_min"], I2["R_max"]],
                              "R_in_98_99_all_seeds": I2["R_min"] >= 98 and I2["R_max"] <= 99,
                              "V_ratio": r2, "V_ratio_in_band": inband(r2, BANDS["I2_Vratio"])}
        verdict_rows["I3"] = {"V_ratio": r3, "V_ratio_in_band": inband(r3, BANDS["I3_Vratio"]), "ci95": ci3,
                              "ci_covers_1": ci3[0] <= 1.0 <= ci3[1], "df": [ns - 1, ns - 1]}
        if a.x_seeds:
            I0x = arm("I0x", 100, "systematic", 0.5, a.x_seeds)
            I3x = arm("I3x", 100, "multinomial", 0.5, a.x_seeds)
            results["arms"].update({"I0x": I0x, "I3x": I3x})
            r3x = I3x["V"] / I0x["V"]; ci3x = var_ratio_ci(r3x, a.x_seeds - 1, a.x_seeds - 1)
            verdict_rows["I3x"] = {"V_ratio": r3x, "V_ratio_in_band": inband(r3x, BANDS["I3_Vratio"]), "ci95": ci3x,
                                   "ci_covers_1": ci3x[0] <= 1.0 <= ci3x[1], "df": [a.x_seeds - 1, a.x_seeds - 1],
                                   "note": "added at the packet's invitation; reported beside I3, never instead"}
        kill = (I1["R_max"] > 0) or (I2["R_min"] < 98 or I2["R_max"] > 99) or (r1 < 2.0 and rm1 < 2.0)
        results["checks"]["CUT_KILL_fires"] = bool(kill)
        results["checks"]["kill_components"] = {"I1_R_gt_0": I1["R_max"] > 0,
                                                "I2_R_outside_98_99": I2["R_min"] < 98 or I2["R_max"] > 99,
                                                "I1_Vratio_lt_2_and_RMSEratio_lt_2": r1 < 2.0 and rm1 < 2.0}
        if verdict_rows["I3"]["ci_covers_1"]:
            indeterminate.append("I3 at 50 seeds: 95% interval of the variance ratio covers 1.0 (underpowered, as the packet predicted)")
    results["verdict_rows"] = verdict_rows
    results["indeterminate_items"] = indeterminate

    # ---------------- typed return ----------------
    if a.quick:
        rt = "NON_ADJUDICATIVE_SMOKE"
    elif not mandatory_ok or witness["payload_hash_mismatch"] or not witness["numba_jit_active"] or a.seeds < 50:
        rt = "PREDICTION_INDETERMINATE"
    elif results["checks"]["CUT_KILL_fires"]:
        rt = "CUT_CHALLENGE"
    else:
        boundary_ok = verdict_rows["I1"]["R_exactly_0_all_seeds"] and verdict_rows["I2"]["R_in_98_99_all_seeds"] \
            and verdict_rows["I1"]["V_ratio_in_band"]
        rt = "CUT_SUPPORTED" if boundary_ok else "PREDICTION_FAILED"
    results["return_type_boundary"] = rt
    if not a.quick and mandatory_ok:
        results["row_readings"] = {
            "I0": "IN_BAND" if verdict_rows["I0"]["absB_in_band"] else "OUT_OF_BAND (informative, not a kill row)",
            "I1": "IN_BAND" if verdict_rows["I1"]["V_ratio_in_band"] and verdict_rows["I1"]["R_exactly_0_all_seeds"] else "OUT_OF_BAND",
            "I2": "IN_BAND" if verdict_rows["I2"]["V_ratio_in_band"] and verdict_rows["I2"]["R_in_98_99_all_seeds"] else "OUT_OF_BAND",
            "I3": "INDETERMINATE" if verdict_rows["I3"]["ci_covers_1"] else ("IN_BAND" if verdict_rows["I3"]["V_ratio_in_band"] else "OUT_OF_BAND"),
        }
        if "I3x" in verdict_rows:
            v = verdict_rows["I3x"]
            results["row_readings"]["I3x"] = "INDETERMINATE" if v["ci_covers_1"] else ("IN_BAND" if v["V_ratio_in_band"] else "OUT_OF_BAND")

    rows_f.close()
    receipt["finished_utc"] = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    receipt["seconds"] = round(time.time() - t0, 1)
    receipt["rows_sha256"] = sha256_file(os.path.join(out, "rows.jsonl"))
    with open(os.path.join(out, "results.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(results, f, indent=1, sort_keys=True)
    with open(os.path.join(out, "receipt.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(receipt, f, indent=1, sort_keys=True)

    # ledger, human-readable
    L = []
    L.append(f"{PACKET_ID}  freeze {PACKET_FREEZE[:8]}  host {witness['host']}  python {witness['python']}  numba {witness['numba']} jit_active {witness['numba_jit_active']}")
    L.append(f"payload hashes at run time: {'MATCH' if not witness['payload_hash_mismatch'] else witness['payload_hash_mismatch']}")
    L.append(f"world: LinearGauss defaults, T={T}, data seed {DATA_SEED}, logL_exact {logL_exact:.4f}")
    L.append("")
    L.append("controls")
    for k, v in results["controls"].items():
        L.append(f"  {k:32s} {'PASS' if v['pass'] else 'FAIL'}")
    for k, v in ctrl.items():
        L.append(f"    {k:12s} RMSE {v['RMSE']:.3g} V {v['V']:.3g} B {v['B']:.3g}")
    c = results["controls"]["C-POS-N-SCALING"]
    L.append(f"    POS  V(10)/V(1000) = {c['V_ratio_10_over_1000']:.3g} band {c['band']}  RMSE10 {c['N10']['RMSE']:.4f} RMSE1000 {c['N1000']['RMSE']:.4f}")
    c = results["controls"]["C-NEG-UNINFORMATIVE"]
    L.append(f"    NEG  R_max under I0 = {c['R_max_I0']}  V(I1)/V(I0) = {c['V_ratio_I1_over_I0']:.3g} band {c['band']}")
    L.append("")
    L.append(f"{'arm':6s} {'N':>5s} {'scheme':12s} {'ESSrmin':>7s} {'seeds':>5s} {'V':>10s} {'B':>9s} {'RMSE':>8s} {'R min/med/max':>16s}")
    for k, v in results["arms"].items():
        L.append(f"{k:6s} {v['N']:5d} {v['scheme']:12s} {v['ESSrmin']:7.2f} {v['n_seeds']:5d} {v['V']:10.4g} {v['B']:9.4f} {v['RMSE']:8.4f} {v['R_min']:5d}/{v['R_median']:5.1f}/{v['R_max']:4d}")
    L.append("")
    for k, v in verdict_rows.items():
        L.append(f"  {k}: {json.dumps(v)}")
    L.append("")
    L.append(f"mandatory controls pass: {mandatory_ok}   CUT_KILL fires: {results['checks'].get('CUT_KILL_fires')}")
    L.append(f"indeterminate items: {indeterminate if indeterminate else 'none'}")
    L.append(f"return_type (boundary claim): {rt}")
    if "row_readings" in results:
        L.append(f"row readings: {results['row_readings']}")
    L.append(f"elapsed {receipt['seconds']} s; rows sha256 {receipt['rows_sha256'][:12]}; out {out}")
    txt = "\n".join(L) + "\n"
    with open(os.path.join(out, "ledger.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(txt)
    print(txt)
    shutil.rmtree(stage_root, ignore_errors=True)


if __name__ == "__main__":
    main()
