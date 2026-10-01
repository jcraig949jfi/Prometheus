"""HT-37e311ce05 / W4 pilot: POSITIVE_CONTROL, CHEAT, NULL_TWIN (+ NULL_TWIN_B).

No treatment arm exists in this file. See NOTES.md for the spec mapping.
"""
import os
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_v] = "1"
import json
import sys
import time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

PARAMS = dict(N=64, R_SIZE=24, S_SIZE=12, M=24, K=6, POP=60, GENS=400,
              COST=0.01, W0=0.5, MUT_P=0.1, MUT_SD=0.05, TRUNC=0.5,
              PC_SPARSITY=6, ENERGY=0.9, PC_REPAIR=1)
SEEDS = list(range(10))
ARM_CODE = {"POSITIVE_CONTROL": 1, "NULL_TWIN": 2, "NULL_TWIN_B": 3,
            "CHEAT": 4, "TREATMENT": 5, "CONTROL": 6}


def make_world(seed):
    P = PARAMS
    rng = np.random.default_rng(seed)
    R = np.sort(rng.choice(P["N"], P["R_SIZE"], replace=False))
    S = np.sort(rng.choice(R, P["S_SIZE"], replace=False))
    host = np.zeros(P["N"]); host[S] = 1.0
    Rmask = np.zeros(P["N"], bool); Rmask[R] = True
    Smask = np.zeros(P["N"], bool); Smask[S] = True
    Q, Rr = np.linalg.qr(rng.standard_normal((P["N"], P["N"])))
    Psi = Q * np.sign(np.diag(Rr))          # columns orthonormal
    A = rng.standard_normal((P["M"], P["N"])) / np.sqrt(P["M"])
    # null space of A (for the L5 ker-A observable)
    _, _, Vt = np.linalg.svd(A)
    kerA = Vt[P["M"]:].T                    # N x (N-M)
    return dict(R=R, S=S, host=host, Rmask=Rmask, Smask=Smask, Psi=Psi,
                A=A, kerA=kerA)


def fitness_parts(W, world):
    """W: pop x N. Returns benefit, cost."""
    P = PARAMS
    h = world["host"][None, :]
    ben = np.minimum(h + W, 1.0)[:, world["Rmask"]].sum(1) / P["R_SIZE"]
    cost = P["COST"] * np.abs(W).sum(1)
    return ben, cost


def omp_residual_frac(A, Y, k):
    """Batched OMP. Y: pop x M. Returns unexplained energy fraction per row."""
    pop = Y.shape[0]
    out = np.zeros(pop)
    for i in range(pop):
        y = Y[i]
        yy = float(y @ y)
        if yy <= 1e-30:
            out[i] = 0.0
            continue
        r = y.copy()
        sel = []
        for _ in range(k):
            j = int(np.argmax(np.abs(A.T @ r)))
            if j not in sel:
                sel.append(j)
            As = A[:, sel]
            coef, *_ = np.linalg.lstsq(As, y, rcond=None)
            r = y - As @ coef
        out[i] = min(max(float(r @ r) / yy, 0.0), 1.0)
    return out


def sanction_prob_verif(W, world):
    C = W @ world["Psi"]                    # coefficients c = Psi^T w, rows
    Y = C @ world["A"].T                    # y = A c
    return omp_residual_frac(world["A"], Y, PARAMS["K"])


def observables(W, world):
    P = PARAMS
    C = W @ world["Psi"]
    e = C ** 2
    tot = e.sum(1)
    srt = -np.sort(-e, axis=1)
    cum = np.cumsum(srt, axis=1)
    s_psi = np.array([int(np.searchsorted(cum[i], P["ENERGY"] * tot[i] - 1e-15) + 1)
                      if tot[i] > 0 else 0 for i in range(len(tot))])
    wn2 = (W ** 2).sum(1)
    overlap = np.where(wn2 > 0, (W[:, world["Smask"]] ** 2).sum(1) / np.maximum(wn2, 1e-300), 0.0)
    l1 = np.abs(W).sum(1)
    ac_l1 = np.where(l1 > 0, np.abs(W[:, world["Smask"]]).sum(1) / np.maximum(l1, 1e-300), 0.0)
    ker = (C @ world["kerA"]) ** 2
    kerfrac = np.where(tot > 0, ker.sum(1) / np.maximum(tot, 1e-300), 0.0)
    return dict(s_psi=float(np.median(s_psi)), overlap=float(np.median(overlap)),
                ac_mass_l1=float(np.median(ac_l1)), kerA_frac=float(np.median(kerfrac)),
                w_norm2=float(np.median(wn2)),
                benefit=float(np.median(fitness_parts(W, world)[0])))


