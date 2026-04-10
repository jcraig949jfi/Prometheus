#!/usr/bin/env python3
"""
Conditional Cross-Ell Independence Test (R4-5)
===============================================
CT1 showed total cross-ell independence: 0/29,043 mod-3 pairs also in
mod-5 clusters. But what if conditioning on a geometric invariant
CREATES dependence?

Tests conditioning on:
  1. Functional equation sign (fricke_eigenval)
  2. Galois image class (R3-2)
  3. Conductor factorization (squarefree vs p²|N)
  4. Starvation status (non-CM starved forms)

For each conditioning, compute cross-ell overlap, expected under
independence, enrichment ratio, and hypergeometric p-value.

Charon / Project Prometheus — 2026-04-09
"""

import json
import math
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import duckdb
import numpy as np

# ── Config ──────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[4]  # F:\Prometheus
DB_PATH = REPO_ROOT / "charon" / "data" / "charon.duckdb"
GALOIS_PATH = Path(__file__).resolve().parent / "galois_image_results.json"
STARVATION_PATH = Path(__file__).resolve().parent / "residue_starvation_results.json"
OUT_PATH = Path(__file__).resolve().parent / "conditional_cross_ell_results.json"

PRIMES_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
             31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
             73, 79, 83, 89, 97]

ELL_PAIRS = [(3, 5), (3, 7), (5, 7)]


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
    """Check if n is squarefree."""
    d = 2
    while d * d <= n:
        if n % (d * d) == 0:
            return False
        d += 1
    return True


def has_square_prime_factor(n):
    """Check if p^2 | n for some prime p."""
    return not is_squarefree(n)


def log_comb(n, k):
    """Log of C(n,k) using sum of logs."""
    if k < 0 or k > n:
        return -float('inf')
    if k == 0 or k == n:
        return 0.0
    k = min(k, n - k)
    return sum(math.log(n - i) - math.log(i + 1) for i in range(k))


def hypergeometric_pmf(k, N, K, n):
    """P(X = k) for hypergeometric(N, K, n)."""
    log_p = log_comb(K, k) + log_comb(N - K, n - k) - log_comb(N, n)
    return math.exp(log_p) if log_p > -700 else 0.0


def hypergeometric_sf(k, N, K, n):
    """P(X >= k) = survival function for hypergeometric."""
    upper = min(K, n)
    if k > upper:
        return 0.0
    if k <= 0:
        return 1.0
    p_total = 0.0
    for j in range(k, upper + 1):
        p_total += hypergeometric_pmf(j, N, K, n)
    return min(p_total, 1.0)


def compute_fingerprint(traces, level, ell):
    """Compute mod-ell fingerprint vector for a form."""
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


# ── Data loading ─────────────────────────────────────────────────────

def load_forms():
    """Load all dim-1 weight-2 newforms from DuckDB with metadata."""
    print(f"[load] Connecting to {DB_PATH}")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    rows = con.execute('''
        SELECT lmfdb_label, level, traces, fricke_eigenval, is_cm,
               ap_coeffs
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND traces IS NOT NULL
        ORDER BY level, lmfdb_label
    ''').fetchall()
    con.close()
    print(f"[load] {len(rows)} forms loaded")

    forms = []
    for label, level, traces, fricke, is_cm, ap_coeffs in rows:
        forms.append({
            'label': label,
            'level': level,
            'traces': traces,
            'fricke': fricke,
            'is_cm': bool(is_cm),
            'ap_coeffs': ap_coeffs,
        })
    return forms


def load_starvation_labels():
    """Load non-CM starved form labels from C02."""
    print(f"[load] Loading starvation results from {STARVATION_PATH}")
    with open(STARVATION_PATH) as f:
        data = json.load(f)

    noncm_starved = set()
    for form in data.get("starved_forms", []):
        if form.get("flag", "").startswith("NON-CM"):
            noncm_starved.add(form["label"])

    print(f"[load] {len(noncm_starved)} non-CM starved forms")
    return noncm_starved


