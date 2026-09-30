"""HT-37e311ce05 / W5 controls (Pass 3 v2). No treatment code.

Arms written to control_rows.jsonl (one JSON row per (arm, seed, m), flushed):
  CALIBRATION     basis-pursuit exact-recovery indicator on 20 draws per m
                  (fixes m* for the sharpness window; must equal spec m_star)
  POSITIVE_CONTROL the effect by construction: for each (seed, m) the optimal
                  L1-cost cheater, i.e. the minimum-L1 element of the host's
                  measurement coset x_good + ker A (linear program). It is
                  paid full reward (A x = A x_good exactly).
  NULL_TWIN       evolved symbiont population, identical world, reward,
                  verification matrix, selection, mutation and cost scale,
                  but cost = c*||x||_2^2 (no sparsity geometry, so no L1
                  phase transition in the coset optimum).
  CHEAT           rows whose gap observable is injected as a step at m*
                  (success injected directly) while the stored genome is the
                  honest cooperator x_good.
Then evaluates the success clauses on PC / NULL_TWIN / CHEAT and the audit
(recompute the observable from the stored genome + world seed).
The treatment (evolution under L1 cost) is NOT implemented here.
"""
import json, os, sys, time, hashlib

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[v] = "1"
import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = json.load(open(os.path.join(HERE, "spec.json"), encoding="utf-8"))
P_ = SPEC["parameters"]
N, K = P_["n"], P_["k"]
GRID = list(range(P_["m_min"], P_["m_max"] + 1, P_["m_step"]))
M_STAR = P_["m_star"]
WIN = P_["window_half_width"]
POP, GENS, C, TAU = P_["pop"], P_["generations"], P_["c"], P_["tau"]
SIG, PMUT = P_["mut_sigma"], P_["mut_prob"]
SEEDS = list(range(P_["control_seeds"]))
CAL_SEEDS = list(range(1000, 1000 + P_["calibration_draws"]))
OUT = os.path.join(HERE, "control_rows.jsonl")


def world(seed, m):
    """Required set R and x_good depend on seed only; A on (seed, m)."""
    R = np.sort(np.random.default_rng(seed).choice(N, K, replace=False))
    xg = np.zeros(N)
    xg[R] = 1.0
    A = np.random.default_rng([seed, m]).normal(0.0, 1.0 / np.sqrt(m), (m, N))
    return R, xg, A


def benefit(X, R):  # delivered benefit
    return np.clip(X[..., R], 0.0, 1.0).mean(-1)


def reward(X, A, yg):  # host pays on measurement match only
    d = ((X @ A.T - yg) ** 2).sum(-1) / (TAU ** 2 * float(yg @ yg))
    return np.exp(-d / 2.0)


def gap_of(X, seed, m):
    R, xg, A = world(seed, m)
    X = np.atleast_2d(np.asarray(X, dtype=float))
    g = reward(X, A, A @ xg) - benefit(X, R)
    return float(np.median(g))


def l1min(A, y):
    n = A.shape[1]
    res = linprog(np.ones(2 * n), A_eq=np.hstack([A, -A]), b_eq=y,
                  bounds=(0, None), method="highs")
    assert res.status == 0, res.message
    return res.x[:n] - res.x[n:]


def evolve_l2_twin(seed, m):
    R, xg, A = world(seed, m)
    yg = A @ xg
    rng = np.random.default_rng([seed, m, 7])
    X = np.tile(xg, (POP, 1))
    half = POP // 2
    for _ in range(GENS):
        f = reward(X, A, yg) - C * (X ** 2).sum(1)
        par = X[np.argsort(-f, kind="stable")[:half]]
        X = par[rng.integers(0, half, POP)]
        X = X + rng.normal(0.0, SIG, X.shape) * (rng.random(X.shape) < PMUT)
    return X


