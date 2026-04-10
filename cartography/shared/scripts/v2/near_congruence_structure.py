#!/usr/bin/env python3
"""
M14: Structure of Near-Congruences (80-99% agreement at ell=3)
==============================================================
M12 found 1,131 pairs at ell=3 that agree at 80-99% of shared positions.
These are NOT full congruences (fail at 1-5 primes) but NOT random.

Analysis:
  1. Identify the 1,131 near-congruence pairs
  2. For each pair, identify exactly WHICH primes they disagree at
  3. "Disagreement prime" analysis: fragile primes, bad-prime correlation
  4. Classify: Type A (1 disagreement), B (2-3), C (4-5)
  5. Type A deep dive: what's special about the single disagreeing prime?
  6. Galois image correlation across near-congruence pairs

Charon / Project Prometheus — 2026-04-10
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
OUT_PATH = Path(__file__).resolve().parent / "near_congruence_results.json"

PRIMES_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
             31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
             73, 79, 83, 89, 97]

ELL = 3
N_SAMPLE = 2000
RNG_SEED = 42

# Galois image classification config (from galois_image_portraits.py)
TEST_ELLS = [2, 3, 5, 7]
MIN_GOOD = 30


def sieve(n):
    s = [True] * (n + 1)
    s[0] = s[1] = False
    for i in range(2, int(n**0.5) + 1):
        if s[i]:
            for j in range(i * i, n + 1, i):
                s[j] = False
    return [i for i in range(2, n + 1) if s[i]]


PRIMES_UP_TO_997 = sieve(997)


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


def load_forms():
    """Load all dim-1 weight-2 newforms from DuckDB."""
    print(f"[load] Connecting to {DB_PATH}")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    rows = con.execute('''
        SELECT lmfdb_label, level, traces
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND traces IS NOT NULL
        ORDER BY level, lmfdb_label
    ''').fetchall()
    con.close()
    print(f"[load] {len(rows)} forms loaded")
    return rows


def load_forms_with_ap():
    """Load forms with ap_coeffs for Galois image classification."""
    print(f"[galois] Loading forms with ap_coeffs...")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    rows = con.execute('''
        SELECT lmfdb_label, level, ap_coeffs, is_cm
        FROM modular_forms
        WHERE dim = 1 AND weight = 2 AND ap_coeffs IS NOT NULL
        ORDER BY level, lmfdb_label
    ''').fetchall()
    con.close()
    print(f"[galois] {len(rows)} forms with ap_coeffs")
    return rows


def build_templates(ell):
    """Build theoretical trace distribution templates for Galois image types."""
    templates = {}

    # Full GL_2: near-uniform
    full = np.ones(ell) / ell
    templates["full"] = full

    # Borel: concentration on 0 and QR classes
    qr = {(x * x) % ell for x in range(ell)}
    borel = np.zeros(ell)
    for r in range(ell):
        if r == 0:
            borel[r] = (1.0 / ell) + (ell - 1) / (ell * ell)
        elif r in qr:
            borel[r] = 2.0 / (ell * (ell - 1)) * (ell - 1) / 2 + 1.0 / (ell * ell)
        else:
            borel[r] = 1.0 / (ell * ell)
    borel /= borel.sum()
    templates["borel"] = borel

    # Cartan (CM): a_p = 0 for half of primes
    cartan = np.ones(ell)
    cartan[0] = ell  # zero is (ell-1)/2 times more frequent
    cartan /= cartan.sum()
    templates["cartan"] = cartan

    # Normalizer of Cartan
    norm_cartan = np.ones(ell)
    norm_cartan[0] = (ell + 1) / 2
    norm_cartan /= norm_cartan.sum()
    templates["norm_cartan"] = norm_cartan

    return templates


def classify_galois_image(ap_list, level, ell, templates):
    """Classify a single form's mod-ell Galois image."""
    good_vals = [ap_list[i] for i, p in enumerate(PRIMES_UP_TO_997)
                 if i < len(ap_list) and level % p != 0 and p != ell]

    if len(good_vals) < MIN_GOOD:
        return None

    # Empirical distribution
    dist = np.zeros(ell)
    for v in good_vals:
        dist[v % ell] += 1
    dist /= dist.sum()

    # Chi-squared distance to each template
    best_class = None
    best_chi = float('inf')
    for name, template in templates.items():
        chi_sq = sum((dist[r] - template[r]) ** 2 / max(template[r], 1e-10)
                     for r in range(ell))
        if chi_sq < best_chi:
            best_chi = chi_sq
            best_class = name

    return best_class


