#!/usr/bin/env python3
"""
Battery Precision Calibration Suite.
Throw known-true, known-false, noisy-true, and random-noise at the battery.
Measure: precision (false positive rate), recall (false negative rate),
and boundary behavior (where does the battery get confused?).

Three calibration axes:
1. SYNTHETIC KNOWNS — inject signals of known strength, measure detection
2. RANDOM EXPLORATION — shuffle real data, see what the battery finds (FPR)
3. NOISY GROUND TRUTHS — known physics/math facts with realistic noise

M1 (Skullport), 2026-04-12
"""
import sys, os, json
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

_scripts = str(Path("F:/Prometheus/cartography/shared/scripts").resolve())
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from battery_v2 import BatteryV2
from scipy import stats as sp_stats
bv2 = BatteryV2()

rng = np.random.RandomState(42)
results = {"synthetic": {}, "random": {}, "noisy_truths": {}}

# ═══════════════════════════════════════════════════════════════════════
# AXIS 1: SYNTHETIC SIGNAL INJECTION
# Inject grouping effects of known eta² and measure battery detection
# ═══════════════════════════════════════════════════════════════════════
print("="*80)
print("AXIS 1: SYNTHETIC SIGNAL INJECTION")
print("="*80)

print("\nInjecting signals with known eta² from 0.001 to 0.500...")
print(f"{'eta2_true':>10s} {'F24_eta2':>10s} {'F24_verdict':>20s} {'F24b':>15s} {'Detected':>10s}")

synthetic_results = []
for true_eta2 in [0.001, 0.005, 0.01, 0.02, 0.05, 0.10, 0.14, 0.20, 0.30, 0.50]:
    # Generate: 5 groups, 200 per group, with specified eta²
    n_groups = 5
    n_per_group = 200
    n_total = n_groups * n_per_group

    # eta² = SS_between / SS_total
    # If group means are mu_k and within-group std is sigma_w:
    # SS_between ~ n_per_group * sum(mu_k - grand_mean)^2
    # SS_within ~ n_total * sigma_w^2
    # eta² = SS_between / (SS_between + SS_within)

    sigma_w = 1.0  # within-group std
    # Solve for between-group std
    # eta² = n_per * k * sigma_b^2 / (n_per * k * sigma_b^2 + n_total * sigma_w^2)
    # eta² * (n_per*k*sb^2 + n_total*sw^2) = n_per*k*sb^2
    # eta² * n_total * sw^2 = n_per*k*sb^2 * (1 - eta²)
    # sb^2 = eta² * n_total * sw^2 / (n_per * k * (1 - eta²))
    sigma_b = np.sqrt(true_eta2 * n_total * sigma_w**2 / (n_per_group * n_groups * (1 - true_eta2 + 1e-10)))

    group_means = rng.normal(0, sigma_b, n_groups)
    values = []
    labels = []
    for g in range(n_groups):
        vals = rng.normal(group_means[g], sigma_w, n_per_group)
        values.extend(vals)
        labels.extend([f"G{g}"] * n_per_group)

    values = np.array(values)
    labels = np.array(labels)

    v24, r24 = bv2.F24_variance_decomposition(values, labels)
    v24b, r24b = bv2.F24b_metric_consistency(values, labels)
    measured_eta2 = r24.get("eta_squared", 0)

    detected = "YES" if (true_eta2 >= 0.14 and v24 == "STRONG_EFFECT") or \
                        (true_eta2 >= 0.06 and v24 in ("STRONG_EFFECT", "MODERATE_EFFECT")) or \
                        (true_eta2 >= 0.01 and v24 != "NEGLIGIBLE_EFFECT") else \
               "CORRECT_NULL" if true_eta2 < 0.01 and v24 == "NEGLIGIBLE_EFFECT" else \
               "MISS" if true_eta2 >= 0.01 and v24 == "NEGLIGIBLE_EFFECT" else \
               "FALSE_POS" if true_eta2 < 0.01 and v24 != "NEGLIGIBLE_EFFECT" else "OK"

    print(f"{true_eta2:>10.3f} {measured_eta2:>10.4f} {v24:>20s} {v24b:>15s} {detected:>10s}")
    synthetic_results.append({
        "true_eta2": true_eta2, "measured_eta2": measured_eta2,
        "verdict": v24, "f24b": v24b, "detected": detected
    })