# ── Core analysis ────────────────────────────────────────────────────

def cluster_forms(forms_subset, ell):
    """
    Cluster a subset of forms by mod-ell fingerprint.
    Returns dict: fingerprint -> list of labels.
    """
    clusters = defaultdict(list)
    for form in forms_subset:
        fp = compute_fingerprint(form['traces'], form['level'], ell)
        clusters[fp].append(form['label'])
    return dict(clusters)


def extract_nontrivial_pairs(clusters):
    """
    Extract all pairs (label_i, label_j) that share a cluster.
    Only from clusters of size >= 2.
    Returns: set of frozenset pairs, and set of labels in any nontrivial cluster.
    """
    pairs = set()
    labels_in_clusters = set()
    for fp, labels in clusters.items():
        if len(labels) < 2:
            continue
        labels_in_clusters.update(labels)
        for i in range(len(labels)):
            for j in range(i + 1, len(labels)):
                pairs.add(frozenset([labels[i], labels[j]]))
    return pairs, labels_in_clusters


def compute_cross_ell_overlap(forms_subset, ell_a, ell_b):
    """
    For a subpopulation, compute:
    - Pairs sharing mod-ell_a cluster
    - Pairs sharing mod-ell_b cluster
    - Overlap (pairs sharing both)
    - Hypergeometric test statistics
    """
    n_forms = len(forms_subset)
    if n_forms < 2:
        return {
            "n_forms": n_forms,
            "ell_a": ell_a,
            "ell_b": ell_b,
            "pairs_a": 0,
            "pairs_b": 0,
            "overlap": 0,
            "expected": 0.0,
            "enrichment": None,
            "p_value": 1.0,
            "note": "too few forms"
        }

    clusters_a = cluster_forms(forms_subset, ell_a)
    clusters_b = cluster_forms(forms_subset, ell_b)

    pairs_a, labels_a = extract_nontrivial_pairs(clusters_a)
    pairs_b, labels_b = extract_nontrivial_pairs(clusters_b)

    overlap = pairs_a & pairs_b

    # Hypergeometric test:
    # N = total possible pairs in subpopulation
    # K = pairs in cluster_a
    # n = pairs in cluster_b
    # k = overlap
    N_total = n_forms * (n_forms - 1) // 2
    K = len(pairs_a)
    n = len(pairs_b)
    k = len(overlap)

    expected = (K * n / N_total) if N_total > 0 else 0.0
    if expected > 0:
        enrichment = k / expected
    elif k > 0:
        enrichment = float('inf')
    else:
        enrichment = 1.0

    # p-value: P(X >= k) under hypergeometric(N_total, K, n)
    if k > 0:
        p_val = hypergeometric_sf(k, N_total, K, n)
    else:
        p_val = 1.0

    result = {
        "n_forms": n_forms,
        "ell_a": ell_a,
        "ell_b": ell_b,
        "total_possible_pairs": N_total,
        "pairs_a": K,
        "pairs_b": n,
        "overlap": k,
        "expected": round(expected, 4),
        "enrichment": round(enrichment, 4) if enrichment != float('inf') else "inf",
        "p_value": p_val,
    }

    if k > 0:
        # Record the overlapping pairs
        overlap_list = [list(p) for p in sorted(overlap, key=lambda x: sorted(x))][:20]
        result["overlap_examples"] = overlap_list

    return result


# Sieve for fast prime checking
def _build_primes(n=997):
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i in range(2, n+1) if sieve[i]]

PRIMES_UP_TO_997 = _build_primes(997)
PRIMES_SET = set(PRIMES_UP_TO_997)
GALOIS_ELLS = [2, 3, 5, 7]
MIN_GOOD = 30


def qr_set(ell):
    """Quadratic residues mod ell (including 0)."""
    return {(x * x) % ell for x in range(ell)}


