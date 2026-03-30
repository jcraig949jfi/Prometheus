"""
Prime Cone Computation — Project Prometheus / Noesis v2
Aletheia overnight task 6.

Maps primes onto conical surfaces via continuous spiral and measures
angular alignment compared to Cramer random-prime null models.

Mapping: each integer n is placed at arc-length n along a spiral that
winds up the cone surface.  At height h the radius is r(h), so the
relationship between arc-length s and (h, theta) comes from:
   ds^2 = dh^2 + r(h)^2 d(theta)^2
We fix d(theta)/ds = 1/r(h) (one radian per r units of arc) and
dh/ds = sin(beta) where beta is a small pitch angle.

Simpler and more standard: Ulam-style.  Place integer n at:
   h(n)     = sqrt(n)              (height grows as sqrt)
   theta(n) = 2*pi*n * golden_ratio  (golden-angle spacing, irrational => never repeats)

This gives a quasi-uniform filling of (theta, h) space for ALL integers,
and any structure in primes shows up as non-uniform angular distribution
relative to random.

For the CONE geometry, the radius at height h determines the local
density.  We apply the cone via:
   r_std(h) = h * sin(alpha)       # standard cone
   r_log(h) = k * ln(1 + h)       # log cone

The angular coordinate on the cone surface is:
   phi(n) = (cumulative_angle up to n)
where the angular increment per step is d_phi = arc_step / r(h(n)).
So phi(n) = sum_{i=1}^{n} 1/r(h(i))  (mod 2*pi)

This means at small radii, the spiral winds fast (many turns per unit
height) and at large radii it winds slowly — physically correct.
"""

import numpy as np
import json
import time
from pathlib import Path

# ── Parameters ──────────────────────────────────────────────────────
N = 1_000_000
ALPHA = np.pi / 6          # standard cone half-angle
N_BANDS = 100              # bands for alignment analysis
N_SECTORS = 36             # angular bins per band
SEED = 42
N_TRIALS = 3

OUT_DIR = Path(__file__).parent
PLOT_DIR = Path("F:/prometheus/prime_cone")


# ── 1. Sieve of Eratosthenes (numpy) ───────────────────────────────
def sieve(n):
    is_prime = np.ones(n + 1, dtype=bool)
    is_prime[:2] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    return is_prime


# ── 2. Height function ─────────────────────────────────────────────
def height(n_array):
    """Height on cone: h = sqrt(n). Gives good spread."""
    return np.sqrt(n_array.astype(np.float64))


# ── 3. Cone angular coordinates via cumulative winding ──────────────
def cone_angles(h_all, radius_fn):
    """
    Compute angular position for each integer 1..N on a cone.

    Angular increment at step i: d_phi = 1 / r(h(i))
    phi(n) = cumsum of d_phi, taken mod 2*pi

    Returns phi mod 2*pi for all n.
    """
    radii = radius_fn(h_all)
    # Avoid division by zero at h=0
    radii = np.maximum(radii, 1e-10)
    d_phi = 1.0 / radii
    phi_cumulative = np.cumsum(d_phi)
    return phi_cumulative % (2 * np.pi)


def radius_standard(h):
    """Standard cone: r = h * sin(alpha)"""
    return h * np.sin(ALPHA)


def radius_log(h, k=None):
    """Log cone: r = k * ln(1 + h)"""
    if k is None:
        # k chosen so r_log(sqrt(N)) = r_std(sqrt(N))
        h_max = np.sqrt(N)
        k = h_max * np.sin(ALPHA) / np.log1p(h_max)
    return k * np.log1p(h)


