"""
Conductor distribution comparison: genus-2 curves vs elliptic curves.
Loads genus-2 from JSON, EC from charon DuckDB.
"""
import json
import numpy as np
import duckdb
from collections import Counter
from pathlib import Path

# ── Load data ──────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent

# Genus-2: use full file (66K curves)
g2_full = json.loads((BASE / "genus2/data/genus2_curves_full.json").read_text())
g2_conds = np.array([r["conductor"] for r in g2_full], dtype=np.int64)

# EC from DuckDB
con = duckdb.connect(str(BASE.parent / "charon/data/charon.duckdb"), read_only=True)
ec_conds = np.array(con.sql("SELECT conductor FROM elliptic_curves").fetchnumpy()["conductor"], dtype=np.int64)
con.close()

print(f"Genus-2 curves: {len(g2_conds)}")
print(f"EC curves:      {len(ec_conds)}")

# ── 1. Basic distribution stats ───────────────────────────────────────
def dist_stats(arr, name):
    return {
        "name": name,
        "count": int(len(arr)),
        "min": int(arr.min()),
        "max": int(arr.max()),
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "std": float(np.std(arr)),
        "p25": float(np.percentile(arr, 25)),
        "p75": float(np.percentile(arr, 75)),
        "p90": float(np.percentile(arr, 90)),
        "p99": float(np.percentile(arr, 99)),
        "num_distinct_conductors": int(len(np.unique(arr))),
    }

g2_stats = dist_stats(g2_conds, "genus-2")
ec_stats = dist_stats(ec_conds, "elliptic_curves")

print("\n── Distribution Stats ──")
for k in g2_stats:
    if k == "name":
        continue
    print(f"  {k:30s}  G2={g2_stats[k]:>14}  EC={ec_stats[k]:>14}")

# ── 2. Curves per conductor (density) ─────────────────────────────────
g2_counter = Counter(g2_conds.tolist())
ec_counter = Counter(ec_conds.tolist())

g2_curves_per_cond = np.array(list(g2_counter.values()))
ec_curves_per_cond = np.array(list(ec_counter.values()))

density_stats = {
    "genus2_mean_curves_per_conductor": float(np.mean(g2_curves_per_cond)),
    "genus2_median_curves_per_conductor": float(np.median(g2_curves_per_cond)),
    "genus2_max_curves_per_conductor": int(np.max(g2_curves_per_cond)),
    "ec_mean_curves_per_conductor": float(np.mean(ec_curves_per_cond)),
    "ec_median_curves_per_conductor": float(np.median(ec_curves_per_cond)),
    "ec_max_curves_per_conductor": int(np.max(ec_curves_per_cond)),
}

print("\n── Curves per Conductor ──")
for k, v in density_stats.items():
    print(f"  {k}: {v}")

# ── 3. Prime conductor fraction ───────────────────────────────────────
def is_prime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

# Use sympy if available, else manual
try:
    from sympy import isprime
    _isprime = isprime
except ImportError:
    _isprime = is_prime

g2_unique_conds = np.unique(g2_conds)
ec_unique_conds = np.unique(ec_conds)

g2_prime_conds = sum(1 for c in g2_unique_conds if _isprime(int(c)))
ec_prime_conds = sum(1 for c in ec_unique_conds if _isprime(int(c)))

prime_stats = {
    "genus2_prime_conductor_fraction": g2_prime_conds / len(g2_unique_conds),
    "genus2_prime_conductors": g2_prime_conds,
    "genus2_total_distinct_conductors": len(g2_unique_conds),
    "ec_prime_conductor_fraction": ec_prime_conds / len(ec_unique_conds),
    "ec_prime_conductors": ec_prime_conds,
    "ec_total_distinct_conductors": len(ec_unique_conds),
}

print("\n── Prime Conductor Fraction ──")
for k, v in prime_stats.items():
    print(f"  {k}: {v}")

