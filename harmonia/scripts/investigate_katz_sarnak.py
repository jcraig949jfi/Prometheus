"""
Katz-Sarnak Anomaly Investigation

SO(even) curves have LOWER scaled gamma_1 than SO(odd) — reversed.
Hypothesis: zeros stored as 0.0 are central zeros of rank-1 curves,
which shifts the SO(odd) distribution up.

Also: check if unfolding is correct.
"""
import numpy as np
import duckdb
import json
from pathlib import Path

print("KATZ-SARNAK ANOMALY INVESTIGATION")
print("=" * 60)
print("Why is SO(even) gamma_1 LOWER than SO(odd)?")
print()

db = duckdb.connect(str(Path("charon/data/charon.duckdb")), read_only=True)
rows = db.sql("""
    SELECT ec.rank, ec.conductor, ec.analytic_rank,
           oz.root_number, oz.zeros_vector, oz.analytic_rank as oz_ar
    FROM object_zeros oz
    JOIN elliptic_curves ec ON oz.object_id = ec.object_id
    WHERE oz.zeros_vector IS NOT NULL AND oz.n_zeros_stored >= 3
          AND oz.root_number IS NOT NULL
          AND ec.conductor IS NOT NULL AND ec.conductor > 10
""").fetchall()
db.close()

print(f"Total curves: {len(rows):,}")

# ---- Understand the zero storage format ----
print("\nSTEP 1: Understanding zero storage")
print("-" * 40)

n_with_zero = 0
n_with_neg = 0
n_rank0_rn_plus = 0
n_rank0_rn_minus = 0
n_rank1_rn_plus = 0
n_rank1_rn_minus = 0

for rank, cond, ar, rn, zvec, oz_ar in rows:
    zeros = list(zvec or [])
    has_zero = any(z is not None and abs(z) < 1e-10 for z in zeros)
    has_neg = any(z is not None and z < -1e-10 for z in zeros)
    if has_zero:
        n_with_zero += 1
    if has_neg:
        n_with_neg += 1

    r = int(rank or 0)
    rn_val = float(rn) if rn is not None else 0
    if r == 0 and rn_val > 0:
        n_rank0_rn_plus += 1
    elif r == 0 and rn_val < 0:
        n_rank0_rn_minus += 1
    elif r == 1 and rn_val > 0:
        n_rank1_rn_plus += 1
    elif r == 1 and rn_val < 0:
        n_rank1_rn_minus += 1

print(f"Curves with zero at 0.0: {n_with_zero:,}")
print(f"Curves with negative zeros: {n_with_neg:,}")
print(f"rank=0, rn=+1 (SO(even)): {n_rank0_rn_plus:,}")
print(f"rank=0, rn=-1 (should NOT exist by parity): {n_rank0_rn_minus:,}")
print(f"rank=1, rn=+1 (should NOT exist by parity): {n_rank1_rn_plus:,}")
print(f"rank=1, rn=-1 (SO(odd)): {n_rank1_rn_minus:,}")

# Check: are zeros stored symmetrically? (both +gamma and -gamma)
print("\nSample zero vectors:")
for i, (rank, cond, ar, rn, zvec, oz_ar) in enumerate(rows[:5]):
    zeros = [z for z in (zvec or []) if z is not None]
    print(f"  rank={rank}, rn={rn:.0f}, zeros={[f'{z:.4f}' for z in zeros[:6]]}")

# ---- STEP 2: Correct the analysis ----
print("\nSTEP 2: Corrected Katz-Sarnak analysis")
print("-" * 40)
print("Use ONLY positive zeros, skip the zero at origin for rank >= 1")

# For rank-0 (SO(even)): first positive zero IS gamma_1
# For rank-1 (SO(odd)): zero at s=1/2 is stored, first POSITIVE nonzero is gamma_1
# For rank-2: two zeros at origin, etc.

gamma1_even = []  # rank-0, rn=+1
gamma1_odd = []   # rank-1, rn=-1
gamma1_even_cond = []
gamma1_odd_cond = []

for rank, cond, ar, rn, zvec, oz_ar in rows:
    r = int(rank or 0)
    rn_val = float(rn) if rn is not None else 0
    c = float(cond)

    # Get positive nonzero zeros
    zeros = sorted([z for z in (zvec or []) if z is not None and z > 1e-6])
    if not zeros:
        continue

    g1 = zeros[0]
    # Scale by log(conductor) for Katz-Sarnak comparison
    # Proper scaling: theta = gamma * log(N*sqrt(q)) / (2*pi) for weight-2
    # Simplified: gamma * log(N) / (2*pi)
    scaled_g1 = g1 * np.log(c) / (2 * np.pi)

    if r == 0 and rn_val > 0:
        gamma1_even.append(scaled_g1)
        gamma1_even_cond.append(c)
    elif r == 1 and rn_val < 0:
        gamma1_odd.append(scaled_g1)
        gamma1_odd_cond.append(c)

g1e = np.array(gamma1_even)
g1o = np.array(gamma1_odd)

