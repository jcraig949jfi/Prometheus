"""HT-974471f045 / W6 controls (Pass 3 v2). NO TREATMENT CODE.

World: heritable readout w (N) and heritable input template M_in (N x D);
each individual's reservoir is resampled at birth: W_in = M_in + SIGMA*xi,
W fresh random (spectral radius 0.9). Nothing is learned in life.
Target y_t = u1_t - u2_t (a contrast; the all-ones mean field cannot carry it).

Arms written to control_rows.jsonl (one row per seed per arm, flushed):
  POSITIVE_CONTROL : constructed genomes whose readout addresses a property
                     invariant across resamples (units 0..19 templated on u1
                     with w=+1, units 20..39 on u2 with w=-1).
  CHEAT            : success injected into the observable: the readout
                     output is replaced by the target (corr^2 = 1) for w and
                     w_perp; the all-ones readout is measured normally.
  NULL_TWIN        : neutral-drift populations (permuted-fitness twin in
                     distribution; no fitness computed).
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import json, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "control_rows.jsonl")

N, D_IN = 40, 8
SIGMA = 0.3        # resampling noise on W_in (not heritable)
RHO = 0.9          # recurrent W resampled each birth, dense N(0,1) rescaled
U_AMP = 1.0        # u ~ U[-1,1] iid, 8 channels
WASH, T = 50, 300
M0_SD, W0_SD = 0.5, 1.0     # gen-0 law: M_in ~ N(0, M0_SD^2), w ~ N(0, W0_SD^2)
N_RESAMPLE = 20    # L5: evaluate across 20 resampled reservoirs
POP, GENS, N_ELITE_KEEP, PARENT_POOL = 20, 60, 4, 8
MUT_M, MUT_W = 0.05, 0.05   # mutation sd: M_in absolute; w relative to rms(w)
N_OBS = 5
SEEDS = [0, 1, 2, 3, 4, 5]


def target(u):
    return u[:, 0] - u[:, 1]


def sample_reservoir(M_in, rng):
    W = rng.standard_normal((N, N))
    W *= RHO / np.max(np.abs(np.linalg.eigvals(W)))
    W_in = M_in + SIGMA * rng.standard_normal(M_in.shape)
    return W, W_in


def run(W, W_in, u):
    x = np.zeros(N)
    X = np.empty((len(u), N))
    for t in range(len(u)):
        x = np.tanh(W @ x + W_in @ u[t])
        X[t] = x
    return X


def corr2(a, b):
    a = a - a.mean(); b = b - b.mean()
    den = np.sqrt((a @ a) * (b @ b))
    return 0.0 if den == 0 else float((a @ b / den) ** 2)


def invariance(M_in, w, meas_seed, cheat=False):
    """L5: fixed heritable readout evaluated on N_RESAMPLE fresh reservoirs
    drawn from the individual's own distribution. Returns mean corr^2 of
    w.x, w_perp.x (w minus its all-ones component) and 1.x with the target."""
    rng = np.random.default_rng(meas_seed)
    w_perp = w - w.mean()
    I_full, I_perp, I_ones = [], [], []
    for _ in range(N_RESAMPLE):
        u = rng.uniform(-U_AMP, U_AMP, (T, D_IN))
        W, W_in = sample_reservoir(M_in, rng)
        X = run(W, W_in, u)[WASH:]
        y = target(u)[WASH:]
        if cheat:
            I_full.append(1.0); I_perp.append(1.0)
        else:
            I_full.append(corr2(X @ w, y)); I_perp.append(corr2(X @ w_perp, y))
        I_ones.append(corr2(X.sum(1), y))
    return dict(I_full=float(np.mean(I_full)), I_perp=float(np.mean(I_perp)),
                I_ones=float(np.mean(I_ones)), I_perp_sd=float(np.std(I_perp)))


def gen0_genome(rng):
    return M0_SD * rng.standard_normal((N, D_IN)), W0_SD * rng.standard_normal(N)


def constructed_genome(rng):
    M = 0.05 * rng.standard_normal((N, D_IN))
    M[:20, 0] += 1.0
    M[20:, 1] += 1.0
    w = np.r_[np.ones(20), -np.ones(20)] + 0.05 * rng.standard_normal(N)
    return M, w


def mutate(M, w, rng):
    return (M + MUT_M * rng.standard_normal(M.shape),
            w + MUT_W * np.sqrt(np.mean(w ** 2)) * rng.standard_normal(w.shape))


def drift_population(rng):
    """Neutral drift = permuted-fitness twin in distribution. No fitness."""
    pop = [gen0_genome(rng) for _ in range(POP)]
    for g in range(GENS):
        order = rng.permutation(POP)
        keep = [pop[i] for i in order[:N_ELITE_KEEP]]
        pool = [pop[i] for i in order[:PARENT_POOL]]
        pop = keep + [mutate(*pool[rng.integers(PARENT_POOL)], rng) for _ in range(POP - N_ELITE_KEEP)]
    order = rng.permutation(POP)
    return [pop[i] for i in order[:N_OBS]]


def arm_stats(pop, seed, cheat=False):
    L = [invariance(M, w, 10_000 + 100 * seed + k, cheat=cheat) for k, (M, w) in enumerate(pop)]
    return {k: float(np.mean([d[k] for d in L])) for k in L[0]}


def emit(fh, row):
    fh.write(json.dumps(row) + "\n"); fh.flush(); os.fsync(fh.fileno())


def main(tag):
    t0 = time.process_time()
    with open(ROWS, "a", encoding="utf-8") as fh:
        for s in SEEDS:
            rng = np.random.default_rng(s)
            pc = [constructed_genome(rng) for _ in range(N_OBS)]
            g0 = [gen0_genome(rng) for _ in range(N_OBS)]
            emit(fh, dict(world="W6", run=tag, arm="POSITIVE_CONTROL", seed=s, **arm_stats(pc, s)))
            emit(fh, dict(world="W6", run=tag, arm="CHEAT", seed=s, **arm_stats(g0, s, cheat=True)))
            tw = drift_population(np.random.default_rng(1_000 + s))
            emit(fh, dict(world="W6", run=tag, arm="NULL_TWIN", seed=s, **arm_stats(tw, s)))
        emit(fh, dict(world="W6", run=tag, arm="CPU", cpu_seconds=time.process_time() - t0))


THRESH = {"S1": 0.60, "S2": 0.30, "S3": 0.25}   # revision 1: S1 was 0.40 (single-channel decoding reaches 0.5)


def clause_values(rows, arm, twin_arm="NULL_TWIN"):
    A = [r for r in rows if r["arm"] == arm]
    Tw = [r for r in rows if r["arm"] == twin_arm]
    m = lambda L, f: float(np.mean([f(r) for r in L]))
    return {"S1": m(A, lambda r: r["I_perp"]),
            "S2": m(A, lambda r: r["I_perp"] - r["I_ones"]),
            "S3": m(A, lambda r: r["I_perp"]) - m(Tw, lambda r: r["I_perp"])}


def passes(vals):
    return {k: bool(vals[k] >= THRESH[k]) for k in THRESH}


def attainability(tag):
    rows = [json.loads(l) for l in open(ROWS, encoding="utf-8")]
    rows = [r for r in rows if r.get("run") == tag]
    return tuple(clause_values(rows, a) for a in ("POSITIVE_CONTROL", "NULL_TWIN", "CHEAT"))


if __name__ == "__main__":
    tag = sys.argv[1] if len(sys.argv) > 1 else "r1"
    if len(sys.argv) > 2 and sys.argv[2] == "--attain":
        pc, tw, ch = attainability(tag)
        print(json.dumps({"pc": pc, "twin": tw, "cheat": ch, "cheat_pass": passes(ch)}, indent=1))
    else:
        main(tag)
