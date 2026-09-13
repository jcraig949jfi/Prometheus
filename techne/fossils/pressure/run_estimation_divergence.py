"""Batch 07 depth (estimation): filter-divergence behaviour of the preserved Kalman filter.

The coverage map flags estimation/control as having NO failed branches. This drives the vault's
own filterpy-labbe fossil (a linear KalmanFilter) into the CANONICAL estimation failure: the
"smug"/overconfident filter. A constant-velocity KF is run against a target that actually
manoeuvres (model mismatch), under several process-noise (Q) settings. With Q too small the filter
trusts its wrong model, its reported covariance P collapses, the Kalman gain -> 0, it stops
listening to measurements, and the estimate diverges from truth while the filter still reports high
confidence. A matched Q is the control branch where it tracks. Techne records the raw divergence
(reported sigma vs actual error); it does not rank tunings or explain the mechanism.

    python run_estimation_divergence.py -> ESTIMATION_DIVERGENCE_<date>.json
"""
import json, pathlib, subprocess, time

HERE = pathlib.Path(__file__).resolve().parent
VAULT = "/mnt/f/Prometheus/vault/fossils"
DATE = "2026-09-13"
FP_TREE = "/vault/filterpy-labbe/upstream/tree"

DRIVER = r'''
import json, numpy as np
from filterpy.kalman import KalmanFilter

def run(Q_scale, seed=7, N=120, dt=1.0):
    rng = np.random.default_rng(seed)
    # truth: a target that manoeuvres -- constant velocity then a sustained turn/accel the
    # constant-velocity model does NOT contain (the model mismatch the filter must survive).
    x = 0.0; v = 1.0; truth = []
    for k in range(N):
        a = 0.0 if k < 40 else 0.30          # a step acceleration at k=40 (the manoeuvre)
        v += a * dt; x += v * dt
        truth.append(x)
    truth = np.array(truth)
    R = 4.0                                   # measurement noise variance (sigma=2.0)
    meas = truth + rng.normal(0.0, np.sqrt(R), size=N)

    kf = KalmanFilter(dim_x=2, dim_z=1)
    kf.F = np.array([[1.0, dt], [0.0, 1.0]])
    kf.H = np.array([[1.0, 0.0]])
    kf.R = np.array([[R]])
    kf.x = np.array([[0.0], [1.0]])
    kf.P = np.eye(2) * 1.0
    # process noise: Q_scale multiplies a small base. Too small => the filter cannot admit the
    # manoeuvre and grows overconfident; matched => it tracks.
    q = Q_scale
    kf.Q = np.array([[q * dt**3 / 3, q * dt**2 / 2], [q * dt**2 / 2, q * dt]])

    est_err = []; rep_sigma = []; gain = []
    for z in meas:
        kf.predict()
        kf.update(np.array([[z]]))
        est_err.append(float(kf.x[0, 0]) - float(truth[len(est_err)]))
        rep_sigma.append(float(np.sqrt(kf.P[0, 0])))   # filter's CLAIMED position stddev
        gain.append(float(kf.K[0, 0]))                  # Kalman gain on position
    est_err = np.array(est_err); rep_sigma = np.array(rep_sigma)
    tail = slice(N - 40, N)                              # after the manoeuvre
    actual_rmse_tail = float(np.sqrt(np.mean(est_err[tail] ** 2)))
    reported_sigma_tail = float(np.mean(rep_sigma[tail]))
    # divergence signature: actual error dwarfs the confidence the filter reports.
    overconfidence = float(actual_rmse_tail / reported_sigma_tail) if reported_sigma_tail > 0 else None
    return {"Q_scale": Q_scale, "final_gain": float(gain[-1]),
            "reported_sigma_final": float(rep_sigma[-1]),
            "actual_abs_error_final": float(abs(est_err[-1])),
            "actual_rmse_after_manoeuvre": actual_rmse_tail,
            "reported_sigma_after_manoeuvre": reported_sigma_tail,
            "overconfidence_ratio_error_over_reported": overconfidence,
            "diverged": bool(overconfidence is not None and overconfidence > 3.0)}

rows = [run(qs) for qs in (1e-6, 1e-4, 1e-2, 1.0)]
print("RESULT " + json.dumps(rows))
'''

SCRIPT = (
    "pip install -q numpy scipy >/dev/null 2>&1\n"
    "cat > /tmp/drv.py <<'PYEOF'\n" + DRIVER + "\nPYEOF\n"
    "PYTHONPATH=%s python /tmp/drv.py\n" % FP_TREE
)


def main():
    out = subprocess.run(["wsl.exe", "-e", "bash", "-lc",
        "docker run --rm -v %s:/vault:ro python:3.11-slim bash -lc %s" % (VAULT, _q(SCRIPT))],
        capture_output=True, text=True, timeout=1200).stdout
    rows = []
    for line in out.splitlines():
        if line.startswith("RESULT "):
            rows = json.loads(line[len("RESULT "):])
    doc = {"schema": "techne.fossil.estimation_divergence/1", "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "fossil_driven": "filterpy-labbe", "method": "a constant-velocity KalmanFilter is run against a target that steps into an acceleration at k=40 (model mismatch), under four process-noise scales Q; record final Kalman gain, the filter's reported position sigma vs its actual error after the manoeuvre, and the overconfidence ratio (actual RMSE / reported sigma).",
           "note": "raw divergence behaviour of a preserved Kalman filter; NOT a tuning ranking. The failed branch is the overconfident/'smug' filter: with Q too small the gain collapses, the filter ignores measurements, and its reported confidence detaches from its true error. A matched Q is the tracking control.",
           "rows": rows}
    op = HERE / ("ESTIMATION_DIVERGENCE_%s.json" % DATE)
    op.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    for r in rows:
        print("Q=%-8g gain_final=%-9.4g reported_sigma=%-9.4g actual_err=%-9.4g rmse_tail=%-9.4g overconf=%-8s diverged=%s" % (
            r["Q_scale"], r["final_gain"], r["reported_sigma_after_manoeuvre"], r["actual_abs_error_final"],
            r["actual_rmse_after_manoeuvre"],
            ("%.2f" % r["overconfidence_ratio_error_over_reported"]) if r["overconfidence_ratio_error_over_reported"] is not None else "na",
            r["diverged"]))
    print("wrote", op, len(rows), "rows")


def _q(s):
    return "'" + s.replace("'", "'\\''") + "'"


if __name__ == "__main__":
    main()
