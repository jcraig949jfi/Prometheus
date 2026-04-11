"""
OEIS Benford's Law Compliance Analysis

Tests whether OEIS integer sequences follow Benford's law:
  P(d) = log10(1 + 1/d) for leading digit d in {1,...,9}

Approach:
1. Load 10,000 OEIS sequences from stripped_new.txt
2. Extract leading digits of all positive integer terms
3. Aggregate distribution and compare to Benford via chi-squared and KL divergence
4. Per-sequence compliance (chi-squared test at alpha=0.05)
5. Growth-rate correlation: exponential sequences should comply better
"""

import json
import math
import os
import numpy as np
from collections import Counter
from scipy import stats

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "oeis", "data", "stripped_new.txt")
OUT_FILE = os.path.join(os.path.dirname(__file__), "oeis_benford_results.json")

NUM_SEQUENCES = 10000


def benford_distribution():
    """Theoretical Benford distribution for digits 1-9."""
    return {d: math.log10(1 + 1/d) for d in range(1, 10)}


def leading_digit(n):
    """Extract leading digit of a positive integer."""
    s = str(n)
    return int(s[0])


def parse_sequences(path, max_seq=NUM_SEQUENCES):
    """Parse stripped OEIS file. Returns list of (seq_id, terms_list)."""
    sequences = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split(" ", 1)
            if len(parts) < 2:
                continue
            seq_id = parts[0]
            raw = parts[1].strip().strip(",")
            if not raw:
                continue
            try:
                terms = [int(x) for x in raw.split(",") if x.strip()]
            except ValueError:
                continue
            sequences.append((seq_id, terms))
            if len(sequences) >= max_seq:
                break
    return sequences


def compute_growth_class(terms):
    """
    Classify growth rate of a sequence.
    Uses ratio of log(|a(n)|) to n for positive terms.
    Returns: 'exponential', 'polynomial', 'sublinear', 'constant', or 'unknown'
    Also returns estimated growth exponent.
    """
    pos = [(i, t) for i, t in enumerate(terms) if t > 0]
    if len(pos) < 5:
        return "unknown", 0.0

    indices = np.array([p[0] for p in pos], dtype=float)
    log_vals = np.array([math.log10(p[1]) if p[1] > 0 else 0 for p in pos])

    # Check if values are all same (constant)
    if np.std(log_vals) < 1e-10:
        return "constant", 0.0

    # Fit log(a(n)) vs n  -- if slope > threshold, exponential
    # Fit log(a(n)) vs log(n) -- polynomial exponent
    valid = indices > 0
    if valid.sum() < 3:
        return "unknown", 0.0

    # Exponential test: log(a(n)) ~ c * n
    try:
        slope_exp, _, r_exp, _, _ = stats.linregress(indices[valid], log_vals[valid])
    except Exception:
        return "unknown", 0.0

    # Polynomial test: log(a(n)) ~ alpha * log(n)
    log_idx = np.log10(indices[valid])
    try:
        slope_poly, _, r_poly, _, _ = stats.linregress(log_idx, log_vals[valid])
    except Exception:
        return "unknown", 0.0

    if r_exp**2 > 0.95 and slope_exp > 0.01:
        return "exponential", slope_exp
    elif r_poly**2 > 0.90 and slope_poly > 0.5:
        return "polynomial", slope_poly
    elif r_poly**2 > 0.80:
        return "sublinear", slope_poly
    else:
        return "unknown", 0.0