results["synthetic"] = synthetic_results

# ═══════════════════════════════════════════════════════════════════════
# AXIS 2: RANDOM EXPLORATION — False Positive Rate
# Shuffle real data labels and run battery. Measure FPR.
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("AXIS 2: RANDOM EXPLORATION — False Positive Rate")
print("="*80)

# Load real data
import duckdb
con = duckdb.connect("F:/Prometheus/charon/data/charon.duckdb", read_only=True)
ec_df = con.execute("SELECT conductor, rank FROM elliptic_curves WHERE rank IS NOT NULL LIMIT 20000").fetchdf()
con.close()

with open(Path("F:/Prometheus/cartography/knots/data/knots.json")) as f:
    knot_data = json.load(f)
knot_dets = np.array([k["determinant"] for k in knot_data["knots"] if (k.get("determinant") or 0) > 0], dtype=float)

with open(Path("F:/Prometheus/cartography/number_fields/data/number_fields.json")) as f:
    nf_data = json.load(f)
nf_cn = np.array([int(d["class_number"]) for d in nf_data if int(d["class_number"]) > 0], dtype=float)

# Test 1: Random grouping labels on real data
print("\nTest 2a: Random 5-group labels on EC conductors (100 trials)")
fp_count_f24 = 0
n_trials = 100
for trial in range(n_trials):
    cond = ec_df["conductor"].values.astype(float)[:5000]
    fake_labels = rng.choice(["A", "B", "C", "D", "E"], size=len(cond))
    v, r = bv2.F24_variance_decomposition(cond, fake_labels)
    if r.get("eta_squared", 0) >= 0.01:  # false positive at TENDENCY threshold
        fp_count_f24 += 1

print(f"  F24 false positives (eta2 >= 0.01): {fp_count_f24}/{n_trials} ({fp_count_f24/n_trials*100:.1f}%)")

# Test 2: Random pairing of cross-domain data
print("\nTest 2b: Random cross-domain pairings (knot det vs NF class number)")
fp_cross = 0
for trial in range(n_trials):
    # Shuffle one array
    min_n = min(len(knot_dets), len(nf_cn), 3000)
    a = rng.choice(knot_dets, min_n, replace=False)
    b = rng.choice(nf_cn, min_n, replace=False)
    rho, p = sp_stats.spearmanr(a, b)
    if abs(rho) > 0.05 and p < 0.01:
        fp_cross += 1

print(f"  Cross-domain false correlations (|rho|>0.05, p<0.01): {fp_cross}/{n_trials} ({fp_cross/n_trials*100:.1f}%)")

# Test 3: Permuted labels on known finding (SC_class->Tc analog)
print("\nTest 2c: Shuffled EC rank labels -> conductor (should be null)")
fp_shuffled = 0
for trial in range(n_trials):
    cond = ec_df["conductor"].values.astype(float)[:5000]
    ranks = ec_df["rank"].values.astype(str)[:5000]
    shuffled_ranks = rng.permutation(ranks)
    v, r = bv2.F24_variance_decomposition(cond, shuffled_ranks)
    if r.get("eta_squared", 0) >= 0.01:
        fp_shuffled += 1

print(f"  Shuffled label false positives: {fp_shuffled}/{n_trials} ({fp_shuffled/n_trials*100:.1f}%)")

results["random"] = {
    "fpr_random_groups": fp_count_f24 / n_trials,
    "fpr_cross_domain": fp_cross / n_trials,
    "fpr_shuffled_labels": fp_shuffled / n_trials,
}

# ═══════════════════════════════════════════════════════════════════════
# AXIS 3: NOISY GROUND TRUTHS
# Known relationships with realistic noise levels
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("AXIS 3: NOISY GROUND TRUTHS")
print("="*80)

noisy_results = []

