#!/usr/bin/env python3
"""
Cross-Level Lift Detection — Objects Sharing mod-p Structure but Differing Globally
====================================================================================
Within single-prime mod-p clusters, all forms share the same residual representation
but differ globally. This script probes what distinguishes lifts of the same mod-p
structure:

1. Top-10 mod-3 clusters: internal structure (conductor, Galois image, Fricke, rank)
2. Branching factor: how a mod-3 cluster splits when adding mod-5
3. Branching vs. representation type correlation
4. Twist pair analysis (4 depth-2 survivors from R3-10)
5. Lift diversity index: entropy of mod-q distribution within mod-p clusters

Charon / Project Prometheus — 2026-04-09
"""

import json
import math
import time
from collections import Counter, defaultdict
from pathlib import Path

import duckdb
import numpy as np

# ── Config ──────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[4]  # F:\Prometheus
DB_PATH = REPO_ROOT / "charon" / "data" / "charon.duckdb"
OUT_PATH = Path(__file__).resolve().parent / "cross_level_lift_results.json"
GALOIS_PATH = Path(__file__).resolve().parent / "galois_image_results.json"

PRIMES_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
             31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
             73, 79, 83, 89, 97]

ELLS = [3, 5, 7]

# Depth-2 survivors from R3-10
TWIST_PAIRS = [
    ("270.2.a.a", "4590.2.a.d"),
    ("270.2.a.d", "4590.2.a.r"),
    ("350.2.a.a", "3850.2.a.a"),
    ("350.2.a.e", "3850.2.a.z"),
]


def prime_factors(n):
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


def compute_fingerprint(traces, level, ell):
    """Mod-ell fingerprint vector: a_p mod ell for 25 primes, -1 for bad primes."""
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