def main():
    print("Loading sequences...")
    sequences = parse_sequences(DATA_FILE, NUM_SEQUENCES)
    print(f"Loaded {len(sequences)} sequences")

    benford = benford_distribution()
    benford_probs = np.array([benford[d] for d in range(1, 10)])

    # === Aggregate analysis ===
    global_counts = Counter()
    total_positive_terms = 0

    # === Per-sequence analysis ===
    per_seq_results = []
    compliant_count = 0
    growth_benford = {"exponential": [], "polynomial": [], "sublinear": [],
                      "constant": [], "unknown": []}

    for seq_id, terms in sequences:
        # Extract leading digits of positive terms
        digits = []
        for t in terms:
            if t > 0:
                d = leading_digit(t)
                if 1 <= d <= 9:
                    digits.append(d)
                    global_counts[d] += 1
                    total_positive_terms += 1

        # Per-sequence chi-squared (need enough terms)
        growth_class, growth_exp = compute_growth_class(terms)

        if len(digits) >= 20:  # minimum for meaningful test
            obs_counts = np.array([digits.count(d) for d in range(1, 10)])
            n = len(digits)
            expected = benford_probs * n

            # Chi-squared
            chi2_stat = np.sum((obs_counts - expected)**2 / expected)
            p_value = 1 - stats.chi2.cdf(chi2_stat, df=8)
            complies = p_value > 0.05

            if complies:
                compliant_count += 1

            # KL divergence for this sequence
            obs_probs = obs_counts / n
            obs_probs = np.clip(obs_probs, 1e-10, None)  # avoid log(0)
            kl = np.sum(obs_probs * np.log(obs_probs / benford_probs))

            per_seq_results.append({
                "seq_id": seq_id,
                "n_terms": n,
                "chi2": round(float(chi2_stat), 4),
                "p_value": round(float(p_value), 6),
                "compliant": bool(complies),
                "kl_divergence": round(float(kl), 6),
                "growth_class": growth_class,
                "growth_exponent": round(float(growth_exp), 6),
            })

            growth_benford[growth_class].append(complies)

    # === Global distribution ===
    total = sum(global_counts.values())
    observed_dist = {d: global_counts[d] / total for d in range(1, 10)}

    obs_array = np.array([global_counts[d] for d in range(1, 10)])
    exp_array = benford_probs * total

    # Global chi-squared
    chi2_global = float(np.sum((obs_array - exp_array)**2 / exp_array))
    p_global = float(1 - stats.chi2.cdf(chi2_global, df=8))

    # Global KL divergence
    obs_probs_global = obs_array / total
    kl_global = float(np.sum(obs_probs_global * np.log(obs_probs_global / benford_probs)))

    # === Growth class compliance rates ===
    growth_compliance = {}
    for gc, vals in growth_benford.items():
        if vals:
            growth_compliance[gc] = {
                "n_sequences": len(vals),
                "compliant": sum(vals),
                "compliance_rate": round(sum(vals) / len(vals), 4),
            }

    # === Median KL by growth class ===
    growth_kl = {}
    for r in per_seq_results:
        gc = r["growth_class"]
        if gc not in growth_kl:
            growth_kl[gc] = []
        growth_kl[gc].append(r["kl_divergence"])

    growth_kl_summary = {}
    for gc, vals in growth_kl.items():
        growth_kl_summary[gc] = {
            "n": len(vals),
            "median_kl": round(float(np.median(vals)), 6),
            "mean_kl": round(float(np.mean(vals)), 6),
        }

    # === Summary ===
    n_tested = len(per_seq_results)

    results = {
        "experiment": "OEIS Benford's Law Compliance",
        "n_sequences_loaded": len(sequences),
        "n_sequences_tested": n_tested,
        "min_terms_for_test": 20,
        "total_positive_terms": total_positive_terms,
        "aggregate": {
            "observed_distribution": {str(d): round(observed_dist[d], 6) for d in range(1, 10)},
            "benford_distribution": {str(d): round(benford[d], 6) for d in range(1, 10)},
            "chi_squared": round(chi2_global, 2),
            "chi_squared_df": 8,
            "p_value": p_global,
            "kl_divergence": round(kl_global, 6),
            "verdict": "COMPLIANT" if p_global > 0.05 else "NON-COMPLIANT",
        },
        "per_sequence": {
            "n_tested": n_tested,
            "n_compliant": compliant_count,
            "compliance_rate": round(compliant_count / n_tested, 4) if n_tested > 0 else 0,
        },
        "growth_class_compliance": growth_compliance,
        "growth_class_kl": growth_kl_summary,
        "interpretation": [],
    }

    # Generate interpretation
    interp = results["interpretation"]
    interp.append(f"Aggregate: {total_positive_terms:,} positive terms across {len(sequences):,} sequences.")

    if p_global > 0.05:
        interp.append(f"Aggregate Benford compliance: YES (chi2={chi2_global:.1f}, p={p_global:.4f}).")
    else:
        interp.append(f"Aggregate Benford compliance: NO (chi2={chi2_global:.1f}, p={p_global:.2e}).")

    interp.append(f"KL divergence from Benford: {kl_global:.6f}")
    interp.append(f"Per-sequence: {compliant_count}/{n_tested} ({100*compliant_count/n_tested:.1f}%) comply at alpha=0.05.")

    for gc in ["exponential", "polynomial", "sublinear", "constant", "unknown"]:
        if gc in growth_compliance:
            gc_data = growth_compliance[gc]
            rate = gc_data["compliance_rate"]
            interp.append(f"  {gc}: {gc_data['compliant']}/{gc_data['n_sequences']} ({100*rate:.1f}%) comply")

    # Top 10 most / least compliant
    sorted_by_kl = sorted(per_seq_results, key=lambda x: x["kl_divergence"])
    results["most_benford_compliant"] = sorted_by_kl[:10]
    results["least_benford_compliant"] = sorted_by_kl[-10:]

    print("\n=== RESULTS ===")
    print(f"Total positive terms analyzed: {total_positive_terms:,}")
    print(f"\nAggregate leading digit distribution:")
    for d in range(1, 10):
        print(f"  d={d}: observed={observed_dist[d]:.4f}  benford={benford[d]:.4f}  "
              f"ratio={observed_dist[d]/benford[d]:.3f}")
    print(f"\nAggregate chi-squared: {chi2_global:.1f} (df=8, p={p_global:.2e})")
    print(f"Aggregate KL divergence: {kl_global:.6f}")
    print(f"\nPer-sequence compliance: {compliant_count}/{n_tested} ({100*compliant_count/n_tested:.1f}%)")
    print(f"\nBy growth class:")
    for gc in ["exponential", "polynomial", "sublinear", "constant", "unknown"]:
        if gc in growth_compliance:
            gc_data = growth_compliance[gc]
            kl_data = growth_kl_summary.get(gc, {})
            print(f"  {gc}: {gc_data['compliance_rate']*100:.1f}% comply, "
                  f"median KL={kl_data.get('median_kl', 'N/A')}")

    # Save
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to {OUT_FILE}")


if __name__ == "__main__":
    main()
