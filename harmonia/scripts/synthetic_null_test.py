"""
Synthetic Null Test — The most powerful missing piece.

Construct fake data where:
  - zeros follow RMT spacing (GUE)
  - class_size assigned randomly or via simple conductor model
Then test: does our pipeline falsely recover a signal?

If yes -> artifact in methodology
If no  -> strong evidence of genuine coupling
"""
import numpy as np
import duckdb
import json
from pathlib import Path
from scipy.stats import spearmanr
from scipy.linalg import eigvalsh

print("SYNTHETIC NULL TEST")
print("=" * 60)
print("Does our pipeline falsely recover a signal from synthetic data?")
print()

# ---- Load REAL data for calibration ----
db = duckdb.connect(str(Path("charon/data/charon.duckdb")), read_only=True)
real_rows = db.sql("""
    SELECT ec.conductor, ec.class_size, ec.rank, ec.cm,
           oz.zeros_vector
    FROM object_zeros oz
    JOIN elliptic_curves ec ON oz.object_id = ec.object_id
    WHERE oz.n_zeros_stored >= 5 AND oz.zeros_vector IS NOT NULL
          AND ec.conductor IS NOT NULL AND ec.conductor <= 50000
          AND ec.class_size IS NOT NULL
""").fetchall()
db.close()

real_data = []
for cond, cs, rank, cm, zvec in real_rows:
    zeros = sorted([z for z in (zvec or []) if z is not None and z > 0])
    if len(zeros) < 3:
        continue
    real_data.append({
        "conductor": int(cond),
        "class_size": int(cs),
        "rank": int(rank or 0),
        "spacing": zeros[1] - zeros[0],
        "gamma1": zeros[0],
    })

n_real = len(real_data)
print(f"Real data: {n_real} curves")

real_conductors = np.array([d["conductor"] for d in real_data])
real_class_sizes = np.array([d["class_size"] for d in real_data])
real_spacings = np.array([d["spacing"] for d in real_data])
real_log_N = np.log10(np.clip(real_conductors, 2, None))

# Real signal for comparison
real_rho, real_p = spearmanr(real_spacings, real_class_sizes)
print(f"Real signal: spacing vs class_size rho={real_rho:.4f}, p={real_p:.2e}")

# ---- SYNTHETIC MODEL 1: Pure GUE zeros, shuffled class_size ----
print("\n" + "-" * 40)
print("SYNTHETIC 1: GUE zeros + randomly assigned class_size")
print("(preserving marginal distributions of both)")
print("-" * 40)

# Generate GUE spacings calibrated to real data
# Use the actual class_size distribution but shuffle assignment
n_synth = n_real

# For GUE nearest-neighbor spacing: Wigner surmise p(s) = (pi/2)*s*exp(-pi*s^2/4)
# Generate from this distribution
def sample_wigner_surmise(n):
    """Sample from Wigner surmise (GUE nearest-neighbor spacing)."""
    # CDF inversion: F(s) = 1 - exp(-pi*s^2/4)
    u = np.random.uniform(0, 1, n)
    return np.sqrt(-4 * np.log(1 - u) / np.pi)

# Scale GUE spacings to match real spacing statistics
real_mean_spacing = np.mean(real_spacings)
real_std_spacing = np.std(real_spacings)

n_trials = 200
false_positives_1 = []

for trial in range(n_trials):
    # Generate GUE spacings, scaled to match real distribution moments
    synth_spacings = sample_wigner_surmise(n_synth)
    synth_spacings = synth_spacings * (real_mean_spacing / np.mean(synth_spacings))

    # Assign class_size by random permutation (no coupling)
    synth_class_size = np.random.permutation(real_class_sizes)

    # Use real conductors (preserving conductor structure)
    synth_log_N = real_log_N.copy()

    # Run the SAME analysis pipeline as our kill protocol
    # Within-bin Spearman correlation (50 bins)
    bins = np.percentile(synth_log_N, np.linspace(0, 100, 51))
    bin_rhos = []
    for b in range(50):
        mask = (synth_log_N >= bins[b]) & (synth_log_N < bins[b + 1])
        if mask.sum() < 30:
            continue
        r, _ = spearmanr(synth_spacings[mask], synth_class_size[mask])
        if not np.isnan(r):
            bin_rhos.append(r)
    false_positives_1.append(np.mean(bin_rhos) if bin_rhos else 0.0)

synth1_mean = np.mean(false_positives_1)
synth1_std = np.std(false_positives_1)
print(f"Synthetic 1 mean rho: {synth1_mean:.6f} +/- {synth1_std:.6f}")
print(f"Real within-bin rho: -0.1628")
print(f"False positive rate (|rho| > 0.05): {np.mean(np.abs(false_positives_1) > 0.05)*100:.1f}%")

