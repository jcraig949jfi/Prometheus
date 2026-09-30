"""HT-974471f045 / W1 -- PHASE 1 pilot: POSITIVE_CONTROL, CHEAT, NULL_TWIN.

Contains the shared ESN/evolution core (used unchanged by world.py in phase 2)
and the three pilot arms. No treatment (sediment) code lives here.
See NOTES.md for every parameter and reading.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import json, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

P = dict(POP=30, N=50, DENSITY=0.10, LAM=1e-4, T=300, WASH=50, GENS=80,
         SWITCH=40, EPS=0.05, FEWSHOT_N=20, PC_N=2000, RHO=0.9, LEAK=0.5,
         MUT_REL=0.1, N_ELITE_KEEP=5, N_PARENTS=10, N_OBS_ELITES=5,
         FEW_R=5, TRAIN_LIFE=150, U_LO=0.0, U_HI=0.5, SEEDS=list(range(10)))


# ---------------------------------------------------------------- tasks
def gen_input(rng, T):
    return rng.uniform(P["U_LO"], P["U_HI"], size=T)


def target_A(u):
    y = np.zeros_like(u)
    y[5:] = u[:-5]
    return y


def target_B(u):
    y = np.zeros_like(u)
    for t in range(4, len(u) - 1):
        y[t + 1] = (0.3 * y[t] + 0.05 * y[t] * y[t - 4:t + 1].sum()
                    + 1.5 * u[t - 4] * u[t] + 0.1)
    return y


def task_io(rng, task, T):
    """Returns (u, y, redraws). NARMA divergence guard (NOTES 7)."""
    redraws = 0
    while True:
        u = gen_input(rng, T)
        y = target_A(u) if task == "A" else target_B(u)
        if np.all(np.isfinite(y)) and np.max(np.abs(y)) <= 10:
            return u, y, redraws
        redraws += 1


# ---------------------------------------------------------------- ESN
def spectral_radius(W):
    return np.max(np.abs(np.linalg.eigvals(W)), axis=-1)


def rescale(W):
    """W (..., N, N) -> rescaled to rho exactly P['RHO']."""
    r = spectral_radius(W)
    return W * (P["RHO"] / r)[..., None, None]


def init_population(rng):
    N, POP = P["N"], P["POP"]
    mask = rng.random((POP, N, N)) < P["DENSITY"]
    W = np.where(mask, rng.standard_normal((POP, N, N)), 0.0)
    W = rescale(W)
    Win = rng.uniform(-1, 1, size=(POP, N))
    return W, Win, mask


def run_esn(W, Win, u):
    """Batched. W (B,N,N), Win (B,N), u (T,) -> states (B, T-WASH, N)."""
    B, N = Win.shape
    a = P["LEAK"]
    x = np.zeros((B, N))
    out = np.empty((B, len(u), N))
    for t in range(len(u)):
        pre = np.einsum("bij,bj->bi", W, x) + Win * u[t]
        x = (1 - a) * x + a * np.tanh(pre)
        out[:, t] = x
    return out[:, P["WASH"]:]


def add_bias(X):
    return np.concatenate([X, np.ones(X.shape[:-1] + (1,))], axis=-1)


def ridge(X, y, lam=None):
    """X (B,n,d) with bias col, y (n,) or (B,n) -> w (B,d). Dual form if n<d."""
    lam = P["LAM"] if lam is None else lam
    B, n, d = X.shape
    Y = np.broadcast_to(y, (B, n))
    if n >= d:
        A = np.einsum("bni,bnj->bij", X, X) + lam * np.eye(d)
        rhs = np.einsum("bni,bn->bi", X, Y)
        return np.linalg.solve(A, rhs[..., None])[..., 0]
    K = np.einsum("bid,bjd->bij", X, X) + lam * np.eye(n)
    alpha = np.linalg.solve(K, Y[..., None])[..., 0]
    return np.einsum("bnd,bn->bd", X, alpha)


def nrmse(yhat, y):
    return np.sqrt(np.mean((yhat - y) ** 2, axis=-1) / np.var(y, axis=-1))


def life(W, Win, u, y):
    """Lifetime: ridge on first TRAIN_LIFE post-washout steps, fitness on rest."""
    S = add_bias(run_esn(W, Win, u))
    yy = y[P["WASH"]:]
    k = P["TRAIN_LIFE"]
    w = ridge(S[:, :k], yy[:k])
    yhat = np.einsum("bnd,bd->bn", S[:, k:], w)
    return nrmse(yhat, np.broadcast_to(yy[k:], yhat.shape)), w[:, :-1]


def input_like_unit(rng):
    v = rng.uniform(-1, 1, size=P["N"])
    return v / np.linalg.norm(v)


# ---------------------------------------------------------------- deposits
def deposit_null(W, w_parent, drng):
    """Null twin: W <- W + eps v r^T, r random, ||r|| = ||w_parent||."""
    v = input_like_unit(drng)
    r = drng.standard_normal(P["N"])
    r *= np.linalg.norm(w_parent) / np.linalg.norm(r)
    return W + P["EPS"] * np.outer(v, r)


# ---------------------------------------------------------------- evolution
def streams(seed):
    ss = np.random.SeedSequence([974471, 1, seed])
    init, inp, mut, dep, meas = ss.spawn(5)
    return (np.random.default_rng(init), np.random.default_rng(inp),
            np.random.default_rng(mut), np.random.default_rng(dep),
            np.random.default_rng(meas))


def evolve(seed, deposit):
    """deposit: None or f(W, w_parent, drng) -> W. Returns final population
    info + gen-0 elites. Mutation/selection/inputs use streams shared across
    arms (common random numbers)."""
    r_init, r_inp, r_mut, r_dep, _ = streams(seed)
    W, Win, mask = init_population(r_init)
    POP, N = P["POP"], P["N"]
    redraws = 0
    gen0 = None
    hist = []
    for g in range(P["GENS"] + 1):
        task = "A" if g <= P["SWITCH"] else "B"
        u, y, rd = task_io(r_inp, task, P["T"] + P["WASH"])
        redraws += rd
        fit, wout = life(W, Win, u, y)
        order = np.argsort(fit, kind="stable")
        hist.append(float(np.mean(fit[order[:P["N_OBS_ELITES"]]])))
        if g == 0:
            e = order[:P["N_OBS_ELITES"]]
            gen0 = (W[e].copy(), Win[e].copy())
        if g == P["GENS"]:
            break
        keep = order[:P["N_ELITE_KEEP"]]
        parents = order[:P["N_PARENTS"]]
        n_off = POP - len(keep)
        pidx = parents[r_mut.integers(0, len(parents), size=n_off)]
        noise = r_mut.standard_normal((n_off, N, N))
        Wc = W[pidx].copy()
        m = mask[pidx]
        rms = np.sqrt(np.sum(np.where(m, Wc, 0) ** 2, axis=(1, 2)) / m.sum(axis=(1, 2)))
        Wc = Wc + np.where(m, noise, 0.0) * (P["MUT_REL"] * rms)[:, None, None]
        if deposit is not None:
            for i in range(n_off):
                Wc[i] = deposit(Wc[i], wout[pidx[i]], r_dep)
        Wc = rescale(Wc)
        W = np.concatenate([W[keep], Wc])
        Win = np.concatenate([Win[keep], Win[pidx]])
        mask = np.concatenate([mask[keep], m])
    e = order[:P["N_OBS_ELITES"]]
    return dict(W=W[e].copy(), Win=Win[e].copy(), gen0=gen0,
                final_fit=fit[e].tolist(), elite_hist=hist, narma_redraws=redraws)


# ---------------------------------------------------------------- measurement
def fewshot_A(W, Win, seed, cheat=False):
    """Few-shot task-A NRMSE per elite, mean over FEW_R draws. Same
    measurement stream for every arm (seeded by seed only)."""
    _, _, _, _, r_meas = streams(seed)
    B = W.shape[0]
    L = P["T"]
    vals = np.zeros((P["FEW_R"], B))
    for k in range(P["FEW_R"]):
        u, y, _ = task_io(r_meas, "A", P["T"] + P["WASH"])
        idx = r_meas.permutation(L)
        tr, te = idx[:P["FEWSHOT_N"]], idx[P["FEWSHOT_N"]:]
        S = add_bias(run_esn(W, Win, u))
        yy = y[P["WASH"]:]
        w = ridge(S[:, tr], yy[tr])
        yhat = np.einsum("bnd,bd->bn", S[:, te], w)
        if cheat:  # success injected directly into the observable
            yhat = yy[te][None, :] + 1e-3 * r_meas.standard_normal(yhat.shape)
        vals[k] = nrmse(yhat, np.broadcast_to(yy[te], yhat.shape))
    return vals.mean(axis=0)


def optimal_A_readout(W, Win, seed, channel_lag=0):
    """Ridge-optimal task-A readout with n=PC_N samples, per elite.
    channel_lag=1 (pilot REPAIR, attempt 2; NOTES 'Pilot log'): the readout is
    fitted to u_{t-5+1} = u_{t-4} on x_t, so that the deposit's one-step
    feedback (W x_t -> x_{t+1}) re-injects exactly the task-A target u_{(t+1)-5}."""
    ss = np.random.SeedSequence([974471, 2, seed])
    rng = np.random.default_rng(ss)
    u, y, _ = task_io(rng, "A", P["PC_N"] + P["WASH"])
    if channel_lag:
        y = np.zeros_like(u)
        y[5 - channel_lag:] = u[:-(5 - channel_lag)]
    S = add_bias(run_esn(W, Win, u))
    return ridge(S, y[P["WASH"]:])[:, :-1]


def gen80_deposit(W, w_list, seed, content=True):
    """Deposit once at gen 80: content=True -> w_A* (positive control);
    content=False -> random r with ||r|| = ||w_A*|| (its null twin)."""
    rng = np.random.default_rng(np.random.SeedSequence([974471, 3, seed]))
    Wn = W.copy()
    for i in range(W.shape[0]):
        v = input_like_unit(rng)
        r = rng.standard_normal(P["N"])
        r *= np.linalg.norm(w_list[i]) / np.linalg.norm(r)
        vec = w_list[i] if content else r
        Wn[i] = W[i] + P["EPS"] * np.outer(v, vec)
    return rescale(Wn)


# ---------------------------------------------------------------- pilot arms
def pilot_arms(seed, nt=None, channel_lag=0):
    """Runs NULL_TWIN evolution (or reuses nt), then PC, its content-free
    twin, and CHEAT on the same gen-80 elites. Returns list of rows."""
    if nt is None:
        nt = evolve(seed, deposit_null)
    W, Win = nt["W"], nt["Win"]
    base = fewshot_A(W, Win, seed)
    g0 = fewshot_A(*nt["gen0"], seed)
    wA = optimal_A_readout(W, Win, seed, channel_lag)
    Wpc = gen80_deposit(W, wA, seed, content=True)
    Wpn = gen80_deposit(W, wA, seed, content=False)
    pc = fewshot_A(Wpc, Win, seed)
    pcn = fewshot_A(Wpn, Win, seed)
    ch = fewshot_A(W, Win, seed, cheat=True)
    common = dict(seed=seed, params=P, pc_channel_lag=channel_lag, final_fitB_elites=nt["final_fit"],
                  narma_redraws=nt["narma_redraws"])
    rows = [
        dict(arm="NULL_TWIN", nrmse_A=float(base.mean()), per_elite=base.tolist(),
             gen0_elites_nrmse_A=float(g0.mean()), elite_fit_hist=nt["elite_hist"], **common),
        dict(arm="POSITIVE_CONTROL", nrmse_A=float(pc.mean()), per_elite=pc.tolist(),
             pre_deposit_nrmse_A=float(base.mean()),
             wA_norm=[float(np.linalg.norm(w)) for w in wA], **common),
        dict(arm="PC_NULL_TWIN", nrmse_A=float(pcn.mean()), per_elite=pcn.tolist(),
             pre_deposit_nrmse_A=float(base.mean()), **common),
        dict(arm="CHEAT", nrmse_A=float(ch.mean()), per_elite=ch.tolist(), **common),
    ]
    return rows


def cpu_log(script, t0, extra=None):
    rec = dict(script=script, cpu_s=time.process_time() - t0,
               utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    if extra:
        rec.update(extra)
    with open(os.path.join(HERE, "cpu_ledger.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def main():
    attempt = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    t0 = time.process_time()
    out = os.path.join(HERE, "pilot_rows.jsonl" if attempt == 1 else f"pilot_rows_attempt{attempt}.jsonl")
    with open(out, "w") as f:
        for s in P["SEEDS"]:
            for row in pilot_arms(s, channel_lag=0 if attempt == 1 else 1):
                row["attempt"] = attempt
                f.write(json.dumps(row) + "\n")
                f.flush()
            print("seed", s, "done", round(time.process_time() - t0, 1), "cpu s", flush=True)
    print(cpu_log("pilot.py", t0, dict(attempt=attempt)))


if __name__ == "__main__":
    main()
