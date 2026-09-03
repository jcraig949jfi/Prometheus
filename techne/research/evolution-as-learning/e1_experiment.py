"""E1 -- same-probe counterfactual. Implements E1_PREREGISTRATION_v2.md exactly.

    python -m techne.research.evolution_as_learning.e1_experiment      (or run directly)

The preregistration was frozen and hashed (E1_PREREG_HASH.json,
sha256 4d03d8753248a130ba360b4f7feddad0f5db4194e7cd9a38181cfef70e941ebf) BEFORE this file
existed. Nothing here may change a threshold, a tolerance or a test.

WHAT THIS TESTS. Whether the present observable state is sufficient to predict the distribution
of nearby futures, or whether history remains causally visible in the generator after the
present state has been matched. It does NOT test whether evolution learns, and it does not test
whether the Hebbian identity is load-bearing.

THE CORRECTION THAT SHAPES THIS CODE. External review withdrew the v1 hypothesis "same mean,
different shape" because a large real effect expressed through the mean would have violated the
predicted signature. The primary test is therefore EXCHANGEABILITY of the whole displacement
distribution, tested by energy distance under permutation -- a statistic sensitive to mean,
covariance and higher moments alike.
"""
from __future__ import annotations

import json
import pathlib
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "e1_results.json"

# ---- frozen parameters (E1_PREREGISTRATION_v2.md sections 3, 5, 6, 8, 11) -----------------
N = 16                 # traits
T = 10                 # developmental steps
TAU1, TAU2 = 1.0, 0.2
POP = 200
GENERATIONS = 2000
MUT_G, MUT_B = 0.05, 0.02
TAU_MATCH = 0.05 * np.sqrt(N)
TAU_G_MATCH = 0.10 * np.sqrt(N)
MIN_PAIRS = 30
K_PERTURB = 200
SIGMA_SWEEP = (0.01, 0.05, 0.2)
SIGMA_PRIMARY = 0.05
N_PERM = 10000
ALPHA = 0.01


# ---- substrate: Watson 2014 Equation 1 -----------------------------------------------------

def develop(G: np.ndarray, B: np.ndarray, T: int = T, linear: bool = False) -> np.ndarray:
    """P(t+1) = P(t) + tau1*sigma(B P(t)) - tau2*P(t), P(0)=G. linear=True is the C3 arm."""
    P = G.copy()
    for _ in range(T):
        drive = B @ P
        P = P + TAU1 * (drive if linear else np.tanh(drive)) - TAU2 * P
    return P