# ---- SYNTHETIC MODEL 2: Real zeros, conductor-correlated class_size ----
print("\n" + "-" * 40)
print("SYNTHETIC 2: REAL zeros + class_size correlated with conductor")
print("(tests if conductor geometry alone generates the signal)")
print("-" * 40)

# Assign class_size based on conductor (matching real correlation)
# but break any direct coupling to zeros
from sklearn.linear_model import LinearRegression

# Fit class_size ~ conductor model from real data
reg = LinearRegression()
reg.fit(real_log_N.reshape(-1, 1), real_class_sizes)
predicted_cs = reg.predict(real_log_N.reshape(-1, 1))
residual_cs = real_class_sizes - predicted_cs

false_positives_2 = []
for trial in range(n_trials):
    # Keep real zeros, but generate class_size from conductor model + shuffled residual
    synth_cs = predicted_cs + np.random.permutation(residual_cs)
    synth_cs = np.clip(np.round(synth_cs), 1, None).astype(int)

    bins = np.percentile(real_log_N, np.linspace(0, 100, 51))
    bin_rhos = []
    for b in range(50):
        mask = (real_log_N >= bins[b]) & (real_log_N < bins[b + 1])
        if mask.sum() < 30:
            continue
        r, _ = spearmanr(real_spacings[mask], synth_cs[mask])
        if not np.isnan(r):
            bin_rhos.append(r)
    false_positives_2.append(np.mean(bin_rhos) if bin_rhos else 0.0)

synth2_mean = np.mean(false_positives_2)
synth2_std = np.std(false_positives_2)
print(f"Synthetic 2 mean rho: {synth2_mean:.6f} +/- {synth2_std:.6f}")
print(f"False positive rate (|rho| > 0.05): {np.mean(np.abs(false_positives_2) > 0.05)*100:.1f}%")

# ---- SYNTHETIC MODEL 3: Real zeros, class_size from FACTORIZATION model ----
print("\n" + "-" * 40)
print("SYNTHETIC 3: REAL zeros + class_size predicted from conductor FACTORIZATION")
print("(tests the conductor geometry confound directly)")
print("-" * 40)

# Compute conductor factorization features
def factorization_features(n):
    """Number of prime factors, largest prime factor, etc."""
    if n <= 1:
        return [0, 0, 0, 0]
    orig = n
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return [
        len(factors),  # omega (with multiplicity)
        len(set(factors)),  # omega (distinct)
        max(factors) if factors else 0,  # largest prime factor
        1 if (len(factors) == 1) else 0,  # is_prime
    ]

print("Computing conductor factorization features...")
fact_features = np.array([factorization_features(d["conductor"]) for d in real_data])

# Fit class_size ~ factorization features
reg_fact = LinearRegression()
reg_fact.fit(np.column_stack([real_log_N, fact_features]), real_class_sizes)
pred_cs_fact = reg_fact.predict(np.column_stack([real_log_N, fact_features]))
resid_cs_fact = real_class_sizes - pred_cs_fact

r2_fact = 1 - np.sum(resid_cs_fact**2) / np.sum((real_class_sizes - np.mean(real_class_sizes))**2)
print(f"Factorization model R^2 for class_size: {r2_fact:.4f}")

false_positives_3 = []
for trial in range(n_trials):
    synth_cs = pred_cs_fact + np.random.permutation(resid_cs_fact)
    synth_cs = np.clip(np.round(synth_cs), 1, None).astype(int)

    bins = np.percentile(real_log_N, np.linspace(0, 100, 51))
    bin_rhos = []
    for b in range(50):
        mask = (real_log_N >= bins[b]) & (real_log_N < bins[b + 1])
        if mask.sum() < 30:
            continue
        r, _ = spearmanr(real_spacings[mask], synth_cs[mask])
        if not np.isnan(r):
            bin_rhos.append(r)
    false_positives_3.append(np.mean(bin_rhos) if bin_rhos else 0.0)

synth3_mean = np.mean(false_positives_3)
synth3_std = np.std(false_positives_3)
print(f"Synthetic 3 mean rho: {synth3_mean:.6f} +/- {synth3_std:.6f}")
print(f"False positive rate (|rho| > 0.05): {np.mean(np.abs(false_positives_3) > 0.05)*100:.1f}%")

# ---- SYNTHETIC MODEL 4: REAL class_size, GUE-reshuffled zeros ----
print("\n" + "-" * 40)
print("SYNTHETIC 4: Real class_size + GUE-resampled spacing")
print("(keeps all arithmetic, replaces spectral with pure RMT)")
print("-" * 40)

