"""HT-974471f045 / W5 controls (Pass 3 v2). NO TREATMENT CODE.

Arms written to control_rows.jsonl (one row per seed per arm, flushed):
  POSITIVE_CONTROL : low-budget arm = constructed task-carrying reservoirs
                     (delay chain broadcasting u1_{t-3}); high-budget arm =
                     reservoirs drawn from the gen-0 law (the hypothesis says
                     high budget leaves the reservoir near-random).
  CHEAT            : success injected into the observable: the low-arm
                     own-reservoir few-shot prediction of the task target is
                     replaced by the target itself (NRMSE_own = 0).
  NULL_TWIN        : neutral-drift populations (permuted-fitness twin in
                     distribution: same genealogy law, same mutation, same
                     generations, parents chosen without regard to fitness;
                     no fitness is computed). Low and high arms are two
                     independent drift runs.
Also a DIAGNOSTIC row per seed: selection pressure at each lifetime budget
(NRMSE of fresh gen-0 reservoir minus NRMSE of the constructed reservoir,
at n=8 and at n=200).
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import json, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "control_rows.jsonl")

# ---- frozen parameters (spec.json "size") ----
N = 40            # reservoir units
D_IN = 2          # input channels u1 (task), u2 (off-task)
DELAY = 3         # task: y_t = u1_{t-DELAY}; off-task: u2_{t-DELAY}
U_AMP = 0.5       # u ~ U[-U_AMP, U_AMP] iid
RHO0 = 0.9        # gen-0 spectral radius
RHO_MAX = 0.95    # births with rho > RHO_MAX are rescaled to RHO_MAX
WIN_AMP = 0.5     # gen-0 W_in ~ U[-WIN_AMP, WIN_AMP]
WASH, T = 50, 350
LAM = 1e-2        # ridge (with intercept; revision 1: was 1e-6)
N_LOW, N_HIGH = 8, 200   # lifetime readout sample budgets
N_EVAL = N_LOW    # instrument budget for the observable
R = 5             # repeats (fresh input + fresh replacement reservoir)
POP, GENS, N_ELITE_KEEP, PARENT_POOL = 20, 60, 4, 8   # revision 2: GENS was 30
MUT = 0.05        # relative mutation sd (revision 2: was 0.02)
N_OBS = 5         # individuals measured per population ("elites")
SEEDS = [0, 1, 2, 3, 4, 5]


def spectral_radius(W):
    return float(np.max(np.abs(np.linalg.eigvals(W))))


def gen0_reservoir(rng):
    W = rng.standard_normal((N, N))
    W *= RHO0 / spectral_radius(W)
    W_in = rng.uniform(-WIN_AMP, WIN_AMP, (N, D_IN))
    return W, W_in


def constructed_reservoir(rng):
    """Effect present by construction: task content u1_{t-3} in 37 units."""
    W = 0.05 * rng.standard_normal((N, N)) / np.sqrt(N)
    W_in = 0.05 * rng.uniform(-1, 1, (N, D_IN))
    # revision 1: chain gain 1.0 (was 2.0, which saturated tanh -> sign(u))
    W_in[0, 0] += 1.0          # x0_t ~ u1_t
    W[1, 0] += 1.0             # x1_t ~ u1_{t-1}
    W[2, 1] += 1.0             # x2_t ~ u1_{t-2}
    W[3:, 2] += 1.0            # x_i_t ~ u1_{t-3}, i >= 3
    r = spectral_radius(W)
    if r > RHO_MAX:
        W *= RHO_MAX / r
    return W, W_in


def run(W, W_in, u):
    x = np.zeros(N)
    X = np.empty((len(u), N))
    for t in range(len(u)):
        x = np.tanh(W @ x + W_in @ u[t])
        X[t] = x
    return X


def targets(u):
    y1 = np.zeros(len(u)); y2 = np.zeros(len(u))
    y1[DELAY:] = u[:-DELAY, 0]
    y2[DELAY:] = u[:-DELAY, 1]
    return y1, y2


def ridge_nrmse(X, y, n, rng):
    Xp, yp = X[WASH:], y[WASH:]
    idx = rng.permutation(len(yp))
    tr, te = idx[:n], idx[n:]
    A = np.hstack([Xp[tr], np.ones((n, 1))])
    w = A.T @ np.linalg.solve(A @ A.T + LAM * np.eye(n), yp[tr])  # min-norm ridge (dual)
    B = np.hstack([Xp[te], np.ones((len(te), 1))])
    e = B @ w - yp[te]
    return float(np.sqrt(np.mean(e ** 2) / np.var(yp[te])))


def gains(W, W_in, meas_seed, n, cheat=False):
    """Reservoir-attributed gain G = NRMSE(fresh gen-0 reservoir) - NRMSE(own),
    same inputs and same training indices, for task and off-task targets."""
    rng = np.random.default_rng(meas_seed)
    g_task, g_off, own_t, rep_t = [], [], [], []
    for r in range(R):
        u = rng.uniform(-U_AMP, U_AMP, (T, D_IN))
        Wr, Wir = gen0_reservoir(rng)
        idx_seed = int(rng.integers(2**31))
        y1, y2 = targets(u)
        Xo, Xr = run(W, W_in, u), run(Wr, Wir, u)
        no1 = 0.0 if cheat else ridge_nrmse(Xo, y1, n, np.random.default_rng(idx_seed))
        nr1 = ridge_nrmse(Xr, y1, n, np.random.default_rng(idx_seed))
        no2 = ridge_nrmse(Xo, y2, n, np.random.default_rng(idx_seed + 1))
        nr2 = ridge_nrmse(Xr, y2, n, np.random.default_rng(idx_seed + 1))
        g_task.append(nr1 - no1); g_off.append(nr2 - no2)
        own_t.append(no1); rep_t.append(nr1)
    return dict(G_task=float(np.mean(g_task)), G_off=float(np.mean(g_off)),
                nrmse_own_task=float(np.mean(own_t)), nrmse_rep_task=float(np.mean(rep_t)))


def mutate(W, W_in, rng):
    W = W + MUT * np.sqrt(np.mean(W ** 2)) * rng.standard_normal(W.shape)
    W_in = W_in + MUT * np.sqrt(np.mean(W_in ** 2)) * rng.standard_normal(W_in.shape)
    r = spectral_radius(W)
    if r > RHO_MAX:
        W *= RHO_MAX / r
    return W, W_in


def drift_population(rng):
    """Neutral drift = permuted-fitness twin in distribution. No fitness."""
    pop = [gen0_reservoir(rng) for _ in range(POP)]
    for g in range(GENS):
        order = rng.permutation(POP)          # a random ranking stands in for permuted fitness
        keep = [pop[i] for i in order[:N_ELITE_KEEP]]
        pool = [pop[i] for i in order[:PARENT_POOL]]
        kids = [mutate(*pool[rng.integers(PARENT_POOL)], rng) for _ in range(POP - N_ELITE_KEEP)]
        pop = keep + kids
    order = rng.permutation(POP)
    return [pop[i] for i in order[:N_OBS]]


def arm_stats(pop_low, pop_high, seed, cheat=False):
    meas = 10_000 + seed           # same measurement stream for every arm (CRN)
    lo = [gains(W, Wi, meas + k, N_EVAL, cheat=cheat) for k, (W, Wi) in enumerate(pop_low)]
    hi = [gains(W, Wi, meas + k, N_EVAL) for k, (W, Wi) in enumerate(pop_high)]
    m = lambda L, key: float(np.mean([d[key] for d in L]))
    return dict(G_task_low=m(lo, "G_task"), G_off_low=m(lo, "G_off"),
                G_task_high=m(hi, "G_task"), G_off_high=m(hi, "G_off"),
                nrmse_own_task_low=m(lo, "nrmse_own_task"),
                nrmse_rep_task_low=m(lo, "nrmse_rep_task"))


def emit(fh, row):
    fh.write(json.dumps(row) + "\n"); fh.flush(); os.fsync(fh.fileno())


def main(tag):
    t0 = time.process_time()
    with open(ROWS, "a", encoding="utf-8") as fh:
        for s in SEEDS:
            rng = np.random.default_rng(s)
            pc_low = [constructed_reservoir(rng) for _ in range(N_OBS)]
            pc_high = [gen0_reservoir(rng) for _ in range(N_OBS)]
            emit(fh, dict(world="W5", run=tag, arm="POSITIVE_CONTROL", seed=s, **arm_stats(pc_low, pc_high, s)))
            emit(fh, dict(world="W5", run=tag, arm="CHEAT", seed=s, **arm_stats(pc_high, pc_high, s, cheat=True)))
            trng = np.random.default_rng(1_000 + s)
            tw_low, tw_high = drift_population(trng), drift_population(trng)
            emit(fh, dict(world="W5", run=tag, arm="NULL_TWIN", seed=s, **arm_stats(tw_low, tw_high, s)))
            # diagnostic: selection pressure at each lifetime budget
            d8 = [gains(W, Wi, 20_000 + s * 10 + k, N_LOW) for k, (W, Wi) in enumerate(pc_low)]
            d200 = [gains(W, Wi, 20_000 + s * 10 + k, N_HIGH) for k, (W, Wi) in enumerate(pc_low)]
            emit(fh, dict(world="W5", run=tag, arm="DIAGNOSTIC_PRESSURE", seed=s,
                          pressure_n8=float(np.mean([d["G_task"] for d in d8])),
                          pressure_n200=float(np.mean([d["G_task"] for d in d200])),
                          nrmse_constructed_n200=float(np.mean([d["nrmse_own_task"] for d in d200])),
                          nrmse_gen0_n200=float(np.mean([d["nrmse_rep_task"] for d in d200]))))
        emit(fh, dict(world="W5", run=tag, arm="CPU", cpu_seconds=time.process_time() - t0))


# ---- success clauses (same thresholds as spec.json; used for controls and treatment) ----
THRESH = {"S1": 0.30, "S2": 0.25, "S3": 0.30, "S4": 0.25}


def clause_values(rows, arm, twin_arm="NULL_TWIN"):
    A = [r for r in rows if r["arm"] == arm]
    Tw = [r for r in rows if r["arm"] == twin_arm]
    m = lambda L, f: float(np.mean([f(r) for r in L]))
    return {
        "S1": m(A, lambda r: r["G_task_low"]),
        "S2": m(A, lambda r: r["G_task_low"] - r["G_task_high"]),
        "S3": m(A, lambda r: r["G_task_low"] - r["G_off_low"]),
        "S4": m(A, lambda r: r["G_task_low"]) - m(Tw, lambda r: r["G_task_low"]),
    }


def passes(vals):
    return {k: bool(vals[k] >= THRESH[k]) for k in THRESH}


def attainability(tag):
    rows = [json.loads(l) for l in open(ROWS, encoding="utf-8")]
    rows = [r for r in rows if r.get("run") == tag]
    pc, tw, ch = (clause_values(rows, a) for a in ("POSITIVE_CONTROL", "NULL_TWIN", "CHEAT"))
    return pc, tw, ch


if __name__ == "__main__":
    tag = sys.argv[1] if len(sys.argv) > 1 else "r1"
    if len(sys.argv) > 2 and sys.argv[2] == "--attain":
        pc, tw, ch = attainability(tag)
        print(json.dumps({"pc": pc, "twin": tw, "cheat": ch, "cheat_pass": passes(ch)}, indent=1))
    else:
        main(tag)
