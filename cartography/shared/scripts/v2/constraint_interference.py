#!/usr/bin/env python3
"""
Constraint Interference Patterns (Challenge C10.5)
===================================================
Test whether mod-ell constraints INTERFERE destructively or constructively.

For each pair of primes (ell_1, ell_2) in {3,5,7,11}:
  - N_1 = forms in non-trivial clusters at ell_1
  - N_2 = forms in non-trivial clusters at ell_2
  - N_12 = forms in non-trivial clusters at BOTH
  - Expected N_12 = N_1 * N_2 / N_total (independence)
  - Ratio = N_12 / expected  (>1 constructive, <1 destructive)

Also tests:
  - Relaxed matching (Hamming distance <= 2)
  - Cross-type interference (fingerprint x conductor, x Galois image, x starvation)

Charon / Project Prometheus — 2026-04-09
"""

import json
import math
import sys
import time
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import duckdb
import numpy as np

# ── Config ──────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[4]  # F:\Prometheus
DB_PATH = REPO_ROOT / "charon" / "data" / "charon.duckdb"
GALOIS_PATH = Path(__file__).resolve().parent / "galois_image_results.json"
STARVATION_PATH = Path(__file__).resolve().parent / "residue_starvation_results.json"
OUT_PATH = Path(__file__).resolve().parent / "constraint_interference_results.json"

PRIMES_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
             31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
             73, 79, 83, 89, 97]

ELLS = [3, 5, 7, 11]
ELL_PAIRS = list(combinations(ELLS, 2))


# ── Helpers ──────────────────────────────────────────────────────────

def prime_factors(n):
    """Return set of prime factors of n."""
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors


def is_squarefree(n):
    d = 2
    while d * d <= n:
        if n % (d * d) == 0:
            return False
        d += 1
    return True


def compute_fingerprint(traces, level, ell):
    """Compute mod-ell fingerprint vector at 25 primes. Bad primes -> -1."""
    bad_primes = prime_factors(level)
    fp = []
    for p in PRIMES_25:
        if p in bad_primes:
            fp.append(-1)
        else:
            if p - 1 < len(traces):
                ap = int(round(traces[p - 1]))
                fp.append(ap % ell)
            else:
                fp.append(-1)
    return tuple(fp)


def hamming_distance(fp1, fp2):
    """Hamming distance ignoring positions where either is -1 (bad prime)."""
    dist = 0
    compared = 0
    for a, b in zip(fp1, fp2):
        if a == -1 or b == -1:
            continue
        compared += 1
        if a != b:
            dist += 1
    return dist, compared


def log_comb(n, k):
    if k < 0 or k > n:
        return -float('inf')
    if k == 0 or k == n:
        return 0.0
    k = min(k, n - k)
    return sum(math.log(n - i) - math.log(i + 1) for i in range(k))


def hypergeometric_sf(k, N, K, n):
    """P(X >= k) for hypergeometric(N, K, n)."""
    upper = min(K, n)
    if k > upper:
        return 0.0
    if k <= 0:
        return 1.0
    p_total = 0.0
    for j in range(k, upper + 1):
        lp = log_comb(K, j) + log_comb(N - K, n - j) - log_comb(N, n)
        p_total += math.exp(lp) if lp > -700 else 0.0
    return min(p_total, 1.0)


# ── Data loading ─────────────────────────────────────────────────────

def load_forms():
    """Load all dim-1 weight-2 newforms with metadata."""
    print(f"[load] Connecting to {DB_PATH}")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    rows = con.execute('''
        SELECT lmfdb_label, level, traces, fricke_eigenval, is_cm
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND traces IS NOT NULL
        ORDER BY level, lmfdb_label
    ''').fetchall()
    con.close()
    print(f"[load] {len(rows)} forms loaded")

    forms = []
    for label, level, traces, fricke, is_cm in rows:
        forms.append({
            'label': label,
            'level': int(level),
            'traces': traces,
            'fricke': fricke,
            'is_cm': bool(is_cm) if is_cm is not None else False,
        })
    return forms


