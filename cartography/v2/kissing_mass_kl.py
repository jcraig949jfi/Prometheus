"""
Kissing Number vs PDG Mass Ratios — KL divergence comparison.

Compares normalized lattice kissing number distribution with particle
mass ratio distribution. Null: is kissing closer to mass ratios than
to random positive integers?
"""

import json
import numpy as np
from scipy import stats
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
LATTICE_PATH = ROOT / "lmfdb_dump" / "lat_lattices.json"
PDG_PATH = ROOT / "physics" / "data" / "pdg" / "particles.json"
OUT_PATH = Path(__file__).resolve().parent / "kissing_mass_kl_results.json"

N_BINS = 50
N_NULL = 1000
RNG = np.random.default_rng(42)


def load_kissing_numbers():
    with open(LATTICE_PATH) as f:
        data = json.load(f)
    kissing = np.array([r["kissing"] for r in data["records"]
                        if r.get("kissing") is not None and r["kissing"] > 0],
                       dtype=float)
    print(f"Loaded {len(kissing)} kissing numbers (min={kissing.min()}, "
          f"max={kissing.max()}, median={np.median(kissing):.0f})")
    return kissing


def load_mass_ratios():
    with open(PDG_PATH) as f:
        particles = json.load(f)
    masses = np.array([p["mass_GeV"] for p in particles
                       if p.get("mass_GeV") and p["mass_GeV"] > 0])
    # All pairwise ratios m_i / m_j where m_i > m_j
    ratios = []
    for i in range(len(masses)):
        for j in range(len(masses)):
            if masses[i] > masses[j]:
                ratios.append(masses[i] / masses[j])
    ratios = np.array(ratios)
    print(f"Loaded {len(masses)} masses -> {len(ratios)} pairwise ratios "
          f"(min={ratios.min():.4f}, max={ratios.max():.2e})")
    return ratios


def normalize_and_bin(values, n_bins=N_BINS, eps=1e-10):
    """Normalize to [0,1] by dividing by max, then histogram into bins."""
    normed = values / values.max()
    counts, edges = np.histogram(normed, bins=n_bins, range=(0, 1))
    # Convert to probability distribution (add eps to avoid log(0))
    probs = (counts + eps) / (counts + eps).sum()
    return probs, edges


def kl_divergence(p, q):
    """KL(P || Q) = sum p_i * log(p_i / q_i)"""
    return float(np.sum(p * np.log(p / q)))


def symmetric_kl(p, q):
    """Jensen-Shannon style: (KL(P||Q) + KL(Q||P)) / 2"""
    return (kl_divergence(p, q) + kl_divergence(q, p)) / 2