# ── 4. Alignment metric (chi-squared style) ────────────────────────
def alignment_scores(thetas, heights, h_all_sorted, n_bands, n_sectors):
    """
    Divide height range into n_bands equal bands.
    For each band, compute how concentrated primes are angularly:
      - Bin prime angles into n_sectors bins
      - Compute chi-squared statistic vs uniform expectation
      - Higher chi2 = more alignment/concentration

    Also compute occupied-sectors metric:
      vacancy = n_sectors - count(sectors with >=1 prime)
    """
    h_min, h_max = h_all_sorted[0], h_all_sorted[-1]
    band_edges = np.linspace(h_min, h_max, n_bands + 1)

    chi2_scores = np.empty(n_bands, dtype=np.float64)
    vacancy_scores = np.empty(n_bands, dtype=np.float64)

    sector_edges = np.linspace(0, 2 * np.pi, n_sectors + 1)

    for b in range(n_bands):
        mask = (heights >= band_edges[b]) & (heights < band_edges[b + 1])
        n_in_band = mask.sum()

        if n_in_band < 2:
            chi2_scores[b] = 0.0
            vacancy_scores[b] = n_sectors - min(n_in_band, 1)
            continue

        band_thetas = thetas[mask]
        counts, _ = np.histogram(band_thetas, bins=sector_edges)
        expected = n_in_band / n_sectors
        chi2 = np.sum((counts - expected) ** 2 / expected)
        chi2_scores[b] = chi2

        occupied = np.count_nonzero(counts)
        vacancy_scores[b] = n_sectors - occupied

    return chi2_scores, vacancy_scores


# ── 5. Cramer random primes ────────────────────────────────────────
def cramer_random_primes(n, seed):
    rng = np.random.default_rng(seed)
    ns = np.arange(2, n + 1)
    probs = 1.0 / np.log(ns)
    is_prime = rng.random(len(ns)) < probs
    full = np.zeros(n + 1, dtype=bool)
    full[2:] = is_prime
    return full


