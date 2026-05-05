"""Compute Sum_{n<=N} mu(n) f(T^n x) for some specific zero-entropy
dynamical systems and report normalized partial sums.

Targets:
  (a) f(T^n x) = e(n alpha) where alpha = sqrt(2)
      (Davenport 1937 type — proven orthogonality, calibration anchor)
  (b) f(T^n x) = e(n^2 alpha)  (polynomial degree 2; harder)
      Proven by Hua-Vinogradov / Sarnak; calibration with weak orthogonality
  (c) Sturmian-like: f(T^n x) = chi[0,beta)( n alpha mod 1 ),
      indicator of Sturmian word — zero entropy. Should also be orthogonal
      to mu (Bourgain et al).
  (d) Random subset density 1/2 (positive entropy, NOT zero entropy)
      — should NOT be orthogonal to mu under Sarnak; calibration that
      our numerics SEE the difference.

We compute partial sums up to N = 1e6 and 1e7 and check decay.
"""
import json
import time
import numpy as np


def mobius_array(N):
    """Standard sieve for Mobius up to N."""
    mu = np.ones(N + 1, dtype=np.int8)
    mu[0] = 0
    is_prime = np.ones(N + 1, dtype=bool)
    is_prime[0:2] = False
    p_min = np.zeros(N + 1, dtype=np.int64)
    primes = []
    for i in range(2, N + 1):
        if is_prime[i]:
            primes.append(i)
            p_min[i] = i
        for p in primes:
            ip = i * p
            if ip > N:
                break
            is_prime[ip] = False
            p_min[ip] = p
            if i % p == 0:
                break
    # Now compute mu via factorization-by-smallest-prime
    mu = np.zeros(N + 1, dtype=np.int8)
    mu[1] = 1
    for n in range(2, N + 1):
        p = p_min[n]
        m = n // p
        if m % p == 0:
            mu[n] = 0
        else:
            mu[n] = -mu[m]
    return mu


def linear_phase_sum(mu, alpha):
    n = np.arange(1, len(mu))
    e = np.exp(2j * np.pi * n * alpha)
    return np.cumsum(mu[1:] * e)


def quadratic_phase_sum(mu, alpha):
    n = np.arange(1, len(mu))
    e = np.exp(2j * np.pi * (n.astype(np.float64) ** 2) * alpha)
    return np.cumsum(mu[1:] * e)


def sturmian_sum(mu, alpha, beta):
    n = np.arange(1, len(mu))
    frac = (n * alpha) % 1.0
    chi = (frac < beta).astype(np.float64) - beta  # mean-subtracted
    return np.cumsum(mu[1:] * chi)


def random_05_sum(mu, seed=0):
    rng = np.random.default_rng(seed)
    f = (rng.uniform(0, 1, len(mu) - 1) > 0.5).astype(np.float64) - 0.5
    return np.cumsum(mu[1:] * f)


def report_decay(name, S, label_powers=(3, 4, 5, 6)):
    out = {"name": name}
    for p in label_powers:
        N = 10 ** p
        if N <= len(S):
            v = abs(S[N - 1]) / N
            out[f"|S(10^{p})|/10^{p}"] = float(v)
    return out


if __name__ == "__main__":
    t0 = time.time()
    N = 1_000_000  # 10^6
    print(f"Sieving Mobius up to {N}...")
    mu = mobius_array(N)
    print(f"  Mobius nonzero density: {(mu != 0).mean():.6f} (theory: 6/pi^2 ~ 0.6079)")

    alpha = np.sqrt(2)

    print("\n(a) Linear phase: e(n*sqrt(2))")
    Sa = linear_phase_sum(mu, alpha)
    decay_a = report_decay("linear_phase_sqrt2", Sa)
    print(decay_a)

    print("\n(b) Quadratic phase: e(n^2 * sqrt(2))")
    Sb = quadratic_phase_sum(mu, alpha)
    decay_b = report_decay("quadratic_phase_sqrt2", Sb)
    print(decay_b)

    print("\n(c) Sturmian indicator: chi[0, golden_ratio_minus_1) of n * sqrt(2)")
    beta = 0.61803398875  # golden ratio - 1; arbitrary choice in (0,1)
    Sc = sturmian_sum(mu, alpha, beta)
    decay_c = report_decay("sturmian_sqrt2_phi", Sc)
    print(decay_c)

    print("\n(d) Random ±1/2 (positive entropy; should NOT decay relative to N^{1/2})")
    Sd = random_05_sum(mu, seed=42)
    decay_d = report_decay("random_pos_entropy", Sd)
    print(decay_d)

    print("\n(d') Same again seed 123 to see variance")
    Sd2 = random_05_sum(mu, seed=123)
    decay_d2 = report_decay("random_pos_entropy_seed123", Sd2)
    print(decay_d2)

    elapsed = time.time() - t0

    payload = {
        "elapsed_sec": elapsed,
        "N": N,
        "results": [decay_a, decay_b, decay_c, decay_d, decay_d2],
    }
    with open("D:/Prometheus/aporia/meta/experiments/2026-05-05/attempts/_scratch_B/sarnak_results.json", "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\nDone in {elapsed:.1f}s")