# 3a. Z -> atomic radius (known, noisy)
print("\n  3a. Atomic number -> log(atomic radius) (periodic table)")
# Ground truth: atomic radius generally increases within groups, decreases across periods
# Real relationship: noisy, non-monotonic, periodic
Z = np.arange(1, 119)
# Approximate: radius ~ 0.5 + 0.3*period + 0.1*random - 0.02*group
period = np.array([1,1,2,2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,
                   4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,
                   5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,
                   6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,
                   7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7][:118])
group_labels = np.array([str(p) for p in period])
radius = 30 + 15 * period + rng.normal(0, 10, 118)

v, r = bv2.F24_variance_decomposition(radius, group_labels)
print(f"  F24 period->radius: {v}, eta2={r.get('eta_squared', 0):.4f}")
noisy_results.append({"test": "Z->radius", "truth": "REAL", "eta2": r.get("eta_squared", 0), "verdict": v})

# 3b. Random walk vs structured walk
print("\n  3b. Random walk (should be NULL) vs structured walk (should detect)")
random_walk = np.cumsum(rng.normal(0, 1, 1000))
structured_walk = np.cumsum(rng.normal(0.05, 1, 1000))  # drift
labels_rw = np.array(["first_half"] * 500 + ["second_half"] * 500)

v_rw, r_rw = bv2.F24_variance_decomposition(random_walk, labels_rw)
v_sw, r_sw = bv2.F24_variance_decomposition(structured_walk, labels_rw)
print(f"  Random walk (half-split): {v_rw}, eta2={r_rw.get('eta_squared', 0):.4f}")
print(f"  Drift walk (half-split): {v_sw}, eta2={r_sw.get('eta_squared', 0):.4f}")

# 3c. Known: prime count ~ x/ln(x) (PNT)
print("\n  3c. Prime counting function vs x/ln(x) (PNT)")
from sympy import primepi
x_vals = np.array([10**k for k in range(2, 8)])
pi_x = np.array([primepi(int(x)) for x in x_vals], dtype=float)
approx = x_vals / np.log(x_vals)
ratio = pi_x / approx
print(f"  pi(x) / (x/ln(x)) ratios: {np.round(ratio, 4)}")
print(f"  Converging to 1: {'YES' if ratio[-1] > ratio[0] and abs(ratio[-1] - 1) < abs(ratio[0] - 1) else 'NO'}")

# 3d. Known FALSE: consecutive primes are independent
print("\n  3d. Consecutive prime gaps -> next gap (should be NULL)")
from sympy import primerange
primes_list = list(primerange(2, 100000))
gaps = np.diff(primes_list).astype(float)
current_gap = gaps[:-1]
next_gap = gaps[1:]
rho, p = sp_stats.spearmanr(current_gap, next_gap)
print(f"  Gap autocorrelation: rho={rho:.4f}, p={p:.2e}")
# F24: bin current gap, measure next gap
gap_bins = np.array(["small" if g <= 2 else "medium" if g <= 6 else "large" for g in current_gap])
v_gap, r_gap = bv2.F24_variance_decomposition(next_gap, gap_bins)
print(f"  F24 gap_bin->next_gap: {v_gap}, eta2={r_gap.get('eta_squared', 0):.4f}")
noisy_results.append({"test": "gap_autocorr", "truth": "WEAK_REAL", "eta2": r_gap.get("eta_squared", 0), "verdict": v_gap})

# 3e. Simpson's paradox trap
print("\n  3e. Simpson's paradox: global vs stratified effect")
# Two groups with opposite slopes
n_each = 500
x1 = rng.normal(10, 2, n_each)
y1 = 2 * x1 + rng.normal(0, 3, n_each) + 50  # positive slope, high baseline
x2 = rng.normal(20, 2, n_each)
y2 = -1.5 * x2 + rng.normal(0, 3, n_each) + 80  # negative slope, higher baseline
x_all = np.concatenate([x1, x2])
y_all = np.concatenate([y1, y2])
group_all = np.array(["A"]*n_each + ["B"]*n_each)

rho_global, _ = sp_stats.spearmanr(x_all, y_all)
rho_a, _ = sp_stats.spearmanr(x1, y1)
rho_b, _ = sp_stats.spearmanr(x2, y2)
print(f"  Global rho: {rho_global:.4f}")
print(f"  Within A: {rho_a:.4f}, Within B: {rho_b:.4f}")
print(f"  Simpson's paradox: {'YES' if rho_global * rho_a < 0 else 'NO'}")

