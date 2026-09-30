"""HT-e743909f97/W3 shared core: model, exact grid posterior, pilot arms.
No treatment arm lives here (see NOTES.md A5)."""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np

N = 256; T = 2000; SWITCH = 1000; SIGMA2 = 0.5; H = 1.0 / 2000
NBIN = 64; LO, HI = -2.0, 2.0; WIDTH = (HI - LO) / NBIN
CENTRES = LO + WIDTH * (np.arange(NBIN) + 0.5)
K = 0.01; ALPHA = 0.1; WIN = (750, 1000); RT_FLOOR = WIDTH / 2; RT_CENSOR = T - SWITCH
SEEDS = list(range(30))
PARAMS = dict(N=N, T=T, SWITCH=SWITCH, SIGMA2=SIGMA2, H=H, NBIN=NBIN, LO=LO, HI=HI,
              K=K, ALPHA=ALPHA, WIN=list(WIN), RT_FLOOR=RT_FLOOR, RT_CENSOR=RT_CENSOR)


def world(seed):
    """Truths (grid centres) and the observation sequence d_t = theta_t + w_t."""
    rng = np.random.default_rng([seed, 1])
    c0 = np.where(np.abs(CENTRES) <= 1.0)[0]
    i0 = int(rng.choice(c0))
    ok = np.where((np.abs(CENTRES - CENTRES[i0]) >= 0.75) & (np.abs(CENTRES - CENTRES[i0]) <= 1.25)
                  & (np.abs(CENTRES) <= 1.5))[0]
    i1 = int(rng.choice(ok))
    th = np.where(np.arange(T) < SWITCH, CENTRES[i0], CENTRES[i1])
    d = th + rng.normal(0.0, np.sqrt(SIGMA2), T)
    return th, d


def exact_posterior(d):
    """Forward HMM filter on the 64 centres; returns log posterior (T, NBIN)."""
    out = np.empty((len(d), NBIN)); lp = np.full(NBIN, -np.log(NBIN))
    for t, dt in enumerate(d):
        if t > 0:
            lp = np.logaddexp(np.log1p(-H) + lp, np.log(H / NBIN))
        lp = lp - (dt - CENTRES) ** 2
        lp -= np.logaddexp.reduce(lp)
        out[t] = lp
    return out


def bin_index(theta):
    return np.clip(np.floor((theta - LO) / WIDTH).astype(int), 0, NBIN - 1)


def kl(q, logp):
    m = q > 0
    return float(np.sum(q[m] * (np.log(q[m]) - logp[m])))


def retrack(mean, sd, th):
    """first s>=0 with |mean-theta1| <= max(sd, floor) at step SWITCH+s; censored."""
    tgt = th[SWITCH]
    ok = np.abs(mean[SWITCH:] - tgt) <= np.maximum(sd[SWITCH:], RT_FLOOR)
    idx = np.flatnonzero(ok)
    return (int(idx[0]), False) if idx.size else (RT_CENSOR, True)


def summarise(arm, seed, kls, mean, sd, th, extra=None):
    rt, cens = retrack(mean, sd, th)
    row = dict(arm=arm, seed=seed, stat_kl=float(np.mean(kls[WIN[0]:WIN[1]])),
               late_kl=float(np.mean(kls[1750:2000])), rt=rt, rt_censored=cens,
               theta0=float(th[0]), theta1=float(th[SWITCH]), params=PARAMS)
    if extra:
        row.update(extra)
    return row


def run_replicator(seed, sd_fn, arm):
    """Bootstrap replicator: reweight exp(-e^2), multinomial resample, measure,
    mutate with per-clone sd from sd_fn(ema, t, rng, state)."""
    th, d = world(seed); logp = exact_posterior(d)
    rng = np.random.default_rng([seed, 2])
    theta = rng.uniform(LO, HI, N); ema = np.zeros(N)
    kls = np.empty(T); mean = np.empty(T); sd = np.empty(T); applied = []
    state = {}
    for t in range(T):
        e2 = (d[t] - theta) ** 2
        ema = e2 if t == 0 else (1 - ALPHA) * ema + ALPHA * e2
        w = np.exp(-(e2 - e2.min())); w /= w.sum()
        idx = rng.choice(N, N, p=w); theta = theta[idx]; ema = ema[idx]
        q = np.bincount(bin_index(theta), minlength=NBIN) / N
        kls[t] = kl(q, logp[t]); mean[t] = theta.mean(); sd[t] = theta.std()
        s = sd_fn(ema, t, rng, state)
        applied.append(float(np.mean(s)))
        theta = np.clip(theta + rng.normal(0.0, 1.0, N) * s, LO, HI)
    return summarise(arm, seed, kls, mean, sd, th,
                     dict(mean_sd_applied=float(np.mean(applied)),
                          sd_applied_pre=float(np.mean(applied[:SWITCH])),
                          sd_applied_post50=float(np.mean(applied[SWITCH:SWITCH + 50]))))


def errscaled_sd(ema):
    """The spec's error-scaled sd rule; used by the null twin to build its pool."""
    return K * np.sqrt(ema)


def null_twin_sd(ema, t, rng, state):
    """Compute the error-scaled sds, append to the pool of all sds so far
    (all clones, all steps), apply a uniform draw from the pool to each clone."""
    buf = state.get("buf")
    if buf is None:
        buf = state["buf"] = np.empty(T * N)
    buf[t * N:(t + 1) * N] = errscaled_sd(ema)
    return buf[rng.integers(0, (t + 1) * N, N)]


def run_null_twin(seed):
    return run_replicator(seed, null_twin_sd, "NULL_TWIN")


def run_positive(seed):
    """Replicator equation on frequencies, zero mutation, clones = 4 per centre."""
    th, d = world(seed); logp = exact_posterior(d)
    lw = np.full(NBIN, -np.log(NBIN))
    kls = np.empty(T); mean = np.empty(T); sd = np.empty(T)
    for t in range(T):
        lw = lw - (d[t] - CENTRES) ** 2; lw -= np.logaddexp.reduce(lw)
        q = np.exp(lw)
        kls[t] = kl(q, logp[t]); mean[t] = q @ CENTRES
        sd[t] = np.sqrt(max(q @ CENTRES ** 2 - mean[t] ** 2, 0.0))
    return summarise("POSITIVE_CONTROL", seed, kls, mean, sd, th)


def run_cheat(seed):
    """Success injected into the observable: q := exact posterior, mean := truth."""
    th, d = world(seed); logp = exact_posterior(d)
    kls = np.empty(T); sd = np.empty(T)
    for t in range(T):
        q = np.exp(logp[t]); kls[t] = kl(q, logp[t])
        m = q @ CENTRES; sd[t] = np.sqrt(max(q @ CENTRES ** 2 - m * m, 0.0))
    return summarise("CHEAT", seed, kls, th.copy(), sd, th)
