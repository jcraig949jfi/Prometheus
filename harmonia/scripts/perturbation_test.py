"""
Perturbation Test — How fragile is Signal A?

Add Gaussian noise to zeros at increasing scales.
Real structure degrades smoothly. Artifacts collapse.
"""
import numpy as np
import duckdb
import json
from pathlib import Path
from scipy.stats import spearmanr

print("PERTURBATION TEST")
print("=" * 60)
print("Does the signal degrade smoothly under noise?")
print()

db = duckdb.connect(str(Path("charon/data/charon.duckdb")), read_only=True)
rows = db.sql("""
    SELECT ec.conductor, ec.class_size, oz.zeros_vector
    FROM object_zeros oz
    JOIN elliptic_curves ec ON oz.object_id = ec.object_id
    WHERE oz.n_zeros_stored >= 5 AND oz.zeros_vector IS NOT NULL
          AND ec.conductor IS NOT NULL AND ec.conductor <= 50000
          AND ec.class_size IS NOT NULL
""").fetchall()
db.close()

data = []
for cond, cs, zvec in rows:
    zeros = sorted([z for z in (zvec or []) if z is not None and z > 0])
    if len(zeros) < 3:
        continue
    data.append({
        "conductor": int(cond),
        "class_size": int(cs),
        "zeros": np.array(zeros[:6]),
    })

n = len(data)
print(f"Curves: {n}")

conductors = np.array([d["conductor"] for d in data])
class_sizes = np.array([d["class_size"] for d in data])
log_N = np.log10(np.clip(conductors, 2, None))

# Compute clean spacing
clean_spacings = np.array([d["zeros"][1] - d["zeros"][0] for d in data])
mean_spacing = np.mean(clean_spacings)
print(f"Mean spacing: {mean_spacing:.6f}")

# Clean signal baseline (within-bin rho with 50 bins)
def compute_signal(spacings, class_sizes, log_N, n_bins=50):
    bins = np.percentile(log_N, np.linspace(0, 100, n_bins + 1))
    rhos = []
    for b in range(n_bins):
        mask = (log_N >= bins[b]) & (log_N < bins[b + 1])
        if mask.sum() < 30:
            continue
        r, _ = spearmanr(spacings[mask], class_sizes[mask])
        if not np.isnan(r):
            rhos.append(r)
    return np.mean(rhos) if rhos else 0.0

clean_rho = compute_signal(clean_spacings, class_sizes, log_N)
print(f"Clean signal (within-bin rho): {clean_rho:.4f}")

# Noise levels as fraction of mean spacing
noise_fractions = [0.0, 0.001, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1.0]
n_trials = 50

print(f"\n{'Noise %':>10} {'Mean rho':>10} {'Std rho':>10} {'Retention':>10}")
print("-" * 44)

results = {}
for frac in noise_fractions:
    sigma = frac * mean_spacing
    trial_rhos = []

    for _ in range(n_trials):
        # Add noise to ALL zeros, then recompute spacing
        noisy_spacings = np.zeros(n)
        for i, d in enumerate(data):
            noisy_zeros = d["zeros"] + np.random.normal(0, max(sigma, 1e-15), len(d["zeros"]))
            noisy_zeros = np.sort(np.abs(noisy_zeros))  # keep positive, sorted
            if len(noisy_zeros) >= 2:
                noisy_spacings[i] = noisy_zeros[1] - noisy_zeros[0]
            else:
                noisy_spacings[i] = clean_spacings[i]

        rho = compute_signal(noisy_spacings, class_sizes, log_N)
        trial_rhos.append(rho)

    mean_rho = np.mean(trial_rhos)
    std_rho = np.std(trial_rhos)
    retention = mean_rho / clean_rho if clean_rho != 0 else 0
    print(f"{frac*100:10.1f} {mean_rho:10.4f} {std_rho:10.4f} {retention*100:9.1f}%")

    results[f"noise_{frac*100:.1f}pct"] = {
        "noise_fraction": float(frac),
        "sigma": float(sigma),
        "mean_rho": float(mean_rho),
        "std_rho": float(std_rho),
        "retention_pct": float(retention * 100),
    }

# Interpretation
retentions = [v["retention_pct"] for v in results.values()]
noise_levels = [v["noise_fraction"] * 100 for v in results.values()]

# Check 5% noise retention
ret_5pct = results.get("noise_5.0pct", {}).get("retention_pct", 0)
ret_10pct = results.get("noise_10.0pct", {}).get("retention_pct", 0)

print("\n" + "=" * 60)
if ret_5pct > 70:
    verdict = "ROBUST - signal degrades smoothly (>70% retained at 5% noise)"
elif ret_5pct > 40:
    verdict = "MODERATE - signal degrades but persists at 5% noise"
elif ret_5pct > 10:
    verdict = "FRAGILE - significant signal loss at 5% noise"
else:
    verdict = "COLLAPSED - signal destroyed by small perturbation"

print(f"VERDICT: {verdict}")
print(f"  5% noise retention: {ret_5pct:.1f}%")
print(f"  10% noise retention: {ret_10pct:.1f}%")

results["verdict"] = verdict
results["clean_rho"] = float(clean_rho)
results["mean_spacing"] = float(mean_spacing)
results["n_curves"] = n
results["n_trials"] = n_trials

out = Path("harmonia/results/perturbation_test.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out}")