def classify_at_ell(distribution, ell, n_good):
    """
    Classify a form's a_p mod ell distribution.
    Mirrors galois_image_portraits.py decision tree.
    """
    total = sum(distribution.values())
    if total == 0 or n_good < MIN_GOOD:
        return None

    observed = np.zeros(ell)
    for k, count in distribution.items():
        observed[int(k) % ell] += count
    observed /= observed.sum()

    zero_freq = observed[0]
    classes_hit = sum(1 for x in observed if x > 0)

    # Chi-squared test against uniform
    chi_sq_uniform = sum((observed[i] - 1.0/ell)**2 / (1.0/ell) for i in range(ell))
    chi_sq_test = chi_sq_uniform * n_good

    # Mod-2 special handling
    if ell == 2:
        if observed[1] < 0.01:
            return "mod2_all_even"
        elif abs(observed[0] - 0.5) < 0.05:
            return "full"
        elif observed[0] > 0.6:
            return "borel"
        else:
            return "full"

    # Cartan threshold
    cartan_threshold = max(0.45, 1.0 / (ell - 1) + 0.05)
    borel_zero_threshold = 1.0 / ell * 1.3

    if zero_freq > cartan_threshold:
        return "cartan"

    if zero_freq > borel_zero_threshold and n_good >= 50:
        # Build borel/full templates
        qr = qr_set(ell)
        borel = np.zeros(ell)
        borel[0] = 2.0 / ell
        for k in range(1, ell):
            if k in qr:
                borel[k] = 1.5 / (ell * max(len(qr) - 1, 1)) * (len(qr) - 1)
            else:
                borel[k] = 0.5 / (ell * max(ell - len(qr), 1)) * (ell - len(qr))
        borel /= borel.sum()
        full = np.ones(ell) / ell

        d_borel = sum((observed[i] - borel[i])**2 / borel[i] if borel[i] > 1e-10 else 0 for i in range(ell))
        d_full = sum((observed[i] - full[i])**2 / full[i] for i in range(ell))
        if d_borel < d_full:
            return "borel"

    if classes_hit < ell and n_good >= 50:
        return "borel"

    # Check for moderate zero enrichment
    expected_zero = 1.0 / ell
    if zero_freq > expected_zero * 1.8 and n_good >= 50:
        return "borel"

    # Chi-squared test for anomalous
    crit_values = {3: 13.8, 5: 18.5, 7: 22.5}
    crit = crit_values.get(ell, 3.84 * (ell - 1))
    if chi_sq_test > crit:
        return "anomalous"

    return "full"


def classify_combined(per_ell_classes):
    """
    Combine per-ell classifications into combined Galois portrait.
    Mirrors galois_image_portraits.py classify_combined().
    """
    classes = {ell: c for ell, c in per_ell_classes.items() if c is not None}
    if not classes:
        return "insufficient_data"

    cartan_ells = [ell for ell, c in classes.items() if c == "cartan" and ell >= 3]
    if len(cartan_ells) >= 2:
        return "CM_cartan"
    if len(cartan_ells) == 1:
        return f"possible_CM_mod{cartan_ells[0]}"

    norm_ells = [ell for ell, c in classes.items() if c == "norm_cartan"]
    if len(norm_ells) >= 2:
        return "CM_normalizer_cartan"
    if len(norm_ells) == 1:
        return f"possible_norm_cartan_mod{norm_ells[0]}"

    if classes.get(2) == "mod2_all_even":
        borel_others = sum(1 for e, c in classes.items() if e != 2 and c == "borel")
        if borel_others >= 1:
            return "borel_isogeny_2plus"
        return "borel_mod2"

    borel_ells = [ell for ell, c in classes.items() if c == "borel" and ell >= 3]
    if len(borel_ells) >= 2:
        return "borel_isogeny"
    if len(borel_ells) == 1:
        return f"borel_mod{borel_ells[0]}"

    full_count = sum(1 for c in classes.values() if c == "full")
    anom_count = sum(1 for c in classes.values() if c == "anomalous")

    if anom_count >= 2:
        return "anomalous_multi"
    if full_count >= len(classes) - 1:
        return "full_image"

    return "mixed"