def load_galois_classes():
    """Load per-form combined Galois image classification."""
    print(f"[load] Loading Galois image from {GALOIS_PATH}")
    with open(GALOIS_PATH) as f:
        data = json.load(f)
    label_to_class = {}
    for s in data.get("sample_classifications", []):
        label_to_class[s["label"]] = s["combined_class"]
    print(f"[load] {len(label_to_class)} Galois classifications")
    return label_to_class


def load_starvation_labels():
    """Load non-CM starved form labels."""
    print(f"[load] Loading starvation from {STARVATION_PATH}")
    with open(STARVATION_PATH) as f:
        data = json.load(f)
    noncm_starved = set()
    for form in data.get("starved_forms", []):
        if form.get("flag", "").startswith("NON-CM"):
            noncm_starved.add(form["label"])
    print(f"[load] {len(noncm_starved)} non-CM starved forms")
    return noncm_starved


# ── Part 1: Exact fingerprint interference ───────────────────────────

def cluster_forms_by_ell(forms, ell):
    """Return dict: fingerprint -> set of labels."""
    clusters = defaultdict(set)
    for form in forms:
        fp = compute_fingerprint(form['traces'], form['level'], ell)
        clusters[fp].add(form['label'])
    return dict(clusters)


def nontrivial_labels(clusters):
    """Set of labels in clusters of size >= 2."""
    result = set()
    for fp, labels in clusters.items():
        if len(labels) >= 2:
            result.update(labels)
    return result


def compute_exact_interference(forms):
    """
    For each pair (ell_1, ell_2), compute interference ratio.
    """
    N = len(forms)
    print(f"\n{'='*60}")
    print(f"PART 1: EXACT FINGERPRINT INTERFERENCE (N={N})")
    print(f"{'='*60}")

    # Cluster at each ell
    ell_clusters = {}
    ell_nontrivial = {}
    for ell in ELLS:
        clusters = cluster_forms_by_ell(forms, ell)
        nt = nontrivial_labels(clusters)
        ell_clusters[ell] = clusters
        ell_nontrivial[ell] = nt
        print(f"  ell={ell:2d}: {len(nt):5d} forms in non-trivial clusters "
              f"({100*len(nt)/N:.1f}%)")

    results = {}
    for ell1, ell2 in ELL_PAIRS:
        N1 = len(ell_nontrivial[ell1])
        N2 = len(ell_nontrivial[ell2])
        N12 = len(ell_nontrivial[ell1] & ell_nontrivial[ell2])
        expected = N1 * N2 / N if N > 0 else 0
        ratio = N12 / expected if expected > 0 else float('inf')

        # Hypergeometric p-value for enrichment
        p_val = hypergeometric_sf(N12, N, N1, N2)

        key = f"{ell1}x{ell2}"
        results[key] = {
            "ell_1": ell1,
            "ell_2": ell2,
            "N_1": N1,
            "N_2": N2,
            "N_12_observed": N12,
            "N_12_expected": round(expected, 2),
            "ratio": round(ratio, 6),
            "interference": "constructive" if ratio > 1.05 else
                           "destructive" if ratio < 0.95 else "independent",
            "hypergeometric_p": p_val,
        }
        tag = results[key]["interference"].upper()
        print(f"  {ell1}x{ell2}: N12={N12}, expected={expected:.1f}, "
              f"ratio={ratio:.4f} [{tag}]  p={p_val:.2e}")

    return results, ell_clusters, ell_nontrivial


# ── Part 2: Relaxed matching (Hamming distance <= threshold) ─────────

