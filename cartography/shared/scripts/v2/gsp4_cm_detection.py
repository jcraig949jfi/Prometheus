"""
GSp_4 CM Detection via Zero-Frequency — CT4 Applied to Genus-2
================================================================
CT4 showed CM is perfectly recoverable from a_p zero-frequency in GL_2.
This applies the same detector to genus-2 (GSp_4) curves:
  1. Compute a_p and b_p zero-frequencies for all 66K curves
  2. Compare zero-frequencies within the 37 mod-3 congruence pairs
  3. Distinguish geometric vs representation-theoretic pairs
  4. Validate against known end_alg (CM) classification

For genus-2 curve C, the Euler factor at good prime p is:
  L_p(T) = 1 - a_p*T + b_p*T^2 - a_p*p*T^3 + p^2*T^4

Zero-frequency = fraction of good primes where a_p = 0 (or b_p = 0).

Usage:
    python gsp4_cm_detection.py
"""

import re
import json
import time
from collections import defaultdict, Counter
from pathlib import Path
from math import sqrt


# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────

def sieve_primes(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]


def prime_factors(n):
    factors = set()
    d = 2
    while d * d <= abs(n):
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if abs(n) > 1:
        factors.add(abs(n))
    return factors


def parse_good_lfactors(s):
    result = {}
    matches = re.findall(r'\[(-?\d+),(-?\d+),(-?\d+)\]', s)
    for m in matches:
        p, a, b = int(m[0]), int(m[1]), int(m[2])
        result[p] = (a, b)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────────────────────

def load_raw_curves(filepath):
    """Load genus-2 curves from LMFDB raw dump with Euler factors."""
    curves = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(':')
            if len(parts) < 17:
                continue

            conductor = int(parts[1])
            st_group = parts[8]
            euler = parse_good_lfactors(parts[16] if len(parts) > 16 else "")
            if not euler:
                continue

            eqn = parts[3]

            curves.append({
                "conductor": conductor,
                "st_group": st_group,
                "eqn": eqn,
                "euler": euler,
                "n_primes": len(euler),
            })
    return curves