false_positives_4 = []
for trial in range(n_trials):
    # Replace spacing with GUE Wigner surmise, scaled per conductor bin
    synth_spacings = np.zeros_like(real_spacings)
    bins = np.percentile(real_log_N, np.linspace(0, 100, 21))
    for b in range(20):
        mask = (real_log_N >= bins[b]) & (real_log_N < bins[b + 1])
        idx = np.where(mask)[0]
        if len(idx) == 0:
            continue
        # Generate GUE spacings scaled to match this bin's mean spacing
        bin_mean = np.mean(real_spacings[idx])
        gue = sample_wigner_surmise(len(idx))
        gue = gue * (bin_mean / np.mean(gue))
        synth_spacings[idx] = gue

    bins50 = np.percentile(real_log_N, np.linspace(0, 100, 51))
    bin_rhos = []
    for b in range(50):
        mask = (real_log_N >= bins50[b]) & (real_log_N < bins50[b + 1])
        if mask.sum() < 30:
            continue
        r, _ = spearmanr(synth_spacings[mask], real_class_sizes[mask])
        if not np.isnan(r):
            bin_rhos.append(r)
    false_positives_4.append(np.mean(bin_rhos) if bin_rhos else 0.0)

synth4_mean = np.mean(false_positives_4)
synth4_std = np.std(false_positives_4)
print(f"Synthetic 4 mean rho: {synth4_mean:.6f} +/- {synth4_std:.6f}")
print(f"False positive rate (|rho| > 0.05): {np.mean(np.abs(false_positives_4) > 0.05)*100:.1f}%")

# ---- SUMMARY ----
print("\n" + "=" * 60)
print("SYNTHETIC NULL TEST SUMMARY")
print("=" * 60)
print(f"Real signal (within-bin rho): -0.1628")
print()
print(f"Synth 1 (GUE zeros + random class_size):     mean={synth1_mean:+.6f}, std={synth1_std:.6f}, FPR={np.mean(np.abs(false_positives_1)>0.05)*100:.1f}%")
print(f"Synth 2 (real zeros + conductor-pred CS):     mean={synth2_mean:+.6f}, std={synth2_std:.6f}, FPR={np.mean(np.abs(false_positives_2)>0.05)*100:.1f}%")
print(f"Synth 3 (real zeros + factorization-pred CS): mean={synth3_mean:+.6f}, std={synth3_std:.6f}, FPR={np.mean(np.abs(false_positives_3)>0.05)*100:.1f}%")
print(f"Synth 4 (GUE spacing + real class_size):      mean={synth4_mean:+.6f}, std={synth4_std:.6f}, FPR={np.mean(np.abs(false_positives_4)>0.05)*100:.1f}%")
print()

all_fps = [
    np.mean(np.abs(false_positives_1) > 0.05),
    np.mean(np.abs(false_positives_2) > 0.05),
    np.mean(np.abs(false_positives_3) > 0.05),
    np.mean(np.abs(false_positives_4) > 0.05),
]

if max(all_fps) < 0.05:
    overall = "PIPELINE VALIDATED - no false positives from synthetic data"
elif max(all_fps) < 0.20:
    overall = "MARGINAL - some false positive leakage, investigate"
else:
    overall = "PIPELINE COMPROMISED - significant false positive rate"

print(f"VERDICT: {overall}")

results = {
    "real_signal_rho": -0.1628,
    "n_trials": n_trials,
    "n_curves": n_real,
    "synthetic_1_gue_random_cs": {
        "description": "GUE Wigner spacing + randomly permuted class_size",
        "mean_rho": float(synth1_mean),
        "std_rho": float(synth1_std),
        "false_positive_rate": float(np.mean(np.abs(false_positives_1) > 0.05)),
    },
    "synthetic_2_real_zeros_conductor_cs": {
        "description": "Real zeros + class_size predicted from conductor",
        "mean_rho": float(synth2_mean),
        "std_rho": float(synth2_std),
        "false_positive_rate": float(np.mean(np.abs(false_positives_2) > 0.05)),
    },
    "synthetic_3_real_zeros_factorization_cs": {
        "description": "Real zeros + class_size predicted from conductor factorization",
        "r2_factorization_model": float(r2_fact),
        "mean_rho": float(synth3_mean),
        "std_rho": float(synth3_std),
        "false_positive_rate": float(np.mean(np.abs(false_positives_3) > 0.05)),
    },
    "synthetic_4_gue_spacing_real_cs": {
        "description": "GUE-resampled spacing (per conductor bin) + real class_size",
        "mean_rho": float(synth4_mean),
        "std_rho": float(synth4_std),
        "false_positive_rate": float(np.mean(np.abs(false_positives_4) > 0.05)),
    },
    "verdict": overall,
}

out = Path("harmonia/results/synthetic_null_test.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out}")
