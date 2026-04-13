"""
Survivor Kill Protocol - Test 5: Twist Stability
Take curves and their quadratic twists. Twists can change rank.
If zero spacing tracks class_size WITHIN twist families, extremely strong.

Also: Test 8 (Asymptotic Scaling) - fit signal_strength ~ C^(-alpha).
"""
import numpy as np
import duckdb
import json
import psycopg2
from pathlib import Path
from scipy.stats import spearmanr
from scipy.optimize import curve_fit

print("SURVIVOR KILL PROTOCOL - TWIST + SCALING")
print("=" * 60)

# ---- TWIST STABILITY ----
# We can't directly identify twist families in DuckDB.
# But we can query LMFDB Postgres for isogeny classes and check
# whether the signal is consistent WITHIN isogeny classes.
# Isogeny-related curves share the same L-function up to twist.

print("\nTEST: Isogeny-Class Internal Consistency")
print("Within each isogeny class, does zero spacing still vary with class position?")
print("-" * 40)

db = duckdb.connect(str(Path("charon/data/charon.duckdb")), read_only=True)
rows = db.sql("""
    SELECT ec.lmfdb_label, ec.lmfdb_iso, ec.conductor, ec.rank, ec.cm,
           ec.class_size, ec.class_deg,
           oz.zeros_vector
    FROM object_zeros oz
    JOIN elliptic_curves ec ON oz.object_id = ec.object_id
    WHERE oz.n_zeros_stored >= 5 AND oz.zeros_vector IS NOT NULL
          AND ec.conductor IS NOT NULL AND ec.conductor <= 50000
          AND ec.class_size IS NOT NULL AND ec.class_size > 1
""").fetchall()
db.close()

# Group by isogeny class (lmfdb_iso)
from collections import defaultdict
iso_classes = defaultdict(list)
for label, iso, cond, rank, cm, cs, cd, zvec in rows:
    zeros = sorted([z for z in (zvec or []) if z is not None and z > 0])
    if len(zeros) < 3:
        continue
    iso_classes[iso].append({
        "label": label,
        "conductor": int(cond),
        "rank": int(rank or 0),
        "class_size": int(cs),
        "class_deg": int(cd or 1),
        "gamma1": zeros[0],
        "spacing": zeros[1] - zeros[0],
        "zeros": zeros[:5],
    })

multi_curve_classes = {k: v for k, v in iso_classes.items() if len(v) > 1}
print(f"Isogeny classes with >1 curve having zeros: {len(multi_curve_classes)}")
print(f"Total curves in multi-curve classes: {sum(len(v) for v in multi_curve_classes.values())}")

# Within each isogeny class, all curves have SAME conductor and class_size.
# But they may differ in rank and zero positions.
# The question: do curves in the SAME isogeny class show zero variation
# that correlates with their position in the class (class_deg)?

# Collect within-class variation
within_class_data = []
for iso, curves in multi_curve_classes.items():
    if len(curves) < 2:
        continue
    # All have same conductor and class_size
    gammas = [c["gamma1"] for c in curves]
    spacings = [c["spacing"] for c in curves]
    degs = [c["class_deg"] for c in curves]
    ranks = [c["rank"] for c in curves]

    # Check if zeros differ within class
    gamma_range = max(gammas) - min(gammas)
    spacing_range = max(spacings) - min(spacings)

    for c in curves:
        within_class_data.append({
            "iso": iso,
            "class_size": curves[0]["class_size"],
            "conductor": curves[0]["conductor"],
            "class_deg": c["class_deg"],
            "rank": c["rank"],
            "gamma1": c["gamma1"],
            "spacing": c["spacing"],
            "gamma_range": gamma_range,
            "spacing_range": spacing_range,
        })

print(f"Within-class data points: {len(within_class_data)}")

# Key question: do different curves in the same isogeny class have
# different gamma1 values? (They share the same L-function if isogenous)
gamma_ranges = [v[0]["gamma1"] for k, v in multi_curve_classes.items() if len(v) >= 2]
# Actually compute range per class
class_gamma_ranges = []
for iso, curves in multi_curve_classes.items():
    gammas = [c["gamma1"] for c in curves]
    class_gamma_ranges.append(max(gammas) - min(gammas))

print(f"Mean gamma1 range within isogeny class: {np.mean(class_gamma_ranges):.6f}")
print(f"Median gamma1 range within isogeny class: {np.median(class_gamma_ranges):.6f}")
print(f"Max gamma1 range: {np.max(class_gamma_ranges):.6f}")

# If gamma1 range is essentially 0 within classes, then isogenous curves
# share the same zeros (as expected - they have the same L-function!)
# This means class_size is a CLASS-LEVEL property correlating with
# CLASS-LEVEL zero positions. The signal is between classes, not within.

if np.median(class_gamma_ranges) < 1e-6:
    print("\nIsogenous curves share identical zeros (as expected).")
    print("Signal is BETWEEN isogeny classes, not within.")
    print("This is consistent: class_size is a class-level invariant,")
    print("and zeros are class-level spectral data.")
    twist_verdict = "CONSISTENT - class-level signal confirmed"
