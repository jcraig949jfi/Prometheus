"""HT-974471f045 / W6 probe round 3: TREATMENT + CONTROL arms, controls re-run
in the same code path (imported from the frozen controls.py). Writes rows.jsonl."""
import os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import controls as C          # sets thread env vars before numpy import
import json, time
import numpy as np

ROWS = os.path.join(HERE, "rows.jsonl")
PARAMS = dict(N=C.N, D_IN=C.D_IN, SIGMA=C.SIGMA, RHO=C.RHO, T=C.T, WASH=C.WASH,
              POP=C.POP, GENS=C.GENS, KEEP=C.N_ELITE_KEEP, PARENT_POOL=C.PARENT_POOL,
              MUT_M=C.MUT_M, MUT_W=C.MUT_W, N_RESAMPLE=C.N_RESAMPLE, N_OBS=C.N_OBS)


def live(M, w, rng):
    W, W_in = C.sample_reservoir(M, rng)
    u = rng.uniform(-C.U_AMP, C.U_AMP, (C.T, C.D_IN))
    X = C.run(W, W_in, u)[C.WASH:]
    return C.corr2(X @ w, C.target(u)[C.WASH:])


def evolve(rng, permuted=False):
    pop = [C.gen0_genome(rng) for _ in range(C.POP)]
    fit = [live(M, w, rng) for M, w in pop]
    traj = []
    for g in range(C.GENS):
        order = rng.permutation(C.POP) if permuted else np.argsort(-np.asarray(fit), kind="stable")
        keep = [pop[i] for i in order[:C.N_ELITE_KEEP]]
        keepf = [fit[i] for i in order[:C.N_ELITE_KEEP]]
        pool = [pop[i] for i in order[:C.PARENT_POOL]]
        kids = [C.mutate(*pool[rng.integers(C.PARENT_POOL)], rng) for _ in range(C.POP - C.N_ELITE_KEEP)]
        kidf = [live(M, w, rng) for M, w in kids]
        pop, fit = keep + kids, keepf + kidf
        traj.append((float(np.max(fit)), float(np.mean(fit))))
    order = np.argsort(-np.asarray(fit), kind="stable")
    return [pop[i] for i in order[:C.N_OBS]], [fit[i] for i in order[:C.N_OBS]], traj


def no_recurrence_Iperp(M, w, meas_seed):
    """Same measurement streams as C.invariance, recurrent W set to 0."""
    rng = np.random.default_rng(meas_seed)
    wp = w - w.mean(); out = []
    for _ in range(C.N_RESAMPLE):
        u = rng.uniform(-C.U_AMP, C.U_AMP, (C.T, C.D_IN))
        W, W_in = C.sample_reservoir(M, rng)
        X = C.run(np.zeros_like(W), W_in, u)[C.WASH:]
        out.append(C.corr2(X @ wp, C.target(u)[C.WASH:]))
    return float(np.mean(out))


def diag(pop, seed, norec=False):
    tnr = [float(np.sqrt(np.mean(M ** 2)) / C.SIGMA) for M, _ in pop]
    share = []
    for _, w in pop:
        wp = w - w.mean(); share.append(float(np.max(wp ** 2) / np.sum(wp ** 2)))
    d = dict(tnr_mean=float(np.mean(tnr)), tnr_list=tnr, max_unit_share_mean=float(np.mean(share)))
    if norec:
        d["I_perp_norec"] = float(np.mean([no_recurrence_Iperp(M, w, 10_000 + 100 * seed + k)
                                           for k, (M, w) in enumerate(pop)]))
    return d


def emit(fh, row):
    fh.write(json.dumps(row) + "\n"); fh.flush(); os.fsync(fh.fileno())


def main(tag):
    t0 = time.process_time()
    with open(ROWS, "a", encoding="utf-8") as fh:
        for s in C.SEEDS:
            base = dict(world="W6", run=tag, seed=s, params=PARAMS)
            rng = np.random.default_rng(s)                       # verbatim controls.main
            pc = [C.constructed_genome(rng) for _ in range(C.N_OBS)]
            g0 = [C.gen0_genome(rng) for _ in range(C.N_OBS)]
            emit(fh, dict(base, arm="POSITIVE_CONTROL", rng_seed=s, **C.arm_stats(pc, s), **diag(pc, s)))
            emit(fh, dict(base, arm="CHEAT", rng_seed=s, **C.arm_stats(g0, s, cheat=True)))
            tw = C.drift_population(np.random.default_rng(1_000 + s))
            emit(fh, dict(base, arm="NULL_TWIN", rng_seed=1000 + s, **C.arm_stats(tw, s), **diag(tw, s)))
            emit(fh, dict(base, arm="CONTROL", rng_seed=s, **C.arm_stats(g0, s), **diag(g0, s)))
            el, ef, tr = evolve(np.random.default_rng(2_000 + s))
            emit(fh, dict(base, arm="TREATMENT", rng_seed=2000 + s, **C.arm_stats(el, s), **diag(el, s, norec=True),
                          elite_lifetime_fitness=ef, best_fit_g1=tr[0][0], best_fit_g60=tr[-1][0],
                          mean_fit_g1=tr[0][1], mean_fit_g60=tr[-1][1],
                          best_fit_every10=[tr[i][0] for i in range(9, C.GENS, 10)]))
            pe, pf, ptr = evolve(np.random.default_rng(3_000 + s), permuted=True)
            emit(fh, dict(base, arm="PERMUTED_TWIN", rng_seed=3000 + s, diagnostic_only=True, **C.arm_stats(pe, s),
                          **diag(pe, s), mean_fit_g60=ptr[-1][1]))
            print("seed", s, "done", round(time.process_time() - t0, 1), "cpu s", flush=True)
        emit(fh, dict(world="W6", run=tag, arm="CPU", cpu_seconds=time.process_time() - t0))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "p1")
