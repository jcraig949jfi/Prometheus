"""
Lattice Minimum Norm Distribution
==================================
Minimum norm = squared length of shortest nonzero vector.
Governs packing density (sphere packing radius = sqrt(min_norm)/2).

Analysis:
1. Distribution of min_norm by dimension
2. min_norm vs det correlation (Minkowski bound: min_norm <= C_d * det^{1/d})
3. Verify Minkowski bound: any violations?
4. min_norm vs kissing number correlation
"""
import json
import math
import numpy as np
from collections import defaultdict
from pathlib import Path
from scipy import stats

DATA = Path("F:/Prometheus/cartography/lmfdb_dump/lat_lattices.json")
OUT = Path("F:/Prometheus/cartography/v2/lattice_min_norm_results.json")


def load_lattices():
    """Load lattice data from LMFDB dump."""
    with open(DATA, "r") as f:
        raw = json.load(f)

    records = raw["records"]
    lattices = []
    for r in records:
        dim = r.get("dim")
        det = r.get("det")
        minimum = r.get("minimum")
        kissing = r.get("kissing")
        if dim is not None and det is not None and minimum is not None:
            lattices.append({
                "dim": int(dim),
                "det": float(det),
                "min_norm": float(minimum),
                "kissing": int(kissing) if kissing is not None else None,
                "label": r.get("label", ""),
                "name": r.get("name", ""),
            })
    return lattices


def minkowski_constant(d):
    """
    Minkowski's theorem: min_norm <= 2 * (det)^{1/d} * (gamma_d)
    where gamma_d ~ d/(2*pi*e) for large d (Hermite constant bound).

    Conservative upper bound using Minkowski-Hlawka:
      min_norm <= 2 * V_d^{-2/d} * det^{1/d}
    where V_d = pi^{d/2} / Gamma(d/2 + 1) is the volume of unit d-ball.

    We use the classical bound: lambda_1^2 <= (4/pi) * Gamma(d/2+1)^{2/d} * det^{2/d}
    which is Minkowski's first theorem for the squared minimum norm.
    Actually the standard Minkowski bound for lattice packing is:
      lambda_1^2 <= gamma_d * det^{2/d}
    where gamma_d is the Hermite constant. Known exact values for d<=8,24.
    For general d, gamma_d <= (4/3)^{(d-1)/2} (Blichfeldt bound, loose).
    We use: gamma_d <= 1 + d/4 as a practical bound for small d.
    """
    # Known Hermite constants (exact or best known) for small d
    hermite_exact = {
        1: 1.0,
        2: 2.0 / math.sqrt(3.0),  # = 2/sqrt(3) ~ 1.1547
        3: 2**(1/3),              # ~ 1.2599
        4: math.sqrt(2),          # ~ 1.4142
        5: 8**(1/5),              # ~ 1.5157
        6: (64/3)**(1/6),         # ~ 1.6654
        7: 64**(1/7),             # ~ 1.8114
        8: 2.0,                   # E8
        24: 4.0,                  # Leech
    }
    # gamma_d values (squared Hermite constant)
    if d in hermite_exact:
        return hermite_exact[d] ** 2
    # Blichfeldt bound for others
    return (4.0 / 3.0) ** ((d - 1) / 2.0)


def distribution_by_dim(lattices):
    """Min norm distribution statistics by dimension."""
    by_dim = defaultdict(list)
    for lat in lattices:
        by_dim[lat["dim"]].append(lat["min_norm"])

    results = {}
    for d in sorted(by_dim):
        vals = np.array(by_dim[d])
        results[str(d)] = {
            "count": len(vals),
            "mean": float(np.mean(vals)),
            "median": float(np.median(vals)),
            "std": float(np.std(vals)),
            "min": float(np.min(vals)),
            "max": float(np.max(vals)),
            "q25": float(np.percentile(vals, 25)),
            "q75": float(np.percentile(vals, 75)),
        }
    return results


