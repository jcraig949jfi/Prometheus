#!/usr/bin/env python3
"""
Layer 3 Symmetry Detection — Transformation Detection via Action, Not Labels.

Detects hidden symmetries in modular forms through:
1. Quadratic twist detection (Dirichlet character ratios)
2. Character invariance scan (small conductor twists)
3. Sign pattern clustering (Hamming distance on sgn(a_p))
4. OEIS shift/scale/twist invariance
5. CM rediscovery without labels

Charon — Cross-Domain Cartographer, Project Prometheus
"""

import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Utility: primes, Kronecker symbol, Dirichlet characters
# ---------------------------------------------------------------------------

def sieve_primes(n):
    """Sieve of Eratosthenes up to n."""
    is_prime = [False, False] + [True] * (n - 1)
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]

PRIMES_1000 = sieve_primes(1000)
PRIMES_100 = [p for p in PRIMES_1000 if p <= 97]

def kronecker_symbol(a, n):
    """Compute the Kronecker symbol (a/n)."""
    if n == 0:
        return 1 if abs(a) == 1 else 0
    if n == 1:
        return 1
    # Factor out sign and powers of 2
    if n < 0:
        result = -1 if a < 0 else 1
        n = -n
    else:
        result = 1
    # Handle n = 2^e * m
    v2 = 0
    while n % 2 == 0:
        v2 += 1
        n //= 2
    if v2 > 0:
        if a % 2 == 0:
            if v2 > 0:
                # (a/2) for each power
                for _ in range(v2):
                    if a % 2 == 0:
                        return 0
                    a_mod8 = a % 8
                    if a_mod8 == 1 or a_mod8 == 7:
                        pass
                    else:
                        result = -result
        else:
            a_mod8 = a % 8
            for _ in range(v2):
                if a_mod8 == 1 or a_mod8 == 7:
                    pass
                else:
                    result = -result
    if n == 1:
        return result
    # Now n is odd > 1, compute Jacobi symbol (a/n)
    return result * jacobi_symbol(a, n)

def jacobi_symbol(a, n):
    """Compute the Jacobi symbol (a/n) for odd n > 0."""
    if n <= 0 or n % 2 == 0:
        raise ValueError(f"n must be odd positive, got {n}")
    a = a % n
    result = 1
    while a != 0:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a = a % n
    return result if n == 1 else 0


def quadratic_character(d, p):
    """Compute the quadratic character chi_d(p) = (d/p) Kronecker symbol."""
    if p == 2:
        # (d/2)
        d_mod8 = d % 8
        if d % 2 == 0:
            return 0
        if d_mod8 == 1 or d_mod8 == 7:
            return 1
        return -1
    return jacobi_symbol(d, p)


# Small fundamental discriminants for quadratic twists
FUNDAMENTAL_DISCS = []
for d in range(-200, 201):
    if d == 0:
        continue
    # Check if d is a fundamental discriminant
    ad = abs(d)
    if d % 4 == 1:
        # d ≡ 1 mod 4, squarefree
        sqfree = True
        for p in [2, 3, 5, 7, 11, 13]:
            if p * p <= ad and ad % (p * p) == 0:
                sqfree = False
                break
        if sqfree:
            FUNDAMENTAL_DISCS.append(d)
    elif d % 4 == 0:
        # d = 4m where m ≡ 2 or 3 mod 4 and m squarefree
        m = d // 4
        if m % 4 in (2, 3) or (d < 0 and m % 4 in (2, 3)):
            am = abs(m)
            sqfree = True
            for p in [2, 3, 5, 7, 11, 13]:
                if p * p <= am and am % (p * p) == 0:
                    sqfree = False
                    break
            if sqfree:
                FUNDAMENTAL_DISCS.append(d)

# Deduplicate and sort
FUNDAMENTAL_DISCS = sorted(set(FUNDAMENTAL_DISCS))

