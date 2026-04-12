"""C43-ext/R2: Prime gap scaling extended to 10^9.
Extends C43 from Round 1 (10^8) to 10^9 (~50M primes).
Computes M4/M2, M6/M2^3, M8/M2^4 at each decade 10^3..10^9.
Linear fit of M4/M2 vs log10(N) -- confirm or update the 0.43/decade slope.
Battery v2 (F24/F24b/F25/F27). Machine: M1 (Skullport), 2026-04-12
"""
import sys, json, time
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from battery_v2 import BatteryV2

DATA = Path(__file__).resolve().parent.parent.parent
bv2 = BatteryV2()

from sympy import primerange
from scipy import stats as sp_stats

print("Prime gap M4/M2 scaling -- extended to 10^9")
print("WARNING: 10^9 generates ~50M primes, needs ~1GB RAM")
print("="*70)

results_by_scale = {}

for exp in range(3, 10):
    limit = 10**exp
    t0 = time.time()
    print(f"\nScale 10^{exp} (limit={limit:,})...")

    primes = np.array(list(primerange(2, limit)), dtype=np.int64)
    n_primes = len(primes)
    gaps = np.diff(primes).astype(float)
    elapsed = time.time() - t0

    if len(gaps) < 30:
        print(f"  Only {len(gaps)} gaps, skipping")
        continue

    # Normalize
    mean_gap = np.mean(gaps)
    normed = gaps / mean_gap

    # Moment ratios
    m2 = np.mean(normed**2)
    m4 = np.mean(normed**4)
    m6 = np.mean(normed**6)
    m8 = np.mean(normed**8)

    m4m2 = m4 / (m2**2) if m2 > 0 else 0
    m6m2 = m6 / (m2**3) if m2 > 0 else 0
    m8m2 = m8 / (m2**4) if m2 > 0 else 0

    std_gap = np.std(gaps)
    max_gap = np.max(gaps)

    results_by_scale[exp] = {
        "exponent": exp,
        "limit": limit,
        "n_primes": int(n_primes),
        "n_gaps": int(len(gaps)),
        "mean_gap": float(mean_gap),
        "std_gap": float(std_gap),
        "max_gap": float(max_gap),
        "m2": float(m2),
        "m4m2": float(m4m2),
        "m6m2": float(m6m2),
        "m8m2": float(m8m2),
        "elapsed_s": round(elapsed, 1),
    }

    print(f"  n_primes={n_primes:,}, mean_gap={mean_gap:.3f}, max_gap={max_gap:.0f}")
    print(f"  M4/M2^2={m4m2:.4f}, M6/M2^3={m6m2:.4f}, M8/M2^4={m8m2:.4f}")
    print(f"  ({elapsed:.1f}s)")

# ============================================================
# TEST 1: M4/M2 linear scaling with log10(N)
# ============================================================
print("\n" + "="*70)
print("TEST 1: M4/M2^2 scaling with log10(N)")
print("="*70)

exps = np.array([r["exponent"] for r in results_by_scale.values()], dtype=float)
m4m2s = np.array([r["m4m2"] for r in results_by_scale.values()])

slope, intercept, r_val, p_val, se = sp_stats.linregress(exps, m4m2s)
print(f"Linear fit: M4/M2^2 = {slope:.4f} * log10(N) + {intercept:.4f}")
print(f"R^2 = {r_val**2:.6f}, p = {p_val:.2e}, SE = {se:.4f}")
print(f"Slope = {slope:.4f} per decade")
print(f"Prior claim from R1: +0.43/decade (or +0.23 from initial)")
print(f"Slope update: {slope:.4f}")

# ============================================================
# TEST 2: M6/M2^3 scaling
# ============================================================
print("\n" + "="*70)
print("TEST 2: M6/M2^3 scaling")
print("="*70)

m6m2s = np.array([r["m6m2"] for r in results_by_scale.values()])
slope6, intercept6, r6, p6, se6 = sp_stats.linregress(exps, m6m2s)
print(f"Linear fit: M6/M2^3 = {slope6:.4f} * log10(N) + {intercept6:.4f}")
print(f"R^2 = {r6**2:.6f}, p = {p6:.2e}")

# Log-linear fit
m6_pos = m6m2s[m6m2s > 0]
exps_pos = exps[m6m2s > 0]
if len(m6_pos) >= 3:
    slope6_log, intercept6_log, r6_log, p6_log, _ = sp_stats.linregress(
        exps_pos, np.log(m6_pos)
    )
    print(f"Log-linear: log(M6/M2^3) = {slope6_log:.4f} * log10(N) + {intercept6_log:.4f}")
    print(f"R^2 = {r6_log**2:.6f}")

# ============================================================
# TEST 3: M8/M2^4 scaling
# ============================================================
print("\n" + "="*70)
print("TEST 3: M8/M2^4 scaling")
print("="*70)

