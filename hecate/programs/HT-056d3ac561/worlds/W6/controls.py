"""HT-056d3ac561 / W6 -- controls only (no treatment code).

World: a hidden fault vector f in R^64 with exactly K=2 nonzero entries
(sign * U(1,2)).  A pool of M=256 metamorphic relations; running relation
i returns the residual r_i = a_i . f + eps, eps ~ N(0, SIGMA^2); a_i has
S_ROW=6 nonzero entries +/- 1/sqrt(6) at uniform positions.  A tester may
run B=24 distinct relations, one at a time.  After the budget is spent a
FIXED decoder (orthogonal matching pursuit, exactly K=2 atoms, on the
columns of the selected rows) outputs a support; success = it equals the
true support.  Arms differ ONLY in which 24 relations are run.

Arms written here:
  POSITIVE_CONTROL  oracle-targeted selection: knows the true support;
                    test b targets true component S[b mod 2]: uniform among
                    unused relations containing the target and not the other
                    true component (else any unused containing the target,
                    else any unused).  Effect present by construction.
  NULL_TWIN         identical procedure aimed at a DECOY support (2 uniform
                    components disjoint from the true support): same
                    targeting machinery, test sparsity and budget; the
                    relation between selection and fault destroyed.
  CHEAT             success flag written directly as 1.
  REFERENCE_RANDOM  the spec's CONTROL (not the treatment): 24 relations
                    uniform without replacement.  Needed here because clause
                    S2 is a difference from it.
  REFERENCE_GAUSSIAN_GREEDY  the spec's second CONTROL (the M9 knockout with
                    the sparse prior removed): greedy expected-covariance-
                    reduction under a fixed isotropic Gaussian belief; its
                    choices never depend on data.  Needed for clause S3.

All arms of one (seed, trial) share the pool, the fault and the residual
noise of every relation (a relation's residual is drawn once per trial).
Rows: control_rows.jsonl, one row per (arm, seed), flushed per row.
"""
import json, os, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "control_rows.jsonl")

N = 64
K = 2
M = 256
S_ROW = 6
SIGMA = 0.3
B = 24
TRIALS = 300
TAU2 = K * (7.0 / 3.0) / N   # isotropic Gaussian prior variance matching E||f||^2
SEEDS = [0, 1, 2, 3, 4]


def make_pool(rng):
    A = np.zeros((M, N))
    for i in range(M):
        c = rng.choice(N, S_ROW, replace=False)
        A[i, c] = rng.choice([-1.0, 1.0], S_ROW) / np.sqrt(S_ROW)
    return A


def omp(A, y, k):
    sup, res = [], y.copy()
    for _ in range(k):
        norms = np.linalg.norm(A, axis=0)
        corr = np.where(norms > 0, np.abs(A.T @ res) / np.where(norms > 0, norms, 1), -1.0)
        corr[sup] = -1.0
        sup.append(int(np.argmax(corr)))
        coef, *_ = np.linalg.lstsq(A[:, sup], y, rcond=None)
        res = y - A[:, sup] @ coef
    return set(sup)


def targeted(A, target, rng):
    used = np.zeros(M, bool)
    sel = []
    for b in range(B):
        t, o = target[b % K], target[(b + 1) % K]
        cand = np.where(~used & (A[:, t] != 0) & (A[:, o] == 0))[0]
        if cand.size == 0:
            cand = np.where(~used & (A[:, t] != 0))[0]
        if cand.size == 0:
            cand = np.where(~used)[0]
        i = int(rng.choice(cand))
        used[i] = True
        sel.append(i)
    return sel


def gaussian_greedy(A):
    """Knockout reference (sparse prior removed): isotropic Gaussian belief
    N(0, TAU2 I); each test = argmax expected trace reduction of the
    Kalman covariance a'P^2a / (a'Pa + SIGMA^2).  Data-independent
    (Riccati), so one selection per pool."""
    P = TAU2 * np.eye(N)
    used = np.zeros(M, bool)
    sel = []
    for _ in range(B):
        AP = A @ P
        gain = np.einsum("ij,ij->i", AP, AP) / (np.einsum("ij,ij->i", AP, A) + SIGMA ** 2)
        gain[used] = -np.inf
        i = int(np.argmax(gain))
        used[i] = True
        sel.append(i)
        a = A[i]
        Pa = P @ a
        P = P - np.outer(Pa, Pa) / (a @ Pa + SIGMA ** 2)
    return sel


def main():
    t0 = time.process_time()
    open(OUT, "w").close()
    with open(OUT, "a") as fo:
        for seed in SEEDS:
            rng = np.random.default_rng(seed)
            A = make_pool(rng)
            gg = gaussian_greedy(A)
            res = {a: [] for a in ["POSITIVE_CONTROL", "NULL_TWIN", "REFERENCE_RANDOM", "REFERENCE_GAUSSIAN_GREEDY", "CHEAT"]}
            cover = {a: [] for a in res}
            for tr in range(TRIALS):
                sup = rng.choice(N, K, replace=False)
                f = np.zeros(N)
                f[sup] = rng.choice([-1.0, 1.0], K) * rng.uniform(1, 2, K)
                r_all = A @ f + rng.normal(0, SIGMA, M)
                rest = np.setdiff1d(np.arange(N), sup)
                decoy = rng.choice(rest, K, replace=False)
                arm_rng = np.random.default_rng([seed, tr, 7])
                sels = {"POSITIVE_CONTROL": targeted(A, list(sup), arm_rng),
                        "NULL_TWIN": targeted(A, list(decoy), arm_rng),
                        "REFERENCE_RANDOM": list(arm_rng.choice(M, B, replace=False)),
                        "REFERENCE_GAUSSIAN_GREEDY": gg}
                for a, sel in sels.items():
                    ok = omp(A[sel], r_all[sel], K) == set(int(s) for s in sup)
                    res[a].append(float(ok))
                    cover[a].append(float(np.all((A[sel][:, sup] != 0).any(axis=0))))
                res["CHEAT"].append(1.0)        # success injected into the observable
                cover["CHEAT"].append(cover["REFERENCE_RANDOM"][-1])
            for a in res:
                row = {"arm": a, "seed": seed, "trials": TRIALS, "success": res[a],
                       "accuracy": float(np.mean(res[a])),
                       "both_true_covered_fraction": float(np.mean(cover[a])),
                       "B": B, "SIGMA": SIGMA, "S_ROW": S_ROW}
                fo.write(json.dumps(row) + "\n"); fo.flush()
    print("cpu_s", round(time.process_time() - t0, 1))


if __name__ == "__main__":
    main()