def classify_all_galois(forms_ap, ell=3):
    """Classify all forms at a given ell. Returns dict label -> class."""
    templates = build_templates(ell)
    label_to_class = {}
    for label, level, ap_str, is_cm in forms_ap:
        try:
            ap = [int(x[0]) for x in json.loads(ap_str)]
        except Exception:
            continue
        cls = classify_galois_image(ap, level, ell, templates)
        if cls is not None:
            label_to_class[label] = cls
    return label_to_class


def compute_fingerprints(forms, ell):
    """
    Compute mod-ell fingerprints for all forms.
    Returns: (n_forms, 25) int16 array (-1 for bad primes), labels list, levels list
    """
    n = len(forms)
    fps = np.full((n, 25), -1, dtype=np.int16)
    labels = []
    levels = []
    for i, (label, level, traces) in enumerate(forms):
        labels.append(label)
        levels.append(level)
        bad = prime_factors(level)
        for j, p in enumerate(PRIMES_25):
            if p not in bad and (p - 1) < len(traces):
                ap = int(round(traces[p - 1]))
                fps[i, j] = ap % ell
    return fps, labels, levels


def find_near_congruences(fps, labels, levels, lo_frac=0.80, hi_frac=0.99):
    """
    Find all pairs with agreement fraction in [lo_frac, hi_frac).
    Returns list of dicts with pair details including disagreement primes.
    """
    n = fps.shape[0]
    valid = (fps >= 0)  # (n, 25) bool

    print(f"[pairs] Computing pairwise agreements for {n} forms...")

    # For 2000 forms, n*(n-1)/2 = ~2M pairs. Process in chunks to manage memory.
    near_pairs = []
    full_pairs = []
    n_total_pairs = 0

    for i in range(n):
        if i % 200 == 0 and i > 0:
            print(f"  Row {i}/{n}, found {len(near_pairs)} near-congruences, {len(full_pairs)} full so far")

        # Vectorized comparison of form i against forms j > i
        fps_i = fps[i]  # (25,)
        valid_i = valid[i]  # (25,)

        # Compare with all j > i
        fps_rest = fps[i+1:]  # (n-i-1, 25)
        valid_rest = valid[i+1:]

        both_valid = valid_i[np.newaxis, :] & valid_rest  # (n-i-1, 25)
        agree = (fps_i[np.newaxis, :] == fps_rest) & both_valid

        n_valid = both_valid.sum(axis=1)
        n_agree = agree.sum(axis=1)

        # Filter: need at least 15 shared positions
        usable = n_valid >= 15
        n_total_pairs += int(usable.sum())

        # Agreement fraction
        frac = np.zeros(len(n_valid))
        mask_nz = n_valid > 0
        frac[mask_nz] = n_agree[mask_nz].astype(float) / n_valid[mask_nz]

        # Near-congruences: 80-99% agreement
        near_mask = usable & (frac >= lo_frac) & (frac < hi_frac)
        near_indices = np.where(near_mask)[0]

        for idx in near_indices:
            j = i + 1 + idx
            bv = both_valid[idx]
            ag = agree[idx]
            # Positions where both valid but disagree
            disagree_positions = np.where(bv & ~ag)[0]
            disagree_primes = [PRIMES_25[pos] for pos in disagree_positions]
            # Positions where both valid and agree
            agree_positions = np.where(bv & ag)[0]

            near_pairs.append({
                "i": i,
                "j": j,
                "label_i": labels[i],
                "label_j": labels[j],
                "level_i": levels[i],
                "level_j": levels[j],
                "n_valid": int(n_valid[idx]),
                "n_agree": int(n_agree[idx]),
                "frac": float(frac[idx]),
                "n_disagree": len(disagree_primes),
                "disagree_primes": disagree_primes,
                "disagree_positions": disagree_positions.tolist(),
            })

        # Full congruences: 100% agreement
        full_mask = usable & (frac >= 0.99)
        full_indices = np.where(full_mask)[0]
        for idx in full_indices:
            j = i + 1 + idx
            full_pairs.append({
                "label_i": labels[i],
                "label_j": labels[j],
                "n_valid": int(n_valid[idx]),
                "n_agree": int(n_agree[idx]),
            })

    print(f"[pairs] Total usable pairs: {n_total_pairs:,}")
    print(f"[pairs] Near-congruences (80-99%): {len(near_pairs)}")
    print(f"[pairs] Full congruences (>=99%): {len(full_pairs)}")

    return near_pairs, full_pairs