print(f"SO(even) (rank=0, rn=+1): {len(g1e):,} curves")
print(f"SO(odd) (rank=1, rn=-1):  {len(g1o):,} curves")
print(f"\nScaled gamma_1 (corrected):")
print(f"  SO(even): mean={np.mean(g1e):.4f}, median={np.median(g1e):.4f}, std={np.std(g1e):.4f}")
print(f"  SO(odd):  mean={np.mean(g1o):.4f}, median={np.median(g1o):.4f}, std={np.std(g1o):.4f}")

# Katz-Sarnak prediction: SO(even) should have density VANISHING at 0
# (zeros repelled from origin), while SO(odd) has density DIVERGING at 0
# (zero attracted to origin after the forced one).
# So the first nontrivial zero for SO(even) should be HIGHER than SO(odd).

if np.mean(g1e) > np.mean(g1o):
    ks_verdict = "CONSISTENT: SO(even) first zero HIGHER (repelled from origin)"
else:
    ks_verdict = "STILL REVERSED: investigating further"

print(f"\n{ks_verdict}")

# ---- STEP 3: Distribution comparison ----
print("\nSTEP 3: Distribution of scaled gamma_1")
print("-" * 40)

bins_hist = np.linspace(0, 2.0, 41)
hist_even, _ = np.histogram(g1e, bins=bins_hist, density=True)
hist_odd, _ = np.histogram(g1o, bins=bins_hist, density=True)

print(f"{'bin center':>10} {'SO(even)':>10} {'SO(odd)':>10}")
for i in range(min(20, len(hist_even))):
    center = (bins_hist[i] + bins_hist[i + 1]) / 2
    print(f"{center:10.3f} {hist_even[i]:10.4f} {hist_odd[i]:10.4f}")

# Low-lying zero density near 0
frac_even_low = np.mean(g1e < 0.2)
frac_odd_low = np.mean(g1o < 0.2)
print(f"\nFraction with scaled gamma_1 < 0.2:")
print(f"  SO(even): {frac_even_low*100:.1f}%")
print(f"  SO(odd):  {frac_odd_low*100:.1f}%")
print(f"  KS predicts: SO(even) should have FEWER low-lying zeros")

# ---- STEP 4: Conductor dependence ----
print("\nSTEP 4: Does the anomaly depend on conductor?")
print("-" * 40)

g1e_c = np.array(gamma1_even_cond)
g1o_c = np.array(gamma1_odd_cond)

cond_edges = np.logspace(np.log10(11), np.log10(max(g1e_c.max(), g1o_c.max())), 8)
print(f"{'Conductor':>12} {'even mean':>10} {'odd mean':>10} {'even > odd?':>12}")
for i in range(len(cond_edges) - 1):
    mask_e = (g1e_c >= cond_edges[i]) & (g1e_c < cond_edges[i + 1])
    mask_o = (g1o_c >= cond_edges[i]) & (g1o_c < cond_edges[i + 1])
    if mask_e.sum() < 50 or mask_o.sum() < 50:
        continue
    me = np.mean(g1e[mask_e])
    mo = np.mean(g1o[mask_o])
    center = np.sqrt(cond_edges[i] * cond_edges[i + 1])
    print(f"{center:12.0f} {me:10.4f} {mo:10.4f} {'YES' if me > mo else 'NO':>12}")

# ---- STEP 5: Raw (unscaled) comparison ----
print("\nSTEP 5: Unscaled gamma_1")
print("-" * 40)

raw_even = []
raw_odd = []
for rank, cond, ar, rn, zvec, oz_ar in rows:
    r = int(rank or 0)
    rn_val = float(rn) if rn is not None else 0
    zeros = sorted([z for z in (zvec or []) if z is not None and z > 1e-6])
    if not zeros:
        continue
    if r == 0 and rn_val > 0:
        raw_even.append(zeros[0])
    elif r == 1 and rn_val < 0:
        raw_odd.append(zeros[0])

print(f"Unscaled gamma_1:")
print(f"  SO(even): mean={np.mean(raw_even):.6f}")
print(f"  SO(odd):  mean={np.mean(raw_odd):.6f}")
print(f"  Even > Odd? {'YES' if np.mean(raw_even) < np.mean(raw_odd) else 'NO'}")
print(f"  (Note: for EC L-functions, lower conductor -> higher gamma_1)")
print(f"  SO(even) mean conductor: {np.mean(gamma1_even_cond):.0f}")
print(f"  SO(odd) mean conductor:  {np.mean(gamma1_odd_cond):.0f}")

results = {
    "n_even": len(g1e),
    "n_odd": len(g1o),
    "corrected_scaled_g1_even_mean": float(np.mean(g1e)),
    "corrected_scaled_g1_odd_mean": float(np.mean(g1o)),
    "raw_g1_even_mean": float(np.mean(raw_even)),
    "raw_g1_odd_mean": float(np.mean(raw_odd)),
    "even_mean_conductor": float(np.mean(gamma1_even_cond)),
    "odd_mean_conductor": float(np.mean(gamma1_odd_cond)),
    "parity_violations": {
        "rank0_rn_minus": n_rank0_rn_minus,
        "rank1_rn_plus": n_rank1_rn_plus,
    },
    "verdict": ks_verdict,
}

out = Path("harmonia/results/katz_sarnak_investigation.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out}")