def classify_galois_image(form):
    """
    Full Galois image classification for a single form.
    Uses ap_coeffs (integer coefficients) for accuracy.
    Falls back to traces if ap_coeffs unavailable.
    """
    level = form['level']

    # Try to parse ap_coeffs (JSON string of integer lists)
    ap = None
    if form.get('ap_coeffs'):
        try:
            raw = json.loads(form['ap_coeffs'])
            ap = [int(x[0]) if isinstance(x, list) else int(x) for x in raw]
        except Exception:
            ap = None

    per_ell = {}
    for ell in GALOIS_ELLS:
        if ap is not None:
            good_vals = [ap[i] for i, p in enumerate(PRIMES_UP_TO_997)
                         if i < len(ap) and level % p != 0 and p != ell]
        else:
            # Fallback to traces
            traces = form['traces']
            good_vals = []
            for p in PRIMES_UP_TO_997:
                if level % p == 0 or p == ell:
                    continue
                if p - 1 < len(traces):
                    good_vals.append(int(round(traces[p - 1])))

        if len(good_vals) < MIN_GOOD:
            per_ell[ell] = None
            continue

        dist = Counter()
        for v in good_vals:
            dist[v % ell] += 1

        per_ell[ell] = classify_at_ell(dist, ell, len(good_vals))

    return classify_combined(per_ell)


def run_conditioned_test(forms_subset, condition_name, condition_detail=""):
    """Run cross-ell overlap test on a conditioned subpopulation."""
    print(f"\n{'='*60}")
    print(f"CONDITION: {condition_name}")
    if condition_detail:
        print(f"  {condition_detail}")
    print(f"  n_forms = {len(forms_subset)}")
    print(f"{'='*60}")

    results = {
        "condition": condition_name,
        "detail": condition_detail,
        "n_forms": len(forms_subset),
        "ell_pairs": {},
    }

    for ell_a, ell_b in ELL_PAIRS:
        key = f"{ell_a}_vs_{ell_b}"
        print(f"  Testing mod-{ell_a} vs mod-{ell_b}...")
        r = compute_cross_ell_overlap(forms_subset, ell_a, ell_b)
        results["ell_pairs"][key] = r

        overlap = r["overlap"]
        expected = r["expected"]
        p_val = r["p_value"]
        tag = ""
        if overlap > 0 and p_val < 0.01:
            tag = " *** SIGNIFICANT ***"
        elif overlap > 0:
            tag = " (overlap detected)"
        print(f"    pairs_a={r['pairs_a']}, pairs_b={r['pairs_b']}, "
              f"overlap={overlap}, expected={expected:.2f}, "
              f"enrichment={r['enrichment']}, p={p_val:.2e}{tag}")

    return results