def analyze_disagreement_primes(near_pairs):
    """Analyze patterns in disagreement primes."""
    print(f"\n[analysis] Analyzing disagreement primes across {len(near_pairs)} pairs...")

    # Count disagreements per prime
    prime_disagree_count = Counter()
    for pair in near_pairs:
        for p in pair["disagree_primes"]:
            prime_disagree_count[p] += 1

    # Total disagreements
    total_disagree = sum(prime_disagree_count.values())

    # Top fragile primes
    fragile_primes = prime_disagree_count.most_common()
    print(f"  Total disagreements: {total_disagree}")
    print(f"  Top 10 fragile primes:")
    for p, count in fragile_primes[:10]:
        pct = 100 * count / len(near_pairs)
        print(f"    p={p:3d}: {count:5d} pairs ({pct:.1f}%)")

    # Concentration: how many primes account for 50% of disagreements?
    cumulative = 0
    n_for_50 = 0
    for p, count in fragile_primes:
        cumulative += count
        n_for_50 += 1
        if cumulative >= total_disagree * 0.50:
            break

    print(f"  Primes needed for 50% of disagreements: {n_for_50}")

    # Bad prime correlation: for each disagreement prime, is it a bad prime for one/both forms?
    bad_prime_stats = {
        "disagree_at_bad_for_i": 0,
        "disagree_at_bad_for_j": 0,
        "disagree_at_bad_for_both": 0,
        "disagree_at_bad_for_neither": 0,
        "total_disagreements": 0,
    }

    for pair in near_pairs:
        bad_i = prime_factors(pair["level_i"])
        bad_j = prime_factors(pair["level_j"])
        for p in pair["disagree_primes"]:
            bad_prime_stats["total_disagreements"] += 1
            in_i = p in bad_i
            in_j = p in bad_j
            if in_i and in_j:
                bad_prime_stats["disagree_at_bad_for_both"] += 1
            elif in_i:
                bad_prime_stats["disagree_at_bad_for_i"] += 1
            elif in_j:
                bad_prime_stats["disagree_at_bad_for_j"] += 1
            else:
                bad_prime_stats["disagree_at_bad_for_neither"] += 1

    bad_for_either = (bad_prime_stats["disagree_at_bad_for_i"] +
                      bad_prime_stats["disagree_at_bad_for_j"] +
                      bad_prime_stats["disagree_at_bad_for_both"])
    pct_bad = 100 * bad_for_either / max(bad_prime_stats["total_disagreements"], 1)
    print(f"\n  Bad prime correlation:")
    print(f"    Disagree at bad prime for one/both: {bad_for_either} ({pct_bad:.1f}%)")
    print(f"    Disagree at good prime for both: {bad_prime_stats['disagree_at_bad_for_neither']} "
          f"({100 - pct_bad:.1f}%)")

    return {
        "prime_disagree_counts": {str(p): c for p, c in fragile_primes},
        "total_disagreements": total_disagree,
        "primes_for_50pct": n_for_50,
        "bad_prime_correlation": bad_prime_stats,
        "bad_prime_pct": round(pct_bad, 2),
    }


def classify_near_congruences(near_pairs):
    """Classify into Type A (1 disagree), B (2-3), C (4-5)."""
    print(f"\n[classify] Classifying {len(near_pairs)} near-congruences...")

    type_a = []  # exactly 1 disagreement
    type_b = []  # 2-3 disagreements
    type_c = []  # 4-5 disagreements
    type_other = []  # >5 (shouldn't happen for 80-99% of ~20-25 positions)

    for pair in near_pairs:
        nd = pair["n_disagree"]
        if nd == 1:
            type_a.append(pair)
        elif nd <= 3:
            type_b.append(pair)
        elif nd <= 5:
            type_c.append(pair)
        else:
            type_other.append(pair)

    print(f"  Type A (1 disagreement):   {len(type_a):5d}")
    print(f"  Type B (2-3 disagreements): {len(type_b):5d}")
    print(f"  Type C (4-5 disagreements): {len(type_c):5d}")
    print(f"  Other (>5):                 {len(type_other):5d}")

    return {
        "type_a": type_a,
        "type_b": type_b,
        "type_c": type_c,
        "type_other": type_other,
        "counts": {
            "A": len(type_a),
            "B": len(type_b),
            "C": len(type_c),
            "other": len(type_other),
        }
    }