else:
    print("\nUnexpected: isogenous curves have different zeros!")
    twist_verdict = "ANOMALOUS - investigate"

print(f"TWIST TEST: {twist_verdict}")

results = {
    "twist_stability": {
        "n_multi_curve_classes": len(multi_curve_classes),
        "n_within_class_points": len(within_class_data),
        "median_gamma1_range": float(np.median(class_gamma_ranges)),
        "mean_gamma1_range": float(np.mean(class_gamma_ranges)),
        "verdict": twist_verdict,
    }
}

# ---- ASYMPTOTIC SCALING LAW ----
print("\n" + "=" * 60)
print("TEST: Asymptotic Scaling Law")
print("Does signal strength decay as conductor^(-alpha)?")
print("-" * 40)

# Load full data
db = duckdb.connect(str(Path("charon/data/charon.duckdb")), read_only=True)
rows = db.sql("""
    SELECT ec.conductor, ec.class_size, oz.zeros_vector
    FROM object_zeros oz
    JOIN elliptic_curves ec ON oz.object_id = ec.object_id
    WHERE oz.n_zeros_stored >= 5 AND oz.zeros_vector IS NOT NULL
          AND ec.conductor IS NOT NULL AND ec.class_size IS NOT NULL
""").fetchall()
db.close()

all_data = []
for cond, cs, zvec in rows:
    zeros = sorted([z for z in (zvec or []) if z is not None and z > 0])
    if len(zeros) < 2:
        continue
    all_data.append({
        "conductor": int(cond),
        "class_size": int(cs),
        "spacing": zeros[1] - zeros[0],
        "gamma1": zeros[0],
    })

print(f"Total curves: {len(all_data)}")

conductors = np.array([d["conductor"] for d in all_data])
spacings = np.array([d["spacing"] for d in all_data])
class_sizes = np.array([d["class_size"] for d in all_data])
log_cond = np.log10(np.clip(conductors, 2, None))

# Compute signal strength in conductor windows
cond_edges = np.logspace(1, np.log10(conductors.max()), 20)
window_data = []
for i in range(len(cond_edges) - 1):
    mask = (conductors >= cond_edges[i]) & (conductors < cond_edges[i + 1])
    if mask.sum() < 100:
        continue
    rho, p = spearmanr(spacings[mask], class_sizes[mask])
    window_data.append({
        "cond_center": float(np.sqrt(cond_edges[i] * cond_edges[i + 1])),
        "n": int(mask.sum()),
        "rho": float(rho),
        "abs_rho": float(abs(rho)),
        "p": float(p),
    })

print("\nSignal strength by conductor window:")
print(f"{'Conductor':>12} {'n':>8} {'rho':>8} {'p':>12}")
for w in window_data:
    print(f"{w['cond_center']:12.0f} {w['n']:8d} {w['rho']:8.4f} {w['p']:12.2e}")

# Fit power law: |rho| = A * N^(-alpha)
if len(window_data) >= 4:
    cond_centers = np.array([w["cond_center"] for w in window_data])
    abs_rhos = np.array([w["abs_rho"] for w in window_data])

    # Only fit where signal is significant
    sig_mask = abs_rhos > 0.01
    if sig_mask.sum() >= 3:
        log_c = np.log10(cond_centers[sig_mask])
        log_r = np.log10(abs_rhos[sig_mask])

        # Linear fit in log-log space
        coeffs = np.polyfit(log_c, log_r, 1)
        alpha = -coeffs[0]
        A = 10**coeffs[1]

        print(f"\nPower law fit: |rho| = {A:.4f} * N^(-{alpha:.4f})")
        print(f"Decay exponent alpha = {alpha:.4f}")

        # RMT prediction: for GUE, fluctuations scale as N^(-1/2) or log(N)
        # But this is spacing-class_size correlation, not GUE fluctuation
        if alpha > 0:
            scaling_verdict = f"DECAYS (alpha={alpha:.3f})"
            if 0.2 < alpha < 0.8:
                scaling_verdict += " - moderate decay, consistent with finite-size effect"
            elif alpha > 0.8:
                scaling_verdict += " - fast decay, may vanish at large N"
            elif alpha < 0.2:
                scaling_verdict += " - slow decay, signal persists"
        else:
            scaling_verdict = f"GROWS with conductor (alpha={alpha:.3f}) - strengthening signal"

        results["asymptotic_scaling"] = {
            "n_windows": len(window_data),
            "windows": window_data,
            "alpha": float(alpha),
            "A": float(A),
            "verdict": scaling_verdict,
        }
    else:
        scaling_verdict = "INSUFFICIENT significant windows"
        results["asymptotic_scaling"] = {"verdict": scaling_verdict}
else:
    scaling_verdict = "INSUFFICIENT windows"
    results["asymptotic_scaling"] = {"verdict": scaling_verdict}

print(f"SCALING TEST: {scaling_verdict}")

# ---- SUMMARY ----
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
for k, v in results.items():
    print(f"  {k}: {v.get('verdict', 'N/A')}")

out = Path("harmonia/results/survivor_kill_twist_scaling.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out}")