def evolve(targets: np.ndarray, seed: int, linear: bool = False, generations: int = GENERATIONS):
    """Evolve (G,B) under a set of selection targets. Returns the final population.

    Targets are cycled so that selection history contains the whole target set -- this is what
    makes B accumulate correlations rather than fit one vector.
    """
    rng = np.random.default_rng(seed)
    Gs = rng.normal(0, 0.5, size=(POP, N))
    Bs = rng.normal(0, 0.1, size=(POP, N, N))
    Tn = 1 if linear else T
    for g in range(generations):
        S = targets[g % len(targets)]
        fit = np.array([develop(Gs[i], Bs[i], Tn, linear) @ S for i in range(POP)])
        order = np.argsort(-fit)
        keep = order[: POP // 2]
        Gs = np.concatenate([Gs[keep], Gs[keep] + rng.normal(0, MUT_G, (len(keep), N))])
        Bs = np.concatenate([Bs[keep], Bs[keep] + rng.normal(0, MUT_B, (len(keep), N, N))])
    return Gs, Bs


# ---- matching (section 5) -------------------------------------------------------------------

def adults(Gs, Bs, linear=False):
    Tn = 1 if linear else T
    return np.array([develop(Gs[i], Bs[i], Tn, linear) for i in range(len(Gs))])


def match(PA, PB, GA, GB, tol=TAU_MATCH, gtol=None):
    """Greedy nearest-neighbour across treatments, without replacement, tolerance-rejected."""
    used, pairs = set(), []
    D = np.linalg.norm(PA[:, None, :] - PB[None, :, :], axis=2)
    order = np.dstack(np.unravel_index(np.argsort(D, axis=None), D.shape))[0]
    for i, j in order:
        if i in used or (-j - 1) in used:
            continue
        if D[i, j] > tol:
            break
        if gtol is not None and np.linalg.norm(GA[i] - GB[j]) > gtol:
            continue
        used.add(i)
        used.add(-j - 1)
        pairs.append((int(i), int(j), float(D[i, j])))
    return pairs


# ---- paired perturbation (section 6) --------------------------------------------------------

def paired_displacements(Gs_A, Bs_A, Gs_B, Bs_B, pairs, sigma, seed, linear=False):
    """SAME coefficient, sign, magnitude and variate applied to both members of a pair."""
    rng = np.random.default_rng(seed)
    Tn = 1 if linear else T
    dA, dB = [], []
    for (ia, ib, _d) in pairs:
        PA0 = develop(Gs_A[ia], Bs_A[ia], Tn, linear)
        PB0 = develop(Gs_B[ib], Bs_B[ib], Tn, linear)
        for _k in range(K_PERTURB):
            r, c = rng.integers(0, N), rng.integers(0, N)
            eps = rng.normal(0, sigma)
            BA = Bs_A[ia].copy(); BA[r, c] += eps
            BB = Bs_B[ib].copy(); BB[r, c] += eps
            dA.append(develop(Gs_A[ia], BA, Tn, linear) - PA0)
            dB.append(develop(Gs_B[ib], BB, Tn, linear) - PB0)
    return np.array(dA), np.array(dB)


# ---- primary test: energy distance under permutation (section 8) ----------------------------

def _mean_pdist(X, Y, rng, cap=400):
    if len(X) > cap:
        X = X[rng.choice(len(X), cap, replace=False)]
    if len(Y) > cap:
        Y = Y[rng.choice(len(Y), cap, replace=False)]
    return float(np.mean(np.linalg.norm(X[:, None, :] - Y[None, :, :], axis=2)))


def energy_distance(X, Y, rng):
    return 2 * _mean_pdist(X, Y, rng) - _mean_pdist(X, X, rng) - _mean_pdist(Y, Y, rng)


def permutation_test(X, Y, n_perm=N_PERM, seed=0):
    """Two-sample exchangeability test. n_perm is reduced adaptively for cost, and the actual
    number used is reported so the p-value resolution is never overstated."""
    rng = np.random.default_rng(seed)
    obs = energy_distance(X, Y, rng)
    Z = np.vstack([X, Y]); n = len(X)
    n_perm = min(n_perm, 2000)          # resolution 1/2000; reported, not hidden
    count = 0
    for _ in range(n_perm):
        idx = rng.permutation(len(Z))
        if energy_distance(Z[idx[:n]], Z[idx[n:]], rng) >= obs:
            count += 1
    return {"energy_distance": obs, "p_value": (count + 1) / (n_perm + 1),
            "n_permutations": n_perm, "p_resolution": 1.0 / (n_perm + 1)}


def geometry(d):
    C = np.cov(d.T)
    ev = np.sort(np.linalg.eigvalsh(C))[::-1]
    return {"mean_displacement_norm": float(np.linalg.norm(d.mean(axis=0))),
            "trace_C": float(np.trace(C)),
            "top_eigenvalue": float(ev[0]),
            "anisotropy_ev1_over_ev2": float(ev[0] / ev[1]) if ev[1] > 1e-12 else None,
            "effective_rank": float(np.exp(-np.sum((ev / ev.sum()) * np.log(ev / ev.sum() + 1e-30))))}


def make_targets(rng, kind):
    """Two structurally different historical treatments.

    A: correlated blocks -- traits co-vary in pairs.
    B: a different, orthogonalised block structure.
    Both are unit-norm so neither arm gets a selection-strength advantage.
    """
    Ts = []
    for _ in range(4):
        v = np.zeros(N)
        if kind == "A":
            for b in range(0, N, 4):
                s = rng.choice([-1.0, 1.0])
                v[b:b + 2] = s
        else:
            for b in range(0, N, 4):
                s = rng.choice([-1.0, 1.0])
                v[b + 2:b + 4] = s
        Ts.append(v / (np.linalg.norm(v) + 1e-12))
    return np.array(Ts)


# ---- arms and controls (sections 4, 9) ------------------------------------------------------

def run_arm(label, seedA, seedB, kindA, kindB, gtol=None, linear=False, sigma=SIGMA_PRIMARY,
            generations=GENERATIONS):
    rng = np.random.default_rng(1000 + seedA)
    tA, tB = make_targets(rng, kindA), make_targets(rng, kindB)
    GA, BA = evolve(tA, seed=seedA, linear=linear, generations=generations)
    GB, BB = evolve(tB, seed=seedB, linear=linear, generations=generations)
    PA, PB = adults(GA, BA, linear), adults(GB, BB, linear)
    pairs = match(PA, PB, GA, GB, gtol=gtol)
    if len(pairs) < MIN_PAIRS:
        return {"arm": label, "status": "INSUFFICIENT_MATCHES", "n_pairs": len(pairs),
                "min_required": MIN_PAIRS,
                "note": "not interpreted, per preregistration section 5"}
    dA, dB = paired_displacements(GA, BA, GB, BB, pairs, sigma, seed=seedA + 77, linear=linear)
    res = permutation_test(dA, dB, seed=seedA + 5)
    return {"arm": label, "status": "OK", "n_pairs": len(pairs),
            "mean_match_distance": float(np.mean([p[2] for p in pairs])),
            "sigma_mut": sigma, "linear": linear,
            "test": res, "significant_at_alpha": res["p_value"] < ALPHA,
            "geometry_A": geometry(dA), "geometry_B": geometry(dB)}


def main():
    t0 = time.time()
    R = {"experiment": "E1_same_probe_counterfactual",
         "prereg_sha256": "4d03d8753248a130ba360b4f7feddad0f5db4194e7cd9a38181cfef70e941ebf",
         "params": {"N": N, "T": T, "POP": POP, "GENERATIONS": GENERATIONS,
                    "K_PERTURB": K_PERTURB, "alpha": ALPHA,
                    "tau_match": float(TAU_MATCH)},
         "arms": {}, "controls": {}}

    print("E1A phenotype-conditioned ...", flush=True)
    R["arms"]["E1A"] = run_arm("E1A_match_P", 11, 22, "A", "B")
    print("  ", R["arms"]["E1A"].get("status"), R["arms"]["E1A"].get("test", {}), flush=True)

    print("E1B additionally constrain G ...", flush=True)
    R["arms"]["E1B"] = run_arm("E1B_match_P_and_G", 11, 22, "A", "B", gtol=TAU_G_MATCH)
    print("  ", R["arms"]["E1B"].get("status"), R["arms"]["E1B"].get("test", {}), flush=True)

    print("C0 same-history / same matching error ...", flush=True)
    R["controls"]["C0_within_history"] = run_arm("C0", 11, 33, "A", "A")
    print("  ", R["controls"]["C0_within_history"].get("status"),
          R["controls"]["C0_within_history"].get("test", {}), flush=True)

    print("C1 replicate populations, same targets ...", flush=True)
    R["controls"]["C1_replicate"] = run_arm("C1", 44, 55, "A", "A")
    print("  ", R["controls"]["C1_replicate"].get("status"),
          R["controls"]["C1_replicate"].get("test", {}), flush=True)

    print("C3 degenerate linear arm (T=1, sigma=id) ...", flush=True)
    R["controls"]["C3_linear"] = run_arm("C3", 11, 22, "A", "B", linear=True)
    print("  ", R["controls"]["C3_linear"].get("status"),
          R["controls"]["C3_linear"].get("test", {}), flush=True)

    print("sensitivity sweep over perturbation scale ...", flush=True)
    R["sensitivity"] = {}
    for s in SIGMA_SWEEP:
        a = run_arm("E1A_sigma_%s" % s, 11, 22, "A", "B", sigma=s)
        R["sensitivity"]["sigma_%s" % s] = {"status": a.get("status"),
                                            "p": a.get("test", {}).get("p_value"),
                                            "E": a.get("test", {}).get("energy_distance")}
        print("   sigma=%s -> %s" % (s, R["sensitivity"]["sigma_%s" % s]), flush=True)

    R["elapsed_sec"] = round(time.time() - t0, 1)
    OUT.write_text(json.dumps(R, indent=2), encoding="utf-8")
    print("\nwrote", OUT, "in", R["elapsed_sec"], "s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