def analyze_type_a(type_a_pairs):
    """Deep dive on Type A: single-disagreement pairs."""
    if not type_a_pairs:
        return {"n_pairs": 0, "note": "no Type A pairs found"}

    print(f"\n[type_a] Deep dive on {len(type_a_pairs)} Type A pairs...")

    # What prime do they disagree at?
    single_prime_counts = Counter()
    for pair in type_a_pairs:
        p = pair["disagree_primes"][0]
        single_prime_counts[p] += 1

    print(f"  Single disagreeing prime distribution:")
    for p, count in single_prime_counts.most_common():
        pct = 100 * count / len(type_a_pairs)
        print(f"    p={p:3d}: {count:4d} ({pct:.1f}%)")

    # Is the disagreeing prime a bad prime?
    bad_for_i = 0
    bad_for_j = 0
    bad_for_both = 0
    bad_for_neither = 0
    small_prime = 0  # p <= 7

    for pair in type_a_pairs:
        p = pair["disagree_primes"][0]
        in_bad_i = p in prime_factors(pair["level_i"])
        in_bad_j = p in prime_factors(pair["level_j"])
        if in_bad_i and in_bad_j:
            bad_for_both += 1
        elif in_bad_i:
            bad_for_i += 1
        elif in_bad_j:
            bad_for_j += 1
        else:
            bad_for_neither += 1
        if p <= 7:
            small_prime += 1

    total = len(type_a_pairs)
    print(f"\n  Bad prime analysis:")
    print(f"    Bad for form i only: {bad_for_i} ({100*bad_for_i/total:.1f}%)")
    print(f"    Bad for form j only: {bad_for_j} ({100*bad_for_j/total:.1f}%)")
    print(f"    Bad for both:        {bad_for_both} ({100*bad_for_both/total:.1f}%)")
    print(f"    Good for both:       {bad_for_neither} ({100*bad_for_neither/total:.1f}%)")
    print(f"    Small prime (<=7):   {small_prime} ({100*small_prime/total:.1f}%)")

    # Level relationship: do the forms share the same level?
    same_level = sum(1 for p in type_a_pairs if p["level_i"] == p["level_j"])
    # Level divisibility: does one level divide the other?
    level_divides = sum(1 for p in type_a_pairs
                        if p["level_i"] % p["level_j"] == 0 or p["level_j"] % p["level_i"] == 0)

    print(f"\n  Level relationship:")
    print(f"    Same level: {same_level} ({100*same_level/total:.1f}%)")
    print(f"    One divides other: {level_divides} ({100*level_divides/total:.1f}%)")

    # GCD of levels
    from math import gcd
    gcd_levels = Counter()
    for pair in type_a_pairs:
        g = gcd(pair["level_i"], pair["level_j"])
        gcd_levels[g] += 1
    top_gcds = gcd_levels.most_common(10)
    print(f"  Top GCD(level_i, level_j):")
    for g, count in top_gcds:
        print(f"    gcd={g}: {count}")

    # Disagreeing prime vs level
    disagree_is_level_i = sum(1 for p in type_a_pairs if p["disagree_primes"][0] == p["level_i"])
    disagree_is_level_j = sum(1 for p in type_a_pairs if p["disagree_primes"][0] == p["level_j"])
    disagree_divides_level = sum(1 for p in type_a_pairs
                                  if p["level_i"] % p["disagree_primes"][0] == 0
                                  or p["level_j"] % p["disagree_primes"][0] == 0)

    print(f"\n  Disagreeing prime vs level:")
    print(f"    p == level_i: {disagree_is_level_i}")
    print(f"    p == level_j: {disagree_is_level_j}")
    print(f"    p | level_i or level_j: {disagree_divides_level} ({100*disagree_divides_level/total:.1f}%)")

    return {
        "n_pairs": len(type_a_pairs),
        "single_prime_distribution": {str(p): c for p, c in single_prime_counts.most_common()},
        "bad_prime_analysis": {
            "bad_for_i_only": bad_for_i,
            "bad_for_j_only": bad_for_j,
            "bad_for_both": bad_for_both,
            "good_for_both": bad_for_neither,
            "small_prime_le7": small_prime,
        },
        "level_relationship": {
            "same_level": same_level,
            "one_divides_other": level_divides,
            "top_gcds": {str(g): c for g, c in top_gcds},
        },
        "disagree_prime_vs_level": {
            "p_equals_level_i": disagree_is_level_i,
            "p_equals_level_j": disagree_is_level_j,
            "p_divides_some_level": disagree_divides_level,
            "p_divides_some_level_pct": round(100 * disagree_divides_level / total, 2),
        },
        "example_pairs": [
            {
                "label_i": p["label_i"],
                "label_j": p["label_j"],
                "level_i": p["level_i"],
                "level_j": p["level_j"],
                "disagree_prime": p["disagree_primes"][0],
                "n_valid": p["n_valid"],
                "frac": round(p["frac"], 4),
            }
            for p in type_a_pairs[:20]
        ],
    }