def curve_stats(gbar):
    """gbar: dict m -> seed-mean gap. Returns the clause statistics."""
    lo, hi = gbar[GRID[0]], gbar[GRID[-1]]
    denom = lo - hi
    ok = denom >= P_["min_total_drop"]
    sharp = (gbar[M_STAR - WIN] - gbar[M_STAR + WIN]) / denom if ok else 0.0
    completion = (lo - gbar[M_STAR + WIN]) / denom if ok else 0.0
    high = [m for m in GRID if m >= P_["high_m_from"]]
    H = float(np.mean([gbar[m] for m in high]))
    return {"S1_completion": float(completion), "S2_high_m_gap": H,
            "sharpness_secondary": float(sharp),
            "total_drop": float(denom), "g_lo": float(lo), "g_hi": float(hi)}


def main():
    t0 = time.process_time()
    f = open(OUT, "w", encoding="utf-8")

    def emit(row):
        f.write(json.dumps(row) + "\n")
        f.flush()

    # calibration of m*
    frac = {}
    for m in GRID:
        ok = 0
        for s in CAL_SEEDS:
            R, xg, A = world(s, m)
            x = l1min(A, A @ xg)
            ok += int(np.abs(x - xg).max() < 1e-4)
        frac[m] = ok / len(CAL_SEEDS)
        emit({"arm": "CALIBRATION", "m": m, "bp_recovery_frac": frac[m]})
    m_star_cal = next(m for m in GRID if frac[m] >= 0.5)

    per_arm = {"POSITIVE_CONTROL": {}, "NULL_TWIN": {}, "CHEAT": {}}
    for seed in SEEDS:
        for m in GRID:
            R, xg, A = world(seed, m)
            x = l1min(A, A @ xg)
            g = gap_of(x, seed, m)
            per_arm["POSITIVE_CONTROL"][(seed, m)] = g
            emit({"arm": "POSITIVE_CONTROL", "seed": seed, "m": m, "gap": g,
                  "l1": float(np.abs(x).sum()), "recovered": bool(np.abs(x - xg).max() < 1e-4),
                  "genome": np.round(x, 6).tolist()})
    for seed in SEEDS:
        for m in GRID:
            X = evolve_l2_twin(seed, m)
            g = gap_of(X, seed, m)
            per_arm["NULL_TWIN"][(seed, m)] = g
            R, xg, A = world(seed, m)
            emit({"arm": "NULL_TWIN", "seed": seed, "m": m, "gap": g,
                  "median_reward": float(np.median(reward(X, A, A @ xg))),
                  "median_benefit": float(np.median(benefit(X, R))),
                  "genome_pop": np.round(X, 4).tolist()})
    for seed in SEEDS:
        for m in GRID:
            R, xg, A = world(seed, m)
            g = 0.8 if m < M_STAR else 0.0  # injected success
            per_arm["CHEAT"][(seed, m)] = g
            emit({"arm": "CHEAT", "seed": seed, "m": m, "gap": g,
                  "genome": xg.tolist()})
    f.close()

    # audit: recompute every stored observable from its stored genome
    flagged = {a: 0 for a in per_arm}
    total = {a: 0 for a in per_arm}
    for line in open(OUT, encoding="utf-8"):
        r = json.loads(line)
        if r["arm"] == "CALIBRATION":
            continue
        G = r.get("genome_pop", r.get("genome"))
        g2 = gap_of(G, r["seed"], r["m"])
        total[r["arm"]] += 1
        if abs(g2 - r["gap"]) > 1e-3:
            flagged[r["arm"]] += 1

    stats = {}
    for a, d in per_arm.items():
        gbar = {m: float(np.mean([d[(s, m)] for s in SEEDS])) for m in GRID}
        stats[a] = curve_stats(gbar)
        stats[a]["curve"] = gbar
    summary = {"m_star_calibrated": m_star_cal, "m_star_spec": M_STAR,
               "calibration": frac, "stats": stats,
               "audit_flagged": flagged, "audit_total": total,
               "cpu_seconds": time.process_time() - t0,
               "rows_sha256": hashlib.sha256(open(OUT, "rb").read()).hexdigest()}
    json.dump(summary, open(os.path.join(HERE, "control_summary.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k != "calibration"}, indent=1))


if __name__ == "__main__":
    main()
