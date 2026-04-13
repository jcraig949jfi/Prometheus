"""
Higher-Order Spacing Test

If the isogeny signal only impacts gamma_2 - gamma_1 (first gap), it may be
tied to BSD (lowest zeros closest to s=1/2).
If it propagates up the spectrum (gamma_3 - gamma_2, gamma_4 - gamma_3, ...),
it's a global geometric property of the L-function.

RMT predicts rigid spacing rules. Which gaps carry the isogeny information?
"""
import numpy as np
import duckdb
import json
from pathlib import Path
from scipy.stats import spearmanr
from sklearn.linear_model import LinearRegression

print("HIGHER-ORDER SPACING TEST")
print("=" * 60)
print("Which zero gaps carry isogeny class information?")
print()

db = duckdb.connect(str(Path("charon/data/charon.duckdb")), read_only=True)
rows = db.sql("""
    SELECT ec.conductor, ec.class_size, ec.rank,
           oz.zeros_vector, oz.n_zeros_stored
    FROM object_zeros oz
    JOIN elliptic_curves ec ON oz.object_id = ec.object_id
    WHERE oz.n_zeros_stored >= 8 AND oz.zeros_vector IS NOT NULL
          AND ec.conductor IS NOT NULL AND ec.conductor <= 50000
          AND ec.class_size IS NOT NULL
""").fetchall()
db.close()

data = []
for cond, cs, rank, zvec, nz in rows:
    zeros = sorted([z for z in (zvec or []) if z is not None and z > 0])
    if len(zeros) < 6:
        continue
    data.append({
        "conductor": int(cond),
        "class_size": int(cs),
        "rank": int(rank or 0),
        "zeros": zeros,
    })

print(f"Curves with 6+ positive zeros: {len(data)}")

conductors = np.array([d["conductor"] for d in data])
class_sizes = np.array([d["class_size"] for d in data])
ranks = np.array([d["rank"] for d in data])
log_N = np.log10(np.clip(conductors, 2, None))

# Compute gaps
max_gaps = 5  # gamma_2-gamma_1 through gamma_6-gamma_5
gap_names = []
gap_arrays = []

for g in range(max_gaps):
    name = f"gap_{g+1}_{g+2}"
    vals = np.array([d["zeros"][g+1] - d["zeros"][g] if len(d["zeros"]) > g+1 else np.nan
                     for d in data])
    gap_names.append(name)
    gap_arrays.append(vals)

# Also compute normalized gaps (gap / mean_gap for that curve)
mean_gaps = np.array([np.mean(np.diff(d["zeros"][:6])) for d in data])

print("\n--- Raw gap correlations with class_size ---")
print(f"{'Gap':>12} {'rho':>8} {'p':>12} {'|rho|':>8}")
print("-" * 44)

gap_results = {}
for name, vals in zip(gap_names, gap_arrays):
    valid = ~np.isnan(vals)
    if valid.sum() < 500:
        continue
    rho, p = spearmanr(vals[valid], class_sizes[valid])
    print(f"{name:>12} {rho:8.4f} {p:12.2e} {abs(rho):8.4f}")
    gap_results[name] = {"raw_rho": float(rho), "raw_p": float(p)}

# Conductor-controlled (within-bin)
print("\n--- Conductor-controlled gap correlations ---")
print(f"{'Gap':>12} {'within-bin rho':>16} {'z-score':>10}")
print("-" * 42)

bins = np.percentile(log_N, np.linspace(0, 100, 51))

for name, vals in zip(gap_names, gap_arrays):
    valid = ~np.isnan(vals)
    if valid.sum() < 500:
        continue

    # Observed within-bin
    obs_rhos = []
    for b in range(50):
        mask = valid & (log_N >= bins[b]) & (log_N < bins[b + 1])
        if mask.sum() < 20:
            continue
        r, _ = spearmanr(vals[mask], class_sizes[mask])
        if not np.isnan(r):
            obs_rhos.append(r)
    obs_mean = np.mean(obs_rhos) if obs_rhos else 0.0

    # Null
    null_means = []
    for trial in range(200):
        shuffled = class_sizes.copy()
        for b in range(50):
            mask = valid & (log_N >= bins[b]) & (log_N < bins[b + 1])
            idx = np.where(mask)[0]
            if len(idx) > 1:
                shuffled[idx] = np.random.permutation(shuffled[idx])
        trial_rhos = []
        for b in range(50):
            mask = valid & (log_N >= bins[b]) & (log_N < bins[b + 1])
            if mask.sum() < 20:
                continue
            r, _ = spearmanr(vals[mask], shuffled[mask])
            if not np.isnan(r):
                trial_rhos.append(r)
        null_means.append(np.mean(trial_rhos) if trial_rhos else 0.0)

    null_m = np.mean(null_means)
    null_s = np.std(null_means)
    z = (obs_mean - null_m) / max(null_s, 1e-10)
    print(f"{name:>12} {obs_mean:16.4f} {z:10.2f}")
    gap_results[name]["within_bin_rho"] = float(obs_mean)
    gap_results[name]["z_score"] = float(z)

# Regression conditioning: does gap_1 explain away higher gaps?
print("\n--- After conditioning on gap_1_2 ---")
print("Does class_size still correlate with higher gaps after removing gap_1?")

gap1 = gap_arrays[0]
valid_all = ~np.isnan(gap1)

# Regress out conductor + rank + gap_1 from each higher gap
X_base = np.column_stack([log_N, ranks, gap1])

for name, vals in zip(gap_names[1:], gap_arrays[1:]):
    valid = valid_all & ~np.isnan(vals)
    if valid.sum() < 500:
        continue

    # Regress gap_k ~ conductor + rank + gap_1
    reg = LinearRegression().fit(X_base[valid], vals[valid])
    resid_gap = vals[valid] - reg.predict(X_base[valid])

    # Also regress class_size ~ conductor + rank + gap_1
    reg_cs = LinearRegression().fit(X_base[valid], class_sizes[valid])
    resid_cs = class_sizes[valid] - reg_cs.predict(X_base[valid])

    rho, p = spearmanr(resid_gap, resid_cs)
    print(f"  {name} residual: rho={rho:.4f}, p={p:.2e}")
    gap_results[name]["residual_after_gap1_rho"] = float(rho)
    gap_results[name]["residual_after_gap1_p"] = float(p)

# Interpretation
print("\n" + "=" * 60)
print("INTERPRETATION")
print("=" * 60)

g1_z = abs(gap_results.get("gap_1_2", {}).get("z_score", 0))
g2_z = abs(gap_results.get("gap_2_3", {}).get("z_score", 0))
g3_z = abs(gap_results.get("gap_3_4", {}).get("z_score", 0))

if g2_z > 3 and g3_z > 3:
    interpretation = "GLOBAL — signal propagates across multiple gaps"
    detail = "Not BSD-specific. The isogeny structure affects the entire zero spectrum."
elif g1_z > 3 and g2_z < 3:
    interpretation = "BSD-LOCALIZED — signal concentrated in first gap only"
    detail = "Consistent with BSD: isogeny structure affects zeros near s=1/2."
else:
    interpretation = "AMBIGUOUS — needs more data"
    detail = f"gap_1 z={g1_z:.1f}, gap_2 z={g2_z:.1f}, gap_3 z={g3_z:.1f}"

print(f"  {interpretation}")
print(f"  {detail}")

results = {
    "n_curves": len(data),
    "min_zeros_required": 6,
    "gaps": gap_results,
    "interpretation": interpretation,
    "detail": detail,
}

out = Path("harmonia/results/higher_order_spacing.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out}")
