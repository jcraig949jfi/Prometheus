"""
Genus-2 Bad Reduction Type Distribution by Sato-Tate Group
==========================================================
Factorize conductors, extract bad reduction statistics, test whether
these statistics distinguish the 6 abelian-surface ST groups (those with
extra endomorphisms), and compute MI between bad-reduction features and
ST group.
"""

import json
import math
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime


# ── helpers ──────────────────────────────────────────────────────────────

def factorize(n):
    """Return list of (prime, exponent) pairs."""
    if n <= 1:
        return []
    factors = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            exp = 0
            while n % d == 0:
                exp += 1
                n //= d
            factors.append((d, exp))
        d += 1
    if n > 1:
        factors.append((n, 1))
    return factors


def conductor_features(cond):
    """Extract bad-reduction statistics from conductor."""
    factors = factorize(cond)
    if not factors:
        return {
            "num_bad_primes": 0,
            "max_exponent": 0,
            "total_exponent": 0,
            "max_prime": 1,
            "min_prime": 1,
            "log_conductor": 0.0,
            "exponent_vector": [],
        }
    primes = [p for p, _ in factors]
    exponents = [e for _, e in factors]
    return {
        "num_bad_primes": len(factors),
        "max_exponent": max(exponents),
        "total_exponent": sum(exponents),
        "max_prime": max(primes),
        "min_prime": min(primes),
        "log_conductor": math.log(cond),
        "exponent_vector": exponents,
    }


def mutual_information(x_labels, y_labels):
    """Compute MI(X;Y) in nats from two aligned label lists."""
    n = len(x_labels)
    if n == 0:
        return 0.0
    xy_counts = Counter(zip(x_labels, y_labels))
    x_counts = Counter(x_labels)
    y_counts = Counter(y_labels)
    mi = 0.0
    for (x, y), nxy in xy_counts.items():
        pxy = nxy / n
        px = x_counts[x] / n
        py = y_counts[y] / n
        if pxy > 0:
            mi += pxy * math.log(pxy / (px * py))
    return mi


def mi_null_distribution(x_labels, y_labels, n_perm=1000, rng=None):
    """Compute null distribution of MI under random permutations."""
    if rng is None:
        rng = np.random.default_rng(42)
    y_arr = np.array(y_labels)
    null_mis = []
    for _ in range(n_perm):
        perm = rng.permutation(len(y_arr))
        null_mis.append(mutual_information(x_labels, y_arr[perm].tolist()))
    return null_mis


def entropy(labels):
    """Shannon entropy in nats."""
    n = len(labels)
    if n == 0:
        return 0.0
    counts = Counter(labels)
    h = 0.0
    for c in counts.values():
        p = c / n
        if p > 0:
            h -= p * math.log(p)
    return h


# ── The 6 abelian-surface ST groups with extra endomorphisms ─────────

ABELIAN_SURFACE_GROUPS = {"E_1", "E_2", "E_3", "E_4", "E_6", "J(E_1)", "J(E_2)", "J(E_3)", "J(E_4)", "J(E_6)"}

# ── main ─────────────────────────────────────────────────────────────