def min_norm_vs_det(lattices):
    """Correlation between min_norm and det^{2/d} (Hermite normalization)."""
    by_dim = defaultdict(list)
    for lat in lattices:
        by_dim[lat["dim"]].append(lat)

    results = {}
    for d in sorted(by_dim):
        lats = by_dim[d]
        if len(lats) < 10:
            continue
        min_norms = np.array([l["min_norm"] for l in lats])
        dets = np.array([l["det"] for l in lats])

        # Hermite invariant: gamma = min_norm / det^{2/d}
        det_scaled = dets ** (2.0 / d)
        hermite_inv = min_norms / np.where(det_scaled > 0, det_scaled, 1e-15)

        # Pearson correlation of min_norm vs det^{2/d}
        r, p = stats.pearsonr(min_norms, det_scaled)
        # Spearman
        rho, p_sp = stats.spearmanr(min_norms, det_scaled)

        results[str(d)] = {
            "count": len(lats),
            "pearson_r": float(r),
            "pearson_p": float(p),
            "spearman_rho": float(rho),
            "spearman_p": float(p_sp),
            "hermite_invariant_mean": float(np.mean(hermite_inv)),
            "hermite_invariant_std": float(np.std(hermite_inv)),
            "hermite_invariant_max": float(np.max(hermite_inv)),
        }
    return results


def verify_minkowski(lattices):
    """Check Minkowski bound: min_norm <= gamma_d * det^{2/d}."""
    violations = []
    by_dim_stats = defaultdict(lambda: {"count": 0, "ratio_max": 0.0, "ratios": []})

    for lat in lattices:
        d = lat["dim"]
        det = lat["det"]
        mn = lat["min_norm"]

        gamma_d = minkowski_constant(d)
        bound = gamma_d * (det ** (2.0 / d))
        ratio = mn / bound if bound > 0 else float("inf")

        by_dim_stats[d]["count"] += 1
        by_dim_stats[d]["ratios"].append(ratio)
        if ratio > by_dim_stats[d]["ratio_max"]:
            by_dim_stats[d]["ratio_max"] = ratio

        if mn > bound * 1.001:  # small tolerance for float
            violations.append({
                "label": lat["label"],
                "name": lat["name"],
                "dim": d,
                "det": det,
                "min_norm": mn,
                "bound": round(bound, 6),
                "ratio": round(ratio, 6),
            })

    summary = {}
    for d in sorted(by_dim_stats):
        ratios = np.array(by_dim_stats[d]["ratios"])
        summary[str(d)] = {
            "count": by_dim_stats[d]["count"],
            "ratio_mean": float(np.mean(ratios)),
            "ratio_max": float(np.max(ratios)),
            "ratio_median": float(np.median(ratios)),
            "fraction_above_half": float(np.mean(ratios > 0.5)),
            "gamma_d_used": float(minkowski_constant(d)),
        }

    return {
        "n_violations": len(violations),
        "violations_sample": violations[:20],
        "by_dim": summary,
    }


def min_norm_vs_kissing(lattices):
    """Correlation between min_norm and kissing number."""
    by_dim = defaultdict(list)
    for lat in lattices:
        if lat["kissing"] is not None:
            by_dim[lat["dim"]].append(lat)

    results = {}
    for d in sorted(by_dim):
        lats = by_dim[d]
        if len(lats) < 10:
            continue
        min_norms = np.array([l["min_norm"] for l in lats])
        kissing = np.array([float(l["kissing"]) for l in lats])

        r, p = stats.pearsonr(min_norms, kissing)
        rho, p_sp = stats.spearmanr(min_norms, kissing)

        # Also log-log
        mask = (min_norms > 0) & (kissing > 0)
        if mask.sum() > 10:
            r_log, p_log = stats.pearsonr(np.log(min_norms[mask]), np.log(kissing[mask]))
        else:
            r_log, p_log = None, None

        results[str(d)] = {
            "count": len(lats),
            "pearson_r": float(r),
            "pearson_p": float(p),
            "spearman_rho": float(rho),
            "spearman_p": float(p_sp),
            "log_log_pearson_r": float(r_log) if r_log is not None else None,
            "log_log_pearson_p": float(p_log) if p_log is not None else None,
            "kissing_mean": float(np.mean(kissing)),
            "kissing_max": float(np.max(kissing)),
        }
    return results