def load_lmfdb_dump(filepath):
    """Load the LMFDB dump JSON with end_alg metadata."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    records = {}
    for rec in data['records']:
        label = rec.get('label', '')
        cond = rec.get('cond')
        eqn = rec.get('eqn')
        end_alg = rec.get('end_alg', 'Q')
        geom_end_alg = rec.get('geom_end_alg', 'Q')
        st_group = rec.get('st_group', '')
        records[label] = {
            'cond': cond,
            'end_alg': end_alg,
            'geom_end_alg': geom_end_alg,
            'st_group': st_group,
            'eqn': eqn,
        }
    return records


# ─────────────────────────────────────────────────────────────────────────────
# Zero-frequency computation
# ─────────────────────────────────────────────────────────────────────────────

def compute_zero_freq(euler, bad_primes):
    """
    Compute a_p and b_p zero-frequencies for a genus-2 curve.

    Returns:
        dict with a_zf, b_zf, n_good, a_zeros, b_zeros
    """
    good_primes = sorted(p for p in euler.keys() if p not in bad_primes)
    if not good_primes:
        return None

    a_zeros = sum(1 for p in good_primes if euler[p][0] == 0)
    b_zeros = sum(1 for p in good_primes if euler[p][1] == 0)
    n = len(good_primes)

    return {
        "a_zf": a_zeros / n,
        "b_zf": b_zeros / n,
        "n_good": n,
        "a_zeros": a_zeros,
        "b_zeros": b_zeros,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Pair analysis
# ─────────────────────────────────────────────────────────────────────────────

def find_mod3_pairs(curves, conductors):
    """Re-derive the 37 mod-3 congruence pairs from raw data."""
    by_cond = defaultdict(list)
    for c in curves:
        by_cond[c["conductor"]].append(c)

    pairs = []
    for cond in conductors:
        if cond % 3 == 0:
            continue
        cond_curves = [c for c in by_cond[cond] if c["st_group"] == "USp(4)"]
        if len(cond_curves) < 2:
            continue

        # Dedup by Euler fingerprint
        classes = defaultdict(list)
        for c in cond_curves:
            primes_avail = sorted(c["euler"].keys())
            fp = tuple(c["euler"][p] for p in primes_avail[:20])
            classes[fp].append(c)

        class_list = list(classes.values())
        if len(class_list) < 2:
            continue

        # Find the mod-3 congruent pair
        found = False
        for i in range(len(class_list)):
            if found:
                break
            for j in range(i + 1, len(class_list)):
                c1 = class_list[i][0]
                c2 = class_list[j][0]
                bad = prime_factors(cond)
                common = sorted(set(c1["euler"].keys()) & set(c2["euler"].keys()))
                good = [p for p in common if p not in bad and p != 3]

                all_cong = True
                has_nz = False
                for p in good:
                    da = c1["euler"][p][0] - c2["euler"][p][0]
                    db = c1["euler"][p][1] - c2["euler"][p][1]
                    if da % 3 != 0 or db % 3 != 0:
                        all_cong = False
                        break
                    if da != 0 or db != 0:
                        has_nz = True

                if all_cong and has_nz:
                    pairs.append((cond, c1, c2))
                    found = True
                    break

    return pairs


def find_mod2_pairs(curves, mod2_data):
    """Load the 733 mod-2 irreducible pairs from stored results."""
    by_cond = defaultdict(list)
    for c in curves:
        by_cond[c["conductor"]].append(c)

    pairs = []
    for entry in mod2_data:
        cond = entry['conductor']
        if not entry.get('coprime', True) or not entry.get('both_USp4', True):
            continue
        if entry.get('irred_witnesses', 0) == 0:
            continue

        eqn1 = entry.get('eqn1', '')
        eqn2 = entry.get('eqn2', '')

        # Match curves by equation
        c1_match = None
        c2_match = None
        for c in by_cond[cond]:
            if c['eqn'] == eqn1:
                c1_match = c
            elif c['eqn'] == eqn2:
                c2_match = c

        if c1_match and c2_match:
            pairs.append((cond, c1_match, c2_match))

    return pairs


def classify_pair(zf1, zf2, threshold=0.05):
    """Classify a congruence pair by zero-frequency similarity."""
    if zf1 is None or zf2 is None:
        return "NO_DATA"

    a_diff = abs(zf1["a_zf"] - zf2["a_zf"])
    b_diff = abs(zf1["b_zf"] - zf2["b_zf"])

    cm_threshold = 0.3
    generic_threshold = 0.1

    both_cm = zf1["a_zf"] > cm_threshold and zf2["a_zf"] > cm_threshold
    both_generic = zf1["a_zf"] < generic_threshold and zf2["a_zf"] < generic_threshold

    if both_cm:
        category = "BOTH_CM_LIKE"
    elif both_generic:
        category = "BOTH_GENERIC"
    else:
        category = "MIXED"

    return {
        "a_diff": a_diff,
        "b_diff": b_diff,
        "a_similar": a_diff < threshold,
        "b_similar": b_diff < threshold,
        "category": category,
        "zf1_a": zf1["a_zf"],
        "zf2_a": zf2["a_zf"],
        "zf1_b": zf1["b_zf"],
        "zf2_b": zf2["b_zf"],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Full distribution analysis
# ─────────────────────────────────────────────────────────────────────────────

def analyze_full_distribution(curves, lmfdb_records):
    """Compute zero-frequency distribution for all curves and compare to CM."""
    results = {
        "total_curves": len(curves),
        "by_st_group": {},
        "by_end_alg": {},
        "cm_detection": {},
    }

    # Group curves by conductor for matching with LMFDB metadata
    by_cond = defaultdict(list)
    for c in curves:
        by_cond[c["conductor"]].append(c)

    # Compute zero-frequency for all curves
    all_zf = []
    st_zf = defaultdict(list)
    end_alg_zf = defaultdict(list)

    # Match raw curves to LMFDB metadata by conductor + st_group
    cond_to_end_alg = defaultdict(list)
    for label, rec in lmfdb_records.items():
        cond_to_end_alg[rec['cond']].append(rec)

    for c in curves:
        bad = prime_factors(c["conductor"])
        zf = compute_zero_freq(c["euler"], bad)
        if zf is None:
            continue

        zf["conductor"] = c["conductor"]
        zf["st_group"] = c["st_group"]
        all_zf.append(zf)
        st_zf[c["st_group"]].append(zf["a_zf"])

    # Distribution stats
    a_zfs = [z["a_zf"] for z in all_zf]
    b_zfs = [z["b_zf"] for z in all_zf]

    results["a_zf_stats"] = {
        "mean": sum(a_zfs) / len(a_zfs) if a_zfs else 0,
        "min": min(a_zfs) if a_zfs else 0,
        "max": max(a_zfs) if a_zfs else 0,
        "n_cm_like": sum(1 for z in a_zfs if z > 0.3),
        "n_generic": sum(1 for z in a_zfs if z < 0.1),
        "n_intermediate": sum(1 for z in a_zfs if 0.1 <= z <= 0.3),
    }

    results["b_zf_stats"] = {
        "mean": sum(b_zfs) / len(b_zfs) if b_zfs else 0,
        "min": min(b_zfs) if b_zfs else 0,
        "max": max(b_zfs) if b_zfs else 0,
        "n_cm_like": sum(1 for z in b_zfs if z > 0.3),
        "n_generic": sum(1 for z in b_zfs if z < 0.1),
    }

    # By Sato-Tate group
    for st, zfs in sorted(st_zf.items()):
        results["by_st_group"][st] = {
            "count": len(zfs),
            "mean_a_zf": sum(zfs) / len(zfs),
            "min_a_zf": min(zfs),
            "max_a_zf": max(zfs),
            "n_cm_like": sum(1 for z in zfs if z > 0.3),
        }

    # Match with LMFDB end_alg to validate CM detection
    # Group by end_alg using LMFDB dump
    end_alg_counts = Counter()
    end_alg_zfs = defaultdict(list)

    for rec in lmfdb_records.values():
        end_alg_counts[rec['end_alg']] += 1

    # For each curve, try to match to LMFDB record and get end_alg
    # Match by conductor + st_group (coarse but workable)
    for z in all_zf:
        cond = z["conductor"]
        st = z["st_group"]
        # Find matching LMFDB record
        candidates = cond_to_end_alg.get(cond, [])
        matched_alg = "Q"  # default
        for cand in candidates:
            if cand['st_group'] == st:
                matched_alg = cand['end_alg']
                break
        end_alg_zfs[matched_alg].append(z["a_zf"])

    for alg, zfs in sorted(end_alg_zfs.items()):
        results["by_end_alg"][alg] = {
            "count": len(zfs),
            "mean_a_zf": sum(zfs) / len(zfs),
            "min_a_zf": min(zfs),
            "max_a_zf": max(zfs),
            "n_cm_like": sum(1 for z in zfs if z > 0.3),
        }

    # CM detection accuracy
    # True CM: end_alg contains "CM"
    # Predicted CM: a_zf > 0.3
    tp = sum(1 for z in all_zf
             if z["a_zf"] > 0.3 and
             any(c['end_alg'] in ('CM',) and c['st_group'] == z['st_group']
                 for c in cond_to_end_alg.get(z["conductor"], [])))
    fp = sum(1 for z in all_zf
             if z["a_zf"] > 0.3 and
             not any(c['end_alg'] in ('CM',) and c['st_group'] == z['st_group']
                     for c in cond_to_end_alg.get(z["conductor"], [])))
    fn = sum(1 for z in all_zf
             if z["a_zf"] <= 0.3 and
             any(c['end_alg'] in ('CM',) and c['st_group'] == z['st_group']
                 for c in cond_to_end_alg.get(z["conductor"], [])))
    tn = len(all_zf) - tp - fp - fn

    results["cm_detection"] = {
        "threshold": 0.3,
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "precision": tp / (tp + fp) if (tp + fp) > 0 else 0,
        "recall": tp / (tp + fn) if (tp + fn) > 0 else 0,
        "total_known_cm": tp + fn,
        "total_predicted_cm": tp + fp,
    }

    # Histogram of a_zf (binned)
    bins = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6, 0.8, 1.01]
    hist = [0] * (len(bins) - 1)
    for z in a_zfs:
        for i in range(len(bins) - 1):
            if bins[i] <= z < bins[i + 1]:
                hist[i] += 1
                break
    results["a_zf_histogram"] = {
        f"[{bins[i]:.2f},{bins[i+1]:.2f})": hist[i]
        for i in range(len(bins) - 1)
    }

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    base = Path(__file__).resolve().parents[3]
    raw_path = base / "genus2" / "data" / "g2c-data" / "gce_1000000_lmfdb.txt"
    lmfdb_path = base / "lmfdb_dump" / "g2c_curves.json"
    struct_path = Path(__file__).resolve().parent / "genus2_structural_results.json"
    output_path = Path(__file__).resolve().parent / "gsp4_cm_detection_results.json"

    print("GSp_4 ZERO-FREQUENCY CM DETECTION")
    print("=" * 72)
    print(f"Raw data: {raw_path}")
    print(f"LMFDB dump: {lmfdb_path}")
    print()

    # ─── Load data ───
    t0 = time.time()
    print("Loading raw curves...")
    curves = load_raw_curves(str(raw_path))
    print(f"  {len(curves)} curves loaded in {time.time()-t0:.1f}s")

    t1 = time.time()
    print("Loading LMFDB metadata...")
    lmfdb_records = load_lmfdb_dump(str(lmfdb_path))
    print(f"  {len(lmfdb_records)} records loaded in {time.time()-t1:.1f}s")

    # ─── The 37 mod-3 conductors ───
    irred_conds_mod3 = [
        1844, 2348, 3572, 4304, 5497, 7945, 9664, 14155, 19201, 20432,
        20560, 21611, 31312, 32119, 32575, 36265, 43276, 50173, 50608,
        69422, 77608, 83776, 88765, 96347, 114437, 124712, 141538, 142265,
        155305, 173936, 195337, 216677, 232912, 235237, 342871, 600953, 745517,
    ]

    # Geometric vs representation-theoretic classification
    geometric_conds = {2348, 20560}
    rep_theoretic_conds = set(irred_conds_mod3) - geometric_conds

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 1: MOD-3 CONGRUENCE PAIR ZERO-FREQUENCY ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════
    print()
    print("=" * 72)
    print("SECTION 1: ZERO-FREQUENCY FOR 37 MOD-3 CONGRUENCE PAIRS")
    print("=" * 72)
    print()

    pairs_37 = find_mod3_pairs(curves, irred_conds_mod3)
    print(f"Recovered {len(pairs_37)} / 37 pairs")
    print()

    pair_results = []
    geo_diffs_a = []
    geo_diffs_b = []
    rep_diffs_a = []
    rep_diffs_b = []

    print(f"{'N':>8}  {'Type':<6}  {'a_zf_1':>8}  {'a_zf_2':>8}  {'|da|':>8}  {'b_zf_1':>8}  {'b_zf_2':>8}  {'|db|':>8}  {'Cat':<15}")
    print("-" * 95)

    for cond, c1, c2 in pairs_37:
        bad = prime_factors(cond)
        zf1 = compute_zero_freq(c1["euler"], bad)
        zf2 = compute_zero_freq(c2["euler"], bad)
        cls = classify_pair(zf1, zf2)

        pair_type = "GEO" if cond in geometric_conds else "REP"

        pr = {
            "conductor": cond,
            "type": "geometric" if cond in geometric_conds else "representation-theoretic",
            "curve1_eqn": c1["eqn"][:50],
            "curve2_eqn": c2["eqn"][:50],
        }

        if isinstance(cls, dict):
            pr.update(cls)
            da = cls["a_diff"]
            db = cls["b_diff"]

            if cond in geometric_conds:
                geo_diffs_a.append(da)
                geo_diffs_b.append(db)
            else:
                rep_diffs_a.append(da)
                rep_diffs_b.append(db)

            print(f"{cond:>8}  {pair_type:<6}  {cls['zf1_a']:>8.4f}  {cls['zf2_a']:>8.4f}  {da:>8.4f}  "
                  f"{cls['zf1_b']:>8.4f}  {cls['zf2_b']:>8.4f}  {db:>8.4f}  {cls['category']:<15}")
        else:
            pr["error"] = cls
            print(f"{cond:>8}  {pair_type:<6}  {'N/A':>8}  {'N/A':>8}")

        if zf1:
            pr["zf1_details"] = zf1
        if zf2:
            pr["zf2_details"] = zf2

        pair_results.append(pr)

    print()

    # ─── Summary statistics ───
    print("=" * 72)
    print("SECTION 2: GEOMETRIC vs REPRESENTATION-THEORETIC COMPARISON")
    print("=" * 72)
    print()

    if geo_diffs_a:
        geo_mean_a = sum(geo_diffs_a) / len(geo_diffs_a)
        geo_max_a = max(geo_diffs_a)
        geo_mean_b = sum(geo_diffs_b) / len(geo_diffs_b)
        print(f"GEOMETRIC pairs (n={len(geo_diffs_a)}):")
        print(f"  a_zf mean |diff|: {geo_mean_a:.4f}")
        print(f"  a_zf max  |diff|: {geo_max_a:.4f}")
        print(f"  b_zf mean |diff|: {geo_mean_b:.4f}")
        print()

    if rep_diffs_a:
        rep_mean_a = sum(rep_diffs_a) / len(rep_diffs_a)
        rep_max_a = max(rep_diffs_a)
        rep_mean_b = sum(rep_diffs_b) / len(rep_diffs_b)
        print(f"REPRESENTATION-THEORETIC pairs (n={len(rep_diffs_a)}):")
        print(f"  a_zf mean |diff|: {rep_mean_a:.4f}")
        print(f"  a_zf max  |diff|: {rep_max_a:.4f}")
        print(f"  b_zf mean |diff|: {rep_mean_b:.4f}")
        print()

    # Compare
    if geo_diffs_a and rep_diffs_a:
        print("COMPARISON:")
        ratio_a = rep_mean_a / geo_mean_a if geo_mean_a > 0 else float('inf')
        print(f"  Rep-theoretic / Geometric a_zf diff ratio: {ratio_a:.2f}x")
        print(f"  More conserved in geometric: {'YES' if geo_mean_a < rep_mean_a else 'NO'}")
        print()

    # Category distribution
    cats = Counter(p.get("category", "N/A") for p in pair_results)
    print("Category distribution:")
    for cat, count in cats.most_common():
        print(f"  {cat}: {count}")
    print()

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 3: MOD-2 CONGRUENCE PAIRS (if available)
    # ═══════════════════════════════════════════════════════════════════════
    mod2_pair_results = []
    try:
        with open(str(struct_path)) as f:
            struct_data = json.load(f)
        mod2_congruences = struct_data.get("mod2_scan", {}).get("congruences", [])
        if mod2_congruences:
            # Only analyze irreducible ones
            mod2_irred = [c for c in mod2_congruences
                          if c.get("coprime") and c.get("both_USp4") and c.get("irred_witnesses", 0) > 0]
            print("=" * 72)
            print(f"SECTION 3: MOD-2 IRREDUCIBLE PAIRS (n={len(mod2_irred)})")
            print("=" * 72)
            print()

            mod2_pairs = find_mod2_pairs(curves, mod2_irred)
            print(f"Matched {len(mod2_pairs)} / {len(mod2_irred)} mod-2 pairs to raw data")

            mod2_a_diffs = []
            mod2_b_diffs = []
            mod2_cats = Counter()

            for cond, c1, c2 in mod2_pairs:
                bad = prime_factors(cond)
                zf1 = compute_zero_freq(c1["euler"], bad)
                zf2 = compute_zero_freq(c2["euler"], bad)
                cls = classify_pair(zf1, zf2)

                if isinstance(cls, dict):
                    mod2_a_diffs.append(cls["a_diff"])
                    mod2_b_diffs.append(cls["b_diff"])
                    mod2_cats[cls["category"]] += 1
                    mod2_pair_results.append({
                        "conductor": cond,
                        "a_diff": cls["a_diff"],
                        "b_diff": cls["b_diff"],
                        "category": cls["category"],
                    })

            if mod2_a_diffs:
                print(f"  Mean a_zf |diff|: {sum(mod2_a_diffs)/len(mod2_a_diffs):.4f}")
                print(f"  Max  a_zf |diff|: {max(mod2_a_diffs):.4f}")
                print(f"  Mean b_zf |diff|: {sum(mod2_b_diffs)/len(mod2_b_diffs):.4f}")
                print(f"  Categories: {dict(mod2_cats)}")
                print()
    except Exception as e:
        print(f"  (mod-2 analysis skipped: {e})")
        print()

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 4: FULL 66K DISTRIBUTION + CM DETECTION
    # ═══════════════════════════════════════════════════════════════════════
    print("=" * 72)
    print("SECTION 4: FULL DISTRIBUTION (ALL 66K CURVES)")
    print("=" * 72)
    print()

    dist = analyze_full_distribution(curves, lmfdb_records)

    print(f"Total curves analyzed: {dist['total_curves']}")
    print()
    print("a_p zero-frequency stats:")
    for k, v in dist["a_zf_stats"].items():
        print(f"  {k}: {v}")
    print()
    print("b_p zero-frequency stats:")
    for k, v in dist["b_zf_stats"].items():
        print(f"  {k}: {v}")
    print()

    print("By Sato-Tate group:")
    for st, info in sorted(dist["by_st_group"].items(), key=lambda x: -x[1]["count"]):
        print(f"  {st:<25} n={info['count']:>6}  mean_a_zf={info['mean_a_zf']:.4f}  "
              f"range=[{info['min_a_zf']:.3f},{info['max_a_zf']:.3f}]  "
              f"CM-like={info['n_cm_like']}")
    print()

    print("By end_alg:")
    for alg, info in sorted(dist["by_end_alg"].items(), key=lambda x: -x[1]["count"]):
        print(f"  {alg:<12} n={info['count']:>6}  mean_a_zf={info['mean_a_zf']:.4f}  "
              f"range=[{info['min_a_zf']:.3f},{info['max_a_zf']:.3f}]  "
              f"CM-like={info['n_cm_like']}")
    print()

    print("CM detection (threshold=0.3):")
    cm = dist["cm_detection"]
    print(f"  True positives:  {cm['true_positives']}")
    print(f"  False positives: {cm['false_positives']}")
    print(f"  False negatives: {cm['false_negatives']}")
    print(f"  True negatives:  {cm['true_negatives']}")
    print(f"  Precision: {cm['precision']:.4f}")
    print(f"  Recall:    {cm['recall']:.4f}")
    print(f"  Known CM:  {cm['total_known_cm']}")
    print(f"  Predicted: {cm['total_predicted_cm']}")
    print()

    print("a_p zero-frequency histogram:")
    for bin_label, count in dist["a_zf_histogram"].items():
        bar = "#" * (count // max(1, max(dist["a_zf_histogram"].values()) // 60))
        print(f"  {bin_label:>14}: {count:>6}  {bar}")
    print()

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 5: SPECIFIC GEOMETRIC PAIR DEEP DIVE
    # ═══════════════════════════════════════════════════════════════════════
    print("=" * 72)
    print("SECTION 5: GEOMETRIC PAIRS DEEP DIVE (N=2348, N=20560)")
    print("=" * 72)
    print()

    for pr in pair_results:
        if pr["conductor"] in geometric_conds:
            print(f"N={pr['conductor']}:")
            print(f"  Curve 1: {pr.get('curve1_eqn', 'N/A')}")
            print(f"  Curve 2: {pr.get('curve2_eqn', 'N/A')}")
            if "zf1_details" in pr:
                z1 = pr["zf1_details"]
                z2 = pr["zf2_details"]
                print(f"  Curve 1: a_zf={z1['a_zf']:.4f} ({z1['a_zeros']}/{z1['n_good']}), "
                      f"b_zf={z1['b_zf']:.4f} ({z1['b_zeros']}/{z1['n_good']})")
                print(f"  Curve 2: a_zf={z2['a_zf']:.4f} ({z2['a_zeros']}/{z2['n_good']}), "
                      f"b_zf={z2['b_zf']:.4f} ({z2['b_zeros']}/{z2['n_good']})")
                print(f"  |diff| a_zf: {pr.get('a_diff', 0):.4f}")
                print(f"  |diff| b_zf: {pr.get('b_diff', 0):.4f}")
                print(f"  Category: {pr.get('category', 'N/A')}")
            print()

    # ═══════════════════════════════════════════════════════════════════════
    # SAVE RESULTS
    # ═══════════════════════════════════════════════════════════════════════
    output = {
        "challenge": "CT4 Zero-Frequency CM Detector on GSp_4",
        "description": "Apply a_p zero-frequency CM detection from GL_2 to genus-2 curves",
        "mod3_pairs": {
            "n_pairs": len(pair_results),
            "n_geometric": len(geo_diffs_a),
            "n_rep_theoretic": len(rep_diffs_a),
            "geometric_mean_a_diff": sum(geo_diffs_a) / len(geo_diffs_a) if geo_diffs_a else None,
            "rep_theoretic_mean_a_diff": sum(rep_diffs_a) / len(rep_diffs_a) if rep_diffs_a else None,
            "geometric_mean_b_diff": sum(geo_diffs_b) / len(geo_diffs_b) if geo_diffs_b else None,
            "rep_theoretic_mean_b_diff": sum(rep_diffs_b) / len(rep_diffs_b) if rep_diffs_b else None,
            "category_distribution": dict(cats),
            "pairs": pair_results,
        },
        "mod2_pairs": {
            "n_matched": len(mod2_pair_results),
            "summary": {
                "mean_a_diff": sum(p["a_diff"] for p in mod2_pair_results) / len(mod2_pair_results) if mod2_pair_results else None,
                "mean_b_diff": sum(p["b_diff"] for p in mod2_pair_results) / len(mod2_pair_results) if mod2_pair_results else None,
            },
        },
        "full_distribution": dist,
        "findings": [],
    }

    # Auto-generate findings
    findings = []

    # Finding 1: Are all 37 pairs generic?
    n_both_generic = cats.get("BOTH_GENERIC", 0)
    n_total = len(pair_results)
    findings.append(f"All {n_total} mod-3 pairs classified: {dict(cats)}")

    # Finding 2: Geometric vs rep-theoretic
    if geo_diffs_a and rep_diffs_a:
        g = sum(geo_diffs_a) / len(geo_diffs_a)
        r = sum(rep_diffs_a) / len(rep_diffs_a)
        findings.append(
            f"Geometric pairs mean a_zf diff: {g:.4f}, "
            f"Rep-theoretic: {r:.4f}. "
            f"Ratio: {r/g if g > 0 else 'inf':.2f}x"
        )

    # Finding 3: CM detection accuracy
    if cm["total_known_cm"] > 0:
        findings.append(
            f"CM detection: precision={cm['precision']:.3f}, "
            f"recall={cm['recall']:.3f}, "
            f"TP={cm['true_positives']}, FP={cm['false_positives']}, "
            f"FN={cm['false_negatives']}"
        )

    # Finding 4: ST group discrimination
    for st, info in dist["by_st_group"].items():
        if info["n_cm_like"] > 0 and info["count"] > 10:
            findings.append(
                f"ST group {st}: {info['n_cm_like']}/{info['count']} CM-like "
                f"(mean a_zf={info['mean_a_zf']:.4f})"
            )

    output["findings"] = findings

    with open(str(output_path), 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