m8m2s = np.array([r["m8m2"] for r in results_by_scale.values()])
slope8, intercept8, r8, p8, se8 = sp_stats.linregress(exps, m8m2s)
print(f"Linear fit: M8/M2^4 = {slope8:.4f} * log10(N) + {intercept8:.4f}")
print(f"R^2 = {r8**2:.6f}, p = {p8:.2e}")

# ============================================================
# TEST 4: Convergence toward Poisson
# ============================================================
print("\n" + "="*70)
print("TEST 4: Convergence toward Poisson reference values")
print("="*70)
print("Reference (Poisson/Exponential): M4/M2^2=9.0, M6/M2^3=225, M8/M2^4=11025")
print("Reference (Gaussian):            M4/M2^2=3.0, M6/M2^3=15,  M8/M2^4=105")

for r in results_by_scale.values():
    pct = (r["m4m2"] - 3.0) / (9.0 - 3.0) * 100
    pct6 = (r["m6m2"] - 15.0) / (225.0 - 15.0) * 100
    pct8 = (r["m8m2"] - 105.0) / (11025.0 - 105.0) * 100
    print(f"  10^{r['exponent']}: M4/M2^2={r['m4m2']:.4f} ({pct:.1f}% G->P), "
          f"M6/M2^3={r['m6m2']:.2f} ({pct6:.1f}%), "
          f"M8/M2^4={r['m8m2']:.1f} ({pct8:.1f}%)")

# ============================================================
# TEST 5: F24 -- gaps grouped by decade of prime
# ============================================================
print("\n" + "="*70)
print("TEST 5: F24 -- gap values by decade of prime (at 10^8)")
print("="*70)
print("(Using 10^8 to keep memory reasonable for F24)")

# Use 10^8 scale for F24
f24_exp = 8
if f24_exp in results_by_scale:
    limit = 10**f24_exp
    primes = np.array(list(primerange(2, limit)), dtype=np.int64)
    gaps = np.diff(primes).astype(float)

    # Group by decade of the prime
    decade_labels = []
    for p in primes[:-1]:
        d = int(np.floor(np.log10(max(p, 2))))
        decade_labels.append(str(d))
    decade_labels = np.array(decade_labels)

    v24, r24 = bv2.F24_variance_decomposition(gaps, decade_labels)
    print(f"F24 verdict: {v24}, eta^2 = {r24.get('eta_squared', 0):.6f}")
    for gname, gstat in sorted(r24.get("group_stats", {}).items()):
        print(f"  Decade {gname}: n={gstat['n']:,}, mean_gap={gstat['mean']:.3f}, "
              f"std={gstat['std']:.3f}")

    # Free memory
    del primes, gaps, decade_labels
else:
    v24, r24 = "INSUFFICIENT_DATA", {}
    print(f"Scale 10^{f24_exp} not available")

# ============================================================
# TEST 6: F24b -- metric consistency across decades
# ============================================================
print("\n" + "="*70)
print("TEST 6: F24b -- metric consistency")
print("="*70)

# Use per-decade M4/M2 values as the metric
decade_m4m2_values = []
decade_m4m2_labels = []
for r in results_by_scale.values():
    decade_m4m2_values.append(r["m4m2"])
    decade_m4m2_labels.append(str(r["exponent"]))

# F24b needs more data points -- use the F24 gap data if available
if f24_exp in results_by_scale:
    print("Using 10^7 gap data for F24b grouping...")
    limit7 = 10**7
    primes7 = np.array(list(primerange(2, limit7)), dtype=np.int64)
    gaps7 = np.diff(primes7).astype(float)
    labels7 = [str(int(np.floor(np.log10(max(p, 2))))) for p in primes7[:-1]]

    if len(gaps7) >= 40 and len(set(labels7)) >= 2:
        v24b, r24b = bv2.F24b_metric_consistency(gaps7, labels7)
        print(f"F24b verdict: {v24b}")
        print(f"  M4/M2 ratio = {r24b.get('m4m2_ratio', 'N/A')}")
        print(f"  eta^2 = {r24b.get('eta_squared', 'N/A')}")
    else:
        v24b, r24b = "INSUFFICIENT_DATA", {}

    del primes7, gaps7, labels7
else:
    v24b, r24b = "INSUFFICIENT_DATA", {}
    print("No gap data available for F24b")

# ============================================================
# TEST 7: F25 -- transportability across even/odd decades
# ============================================================
print("\n" + "="*70)
print("TEST 7: F25 -- transportability across decade parity")
print("="*70)