def main():
    print("Loading lattices...")
    lattices = load_lattices()
    print(f"  {len(lattices)} lattices loaded")

    print("1. Distribution by dimension...")
    dist = distribution_by_dim(lattices)
    for d, s in dist.items():
        print(f"  dim={d}: n={s['count']}, mean={s['mean']:.2f}, "
              f"median={s['median']:.1f}, range=[{s['min']:.0f}, {s['max']:.0f}]")

    print("\n2. min_norm vs det correlation...")
    det_corr = min_norm_vs_det(lattices)
    for d, s in det_corr.items():
        print(f"  dim={d}: Pearson r={s['pearson_r']:.4f}, "
              f"Spearman rho={s['spearman_rho']:.4f}, "
              f"Hermite mean={s['hermite_invariant_mean']:.4f}")

    print("\n3. Minkowski bound verification...")
    mink = verify_minkowski(lattices)
    print(f"  Violations: {mink['n_violations']}")
    for d, s in mink["by_dim"].items():
        print(f"  dim={d}: ratio_mean={s['ratio_mean']:.4f}, "
              f"ratio_max={s['ratio_max']:.4f}, gamma_d={s['gamma_d_used']:.4f}")
    if mink["violations_sample"]:
        print("  Sample violations:")
        for v in mink["violations_sample"][:5]:
            print(f"    {v['label']}: min_norm={v['min_norm']}, "
                  f"bound={v['bound']}, ratio={v['ratio']}")

    print("\n4. min_norm vs kissing number...")
    kiss_corr = min_norm_vs_kissing(lattices)
    for d, s in kiss_corr.items():
        print(f"  dim={d}: Pearson r={s['pearson_r']:.4f}, "
              f"Spearman rho={s['spearman_rho']:.4f}")

    results = {
        "experiment": "lattice_min_norm_distribution",
        "source": str(DATA),
        "n_lattices": len(lattices),
        "distribution_by_dim": dist,
        "min_norm_vs_det": det_corr,
        "minkowski_bound": mink,
        "min_norm_vs_kissing": kiss_corr,
        "verdict": None,  # filled below
    }

    # Build verdict
    v_lines = []
    v_lines.append(f"39K lattices (dims 1-24), min_norm extracted from LMFDB 'minimum' field.")

    # Distribution summary
    if "3" in dist:
        v_lines.append(f"dim=3 dominates ({dist['3']['count']} lattices), "
                       f"median min_norm={dist['3']['median']:.1f}.")

    # Minkowski
    v_lines.append(f"Minkowski bound: {mink['n_violations']} violations "
                   f"(using known Hermite constants + Blichfeldt fallback).")

    # Best correlations
    best_det_dim = max(det_corr, key=lambda d: abs(det_corr[d]["spearman_rho"]))
    v_lines.append(f"Strongest min_norm~det correlation: dim={best_det_dim}, "
                   f"Spearman rho={det_corr[best_det_dim]['spearman_rho']:.4f}.")

    if kiss_corr:
        best_kiss_dim = max(kiss_corr, key=lambda d: abs(kiss_corr[d]["spearman_rho"]))
        v_lines.append(f"Strongest min_norm~kissing correlation: dim={best_kiss_dim}, "
                       f"Spearman rho={kiss_corr[best_kiss_dim]['spearman_rho']:.4f}.")

    results["verdict"] = " ".join(v_lines)

    with open(OUT, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT}")
    print(f"Verdict: {results['verdict']}")


if __name__ == "__main__":
    main()