# Small Dirichlet characters by conductor
def dirichlet_characters(conductor):
    """Return all Dirichlet characters of given conductor as functions p -> value.
    Returns list of (label, chi_func) pairs. Only non-trivial ones."""
    chars = []
    if conductor == 3:
        # chi_3: 1->1, 2->-1, 0->0 (Legendre-like)
        def chi3(n):
            r = n % 3
            if r == 0: return 0
            return 1 if r == 1 else -1
        chars.append(("chi_3", chi3))
    elif conductor == 4:
        def chi4(n):
            r = n % 4
            if r == 0 or r == 2: return 0
            return 1 if r == 1 else -1
        chars.append(("chi_4", chi4))
    elif conductor == 5:
        def chi5_2(n):
            r = n % 5
            if r == 0: return 0
            return {1: 1, 2: -1, 3: -1, 4: 1}[r]
        chars.append(("chi_5_quad", chi5_2))
    elif conductor == 7:
        def chi7(n):
            r = n % 7
            if r == 0: return 0
            return {1: 1, 2: 1, 3: -1, 4: 1, 5: -1, 6: -1}[r]
        chars.append(("chi_7_quad", chi7))
    elif conductor == 8:
        def chi8a(n):
            r = n % 8
            if r % 2 == 0: return 0
            return {1: 1, 3: -1, 5: -1, 7: 1}[r]
        def chi8b(n):
            r = n % 8
            if r % 2 == 0: return 0
            return {1: 1, 3: 1, 5: -1, 7: -1}[r]
        chars.append(("chi_8a", chi8a))
        chars.append(("chi_8b", chi8b))
    return chars


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_modular_forms():
    """Load weight-2 dim-1 modular forms from DuckDB."""
    import duckdb
    conn = duckdb.connect(str(Path(__file__).resolve().parents[4] / "charon" / "data" / "charon.duckdb"), read_only=True)
    rows = conn.execute("""
        SELECT lmfdb_label, level, traces, is_cm, self_twist_type, fricke_eigenval,
               sato_tate_group, char_order, related_objects
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND char_order = 1
        ORDER BY level, lmfdb_label
    """).fetchall()
    conn.close()

    forms = []
    for row in rows:
        label, level, traces, is_cm, self_twist, fricke, st_group, char_order, related = row
        if traces is None or len(traces) < 100:
            continue
        # Extract a_p at prime indices (traces is 1-indexed: traces[0] = a_1, traces[1] = a_2, ...)
        ap = {}
        for p in PRIMES_1000:
            if p <= len(traces):
                ap[p] = traces[p - 1]  # traces[n-1] = a_n
        forms.append({
            "label": label,
            "level": level,
            "traces": traces,
            "ap": ap,
            "is_cm": bool(is_cm),
            "self_twist_type": self_twist,
            "fricke": fricke,
            "st_group": st_group,
            "related": related or [],
        })
    return forms


# ---------------------------------------------------------------------------
# Task 1: Quadratic Twist Detection
# ---------------------------------------------------------------------------