# ── Main ─────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    print("=" * 72)
    print("CONDITIONAL CROSS-ELL INDEPENDENCE TEST (R4-5)")
    print("=" * 72)

    # Load data
    forms = load_forms()
    noncm_starved = load_starvation_labels()

    all_results = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "n_forms_total": len(forms),
            "ell_pairs": ELL_PAIRS,
            "primes_for_fingerprint": PRIMES_25,
        },
        "tests": [],
        "enrichment_table": [],
    }

    # ── 1. UNCONDITIONAL BASELINE ────────────────────────────────────
    baseline = run_conditioned_test(forms, "unconditional", "Full population (baseline)")
    all_results["tests"].append(baseline)

    # ── 2. CONDITION ON FRICKE EIGENVALUE ────────────────────────────
    fricke_plus = [f for f in forms if f['fricke'] == 1]
    fricke_minus = [f for f in forms if f['fricke'] == -1]
    fricke_null = [f for f in forms if f['fricke'] is None or f['fricke'] not in (1, -1)]

    print(f"\n[info] Fricke distribution: +1={len(fricke_plus)}, -1={len(fricke_minus)}, other={len(fricke_null)}")

    r_fp = run_conditioned_test(fricke_plus, "fricke=+1", f"n={len(fricke_plus)} forms with functional equation sign +1")
    r_fm = run_conditioned_test(fricke_minus, "fricke=-1", f"n={len(fricke_minus)} forms with functional equation sign -1")
    all_results["tests"].extend([r_fp, r_fm])

    # ── 3. CONDITION ON GALOIS IMAGE CLASS ───────────────────────────
    # Classify all forms by Galois image using the R3-2 method
    print("\n[info] Classifying Galois images (R3-2 method)...")
    galois_classes = defaultdict(list)

    for i, form in enumerate(forms):
        cls = classify_galois_image(form)
        galois_classes[cls].append(form)
        if (i + 1) % 5000 == 0:
            print(f"  classified {i+1}/{len(forms)}...")

    print(f"[info] Galois class distribution:")
    for cls, members in sorted(galois_classes.items(), key=lambda x: -len(x[1])):
        print(f"  {cls}: {len(members)}")

    # Test specific classes
    for cls_name in ["borel_mod2", "CM_cartan", "full_image"]:
        if cls_name in galois_classes and len(galois_classes[cls_name]) >= 10:
            r = run_conditioned_test(
                galois_classes[cls_name],
                f"galois={cls_name}",
                f"n={len(galois_classes[cls_name])} forms with Galois image class {cls_name}"
            )
            all_results["tests"].append(r)

    # Also test borel_mod3 if present (smaller, more constrained)
    if "borel_mod3" in galois_classes and len(galois_classes["borel_mod3"]) >= 10:
        r = run_conditioned_test(
            galois_classes["borel_mod3"],
            "galois=borel_mod3",
            f"n={len(galois_classes['borel_mod3'])} forms with borel mod-3 image"
        )
        all_results["tests"].append(r)

    # ── 4. CONDITION ON CONDUCTOR FACTORIZATION ──────────────────────
    squarefree_forms = [f for f in forms if is_squarefree(f['level'])]
    nonsquarefree_forms = [f for f in forms if has_square_prime_factor(f['level'])]

    print(f"\n[info] Conductor factorization: squarefree={len(squarefree_forms)}, "
          f"has p^2={len(nonsquarefree_forms)}")

    r_sq = run_conditioned_test(
        squarefree_forms,
        "conductor=squarefree",
        f"n={len(squarefree_forms)} forms with squarefree conductor"
    )
    r_nsq = run_conditioned_test(
        nonsquarefree_forms,
        "conductor=has_p^2",
        f"n={len(nonsquarefree_forms)} forms with p^2 | N"
    )
    all_results["tests"].extend([r_sq, r_nsq])

    # ── 5. CONDITION ON STARVATION ───────────────────────────────────
    starved_forms = [f for f in forms if f['label'] in noncm_starved]
    nonstarved_forms = [f for f in forms if f['label'] not in noncm_starved]

    print(f"\n[info] Starvation: non-CM starved={len(starved_forms)}, "
          f"not starved={len(nonstarved_forms)}")

    r_starv = run_conditioned_test(
        starved_forms,
        "starvation=non-CM",
        f"n={len(starved_forms)} non-CM starved forms (constrained Galois images)"
    )
    all_results["tests"].append(r_starv)

    # ── 6. ENRICHMENT SUMMARY TABLE ──────────────────────────────────
    print("\n" + "=" * 72)
    print("ENRICHMENT SUMMARY TABLE")
    print("=" * 72)
    print(f"{'Condition':<30} {'Ells':>8} {'N':>6} {'Pairs_a':>8} "
          f"{'Pairs_b':>8} {'Overlap':>8} {'Expected':>9} {'Enrich':>8} {'p-value':>12}")
    print("-" * 120)

    for test in all_results["tests"]:
        for key, r in test["ell_pairs"].items():
            sig = " ***" if r["overlap"] > 0 and r["p_value"] < 0.01 else ""
            enrich_str = f"{r['enrichment']:.2f}x" if isinstance(r['enrichment'], (int, float)) else r['enrichment']
            print(f"{test['condition']:<30} {key:>8} {r['n_forms']:>6} "
                  f"{r['pairs_a']:>8} {r['pairs_b']:>8} {r['overlap']:>8} "
                  f"{r['expected']:>9.2f} {enrich_str:>8} {r['p_value']:>12.2e}{sig}")

            all_results["enrichment_table"].append({
                "condition": test["condition"],
                "ell_pair": key,
                "n_forms": r["n_forms"],
                "pairs_a": r["pairs_a"],
                "pairs_b": r["pairs_b"],
                "overlap": r["overlap"],
                "expected": r["expected"],
                "enrichment": r["enrichment"],
                "p_value": r["p_value"],
                "significant": r["overlap"] > 0 and r["p_value"] < 0.01,
            })

    # ── 7. INTERPRETATION ────────────────────────────────────────────
    any_significant = any(e["significant"] for e in all_results["enrichment_table"])
    any_overlap = any(e["overlap"] > 0 for e in all_results["enrichment_table"])

    print("\n" + "=" * 72)
    print("INTERPRETATION")
    print("=" * 72)

    if any_significant:
        sig_entries = [e for e in all_results["enrichment_table"] if e["significant"]]
        print(f"  MAJOR FINDING: {len(sig_entries)} conditioned tests show significant cross-ell overlap!")
        for e in sig_entries:
            print(f"    {e['condition']} / {e['ell_pair']}: "
                  f"overlap={e['overlap']}, enrichment={e['enrichment']}, p={e['p_value']:.2e}")
        print("  These geometric invariants create entanglement between mod-ell fibers!")
        all_results["interpretation"] = {
            "finding": "SIGNIFICANT_ENTANGLEMENT",
            "significant_conditions": [
                {"condition": e["condition"], "ell_pair": e["ell_pair"],
                 "overlap": e["overlap"], "enrichment": e["enrichment"],
                 "p_value": e["p_value"]}
                for e in sig_entries
            ],
        }
    elif any_overlap:
        overlap_entries = [e for e in all_results["enrichment_table"] if e["overlap"] > 0]
        print(f"  Overlap detected in {len(overlap_entries)} tests but not significant:")
        for e in overlap_entries:
            print(f"    {e['condition']} / {e['ell_pair']}: "
                  f"overlap={e['overlap']}, p={e['p_value']:.2e}")
        print("  No geometric invariant breaks cross-ell independence at significance threshold.")
        all_results["interpretation"] = {
            "finding": "WEAK_SIGNAL_NOT_SIGNIFICANT",
            "overlap_conditions": [
                {"condition": e["condition"], "ell_pair": e["ell_pair"],
                 "overlap": e["overlap"], "p_value": e["p_value"]}
                for e in overlap_entries
            ],
        }
    else:
        print("  TOTAL INDEPENDENCE CONFIRMED under all conditioning variables.")
        print("  No geometric invariant creates cross-ell entanglement.")
        print("  Cross-ell independence is a deep structural property, not an artifact of averaging.")
        all_results["interpretation"] = {
            "finding": "TOTAL_INDEPENDENCE_CONFIRMED",
            "detail": "Zero overlap under all conditioning variables. "
                      "Cross-ell independence is intrinsic, not hidden by population averaging."
        }

    elapsed = time.time() - t0
    all_results["metadata"]["elapsed_seconds"] = round(elapsed, 1)

    # Save
    with open(OUT_PATH, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\n[done] Results saved to {OUT_PATH}")
    print(f"[done] Elapsed: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