def main():
    data_path = Path("F:/Prometheus/cartography/genus2/data/genus2_curves_full.json")
    curves = json.loads(data_path.read_text())

    print(f"Loaded {len(curves)} genus-2 curves")

    # Compute features for every curve
    for c in curves:
        c["_feat"] = conductor_features(c["conductor"])

    # ── 1. Statistics by ST group ────────────────────────────────────
    st_groups = defaultdict(list)
    for c in curves:
        st_groups[c["st_group"]].append(c)

    group_stats = {}
    for st, group_curves in sorted(st_groups.items()):
        feats = [c["_feat"] for c in group_curves]
        n = len(feats)
        nbp = [f["num_bad_primes"] for f in feats]
        maxe = [f["max_exponent"] for f in feats]
        tote = [f["total_exponent"] for f in feats]
        logc = [f["log_conductor"] for f in feats]
        maxp = [f["max_prime"] for f in feats]
        minp = [f["min_prime"] for f in feats]

        group_stats[st] = {
            "count": n,
            "num_bad_primes": {
                "mean": float(np.mean(nbp)),
                "std": float(np.std(nbp)),
                "median": float(np.median(nbp)),
                "min": int(min(nbp)),
                "max": int(max(nbp)),
            },
            "max_exponent": {
                "mean": float(np.mean(maxe)),
                "std": float(np.std(maxe)),
                "median": float(np.median(maxe)),
            },
            "total_exponent": {
                "mean": float(np.mean(tote)),
                "std": float(np.std(tote)),
                "median": float(np.median(tote)),
            },
            "log_conductor": {
                "mean": float(np.mean(logc)),
                "std": float(np.std(logc)),
            },
            "max_prime": {
                "mean": float(np.mean(maxp)),
                "median": float(np.median(maxp)),
            },
            "min_prime": {
                "mean": float(np.mean(minp)),
                "median": float(np.median(minp)),
            },
        }

    print("\n=== Bad Reduction Statistics by ST Group ===")
    for st, s in sorted(group_stats.items(), key=lambda x: -x[1]["count"]):
        print(f"\n{st} (n={s['count']}):")
        print(f"  num_bad_primes:  mean={s['num_bad_primes']['mean']:.2f}  std={s['num_bad_primes']['std']:.2f}  median={s['num_bad_primes']['median']:.0f}")
        print(f"  max_exponent:    mean={s['max_exponent']['mean']:.2f}  std={s['max_exponent']['std']:.2f}")
        print(f"  total_exponent:  mean={s['total_exponent']['mean']:.2f}  std={s['total_exponent']['std']:.2f}")
        print(f"  log_conductor:   mean={s['log_conductor']['mean']:.2f}")
        print(f"  min_prime:       median={s['min_prime']['median']:.0f}")

    # ── 2. Discretize features for MI ────────────────────────────────
    # Use binned num_bad_primes and max_exponent as joint feature
    def discretize_curve(c):
        f = c["_feat"]
        nbp = min(f["num_bad_primes"], 8)  # cap at 8
        maxe = min(f["max_exponent"], 10)   # cap at 10
        return f"{nbp}_{maxe}"

    feat_labels = [discretize_curve(c) for c in curves]
    st_labels = [c["st_group"] for c in curves]

    mi_val = mutual_information(feat_labels, st_labels)
    h_st = entropy(st_labels)
    h_feat = entropy(feat_labels)
    nmi = mi_val / h_st if h_st > 0 else 0.0

    print(f"\n=== Mutual Information ===")
    print(f"MI(bad_reduction_features, ST_group) = {mi_val:.4f} nats")
    print(f"H(ST_group) = {h_st:.4f} nats")
    print(f"H(features) = {h_feat:.4f} nats")
    print(f"NMI = MI/H(ST) = {nmi:.4f}")

    # Null distribution
    null_mis = mi_null_distribution(feat_labels, st_labels, n_perm=1000)
    null_mean = float(np.mean(null_mis))
    null_std = float(np.std(null_mis))
    z_score = (mi_val - null_mean) / null_std if null_std > 0 else 0.0

    print(f"Null MI: mean={null_mean:.6f}, std={null_std:.6f}")
    print(f"z-score = {z_score:.1f}")

    # ── 3. Abelian surface groups distinguishability ─────────────────
    abelian_curves = [c for c in curves if c["st_group"] in ABELIAN_SURFACE_GROUPS]
    print(f"\n=== Abelian Surface Groups (extra endomorphisms) ===")
    print(f"Total curves in abelian-surface groups: {len(abelian_curves)}")

    ab_feat_labels = [discretize_curve(c) for c in abelian_curves]
    ab_st_labels = [c["st_group"] for c in abelian_curves]

    ab_mi = mutual_information(ab_feat_labels, ab_st_labels)
    ab_h_st = entropy(ab_st_labels)
    ab_nmi = ab_mi / ab_h_st if ab_h_st > 0 else 0.0

    print(f"MI(features, ST) = {ab_mi:.4f} nats")
    print(f"H(ST) = {ab_h_st:.4f} nats")
    print(f"NMI = {ab_nmi:.4f}")

    ab_null = mi_null_distribution(ab_feat_labels, ab_st_labels, n_perm=1000)
    ab_null_mean = float(np.mean(ab_null))
    ab_null_std = float(np.std(ab_null))
    ab_z = (ab_mi - ab_null_mean) / ab_null_std if ab_null_std > 0 else 0.0
    print(f"Null MI: mean={ab_null_mean:.6f}, std={ab_null_std:.6f}")
    print(f"z-score = {ab_z:.1f}")

    # Per-group feature distributions for abelian groups
    abelian_group_stats = {}
    for st in sorted(ABELIAN_SURFACE_GROUPS):
        gcurves = [c for c in abelian_curves if c["st_group"] == st]
        if not gcurves:
            continue
        feats = [c["_feat"] for c in gcurves]
        nbp = [f["num_bad_primes"] for f in feats]
        maxe = [f["max_exponent"] for f in feats]
        tote = [f["total_exponent"] for f in feats]
        # Exponent distribution
        exp_dist = Counter()
        for f in feats:
            for e in f["exponent_vector"]:
                exp_dist[e] += 1
        total_exp_entries = sum(exp_dist.values())
        exp_frac = {str(k): round(v / total_exp_entries, 3) for k, v in sorted(exp_dist.items())} if total_exp_entries > 0 else {}

        abelian_group_stats[st] = {
            "count": len(gcurves),
            "num_bad_primes_mean": round(float(np.mean(nbp)), 2),
            "max_exponent_mean": round(float(np.mean(maxe)), 2),
            "total_exponent_mean": round(float(np.mean(tote)), 2),
            "exponent_distribution": exp_frac,
        }
        print(f"\n  {st} (n={len(gcurves)}):")
        print(f"    num_bad_primes mean={np.mean(nbp):.2f}, max_exp mean={np.mean(maxe):.2f}")
        print(f"    exponent dist: {exp_frac}")

    # ── 4. Comparison to EC ──────────────────────────────────────────
    # For EC, the ST group is always USp(2) for non-CM, and there are
    # only 2 classes. Bad reduction in EC: additive vs multiplicative
    # (determined by conductor exponent: 1=multiplicative, >=2=additive).
    # For genus-2, we have 20 ST groups with more varied conductor structure.

    # Simulate EC comparison: compute MI for "is_generic" (USp(4) vs rest)
    binary_labels = ["USp(4)" if c["st_group"] == "USp(4)" else "non-generic" for c in curves]
    mi_binary = mutual_information(feat_labels, binary_labels)
    h_binary = entropy(binary_labels)
    nmi_binary = mi_binary / h_binary if h_binary > 0 else 0.0

    print(f"\n=== EC Comparison (generic vs non-generic) ===")
    print(f"MI(features, generic_vs_not) = {mi_binary:.4f} nats")
    print(f"H(binary_label) = {h_binary:.4f} nats")
    print(f"NMI = {nmi_binary:.4f}")

    # Also: what fraction of conductor exponents are 1 (multiplicative-like)
    # vs >=2 (additive-like) by ST group
    reduction_type_by_st = {}
    for st, gcurves in st_groups.items():
        mult_count = 0
        add_count = 0
        for c in gcurves:
            factors = factorize(c["conductor"])
            for p, e in factors:
                if e == 1:
                    mult_count += 1
                else:
                    add_count += 1
        total = mult_count + add_count
        reduction_type_by_st[st] = {
            "multiplicative_frac": round(mult_count / total, 3) if total > 0 else 0,
            "additive_frac": round(add_count / total, 3) if total > 0 else 0,
            "total_bad_primes": total,
        }

    print(f"\n=== Reduction Type Fractions by ST Group ===")
    for st in sorted(reduction_type_by_st.keys()):
        r = reduction_type_by_st[st]
        print(f"  {st}: mult={r['multiplicative_frac']:.3f}  add={r['additive_frac']:.3f}  (n={r['total_bad_primes']})")

    # ── 5. Build results ─────────────────────────────────────────────
    results = {
        "experiment": "genus2_bad_reduction_type_distribution",
        "description": "Bad reduction statistics by Sato-Tate group for genus-2 curves",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "source": "genus2_curves_full.json",
            "n_curves": len(curves),
            "n_st_groups": len(st_groups),
            "conductor_range": [min(c["conductor"] for c in curves), max(c["conductor"] for c in curves)],
        },
        "group_statistics": group_stats,
        "mutual_information": {
            "full_dataset": {
                "MI_nats": round(mi_val, 6),
                "H_ST": round(h_st, 4),
                "H_features": round(h_feat, 4),
                "NMI": round(nmi, 4),
                "null_mean": round(null_mean, 6),
                "null_std": round(null_std, 6),
                "z_score": round(z_score, 1),
                "significant": z_score > 3.0,
            },
            "abelian_surface_groups": {
                "n_curves": len(abelian_curves),
                "groups_present": sorted([st for st in ABELIAN_SURFACE_GROUPS if st in st_groups]),
                "MI_nats": round(ab_mi, 6),
                "H_ST": round(ab_h_st, 4),
                "NMI": round(ab_nmi, 4),
                "null_mean": round(ab_null_mean, 6),
                "null_std": round(ab_null_std, 6),
                "z_score": round(ab_z, 1),
                "significant": ab_z > 3.0,
                "per_group_stats": abelian_group_stats,
            },
            "generic_vs_nongeneric": {
                "MI_nats": round(mi_binary, 6),
                "H_binary": round(h_binary, 4),
                "NMI": round(nmi_binary, 4),
            },
        },
        "reduction_type_fractions": reduction_type_by_st,
        "ec_comparison": {
            "note": "In EC, bad reduction type (mult vs additive) is read from conductor exponent (1=mult, >=2=add). "
                    "For genus-2, conductor exponents encode more complex reduction types. "
                    "The NMI of bad-reduction features vs ST group measures how informative these features are.",
            "genus2_NMI_full": round(nmi, 4),
            "genus2_NMI_binary": round(nmi_binary, 4),
            "genus2_z_score": round(z_score, 1),
            "interpretation": (
                "HIGH" if nmi > 0.05 else "MODERATE" if nmi > 0.01 else "LOW"
            ) + f" informativeness (NMI={nmi:.4f}). "
              + ("Bad reduction features significantly distinguish ST groups. " if z_score > 3 else "Weak or no significant signal. ")
              + f"For the {len(abelian_curves)} abelian-surface curves, "
              + ("bad reduction IS distinguishing" if ab_z > 3 else "bad reduction is NOT sufficient to distinguish")
              + f" (z={ab_z:.1f}).",
        },
        "verdict": {
            "distinguishable_by_bad_reduction": z_score > 3.0,
            "abelian_groups_distinguishable": ab_z > 3.0,
            "z_score_full": round(z_score, 1),
            "z_score_abelian": round(ab_z, 1),
        },
    }

    out_path = Path("F:/Prometheus/cartography/v2/genus2_bad_reduction_results.json")
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