def analyze_galois_correlation(near_pairs, galois_map):
    """Correlate near-congruences with Galois image classes."""
    print(f"\n[galois] Correlating near-congruences with Galois images...")

    # Pair class combinations
    pair_classes = Counter()
    classified_pairs = 0
    unclassified = 0

    for pair in near_pairs:
        ci = galois_map.get(pair["label_i"])
        cj = galois_map.get(pair["label_j"])
        if ci is None or cj is None:
            unclassified += 1
            continue
        classified_pairs += 1
        key = tuple(sorted([ci, cj]))
        pair_classes[key] += 1

    print(f"  Classified pairs: {classified_pairs}, unclassified: {unclassified}")
    print(f"  Pair class distribution:")
    for (c1, c2), count in pair_classes.most_common():
        pct = 100 * count / max(classified_pairs, 1)
        print(f"    {c1}-{c2}: {count} ({pct:.1f}%)")

    # Baseline: what fraction of ALL forms are in each class?
    class_counts = Counter(galois_map.values())
    total_classified_forms = sum(class_counts.values())
    print(f"\n  Background class distribution:")
    for cls, count in class_counts.most_common():
        print(f"    {cls}: {count} ({100*count/total_classified_forms:.1f}%)")

    # Expected pair distribution under independence
    expected_pair_dist = {}
    for c1 in class_counts:
        for c2 in class_counts:
            key = tuple(sorted([c1, c2]))
            p1 = class_counts[c1] / total_classified_forms
            p2 = class_counts[c2] / total_classified_forms
            if c1 == c2:
                expected = p1 * p2
            else:
                expected = 2 * p1 * p2
            expected_pair_dist[key] = expected_pair_dist.get(key, 0) + (0 if c1 != c2 else expected)
            if c1 != c2 and key not in expected_pair_dist:
                expected_pair_dist[key] = expected

    # Recalculate properly
    expected_pair_dist = {}
    classes = sorted(class_counts.keys())
    for i, c1 in enumerate(classes):
        for j, c2 in enumerate(classes):
            if j < i:
                continue
            key = (c1, c2)
            p1 = class_counts[c1] / total_classified_forms
            p2 = class_counts[c2] / total_classified_forms
            if c1 == c2:
                expected_pair_dist[key] = p1 * p2
            else:
                expected_pair_dist[key] = 2 * p1 * p2

    # Enrichment
    enrichments = {}
    print(f"\n  Enrichment of near-congruence pair classes vs background:")
    for (c1, c2), count in pair_classes.most_common():
        key = (c1, c2) if c1 <= c2 else (c2, c1)
        obs_frac = count / max(classified_pairs, 1)
        exp_frac = expected_pair_dist.get(key, 1e-10)
        enr = obs_frac / max(exp_frac, 1e-10)
        enrichments[f"{c1}-{c2}"] = round(enr, 2)
        if count >= 5:
            print(f"    {c1}-{c2}: obs={obs_frac:.4f}, exp={exp_frac:.4f}, enrichment={enr:.2f}x")

    return {
        "classified_pairs": classified_pairs,
        "unclassified_pairs": unclassified,
        "pair_class_distribution": {f"{c1}-{c2}": c for (c1, c2), c in pair_classes.most_common()},
        "background_class_distribution": {cls: count for cls, count in class_counts.most_common()},
        "enrichments": enrichments,
    }