def entropy(counts):
    """Shannon entropy from a Counter/dict of counts."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    ent = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            ent -= p * math.log2(p)
    return ent


def load_all_data():
    """Load forms + EC rank + Galois image classifications."""
    print("[load] Connecting to DuckDB...")
    con = duckdb.connect(str(DB_PATH), read_only=True)

    # Load modular forms
    rows = con.execute('''
        SELECT lmfdb_label, level, weight, dim, fricke_eigenval,
               is_cm, self_twist_type, traces, related_objects
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND traces IS NOT NULL
        ORDER BY level, lmfdb_label
    ''').fetchall()
    print(f"[load] {len(rows)} modular forms loaded")

    # Build label -> form data
    forms = {}
    for r in rows:
        label, level, weight, dim, fricke, is_cm, self_twist, traces, rel_objs = r
        forms[label] = {
            "level": level,
            "fricke": fricke,
            "is_cm": is_cm,
            "self_twist_type": self_twist,
            "traces": traces,
            "related_objects": rel_objs or [],
        }

    # Load EC data for analytic rank lookup
    ec_rows = con.execute('''
        SELECT lmfdb_label, conductor, analytic_rank, rank, cm, torsion
        FROM elliptic_curves
    ''').fetchall()
    print(f"[load] {len(ec_rows)} elliptic curves loaded")

    # Build EC iso-class lookup (e.g., "EllipticCurve/Q/11/a" -> rank info)
    ec_by_iso = {}
    for er in ec_rows:
        ec_label, cond, arank, rank, cm, torsion = er
        # Convert lmfdb_label like "11.a1" to iso path "EllipticCurve/Q/11/a"
        parts = ec_label.split(".")
        if len(parts) >= 2:
            # iso class: everything before the number suffix
            iso_letter = ''.join(c for c in parts[1] if c.isalpha())
            iso_path = f"EllipticCurve/Q/{parts[0]}/{iso_letter}"
            if iso_path not in ec_by_iso:
                ec_by_iso[iso_path] = {
                    "analytic_rank": arank,
                    "rank": rank,
                    "cm": cm,
                    "torsion": torsion,
                }

    con.close()

    # Link MF -> EC analytic rank
    linked = 0
    for label, fdata in forms.items():
        fdata["analytic_rank"] = None
        for ro in fdata["related_objects"]:
            if ro in ec_by_iso:
                fdata["analytic_rank"] = ec_by_iso[ro]["analytic_rank"]
                linked += 1
                break
    print(f"[load] {linked} forms linked to EC analytic rank")

    # Load Galois image classifications
    galois_classes = {}
    if GALOIS_PATH.exists():
        gdata = json.loads(GALOIS_PATH.read_text())
        if "combined_classification" in gdata:
            # Need per-form classification — check structure
            pass
        # Per-ell classification is aggregate; we need per-form data
        # Recompute from DB traces using the same logic as galois_image_portraits.py
    print(f"[load] Will compute Galois image from trace data directly")

    return forms


def classify_galois_image_mod_ell(traces, level, ell, n_primes=168):
    """
    Simplified Galois image classification at a single ell.
    Uses zero-frequency of a_p mod ell for good primes p up to ~997.
    Returns: 'full', 'borel', 'cartan', 'anomalous', 'norm_cartan'
    """
    bad_primes = prime_factors(level)
    zero_count = 0
    total = 0

    # Generate primes up to 997
    def sieve(limit):
        is_prime = [True] * (limit + 1)
        is_prime[0] = is_prime[1] = False
        for i in range(2, int(limit**0.5) + 1):
            if is_prime[i]:
                for j in range(i*i, limit + 1, i):
                    is_prime[j] = False
        return [i for i in range(2, limit + 1) if is_prime[i]]

    all_primes = sieve(997)

    for p in all_primes:
        if p in bad_primes:
            continue
        if p - 1 < len(traces):
            ap = int(round(traces[p - 1]))
            if ap % ell == 0:
                zero_count += 1
            total += 1

    if total < 30:
        return "insufficient_data"

    zero_freq = zero_count / total

    # Classification thresholds (from galois_image_portraits.py logic)
    if ell == 2:
        if zero_freq > 0.9:
            return "mod2_all_even"
        elif zero_freq > 0.4:
            return "borel"
        else:
            return "full"
    else:
        expected_full = 1.0 / ell
        expected_borel_qr = (1 + (ell - 1) / 2) / ell  # zero + QR classes
        expected_cartan = 0.5  # ~50% zero for CM forms

        if abs(zero_freq - expected_cartan) < 0.05 and ell >= 3:
            return "cartan"
        elif zero_freq > expected_full + 0.08:
            return "borel"
        elif zero_freq < expected_full - 0.05:
            return "anomalous"
        else:
            return "full"


def build_mod3_clusters(forms):
    """Build mod-3 clusters using exact fingerprint match (same as residual_rep_clustering)."""
    clusters = defaultdict(list)
    for label, fdata in forms.items():
        fp = compute_fingerprint(fdata["traces"], fdata["level"], 3)
        clusters[fp].append(label)

    # Sort clusters by size descending
    sorted_clusters = sorted(clusters.items(), key=lambda x: -len(x[1]))
    return sorted_clusters


def analyze_cluster_internals(cluster_labels, forms, cluster_fp):
    """Analyze the internal structure of a single mod-3 cluster."""
    n = len(cluster_labels)

    # Conductor/level distribution
    levels = [forms[l]["level"] for l in cluster_labels]
    level_counter = Counter(levels)

    # Fricke eigenvalue distribution
    fricke_vals = [forms[l]["fricke"] for l in cluster_labels if forms[l]["fricke"] is not None]
    fricke_counter = Counter(fricke_vals)

    # Analytic rank distribution
    ranks = [forms[l]["analytic_rank"] for l in cluster_labels if forms[l]["analytic_rank"] is not None]
    rank_counter = Counter(ranks)

    # CM distribution
    cm_vals = [forms[l]["is_cm"] for l in cluster_labels]
    cm_counter = Counter(cm_vals)

    # Galois image at ell=3
    galois_classes = []
    for l in cluster_labels:
        gc = classify_galois_image_mod_ell(forms[l]["traces"], forms[l]["level"], 3)
        galois_classes.append(gc)
    galois_counter = Counter(galois_classes)

    # Level statistics
    level_arr = np.array(levels)

    result = {
        "size": n,
        "fingerprint_summary": {
            "n_good_primes": sum(1 for x in cluster_fp if x != -1),
            "unique_residues": len(set(x for x in cluster_fp if x >= 0)),
        },
        "level_stats": {
            "min": int(level_arr.min()),
            "max": int(level_arr.max()),
            "median": float(np.median(level_arr)),
            "mean": float(level_arr.mean()),
            "n_distinct": len(level_counter),
            "top5_levels": level_counter.most_common(5),
        },
        "fricke_distribution": dict(fricke_counter),
        "analytic_rank_distribution": {str(k): v for k, v in rank_counter.items()},
        "n_with_rank": len(ranks),
        "galois_image_mod3": dict(galois_counter),
        "cm_distribution": {str(k): v for k, v in cm_counter.items()},
    }

    return result


def compute_branching_factor(forms, mod3_clusters_top):
    """
    For each mod-3 cluster, compute mod-5 fingerprints of its members.
    The branching factor = number of distinct mod-5 fingerprints within
    a mod-3 cluster.
    """
    results = []
    for cluster_fp, cluster_labels in mod3_clusters_top:
        # Compute mod-5 fingerprints for all members
        mod5_fps = {}
        for label in cluster_labels:
            fp5 = compute_fingerprint(forms[label]["traces"], forms[label]["level"], 5)
            mod5_fps[label] = fp5

        # Count distinct mod-5 fingerprints
        fp5_counter = Counter(mod5_fps.values())
        n_distinct_mod5 = len(fp5_counter)

        # Also compute mod-7 branching
        mod7_fps = {}
        for label in cluster_labels:
            fp7 = compute_fingerprint(forms[label]["traces"], forms[label]["level"], 7)
            mod7_fps[label] = fp7
        fp7_counter = Counter(mod7_fps.values())
        n_distinct_mod7 = len(fp7_counter)

        # Branching factor = distinct sub-fingerprints / cluster size
        n = len(cluster_labels)
        results.append({
            "mod3_cluster_size": n,
            "n_distinct_mod5": n_distinct_mod5,
            "n_distinct_mod7": n_distinct_mod7,
            "branching_factor_mod5": n_distinct_mod5 / n,
            "branching_factor_mod7": n_distinct_mod7 / n,
            "mod5_largest_subcluster": fp5_counter.most_common(1)[0][1] if fp5_counter else 0,
            "mod7_largest_subcluster": fp7_counter.most_common(1)[0][1] if fp7_counter else 0,
        })

    return results


def branching_by_rep_type(forms, all_mod3_clusters):
    """
    Test if branching factor depends on Galois image type.
    Group clusters by the dominant Galois image, then compare branching.
    """
    # Only use clusters of size >= 5 for statistics
    type_branching = defaultdict(list)

    for cluster_fp, cluster_labels in all_mod3_clusters:
        n = len(cluster_labels)
        if n < 5:
            continue

        # Classify Galois image of first few members (all should be same for mod-3)
        galois_types = []
        for label in cluster_labels[:min(20, n)]:
            gc = classify_galois_image_mod_ell(forms[label]["traces"], forms[label]["level"], 3)
            galois_types.append(gc)
        dominant_type = Counter(galois_types).most_common(1)[0][0]

        # Compute branching
        mod5_fps = set()
        for label in cluster_labels:
            fp5 = compute_fingerprint(forms[label]["traces"], forms[label]["level"], 5)
            mod5_fps.add(fp5)

        bf = len(mod5_fps) / n
        type_branching[dominant_type].append({
            "cluster_size": n,
            "branching_factor": bf,
            "n_distinct_mod5": len(mod5_fps),
        })

    # Compute aggregate statistics per type
    summary = {}
    for gtype, entries in type_branching.items():
        bfs = [e["branching_factor"] for e in entries]
        sizes = [e["cluster_size"] for e in entries]
        summary[gtype] = {
            "n_clusters": len(entries),
            "total_forms": sum(sizes),
            "mean_branching_factor": float(np.mean(bfs)),
            "median_branching_factor": float(np.median(bfs)),
            "std_branching_factor": float(np.std(bfs)),
            "mean_cluster_size": float(np.mean(sizes)),
        }

    return summary


def analyze_twist_pairs(forms):
    """
    Deep analysis of the 4 twist pairs that survived depth-2 in R3-10.
    What algebraic property forces them to share mod-15 but differ at mod-7?

    Key hypothesis: these are quadratic twists f ⊗ χ_d where d is the level ratio.
    A quadratic twist by χ_d multiplies a_p by χ_d(p) = Legendre(d|p).
    If a_p(f⊗χ) = χ_d(p) * a_p(f), then:
      - mod-ell agreement iff χ_d(p)*a_p ≡ a_p (mod ell) for all good p
      - This happens when a_p ≡ 0 (mod ell) OR χ_d(p) ≡ 1 (mod ell)
    """
    results = []
    for label_a, label_b in TWIST_PAIRS:
        if label_a not in forms or label_b not in forms:
            print(f"  [twist] WARNING: {label_a} or {label_b} not found")
            continue

        fa = forms[label_a]
        fb = forms[label_b]

        # Compute fingerprints at all ells
        fps = {}
        for ell in [2, 3, 5, 7, 11, 13]:
            fp_a = compute_fingerprint(fa["traces"], fa["level"], ell)
            fp_b = compute_fingerprint(fb["traces"], fb["level"], ell)
            agree = 0
            disagree = 0
            total_good = 0
            for i, p in enumerate(PRIMES_25):
                if fp_a[i] == -1 or fp_b[i] == -1:
                    continue
                total_good += 1
                if fp_a[i] == fp_b[i]:
                    agree += 1
                else:
                    disagree += 1
            fps[str(ell)] = {
                "agree": agree,
                "disagree": disagree,
                "total_good": total_good,
                "agreement_rate": agree / total_good if total_good > 0 else 0,
                "fp_a": list(fp_a),
                "fp_b": list(fp_b),
            }

        # Level analysis
        level_a, level_b = fa["level"], fb["level"]
        gcd_level = math.gcd(level_a, level_b)
        ratio = max(level_a, level_b) // gcd_level

        pf_a = sorted(prime_factors(level_a))
        pf_b = sorted(prime_factors(level_b))
        pf_ratio = sorted(prime_factors(int(ratio)))

        # Galois image comparison
        gi_a = {ell: classify_galois_image_mod_ell(fa["traces"], fa["level"], ell)
                for ell in [2, 3, 5, 7]}
        gi_b = {ell: classify_galois_image_mod_ell(fb["traces"], fb["level"], ell)
                for ell in [2, 3, 5, 7]}

        # ── Quadratic twist test ──
        # If b = a ⊗ χ_d, then a_p(b) = χ_d(p) * a_p(a) for good primes p
        # Test: for each good prime, check if a_p(b) / a_p(a) = ±1 consistently
        twist_test = _test_quadratic_twist(fa["traces"], fb["traces"],
                                           fa["level"], fb["level"], ratio)

        # ── Deeper mod analysis: use raw traces, not just mod-ell ──
        raw_comparison = _compare_raw_traces(fa["traces"], fb["traces"],
                                             fa["level"], fb["level"])

        pair_result = {
            "pair": [label_a, label_b],
            "levels": [level_a, level_b],
            "level_gcd": gcd_level,
            "level_ratio": ratio,
            "ratio_prime_factors": pf_ratio,
            "prime_factors_a": pf_a,
            "prime_factors_b": pf_b,
            "fricke_a": fa["fricke"],
            "fricke_b": fb["fricke"],
            "is_cm_a": fa["is_cm"],
            "is_cm_b": fb["is_cm"],
            "analytic_rank_a": fa["analytic_rank"],
            "analytic_rank_b": fb["analytic_rank"],
            "galois_images_a": gi_a,
            "galois_images_b": gi_b,
            "fingerprint_agreement_by_ell": {
                k: {kk: vv for kk, vv in v.items() if kk != "fp_a" and kk != "fp_b"}
                for k, v in fps.items()
            },
            "first_disagreement_primes_mod7": [],
            "quadratic_twist_test": twist_test,
            "raw_trace_comparison": raw_comparison,
        }

        # Find specific primes where mod-7 disagrees
        if "fp_a" in fps.get("7", {}):
            fp_a_7 = fps["7"]["fp_a"]
            fp_b_7 = fps["7"]["fp_b"]
            for i, p in enumerate(PRIMES_25):
                if fp_a_7[i] != -1 and fp_b_7[i] != -1 and fp_a_7[i] != fp_b_7[i]:
                    pair_result["first_disagreement_primes_mod7"].append({
                        "prime": p,
                        "a_p_mod7_a": fp_a_7[i],
                        "a_p_mod7_b": fp_b_7[i],
                    })

        results.append(pair_result)

    return results


def _legendre_symbol(a, p):
    """Compute Legendre symbol (a/p) for odd prime p."""
    a = a % p
    if a == 0:
        return 0
    result = pow(a, (p - 1) // 2, p)
    return result if result <= 1 else -1


def _test_quadratic_twist(traces_a, traces_b, level_a, level_b, d):
    """
    Test if form B is a quadratic twist of form A by character χ_d.
    For a twist, a_p(B) = χ_d(p) * a_p(A) at all good primes.
    """
    bad_a = prime_factors(level_a)
    bad_b = prime_factors(level_b)

    # Generate primes up to 997
    def sieve(limit):
        is_prime = [True] * (limit + 1)
        is_prime[0] = is_prime[1] = False
        for i in range(2, int(limit**0.5) + 1):
            if is_prime[i]:
                for j in range(i*i, limit + 1, i):
                    is_prime[j] = False
        return [i for i in range(2, limit + 1) if is_prime[i]]

    primes = sieve(997)
    n_tested = 0
    n_twist_match = 0
    n_negtwist_match = 0
    n_exact_match = 0
    sign_pattern = []  # (prime, a_p_a, a_p_b, chi_d_p, expected)

    for p in primes:
        if p in bad_a or p in bad_b:
            continue
        if p - 1 >= len(traces_a) or p - 1 >= len(traces_b):
            continue

        ap_a = int(round(traces_a[p - 1]))
        ap_b = int(round(traces_b[p - 1]))
        chi_d_p = _legendre_symbol(d, p) if p != 2 else (1 if d % 8 in [1, 7] else -1)

        n_tested += 1
        if ap_b == chi_d_p * ap_a:
            n_twist_match += 1
        if ap_b == -chi_d_p * ap_a:
            n_negtwist_match += 1
        if ap_b == ap_a:
            n_exact_match += 1

        if n_tested <= 30:
            sign_pattern.append({
                "p": p, "ap_a": ap_a, "ap_b": ap_b,
                "chi_d_p": chi_d_p,
                "is_twist": ap_b == chi_d_p * ap_a,
            })

    # Also test twist by -d, 4d, -4d (different discriminants)
    twist_candidates = {}
    for test_d_label, test_d in [("d", d), ("-d", -d), ("4d", 4*d), ("-4d", -4*d)]:
        match = 0
        for p in primes:
            if p in bad_a or p in bad_b or p == 2:
                continue
            if p - 1 >= len(traces_a) or p - 1 >= len(traces_b):
                continue
            ap_a = int(round(traces_a[p - 1]))
            ap_b = int(round(traces_b[p - 1]))
            chi = _legendre_symbol(test_d, p)
            if ap_b == chi * ap_a:
                match += 1
        twist_candidates[test_d_label] = match

    return {
        "d_tested": d,
        "n_primes_tested": n_tested,
        "n_twist_d_match": n_twist_match,
        "n_negtwist_match": n_negtwist_match,
        "n_exact_match": n_exact_match,
        "twist_rate": n_twist_match / n_tested if n_tested > 0 else 0,
        "is_quadratic_twist": n_twist_match == n_tested,
        "twist_candidates": twist_candidates,
        "sign_pattern_sample": sign_pattern[:15],
        "why_mod3_agrees": (
            "If χ_d(p) ≡ 1 (mod 3) for all good p, then a_p*χ_d(p) ≡ a_p (mod 3). "
            "Since χ_d takes values ±1 and -1 ≡ 2 (mod 3), this requires χ_d(p)=+1 "
            "or a_p ≡ 0 (mod 3) whenever χ_d(p)=-1."
        ),
    }


def _compare_raw_traces(traces_a, traces_b, level_a, level_b):
    """Compare raw a_p values to detect the relationship between two forms."""
    bad_a = prime_factors(level_a)
    bad_b = prime_factors(level_b)

    # Use more primes for a deeper analysis
    def sieve(limit):
        is_prime = [True] * (limit + 1)
        is_prime[0] = is_prime[1] = False
        for i in range(2, int(limit**0.5) + 1):
            if is_prime[i]:
                for j in range(i*i, limit + 1, i):
                    is_prime[j] = False
        return [i for i in range(2, limit + 1) if is_prime[i]]

    all_primes = sieve(500)
    ratios = []
    diff_counter = Counter()
    n_good = 0

    for p in all_primes:
        if p in bad_a or p in bad_b:
            continue
        if p - 1 >= len(traces_a) or p - 1 >= len(traces_b):
            continue
        ap_a = int(round(traces_a[p - 1]))
        ap_b = int(round(traces_b[p - 1]))
        diff = ap_a - ap_b
        diff_counter[diff] += 1
        n_good += 1
        if len(ratios) < 25:  # Only store first 25 for output
            if ap_a != 0:
                ratios.append({"p": p, "ap_a": ap_a, "ap_b": ap_b,
                              "diff": diff, "ratio": ap_b / ap_a})
            else:
                ratios.append({"p": p, "ap_a": ap_a, "ap_b": ap_b,
                              "diff": diff, "ratio": "a=0"})

    # Analyze the difference structure
    all_diffs = sorted(diff_counter.keys())
    gcd_diff = 0
    for d in all_diffs:
        if d != 0:
            gcd_diff = math.gcd(gcd_diff, abs(d))

    # Check divisibility by various primes
    div_tests = {}
    for ell in [2, 3, 5, 7, 11, 13, 15, 30]:
        all_div = all(d % ell == 0 for d in all_diffs)
        div_tests[str(ell)] = all_div

    return {
        "first_25_comparisons": ratios,
        "n_good_primes_tested": n_good,
        "unique_differences": dict(diff_counter.most_common()),
        "gcd_of_all_diffs": gcd_diff,
        "divisibility_tests": div_tests,
        "all_diffs_are_multiples_of_15": div_tests.get("15", False),
    }


def compute_lift_diversity_index(forms, all_mod3_clusters, min_cluster_size=3):
    """
    For each mod-p cluster, compute the entropy of the mod-q distribution
    within it (for q != p). High entropy = highly diverse lifts.
    """
    # We compute for mod-3 clusters -> entropy of mod-5 and mod-7 distributions
    diversity_data = []

    for cluster_fp, cluster_labels in all_mod3_clusters:
        n = len(cluster_labels)
        if n < min_cluster_size:
            continue

        # Mod-5 fingerprint distribution within this mod-3 cluster
        fp5_counter = Counter()
        fp7_counter = Counter()
        for label in cluster_labels:
            fp5 = compute_fingerprint(forms[label]["traces"], forms[label]["level"], 5)
            fp7 = compute_fingerprint(forms[label]["traces"], forms[label]["level"], 7)
            fp5_counter[fp5] += 1
            fp7_counter[fp7] += 1

        ent5 = entropy(fp5_counter)
        ent7 = entropy(fp7_counter)

        # Maximum possible entropy for this cluster size
        max_ent = math.log2(n) if n > 1 else 0

        diversity_data.append({
            "mod3_cluster_size": n,
            "n_distinct_mod5": len(fp5_counter),
            "n_distinct_mod7": len(fp7_counter),
            "entropy_mod5": round(ent5, 4),
            "entropy_mod7": round(ent7, 4),
            "max_entropy": round(max_ent, 4),
            "normalized_entropy_mod5": round(ent5 / max_ent, 4) if max_ent > 0 else 0,
            "normalized_entropy_mod7": round(ent7 / max_ent, 4) if max_ent > 0 else 0,
        })

    # Overall statistics
    if diversity_data:
        ne5 = [d["normalized_entropy_mod5"] for d in diversity_data]
        ne7 = [d["normalized_entropy_mod7"] for d in diversity_data]
        sizes = [d["mod3_cluster_size"] for d in diversity_data]

        # Correlation between cluster size and entropy
        # (may be NaN if all values identical = zero variance)
        if len(sizes) > 2 and np.std(ne5) > 0 and np.std(sizes) > 0:
            corr_size_ent5 = float(np.corrcoef(sizes, ne5)[0, 1])
        else:
            corr_size_ent5 = None
        if len(sizes) > 2 and np.std(ne7) > 0 and np.std(sizes) > 0:
            corr_size_ent7 = float(np.corrcoef(sizes, ne7)[0, 1])
        else:
            corr_size_ent7 = None

        summary = {
            "n_clusters_analyzed": len(diversity_data),
            "mean_normalized_entropy_mod5": float(np.mean(ne5)),
            "mean_normalized_entropy_mod7": float(np.mean(ne7)),
            "median_normalized_entropy_mod5": float(np.median(ne5)),
            "median_normalized_entropy_mod7": float(np.median(ne7)),
            "correlation_size_vs_entropy_mod5": corr_size_ent5,
            "correlation_size_vs_entropy_mod7": corr_size_ent7,
        }
    else:
        summary = {"n_clusters_analyzed": 0}

    return diversity_data, summary


def compute_mod5_clusters_diversity(forms):
    """Same analysis for mod-5 clusters -> entropy of mod-3 and mod-7."""
    clusters = defaultdict(list)
    for label, fdata in forms.items():
        fp = compute_fingerprint(fdata["traces"], fdata["level"], 5)
        clusters[fp].append(label)

    sorted_clusters = sorted(clusters.items(), key=lambda x: -len(x[1]))
    diversity_data = []

    for cluster_fp, cluster_labels in sorted_clusters:
        n = len(cluster_labels)
        if n < 3:
            continue

        fp3_counter = Counter()
        fp7_counter = Counter()
        for label in cluster_labels:
            fp3 = compute_fingerprint(forms[label]["traces"], forms[label]["level"], 3)
            fp7 = compute_fingerprint(forms[label]["traces"], forms[label]["level"], 7)
            fp3_counter[fp3] += 1
            fp7_counter[fp7] += 1

        ent3 = entropy(fp3_counter)
        ent7 = entropy(fp7_counter)
        max_ent = math.log2(n) if n > 1 else 0

        diversity_data.append({
            "mod5_cluster_size": n,
            "n_distinct_mod3": len(fp3_counter),
            "n_distinct_mod7": len(fp7_counter),
            "entropy_mod3": round(ent3, 4),
            "entropy_mod7": round(ent7, 4),
            "normalized_entropy_mod3": round(ent3 / max_ent, 4) if max_ent > 0 else 0,
            "normalized_entropy_mod7": round(ent7 / max_ent, 4) if max_ent > 0 else 0,
        })

    if diversity_data:
        ne3 = [d["normalized_entropy_mod3"] for d in diversity_data]
        ne7 = [d["normalized_entropy_mod7"] for d in diversity_data]
        summary = {
            "n_clusters_analyzed": len(diversity_data),
            "mean_normalized_entropy_mod3": float(np.mean(ne3)),
            "mean_normalized_entropy_mod7": float(np.mean(ne7)),
        }
    else:
        summary = {"n_clusters_analyzed": 0}

    return diversity_data, summary


def main():
    t0 = time.time()
    print("=" * 70)
    print("Cross-Level Lift Detection")
    print("=" * 70)

    # ── Load data ──
    forms = load_all_data()

    # ── Build mod-3 clusters ──
    print("\n[cluster] Building mod-3 clusters...")
    all_mod3_clusters = build_mod3_clusters(forms)
    print(f"[cluster] {len(all_mod3_clusters)} total mod-3 clusters")
    top10 = all_mod3_clusters[:10]
    print(f"[cluster] Top 10 sizes: {[len(c[1]) for _, c in zip(range(10), all_mod3_clusters)]}")

    # ── 1. Cluster internal structure ──
    print("\n[internal] Analyzing top 10 cluster internals...")
    cluster_internals = []
    for i, (fp, labels) in enumerate(top10):
        print(f"  Cluster {i+1}: size={len(labels)}, analyzing...")
        analysis = analyze_cluster_internals(labels, forms, fp)
        analysis["rank"] = i + 1
        analysis["sample_labels"] = labels[:10]
        cluster_internals.append(analysis)

    # ── 2. Branching factor ──
    print("\n[branching] Computing branching factors for top 10...")
    branching = compute_branching_factor(forms, top10)

    # ── 3. Branching by representation type ──
    print("\n[rep_type] Analyzing branching by Galois image type...")
    branching_by_type = branching_by_rep_type(forms, all_mod3_clusters)

    # ── 4. Twist pair analysis ──
    print("\n[twist] Analyzing 4 depth-2 survivor twist pairs...")
    twist_analysis = analyze_twist_pairs(forms)

    # ── 5. Lift diversity index ──
    print("\n[diversity] Computing lift diversity index (mod-3 clusters)...")
    div_data_mod3, div_summary_mod3 = compute_lift_diversity_index(forms, all_mod3_clusters)

    print("[diversity] Computing lift diversity index (mod-5 clusters)...")
    div_data_mod5, div_summary_mod5 = compute_mod5_clusters_diversity(forms)

    elapsed = time.time() - t0

    # ── Assemble results ──
    results = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "n_forms": len(forms),
            "elapsed_seconds": round(elapsed, 2),
        },
        "top10_mod3_clusters": {
            "internals": cluster_internals,
            "branching_factors": branching,
            "summary": {
                "sizes": [c["size"] for c in cluster_internals],
                "mean_branching_mod5": float(np.mean([b["branching_factor_mod5"] for b in branching])),
                "mean_branching_mod7": float(np.mean([b["branching_factor_mod7"] for b in branching])),
            },
        },
        "branching_by_galois_type": branching_by_type,
        "twist_pair_analysis": twist_analysis,
        "lift_diversity_mod3_clusters": {
            "summary": div_summary_mod3,
            "top20_by_size": div_data_mod3[:20],
        },
        "lift_diversity_mod5_clusters": {
            "summary": div_summary_mod5,
            "top20_by_size": div_data_mod5[:20],
        },
    }

    # ── Print key findings ──
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)

    print("\n--- Top 10 Mod-3 Cluster Internals ---")
    for ci in cluster_internals:
        print(f"  Cluster #{ci['rank']}: size={ci['size']}, "
              f"levels={ci['level_stats']['n_distinct']} distinct ({ci['level_stats']['min']}-{ci['level_stats']['max']}), "
              f"fricke={ci['fricke_distribution']}, "
              f"galois={ci['galois_image_mod3']}")

    print("\n--- Branching Factors ---")
    for i, b in enumerate(branching):
        print(f"  Cluster #{i+1} (size {b['mod3_cluster_size']}): "
              f"mod5 branches={b['n_distinct_mod5']} (BF={b['branching_factor_mod5']:.3f}), "
              f"mod7 branches={b['n_distinct_mod7']} (BF={b['branching_factor_mod7']:.3f})")

    print("\n--- Branching by Galois Image Type ---")
    for gtype, stats in branching_by_type.items():
        print(f"  {gtype}: {stats['n_clusters']} clusters, "
              f"mean BF={stats['mean_branching_factor']:.3f} +/- {stats['std_branching_factor']:.3f}")

    print("\n--- Twist Pair Analysis ---")
    for tp in twist_analysis:
        print(f"  {tp['pair'][0]} <-> {tp['pair'][1]}")
        print(f"    Levels: {tp['levels']}, ratio={tp['level_ratio']}, "
              f"ratio factors={tp['ratio_prime_factors']}")
        print(f"    CM: {tp['is_cm_a']}, {tp['is_cm_b']}")
        print(f"    Fricke: {tp['fricke_a']}, {tp['fricke_b']}")
        print(f"    Rank: {tp['analytic_rank_a']}, {tp['analytic_rank_b']}")
        for ell_str, fa_data in tp["fingerprint_agreement_by_ell"].items():
            print(f"    mod-{ell_str}: {fa_data['agree']}/{fa_data['total_good']} agree "
                  f"({fa_data['agreement_rate']:.3f})")
        if tp["first_disagreement_primes_mod7"]:
            print(f"    mod-7 disagreements at primes: "
                  f"{[d['prime'] for d in tp['first_disagreement_primes_mod7']]}")
        # Quadratic twist test
        qt = tp.get("quadratic_twist_test", {})
        if qt:
            print(f"    Quadratic twist by d={qt['d_tested']}: "
                  f"{qt['n_twist_d_match']}/{qt['n_primes_tested']} match "
                  f"(rate={qt['twist_rate']:.4f}), "
                  f"is_twist={qt['is_quadratic_twist']}")
            print(f"    Twist candidates: {qt['twist_candidates']}")
            if qt.get("sign_pattern_sample"):
                print(f"    First 5 sign patterns:")
                for sp in qt["sign_pattern_sample"][:5]:
                    print(f"      p={sp['p']}: a_p(a)={sp['ap_a']}, a_p(b)={sp['ap_b']}, "
                          f"chi_d(p)={sp['chi_d_p']}, twist_match={sp['is_twist']}")
        # Raw trace difference structure
        raw = tp.get("raw_trace_comparison", {})
        if isinstance(raw, dict):
            print(f"    GCD of all diffs: {raw.get('gcd_of_all_diffs')}")
            print(f"    All diffs multiples of 15: {raw.get('all_diffs_are_multiples_of_15')}")
            print(f"    Unique differences: {raw.get('unique_differences')}")
            print(f"    Divisibility: {raw.get('divisibility_tests')}")

    print("\n--- Lift Diversity Summary ---")
    print(f"  Mod-3 clusters (n={div_summary_mod3['n_clusters_analyzed']}): "
          f"mean norm entropy(mod5)={div_summary_mod3.get('mean_normalized_entropy_mod5', 'N/A'):.4f}, "
          f"entropy(mod7)={div_summary_mod3.get('mean_normalized_entropy_mod7', 'N/A'):.4f}")
    if div_summary_mod3.get("correlation_size_vs_entropy_mod5") is not None:
        print(f"  Size-entropy correlation: "
              f"mod5 r={div_summary_mod3['correlation_size_vs_entropy_mod5']:.4f}, "
              f"mod7 r={div_summary_mod3['correlation_size_vs_entropy_mod7']:.4f}")

    # ── Save ──
    OUT_PATH.write_text(json.dumps(results, indent=2, default=str))
    print(f"\n[save] Results saved to {OUT_PATH}")
    print(f"[done] Elapsed: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
