"""SCOUT / NON-ADJUDICATIVE. Characterises the positive control C-POS-N-SCALING of
MECH-PARTICLES-ESSTRIGGER-001: V(logLt_hat) and RMSE as a function of N at I0
settings (systematic, ESSrmin 0.5), 50 seeds each, same world and dataset as
ruler.py. Touches NO intervention arm (I1-I3 are not run here). Its purpose is
to let Nyx set a control band that the instrument can satisfy when the effect
is real, in a superseding packet. Numbers here enter no verdict.
"""
import json, os, sys, time, hashlib, shutil, tempfile
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"; sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ruler  # noqa: E402  (reuses stage_body / run_arm / aggregate; same world)

VAULT = r"C:\Prometheus-vault\fossils\particles-chopin-0.4\upstream\tree\particles-0.4"
NS = [10, 20, 50, 100, 200, 500, 1000]
SEEDS = 50

def main():
    stage_root = tempfile.mkdtemp(prefix="harmonia_particles_scout_")
    stage = ruler.stage_body(VAULT, stage_root)
    sys.path.insert(0, stage)
    w = ruler.runtime_witness(stage)
    assert not w["payload_hash_mismatch"], w["payload_hash_mismatch"]
    import numpy as np, particles
    from particles import state_space_models as ssms, kalman
    from particles.collectors import Moments
    model = kalman.LinearGauss()
    np.random.seed(ruler.DATA_SEED); x, y = model.simulate(ruler.T)
    kf = kalman.Kalman(ssm=model, data=y); kf.filter()
    m_exact = np.array([float(np.asarray(f.mean).ravel()[0]) for f in kf.filt]); logL = float(np.sum(kf.logpyt))
    out = os.path.join(HERE, "out", "SCOUT_pos_control_" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
    os.makedirs(out, exist_ok=True)
    table = []
    with open(os.path.join(out, "rows.jsonl"), "w", encoding="utf-8", newline="\n") as rf:
        for N in NS:
            rows, means = [], []
            for s in range(1, SEEDS + 1):
                r, m = ruler.run_arm(np, particles, ssms, Moments, model, y, s, N, "systematic", 0.5)
                r["arm"] = f"SCOUT-POS-N{N}"; rows.append(r); means.append(m); rf.write(json.dumps(r) + "\n")
            agg = ruler.aggregate(np, rows, means, m_exact, logL); agg["N"] = N
            L = np.array([r["logLt"] for r in rows])
            agg["logLt_min"] = float(L.min()); agg["logLt_max"] = float(L.max())
            agg["n_seeds_logLt_below_exact_minus_20"] = int((L < logL - 20).sum())
            table.append(agg)
    res = {"label": "SCOUT / NON-ADJUDICATIVE", "packet": ruler.PACKET_ID, "world": "as ruler.py", "seeds": SEEDS,
           "logL_exact": logL, "witness": w, "table": table,
           "ratios_vs_N1000": {str(t["N"]): t["V"] / table[-1]["V"] for t in table}}
    with open(os.path.join(out, "results.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1, sort_keys=True)
    lines = ["SCOUT / NON-ADJUDICATIVE: C-POS-N-SCALING curve, I0 settings, 50 seeds, same world/data as ruler.py",
             f"logL_exact {logL:.4f}", "",
             f"{'N':>5s} {'V':>10s} {'V/V(1000)':>10s} {'B':>9s} {'RMSE':>8s} {'R med':>6s} {'logLt min':>10s} {'#<exact-20':>10s}"]
    for t in table:
        lines.append(f"{t['N']:5d} {t['V']:10.4g} {t['V']/table[-1]['V']:10.4g} {t['B']:9.3f} {t['RMSE']:8.4f} {t['R_median']:6.1f} {t['logLt_min']:10.2f} {t['n_seeds_logLt_below_exact_minus_20']:10d}")
    txt = "\n".join(lines) + "\n"
    open(os.path.join(out, "ledger.txt"), "w", encoding="utf-8", newline="\n").write(txt)
    print(txt); print("out", out)
    shutil.rmtree(stage_root, ignore_errors=True)

if __name__ == "__main__":
    main()
