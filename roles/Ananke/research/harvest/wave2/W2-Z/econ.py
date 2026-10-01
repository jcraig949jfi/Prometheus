"""W2-Z exact single-site energy recursion (engine.py step 5), program-independent.
E_{t+1} = clamp(E_t + inc - want*cE - awake*c_op*k - c_mem*m, 0, e_max); want requires awake & E_t >= cE.
Ops always execute (only EMISSION is gated by energy); deficits below 0 are forgiven.
Wake: sync -> t % P == 0 ; async -> Bernoulli(p) per tick (exact Markov chain over E in 0..e_max).
Emission wish model W1: the site wishes to emit at every awake tick inside a window of w ticks starting at
trial onset (phase 0..w-1 of each trial period Pd), at most `nmax` emissions per trial; otherwise silent.
Returns the expected number of emissions per trial in steady state (and from E0=e_max over the episode)."""
import numpy as np


def site_rates(inc, emax, cE, cop, cmem, k, m, mode, P, p, Pd, w, nmax, trials):
    """Exact for sync (deterministic over trial phases, but sync wake parity vs Pd handled by simulating
    the full episode); exact distribution for async via forward propagation of the E-distribution
    (state = (E, emissions-this-trial)) over the episode. Returns per-trial expected emissions list."""
    T = trials * Pd
    # state distribution over (E, n_emitted_this_trial)
    dist = np.zeros((emax + 1, nmax + 1)); dist[emax, 0] = 1.0
    out = np.zeros(trials)
    for t in range(T):
        ph = t % Pd
        if ph == 0:
            dist = np.stack([dist.sum(1)] + [np.zeros(emax + 1)] * nmax, 1)
        if mode == "sync":
            pa = 1.0 if t % P == 0 else 0.0
        else:
            pa = p
        new = np.zeros_like(dist)
        for n in range(nmax + 1):
            col = dist[:, n]
            if not col.any():
                continue
            E = np.arange(emax + 1)
            # asleep
            if pa < 1.0:
                e2 = np.clip(E + inc - cmem * m, 0, emax)
                np.add.at(new[:, n], e2, col * (1 - pa))
            if pa > 0.0:
                wish = (ph < w) and (n < nmax)
                can = wish & (E >= cE)
                e_emit = np.clip(E + inc - cE - cop * k - cmem * m, 0, emax)
                e_no = np.clip(E + inc - cop * k - cmem * m, 0, emax)
                if wish:
                    np.add.at(new[:, n + 1], e_emit[can], col[can] * pa)
                    out[t // Pd] += (col[can] * pa).sum()
                    np.add.at(new[:, n], e_no[~can], col[~can] * pa)
                else:
                    np.add.at(new[:, n], e_no, col * pa)
        dist = new
    return out


def row_table(ph, env, ks=range(0, 17), m=0, w=None, nmax=1):
    Pd = env.period()
    w = Pd if w is None else w
    cE = ph.c_emit * ph.copies()
    res = {}
    for k in ks:
        r = site_rates(ph.e_income, ph.e_max, cE, ph.c_op, ph.c_mem, k, m, ph.update_mode,
                       ph.update_period, ph.update_p, Pd, w, nmax, env.trials)
        res[k] = r
    return res