# ── 4. Growth exponent: #{curves with cond ≤ N} ~ N^α ────────────────
def fit_growth_exponent(conds):
    """Fit cumulative count ~ N^alpha using log-log linear regression."""
    sorted_c = np.sort(conds)
    # Sample ~200 log-spaced thresholds
    N_vals = np.unique(np.geomspace(sorted_c.min(), sorted_c.max(), 300).astype(np.int64))
    counts = np.searchsorted(sorted_c, N_vals, side="right")
    # Filter to positive counts
    mask = counts > 0
    N_vals, counts = N_vals[mask], counts[mask]
    log_N = np.log(N_vals.astype(float))
    log_C = np.log(counts.astype(float))
    # Linear fit: log_C = alpha * log_N + beta
    alpha, beta = np.polyfit(log_N, log_C, 1)
    residuals = log_C - (alpha * log_N + beta)
    r_squared = 1 - np.var(residuals) / np.var(log_C)
    return float(alpha), float(beta), float(r_squared)

g2_alpha, g2_beta, g2_r2 = fit_growth_exponent(g2_conds)
ec_alpha, ec_beta, ec_r2 = fit_growth_exponent(ec_conds)

growth_stats = {
    "genus2_alpha": round(g2_alpha, 4),
    "genus2_r_squared": round(g2_r2, 6),
    "ec_alpha": round(ec_alpha, 4),
    "ec_r_squared": round(ec_r2, 6),
    "interpretation": (
        f"genus-2: N(cond<=N) ~ N^{g2_alpha:.3f}, "
        f"EC: N(cond<=N) ~ N^{ec_alpha:.3f}. "
        + ("Genus-2 grows FASTER." if g2_alpha > ec_alpha else
           "EC grows FASTER." if ec_alpha > g2_alpha else
           "Same rate.")
    ),
}

print("\n── Growth Exponent (N^α fit) ──")
for k, v in growth_stats.items():
    print(f"  {k}: {v}")

# ── 5. Histogram shape comparison (log-binned) ────────────────────────
log_bins = np.geomspace(
    min(g2_conds.min(), ec_conds.min()),
    max(g2_conds.max(), ec_conds.max()),
    30,
)
g2_hist, _ = np.histogram(g2_conds, bins=log_bins)
ec_hist, _ = np.histogram(ec_conds, bins=log_bins)

# Normalize to density
g2_density = g2_hist / g2_hist.sum()
ec_density = ec_hist / ec_hist.sum()

histogram = {
    "bin_edges": [float(b) for b in log_bins],
    "genus2_counts": [int(c) for c in g2_hist],
    "ec_counts": [int(c) for c in ec_hist],
    "genus2_density": [round(float(d), 6) for d in g2_density],
    "ec_density": [round(float(d), 6) for d in ec_density],
}

# ── Assemble results ──────────────────────────────────────────────────
results = {
    "genus2_distribution": g2_stats,
    "ec_distribution": ec_stats,
    "density_scaling": density_stats,
    "prime_conductor_fraction": prime_stats,
    "growth_exponent": growth_stats,
    "histogram": histogram,
    "summary": {
        "genus2_alpha": growth_stats["genus2_alpha"],
        "ec_alpha": growth_stats["ec_alpha"],
        "genus2_faster": g2_alpha > ec_alpha,
        "genus2_median_conductor": g2_stats["median"],
        "ec_median_conductor": ec_stats["median"],
        "genus2_prime_fraction": round(prime_stats["genus2_prime_conductor_fraction"], 4),
        "ec_prime_fraction": round(prime_stats["ec_prime_conductor_fraction"], 4),
        "genus2_mean_per_cond": round(density_stats["genus2_mean_curves_per_conductor"], 3),
        "ec_mean_per_cond": round(density_stats["ec_mean_curves_per_conductor"], 3),
    },
}

out_path = Path(__file__).resolve().parent / "conductor_comparison_results.json"
out_path.write_text(json.dumps(results, indent=2))
print(f"\nResults saved to {out_path}")