# Use 10^7 data: primary = even/odd gap, secondary = decade
limit7 = 10**7
primes7 = np.array(list(primerange(2, limit7)), dtype=np.int64)
gaps7 = np.diff(primes7).astype(float)
prim_labels_f25 = ["even" if g % 2 == 0 else "odd" for g in gaps7]
sec_labels_f25 = [str(int(np.floor(np.log10(max(p, 2))))) for p in primes7[:-1]]

if len(set(sec_labels_f25)) >= 2:
    v25, r25 = bv2.F25_transportability(gaps7, prim_labels_f25, sec_labels_f25)
    print(f"F25 verdict: {v25}")
    print(f"  Weighted OOS R^2 = {r25.get('weighted_oos_r2', 'N/A')}")
    print(f"  Mean OOS R^2 = {r25.get('mean_oos_r2', 'N/A')}")
else:
    v25, r25 = "INSUFFICIENT_DATA", {}
    print("Insufficient secondary groups for F25")

del primes7, gaps7

# ============================================================
# TEST 8: F27 -- consequence check
# ============================================================
print("\n" + "="*70)
print("TEST 8: F27 -- tautology check")
print("="*70)

v27, r27 = bv2.F27_consequence_check("prime_decade", "gap_moment_ratio")
print(f"F27 verdict: {v27}")
if r27:
    print(f"  Details: {r27}")

# ============================================================
# CLASSIFICATION
# ============================================================
print("\n" + "="*70)
print("CLASSIFICATION")
print("="*70)

print(f"\nM4/M2^2 scaling slope: {slope:.4f}/decade (prior R1: ~0.43)")
print(f"M4/M2^2 at 10^9: {results_by_scale.get(9, {}).get('m4m2', 'N/A')}")
print(f"M6/M2^3 slope: {slope6:.4f}/decade")
print(f"M8/M2^4 slope: {slope8:.4f}/decade")
print(f"F24 decade grouping: {v24} (eta^2={r24.get('eta_squared', 'N/A')})")
print(f"F24b: {v24b}")
print(f"F25: {v25}")
print(f"F27: {v27}")

# Check if slope is consistent with prior
prior_slope = 0.43
slope_diff = abs(slope - prior_slope)
if slope_diff < 0.05:
    slope_verdict = "CONFIRMED"
    print(f"\n--> Slope CONFIRMED at {slope:.4f}/decade (within 0.05 of prior {prior_slope})")
elif slope_diff < 0.15:
    slope_verdict = "REFINED"
    print(f"\n--> Slope REFINED to {slope:.4f}/decade (prior was {prior_slope})")
else:
    slope_verdict = "REVISED"
    print(f"\n--> Slope REVISED to {slope:.4f}/decade (prior was {prior_slope}, delta={slope_diff:.3f})")

if r24.get("eta_squared", 0) >= 0.14:
    classification = "LAW"
elif r24.get("eta_squared", 0) >= 0.01:
    classification = "TENDENCY"
else:
    classification = "NEGLIGIBLE"
print(f"--> CLASSIFICATION: {classification}")

# ============================================================
# Table summary
# ============================================================
print("\n" + "="*70)
print("SUMMARY TABLE")
print("="*70)
print(f"{'Decade':<10} {'n_primes':>12} {'mean_gap':>10} {'M4/M2^2':>10} "
      f"{'M6/M2^3':>12} {'M8/M2^4':>12} {'time_s':>8}")
print("-"*74)
for r in sorted(results_by_scale.values(), key=lambda x: x["exponent"]):
    print(f"  10^{r['exponent']:<5} {r['n_primes']:>12,} {r['mean_gap']:>10.3f} "
          f"{r['m4m2']:>10.4f} {r['m6m2']:>12.4f} {r['m8m2']:>12.2f} "
          f"{r['elapsed_s']:>8.1f}")

# ============================================================
# Save results
# ============================================================
final_results = {
    "test": "C43-ext/R2",
    "claim": f"Prime gap M4/M2^2 scales at ~{prior_slope}/decade toward Poisson",
    "scaling_slope_m4m2": float(slope),
    "scaling_r2_m4m2": float(r_val**2),
    "scaling_slope_m6m2": float(slope6),
    "scaling_slope_m8m2": float(slope8),
    "slope_verdict": slope_verdict,
    "decade_eta2": r24.get("eta_squared", 0),
    "classification": classification,
    "f24": {"verdict": v24, "result": r24},
    "f24b": {"verdict": v24b, "result": r24b},
    "f25": {"verdict": v25, "result": r25},
    "f27": {"verdict": v27, "result": r27},
    "by_scale": results_by_scale,
}

out_path = Path(__file__).resolve().parent / "v2" / "c43_ext_prime_gap_scaling_results.json"
out_path.parent.mkdir(exist_ok=True)
with open(out_path, "w") as f:
    json.dump(final_results, f, indent=2, default=str)
print(f"\nResults saved to v2/c43_ext_prime_gap_scaling_results.json")