def main():
    t_start = time.time()

    # ── Load forms ──
    forms_all = load_forms()
    n_total = len(forms_all)

    # ── Sample same 2000 forms as M12 ──
    rng = np.random.RandomState(RNG_SEED)
    if n_total > N_SAMPLE:
        indices = rng.choice(n_total, N_SAMPLE, replace=False)
        indices.sort()
        sampled_forms = [forms_all[i] for i in indices]
        print(f"[sample] Sampled {N_SAMPLE} from {n_total}")
    else:
        sampled_forms = forms_all

    # ── Compute fingerprints at ell=3 ──
    fps, labels, levels = compute_fingerprints(sampled_forms, ELL)
    print(f"[fps] Fingerprint matrix: {fps.shape}")

    # ── Find near-congruences ──
    near_pairs, full_pairs = find_near_congruences(fps, labels, levels)

    # ── Disagreement prime analysis ──
    disagree_analysis = analyze_disagreement_primes(near_pairs)

    # ── Classify near-congruences ──
    classification = classify_near_congruences(near_pairs)

    # ── Type A deep dive ──
    type_a_analysis = analyze_type_a(classification["type_a"])

    # ── Galois image correlation ──
    # Classify all sampled forms at ell=3
    print(f"\n[galois] Classifying Galois images for sampled forms...")
    forms_ap = load_forms_with_ap()
    # Build label lookup for sampled forms
    sampled_labels = set(labels)
    sampled_ap = [row for row in forms_ap if row[0] in sampled_labels]
    print(f"[galois] {len(sampled_ap)} sampled forms have ap_coeffs")

    galois_map = classify_all_galois(sampled_ap, ell=ELL)
    print(f"[galois] Classified {len(galois_map)} forms at ell={ELL}")

    galois_analysis = analyze_galois_correlation(near_pairs, galois_map)

    # ── Also correlate by type ──
    print(f"\n[galois-by-type] Galois correlation by near-congruence type:")
    galois_by_type = {}
    for type_name, pairs_list in [("A", classification["type_a"]),
                                   ("B", classification["type_b"]),
                                   ("C", classification["type_c"])]:
        if not pairs_list:
            galois_by_type[type_name] = {"n": 0}
            continue
        pair_classes = Counter()
        for pair in pairs_list:
            ci = galois_map.get(pair["label_i"])
            cj = galois_map.get(pair["label_j"])
            if ci and cj:
                key = tuple(sorted([ci, cj]))
                pair_classes[key] += 1
        galois_by_type[type_name] = {
            "n": len(pairs_list),
            "pair_classes": {f"{c1}-{c2}": c for (c1, c2), c in pair_classes.most_common()},
        }
        print(f"  Type {type_name}: {dict(pair_classes.most_common(5))}")

    # ── Disagreement pattern: is it concentrated or random? ──
    print(f"\n[pattern] Disagreement pattern analysis...")
    # For each pair, store the set of disagreeing primes
    # Check: do pairs tend to disagree at the SAME primes?
    disagree_sets = [frozenset(p["disagree_primes"]) for p in near_pairs]
    set_counts = Counter(disagree_sets)
    top_sets = set_counts.most_common(20)
    print(f"  Unique disagreement sets: {len(set_counts)}")
    print(f"  Top repeated sets:")
    for s, count in top_sets[:10]:
        if count >= 2:
            print(f"    {set(s)}: {count} pairs")

    # Entropy of disagreement sets
    n_pairs = len(disagree_sets)
    entropy = -sum((c / n_pairs) * math.log2(c / n_pairs) for c in set_counts.values())
    max_entropy = math.log2(n_pairs) if n_pairs > 0 else 0
    norm_entropy = entropy / max_entropy if max_entropy > 0 else 0
    print(f"  Entropy of disagreement sets: {entropy:.2f} bits (normalized: {norm_entropy:.3f})")

    # ── Assemble results ──
    elapsed = time.time() - t_start

    results = {
        "metadata": {
            "description": "M14: Structure of Near-Congruences (80-99% agreement at ell=3)",
            "ell": ELL,
            "n_forms_sampled": N_SAMPLE,
            "n_near_congruences": len(near_pairs),
            "n_full_congruences": len(full_pairs),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "elapsed_seconds": round(elapsed, 1),
        },
        "classification": {
            "counts": classification["counts"],
            "type_A_fraction": round(len(classification["type_a"]) / max(len(near_pairs), 1), 4),
            "type_B_fraction": round(len(classification["type_b"]) / max(len(near_pairs), 1), 4),
            "type_C_fraction": round(len(classification["type_c"]) / max(len(near_pairs), 1), 4),
        },
        "disagreement_prime_analysis": disagree_analysis,
        "type_a_deep_dive": type_a_analysis,
        "disagreement_pattern": {
            "unique_sets": len(set_counts),
            "top_repeated_sets": [
                {"primes": sorted(list(s)), "count": c}
                for s, c in top_sets if c >= 2
            ],
            "entropy_bits": round(entropy, 2),
            "normalized_entropy": round(norm_entropy, 3),
            "interpretation": (
                "high" if norm_entropy > 0.9 else
                "moderate" if norm_entropy > 0.7 else
                "concentrated"
            ),
        },
        "galois_image_correlation": galois_analysis,
        "galois_by_type": galois_by_type,
        "example_near_congruences": {
            "type_a": [
                {
                    "label_i": p["label_i"], "label_j": p["label_j"],
                    "level_i": p["level_i"], "level_j": p["level_j"],
                    "n_valid": p["n_valid"], "frac": round(p["frac"], 4),
                    "disagree_primes": p["disagree_primes"],
                }
                for p in classification["type_a"][:10]
            ],
            "type_b": [
                {
                    "label_i": p["label_i"], "label_j": p["label_j"],
                    "level_i": p["level_i"], "level_j": p["level_j"],
                    "n_valid": p["n_valid"], "frac": round(p["frac"], 4),
                    "disagree_primes": p["disagree_primes"],
                }
                for p in classification["type_b"][:10]
            ],
            "type_c": [
                {
                    "label_i": p["label_i"], "label_j": p["label_j"],
                    "level_i": p["level_i"], "level_j": p["level_j"],
                    "n_valid": p["n_valid"], "frac": round(p["frac"], 4),
                    "disagree_primes": p["disagree_primes"],
                }
                for p in classification["type_c"][:10]
            ],
        },
        "verdict": {},  # Filled below
    }

    # ── Verdict ──
    n_near = len(near_pairs)
    n_a = classification["counts"]["A"]
    n_b = classification["counts"]["B"]
    n_c = classification["counts"]["C"]
    bad_pct = disagree_analysis["bad_prime_pct"]
    n_unique_sets = len(set_counts)

    results["verdict"] = {
        "total_near_congruences": n_near,
        "type_distribution": f"A={n_a}, B={n_b}, C={n_c}",
        "disagreement_concentrated": norm_entropy < 0.85,
        "bad_prime_dominated": bad_pct > 50,
        "interpretation": (
            f"Found {n_near} near-congruence pairs at ell={ELL}. "
            f"Type A (single-prime disagreement): {n_a} ({100*n_a/max(n_near,1):.1f}%). "
            f"Disagreements occur at bad primes {bad_pct:.1f}% of the time. "
            f"Disagreement set entropy: {norm_entropy:.3f} "
            f"({'concentrated — specific primes are fragile' if norm_entropy < 0.85 else 'dispersed — disagreements spread across primes'}). "
        ),
    }

    # ── Save ──
    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n[done] Results saved to {OUT_PATH}")
    print(f"[done] Total time: {elapsed:.1f}s")

    # ── Summary ──
    print(f"\n{'='*70}")
    print(f"  M14 SUMMARY: Near-Congruence Structure at ell={ELL}")
    print(f"{'='*70}")
    print(f"  Near-congruences found: {n_near}")
    print(f"  Type A (1 disagree): {n_a} ({100*n_a/max(n_near,1):.1f}%)")
    print(f"  Type B (2-3):        {n_b} ({100*n_b/max(n_near,1):.1f}%)")
    print(f"  Type C (4-5):        {n_c} ({100*n_c/max(n_near,1):.1f}%)")
    print(f"  Disagree at bad prime: {bad_pct:.1f}%")
    print(f"  Disagreement entropy:  {norm_entropy:.3f}")
    print(f"  Top fragile primes: {[p for p, _ in Counter(disagree_analysis['prime_disagree_counts']).most_common(5)]}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