def main():
    # ── Load data ──────────────────────────────────────────────────
    kissing = load_kissing_numbers()
    ratios = load_mass_ratios()

    # ── Bin both distributions ─────────────────────────────────────
    p_kiss, edges = normalize_and_bin(kissing)
    p_mass, _ = normalize_and_bin(ratios)

    # ── Divergence / distance metrics ──────────────────────────────
    kl_km = kl_divergence(p_kiss, p_mass)
    kl_mk = kl_divergence(p_mass, p_kiss)
    kl_sym = symmetric_kl(p_kiss, p_mass)

    # KS test on normalized values
    kiss_normed = kissing / kissing.max()
    ratio_normed = ratios / ratios.max()
    ks_stat, ks_pval = stats.ks_2samp(kiss_normed, ratio_normed)

    # Wasserstein distance on normalized values
    wass = float(stats.wasserstein_distance(kiss_normed, ratio_normed))

    print(f"\n-- Results --")
    print(f"KL(kiss || mass)  = {kl_km:.4f}")
    print(f"KL(mass || kiss)  = {kl_mk:.4f}")
    print(f"Symmetric KL      = {kl_sym:.4f}")
    print(f"KS statistic      = {ks_stat:.4f}  (p = {ks_pval:.2e})")
    print(f"Wasserstein       = {wass:.6f}")

    # ── Null model: random positive integers ───────────────────────
    # Draw same number of values as kissing, from power-law-ish dist
    # matching the range of kissing numbers
    null_kls = []
    null_kl_syms = []
    null_ks_stats = []
    null_wass = []

    for _ in range(N_NULL):
        # Random integers with similar range to kissing numbers
        rand_vals = RNG.integers(1, int(kissing.max()) + 1,
                                 size=len(kissing)).astype(float)
        p_rand, _ = normalize_and_bin(rand_vals)
        null_kls.append(kl_divergence(p_rand, p_mass))
        null_kl_syms.append(symmetric_kl(p_rand, p_mass))
        rand_normed = rand_vals / rand_vals.max()
        null_ks_stats.append(stats.ks_2samp(rand_normed, ratio_normed).statistic)
        null_wass.append(float(stats.wasserstein_distance(rand_normed, ratio_normed)))

    null_kls = np.array(null_kls)
    null_kl_syms = np.array(null_kl_syms)
    null_ks_stats = np.array(null_ks_stats)
    null_wass_arr = np.array(null_wass)

    # Percentile of observed value in null distribution
    kl_pct = float(np.mean(null_kls <= kl_km) * 100)
    sym_pct = float(np.mean(null_kl_syms <= kl_sym) * 100)
    ks_pct = float(np.mean(null_ks_stats <= ks_stat) * 100)
    wass_pct = float(np.mean(null_wass_arr <= wass) * 100)

    print(f"\n-- Null comparison (uniform random integers, N={N_NULL}) --")
    print(f"KL(kiss||mass) percentile in null: {kl_pct:.1f}%")
    print(f"  null mean={null_kls.mean():.4f} ± {null_kls.std():.4f}")
    print(f"Symmetric KL percentile in null:   {sym_pct:.1f}%")
    print(f"  null mean={null_kl_syms.mean():.4f} ± {null_kl_syms.std():.4f}")
    print(f"KS percentile in null:             {ks_pct:.1f}%")
    print(f"  null mean={null_ks_stats.mean():.4f} ± {null_ks_stats.std():.4f}")
    print(f"Wasserstein percentile in null:     {wass_pct:.1f}%")
    print(f"  null mean={null_wass_arr.mean():.6f} ± {null_wass_arr.std():.6f}")

    # Closer = lower KL/KS/Wasserstein → lower percentile means kissing
    # is closer to mass ratios than random
    closer = kl_pct < 50
    print(f"\nKissing distribution {'IS' if closer else 'is NOT'} closer to "
          f"mass ratios than random integers (KL percentile {kl_pct:.1f}%)")

    # ── Save results ───────────────────────────────────────────────
    results = {
        "description": "KL divergence: lattice kissing numbers vs PDG mass ratios",
        "n_lattices": int(len(kissing)),
        "n_masses": int(len(ratios)),
        "n_bins": N_BINS,
        "metrics": {
            "kl_kiss_given_mass": round(kl_km, 6),
            "kl_mass_given_kiss": round(kl_mk, 6),
            "symmetric_kl": round(kl_sym, 6),
            "ks_statistic": round(ks_stat, 6),
            "ks_pvalue": float(f"{ks_pval:.6e}"),
            "wasserstein": round(wass, 6),
        },
        "null_model": {
            "type": "uniform_random_integers",
            "n_trials": N_NULL,
            "kl_null_mean": round(float(null_kls.mean()), 6),
            "kl_null_std": round(float(null_kls.std()), 6),
            "kl_percentile": round(kl_pct, 2),
            "symmetric_kl_null_mean": round(float(null_kl_syms.mean()), 6),
            "symmetric_kl_null_std": round(float(null_kl_syms.std()), 6),
            "symmetric_kl_percentile": round(sym_pct, 2),
            "ks_null_mean": round(float(null_ks_stats.mean()), 6),
            "ks_null_std": round(float(null_ks_stats.std()), 6),
            "ks_percentile": round(ks_pct, 2),
            "wasserstein_null_mean": round(float(null_wass_arr.mean()), 6),
            "wasserstein_null_std": round(float(null_wass_arr.std()), 6),
            "wasserstein_percentile": round(wass_pct, 2),
        },
        "interpretation": {
            "closer_than_random": closer,
            "summary": (
                f"Kissing number distribution has KL={kl_sym:.4f} to mass ratios "
                f"(percentile {kl_pct:.1f}% vs random null). "
                f"{'Closer' if closer else 'Not closer'} than random integers."
            ),
        },
        "distributions": {
            "kissing_histogram": [round(float(x), 8) for x in p_kiss],
            "mass_ratio_histogram": [round(float(x), 8) for x in p_mass],
            "bin_edges": [round(float(x), 4) for x in edges],
        },
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {OUT_PATH}")


if __name__ == "__main__":
    main()