# ── Main ────────────────────────────────────────────────────────────
def main():
    t0 = time.time()
    print(f"[prime_cone] N = {N:,}")

    # Step 1: sieve
    print("[1] Sieving primes ...")
    is_prime = sieve(N)
    primes = np.nonzero(is_prime)[0]
    print(f"    {len(primes):,} primes found up to {N:,}")

    # Step 2: compute heights for all integers
    all_n = np.arange(1, N + 1)
    h_all = height(all_n)

    # Compute k_log
    h_max = np.sqrt(N)
    k_log = h_max * np.sin(ALPHA) / np.log1p(h_max)

    # Step 3: Standard cone angles
    print("[2] Standard cone winding ...")
    theta_all_std = cone_angles(h_all, radius_standard)

    # Step 4: Log cone angles
    print("[3] Log cone winding ...")
    theta_all_log = cone_angles(h_all, lambda h: radius_log(h, k_log))

    # Extract prime coordinates
    prime_mask = is_prime[1:]  # shift: index 0 -> n=1
    theta_primes_std = theta_all_std[prime_mask]
    theta_primes_log = theta_all_log[prime_mask]
    h_primes = h_all[prime_mask]

    # Step 5: Alignment — real primes
    print("[4] Computing alignment (real primes) ...")
    chi2_std_real, vac_std_real = alignment_scores(
        theta_primes_std, h_primes, h_all, N_BANDS, N_SECTORS)
    chi2_log_real, vac_log_real = alignment_scores(
        theta_primes_log, h_primes, h_all, N_BANDS, N_SECTORS)

    # Step 6: Cramer null model
    print("[5] Cramer null model (3 trials) ...")
    chi2_std_rand_all = []
    chi2_log_rand_all = []
    vac_std_rand_all = []
    vac_log_rand_all = []

    for trial in range(N_TRIALS):
        seed = SEED + trial
        is_rand = cramer_random_primes(N, seed)
        rand_mask = is_rand[1:]

        theta_rand_std = theta_all_std[rand_mask]
        theta_rand_log = theta_all_log[rand_mask]
        h_rand = h_all[rand_mask]

        c2s, vs = alignment_scores(theta_rand_std, h_rand, h_all, N_BANDS, N_SECTORS)
        c2l, vl = alignment_scores(theta_rand_log, h_rand, h_all, N_BANDS, N_SECTORS)

        chi2_std_rand_all.append(c2s)
        chi2_log_rand_all.append(c2l)
        vac_std_rand_all.append(vs)
        vac_log_rand_all.append(vl)

        rand_count = np.count_nonzero(is_rand)
        print(f"    trial {trial}: {rand_count:,} random primes")

    chi2_std_rand = np.mean(chi2_std_rand_all, axis=0)
    chi2_log_rand = np.mean(chi2_log_rand_all, axis=0)
    vac_std_rand = np.mean(vac_std_rand_all, axis=0)
    vac_log_rand = np.mean(vac_log_rand_all, axis=0)

    # Step 7: Summary
    print("[6] Results summary ...")

    def stats(arr):
        return {
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "median": float(np.median(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
        }

    results = {
        "N": N,
        "n_primes": int(len(primes)),
        "alpha_rad": ALPHA,
        "k_log": float(k_log),
        "n_bands": N_BANDS,
        "n_sectors": N_SECTORS,
        "height_fn": "sqrt(n)",
        "winding": "cumulative 1/r(h) mod 2*pi",
        "standard_cone": {
            "chi2_real": stats(chi2_std_real),
            "chi2_random": stats(chi2_std_rand),
            "chi2_delta": float(np.mean(chi2_std_real) - np.mean(chi2_std_rand)),
            "vacancy_real": stats(vac_std_real),
            "vacancy_random": stats(vac_std_rand),
            "vacancy_delta": float(np.mean(vac_std_real) - np.mean(vac_std_rand)),
        },
        "log_cone": {
            "chi2_real": stats(chi2_log_real),
            "chi2_random": stats(chi2_log_rand),
            "chi2_delta": float(np.mean(chi2_log_real) - np.mean(chi2_log_rand)),
            "vacancy_real": stats(vac_log_real),
            "vacancy_random": stats(vac_log_rand),
            "vacancy_delta": float(np.mean(vac_log_real) - np.mean(vac_log_rand)),
        },
        "comparison": {
            "chi2_log_minus_std_real": float(np.mean(chi2_log_real) - np.mean(chi2_std_real)),
            "log_shows_more_structure_chi2": bool(np.mean(chi2_log_real) > np.mean(chi2_std_real)),
            "real_beats_random_std_chi2": bool(np.mean(chi2_std_real) > np.mean(chi2_std_rand)),
            "real_beats_random_log_chi2": bool(np.mean(chi2_log_real) > np.mean(chi2_log_rand)),
            "vacancy_log_minus_std_real": float(np.mean(vac_log_real) - np.mean(vac_std_real)),
            "log_shows_more_structure_vacancy": bool(np.mean(vac_log_real) > np.mean(vac_std_real)),
        },
        "elapsed_seconds": round(time.time() - t0, 2),
    }

    # Print key findings
    sc = results["standard_cone"]
    lc = results["log_cone"]
    comp = results["comparison"]

    print(f"\n{'='*70}")
    print(f"  STANDARD CONE  (r = h*sin(alpha))")
    print(f"    chi2 real:   mean={sc['chi2_real']['mean']:.2f}  std={sc['chi2_real']['std']:.2f}")
    print(f"    chi2 random: mean={sc['chi2_random']['mean']:.2f}  std={sc['chi2_random']['std']:.2f}")
    print(f"    delta:       {sc['chi2_delta']:.2f}")
    print(f"    vacancy real:   {sc['vacancy_real']['mean']:.2f}")
    print(f"    vacancy random: {sc['vacancy_random']['mean']:.2f}")
    print()
    print(f"  LOG CONE  (r = k*ln(1+h))")
    print(f"    chi2 real:   mean={lc['chi2_real']['mean']:.2f}  std={lc['chi2_real']['std']:.2f}")
    print(f"    chi2 random: mean={lc['chi2_random']['mean']:.2f}  std={lc['chi2_random']['std']:.2f}")
    print(f"    delta:       {lc['chi2_delta']:.2f}")
    print(f"    vacancy real:   {lc['vacancy_real']['mean']:.2f}")
    print(f"    vacancy random: {lc['vacancy_random']['mean']:.2f}")
    print()
    print(f"  COMPARISON")
    print(f"    Log shows MORE structure (chi2)?    {comp['log_shows_more_structure_chi2']}")
    print(f"    Real beats random (std, chi2)?      {comp['real_beats_random_std_chi2']}")
    print(f"    Real beats random (log, chi2)?      {comp['real_beats_random_log_chi2']}")
    print(f"    chi2 log-std (real):                {comp['chi2_log_minus_std_real']:.2f}")
    print(f"{'='*70}")

    # Step 8: Save results JSON
    json_path = OUT_DIR / "prime_cone_results.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[7] Results saved to {json_path}")

    # Step 9: Save coords
    npz_path = OUT_DIR / "prime_cone_coords.npz"
    np.savez_compressed(
        npz_path,
        primes=primes,
        theta_std=theta_primes_std,
        theta_log=theta_primes_log,
        heights=h_primes,
    )
    print(f"[8] Coordinates saved to {npz_path}")
    print(f"\nDone in {time.time()-t0:.1f}s")

    return results


if __name__ == "__main__":
    main()
