"""HT-974471f045 / W3: heritable input mask (epoche gate) before a fixed ESN,
readout restricted to k taps. See IMPLEMENTATION_NOTES.md.
Writes rows.jsonl (one row per arm x seed [x k]), flushed per row."""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import json
import sys
import time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "rows.jsonl")

P = dict(
    pop=30, n_elite=6, N=50, C=8, n_inf=2, gens=60, seeds=list(range(8)),
    ks=[3, 50], spectral_radius=0.9, win_scale=0.2, inf_std=1.0,
    dis_std=3.0, washout=100, train=600, test=300, ridge=1e-4,
    flip_p=1.0 / 8, init_p_one=0.5,
)
DIS = list(range(P["n_inf"], P["C"]))
HAND = np.array([1] * P["n_inf"] + [0] * (P["C"] - P["n_inf"]), dtype=float)
ONES = np.ones(P["C"])


def make_world(seed):
    rng = np.random.default_rng(1000 + seed)
    N, C = P["N"], P["C"]
    W = rng.standard_normal((N, N))
    W *= P["spectral_radius"] / np.max(np.abs(np.linalg.eigvals(W)))
    Win = rng.uniform(-P["win_scale"], P["win_scale"], (N, C))
    T = P["washout"] + P["train"] + P["test"]
    std = np.array([P["inf_std"]] * P["n_inf"] + [P["dis_std"]] * len(DIS))
    U = rng.standard_normal((T, C)) * std
    y = np.zeros(T)
    y[2:] = 0.6 * U[1:-1, 0] + 0.4 * U[:-2, 1]
    return W, Win, U, y


def nrmse_batch(masks, k, world):
    """masks (B,C) -> NRMSE (B,) of ridge readout on first k reservoir units."""
    W, Win, U, y = world
    B = masks.shape[0]
    inp = np.einsum("btc,nc->btn", masks[:, None, :] * U[None], Win)
    T = U.shape[0]
    X = np.zeros((B, P["N"]))
    S = np.empty((B, T, k))
    for t in range(T):
        X = np.tanh(X @ W.T + inp[:, t])
        S[:, t] = X[:, :k]
    w0, tr = P["washout"], P["train"]
    ytr, yte = y[w0:w0 + tr], y[w0 + tr:]
    out = np.empty(B)
    for b in range(B):
        A = np.hstack([S[b, w0:w0 + tr], np.ones((tr, 1))])
        wr = np.linalg.solve(A.T @ A + P["ridge"] * np.eye(k + 1), A.T @ ytr)
        Ate = np.hstack([S[b, w0 + tr:], np.ones((len(yte), 1))])
        out[b] = np.sqrt(np.mean((Ate @ wr - yte) ** 2)) / np.std(yte)
    return out


def masked_frac(masks):
    return float(np.mean(masks[:, DIS] == 0))


def run_evolution(seed, k, permute, world):
    rng = np.random.default_rng(seed * 100 + k)
    prng = np.random.default_rng(seed * 100 + k + 7777)
    pop = (rng.random((P["pop"], P["C"])) < P["init_p_one"]).astype(float)
    traj = []
    for g in range(1, P["gens"] + 1):
        nr = nrmse_batch(pop, k, world)
        fit = -nr
        sel_fit = prng.permutation(fit) if permute else fit
        order = np.argsort(-sel_fit, kind="stable")
        elites = pop[order[:P["n_elite"]]].copy()
        traj.append(masked_frac(elites))
        if g == P["gens"]:
            return dict(
                masked_frac=masked_frac(elites),
                elite_true_nrmse=float(np.mean(nr[order[:P["n_elite"]]])),
                pop_masked_frac=masked_frac(pop),
                elite_masks=elites.astype(int).tolist(),
                inf_kept_frac=float(np.mean(elites[:, :P["n_inf"]] == 1)),
                traj_masked_frac=traj,
            )
        parents = elites[rng.integers(0, P["n_elite"], P["pop"] - P["n_elite"])]
        flips = rng.random(parents.shape) < P["flip_p"]
        children = np.where(flips, 1 - parents, parents)
        pop = np.vstack([elites, children])


def write(fh, row):
    fh.write(json.dumps(row) + "\n")
    fh.flush()


def main():
    t0 = time.process_time()
    w0 = time.time()
    attempt = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    with open(ROWS, "w") as fh:
        for seed in P["seeds"]:
            world = make_world(seed)
            base = dict(seed=seed, attempt=attempt, params=P)
            # CONTROL and POSITIVE_CONTROL
            for k in P["ks"]:
                n_ones, n_hand = nrmse_batch(np.vstack([ONES, HAND]), k, world)
                write(fh, dict(base, arm="CONTROL", k=k, masked_frac=0.0,
                               nrmse=float(n_ones)))
                write(fh, dict(base, arm="POSITIVE_CONTROL", k=k,
                               nrmse_all_ones=float(n_ones),
                               nrmse_hand=float(n_hand),
                               rel_gain=float((n_ones - n_hand) / n_ones)))
            for k in P["ks"]:
                for arm, perm in (("TREATMENT", False), ("NULL_TWIN", True)):
                    r = run_evolution(seed, k, perm, world)
                    write(fh, dict(base, arm=arm, k=k, **r,
                                   cpu_s_so_far=time.process_time() - t0))
                # CHEAT: success injected directly into the observable
                write(fh, dict(base, arm="CHEAT", k=k,
                               masked_frac=1.0 if k == 3 else 0.0))
            print(f"seed {seed} done cpu={time.process_time()-t0:.1f}s", flush=True)
        write(fh, dict(arm="_META", attempt=attempt,
                       cpu_seconds=time.process_time() - t0,
                       wall_seconds=time.time() - w0))


if __name__ == "__main__":
    main()