def detect_quadratic_twists(forms, max_level=500):
    """Detect quadratic twist pairs among forms at the same level."""
    print(f"\n=== Task 1: Quadratic Twist Detection (levels <= {max_level}) ===")
    t0 = time.time()

    # Group by level
    by_level = defaultdict(list)
    for f in forms:
        if f["level"] <= max_level:
            by_level[f["level"]].append(f)

    test_primes = [p for p in PRIMES_1000 if p <= 200]
    twist_pairs = []
    pairs_tested = 0

    for level, level_forms in sorted(by_level.items()):
        if len(level_forms) < 2:
            continue
        for i in range(len(level_forms)):
            for j in range(i + 1, len(level_forms)):
                f, g = level_forms[i], level_forms[j]
                pairs_tested += 1

                # Get good primes (not dividing level)
                good_primes = [p for p in test_primes if level % p != 0 and p in f["ap"] and p in g["ap"]]
                if len(good_primes) < 10:
                    continue

                # Check each fundamental discriminant
                for d in FUNDAMENTAL_DISCS:
                    if d == 1:
                        continue
                    match = True
                    mismatches = 0
                    tested = 0
                    for p in good_primes:
                        chi_p = quadratic_character(d, p)
                        if chi_p == 0:
                            continue  # p divides conductor of chi
                        tested += 1
                        expected = f["ap"][p] * chi_p
                        if abs(expected - g["ap"][p]) > 0.5:
                            mismatches += 1
                            if mismatches > 1:
                                match = False
                                break

                    if match and tested >= 8 and mismatches == 0:
                        twist_pairs.append({
                            "form_f": f["label"],
                            "form_g": g["label"],
                            "level": level,
                            "discriminant": d,
                            "primes_tested": tested,
                        })
                        break  # Found the twist for this pair

    elapsed = time.time() - t0
    print(f"  Pairs tested: {pairs_tested}")
    print(f"  Twist pairs found: {len(twist_pairs)}")
    if twist_pairs:
        print(f"  Examples:")
        for tp in twist_pairs[:10]:
            print(f"    {tp['form_f']} <-> {tp['form_g']}, d={tp['discriminant']}, tested={tp['primes_tested']}")
    print(f"  Time: {elapsed:.1f}s")

    return {
        "pairs_tested": pairs_tested,
        "twist_pairs_found": len(twist_pairs),
        "pairs": twist_pairs[:100],
        "levels_scanned": len(by_level),
        "elapsed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Task 2: Character Invariance Scan
# ---------------------------------------------------------------------------

def character_invariance_scan(forms, max_level=300):
    """Check if twisting a form by a small Dirichlet character yields another form."""
    print(f"\n=== Task 2: Character Invariance Scan (levels <= {max_level}) ===")
    t0 = time.time()

    # Build signature index: for each form, compute a hash from first few a_p values
    # Then for each twist, check if the twisted signature matches any form
    conductors = [3, 4, 5, 7, 8]
    test_primes = [p for p in PRIMES_1000 if p <= 100]

    # Build lookup: tuple of a_p values -> form label
    sig_to_label = {}
    candidate_forms = [f for f in forms if f["level"] <= max_level]

    for f in candidate_forms:
        sig = tuple(int(f["ap"].get(p, 0)) for p in test_primes)
        sig_to_label[sig] = f["label"]

    matches = []
    forms_scanned = 0

    for f in candidate_forms:
        forms_scanned += 1
        for cond in conductors:
            chars = dirichlet_characters(cond)
            for char_label, chi in chars:
                # Twist: a_p * chi(p)
                twisted_sig = []
                valid = True
                for p in test_primes:
                    chi_val = chi(p)
                    if chi_val == 0:
                        twisted_sig.append(0)  # Mark as unknown
                        continue
                    twisted_sig.append(int(f["ap"].get(p, 0) * chi_val))

                twisted_sig = tuple(twisted_sig)

                # Check against all forms — but we need to handle the chi(p)=0 entries
                # Do a more careful comparison
                for g in candidate_forms:
                    if g["label"] == f["label"]:
                        continue
                    match_count = 0
                    mismatch_count = 0
                    for k, p in enumerate(test_primes):
                        chi_val = chi(p)
                        if chi_val == 0 or f["level"] % p == 0 or g["level"] % p == 0:
                            continue
                        expected = f["ap"][p] * chi_val
                        if abs(expected - g["ap"][p]) < 0.5:
                            match_count += 1
                        else:
                            mismatch_count += 1
                            if mismatch_count > 1:
                                break

                    if match_count >= 8 and mismatch_count == 0:
                        # Avoid duplicate pairs
                        pair_key = tuple(sorted([f["label"], g["label"]]))
                        matches.append({
                            "form_f": f["label"],
                            "form_g": g["label"],
                            "character": char_label,
                            "conductor": cond,
                            "primes_matched": match_count,
                        })

    # Deduplicate
    seen = set()
    unique_matches = []
    for m in matches:
        key = (tuple(sorted([m["form_f"], m["form_g"]])), m["character"])
        if key not in seen:
            seen.add(key)
            unique_matches.append(m)

    elapsed = time.time() - t0
    print(f"  Forms scanned: {forms_scanned}")
    print(f"  Character-twist matches: {len(unique_matches)}")
    if unique_matches:
        print(f"  Examples:")
        for m in unique_matches[:10]:
            print(f"    {m['form_f']} --[{m['character']}]--> {m['form_g']} ({m['primes_matched']} primes)")
    print(f"  Time: {elapsed:.1f}s")

    return {
        "forms_scanned": forms_scanned,
        "matches_found": len(unique_matches),
        "matches": unique_matches[:100],
        "elapsed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Task 3: Sign Pattern Detection
# ---------------------------------------------------------------------------

def sign_pattern_detection(forms, max_forms=5000):
    """Cluster forms by sign patterns of a_p."""
    print(f"\n=== Task 3: Sign Pattern Detection ===")
    t0 = time.time()

    primes_for_sign = PRIMES_100  # p = 2, 3, 5, ..., 97

    # Compute sign vectors
    sign_data = []
    for f in forms[:max_forms]:
        signs = []
        for p in primes_for_sign:
            val = f["ap"].get(p, 0)
            if f["level"] % p == 0:
                signs.append(0)  # bad prime
            elif val > 0:
                signs.append(1)
            elif val < 0:
                signs.append(-1)
            else:
                signs.append(0)
        sign_data.append({
            "label": f["label"],
            "level": f["level"],
            "is_cm": f["is_cm"],
            "signs": signs,
        })

    # Compute zero-fraction for each form (proxy for CM detection)
    zero_fracs = []
    for sd in sign_data:
        good_primes = [i for i, p in enumerate(primes_for_sign) if sd["signs"][i] != 0 or forms[0]["level"] % p != 0]
        # Count zeros at good primes
        n_good = 0
        n_zero = 0
        for i, p in enumerate(primes_for_sign):
            level = sd["level"]
            if level % p != 0:  # good prime
                n_good += 1
                ap_val = 0
                for f in forms:
                    if f["label"] == sd["label"]:
                        ap_val = f["ap"].get(p, 0)
                        break
                if abs(ap_val) < 0.5:
                    n_zero += 1
        zero_fracs.append({
            "label": sd["label"],
            "is_cm": sd["is_cm"],
            "zero_frac": n_zero / max(n_good, 1),
            "n_good": n_good,
            "n_zero": n_zero,
        })

    # Sign pattern clustering via Hamming distance
    # Instead of full pairwise (too expensive), group by exact sign pattern
    pattern_groups = defaultdict(list)
    for sd in sign_data:
        # Use only signs at universally good primes (p > 5 to avoid common bad primes)
        key_primes = [i for i, p in enumerate(primes_for_sign) if p > 5 and sd["level"] % p != 0]
        pattern = tuple(sd["signs"][i] for i in key_primes[:20])  # First 20 good primes > 5
        pattern_groups[pattern].append(sd["label"])

    # Find clusters of size > 1
    clusters = {str(k): v for k, v in pattern_groups.items() if len(v) > 1}
    cluster_sizes = sorted([len(v) for v in clusters.values()], reverse=True)

    # Check CM correlation
    cm_labels = {f["label"] for f in forms if f["is_cm"]}
    cm_in_clusters = 0
    non_cm_in_clusters = 0
    for members in clusters.values():
        for label in members:
            if label in cm_labels:
                cm_in_clusters += 1
            else:
                non_cm_in_clusters += 1

    elapsed = time.time() - t0
    print(f"  Forms analyzed: {len(sign_data)}")
    print(f"  Unique sign patterns: {len(pattern_groups)}")
    print(f"  Clusters (size > 1): {len(clusters)}")
    if cluster_sizes:
        print(f"  Largest clusters: {cluster_sizes[:10]}")
    print(f"  CM in clusters: {cm_in_clusters}, non-CM in clusters: {non_cm_in_clusters}")
    print(f"  Time: {elapsed:.1f}s")

    return {
        "forms_analyzed": len(sign_data),
        "unique_patterns": len(pattern_groups),
        "clusters_gt1": len(clusters),
        "cluster_size_distribution": cluster_sizes[:20],
        "cm_in_clusters": cm_in_clusters,
        "non_cm_in_clusters": non_cm_in_clusters,
        "sample_clusters": {k: v for k, v in list(clusters.items())[:10]},
        "elapsed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Task 4: Shift Invariance in OEIS Algebraic Families
# ---------------------------------------------------------------------------

def load_oeis_sequences(seq_ids):
    """Load OEIS sequence values from stripped_new.txt for given sequence IDs."""
    stripped_path = Path(__file__).resolve().parents[3] / "oeis" / "data" / "stripped_new.txt"
    if not stripped_path.exists():
        return {}
    wanted = set(seq_ids)
    result = {}
    with open(stripped_path, "r") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split(" ", 1)
            if len(parts) < 2:
                continue
            sid = parts[0]
            if sid not in wanted:
                continue
            vals_str = parts[1].strip().rstrip(",").lstrip(",")
            try:
                vals = [int(v) for v in vals_str.split(",") if v.strip()]
                if len(vals) >= 5:
                    result[sid] = vals
            except ValueError:
                continue
    return result


def oeis_shift_invariance():
    """Test shift/scale/twist relationships in OEIS algebraic DNA families."""
    print(f"\n=== Task 4: OEIS Shift/Scale/Twist Invariance ===")
    t0 = time.time()

    # Load algebraic DNA results
    dna_path = Path(__file__).parent / "algebraic_dna_fungrim_results.json"
    if not dna_path.exists():
        print("  No algebraic DNA results found — skipping")
        return {"status": "skipped", "reason": "no algebraic_dna_fungrim_results.json"}

    with open(dna_path) as fh:
        dna_data = json.load(fh)

    # Extract families: groups of OEIS sequences sharing a characteristic polynomial
    # Use top_interesting_connections which has sample_sequences grouped by char_poly
    raw_families = {}
    for cluster in dna_data.get("top_interesting_connections", []):
        if isinstance(cluster, dict):
            key = cluster.get("char_poly_str", "")
            seqs = cluster.get("sample_sequences", [])
            if key and len(seqs) >= 2:
                raw_families[key] = seqs[:20]  # Cap at 20 per family

    # Also include all_cluster_results with >= 2 sequences
    for cluster in dna_data.get("all_cluster_results", []):
        if isinstance(cluster, dict):
            key = cluster.get("char_poly_str", "")
            seqs = cluster.get("fungrim_direct_refs", [])
            if key and len(seqs) >= 2 and key not in raw_families:
                raw_families[key] = seqs[:20]

    # Collect all sequence IDs needed
    all_ids = set()
    for seqs in raw_families.values():
        for sid in seqs:
            all_ids.add(sid)

    print(f"  Loading {len(all_ids)} OEIS sequences from stripped data...")
    oeis_data = load_oeis_sequences(all_ids)
    print(f"  Loaded {len(oeis_data)} sequences with values")

    shift_pairs = 0
    scale_pairs = 0
    twist_pairs = 0
    negation_pairs = 0
    total_pairs = 0
    family_count = 0
    examples = {"shift": [], "scale": [], "twist": []}

    for family_key, seq_ids in raw_families.items():
        # Get sequences with values
        seqs = []
        for sid in seq_ids:
            if sid in oeis_data:
                seqs.append({"label": sid, "values": oeis_data[sid][:50]})
        if len(seqs) < 2:
            continue
        family_count += 1

        for i in range(len(seqs)):
            for j in range(i + 1, len(seqs)):
                total_pairs += 1
                a = np.array(seqs[i]["values"], dtype=float)
                b = np.array(seqs[j]["values"], dtype=float)
                minlen = min(len(a), len(b))
                if minlen < 5:
                    continue

                found_relation = None

                # Test shift: a(n) = b(n+k)
                for k in range(1, min(8, minlen - 4)):
                    if np.allclose(a[:minlen-k], b[k:minlen], atol=0.5):
                        shift_pairs += 1
                        found_relation = f"shift(+{k})"
                        break
                    if np.allclose(b[:minlen-k], a[k:minlen], atol=0.5):
                        shift_pairs += 1
                        found_relation = f"shift(-{k})"
                        break

                # Test scale: a(n) = c * b(n)
                if found_relation is None:
                    a_t = a[:minlen]
                    b_t = b[:minlen]
                    nonzero = np.abs(b_t) > 0.5
                    if np.sum(nonzero) >= 5:
                        ratios = a_t[nonzero] / b_t[nonzero]
                        if np.std(ratios) < 1e-6 * (np.abs(np.mean(ratios)) + 1):
                            c = np.mean(ratios)
                            if abs(c) > 1e-6 and abs(c - 1.0) > 1e-6:
                                scale_pairs += 1
                                found_relation = f"scale({c:.4g})"

                # Test twist: a(n) = chi(n) * b(n) for alternating signs
                if found_relation is None:
                    a_t = a[:minlen]
                    b_t = b[:minlen]
                    if np.allclose(np.abs(a_t), np.abs(b_t), atol=0.5):
                        nonzero_both = (np.abs(a_t) > 0.5) & (np.abs(b_t) > 0.5)
                        if np.sum(nonzero_both) >= 5:
                            sign_ratio = np.sign(a_t[nonzero_both]) * np.sign(b_t[nonzero_both])
                            if np.all(sign_ratio == -1):
                                negation_pairs += 1
                                found_relation = "negation"
                            elif not np.all(sign_ratio == 1):
                                twist_pairs += 1
                                found_relation = "twist"

                if found_relation and len(examples.get(found_relation.split("(")[0], [])) < 5:
                    cat = found_relation.split("(")[0]
                    if cat in examples:
                        examples[cat].append({
                            "a": seqs[i]["label"], "b": seqs[j]["label"],
                            "family": family_key, "relation": found_relation
                        })

    elapsed = time.time() - t0
    total_classified = shift_pairs + scale_pairs + twist_pairs + negation_pairs

    print(f"  Families with loaded data: {family_count}")
    print(f"  Total pairs tested: {total_pairs}")
    print(f"  Shift pairs: {shift_pairs}")
    print(f"  Scale pairs: {scale_pairs}")
    print(f"  Negation pairs: {negation_pairs}")
    print(f"  Twist pairs: {twist_pairs}")
    if total_pairs > 0:
        print(f"  Classified fraction: {total_classified}/{total_pairs} = {total_classified/total_pairs:.1%}")
    if examples["shift"]:
        print(f"  Shift examples:")
        for ex in examples["shift"][:3]:
            print(f"    {ex['a']} <-> {ex['b']} [{ex['relation']}] (family: {ex['family'][:40]})")
    if examples["scale"]:
        print(f"  Scale examples:")
        for ex in examples["scale"][:3]:
            print(f"    {ex['a']} <-> {ex['b']} [{ex['relation']}] (family: {ex['family'][:40]})")
    print(f"  Time: {elapsed:.1f}s")

    return {
        "families_analyzed": family_count,
        "total_pairs": total_pairs,
        "shift_pairs": shift_pairs,
        "scale_pairs": scale_pairs,
        "negation_pairs": negation_pairs,
        "twist_pairs": twist_pairs,
        "classified_fraction": total_classified / max(total_pairs, 1),
        "examples": examples,
        "elapsed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Task 5: CM Rediscovery Without Labels
# ---------------------------------------------------------------------------

def cm_rediscovery(forms):
    """Detect CM forms from a_p = 0 frequency without using the CM label."""
    print(f"\n=== Task 5: CM Rediscovery Test ===")
    t0 = time.time()

    # For CM forms, a_p = 0 for ~50% of good primes (those inert in CM field)
    # For non-CM forms, a_p = 0 is very rare

    test_primes = [p for p in PRIMES_1000 if p <= 500]

    zero_fracs = []
    for f in forms:
        level = f["level"]
        n_good = 0
        n_zero = 0
        for p in test_primes:
            if level % p != 0 and p in f["ap"]:
                n_good += 1
                if abs(f["ap"][p]) < 0.5:
                    n_zero += 1
        frac = n_zero / max(n_good, 1)
        zero_fracs.append({
            "label": f["label"],
            "level": level,
            "is_cm": f["is_cm"],
            "zero_frac": frac,
            "n_good": n_good,
            "n_zero": n_zero,
        })

    # Classification: predict CM if zero_frac > threshold
    # Find optimal threshold
    zero_fracs.sort(key=lambda x: x["zero_frac"], reverse=True)

    # CM forms should cluster around 50% zeros
    cm_zero_fracs = [z["zero_frac"] for z in zero_fracs if z["is_cm"]]
    non_cm_zero_fracs = [z["zero_frac"] for z in zero_fracs if not z["is_cm"]]

    cm_mean = np.mean(cm_zero_fracs) if cm_zero_fracs else 0
    cm_min = np.min(cm_zero_fracs) if cm_zero_fracs else 0
    non_cm_max = np.max(non_cm_zero_fracs) if non_cm_zero_fracs else 0
    non_cm_mean = np.mean(non_cm_zero_fracs) if non_cm_zero_fracs else 0

    # Sweep thresholds
    best_threshold = 0.3
    best_f1 = 0
    for thresh in np.arange(0.1, 0.6, 0.01):
        tp = sum(1 for z in zero_fracs if z["zero_frac"] > thresh and z["is_cm"])
        fp = sum(1 for z in zero_fracs if z["zero_frac"] > thresh and not z["is_cm"])
        fn = sum(1 for z in zero_fracs if z["zero_frac"] <= thresh and z["is_cm"])
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        f1 = 2 * precision * recall / max(precision + recall, 1e-10)
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = thresh

    # Apply best threshold
    tp = sum(1 for z in zero_fracs if z["zero_frac"] > best_threshold and z["is_cm"])
    fp = sum(1 for z in zero_fracs if z["zero_frac"] > best_threshold and not z["is_cm"])
    fn = sum(1 for z in zero_fracs if z["zero_frac"] <= best_threshold and z["is_cm"])
    tn = sum(1 for z in zero_fracs if z["zero_frac"] <= best_threshold and not z["is_cm"])

    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    accuracy = (tp + tn) / len(zero_fracs)

    # Top predictions vs ground truth
    top_predictions = [z for z in zero_fracs if z["zero_frac"] > best_threshold]

    elapsed = time.time() - t0
    print(f"  Total forms: {len(forms)}")
    print(f"  Known CM: {len(cm_zero_fracs)}")
    print(f"  CM mean zero-frac: {cm_mean:.4f}")
    print(f"  CM min zero-frac: {cm_min:.4f}")
    print(f"  Non-CM max zero-frac: {non_cm_max:.4f}")
    print(f"  Non-CM mean zero-frac: {non_cm_mean:.4f}")
    print(f"  Best threshold: {best_threshold:.2f}")
    print(f"  TP={tp}, FP={fp}, FN={fn}, TN={tn}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall: {recall:.4f}")
    print(f"  F1: {best_f1:.4f}")
    print(f"  Accuracy: {accuracy:.6f}")

    # Show misclassifications
    false_positives = [z for z in zero_fracs if z["zero_frac"] > best_threshold and not z["is_cm"]]
    false_negatives = [z for z in zero_fracs if z["zero_frac"] <= best_threshold and z["is_cm"]]

    if false_positives:
        print(f"  False positives ({len(false_positives)}):")
        for fp_item in false_positives[:5]:
            print(f"    {fp_item['label']}: zero_frac={fp_item['zero_frac']:.4f}")
    if false_negatives:
        print(f"  False negatives ({len(false_negatives)}):")
        for fn_item in false_negatives[:5]:
            print(f"    {fn_item['label']}: zero_frac={fn_item['zero_frac']:.4f}")

    print(f"  Time: {elapsed:.1f}s")

    return {
        "total_forms": len(forms),
        "known_cm": len(cm_zero_fracs),
        "cm_mean_zero_frac": round(cm_mean, 4),
        "cm_min_zero_frac": round(cm_min, 4),
        "non_cm_max_zero_frac": round(non_cm_max, 4),
        "non_cm_mean_zero_frac": round(non_cm_mean, 4),
        "best_threshold": round(best_threshold, 2),
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(best_f1, 4),
        "accuracy": round(accuracy, 6),
        "false_positives": [{"label": z["label"], "zero_frac": round(z["zero_frac"], 4)} for z in false_positives[:20]],
        "false_negatives": [{"label": z["label"], "zero_frac": round(z["zero_frac"], 4)} for z in false_negatives[:20]],
        "elapsed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Extended Task 1: Cross-level twist detection
# ---------------------------------------------------------------------------

def cross_level_twist_detection(forms, max_level=200):
    """Detect twists between forms at DIFFERENT levels.
    If f has level N and g = f ⊗ chi_d, then g has level N * |d| (roughly).
    """
    print(f"\n=== Extended: Cross-Level Twist Detection (levels <= {max_level}) ===")
    t0 = time.time()

    candidate_forms = [f for f in forms if f["level"] <= max_level]
    test_primes = [p for p in PRIMES_1000 if p <= 150]

    # For each form f at level N, and each small discriminant d,
    # compute the twisted a_p sequence and search for a match

    # Build lookup by (approximate) a_p signature
    # Use a_p at p=2,3,5,7,11,13 (the first few primes) as a quick filter
    filter_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    sig_index = defaultdict(list)
    for f in candidate_forms:
        sig = tuple(int(f["ap"].get(p, -9999)) for p in filter_primes if f["level"] % p != 0)
        sig_index[sig].append(f)

    cross_twists = []
    small_discs = [d for d in FUNDAMENTAL_DISCS if 1 < abs(d) <= 20]

    for f in candidate_forms:
        for d in small_discs:
            # Compute twisted signature
            twisted_sig = []
            for p in filter_primes:
                if f["level"] % p != 0:
                    chi_val = quadratic_character(d, p)
                    if chi_val == 0:
                        twisted_sig.append(int(f["ap"].get(p, -9999)))
                    else:
                        twisted_sig.append(int(f["ap"].get(p, 0) * chi_val))
            twisted_sig = tuple(twisted_sig)

            # Check index
            if twisted_sig in sig_index:
                for g in sig_index[twisted_sig]:
                    if g["label"] == f["label"]:
                        continue
                    if g["level"] == f["level"]:
                        continue  # Same level handled by Task 1

                    # Full verification
                    good_primes = [p for p in test_primes
                                   if f["level"] % p != 0 and g["level"] % p != 0
                                   and p in f["ap"] and p in g["ap"]]
                    match = 0
                    mismatch = 0
                    for p in good_primes:
                        chi_val = quadratic_character(d, p)
                        if chi_val == 0:
                            continue
                        expected = f["ap"][p] * chi_val
                        if abs(expected - g["ap"][p]) < 0.5:
                            match += 1
                        else:
                            mismatch += 1
                            if mismatch > 1:
                                break

                    if match >= 10 and mismatch == 0:
                        pair_key = tuple(sorted([f["label"], g["label"]]))
                        cross_twists.append({
                            "form_f": f["label"],
                            "form_g": g["label"],
                            "level_f": f["level"],
                            "level_g": g["level"],
                            "discriminant": d,
                            "primes_matched": match,
                        })

    # Deduplicate
    seen = set()
    unique_cross = []
    for ct in cross_twists:
        key = tuple(sorted([ct["form_f"], ct["form_g"]]))
        if key not in seen:
            seen.add(key)
            unique_cross.append(ct)

    elapsed = time.time() - t0
    print(f"  Cross-level twist pairs: {len(unique_cross)}")
    if unique_cross:
        print(f"  Examples:")
        for ct in unique_cross[:10]:
            print(f"    {ct['form_f']} (N={ct['level_f']}) <-d={ct['discriminant']}-> {ct['form_g']} (N={ct['level_g']}), {ct['primes_matched']} primes")
    print(f"  Time: {elapsed:.1f}s")

    return {
        "cross_level_pairs": len(unique_cross),
        "pairs": unique_cross[:50],
        "elapsed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("LAYER 3: Symmetry Group Detection via Action, Not Labels")
    print("=" * 70)

    print("\nLoading modular forms...")
    forms = load_modular_forms()
    print(f"  Loaded {len(forms)} weight-2 dim-1 forms")
    print(f"  CM forms: {sum(1 for f in forms if f['is_cm'])}")
    print(f"  Level range: {min(f['level'] for f in forms)} - {max(f['level'] for f in forms)}")

    results = {}

    # Task 1: Quadratic twist detection
    results["quadratic_twists"] = detect_quadratic_twists(forms, max_level=500)

    # Extended: Cross-level twists
    results["cross_level_twists"] = cross_level_twist_detection(forms, max_level=200)

    # Task 2: Character invariance
    results["character_invariance"] = character_invariance_scan(forms, max_level=300)

    # Task 3: Sign patterns
    results["sign_patterns"] = sign_pattern_detection(forms, max_forms=5000)

    # Task 4: OEIS shift invariance
    results["oeis_shift"] = oeis_shift_invariance()

    # Task 5: CM rediscovery
    results["cm_rediscovery"] = cm_rediscovery(forms)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    qt = results["quadratic_twists"]
    print(f"  Quadratic twist pairs (same level): {qt['twist_pairs_found']}")
    clt = results["cross_level_twists"]
    print(f"  Cross-level twist pairs: {clt['cross_level_pairs']}")
    ci = results["character_invariance"]
    print(f"  Character-twist matches: {ci['matches_found']}")
    sp = results["sign_patterns"]
    print(f"  Sign pattern clusters: {sp['clusters_gt1']}")
    oi = results["oeis_shift"]
    if "classified_fraction" in oi:
        print(f"  OEIS shift/scale/twist fraction: {oi['classified_fraction']:.1%}")
    cm = results["cm_rediscovery"]
    print(f"  CM rediscovery: P={cm['precision']:.2f} R={cm['recall']:.2f} F1={cm['f1']:.2f}")

    # Save
    out_path = Path(__file__).parent / "symmetry_detection_results.json"
    with open(out_path, "w") as fh:
        json.dump(results, fh, indent=2, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
