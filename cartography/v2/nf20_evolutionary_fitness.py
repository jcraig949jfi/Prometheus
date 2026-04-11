"""
NF20: Evolutionary Translation Viability Limit

Evolve a 20x20 matrix W mapping Sato-Tate moment vectors to L-function
trace vectors for genus-2 curves. Measure max achievable fitness (correlation).

Two strategies:
1. OLS baseline (analytical)
2. (mu+lambda)-ES seeded from OLS, run for 10^4 generations
"""

import json
import sys
import time
import numpy as np
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────
N_DIM = 20               # Dimension of moment/trace vectors
MAX_CURVES = 800         # Sample size
MAX_GENERATIONS = 10000
NUM_PRIMES = 60          # Primes to use for trace computation
SEED = 42
OUT_PATH = Path("F:/Prometheus/cartography/v2/evolutionary_fitness_results.json")

# ES parameters
MU = 20         # parents
LAMBDA = 100    # offspring per generation
SIGMA_INIT = 0.1  # initial mutation step size

np.random.seed(SEED)


def sieve_primes(n):
    """Return list of primes up to n."""
    sieve = np.ones(n + 1, dtype=bool)
    sieve[:2] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = False
    return [int(x) for x in np.where(sieve)[0]]


def count_points_genus2(f_coeffs, h_coeffs, p):
    """
    Vectorized point count on y^2 + h(x)*y = f(x) over F_p.
    """
    xs = np.arange(p, dtype=np.int64)

    # Evaluate f(x) mod p using Horner's method
    fx = np.zeros(p, dtype=np.int64)
    for c in reversed(f_coeffs):
        fx = (fx * xs + int(c)) % p

    # Evaluate h(x) mod p
    hx = np.zeros(p, dtype=np.int64)
    for c in reversed(h_coeffs):
        hx = (hx * xs + int(c)) % p

    # Discriminant: h(x)^2 + 4*f(x) mod p
    disc = (hx * hx + 4 * fx) % p

    if p == 2:
        count = 2 * p
    else:
        count = int(np.sum(disc == 0))
        nonzero = disc[disc > 0]
        if len(nonzero) > 0:
            ls = np.array([pow(int(d), (p - 1) // 2, p) for d in nonzero])
            count += 2 * int(np.sum(ls == 1))

    # Points at infinity
    deg_f = len(f_coeffs) - 1
    while deg_f > 0 and f_coeffs[deg_f] == 0:
        deg_f -= 1
    if deg_f <= 5:
        count += 1
    else:
        lc = int(f_coeffs[deg_f]) % p
        if lc == 0:
            count += 1
        elif p == 2:
            count += 2
        else:
            if pow(lc, (p - 1) // 2, p) == 1:
                count += 2
    return count


def trace_of_frobenius(f_coeffs, h_coeffs, p):
    npts = count_points_genus2(f_coeffs, h_coeffs, p)
    return p + 1 - npts


def parse_equation(eq):
    if isinstance(eq, str):
        eq = json.loads(eq)
    return [int(c) for c in eq[0]], [int(c) for c in eq[1]]


def compute_vectors_for_curve(f_coeffs, h_coeffs, conductor, primes):
    good_primes = [p for p in primes if conductor % p != 0]
    if len(good_primes) < N_DIM:
        return None

    traces = []
    for p in good_primes[:max(N_DIM, 40)]:
        a_p = trace_of_frobenius(f_coeffs, h_coeffs, p)
        traces.append((a_p, p))

    if len(traces) < N_DIM:
        return None

    norm_traces = np.array([a / np.sqrt(p) for a, p in traces])
    trace_vec = norm_traces[:N_DIM]

    moment_vec = np.zeros(N_DIM)
    for k in range(1, N_DIM + 1):
        vals = np.array([a / (p ** (k / 2.0)) for a, p in traces])
        moment_vec[k - 1] = np.mean(vals)

    if not (np.all(np.isfinite(moment_vec)) and np.all(np.isfinite(trace_vec))):
        return None

    return moment_vec, trace_vec


def compute_fitness_vectorized(W, M_norm, T_norm):
    """Compute mean per-curve correlation for a weight matrix."""
    predicted = M_norm @ W.T  # (n_curves, 20)
    # Vectorized correlation
    p_c = predicted - predicted.mean(axis=1, keepdims=True)
    t_c = T_norm - T_norm.mean(axis=1, keepdims=True)
    num = np.sum(p_c * t_c, axis=1)
    den = np.sqrt(np.sum(p_c**2, axis=1) * np.sum(t_c**2, axis=1))
    den = np.maximum(den, 1e-12)
    corrs = num / den
    return float(np.mean(corrs)), corrs


def mu_plus_lambda_es(M_norm, T_norm, W_init, max_gen=10000):
    """
    (mu + lambda)-ES for evolving the 20x20 weight matrix.
    Seeded with W_init (e.g., OLS solution).
    """
    n_params = N_DIM * N_DIM
    rng = np.random.RandomState(SEED + 1)

    # Initialize population: mu copies of W_init with small perturbations
    population = []
    sigmas = []
    fitnesses = []

    for i in range(MU):
        if i == 0:
            w = W_init.copy().flatten()
        else:
            w = W_init.flatten() + rng.randn(n_params) * SIGMA_INIT * 0.5
        population.append(w)
        sigmas.append(SIGMA_INIT)
        f, _ = compute_fitness_vectorized(w.reshape(N_DIM, N_DIM), M_norm, T_norm)
        fitnesses.append(f)

    convergence = []
    best_fitness = max(fitnesses)
    best_w = population[np.argmax(fitnesses)].copy()
    stall_count = 0
    prev_best = best_fitness

    print(f"  Initial best fitness: {best_fitness:.6f}", flush=True)

    for gen in range(1, max_gen + 1):
        # Generate lambda offspring
        offspring = []
        off_sigmas = []
        off_fitnesses = []

        for _ in range(LAMBDA):
            # Select random parent
            parent_idx = rng.randint(MU)
            parent = population[parent_idx]
            sigma = sigmas[parent_idx]

            # Self-adaptive sigma (1/5 rule approximation)
            tau = 1.0 / np.sqrt(2.0 * np.sqrt(n_params))
            new_sigma = sigma * np.exp(tau * rng.randn())
            new_sigma = np.clip(new_sigma, 1e-6, 1.0)

            # Mutate
            child = parent + new_sigma * rng.randn(n_params)
            offspring.append(child)
            off_sigmas.append(new_sigma)

            f, _ = compute_fitness_vectorized(child.reshape(N_DIM, N_DIM), M_norm, T_norm)
            off_fitnesses.append(f)

        # (mu + lambda) selection: combine parents + offspring, keep top mu
        all_pop = population + offspring
        all_sig = sigmas + off_sigmas
        all_fit = fitnesses + off_fitnesses

        sorted_idx = np.argsort(all_fit)[::-1]  # descending by fitness
        population = [all_pop[i] for i in sorted_idx[:MU]]
        sigmas = [all_sig[i] for i in sorted_idx[:MU]]
        fitnesses = [all_fit[i] for i in sorted_idx[:MU]]

        gen_best = fitnesses[0]
        if gen_best > best_fitness:
            best_fitness = gen_best
            best_w = population[0].copy()

        # Track convergence
        if gen % 100 == 0 or gen <= 10 or gen == max_gen:
            convergence.append({
                "generation": gen,
                "fitness": float(best_fitness),
                "mean_sigma": float(np.mean(sigmas))
            })

        if gen % 500 == 0 or gen <= 10:
            print(f"  Gen {gen:5d}: F = {best_fitness:.6f}, sigma = {np.mean(sigmas):.6f}", flush=True)

        # Check for convergence stall
        if gen % 100 == 0:
            if abs(best_fitness - prev_best) < 1e-8:
                stall_count += 1
            else:
                stall_count = 0
            prev_best = best_fitness
            if stall_count >= 20:  # 2000 generations with no improvement
                print(f"  Converged at gen {gen} (stall)", flush=True)
                break

    return best_w.reshape(N_DIM, N_DIM), best_fitness, convergence, gen


def main():
    print("NF20: Evolutionary Translation Viability Limit", flush=True)
    print("=" * 60, flush=True)
    t0 = time.time()

    # Load curves
    print("Loading genus-2 curves...", flush=True)
    with open("F:/Prometheus/cartography/genus2/data/genus2_curves_lmfdb.json") as f:
        data = json.load(f)
    records = data["records"]
    print(f"  Total curves in file: {len(records)}", flush=True)

    primes = sieve_primes(500)[:NUM_PRIMES]
    print(f"  Using {len(primes)} primes up to {primes[-1]}", flush=True)

    # Compute vectors
    print("Computing ST moment and trace vectors...", flush=True)
    np.random.seed(SEED)
    indices = np.random.permutation(len(records))

    moment_vecs, trace_vecs, labels = [], [], []
    tried = 0

    for idx in indices:
        if len(moment_vecs) >= MAX_CURVES:
            break
        tried += 1
        rec = records[idx]
        try:
            f_coeffs, h_coeffs = parse_equation(rec["equation"])
            cond = int(rec["conductor"])
        except (KeyError, ValueError, TypeError):
            continue

        result = compute_vectors_for_curve(f_coeffs, h_coeffs, cond, primes)
        if result is not None:
            mv, tv = result
            moment_vecs.append(mv)
            trace_vecs.append(tv)
            labels.append(rec["label"])

        if tried % 200 == 0:
            print(f"  ... tried {tried}, got {len(moment_vecs)} valid", flush=True)

    n_curves = len(moment_vecs)
    print(f"  Computed vectors for {n_curves} curves ({time.time()-t0:.1f}s)", flush=True)

    if n_curves < 10:
        print("ERROR: Too few curves")
        return

    M = np.array(moment_vecs)
    T = np.array(trace_vecs)

    # Standardize
    M_mean, M_std = M.mean(axis=0), M.std(axis=0)
    T_mean, T_std = T.mean(axis=0), T.std(axis=0)
    M_std[M_std < 1e-12] = 1.0
    T_std[T_std < 1e-12] = 1.0
    M_norm = (M - M_mean) / M_std
    T_norm = (T - T_mean) / T_std

    print(f"\n  Moment stats: mean|M| = {np.mean(np.abs(M)):.6f}", flush=True)
    print(f"  Trace stats:  mean|T| = {np.mean(np.abs(T)):.6f}", flush=True)

    # ── OLS baseline ───────────────────────────────────────────────────
    print("\nOLS baseline...", flush=True)
    W_ols = np.linalg.lstsq(M_norm, T_norm, rcond=None)[0].T
    ols_fitness, ols_corrs = compute_fitness_vectorized(W_ols, M_norm, T_norm)
    ols_cond = float(np.linalg.cond(W_ols))
    print(f"  OLS mean correlation: {ols_fitness:.6f}", flush=True)
    print(f"  OLS condition number: {ols_cond:.2e}", flush=True)

    # ── Also try ridge regression for a better seed ────────────────────
    print("\nRidge regression baseline...", flush=True)
    best_ridge_f = ols_fitness
    best_ridge_W = W_ols
    for alpha in [0.01, 0.1, 1.0, 10.0, 100.0]:
        MtM = M_norm.T @ M_norm
        W_ridge = np.linalg.solve(MtM + alpha * np.eye(N_DIM), M_norm.T @ T_norm).T
        rf, _ = compute_fitness_vectorized(W_ridge, M_norm, T_norm)
        print(f"  alpha={alpha:6.2f}: corr={rf:.6f}, cond={np.linalg.cond(W_ridge):.2e}", flush=True)
        if rf > best_ridge_f:
            best_ridge_f = rf
            best_ridge_W = W_ridge

    # Seed ES with the best linear solution
    W_seed = best_ridge_W if best_ridge_f > ols_fitness else W_ols
    seed_fitness = max(ols_fitness, best_ridge_f)
    print(f"\n  Best linear seed: {seed_fitness:.6f}", flush=True)

    # ── Evolutionary Strategy ──────────────────────────────────────────
    print(f"\n(mu+lambda)-ES: mu={MU}, lambda={LAMBDA}, max_gen={MAX_GENERATIONS}", flush=True)

    W_best, F_max_es, convergence, gens_used = mu_plus_lambda_es(
        M_norm, T_norm, W_seed, max_gen=MAX_GENERATIONS
    )

    # Use best overall
    F_max = max(F_max_es, seed_fitness)
    if F_max_es >= seed_fitness:
        W_final = W_best
    else:
        W_final = W_seed

    # ── Final analysis ─────────────────────────────────────────────────
    final_fitness, per_curve_corrs = compute_fitness_vectorized(W_final, M_norm, T_norm)
    cond_number = float(np.linalg.cond(W_final))

    elapsed = time.time() - t0

    print("\n" + "=" * 60, flush=True)
    print("RESULTS", flush=True)
    print("=" * 60, flush=True)
    print(f"  Curves used:                {n_curves}", flush=True)
    print(f"  F_max (best):               {F_max:.6f}", flush=True)
    print(f"  F_max (ES evolved):         {F_max_es:.6f}", flush=True)
    print(f"  OLS baseline:               {ols_fitness:.6f}", flush=True)
    print(f"  Best ridge:                 {best_ridge_f:.6f}", flush=True)
    print(f"  Matrix condition number:    {cond_number:.2e}", flush=True)
    print(f"  Generations used:           {gens_used}", flush=True)
    pcc = per_curve_corrs
    print(f"  Per-curve correlation dist:", flush=True)
    print(f"    mean   = {np.mean(pcc):.6f}", flush=True)
    print(f"    median = {np.median(pcc):.6f}", flush=True)
    print(f"    std    = {np.std(pcc):.6f}", flush=True)
    print(f"    min    = {np.min(pcc):.6f}", flush=True)
    print(f"    max    = {np.max(pcc):.6f}", flush=True)
    print(f"    >0.5   = {np.sum(pcc > 0.5)} ({100*np.mean(pcc>0.5):.1f}%)", flush=True)
    print(f"    >0.8   = {np.sum(pcc > 0.8)} ({100*np.mean(pcc>0.8):.1f}%)", flush=True)
    print(f"  Elapsed time:               {elapsed:.1f}s", flush=True)

    # ── Save ───────────────────────────────────────────────────────────
    output = {
        "challenge": "NF20",
        "description": "Evolutionary Translation Viability Limit",
        "method": "(mu+lambda)-ES seeded from ridge/OLS",
        "n_curves": n_curves,
        "n_dim": N_DIM,
        "n_primes": NUM_PRIMES,
        "es_params": {"mu": MU, "lambda": LAMBDA, "sigma_init": SIGMA_INIT},
        "max_generations": MAX_GENERATIONS,
        "generations_used": gens_used,
        "F_max": float(F_max),
        "F_max_evolved": float(F_max_es),
        "ols_baseline_mean_corr": float(ols_fitness),
        "ridge_baseline_mean_corr": float(best_ridge_f),
        "matrix_condition_number": cond_number,
        "ols_condition_number": ols_cond,
        "per_curve_correlation": {
            "mean": float(np.mean(pcc)),
            "median": float(np.median(pcc)),
            "std": float(np.std(pcc)),
            "min": float(np.min(pcc)),
            "max": float(np.max(pcc)),
            "frac_above_0.5": float(np.mean(pcc > 0.5)),
            "frac_above_0.8": float(np.mean(pcc > 0.8)),
            "quartiles": [float(np.percentile(pcc, q)) for q in [25, 50, 75]],
            "histogram_edges": [float(x) for x in np.linspace(-1, 1, 21)],
            "histogram_counts": [int(x) for x in np.histogram(pcc, bins=np.linspace(-1, 1, 21))[0]]
        },
        "convergence_curve": convergence,
        "W_best_frobenius_norm": float(np.linalg.norm(W_final, 'fro')),
        "W_best_spectral_norm": float(np.linalg.norm(W_final, 2)),
        "elapsed_seconds": elapsed
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}", flush=True)


if __name__ == "__main__":
    main()