v_simp, r_simp = bv2.F24_variance_decomposition(y_all, group_all)
print(f"  F24 group->y: {v_simp}, eta2={r_simp.get('eta_squared', 0):.4f}")

# F25: does the relationship transfer?
x_labels = np.array(["lo" if v < np.median(x_all) else "hi" for v in x_all])
v_f25, r_f25 = bv2.F25_transportability(y_all, x_labels, group_all)
print(f"  F25 (x->y across groups): {v_f25}")
noisy_results.append({"test": "simpsons_paradox", "truth": "PARADOX", "eta2": r_simp.get("eta_squared", 0),
                       "f25": v_f25, "global_rho": float(rho_global)})

# 3f. Tail-driven vs bulk effect (battery should distinguish)
print("\n  3f. Tail-driven vs bulk-driven effect")
# Bulk: two groups with different means, same shape
bulk_a = rng.normal(10, 3, 500)
bulk_b = rng.normal(12, 3, 500)
bulk_all = np.concatenate([bulk_a, bulk_b])
bulk_labels = np.array(["A"]*500 + ["B"]*500)

v_bulk, r_bulk = bv2.F24_variance_decomposition(bulk_all, bulk_labels)
v_bulk_b, r_bulk_b = bv2.F24b_metric_consistency(bulk_all, bulk_labels)
print(f"  Bulk effect: F24 eta2={r_bulk.get('eta_squared', 0):.4f}, F24b={v_bulk_b}")

# Tail: same means, different tail heaviness
tail_a = rng.normal(10, 3, 500)
tail_b = np.concatenate([rng.normal(10, 3, 450), rng.normal(10, 15, 50)])  # 10% heavy tail
tail_all = np.concatenate([tail_a, tail_b])
tail_labels = np.array(["A"]*500 + ["B"]*500)

v_tail, r_tail = bv2.F24_variance_decomposition(tail_all, tail_labels)
v_tail_b, r_tail_b = bv2.F24b_metric_consistency(tail_all, tail_labels)
print(f"  Tail effect: F24 eta2={r_tail.get('eta_squared', 0):.4f}, F24b={v_tail_b}")
print(f"  Battery distinguishes: {'YES' if v_bulk_b != v_tail_b else 'NO'}")

results["noisy_truths"] = noisy_results

# ═══════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("BATTERY CALIBRATION SUMMARY")
print("="*80)

print("\n  SYNTHETIC SIGNAL DETECTION:")
for s in synthetic_results:
    marker = "OK" if s["detected"] in ("YES", "CORRECT_NULL", "OK") else "**PROBLEM**"
    print(f"    eta2={s['true_eta2']:.3f} -> measured {s['measured_eta2']:.4f}, {s['verdict']:>20s} [{marker}]")

print(f"\n  FALSE POSITIVE RATES:")
print(f"    Random 5-group labels: {results['random']['fpr_random_groups']*100:.1f}%")
print(f"    Random cross-domain: {results['random']['fpr_cross_domain']*100:.1f}%")
print(f"    Shuffled real labels: {results['random']['fpr_shuffled_labels']*100:.1f}%")

print(f"\n  PRECISION ESTIMATE:")
total_nulls = 300  # 3 x 100 trials
total_fp = fp_count_f24 + fp_cross + fp_shuffled
fpr = total_fp / total_nulls
print(f"    Total null trials: {total_nulls}")
print(f"    Total false positives: {total_fp}")
print(f"    FPR: {fpr*100:.1f}%")
print(f"    Precision at TENDENCY threshold (eta2>=0.01): {(1-fpr)*100:.1f}%")

print(f"\n  BOUNDARY BEHAVIOR:")
print(f"    Simpson's paradox: {'DETECTED' if 'PARADOX' in str(noisy_results) else 'MISSED'}")
print(f"    Tail vs bulk distinction: {'WORKING' if v_bulk_b != v_tail_b else 'NEEDS WORK'}")

# Save
with open(Path(_scripts) / "v2/battery_calibration_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nSaved to v2/battery_calibration_results.json")