def init_pop(arm, world, rng):
    """Returns (W, J, Cj). J/Cj are None except for the (repaired) PC."""
    P = PARAMS
    if arm == "POSITIVE_CONTROL":
        k = P["PC_SPARSITY"]
        J = np.stack([rng.choice(P["N"], k, replace=False) for _ in range(P["POP"])])
        Cj = rng.standard_normal((P["POP"], k))
        W = pc_genome(J, Cj, world)
        Cj = Cj * (np.sqrt(P["N"] * P["W0"] ** 2) / np.linalg.norm(W, axis=1))[:, None]
        return pc_genome(J, Cj, world), J, Cj
    return np.full((P["POP"], P["N"]), P["W0"]), None, None


def pc_genome(J, Cj, world):
    Psi = world["Psi"]
    return np.einsum("pnk,pk->pn", Psi[:, J].transpose(1, 0, 2), Cj)


def evolve(arm, seed, world, mode, rate_schedule=None):
    """mode 'verif' (sanction prob from OMP residual) or 'random' (matched rate)."""
    P = PARAMS
    rng = np.random.default_rng([seed, ARM_CODE[arm]])
    W, J, Cj = init_pop(arm, world, rng)
    rates, realized = [], []
    gen0_rate = None
    for g in range(P["GENS"]):
        ben, cost = fitness_parts(W, world)
        if mode == "verif":
            p = sanction_prob_verif(W, world)
        else:
            p = np.full(P["POP"], rate_schedule[g])
        if g == 0:
            gen0_rate = float(p.mean())
        rates.append(float(p.mean()))
        sanc = rng.random(P["POP"]) < p
        realized.append(float(sanc.mean()))
        fit = np.where(sanc, -cost, ben - cost)
        order = np.argsort(-fit, kind="stable")
        parents = order[: int(P["POP"] * P["TRUNC"])]
        pick = rng.choice(parents, P["POP"])
        if J is None:
            W = W[pick].copy()
            mut = rng.random(W.shape) < P["MUT_P"]
            W = W + mut * rng.normal(0.0, P["MUT_SD"], W.shape)
        else:   # repaired PC: mutate the 6 inherited Psi_h coefficients
            J, Cj = J[pick].copy(), Cj[pick].copy()
            Cj = Cj + rng.normal(0.0, P["MUT_SD"], Cj.shape)
            W = pc_genome(J, Cj, world)
    obs = observables(W, world)
    if mode == "verif":
        obs["final_sanction_prob"] = float(sanction_prob_verif(W, world).mean())
    return obs, rates, realized, gen0_rate


def run_arm(arm, seed, world, rate_schedule=None, mode=None):
    t0 = time.process_time()
    if arm == "CHEAT":
        obs = dict(s_psi=1.0, overlap=0.0, ac_mass_l1=0.0, kerA_frac=None,
                   w_norm2=None, benefit=None, injected=True)
        rates, realized, gen0 = [], [], None
    else:
        obs, rates, realized, gen0 = evolve(arm, seed, world, mode, rate_schedule)
    row = dict(triplicateId="HT-37e311ce05", world="W4", arm=arm, seed=seed,
               mode=mode, params=PARAMS, gen0_sanction_rate=gen0,
               mean_sanction_rate=float(np.mean(rates)) if rates else None,
               mean_realized_sanction=float(np.mean(realized)) if realized else None,
               rate_schedule=rates, cpu_s=time.process_time() - t0, **obs)
    return row


def main(out_name="pilot_rows.jsonl"):
    path = os.path.join(HERE, out_name)
    with open(path, "w") as f:
        for seed in SEEDS:
            world = make_world(seed)
            pc = run_arm("POSITIVE_CONTROL", seed, world, mode="verif")
            sched = pc["rate_schedule"]
            rows = [pc,
                    run_arm("NULL_TWIN", seed, world, sched, mode="random"),
                    run_arm("NULL_TWIN_B", seed, world, sched, mode="random"),
                    run_arm("CHEAT", seed, world)]
            for r in rows:
                f.write(json.dumps(r) + "\n"); f.flush()
            print(seed, [(r["arm"], r["s_psi"], round(r["overlap"], 3)) for r in rows],
                  round(sum(r["cpu_s"] for r in rows), 1), flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:])
