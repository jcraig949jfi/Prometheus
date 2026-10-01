"""HT-37e311ce05 / W5 probe round 3: TREATMENT + re-run controls.

Imports the frozen ../controls.py (does NOT call its main(), which would
overwrite the frozen control_rows.jsonl). Writes probe/rows.jsonl, one
row per (arm, seed), flushed. See NOTES.md.
"""
import json, os, sys, time, importlib.util

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[v] = "1"
import numpy as np

PROBE = os.path.dirname(os.path.abspath(__file__))
WDIR = os.path.dirname(PROBE)
_spec = importlib.util.spec_from_file_location("w5_controls", os.path.join(WDIR, "controls.py"))
ctl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ctl)

OUT = os.path.join(PROBE, "rows.jsonl")
SEEDS = list(ctl.SPEC["seeds"]["treatment"])
assert SEEDS == list(ctl.SPEC["seeds"]["controls"]) == ctl.SEEDS
PARAMS = dict(ctl.P_)


def evolve_l1_treatment(seed, m):
    """controls.evolve_l2_twin with the cost term swapped to L1; nothing else."""
    R, xg, A = ctl.world(seed, m)
    yg = A @ xg
    rng = np.random.default_rng([seed, m, 7])
    X = np.tile(xg, (ctl.POP, 1))
    half = ctl.POP // 2
    for _ in range(ctl.GENS):
        f = ctl.reward(X, A, yg) - ctl.C * np.abs(X).sum(1)
        par = X[np.argsort(-f, kind="stable")[:half]]
        X = par[rng.integers(0, half, ctl.POP)]
        X = X + rng.normal(0.0, ctl.SIG, X.shape) * (rng.random(X.shape) < ctl.PMUT)
    return X


def evolved_row(arm, seed, evolve):
    per_m = {}
    for m in ctl.GRID:
        X = evolve(seed, m)
        Xs = np.round(X, 4)  # stored precision, as in controls.py
        R, xg, A = ctl.world(seed, m)
        per_m[str(m)] = {
            "gap": ctl.gap_of(X, seed, m),
            "median_reward": float(np.median(ctl.reward(X, A, A @ xg))),
            "median_benefit": float(np.median(ctl.benefit(X, R))),
            "median_l1": float(np.median(np.abs(X).sum(1))),
            "genome_pop": Xs.tolist(),
        }
    return {"arm": arm, "seed": seed, "per_m": per_m}


def main():
    t0 = time.process_time()
    f = open(OUT, "w", encoding="utf-8")

    def emit(row):
        row["params"] = PARAMS
        row["cpu_s_cum"] = time.process_time() - t0
        f.write(json.dumps(row) + "\n")
        f.flush()
        print(row["arm"], row.get("seed"), round(row["cpu_s_cum"], 1), flush=True)

    frac = {}
    for m in ctl.GRID:
        ok = 0
        for s in ctl.CAL_SEEDS:
            R, xg, A = ctl.world(s, m)
            x = ctl.l1min(A, A @ xg)
            ok += int(np.abs(x - xg).max() < 1e-4)
        frac[str(m)] = ok / len(ctl.CAL_SEEDS)
    emit({"arm": "CALIBRATION", "seed": None, "bp_recovery_frac": frac})

    for seed in SEEDS:
        per_m = {}
        for m in ctl.GRID:
            R, xg, A = ctl.world(seed, m)
            x = ctl.l1min(A, A @ xg)
            per_m[str(m)] = {"gap": ctl.gap_of(x, seed, m),
                             "l1": float(np.abs(x).sum()),
                             "recovered": bool(np.abs(x - xg).max() < 1e-4),
                             "genome": np.round(x, 6).tolist()}
        emit({"arm": "POSITIVE_CONTROL", "seed": seed, "per_m": per_m})

    for seed in SEEDS:
        per_m = {}
        for m in ctl.GRID:
            R, xg, A = ctl.world(seed, m)
            per_m[str(m)] = {"gap": 0.8 if m < ctl.M_STAR else 0.0,  # injected
                             "genome": xg.tolist()}
        emit({"arm": "CHEAT", "seed": seed, "per_m": per_m})

    for seed in SEEDS:
        emit(evolved_row("NULL_TWIN", seed, ctl.evolve_l2_twin))

    for seed in SEEDS:
        emit(evolved_row("TREATMENT", seed, evolve_l1_treatment))

    f.close()
    json.dump({"cpu_seconds": time.process_time() - t0},
              open(os.path.join(PROBE, "world_cpu.json"), "w"))


if __name__ == "__main__":
    main()