def relaxed_nontrivial(forms, ell, max_hamming=2, sample_limit=5000):
    """
    Find forms that have at least one near-neighbor (Hamming dist <= max_hamming)
    among other forms. Uses sampling for efficiency.
    """
    # Build fingerprints
    fps = []
    for form in forms:
        fp = compute_fingerprint(form['traces'], form['level'], ell)
        fps.append((form['label'], fp))

    # Exact cluster first (all pairs within exact clusters are dist 0)
    clusters = defaultdict(list)
    for label, fp in fps:
        clusters[fp].append(label)

    # Forms already in exact non-trivial clusters
    exact_nt = set()
    for fp, labels in clusters.items():
        if len(labels) >= 2:
            exact_nt.update(labels)

    # For near-miss detection: sample pairs from singletons
    singletons = [(label, fp) for label, fp in fps
                  if len(clusters[fps[0][1] if False else fp]) == 1]
    # Actually get singletons properly
    singleton_set = set()
    for fp, labels in clusters.items():
        if len(labels) == 1:
            singleton_set.add(labels[0])

    singleton_fps = [(label, fp) for label, fp in fps if label in singleton_set]

    # Sample pairs from singletons to find near-misses
    rng = np.random.default_rng(42)
    n_sing = len(singleton_fps)
    near_miss_labels = set()

    if n_sing > 1:
        n_pairs = min(sample_limit, n_sing * (n_sing - 1) // 2)
        for _ in range(n_pairs):
            i, j = rng.choice(n_sing, size=2, replace=False)
            d, comp = hamming_distance(singleton_fps[i][1], singleton_fps[j][1])
            if comp > 0 and d <= max_hamming:
                near_miss_labels.add(singleton_fps[i][0])
                near_miss_labels.add(singleton_fps[j][0])

    # Also check singletons against cluster representatives
    cluster_reps = [(fp, labels) for fp, labels in clusters.items()
                    if len(labels) >= 2]
    for label, fp_s in singleton_fps[:2000]:  # limit for speed
        for fp_c, _ in cluster_reps:
            d, comp = hamming_distance(fp_s, fp_c)
            if comp > 0 and d <= max_hamming:
                near_miss_labels.add(label)
                break

    relaxed_nt = exact_nt | near_miss_labels
    return relaxed_nt, len(exact_nt), len(near_miss_labels)


def compute_relaxed_interference(forms):
    """
    Relaxed matching: Hamming distance <= 2.
    """
    N = len(forms)
    print(f"\n{'='*60}")
    print(f"PART 2: RELAXED MATCHING INTERFERENCE (Hamming <= 2)")
    print(f"{'='*60}")

    ell_relaxed = {}
    for ell in ELLS:
        relaxed, n_exact, n_near = relaxed_nontrivial(forms, ell, max_hamming=2)
        ell_relaxed[ell] = relaxed
        print(f"  ell={ell:2d}: {len(relaxed):5d} relaxed non-trivial "
              f"(exact={n_exact}, near-miss={n_near})")

    results = {}
    for ell1, ell2 in ELL_PAIRS:
        N1 = len(ell_relaxed[ell1])
        N2 = len(ell_relaxed[ell2])
        N12 = len(ell_relaxed[ell1] & ell_relaxed[ell2])
        expected = N1 * N2 / N if N > 0 else 0
        ratio = N12 / expected if expected > 0 else float('inf')

        key = f"{ell1}x{ell2}"
        results[key] = {
            "ell_1": ell1,
            "ell_2": ell2,
            "N_1_relaxed": N1,
            "N_2_relaxed": N2,
            "N_12_observed": N12,
            "N_12_expected": round(expected, 2),
            "ratio": round(ratio, 6),
            "interference": "constructive" if ratio > 1.05 else
                           "destructive" if ratio < 0.95 else "independent",
        }
        tag = results[key]["interference"].upper()
        print(f"  {ell1}x{ell2}: N12={N12}, expected={expected:.1f}, "
              f"ratio={ratio:.4f} [{tag}]")

    return results


# ── Part 3: Cross-type interference ──────────────────────────────────

def compute_cross_type_interference(forms, ell_nontrivial,
                                     galois_classes, starved_labels):
    """
    Test interference between mod-p fingerprint and other constraint types:
      - conductor range (level < 1000)
      - Galois image class
      - starvation status
    """
    N = len(forms)
    print(f"\n{'='*60}")
    print(f"PART 3: CROSS-TYPE INTERFERENCE")
    print(f"{'='*60}")

    all_labels = {f['label'] for f in forms}
    label_level = {f['label']: f['level'] for f in forms}

    # Define binary constraints
    constraints = {}

    # C1: low conductor (level < 1000)
    low_cond = {f['label'] for f in forms if f['level'] < 1000}
    constraints["low_conductor"] = low_cond

    # C2: high conductor (level >= 5000)
    high_cond = {f['label'] for f in forms if f['level'] >= 5000}
    constraints["high_conductor"] = high_cond

    # C3: Galois image = full
    full_galois = {lbl for lbl, cls in galois_classes.items()
                   if cls == "full_image" and lbl in all_labels}
    constraints["galois_full"] = full_galois

    # C4: Galois image = borel (any mod)
    borel_galois = {lbl for lbl, cls in galois_classes.items()
                    if "borel" in cls and lbl in all_labels}
    constraints["galois_borel"] = borel_galois

    # C5: non-CM starved
    starved_in_data = starved_labels & all_labels
    constraints["starved_noncm"] = starved_in_data

    # C6: CM forms
    cm_forms = {f['label'] for f in forms if f['is_cm']}
    constraints["is_cm"] = cm_forms

    # C7: squarefree level
    sqfree = {f['label'] for f in forms if is_squarefree(f['level'])}
    constraints["squarefree_level"] = sqfree

    # C8: fricke = +1
    fricke_plus = {f['label'] for f in forms if f['fricke'] == 1}
    constraints["fricke_plus"] = fricke_plus

    results = {}

    for cname, c_labels in constraints.items():
        Nc = len(c_labels)
        if Nc < 10:
            continue

        for ell in ELLS:
            Nell = len(ell_nontrivial[ell])
            overlap = len(c_labels & ell_nontrivial[ell])
            expected = Nc * Nell / N if N > 0 else 0
            ratio = overlap / expected if expected > 0 else float('inf')

            key = f"mod{ell}_x_{cname}"
            results[key] = {
                "ell": ell,
                "constraint": cname,
                "N_ell": Nell,
                "N_constraint": Nc,
                "N_overlap": overlap,
                "N_expected": round(expected, 2),
                "ratio": round(ratio, 6),
                "interference": "constructive" if ratio > 1.05 else
                               "destructive" if ratio < 0.95 else "independent",
            }

    # Print summary: strongest interference
    print(f"\n  {'Combination':<35s} {'Ratio':>8s} {'Type':>14s} "
          f"{'N_overlap':>9s} {'N_expected':>10s}")
    print(f"  {'-'*35} {'-'*8} {'-'*14} {'-'*9} {'-'*10}")

    sorted_results = sorted(results.items(),
                            key=lambda x: abs(x[1]["ratio"] - 1), reverse=True)
    for key, v in sorted_results:
        tag = v["interference"].upper()
        print(f"  {key:<35s} {v['ratio']:8.4f} {tag:>14s} "
              f"{v['N_overlap']:9d} {v['N_expected']:10.1f}")

    return results


# ── Part 4: Cluster-size distribution interference ───────────────────

def compute_cluster_size_interference(forms, ell_clusters):
    """
    Instead of just binary (in/out of non-trivial cluster), look at
    whether forms in LARGE clusters at ell_1 are enriched in large
    clusters at ell_2.
    """
    N = len(forms)
    print(f"\n{'='*60}")
    print(f"PART 4: CLUSTER SIZE CORRELATION")
    print(f"{'='*60}")

    # For each ell, assign each form its cluster size
    ell_sizes = {}
    for ell in ELLS:
        label_size = {}
        for fp, labels in ell_clusters[ell].items():
            sz = len(labels)
            for lbl in labels:
                label_size[lbl] = sz
        ell_sizes[ell] = label_size

    # For each pair, compute Spearman correlation of cluster sizes
    results = {}
    all_labels = [f['label'] for f in forms]

    for ell1, ell2 in ELL_PAIRS:
        sizes1 = np.array([ell_sizes[ell1].get(lbl, 1) for lbl in all_labels],
                         dtype=float)
        sizes2 = np.array([ell_sizes[ell2].get(lbl, 1) for lbl in all_labels],
                         dtype=float)

        # Spearman rank correlation
        from scipy.stats import spearmanr
        rho, pval = spearmanr(sizes1, sizes2)

        # Also check: forms in top-10% cluster at ell1 vs ell2
        thresh1 = np.percentile(sizes1, 90)
        thresh2 = np.percentile(sizes2, 90)
        top1 = set(lbl for lbl, s in zip(all_labels, sizes1) if s >= max(thresh1, 2))
        top2 = set(lbl for lbl, s in zip(all_labels, sizes2) if s >= max(thresh2, 2))
        n_top1 = len(top1)
        n_top2 = len(top2)
        n_both = len(top1 & top2)
        expected_both = n_top1 * n_top2 / N if N > 0 else 0
        top_ratio = n_both / expected_both if expected_both > 0 else float('inf')

        key = f"{ell1}x{ell2}"
        results[key] = {
            "ell_1": ell1,
            "ell_2": ell2,
            "spearman_rho": round(rho, 6),
            "spearman_p": pval,
            "top10pct_ell1": n_top1,
            "top10pct_ell2": n_top2,
            "top10pct_both": n_both,
            "top10pct_expected": round(expected_both, 2),
            "top10pct_ratio": round(top_ratio, 4),
        }
        print(f"  {ell1}x{ell2}: Spearman rho={rho:.4f} (p={pval:.2e}), "
              f"top-10% ratio={top_ratio:.4f}")

    return results


# ── Part 5: Conductor-conditioned ell-pair interference ──────────────

def compute_conductor_conditioned(forms, ell_nontrivial):
    """
    Does interference change when we condition on conductor range?
    Slice forms into conductor bins and recompute interference within each.
    """
    N = len(forms)
    print(f"\n{'='*60}")
    print(f"PART 5: CONDUCTOR-CONDITIONED INTERFERENCE")
    print(f"{'='*60}")

    bins = [
        ("N<500", lambda f: f['level'] < 500),
        ("500<=N<2000", lambda f: 500 <= f['level'] < 2000),
        ("2000<=N<5000", lambda f: 2000 <= f['level'] < 5000),
        ("N>=5000", lambda f: f['level'] >= 5000),
    ]

    results = {}
    for bin_name, pred in bins:
        subset = [f for f in forms if pred(f)]
        Nsub = len(subset)
        if Nsub < 50:
            continue

        # Recluster within this subset
        sub_nt = {}
        for ell in ELLS:
            clusters = cluster_forms_by_ell(subset, ell)
            sub_nt[ell] = nontrivial_labels(clusters)

        for ell1, ell2 in ELL_PAIRS:
            N1 = len(sub_nt[ell1])
            N2 = len(sub_nt[ell2])
            N12 = len(sub_nt[ell1] & sub_nt[ell2])
            expected = N1 * N2 / Nsub if Nsub > 0 else 0
            ratio = N12 / expected if expected > 0 else float('inf')

            key = f"{bin_name}_{ell1}x{ell2}"
            results[key] = {
                "bin": bin_name,
                "ell_1": ell1,
                "ell_2": ell2,
                "N_subset": Nsub,
                "N_1": N1,
                "N_2": N2,
                "N_12": N12,
                "expected": round(expected, 2),
                "ratio": round(ratio, 4) if expected > 0 else None,
            }

        # Print summary for this bin
        print(f"\n  {bin_name} (N={Nsub}):")
        for ell1, ell2 in ELL_PAIRS:
            k = f"{bin_name}_{ell1}x{ell2}"
            r = results[k]
            tag = ("CONSTRUCTIVE" if r['ratio'] and r['ratio'] > 1.05 else
                   "DESTRUCTIVE" if r['ratio'] and r['ratio'] < 0.95 else
                   "INDEPENDENT") if r['ratio'] else "N/A"
            print(f"    {ell1}x{ell2}: ratio={r['ratio']}  [{tag}]")

    return results


# ── Main ─────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    forms = load_forms()
    N = len(forms)

    # Load auxiliary data
    try:
        galois_classes = load_galois_classes()
    except Exception as e:
        print(f"[warn] Could not load Galois classes: {e}")
        galois_classes = {}

    try:
        starved_labels = load_starvation_labels()
    except Exception as e:
        print(f"[warn] Could not load starvation data: {e}")
        starved_labels = set()

    # Part 1: Exact fingerprint interference
    exact_results, ell_clusters, ell_nontrivial = compute_exact_interference(forms)

    # Part 2: Relaxed matching interference
    relaxed_results = compute_relaxed_interference(forms)

    # Part 3: Cross-type interference
    cross_type_results = compute_cross_type_interference(
        forms, ell_nontrivial, galois_classes, starved_labels)

    # Part 4: Cluster size correlation
    size_corr_results = compute_cluster_size_interference(forms, ell_clusters)

    # Part 5: Conductor-conditioned
    cond_results = compute_conductor_conditioned(forms, ell_nontrivial)

    elapsed = time.time() - t0

    # ── Synthesis ────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"SYNTHESIS")
    print(f"{'='*60}")

    # Find strongest interference
    all_exact_ratios = {k: v["ratio"] for k, v in exact_results.items()}
    strongest_exact = max(all_exact_ratios.items(),
                         key=lambda x: abs(x[1] - 1))
    print(f"  Strongest exact pair interference: {strongest_exact[0]} "
          f"ratio={strongest_exact[1]:.4f}")

    all_cross = {k: v["ratio"] for k, v in cross_type_results.items()}
    if all_cross:
        strongest_cross = max(all_cross.items(),
                             key=lambda x: abs(x[1] - 1))
        print(f"  Strongest cross-type interference: {strongest_cross[0]} "
              f"ratio={strongest_cross[1]:.4f}")

    # Determine overall verdict
    max_departure = max(abs(r - 1) for r in all_exact_ratios.values())
    if max_departure < 0.1:
        verdict = "Near-independence confirmed: all exact pair ratios within 10% of 1.0"
    elif max_departure < 0.3:
        verdict = "Weak interference detected: some pairs deviate 10-30% from independence"
    else:
        verdict = "Strong interference detected: pairs deviate >30% from independence"

    print(f"\n  VERDICT: {verdict}")

    # ── Save results ─────────────────────────────────────────────────
    output = {
        "metadata": {
            "n_forms": N,
            "ells": ELLS,
            "ell_pairs": [list(p) for p in ELL_PAIRS],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "elapsed_seconds": round(elapsed, 2),
        },
        "exact_interference": exact_results,
        "relaxed_interference": relaxed_results,
        "cross_type_interference": cross_type_results,
        "cluster_size_correlation": size_corr_results,
        "conductor_conditioned": cond_results,
        "synthesis": {
            "strongest_exact_pair": strongest_exact[0],
            "strongest_exact_ratio": strongest_exact[1],
            "strongest_cross_type": strongest_cross[0] if all_cross else None,
            "strongest_cross_ratio": strongest_cross[1] if all_cross else None,
            "max_departure_from_independence": round(max_departure, 4),
            "verdict": verdict,
        }
    }

    # Convert any numpy/special types for JSON
    def convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return str(obj)
        return obj

    def deep_convert(obj):
        if isinstance(obj, dict):
            return {k: deep_convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [deep_convert(v) for v in obj]
        return convert(obj)

    output = deep_convert(output)

    with open(OUT_PATH, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n[save] Results written to {OUT_PATH}")
    print(f"[done] Total elapsed: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
